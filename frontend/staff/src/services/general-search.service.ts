import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface SearchResult {
  id: number;
  type: 'client' | 'booking' | 'gift_voucher';
  display_text: string;
  secondary_text: string;
}

export interface ClientResult extends SearchResult {
  type: 'client';
  name: string;
  surname: string;
  phone_number: string;
  email: string;
  created_at: string | null;
}

export interface BookingResult extends SearchResult {
  type: 'booking';
  internal_order_id: string;
  book_date: string | null;
  hour: string | null;
  people: number;
  client: {
    id: number;
    name: string;
    surname: string;
    phone_number: string;
    email: string;
  };
  product_name: string;
  amount_paid: string;
  amount_pending: string;
  checked_in: boolean;
  checked_out: boolean;
}

export interface GiftVoucherResult extends SearchResult {
  type: 'gift_voucher';
  code: string;
  price: string;
  used: boolean;
  status: 'pending_payment' | 'paid' | 'used';
  bought_date: string | null;
  recipient: {
    name: string;
    surname: string;
    email: string;
  };
  buyer_client: {
    id: number;
    name: string;
    surname: string;
    phone_number: string;
    email: string;
  };
  product_id: number;
  product_name: string;
  gift_name: string;
  people: number;
  product_baths: Array<{
    massage_type: 'relax' | 'rock' | 'exfoliation' | 'none';
    massage_duration: '15' | '30' | '60' | '0';
    quantity: number;
  }>;
}

export interface GeneralSearchResponse {
  success: boolean;
  query: string;
  total_results: number;
  results: {
    clients: ClientResult[];
    bookings: BookingResult[];
    gift_vouchers: GiftVoucherResult[];
  };
}

export interface ClientAutocompleteData {
  name: string;
  surname: string;
  phone_number: string;
  email: string;
}

export interface ClientAutocompleteResponse {
  success: boolean;
  client_data?: ClientAutocompleteData;
  error?: string;
}

export const generalSearchService = {
  async search(term: string): Promise<GeneralSearchResponse> {
    const response = await axios.get(`${BASE_URL}/busqueda-general/`, {
      params: { q: term }
    });
    return response.data;
  },

  async getClientDataForAutocomplete(clientId: number): Promise<ClientAutocompleteResponse> {
    const response = await axios.get(`${BASE_URL}/busqueda-general/`, {
      params: { autocomplete_client: clientId }
    });
    return response.data;
  }
}; 