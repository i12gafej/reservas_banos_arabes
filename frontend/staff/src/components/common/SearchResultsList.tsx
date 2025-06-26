import React from 'react';
import { SearchResult, ClientResult, BookingResult, GiftVoucherResult } from '@/services/general-search.service';
import ReactiveButton from 'reactive-button';
import './search-results-list.css';

interface SearchResultsListProps {
  results: SearchResult[];
  onClientSelect?: (clientData: {
    name: string;
    surname: string;
    phone_number: string;
    email: string;
  }) => void;
  onGiftVoucherSelect?: (giftVoucherId: number, clientData: {
    name: string;
    surname: string;
    phone_number: string;
    email: string;
  }) => void;
  onClose: () => void;
}

const SearchResultsList: React.FC<SearchResultsListProps> = ({
  results,
  onClientSelect,
  onGiftVoucherSelect,
  onClose
}) => {
  // Manejar autocompletado de cliente
  const handleClientAutocomplete = (clientData: {
    name: string;
    surname: string;
    phone_number: string;
    email: string;
  }) => {
    if (onClientSelect) {
      onClientSelect(clientData);
      onClose();
    }
  };

  // Manejar autocompletado de cheque regalo
  const handleGiftVoucherAutocomplete = (giftVoucherId: number, clientData: {
    name: string;
    surname: string;
    phone_number: string;
    email: string;
  }) => {
    if (onGiftVoucherSelect) {
      onGiftVoucherSelect(giftVoucherId, clientData);
      onClose();
    }
  };

  // Obtener icono según el tipo de resultado
  const getResultIcon = (type: string) => {
    switch (type) {
      case 'client':
        return '👤';
      case 'booking':
        return '📅';
      case 'gift_voucher':
        return '🎁';
      default:
        return '📄';
    }
  };

  // Renderizar elemento de cliente
  const renderClientItem = (result: ClientResult) => (
    <div key={`client-${result.id}`} className="search-result-item">
      <div className="result-header">
        <span className="result-icon">{getResultIcon(result.type)}</span>
        <span className="result-type-badge">Cliente</span>
      </div>
      <div className="result-content">
        <h4>{result.name} {result.surname}</h4>
        <p>Teléfono: {result.phone_number || 'N/A'}</p>
        <p>Email: {result.email || 'N/A'}</p>
      </div>
      <div className="result-actions">
        <ReactiveButton
          style={{ backgroundColor: 'var(--color-primary)' }}
          idleText="Autocompletar"
          onClick={() => handleClientAutocomplete({
            name: result.name,
            surname: result.surname,
            phone_number: result.phone_number,
            email: result.email
          })}
          size="small"
        />
      </div>
    </div>
  );

  // Renderizar elemento de reserva
  const renderBookingItem = (result: BookingResult) => (
    <div key={`booking-${result.id}`} className="search-result-item">
      <div className="result-header">
        <span className="result-icon">{getResultIcon(result.type)}</span>
        <span className="result-type-badge">Reserva</span>
      </div>
      <div className="result-content">
        <h4>#{result.internal_order_id}</h4>
        <p>Producto: {result.product_name}</p>
        <p>Cliente: {result.client.name} {result.client.surname}</p>
        <p>Fecha: {result.book_date} - {result.hour}</p>
      </div>
      <div className="result-actions">
        <ReactiveButton
          style={{ backgroundColor: 'var(--color-primary)' }}
          idleText="Autocomp. info. cliente"
          onClick={() => handleClientAutocomplete({
            name: result.client.name,
            surname: result.client.surname,
            phone_number: result.client.phone_number,
            email: result.client.email
          })}
          size="small"
        />
      </div>
    </div>
  );

  // Renderizar elemento de cheque regalo
  const renderGiftVoucherItem = (result: GiftVoucherResult) => (
    <div key={`voucher-${result.id}`} className="search-result-item">
      <div className="result-header">
        <span className="result-icon">{getResultIcon(result.type)}</span>
        <span className="result-type-badge">Cheque Regalo</span>
      </div>
      <div className="result-content">
        <h4>#{result.code} - {result.gift_name}</h4>
        <p><strong>Comprador:</strong> {result.buyer_client.name} {result.buyer_client.surname}</p>
        <p>Email comprador: {result.buyer_client.email || 'N/A'}</p>
        {result.recipient.name && (
          <>
            <p><strong>Destinatario:</strong> {result.recipient.name} {result.recipient.surname}</p>
            <p>Email destinatario: {result.recipient.email || 'N/A'}</p>
          </>
        )}
      </div>
      <div className="result-actions">
        <ReactiveButton
          style={{ backgroundColor: 'var(--color-primary)', marginRight: '0.5rem' }}
          idleText="Autocomp. comprador"
          onClick={() => handleGiftVoucherAutocomplete(result.id, {
            name: result.buyer_client.name,
            surname: result.buyer_client.surname,
            phone_number: result.buyer_client.phone_number,
            email: result.buyer_client.email
          })}
          size="small"
        />
        {result.recipient.name && (
          <ReactiveButton
            style={{ backgroundColor: 'var(--color-secondary)' }}
            idleText="Autocomp. recibidor"
            onClick={() => handleGiftVoucherAutocomplete(result.id, {
              name: result.recipient.name,
              surname: result.recipient.surname,
              phone_number: '',
              email: result.recipient.email
            })}
            size="small"
          />
        )}
      </div>
    </div>
  );

  if (results.length === 0) {
    return (
      <div className="no-results">
        <p>No se encontraron resultados</p>
      </div>
    );
  }

  return (
    <div className="search-results-list">
      {results.map((result) => {
        switch (result.type) {
          case 'client':
            return renderClientItem(result as ClientResult);
          case 'booking':
            return renderBookingItem(result as BookingResult);
          case 'gift_voucher':
            return renderGiftVoucherItem(result as GiftVoucherResult);
          default:
            return null;
        }
      })}
    </div>
  );
};

export default SearchResultsList; 