import React, { useState, useMemo } from 'react';
import { useForm, Controller } from 'react-hook-form';
import DatePicker from 'react-datepicker';
import ReactiveButton from 'reactive-button';
import { DefaultDialog } from '@/components/elements';
import { getBookDetail, updateBookDetail, getBookLogs, createBookLog, BookDetail, BookLog, BookDetailUpdate } from '@/services/reservas.service';
import './book-grid.css';

export interface BookRow {
  id: string;
  clientName: string;
  clientId: number;
  clientInfo?: {
    name: string;
    surname: string;
    phone_number: string;
    email: string;
    created_at: string;
  };
  entryTime: string;
  people: number;
  isPaid: boolean;
  hasCheckout: boolean;
  isPastDate: boolean;
  createdAt: string;
}

interface BookGridProps {
  books: BookRow[];
  columnWidth?: number;
}

type SortField = 'entryTime' | 'clientName';
type SortDirection = 'asc' | 'desc';

interface BookEditForm {
  booking_date: Date | null;
  hour: string;
  people: number;
  comment: string;
  amount_paid: string;
  amount_pending: string;
  payment_date: Date | null;
  product_id: number;
}

const TIMES = Array.from({ length: 25 }, (_, i) => {
  const minutes = 10 * 60 + i * 30;
  const h = Math.floor(minutes / 60)
    .toString()
    .padStart(2, '0');
  const m = (minutes % 60).toString().padStart(2, '0');
  return `${h}:${m}`;
});

const BookGrid: React.FC<BookGridProps> = ({ books, columnWidth = 20 }) => {
  const [sortField, setSortField] = useState<SortField>('entryTime');
  const [sortDirection, setSortDirection] = useState<SortDirection>('asc');
  const [selectedClient, setSelectedClient] = useState<BookRow | null>(null);
  const [showClientDialog, setShowClientDialog] = useState(false);
  
  // Estados para el nuevo diálogo de edición
  const [showBookDetailDialog, setShowBookDetailDialog] = useState(false);
  const [bookDetail, setBookDetail] = useState<BookDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [showLogs, setShowLogs] = useState(false);
  const [logs, setLogs] = useState<BookLog[]>([]);
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);
  const [changePreview, setChangePreview] = useState('');
  const [customLogComment, setCustomLogComment] = useState('');

  // React Hook Form
  const { control, handleSubmit, reset, watch, formState: { isDirty } } = useForm<BookEditForm>();
  const formValues = watch();

  // Función para obtener el color de la celda según el estado de la reserva
  const getCellColor = (book: BookRow): string => {
    if (book.isPastDate || book.hasCheckout) {
      return '#ffeb3b'; // Amarillo
    } else if (book.isPaid) {
      return '#4caf50'; // Verde
    } else {
      return '#f44336'; // Rojo
    }
  };

  // Función para convertir hora de entrada a índice de columna
  const getTimeIndex = (time: string): number => {
    const timeStr = time.substring(0, 5); // Extraer HH:MM
    return TIMES.findIndex(t => t === timeStr);
  };

  // Función para ordenar las reservas
  const sortedBooks = useMemo(() => {
    return [...books].sort((a, b) => {
      let comparison = 0;
      
      if (sortField === 'entryTime') {
        const timeA = getTimeIndex(a.entryTime);
        const timeB = getTimeIndex(b.entryTime);
        comparison = timeA - timeB;
      } else if (sortField === 'clientName') {
        const dateA = new Date(a.createdAt).getTime();
        const dateB = new Date(b.createdAt).getTime();
        comparison = dateA - dateB;
      }
      
      return sortDirection === 'asc' ? comparison : -comparison;
    });
  }, [books, sortField, sortDirection]);

  // Función para manejar el clic en el header de ordenamiento
  const handleSortClick = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  // Función para generar las celdas de una fila
  const generateRowCells = (book: BookRow) => {
    const cells = Array(25).fill(0);
    const timeIndex = getTimeIndex(book.entryTime);
    
    if (timeIndex !== -1) {
      cells[timeIndex] = book.people;
    }
    
    return cells;
  };

  // Función para manejar el clic en el nombre del cliente
  const handleClientClick = (book: BookRow) => {
    setSelectedClient(book);
    setShowClientDialog(true);
  };

  // Función para abrir el diálogo de edición de reserva
  const handleBookCellClick = async (book: BookRow) => {
    try {
      setLoading(true);
      const detail = await getBookDetail(parseInt(book.id));
      setBookDetail(detail);
      
      // Resetear el formulario con los datos de la reserva
      reset({
        booking_date: detail.booking_date ? new Date(detail.booking_date) : null,
        hour: detail.hour || '',
        people: detail.people || 1,
        comment: detail.comment || '',
        amount_paid: detail.amount_paid || '',
        amount_pending: detail.amount_pending || '',
        payment_date: detail.payment_date ? new Date(detail.payment_date) : null,
        product_id: detail.product_id || 1,
      });
      
      setShowBookDetailDialog(true);
    } catch (error) {
      console.error('Error al cargar detalles de la reserva:', error);
      alert('Error al cargar los detalles de la reserva');
    } finally {
      setLoading(false);
    }
  };

  // Función para cargar logs
  const handleLoadLogs = async () => {
    if (!bookDetail) return;
    try {
      setLoading(true);
      const bookLogs = await getBookLogs(bookDetail.id);
      setLogs(bookLogs);
      setShowLogs(true);
    } catch (error) {
      console.error('Error al cargar logs:', error);
      alert('Error al cargar los registros de la reserva');
    } finally {
      setLoading(false);
    }
  };

  // Función para generar vista previa de cambios
  const generateChangePreview = () => {
    if (!bookDetail || !formValues) return '';
    
    const changes = [];
    
    const formBookingDate = formValues.booking_date ? formValues.booking_date.toISOString().split('T')[0] : '';
    if (formBookingDate !== bookDetail.booking_date) {
      changes.push(`Fecha modificada del día ${bookDetail.booking_date} al día ${formBookingDate}`);
    }
    if (formValues.hour !== bookDetail.hour) {
      changes.push(`Hora modificada de ${bookDetail.hour} a ${formValues.hour}`);
    }
    if (formValues.people !== bookDetail.people) {
      changes.push(`Pasa de ${bookDetail.people} a ${formValues.people} personas`);
    }
    
    const formPaymentDate = formValues.payment_date ? formValues.payment_date.toISOString() : null;
    if (formPaymentDate !== bookDetail.payment_date) {
      changes.push(`La fecha de pago cambia de ${bookDetail.payment_date || 'Sin fecha'} a ${formPaymentDate || 'Sin fecha'}`);
    }
    if (formValues.amount_paid !== bookDetail.amount_paid) {
      changes.push(`El importe pagado cambia de €${bookDetail.amount_paid} a €${formValues.amount_paid}`);
    }
    if (formValues.amount_pending !== bookDetail.amount_pending) {
      changes.push(`El importe a deber cambia de €${bookDetail.amount_pending} a €${formValues.amount_pending}`);
    }
    if (formValues.product_id !== bookDetail.product_id) {
      changes.push('Producto/masajes modificados');
    }
    
    return changes.length > 0 ? changes.join('. ') : 'Sin cambios detectados';
  };



  // Función para enviar el formulario
  const onSubmit = async (data: BookEditForm) => {
    if (!bookDetail) return;
    
    const preview = generateChangePreview();
    setChangePreview(preview);
    setShowConfirmDialog(true);
  };

  // Función para confirmar y guardar cambios
  const handleConfirmSave = async () => {
    if (!bookDetail || !formValues) return;
    try {
      setLoading(true);
      const updateData: BookDetailUpdate = {
        booking_date: formValues.booking_date ? formValues.booking_date.toISOString().split('T')[0] : undefined,
        hour: formValues.hour || undefined,
        people: formValues.people || undefined,
        comment: formValues.comment || undefined,
        amount_paid: formValues.amount_paid || undefined,
        amount_pending: formValues.amount_pending || undefined,
        payment_date: formValues.payment_date ? formValues.payment_date.toISOString() : null,
        product_id: formValues.product_id || undefined,
        log_comment: customLogComment || undefined,
      };
      
      const updated = await updateBookDetail(bookDetail.id, updateData);
      setBookDetail(updated);
      setShowConfirmDialog(false);
      setCustomLogComment('');
      alert('Reserva actualizada correctamente');
    } catch (error) {
      console.error('Error al actualizar reserva:', error);
      alert('Error al actualizar la reserva');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="book-grid">
      <table style={{ '--col-width': `${columnWidth}px` } as React.CSSProperties}>
        <thead>
          <tr>
            <th 
              className="sortable-header client-col"
              onClick={() => handleSortClick('clientName')}
            >
              Cliente
              {sortField === 'clientName' && (
                <span style={{ marginLeft: '2px' }}>
                  {sortDirection === 'asc' ? '↑' : '↓'}
                </span>
              )}
            </th>
            <th 
              className="sortable-header time-col"
              onClick={() => handleSortClick('entryTime')}
            >
              Hora
              {sortField === 'entryTime' && (
                <span style={{ marginLeft: '2px' }}>
                  {sortDirection === 'asc' ? '↑' : '↓'}
                </span>
              )}
            </th>
            {TIMES.map((time) => (
              <th key={time}>
                {time}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {sortedBooks.map((book) => {
            const cells = generateRowCells(book);
            const cellColor = getCellColor(book);
            
            return (
              <tr key={book.id}>
                <td 
                  className="client-col"
                  onClick={() => handleClientClick(book)}
                  style={{ cursor: 'pointer' }}
                >
                  {book.clientName}
                </td>
                <td className="time-col">
                  {book.entryTime.substring(0, 5)}
                </td>
                {cells.map((value, index) => (
                  <td
                    key={index}
                    style={{
                      backgroundColor: value > 0 ? cellColor : 'transparent',
                      color: value > 0 ? 'black' : 'inherit',
                      fontWeight: value > 0 ? 'bold' : 'normal',
                      cursor: value > 0 ? 'pointer' : 'default',
                    }}
                    onClick={value > 0 ? () => handleBookCellClick(book) : undefined}
                  >
                    {value > 0 ? value : ''}
                  </td>
                ))}
              </tr>
            );
          })}
        </tbody>
      </table>

      {/* Diálogo de información del cliente */}
      <DefaultDialog
        open={showClientDialog}
        onClose={() => setShowClientDialog(false)}
        title="Información del Cliente"
      >
        {selectedClient && (
          <div>
            <p><strong>Nombre:</strong> {selectedClient.clientInfo?.name || 'No disponible'}</p>
            <p><strong>Apellidos:</strong> {selectedClient.clientInfo?.surname || 'No disponible'}</p>
            <p><strong>Teléfono:</strong> {selectedClient.clientInfo?.phone_number || 'No disponible'}</p>
            <p><strong>Email:</strong> {selectedClient.clientInfo?.email || 'No disponible'}</p>
            <p><strong>Fecha de registro:</strong> {selectedClient.clientInfo?.created_at ? new Date(selectedClient.clientInfo.created_at).toLocaleDateString('es-ES') : 'No disponible'}</p>
            <hr style={{ margin: '1rem 0' }} />
            <p><strong>Reserva:</strong></p>
            <p><strong>ID de reserva:</strong> {selectedClient.id}</p>
            <p><strong>Hora de entrada:</strong> {selectedClient.entryTime.substring(0, 5)}</p>
            <p><strong>Personas:</strong> {selectedClient.people}</p>
            <p><strong>Estado de pago:</strong> {selectedClient.isPaid ? 'Pagado' : 'Pendiente'}</p>
            <p><strong>Check-in:</strong> {selectedClient.hasCheckout ? 'Completado' : 'Pendiente'}</p>
          </div>
        )}
      </DefaultDialog>

      {/* Diálogo de edición de reserva */}
      <DefaultDialog
        open={showBookDetailDialog}
        onClose={() => setShowBookDetailDialog(false)}
        title="Editar Reserva"
      >
        {bookDetail && (
          <div className="book-dialog-content">
            <div className="book-dialog-main-grid">
              {/* Información del cliente */}
              <div className="book-dialog-section book-section-cliente">
                <h3>Cliente</h3>
                <p><strong>Nombre:</strong> {bookDetail.client_name} {bookDetail.client_surname}</p>
                <p><strong>Teléfono:</strong> {bookDetail.client_phone || 'No disponible'}</p>
                <p><strong>Email:</strong> {bookDetail.client_email || 'No disponible'}</p>
                <p><strong>Registro:</strong> {new Date(bookDetail.client_created_at).toLocaleDateString('es-ES')}</p>
              </div>

              {/* Información del creador */}
              <div className="book-dialog-section book-section-creador">
                <h3>Creador</h3>
                <p><strong>Tipo:</strong> {bookDetail.creator_type_name}</p>
                <p><strong>Creador:</strong> {bookDetail.creator_name}</p>
              </div>

              {/* Botón de logs */}
              <div className="book-dialog-section book-section-registros">
                <ReactiveButton
                  buttonState={loading ? 'loading' : 'idle'}
                  onClick={handleLoadLogs}
                  idleText="Ver Registros"
                  loadingText="Cargando..."
                  style={{ backgroundColor: '#007bff', fontSize: '0.7rem' }}
                  className="book-dialog-button"
                />
              </div>

              {/* Formulario de edición - Datos de reserva */}
              <div className="book-dialog-section book-section-datos">
                <h3>Datos Reserva</h3>
                <form onSubmit={handleSubmit(onSubmit)}>
                  <div className="book-form-grid-single">
                    <div className="book-form-field book-form-field-date">
                      <label>Fecha:</label>
                      <Controller
                        control={control}
                        name="booking_date"
                        render={({ field }) => (
                          <DatePicker
                            selected={field.value}
                            onChange={field.onChange}
                            dateFormat="dd/MM/yyyy"
                            placeholderText="Seleccionar fecha"
                            className="book-form-field book-form-field-date input"
                          />
                        )}
                      />
                    </div>
                    
                    <div className="book-form-field">
                      <label>Hora:</label>
                      <Controller
                        control={control}
                        name="hour"
                        render={({ field }) => (
                          <select {...field} className="book-form-field book-form-field-hour input">
                            {Array.from({ length: 25 }, (_, i) => 10 * 60 + i * 30)
                              .filter((m) => m <= 22 * 60)
                              .map((m) => {
                                const h = Math.floor(m / 60);
                                const min = m % 60;
                                const label = `${h.toString().padStart(2, '0')}:${min.toString().padStart(2, '0')}`;
                                return (
                                  <option key={label} value={label}>
                                    {label}
                                  </option>
                                );
                              })}
                          </select>
                        )}
                      />
                    </div>
                    
                    <div className="book-form-field">
                      <label>Personas:</label>
                      <Controller
                        control={control}
                        name="people"
                        render={({ field }) => (
                          <input
                            {...field}
                            className="book-form-field book-form-field-people"
                            type="number"
                            min="1"
                            onChange={(e) => field.onChange(parseInt(e.target.value))}
                          />
                        )}
                      />
                    </div>
                    
                    <div className="book-custom-comment">
                      <label>Comentarios:</label>
                      <Controller
                        control={control}
                        name="comment"
                        render={({ field }) => (
                          <textarea {...field} className="book-form-field book-form-field-comment" />
                        )}
                      />
                    </div>
                  </div>
                </form>
              </div>

              {/* Matriz de masajes */}
              <div className="book-dialog-section book-section-masajes">
                <h3>Masajes Incluidos</h3>
                {bookDetail.product_baths && bookDetail.product_baths.length > 0 ? (
                  <div>
                    {bookDetail.product_baths.map((bath, index) => (
                      <div key={index} className="book-massage-item">
                        <strong>{bath.name}</strong> - {bath.massage_type} ({bath.massage_duration}min) x{bath.quantity}
                      </div>
                    ))}
                  </div>
                ) : (
                  <p>No hay masajes incluidos</p>
                )}
              </div>

              {/* Sección de pago */}
              <div className="book-dialog-section book-section-pago">
                <h3>Información de Pago</h3>
                <form onSubmit={handleSubmit(onSubmit)}>
                  <div className="book-form-grid">
                    <div className="book-form-field">
                      <label>Pagado (€):</label>
                      <Controller
                        control={control}
                        name="amount_paid"
                        render={({ field }) => (
                          <input {...field} type="number" step="0.01" />
                        )}
                      />
                    </div>
                    
                    <div className="book-form-field">
                      <label>Pendiente (€):</label>
                      <Controller
                        control={control}
                        name="amount_pending"
                        render={({ field }) => (
                          <input {...field} type="number" step="0.01" />
                        )}
                      />
                    </div>
                    
                    <div className="book-form-field">
                      <label>Fecha pago:</label>
                      <div className="payment-date-container">
                        <Controller
                          control={control}
                          name="payment_date"
                          render={({ field }) => (
                            <DatePicker
                              selected={field.value}
                              onChange={field.onChange}
                              showTimeSelect
                              timeFormat="HH:mm"
                              timeIntervals={1}
                              dateFormat="dd/MM/yyyy HH:mm"
                              placeholderText="Fecha y hora"
                              className="book-form-field input payment-date-picker"
                            />
                          )}
                        />
                        <ReactiveButton
                          buttonState="idle"
                          onClick={() => {
                            const now = new Date();
                            reset({
                              ...formValues,
                              payment_date: now
                            });
                          }}
                          idleText="Ahora"
                          style={{ 
                            backgroundColor: '#17a2b8', 
                            fontSize: '0.65rem',
                            padding: '0.2rem 0.4rem',
                            minWidth: 'auto'
                          }}
                        />
                      </div>
                    </div>
                  </div>

                  {/* Botones de acción */}
                  <div className="book-dialog-buttons">
                    <ReactiveButton
                      buttonState="idle"
                      onClick={() => setShowBookDetailDialog(false)}
                      idleText="Cancelar"
                      style={{ backgroundColor: '#6c757d' }}
                      className="book-dialog-button"
                    />
                    <ReactiveButton
                      buttonState={loading ? 'loading' : 'idle'}
                      type="submit"
                      idleText="Guardar"
                      loadingText="Guardando..."
                      style={{ backgroundColor: '#28a745' }}
                      className="book-dialog-button"
                    />
                  </div>
                </form>
              </div>
            </div>
          </div>
        )}
      </DefaultDialog>

      {/* Diálogo de logs */}
      <DefaultDialog
        open={showLogs}
        onClose={() => setShowLogs(false)}
        title="Registros de la Reserva"
      >
        <div className="book-logs-container">
          {logs.length > 0 ? (
            logs.map((log) => (
              <div key={log.id} className="book-log-item">
                <div className="book-log-date">{new Date(log.datetime).toLocaleString('es-ES')}</div>
                <p className="book-log-comment">{log.comment}</p>
              </div>
            ))
          ) : (
            <p>No hay registros disponibles para esta reserva</p>
          )}
        </div>
      </DefaultDialog>

      {/* Diálogo de confirmación */}
      <DefaultDialog
        open={showConfirmDialog}
        onClose={() => setShowConfirmDialog(false)}
        title="Confirmar Cambios"
      >
        <div className="book-dialog-content">
          <h4>Resumen de cambios:</h4>
          <div className="book-change-preview">
            {changePreview || 'Sin cambios detectados'}
          </div>
          
          <div className="book-custom-comment">
            <label>Comentario personalizado (opcional):</label>
            <textarea
              value={customLogComment}
              onChange={(e) => setCustomLogComment(e.target.value)}
              placeholder="Añadir comentario adicional al log..."
              rows={3}
            />
          </div>

          <div className="book-dialog-buttons">
            <ReactiveButton
              buttonState="idle"
              onClick={() => setShowConfirmDialog(false)}
              idleText="Cancelar"
              style={{ backgroundColor: '#6c757d' }}
              className="book-dialog-button"
            />
            <ReactiveButton
              buttonState={loading ? 'loading' : 'idle'}
              onClick={handleConfirmSave}
              idleText="Confirmar Cambios"
              loadingText="Guardando..."
              style={{ backgroundColor: '#007bff' }}
              className="book-dialog-button"
            />
          </div>
        </div>
      </DefaultDialog>
    </div>
  );
};

export default BookGrid;
