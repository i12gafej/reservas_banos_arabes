/*
  Servicio de utilidades para cuadrante.
  Lee la URL base del backend de la variable de entorno VITE_API_URL.
  Ej. en tu .env.local →  VITE_API_URL="http://localhost:8000/api/v1"
*/

import { getProductBathTypes } from './productos.service';
import { getDayAvailability as getMasajistasAvailability, AvailabilityRange as MasajistaAvailabilityRange } from './masajistas.service';

const BASE_URL = import.meta.env.VITE_API_URL?.replace(/\/$/, '') ?? '';

if (!BASE_URL) {
  // Aviso en consola para entornos de desarrollo
  // eslint-disable-next-line no-console
  console.warn('VITE_API_URL no está definida; las peticiones no funcionarán.');
}

// Helpers --------------------------------------------------------------

async function http<T>(url: string, options: RequestInit = {}): Promise<T> {
  const resp = await fetch(url, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  });
  if (!resp.ok) {
    const msg = await resp.text();
    throw new Error(`${resp.status} ${resp.statusText} – ${msg}`);
  }
  return resp.json() as Promise<T>;
}

// Helpers de MasajistasPage
const TIMES = Array.from({ length: 25 }, (_, i) => {
  const minutes = 10 * 60 + i * 30;
  const h = Math.floor(minutes / 60)
    .toString()
    .padStart(2, '0');
  const m = (minutes % 60).toString().padStart(2, '0');
  return `${h}:${m}`;
});

function rangesToCells(ranges: MasajistaAvailabilityRange[]): number[] {
  const cells = Array(25).fill(0);
  ranges.forEach((r) => {
    const startIdx = TIMES.findIndex((t) => t === r.initial_time.substring(0, 5));
    const endIdx = TIMES.findIndex((t) => t === r.end_time.substring(0, 5));
    if (startIdx === -1 || endIdx === -1) return;
    for (let i = startIdx; i < endIdx; i++) {
      cells[i] = r.massagists_availability;
    }
  });
  return cells;
}

// Tipos ----------------------------------------------------------------
export interface AvailabilityRange {
  initial_time: string;    // "HH:MM:SS"
  end_time: string;        // "HH:MM:SS"
  massagists_availability: number;
}

export interface Availability {
  id: number;
  type: 'weekday' | 'punctual';
  punctual_day: string | null;  // ISO date
  weekday: number | null;       // 1-7 cuando type=weekday
  ranges: AvailabilityRange[];
}

export interface Capacity {
  id: number;
  value: number;
}

// --------------------------------------------------------------------
// Tipos y endpoints de Reservas (Bookings)
// --------------------------------------------------------------------

export interface Booking {
  id?: number;
  internal_order_id?: string;

  booking_date: string; // ISO 8601 date-time (YYYY-MM-DDTHH:mm:ss)
  hour?: string;        // "HH:MM:SS" si el backend lo separa
  people: number;
  comment?: string | null;

  amount_paid: string;     // Decimal en texto para evitar problemas de coma
  amount_pending: string;  // idem
  payment_date?: string | null; // ISO date-time

  checked_in: boolean;
  checked_out: boolean;

  client_id: number;
  product_id: number;  // Un solo producto por reserva

  created_at?: string;
}

const BOOKING_ENDPOINT = `${BASE_URL}/reservas/`;

/** Obtiene todas las reservas */
export async function getBookings(): Promise<Booking[]> {
  return http<Booking[]>(BOOKING_ENDPOINT);
}

/** Obtiene reservas por fecha específica */
export async function getBookingsByDate(date: string): Promise<Booking[]> {
  return http<Booking[]>(`${BOOKING_ENDPOINT}by-date/?date=${date}`);
}

export type BookingCreate = Omit<Booking, 'id' | 'internal_order_id' | 'created_at'>;

/** Crea una nueva reserva */
export async function createBooking(payload: BookingCreate): Promise<Booking> {
  return http<Booking>(BOOKING_ENDPOINT, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

/** Actualiza una reserva existente */
export async function updateBooking(id: number, payload: Partial<Booking>): Promise<Booking> {
  return http<Booking>(`${BOOKING_ENDPOINT}${id}/`, {
    method: 'PUT',
    body: JSON.stringify(payload),
  });
}

// API Availability -----------------------------------------------------

export async function getAvailabilities(): Promise<Availability[]> {
  return http<Availability[]>(`${BASE_URL}/availability/`);
}

export async function updateAvailability(id: number, payload: Partial<Availability>): Promise<Availability> {
  return http<Availability>(`${BASE_URL}/availability/${id}/`, {
    method: 'PUT',
    body: JSON.stringify(payload),
  });
}

// API Capacity (singleton) ---------------------------------------------

const CAPACITY_ENDPOINT = `${BASE_URL}/capacity/`;

/**
 * Obtiene el único registro de aforo. El backend debe devolverlo sin necesidad de ID.
 */
export async function getCapacity(): Promise<Capacity> {
  return http<Capacity>(CAPACITY_ENDPOINT);
}

/**
 * Actualiza el valor del aforo único.
 */
export async function updateCapacity(id: number, value: number): Promise<Capacity> {
  return http<Capacity>(`${CAPACITY_ENDPOINT}${id}/`, {
    method: 'PUT',
    body: JSON.stringify({ value }),
  });
}

export interface StaffBath {
  massage_type: 'relax' | 'exfoliation' | 'rock' | 'none';
  minutes: '15' | '30' | '60';
  quantity: number;
}

export interface StaffBookingPayload {
  name: string;
  surname?: string;
  phone_number: string;
  email?: string;
  date: string;   // YYYY-MM-DD
  hour: string;   // HH:MM:SS
  people: number;
  baths: StaffBath[];
  comment?: string;
  send_whatsapp?: boolean;
}

/** Crea una reserva proveniente de la interfaz staff */
export async function createStaffBooking(payload: StaffBookingPayload): Promise<Booking> {
  return http<Booking>(`${BASE_URL}/reservas/staff/`, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

// --------------------------------------------------------------------
// Interfaces para el cuadrante
// --------------------------------------------------------------------

export interface CuadranteData {
  date: string;
  capacity: number;
  bookings: Booking[];
  timeSlots: string[]; // Array de horas "HH:MM"
}

export interface TimeSlotData {
  hour: string;
  ocupacion: number;
  disponibles: number;
  masajistasDisponibles: number;
  minutosOcupados: number;
  minutosDisponibles: number;
}

export interface CuadranteCalculated {
  date: string;
  capacity: number;
  timeSlots: TimeSlotData[];
}

// --------------------------------------------------------------------
// Funciones de cálculo para el cuadrante
// --------------------------------------------------------------------

/**
 * Calcula los datos del cuadrante para una fecha específica
 */
export async function calculateCuadrante(date: string): Promise<CuadranteCalculated> {
  // Obtener capacidad
  const capacity = await getCapacity();
  
  // Obtener reservas del día
  const bookings = await getBookingsByDate(date);

  // Obtener disponibilidad de masajistas
  const masajistasAv = await getMasajistasAvailability(date);
  const masajistasCells = masajistasAv ? rangesToCells(masajistasAv.ranges) : Array(25).fill(0);
  
  // Generar slots de tiempo (10:00 a 22:00 cada 30 minutos)
  const timeSlots = generateTimeSlots('10:00', '22:00', 30);
  
  // Calcular datos para cada slot
  const calculatedSlots: TimeSlotData[] = [];
  
  for (const hour of timeSlots) {
    const slotBookings = bookings.filter(b => {
      const bookingHour = b.hour?.substring(0, 5) || '00:00';
      return bookingHour === hour;
    });
    
    // Calcular ocupación (personas totales)
    const ocupacion = slotBookings.reduce((sum, b) => sum + b.people, 0);
    
    // Calcular disponibles
    const disponibles = capacity.value - ocupacion;
    
    // Calcular masajistas disponibles
    const slotIndex = timeSlots.findIndex(t => t === hour);
    const masajistasDisponibles = masajistasCells[slotIndex] ?? 0;
    
    // Calcular minutos ocupados por masajes
    const minutosOcupados = await calculateMinutosOcupados(slotBookings);
    
    // Calcular minutos disponibles (masajistas * 25 - ocupados)
    const minutosDisponibles = (masajistasDisponibles * 25) - minutosOcupados;
    
    calculatedSlots.push({
      hour,
      ocupacion,
      disponibles,
      masajistasDisponibles,
      minutosOcupados,
      minutosDisponibles
    });
  }
  
  return {
    date,
    capacity: capacity.value,
    timeSlots: calculatedSlots
  };
}

/**
 * Genera slots de tiempo entre start y end cada step minutos
 */
function generateTimeSlots(start: string, end: string, stepMinutes: number): string[] {
  const [startH, startM] = start.split(':').map(Number);
  const [endH, endM] = end.split(':').map(Number);
  const result: string[] = [];
  let minutes = startH * 60 + startM;
  const endTotal = endH * 60 + endM;
  
  while (minutes <= endTotal) {
    const h = Math.floor(minutes / 60).toString().padStart(2, '0');
    const m = (minutes % 60).toString().padStart(2, '0');
    result.push(`${h}:${m}`);
    minutes += stepMinutes;
  }
  
  return result;
}

/**
 * Calcula los minutos ocupados por masajes en las reservas
 */
async function calculateMinutosOcupados(bookings: Booking[]): Promise<number> {
  let totalMinutos = 0;
  
  for (const booking of bookings) {
    try {
      // Obtener tipos de baño del producto
      const bathTypes = await getProductBathTypes(booking.product_id);
      
      // Sumar minutos de cada tipo de baño
      for (const bathType of bathTypes) {
        if (bathType.massage_duration !== '0') {
          const minutos = parseInt(bathType.massage_duration);
          totalMinutos += minutos; // Ya no multiplicamos por quantity porque es un solo producto
        }
      }
    } catch (error) {
      console.warn(`Error obteniendo tipos de baño para producto ${booking.product_id}:`, error);
    }
  }
  
  return totalMinutos;
}
