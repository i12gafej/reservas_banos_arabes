import React from 'react';
import {
  Routes,
  Route,
  Navigate,
} from 'react-router-dom';

import Header from '@/components/layout/Header';
import { BackToTop } from '@/components/common';

import {
  CuadrantePage,
  MasajistasPage,
  ReservarPage,
  ChequesPage,
  ClientesPage,
  FacturacionPage,
  ProductosPage,
  GestionGeneralPage,
} from '@/pages';

const App: React.FC = () => {
  return (
    <div>
      <Header />
      <div style={{ padding: '1rem', maxWidth: 'var(--container-max)', margin: '0 auto' }}>
        <Routes>
          <Route path="/" element={<Navigate to="/cuadrante" replace />} />
          <Route path="/cuadrante" element={<CuadrantePage />} />
          <Route path="/masajistas" element={<MasajistasPage />} />
          <Route path="/reservas" element={<ReservarPage />} />
          <Route path="/cheques" element={<ChequesPage />} />
          <Route path="/clientes" element={<ClientesPage />} />
          <Route path="/facturacion" element={<FacturacionPage />} />
          <Route path="/productos" element={<ProductosPage />} />
          <Route path="/gestion" element={<GestionGeneralPage />} />
        </Routes>
      </div>
      <BackToTop />
    </div>
  );
};

export default App; 