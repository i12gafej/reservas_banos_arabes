import React from 'react';
import { MassageReservation } from './MassageGrid';
import './massage-print-view.css';

interface MassagePrintViewProps {
  reservations: MassageReservation[];
  date: string;
  onClose: () => void;
}

const MassagePrintView: React.FC<MassagePrintViewProps> = ({ reservations, date, onClose }) => {
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('es-ES', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const handlePrint = () => {
    // Crear una nueva ventana para impresión
    const printWindow = window.open('', '_blank');
    if (!printWindow) {
      alert('No se pudo abrir la ventana de impresión. Por favor, permite las ventanas emergentes.');
      return;
    }

    // Obtener el contenido del listado
    const printContent = document.querySelector('.print-content');
    if (!printContent) {
      alert('Error: No se encontró el contenido para imprimir.');
      printWindow.close();
      return;
    }

    // Crear el HTML completo para la ventana de impresión
    const htmlContent = `
      <!DOCTYPE html>
      <html lang="es">
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Listado de Masajes - ${formatDate(date)}</title>
        <style>
          /* Reset básico */
          * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
          }

          body {
            font-family: 'Arial', sans-serif;
            background: white;
            color: #000;
            -webkit-print-color-adjust: exact;
            color-adjust: exact;
            print-color-adjust: exact;
          }

          /* Configuración de página */
          @page {
            size: A4;
            margin: 15mm;
          }

          .print-page {
            page-break-after: always;
            display: flex;
            flex-direction: column;
            min-height: 250mm;
            width: 100%;
          }

          .print-page:last-child {
            page-break-after: avoid;
          }

          /* Header */
          .print-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 1.5rem;
            padding-bottom: 1rem;
            border-bottom: 2px solid #333;
          }

          .spa-info h1 {
            margin: 0;
            font-size: 2rem;
            font-weight: bold;
            color: #2c3e50;
            text-transform: uppercase;
            letter-spacing: 1px;
          }

          .spa-info h2 {
            margin: 0.5rem 0 0 0;
            font-size: 1.2rem;
            color: #34495e;
            font-weight: normal;
          }

          .date-info {
            text-align: right;
          }

          .print-date {
            margin: 0;
            font-size: 1.1rem;
            font-weight: bold;
            color: #2c3e50;
            text-transform: capitalize;
          }

          .page-info {
            margin: 0.5rem 0 0 0;
            font-size: 0.9rem;
            color: #7f8c8d;
            font-style: italic;
          }

          /* Tabla */
          .print-table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: auto;
            font-size: 0.75rem;
          }

          .print-table th {
            background: #34495e;
            color: white;
            padding: 0.5rem 0.4rem;
            text-align: left;
            font-weight: bold;
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border: 1px solid #2c3e50;
          }

          .print-table td {
            padding: 0.4rem 0.3rem;
            border: 1px solid #bdc3c7;
            vertical-align: top;
            line-height: 1.3;
          }

          .even-row {
            background: #f8f9fa;
          }

          .odd-row {
            background: white;
          }

          /* Estilos específicos por columna */
          .hour-cell {
            font-family: 'Courier New', monospace;
            font-weight: bold;
            font-size: 0.8rem;
            text-align: center;
            width: 8%;
            color: #27ae60;
          }

          .client-cell {
            font-weight: 600;
            width: 20%;
            color: #2c3e50;
          }

          .phone-cell {
            font-family: 'Courier New', monospace;
            font-size: 0.7rem;
            width: 12%;
            color: #7f8c8d;
          }

          .people-cell {
            text-align: center;
            font-weight: bold;
            width: 8%;
            color: #3498db;
          }

          .massages-cell {
            width: 25%;
            font-weight: 500;
            color: #8e44ad;
            line-height: 1.4;
            font-size: 0.75rem;
          }

          .comments-cell {
            width: 27%;
            font-style: italic;
            color: #7f8c8d;
            font-size: 0.7rem;
            line-height: 1.2;
          }

          /* Footer */
          .print-footer {
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
            margin-top: 1rem;
            padding-top: 1rem;
            border-top: 1px solid #bdc3c7;
            font-size: 0.7rem;
            color: #7f8c8d;
          }

          .footer-left p,
          .footer-right p {
            margin: 0.25rem 0;
          }

          .footer-left strong {
            color: #2c3e50;
          }

          .footer-right {
            text-align: right;
          }

          /* Estilo para pantalla en la ventana de impresión */
          @media screen {
            body {
              padding: 20px;
            }
            .print-page {
              margin-bottom: 40px;
              border: 1px solid #ddd;
              padding: 20px;
              box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
          }
        </style>
      </head>
      <body>
        ${printContent.innerHTML}
        <script>
          // Imprimir automáticamente cuando se carga la página
          window.onload = function() {
            window.focus();
            // Dar un pequeño delay para asegurar que los estilos se carguen
            setTimeout(function() {
              window.print();
              // Cerrar la ventana después de imprimir (opcional)
              // window.onafterprint = function() { window.close(); };
            }, 500);
          };
        </script>
      </body>
      </html>
    `;

    try {
      // Escribir el contenido en la nueva ventana
      printWindow.document.write(htmlContent);
      printWindow.document.close();
    } catch (error) {
      console.error('Error al generar el contenido de impresión:', error);
      alert('Error al preparar la impresión. Por favor, inténtalo de nuevo.');
      printWindow.close();
    }
  };

  // Agrupar reservas por página (aproximadamente 15-20 por página)
  const reservationsPerPage = 15;
  const totalPages = Math.ceil(reservations.length / reservationsPerPage);
  
  const getPageReservations = (pageIndex: number) => {
    const startIndex = pageIndex * reservationsPerPage;
    const endIndex = startIndex + reservationsPerPage;
    return reservations.slice(startIndex, endIndex);
  };

  return (
    <div className="massage-print-overlay">
      {/* Botones de control - Solo visible en pantalla */}
      <div className="print-controls no-print">
        <div className="print-controls-header">
          <h3>Vista previa de impresión - Listado de masajes</h3>
          <p>{formatDate(date)} - {reservations.length} reservas</p>
        </div>
        <div className="print-controls-buttons">
          <button onClick={handlePrint} className="print-btn">
            🖨️ Imprimir
          </button>
          <button onClick={onClose} className="close-btn">
            ✕ Cerrar
          </button>
        </div>
      </div>

      {/* Contenido para impresión */}
      <div className="print-content">
        {Array.from({ length: totalPages }, (_, pageIndex) => {
          const pageReservations = getPageReservations(pageIndex);
          const pageNumber = pageIndex + 1;
          
          return (
            <div key={pageIndex} className="print-page">
              {/* Encabezado de página */}
              <div className="print-header">
                <div className="spa-info">
                  <h1>Baños Árabes</h1>
                  <h2>Listado de Masajes del Día</h2>
                </div>
                <div className="date-info">
                  <p className="print-date">{formatDate(date)}</p>
                  <p className="page-info">Página {pageNumber} de {totalPages}</p>
                </div>
              </div>

              {/* Tabla de reservas */}
              <table className="print-table">
                <thead>
                  <tr>
                    <th>Hora</th>
                    <th>Cliente</th>
                    <th>Teléfono</th>
                    <th>Personas</th>
                    <th>Masajes</th>
                    <th>Comentarios</th>
                  </tr>
                </thead>
                <tbody>
                  {pageReservations.map((reservation, index) => (
                    <tr key={reservation.id} className={index % 2 === 0 ? 'even-row' : 'odd-row'}>
                      <td className="hour-cell">{reservation.hour}</td>
                      <td className="client-cell">{reservation.clientName}</td>
                      <td className="phone-cell">{reservation.clientPhone || 'N/A'}</td>
                      <td className="people-cell">{reservation.people}</td>
                      <td className="massages-cell">{reservation.massages}</td>
                      <td className="comments-cell">{reservation.comment || '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>

              {/* Pie de página */}
              <div className="print-footer">
                <div className="footer-left">
                  <p>Total de reservas: <strong>{reservations.length}</strong></p>
                  <p>Reservas en esta página: <strong>{pageReservations.length}</strong></p>
                </div>
                <div className="footer-right">
                  <p>Impreso el: {new Date().toLocaleDateString('es-ES')} a las {new Date().toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })}</p>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default MassagePrintView; 