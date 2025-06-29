/*
  Servicio para gestionar la disponibilidad de masajistas (Availability + AvailabilityRange).
  Usa el mismo patrón que cuadrante.service.ts para resolver la URL base.
*/

import { toLocalISODate } from '@/utils/date';

const BASE_URL = import.meta.env.VITE_API_URL?.replace(/\/$/, '') ?? '';

if (!BASE_URL) {
  // eslint-disable-next-line no-console
  console.warn('VITE_API_URL no está definida; las peticiones no funcionarán.');
}

// Helper HTTP ---------------------------------------------------------
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

// Tipos ---------------------------------------------------------------
export interface AvailabilityRange {
  initial_time: string; // "HH:MM:SS"
  end_time: string;     // "HH:MM:SS"
  massagists_availability: number;
}

export interface Availability {
  id: number;
  type: 'weekday' | 'punctual';
  punctual_day: string | null; // ISO date YYYY-MM-DD
  weekday: number | null;      // 1-7 cuando type=weekday
  ranges: AvailabilityRange[];
}

// Nuevos tipos para el sistema de versionado
export interface AvailabilityHistoryItem {
  id: number;
  type: 'weekday' | 'punctual';
  punctual_day: string | null;
  weekday: number | null;
  created_at: string;
  temporal_range: string;
  ranges: AvailabilityRange[];
}

export interface AvailabilityById {
  id: number;
  type: 'weekday' | 'punctual';
  punctual_day: string | null;
  weekday: number | null;
  created_at: string;
  ranges: AvailabilityRange[];
}

// Endpoints base ------------------------------------------------------
const AVAIL_ENDPOINT = `${BASE_URL}/disponibilidades/`;

// --------------------------------------------------------------------
// Lectura de disponibilidades
// --------------------------------------------------------------------

/** Devuelve la lista completa de Availability (con sus rangos). */
export async function getAvailabilities(): Promise<Availability[]> {
  return http<Availability[]>(AVAIL_ENDPOINT);
}

/**
 * Devuelve la Availability (y sus rangos) para un día concreto.
 * 1. Busca primero una disponibilidad puntual (type="punctual") con ese día.
 * 2. Si no la encuentra, devuelve la Availability por weekday correspondiente (si existe).
 * 3. Si no encuentra nada, devuelve null.
 */
export async function getDayAvailability(targetDay: Date | string): Promise<Availability | null> {
  const isoDay = toLocalISODate(targetDay);
  const list = await getAvailabilities();

  // 1) puntual
  let found = list.find((av) => av.type === 'punctual' && av.punctual_day === isoDay);
  if (found) return found;

  // 2) weekday (1=Lunes … 7=Domingo)
  const weekdayJS = new Date(isoDay).getDay(); // 0=Domingo
  const isoWeekday = weekdayJS === 0 ? 7 : weekdayJS; // Convertir a 1-7
  found = list.find((av) => av.type === 'weekday' && av.weekday === isoWeekday);
  return found ?? null;
}

// --------------------------------------------------------------------
// Nuevos métodos para el sistema de versionado
// --------------------------------------------------------------------

/**
 * Obtiene el historial completo de disponibilidades para un día específico.
 */
export async function getAvailabilityHistory(targetDay: Date | string): Promise<AvailabilityHistoryItem[]> {
  const isoDay = toLocalISODate(targetDay);
  return http<AvailabilityHistoryItem[]>(`${AVAIL_ENDPOINT}history/${isoDay}/`);
}

/**
 * Obtiene una disponibilidad específica por ID.
 */
export async function getAvailabilityById(availabilityId: number): Promise<AvailabilityById | null> {
  try {
    return await http<AvailabilityById>(`${AVAIL_ENDPOINT}by-id/${availabilityId}/`);
  } catch (error) {
    if (error instanceof Error && error.message.includes('404')) {
      return null;
    }
    throw error;
  }
}

/**
 * Crea una nueva versión de disponibilidad para un día específico.
 */
export async function createAvailabilityVersion(
  targetDay: Date | string,
  ranges: AvailabilityRange[],
  effectiveDate?: Date
): Promise<Availability> {
  const payload = {
    target_date: toLocalISODate(targetDay),
    ranges: ranges,
    effective_date: effectiveDate ? toLocalISODate(effectiveDate) : undefined,
  };
  
  return http<Availability>(`${AVAIL_ENDPOINT}create-version/`, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

/**
 * Crea una nueva versión de disponibilidad para un día de la semana.
 */
export async function createWeekdayAvailabilityVersion(
  weekday: number,
  ranges: AvailabilityRange[],
  effectiveDate?: Date
): Promise<Availability> {
  const payload = {
    weekday: weekday,
    ranges: ranges,
    effective_date: effectiveDate ? toLocalISODate(effectiveDate) : undefined,
  };
  
  return http<Availability>(`${AVAIL_ENDPOINT}create-weekday-version/`, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

// --------------------------------------------------------------------
// Creación / actualización
// --------------------------------------------------------------------

/**
 * Crea o actualiza (upsert) la disponibilidad puntual de un día.
 * Si ya existe Availability puntual para ese día → PUT /availability/{id}/.
 * Si no existe → POST /availability/.
 * Devuelve el objeto Availability resultante.
 */
export async function saveDayAvailability(
  targetDay: Date | string,
  ranges: AvailabilityRange[],
): Promise<Availability> {
  const isoDay = toLocalISODate(targetDay);

  // Intentar obtener disponibilidad puntual existente
  const existing = await getDayAvailability(isoDay);
  if (existing && existing.type === 'punctual' && existing.punctual_day === isoDay) {
    // Actualizar
    const payload = {
      ...existing,
      ranges,
    };
    return http<Availability>(`${AVAIL_ENDPOINT}${existing.id}/`, {
      method: 'PUT',
      body: JSON.stringify(payload),
    });
  }

  // Crear nueva disponibilidad puntual
  const payload = {
    type: 'punctual',
    punctual_day: isoDay,
    weekday: null,
    ranges,
  } as Omit<Availability, 'id'>;

  return http<Availability>(AVAIL_ENDPOINT, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

/** Upsert de disponibilidad por weekday (1=Lunes..7=Domingo) */
export async function saveWeekdayAvailability(
  weekday: number,
  ranges: AvailabilityRange[],
): Promise<Availability> {
  if (weekday < 1 || weekday > 7) {
    throw new Error('weekday debe estar entre 1 y 7');
  }

  const list = await getAvailabilities();
  const existing = list.find((av) => av.type === 'weekday' && av.weekday === weekday);

  if (existing) {
    const payload = { ...existing, ranges };
    return http<Availability>(`${AVAIL_ENDPOINT}${existing.id}/`, {
      method: 'PUT',
      body: JSON.stringify(payload),
    });
  }

  const payload = {
    type: 'weekday',
    weekday,
    punctual_day: null,
    ranges,
  } as Omit<Availability, 'id'>;

  return http<Availability>(AVAIL_ENDPOINT, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

// --------------------------------------------------------------------
// API Genérica (recomendada) -----------------------------------------
// --------------------------------------------------------------------
/**
 * Guarda una disponibilidad.
 * Ejemplos de uso:
 *   saveAvailability({ date: '2025-06-21' }, ranges)
 *   saveAvailability({ weekday: 1 }, ranges)   // 1=Lunes
 */
export async function saveAvailability(
  target: { date: Date | string } | { weekday: number },
  ranges: AvailabilityRange[],
): Promise<Availability> {
  if ('date' in target) {
    return saveDayAvailability(target.date, ranges);
  }
  return saveWeekdayAvailability(target.weekday, ranges);
}
