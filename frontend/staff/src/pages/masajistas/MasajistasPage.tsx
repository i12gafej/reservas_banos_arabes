import React, { useState, useEffect, useMemo } from 'react';
import { DefaultDialog, DatePicker } from '@/components/elements';
import { TimeGrid } from '@/components/timetable';
import type { AvailabilityRange, AvailabilityHistoryItem } from '@/services/masajistas.service';
import {
  getDayAvailability,
  saveAvailability,
  getAvailabilityHistory,
  getAvailabilityById,
  createAvailabilityVersion,
} from '@/services/masajistas.service';
import './masajistas.css';
import ReactiveButton from 'reactive-button';
import { toLocalISODate } from '@/utils/date';

const TIMES = Array.from({ length: 25 }, (_, i) => {
  const minutes = 10 * 60 + i * 30;
  const h = Math.floor(minutes / 60)
    .toString()
    .padStart(2, '0');
  const m = (minutes % 60).toString().padStart(2, '0');
  return `${h}:${m}`;
});

// Utilidades para convertir entre rangos y celdas --------------------
function rangesToCells(ranges: AvailabilityRange[]): number[] {
  const cells = Array(25).fill(0);
  ranges.forEach((r) => {
    const startIdx = TIMES.findIndex((t) => t === r.initial_time.substring(0, 5));
    const endIdx = TIMES.findIndex((t) => t === r.end_time.substring(0, 5));
    if (startIdx === -1 || endIdx === -1) return;
    for (let i = startIdx; i < endIdx; i++) {
      cells[i] = r.massagists_availability;
    }
  });
  return cells;
}

function cellsToRanges(cells: number[]): AvailabilityRange[] {
  const ranges: AvailabilityRange[] = [];
  let i = 0;
  while (i < cells.length) {
    const val = cells[i];
    let j = i + 1;
    while (j < cells.length && cells[j] === val) j++;
    ranges.push({
      initial_time: `${TIMES[i]}:00`,
      end_time: `${TIMES[j] ?? '22:00'}:00`,
      massagists_availability: val,
    });
    i = j;
  }
  return ranges;
}

const weekdayNames = [
  'Lunes',
  'Martes',
  'Miércoles',
  'Jueves',
  'Viernes',
  'Sábado',
  'Domingo',
];

interface SelectedWeekday {
  weekday: number;
  name: string;
  availability: AvailabilityRange[];
  history: AvailabilityHistoryItem[];
  selectedHistoryId: number | null;
}

interface SelectedDate {
  date: Date;
  dateString: string;
  availability: AvailabilityRange[];
  history: AvailabilityHistoryItem[];
  selectedHistoryId: number | null;
}

const MasajistasPage: React.FC = () => {
  // Modo de selección
  const [mode, setMode] = useState<'date' | 'weekday'>('date');
  const [selectedDates, setSelectedDates] = useState<Date[]>([]);
  const [selectedWeekdays, setSelectedWeekdays] = useState<number[]>([]);

  // Datos de disponibilidad
  const [cells, setCells] = useState<number[]>(Array(25).fill(0));
  const [infoMsg, setInfoMsg] = useState<string>('');

  // Días de la semana seleccionados con sus datos
  const [selectedWeekdaysData, setSelectedWeekdaysData] = useState<SelectedWeekday[]>([]);
  const [activeWeekday, setActiveWeekday] = useState<number | null>(null);

  // Fechas seleccionadas con sus datos
  const [selectedDatesData, setSelectedDatesData] = useState<SelectedDate[]>([]);
  const [activeDate, setActiveDate] = useState<Date | null>(null);

  // Diálogo confirmación
  const [openDlg, setOpenDlg] = useState(false);
  const [pendingSave, setPendingSave] = useState<'date' | 'weekday' | null>(null);

  // ------------------------------------------------------------------
  // Cargar datos de fechas seleccionadas
  // ------------------------------------------------------------------
  useEffect(() => {
    if (mode === 'date' && selectedDates.length > 0) {
      const loadDatesData = async () => {
        const datesData: SelectedDate[] = [];
        
        for (const date of selectedDates) {
          console.log('[Masajistas] 📅 Cargando fecha:', date);
          const iso = toLocalISODate(date);
          
          try {
            // Obtener historial de disponibilidades
            const history = await getAvailabilityHistory(iso);
            console.log('[Masajistas] 📦 Historial de disponibilidades:', history);
            
            // Obtener disponibilidad actual
            const av = await getDayAvailability(iso);
            console.log('[Masajistas] 📦 Disponibilidad actual:', av);
            
            let currentAvailability: AvailabilityRange[] = [];
            let selectedHistoryId: number | null = null;
            
            if (av) {
              currentAvailability = av.ranges;
              // Si hay historial, seleccionar la más reciente
              if (history.length > 0) {
                selectedHistoryId = history[history.length - 1].id;
              }
            }
            
            datesData.push({
              date,
              dateString: date.toLocaleDateString('es-ES'),
              availability: currentAvailability,
              history: history,
              selectedHistoryId: selectedHistoryId,
            });
          } catch (error) {
            console.error(`Error cargando disponibilidad para ${date.toLocaleDateString()}:`, error);
            datesData.push({
              date,
              dateString: date.toLocaleDateString('es-ES'),
              availability: [],
              history: [],
              selectedHistoryId: null,
            });
          }
        }
        
        setSelectedDatesData(datesData);
        
        // Si no hay una fecha activa, seleccionar la primera
        if (!activeDate && datesData.length > 0) {
          setActiveDate(datesData[0].date);
          setCells(rangesToCells(datesData[0].availability));
          setInfoMsg(`Disponibilidad cargada para ${datesData[0].dateString}.`);
        }
      };
      
      loadDatesData();
    } else if (mode === 'date' && selectedDates.length === 0) {
      setSelectedDatesData([]);
      setActiveDate(null);
      setCells(Array(25).fill(0));
      setInfoMsg('Selecciona al menos una fecha.');
    }
  }, [mode, selectedDates, activeDate]);

  // ------------------------------------------------------------------
  // Cargar datos de días de la semana seleccionados
  // ------------------------------------------------------------------
  useEffect(() => {
    if (mode === 'weekday' && selectedWeekdays.length > 0) {
      const loadWeekdaysData = async () => {
        const weekdaysData: SelectedWeekday[] = [];
        
        for (const weekday of selectedWeekdays) {
          console.log('[Masajistas] 📅 Cargando weekday:', weekday);
          // Simular día para obtener disponibilidad
          const tempDate = new Date();
          const weekdayToDate = new Date(tempDate.setDate(tempDate.getDate() + (((weekday - 1 - (tempDate.getDay() + 6) % 7) + 7) % 7)));
          const iso = toLocalISODate(weekdayToDate);
          
          try {
            // Obtener historial de disponibilidades
            const history = await getAvailabilityHistory(iso);
            console.log('[Masajistas] 📦 Historial de disponibilidades:', history);
            
            // Obtener disponibilidad actual
            const av = await getDayAvailability(iso);
            console.log('[Masajistas] 📦 Disponibilidad actual:', av);
            
            let currentAvailability: AvailabilityRange[] = [];
            let selectedHistoryId: number | null = null;
            
            if (av) {
              currentAvailability = av.ranges;
              // Si hay historial, seleccionar la más reciente
              if (history.length > 0) {
                selectedHistoryId = history[history.length - 1].id;
              }
            }
            
            weekdaysData.push({
              weekday,
              name: weekdayNames[weekday - 1],
              availability: currentAvailability,
              history: history,
              selectedHistoryId: selectedHistoryId,
            });
          } catch (error) {
            console.error(`Error cargando disponibilidad para ${weekdayNames[weekday - 1]}:`, error);
            weekdaysData.push({
              weekday,
              name: weekdayNames[weekday - 1],
              availability: [],
              history: [],
              selectedHistoryId: null,
            });
          }
        }
        
        setSelectedWeekdaysData(weekdaysData);
        
        // Si no hay un día activo, seleccionar el primero
        if (!activeWeekday && weekdaysData.length > 0) {
          setActiveWeekday(weekdaysData[0].weekday);
          setCells(rangesToCells(weekdaysData[0].availability));
          setInfoMsg(`Disponibilidad cargada para ${weekdaysData[0].name}.`);
        }
      };
      
      loadWeekdaysData();
    } else if (mode === 'weekday' && selectedWeekdays.length === 0) {
      setSelectedWeekdaysData([]);
      setActiveWeekday(null);
      setCells(Array(25).fill(0));
      setInfoMsg('Selecciona al menos un día de la semana.');
    }
  }, [mode, selectedWeekdays, activeWeekday]);

  // ------------------------------------------------------------------
  // Cargar datos de una fecha específica en la tabla de edición
  // ------------------------------------------------------------------
  const loadDateData = (date: Date) => {
    const dateData = selectedDatesData.find(d => d.date.toDateString() === date.toDateString());
    if (dateData) {
      setActiveDate(date);
      setCells(rangesToCells(dateData.availability));
      setInfoMsg(`Disponibilidad cargada para ${dateData.dateString}.`);
    }
  };

  // ------------------------------------------------------------------
  // Cargar datos de un día específico en la tabla de edición
  // ------------------------------------------------------------------
  const loadWeekdayData = (weekday: number) => {
    const weekdayData = selectedWeekdaysData.find(w => w.weekday === weekday);
    if (weekdayData) {
      setActiveWeekday(weekday);
      setCells(rangesToCells(weekdayData.availability));
      setInfoMsg(`Disponibilidad cargada para ${weekdayData.name}.`);
    }
  };

  // ------------------------------------------------------------------
  // Cargar datos de un historial específico
  // ------------------------------------------------------------------
  const loadHistoryData = async (availabilityId: number) => {
    try {
      const availability = await getAvailabilityById(availabilityId);
      if (availability) {
        setCells(rangesToCells(availability.ranges));
        setInfoMsg(`Disponibilidad cargada del historial (${availability.created_at.substring(0, 10)}).`);
      }
    } catch (error) {
      console.error('Error cargando datos del historial:', error);
      setInfoMsg('Error cargando datos del historial.');
    }
  };

  // ------------------------------------------------------------------
  // Actualizar historial seleccionado para fechas
  // ------------------------------------------------------------------
  const updateSelectedDateHistory = (date: Date, historyId: number | null) => {
    setSelectedDatesData(prev => prev.map(d => 
      d.date.toDateString() === date.toDateString()
        ? { ...d, selectedHistoryId: historyId }
        : d
    ));
  };

  // ------------------------------------------------------------------
  // Actualizar historial seleccionado para días de la semana
  // ------------------------------------------------------------------
  const updateSelectedWeekdayHistory = (weekday: number, historyId: number | null) => {
    setSelectedWeekdaysData(prev => prev.map(w => 
      w.weekday === weekday 
        ? { ...w, selectedHistoryId: historyId }
        : w
    ));
  };

  // ------------------------------------------------------------------
  // Eliminar fecha seleccionada
  // ------------------------------------------------------------------
  const removeDate = (dateToRemove: Date) => {
    setSelectedDates(prev => prev.filter(date => date.toDateString() !== dateToRemove.toDateString()));
  };

  // ------------------------------------------------------------------
  // Guardar
  // ------------------------------------------------------------------
  const handleSave = async () => {
    const ranges = cellsToRanges(cells);
    console.log('[Masajistas] 💾 Guardar – payload a enviar:', {
      pendingSave,
      selectedDates,
      selectedWeekdays,
      ranges,
    });
    try {
      if (pendingSave === 'date' && selectedDates.length > 0) {
        // Guardar para todas las fechas seleccionadas
        for (const date of selectedDates) {
          await saveAvailability({ date }, ranges);
        }
      } else if (pendingSave === 'weekday') {
        // Guardar para todos los días de la semana seleccionados
        for (const weekday of selectedWeekdays) {
          await saveAvailability({ weekday }, ranges);
        }
      }
    } catch (err) {
      // eslint-disable-next-line no-console
      console.error('Error guardando disponibilidad', err);
    } finally {
      setOpenDlg(false);
      setPendingSave(null);
    }
  };

  // ------------------------------------------------------------------
  // Guardar nueva versión
  // ------------------------------------------------------------------
  const handleSaveNewVersion = async () => {
    const ranges = cellsToRanges(cells);
    const today = new Date();
    
    console.log('[Masajistas] 💾 Guardar nueva versión – payload a enviar:', {
      selectedDates,
      selectedWeekdays,
      ranges,
      effectiveDate: today,
    });
    
    try {
      if (pendingSave === 'date') {
        // Crear nueva versión para cada fecha seleccionada
        for (const date of selectedDates) {
          await createAvailabilityVersion(date, ranges, today);
        }
      } else if (pendingSave === 'weekday') {
        // Crear nueva versión para cada día seleccionado
        for (const weekday of selectedWeekdays) {
          // Simular día para obtener la fecha
          const tempDate = new Date();
          const weekdayToDate = new Date(tempDate.setDate(tempDate.getDate() + (((weekday - 1 - (tempDate.getDay() + 6) % 7) + 7) % 7)));
          
          await createAvailabilityVersion(weekdayToDate, ranges, today);
        }
      }
    } catch (err) {
      // eslint-disable-next-line no-console
      console.error('Error guardando nueva versión', err);
    } finally {
      setOpenDlg(false);
      setPendingSave(null);
    }
  };

  const confirmSave = (type: 'date' | 'weekday') => {
    setPendingSave(type);
    setOpenDlg(true);
  };

  // ------------------------------------------------------------------
  // Render
  // ------------------------------------------------------------------
  return (
    <div>
      <h2>Editar Masajistas</h2>

      {/* Selector de fecha o weekday */}
      <div className="card" style={{ maxWidth: 480 }}>
        <h3>Seleccionar día</h3>
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <label>
            <input
              type="radio"
              checked={mode === 'date'}
              onChange={() => setMode('date')}
            />{' '}
            Fecha puntual
          </label>
          <label>
            <input
              type="radio"
              checked={mode === 'weekday'}
              onChange={() => setMode('weekday')}
            />{' '}
            Día de la semana
          </label>
        </div>

        {mode === 'date' ? (
          <div style={{ marginTop: '0.5rem' }}>
            <DatePicker 
              value={selectedDates} 
              onChange={(dates) => setSelectedDates(Array.isArray(dates) ? dates : dates ? [dates] : [])}
              multiselection={true}
            />
            <p style={{ fontSize: '0.8rem', color: '#666', marginTop: '0.25rem' }}>
              Haz clic en las fechas para seleccionarlas. Puedes seleccionar múltiples fechas.
            </p>
          </div>
        ) : (
          <div style={{ marginTop: '0.5rem' }}>
            <select
              multiple
              value={selectedWeekdays.map(w => w.toString())}
              onChange={(e) => {
                const selectedOptions = Array.from(e.target.selectedOptions, option => Number(option.value));
                setSelectedWeekdays(selectedOptions);
              }}
              style={{ minHeight: '100px' }}
            >
              {weekdayNames.map((n, idx) => (
                <option key={idx + 1} value={idx + 1}>
                  {n}
                </option>
              ))}
            </select>
            <p style={{ fontSize: '0.8rem', color: '#666', marginTop: '0.25rem' }}>
              Mantén Ctrl (Cmd en Mac) para seleccionar múltiples días
            </p>
          </div>
        )}

        {infoMsg && <p style={{ marginTop: '0.75rem', color: '#555' }}>{infoMsg}</p>}
      </div>

      {/* TimeGrid */}
      <div style={{ marginTop: '1rem' }}>
        <TimeGrid
          rows={[{
            label: 'Masajistas',
            values: cells,
            editable: true,
            onSelectionChange: () => {},
            onValuesChange: (vals) => setCells(vals as number[]),
          }]}
          columnWidth={40}
        />
      </div>

      <ReactiveButton
        style={{ backgroundColor: 'var(--color-primary)', marginTop: '1rem' }}
        idleText="Guardar configuración"
        onClick={() => confirmSave(mode)}
        disabled={
          (mode === 'date' && selectedDates.length === 0) ||
          (mode === 'weekday' && selectedWeekdays.length === 0)
        }
      />

      {/* Tabla de fechas seleccionadas */}
      {mode === 'date' && selectedDatesData.length > 0 && (
        <div style={{ marginTop: '2rem' }}>
          <h3>Fechas seleccionadas</h3>
          <div className="card">
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid #ddd' }}>
                  <th style={{ padding: '0.5rem', textAlign: 'left' }}>Fecha</th>
                  
                  <th style={{ padding: '0.5rem', textAlign: 'left' }}>Estado</th>
                  <th style={{ padding: '0.5rem', textAlign: 'center' }}>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {selectedDatesData.map((dateData) => (
                  <tr
                    key={dateData.date.toISOString()}
                    style={{
                      borderBottom: '1px solid #eee',
                      backgroundColor: activeDate?.toDateString() === dateData.date.toDateString() ? '#f0f8ff' : 'transparent',
                    }}
                  >
                    <td 
                      style={{ padding: '0.5rem', cursor: 'pointer' }}
                      onClick={() => loadDateData(dateData.date)}
                    >
                      <strong>{dateData.dateString}</strong>
                    </td>
                    
                    <td style={{ padding: '0.5rem' }}>
                      {dateData.availability.length > 0 ? (
                        <span style={{ color: 'green' }}>✓ Configurado</span>
                      ) : (
                        <span style={{ color: 'orange' }}>⚠ Sin configuración</span>
                      )}
                    </td>
                    <td style={{ padding: '0.5rem', textAlign: 'center' }}>
                      <button
                        onClick={() => removeDate(dateData.date)}
                        style={{
                          background: 'none',
                          border: 'none',
                          color: '#d32f2f',
                          cursor: 'pointer',
                          fontSize: '1.2rem',
                          padding: '0.25rem',
                        }}
                        title="Eliminar fecha"
                      >
                        ✕
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Tabla de días de la semana seleccionados */}
      {mode === 'weekday' && selectedWeekdaysData.length > 0 && (
        <div style={{ marginTop: '2rem' }}>
          <h3>Días seleccionados</h3>
          <div className="card">
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid #ddd' }}>
                  <th style={{ padding: '0.5rem', textAlign: 'left' }}>Día</th>
                  <th style={{ padding: '0.5rem', textAlign: 'left' }}>Historial de disponibilidades</th>
                  <th style={{ padding: '0.5rem', textAlign: 'left' }}>Estado</th>
                </tr>
              </thead>
              <tbody>
                {selectedWeekdaysData.map((weekdayData) => (
                  <tr
                    key={weekdayData.weekday}
                    style={{
                      borderBottom: '1px solid #eee',
                      backgroundColor: activeWeekday === weekdayData.weekday ? '#f0f8ff' : 'transparent',
                    }}
                  >
                    <td 
                      style={{ padding: '0.5rem', cursor: 'pointer' }}
                      onClick={() => loadWeekdayData(weekdayData.weekday)}
                    >
                      <strong>{weekdayData.name}</strong>
                    </td>
                    <td style={{ padding: '0.5rem' }}>
                      {weekdayData.history.length > 0 ? (
                        <select
                          value={weekdayData.selectedHistoryId || ''}
                          onChange={(e) => {
                            const historyId = e.target.value ? Number(e.target.value) : null;
                            updateSelectedWeekdayHistory(weekdayData.weekday, historyId);
                            if (historyId) {
                              loadHistoryData(historyId);
                            } else {
                              loadWeekdayData(weekdayData.weekday);
                            }
                          }}
                          style={{ width: '100%', padding: '0.25rem' }}
                        >
                          <option value="">Disponibilidad actual</option>
                          {weekdayData.history.map((item) => (
                            <option key={item.id} value={item.id}>
                              {item.temporal_range}
                            </option>
                          ))}
                        </select>
                      ) : (
                        <span style={{ color: '#999' }}>Sin historial</span>
                      )}
                    </td>
                    <td style={{ padding: '0.5rem' }}>
                      {weekdayData.availability.length > 0 ? (
                        <span style={{ color: 'green' }}>✓ Configurado</span>
                      ) : (
                        <span style={{ color: 'orange' }}>⚠ Sin configuración</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      <DefaultDialog
        open={openDlg}
        onClose={() => setOpenDlg(false)}
        onSave={handleSaveNewVersion}
        title={
          pendingSave === 'weekday'
            ? `Guardar nueva configuración de masajistas`
            : `Guardar nueva configuración de masajistas`
        }
      >
        {pendingSave === 'weekday' ? (
          <div>
            <p>
              Si guardas esta disponibilidad, se aplicarán los cambios a partir del día de hoy,{' '}
              {new Date().toLocaleDateString('es-ES')}.
            </p>
            <p>¿Quieres modificar la disponibilidad de masajistas para los días: {selectedWeekdays.map(w => weekdayNames[w - 1]).join(', ')}?</p>
          </div>
        ) : (
          <div>
            <p>
              Si guardas esta disponibilidad, se aplicarán los cambios a partir del día de hoy,{' '}
              {new Date().toLocaleDateString('es-ES')}.
            </p>
            <p>¿Quieres modificar la disponibilidad de masajistas para las fechas: {selectedDates.map(d => d.toLocaleDateString('es-ES')).join(', ')}?</p>
          </div>
        )}
      </DefaultDialog>
    </div>
  );
};

export default MasajistasPage; 