/* Servicio para clientes */
export interface Client {
  id: number;
  name: string;
  surname?: string;
  email?: string;
  phone_number?: string;
  created_at?: string;
  match_info?: {
    email: boolean;
    phone: boolean;
    name: boolean;
    surname: boolean;
    name_surname_combo: boolean;
  };
}

export interface DuplicateGroup {
  email: string;
  phone: string;
  main_client: {
    id: number;
    name: string;
    surname: string;
    created_at: string | null;
  };
  duplicates: Array<{
    id: number;
    name: string;
    surname: string;
    created_at: string | null;
  }>;
  books_to_update: number;
  vouchers_to_update: number;
}

export interface DuplicatesPreview {
  total_groups: number;
  total_duplicates: number;
  groups: DuplicateGroup[];
}

export interface UnificationResult {
  success: boolean;
  message: string;
  unified_groups: number;
  clients_removed: number;
  books_updated: number;
  gift_vouchers_updated: number;
}

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

const CLIENT_ENDPOINT = `${BASE_URL}/clientes/`;

export async function getClientes(): Promise<Client[]> {
  return http<Client[]>(CLIENT_ENDPOINT);
}
// ------------------------------------------------------------------
// Funciones para unificación de clientes
// ------------------------------------------------------------------

/**
 * Obtiene una vista previa de los clientes duplicados sin realizar cambios
 */
export async function getDuplicatesPreview(): Promise<DuplicatesPreview> {
  return http<DuplicatesPreview>(`${CLIENT_ENDPOINT}duplicados-preview/`);
}

/**
 * Ejecuta la unificación de todos los clientes duplicados
 */
export async function unifyClients(): Promise<UnificationResult> {
  return http<UnificationResult>(`${CLIENT_ENDPOINT}unificar/`, {
    method: 'POST',
  });
}

/**
 * Busca clientes similares basándose en criterios de búsqueda
 */
export async function findSimilarClients(params: {
  name?: string;
  surname?: string;
  email?: string;
  phone_number?: string;
}): Promise<Client[]> {
  const searchParams = new URLSearchParams();
  
  if (params.name) searchParams.append('name', params.name);
  if (params.surname) searchParams.append('surname', params.surname);
  if (params.email) searchParams.append('email', params.email);
  if (params.phone_number) searchParams.append('phone_number', params.phone_number);
  
  const url = `${CLIENT_ENDPOINT}buscar-similares/?${searchParams.toString()}`;
  return http<Client[]>(url);
}

