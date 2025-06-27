import React, { useState } from 'react';
import MassagePrintView from './MassagePrintView';
import './massage-grid.css';

export interface MassageReservation {
  id: number;
  clientName: string;
  clientPhone: string;
  hour: string;
  people: number;
  comment: string;
  massages: string; // Formato: "2x Relajante 60', 1x Exfoliante 30'"
}

interface MassageGridProps {
  reservations: MassageReservation[];
  selectedDate?: string; // Añadir fecha para el listado de impresión
}

const MassageGrid: React.FC<MassageGridProps> = ({ reservations, selectedDate }) => {
  const [showPrintView, setShowPrintView] = useState(false);
  
  // Filtrar solo reservas con masajes y ordenar por hora
  const massageReservations = reservations
    .filter(reservation => reservation.massages && reservation.massages.trim() !== '')
    .sort((a, b) => a.hour.localeCompare(b.hour));

  const handlePrintList = () => {
    setShowPrintView(true);
  };

  const handleClosePrintView = () => {
    setShowPrintView(false);
  };

  if (massageReservations.length === 0) {
    return (
      <div className="massage-grid-container">
        <h4>Masajes del día</h4>
        <p className="no-massages-message">No hay reservas con masajes para este día</p>
      </div>
    );
  }

  return (
    <div className="massage-grid-container">
      <div className="massage-grid-header">
        <h4>Masajes del día ({massageReservations.length} reservas)</h4>
        <button
          onClick={handlePrintList}
          className="print-button"
          title="Imprimir listado diario de masajes"
        >
          🖨️ Imprimir listado diario
        </button>
      </div>
      <div className="massage-books-table-wrapper">
        <table className="massage-books-table">
          <thead>
            <tr>
              <th>Nombre Cliente</th>
              <th>Hora de Llegada</th>
              <th>Teléfono</th>
              <th>Masajes</th>
              <th>Comentarios</th>
              <th>Personas</th>
            </tr>
          </thead>
          <tbody>
            {massageReservations.map((reservation) => (
              <tr key={reservation.id}>
                <td className="client-name">{reservation.clientName}</td>
                <td className="arrival-time">{reservation.hour}</td>
                <td className="client-phone">{reservation.clientPhone || 'N/A'}</td>
                <td className="massages">{reservation.massages}</td>
                <td className="comments">{reservation.comment || '-'}</td>
                <td className="people">{reservation.people}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      
      {/* Modal de vista de impresión */}
      {showPrintView && (
        <MassagePrintView
          reservations={massageReservations}
          date={selectedDate || new Date().toISOString().split('T')[0]}
          onClose={handleClosePrintView}
        />
      )}
    </div>
  );
};

export default MassageGrid;
