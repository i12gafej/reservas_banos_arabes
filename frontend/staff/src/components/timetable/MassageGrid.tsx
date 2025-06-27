import React from 'react';
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
}

const MassageGrid: React.FC<MassageGridProps> = ({ reservations }) => {
  // Filtrar solo reservas con masajes y ordenar por hora
  const massageReservations = reservations
    .filter(reservation => reservation.massages && reservation.massages.trim() !== '')
    .sort((a, b) => a.hour.localeCompare(b.hour));

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
      <h4>Masajes del día ({massageReservations.length} reservas)</h4>
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
    </div>
  );
};

export default MassageGrid;
