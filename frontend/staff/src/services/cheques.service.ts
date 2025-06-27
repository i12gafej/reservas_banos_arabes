import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface GiftVoucher {
  id: number;
  code: string;
  bought_date: string;
  payment_date?: string;
  people: number;
  price: string;
  status: 'pending_payment' | 'paid' | 'used';
  recipients_email?: string;
  recipients_name?: string;
  recipients_surname?: string;
  gift_name?: string;
  gift_description?: string;
  buyer_client: number;
  created_at: string;
  updated_at: string;
  product: number;
}

export interface GiftVoucherWithDetails {
  // Campos básicos
  id: number;
  code: string;
  price: string;
  used?: boolean;
  status: 'pending_payment' | 'paid' | 'used';
  payment_date?: string;
  people: number;
  buyer_client_id: number;
  product_id: number;
  recipients_email?: string;
  recipients_name?: string;
  recipients_surname?: string;
  gift_name?: string;
  gift_description?: string;
  created_at: string;
  bought_date?: string;
  
  // Información del cliente comprador
  buyer_name?: string;
  buyer_surname?: string;
  buyer_phone?: string;
  buyer_email?: string;
  buyer_client_created_at?: string;
  
  // Información del producto
  product_name?: string;
}

export interface StaffBathRequest {
  massage_type: string;
  minutes: string;
  quantity: number;
}

export interface CreateGiftVoucherRequest {
  buyer_name: string;
  buyer_surname?: string;
  buyer_phone?: string;
  buyer_email: string;
  recipient_name?: string;
  recipient_surname?: string;
  recipient_email?: string;
  gift_name: string;
  gift_description?: string;
  people: number;
  baths: StaffBathRequest[];
  send_whatsapp_buyer?: boolean;
}

export const getCheques = async (): Promise<GiftVoucherWithDetails[]> => {
  try {
    const response = await axios.get(`${BASE_URL}/cheques/`);
    return response.data;
  } catch (error) {
    console.error('Error fetching cheques:', error);
    throw error;
  }
};

export const createGiftVoucher = async (data: CreateGiftVoucherRequest): Promise<GiftVoucher> => {
  try {
    const response = await axios.post(`${BASE_URL}/cheques/create-from-staff/`, data);
    return response.data;
  } catch (error) {
    console.error('Error creating gift voucher:', error);
    throw error;
  }
}; 