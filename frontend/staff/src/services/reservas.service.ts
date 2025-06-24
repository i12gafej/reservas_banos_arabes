/* Servicio reservas */
import { Booking } from '@/services/cuadrante.service';

const BASE_URL = import.meta.env.VITE_API_URL?.replace(/\/$/, '') ?? '';

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

const BOOKING_ENDPOINT = `${BASE_URL}/reservas/`;

export async function getReservas(): Promise<Booking[]> {
  return http<Booking[]>(BOOKING_ENDPOINT);
}

// Interfaces para los nuevos endpoints
export interface BookLog {
  id: number;
  book_id: number;
  datetime: string;
  comment: string;
}

export interface BookDetail {
  id: number;
  internal_order_id: string;
  created_at: string;
  
  // Datos editables básicos
  booking_date: string;
  hour: string;
  people: number;
  comment: string;

  // Datos de pago
  amount_paid: string;
  amount_pending: string;
  payment_date: string | null;
  
  // Estados
  checked_in: boolean;
  checked_out: boolean;

  // Referencias
  client_id: number;
  product_id: number;

  // Información del cliente (solo lectura)
  client_name: string;
  client_surname: string;
  client_phone: string;
  client_email: string;
  client_created_at: string;

  // Información del creador (solo lectura)
  creator_type_name: string;
  creator_name: string;

  // Información del producto/masajes (solo lectura)
  product_baths: Array<{
    massage_type: string;
    massage_duration: string;
    quantity: number;
    name: string;
    price: string;
  }>;
}

export interface BookDetailUpdate {
  booking_date?: string;
  hour?: string;
  people?: number;
  comment?: string;
  amount_paid?: string;
  amount_pending?: string;
  payment_date?: string | null;
  checked_in?: boolean;
  checked_out?: boolean;
  product_id?: number;
  log_comment?: string; // Comentario personalizado para el log
}

// Funciones para obtener detalles de reserva
export async function getBookDetail(bookId: number): Promise<BookDetail> {
  return http<BookDetail>(`${BOOKING_ENDPOINT}${bookId}/detail/`);
}

// Funciones para actualizar reserva con log automático
export async function updateBookDetail(bookId: number, data: BookDetailUpdate): Promise<BookDetail> {
  return http<BookDetail>(`${BOOKING_ENDPOINT}${bookId}/detail/`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

// Funciones para gestión de logs
export async function getBookLogs(bookId: number): Promise<BookLog[]> {
  return http<BookLog[]>(`${BOOKING_ENDPOINT}${bookId}/logs/`);
}

export async function createBookLog(bookId: number, comment: string): Promise<BookLog> {
  return http<BookLog>(`${BOOKING_ENDPOINT}${bookId}/logs/`, {
    method: 'POST',
    body: JSON.stringify({ comment }),
  });
}
