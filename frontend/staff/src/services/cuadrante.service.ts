/*
  Servicio de utilidades para cuadrante.
  Lee la URL base del backend de la variable de entorno VITE_API_URL.
  Ej. en tu .env.local →  VITE_API_URL="http://localhost:8000/api/v1"
*/

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
