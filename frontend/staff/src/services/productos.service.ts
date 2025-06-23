/*
  Servicio para gestión de tipos de baño y productos.
  Reutiliza la variable de entorno VITE_API_URL al igual que otros servicios.
*/

const BASE_URL = import.meta.env.VITE_API_URL?.replace(/\/$/, '') ?? '';

if (!BASE_URL) {
  // eslint-disable-next-line no-console
  console.warn('VITE_API_URL no está definida; las peticiones no funcionarán.');
}

// Helper HTTP ------------------------------------------------------------
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

// ----------------------------------------------------------------------
// Interfaces de dominio (mantener sincronizadas con backend)
// ----------------------------------------------------------------------

export interface BathType {
  id: number;
  name: string;
  massage_type: 'relax' | 'rock' | 'exfoliation' | 'none';
  massage_duration: '15' | '30' | '60' | '0';
  baths_duration: string; // HH:MM:SS
  description?: string | null;
  price: string;          // string para mantener decimales
}

export interface BathTypePriceUpdate {
  price: string | number;
}

export interface BathQuantity {
  bath_type_id: number;
  quantity: number;
}

export interface HostingQuantity {
  hosting_type_id: number;
  quantity: number;
}

export interface Product {
  id: number;
  name: string;
  observation?: string;
  description?: string;
  price: string;
  uses_capacity: boolean;
  uses_massagist: boolean;
  visible: boolean;
  baths: BathQuantity[];
  hostings: HostingQuantity[];
}

export type ProductCreate = Omit<Product, 'id'>;

// ----------------------------------------------------------------------
// BathType endpoints
// ----------------------------------------------------------------------
const BATH_TYPES_ENDPOINT = `${BASE_URL}/bath-types/`;

export async function getBathTypes(): Promise<BathType[]> {
  return http<BathType[]>(BATH_TYPES_ENDPOINT);
}

export async function updateBathTypePrice(id: number, price: string | number): Promise<BathType> {
  return http<BathType>(`${BATH_TYPES_ENDPOINT}${id}/`, {
    method: 'PATCH',
    body: JSON.stringify({ price }),
  });
}

// ----------------------------------------------------------------------
// Product endpoints (crud básico)
// ----------------------------------------------------------------------
const PRODUCTS_ENDPOINT = `${BASE_URL}/productos/`;

export async function getProducts(): Promise<Product[]> {
  return http<Product[]>(PRODUCTS_ENDPOINT);
}

export async function createProduct(payload: ProductCreate): Promise<Product> {
  return http<Product>(PRODUCTS_ENDPOINT, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function updateProduct(id: number, payload: Partial<ProductCreate>): Promise<Product> {
  return http<Product>(`${PRODUCTS_ENDPOINT}${id}/`, {
    method: 'PUT',
    body: JSON.stringify(payload),
  });
}

/** Obtiene los tipos de baño de un producto específico */
export async function getProductBathTypes(productId: number): Promise<BathType[]> {
  return http<BathType[]>(`${PRODUCTS_ENDPOINT}${productId}/baths/`);
}
