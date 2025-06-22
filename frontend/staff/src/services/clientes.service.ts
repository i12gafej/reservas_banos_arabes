/* Servicio para clientes */
export interface Client {
  id: number;
  name: string;
  surname?: string;
  email?: string;
  phone_number?: string;
  created_at?: string;
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
