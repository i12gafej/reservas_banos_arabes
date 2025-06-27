import React, { useState, useRef, useEffect } from 'react';
import { generalSearchService, SearchResult, ClientResult, BookingResult, GiftVoucherResult } from '@/services/general-search.service';
import { DefaultDialog } from '@/components/elements';
import {SearchResultsList} from './index.ts';
import './general-search.css';

interface GeneralSearchProps {
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
  }, productBaths?: Array<{
    massage_type: 'relax' | 'rock' | 'exfoliation' | 'none';
    massage_duration: '15' | '30' | '60' | '0';
    quantity: number;
  }>, people?: number, productId?: number) => void;
  placeholder?: string;
}

const GeneralSearch: React.FC<GeneralSearchProps> = ({
  onClientSelect,
  onGiftVoucherSelect,
  placeholder = "Buscar por nombre, teléfono, email, ID de reserva..."
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showDialog, setShowDialog] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  // Función para realizar la búsqueda
  const performSearch = async (term: string) => {
    if (term.length < 2) {
      return;
    }

    setIsLoading(true);
    try {
      const response = await generalSearchService.search(term);
      if (response.success) {
        // Combinar todos los resultados en un solo array
        const allResults: SearchResult[] = [
          ...response.results.clients,
          ...response.results.bookings,
          ...response.results.gift_vouchers
        ];
        setResults(allResults);
        setShowDialog(true);
      }
    } catch (error) {
      console.error('Error en búsqueda general:', error);
      setResults([]);
    } finally {
      setIsLoading(false);
    }
  };

  // Manejar cambios en el input de búsqueda
  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value);
  };

  // Manejar tecla Enter para buscar
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      if (searchTerm.trim()) {
        performSearch(searchTerm.trim());
      }
    }
  };

  // Cerrar dialog
  const handleCloseDialog = () => {
    setShowDialog(false);
    setResults([]);
  };

  return (
    <>
      <div className="general-search">
        <div className="search-input-container">
          <input
            ref={inputRef}
            type="text"
            value={searchTerm}
            onChange={handleSearchChange}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            className="search-input"
          />
          {isLoading && <div className="search-loading">🔍</div>}
        </div>
        <p style={{ fontSize: '0.875rem', color: '#64748b', marginTop: '0.25rem' }}>
          Presiona Enter para buscar
        </p>
      </div>

      <DefaultDialog
        open={showDialog}
        title={`Resultados de búsqueda: "${searchTerm}"`}
        onClose={handleCloseDialog}
      >
        <SearchResultsList
          results={results}
          onClientSelect={onClientSelect}
          onGiftVoucherSelect={onGiftVoucherSelect}
          onClose={handleCloseDialog}
        />
      </DefaultDialog>
    </>
  );
};

export default GeneralSearch; 