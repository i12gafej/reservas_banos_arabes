/*
  Servicio para gestionar restricciones de reservas.
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
export interface ConstraintRange {
  initial_time: string; // "HH:MM:SS"
  end_time: string;     // "HH:MM:SS"
}

export interface Constraint {
  id: number;
  day: string;          // ISO date YYYY-MM-DD
  created_at: string;   // ISO datetime
  ranges: ConstraintRange[];
}

// Endpoints -----------------------------------------------------------
const CONSTRAINT_ENDPOINT = `${BASE_URL}/restricciones/`;

/**
 * Obtiene todas las restricciones.
 */
export async function getConstraints(): Promise<Constraint[]> {
  return http<Constraint[]>(CONSTRAINT_ENDPOINT);
}

/**
 * Obtiene una restricción específica por ID.
 */
export async function getConstraintById(id: number): Promise<Constraint> {
  return http<Constraint>(`${CONSTRAINT_ENDPOINT}${id}/`);
}

/**
 * Obtiene la restricción para una fecha específica.
 */
export async function getConstraintByDate(targetDay: Date | string): Promise<Constraint | null> {
  const isoDay = toLocalISODate(targetDay);
  try {
    return await http<Constraint>(`${CONSTRAINT_ENDPOINT}by-date/${isoDay}/`);
  } catch (error) {
    if (error instanceof Error && error.message.includes('404')) {
      return null;
    }
    throw error;
  }
}

/**
 * Guarda restricciones para una fecha específica desde un array de celdas booleanas.
 */
export async function saveConstraintForDate(
  targetDay: Date | string,
  cells: boolean[]
): Promise<Constraint | null> {
  const isoDay = toLocalISODate(targetDay);
  const payload = {
    date: isoDay,
    cells: cells,
  };
  
  const response = await http<Constraint | { detail: string }>(`${CONSTRAINT_ENDPOINT}save-for-date/`, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
  
  // Si la respuesta contiene 'detail', significa que se eliminaron las restricciones
  if ('detail' in response) {
    return null;
  }
  
  return response as Constraint;
}

/**
 * Elimina una restricción por ID.
 */
export async function deleteConstraint(id: number): Promise<void> {
  await http<void>(`${CONSTRAINT_ENDPOINT}${id}/`, {
    method: 'DELETE',
  });
}

/**
 * Convierte rangos de restricción a un array de celdas booleanas.
 */
export function constraintRangesToCells(
  ranges: ConstraintRange[],
  numCells: number = 25,
  startHour: number = 10,
  stepMinutes: number = 30
): boolean[] {
  const cells = Array(numCells).fill(false);
  
  for (const range of ranges) {
    // Extraer horas y minutos de los tiempos
    const [startH, startM] = range.initial_time.split(':').map(Number);
    const [endH, endM] = range.end_time.split(':').map(Number);
    
    // Convertir a minutos
    const startMinutes = startH * 60 + startM;
    const endMinutes = endH * 60 + endM;
    
    // Convertir a índices
    const startIndex = (startMinutes - startHour * 60) / stepMinutes;
    const endIndex = (endMinutes - startHour * 60) / stepMinutes;
    
    // Marcar celdas como restringidas
    for (let i = Math.max(0, startIndex); i < Math.min(numCells, endIndex); i++) {
      cells[i] = true;
    }
  }
  
  return cells;
}

/**
 * Convierte un array de celdas booleanas a rangos de restricción.
 */
export function cellsToConstraintRanges(
  cells: boolean[],
  startHour: number = 10,
  stepMinutes: number = 30
): ConstraintRange[] {
  const ranges: ConstraintRange[] = [];
  let i = 0;
  
  while (i < cells.length) {
    if (cells[i]) {
      // Encontrar el inicio del rango
      const startMinutes = startHour * 60 + i * stepMinutes;
      const startTime = `${Math.floor(startMinutes / 60).toString().padStart(2, '0')}:${(startMinutes % 60).toString().padStart(2, '0')}:00`;
      
      // Encontrar el final del rango
      let j = i;
      while (j < cells.length && cells[j]) {
        j++;
      }
      
      const endMinutes = startHour * 60 + j * stepMinutes;
      const endTime = `${Math.floor(endMinutes / 60).toString().padStart(2, '0')}:${(endMinutes % 60).toString().padStart(2, '0')}:00`;
      
      ranges.push({
        initial_time: startTime,
        end_time: endTime,
      });
      
      i = j;
    } else {
      i++;
    }
  }
  
  return ranges;
} 