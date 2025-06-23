import React, { useState, useEffect, useMemo } from 'react';
import { DefaultDialog, DatePicker } from '@/components/elements';
import { TimeGrid } from '@/components/timetable';
import type { AvailabilityRange } from '@/services/masajistas.service';
import {
  getDayAvailability,
  saveAvailability,
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

const MasajistasPage: React.FC = () => {
  // Modo de selección
  const [mode, setMode] = useState<'date' | 'weekday'>('date');
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);
  const [selectedWeekday, setSelectedWeekday] = useState<number>(1);

  // Datos de disponibilidad
  const [cells, setCells] = useState<number[]>(Array(25).fill(0));
  const [infoMsg, setInfoMsg] = useState<string>('');

  // Diálogo confirmación
  const [openDlg, setOpenDlg] = useState(false);
  const [pendingSave, setPendingSave] = useState<'date' | 'weekday' | null>(null);

  // ------------------------------------------------------------------
  // Cargar disponibilidad cuando cambien selección
  // ------------------------------------------------------------------
  useEffect(() => {
    if (mode === 'date' && selectedDate) {
      console.log('[Masajistas] 📅 Modo "date" – fecha seleccionada:', {
        iso: selectedDate.toISOString(),
        local: selectedDate,
        weekdayJs: selectedDate.getDay(), // 0=Domingo…6=Sábado
      });
      getDayAvailability(selectedDate).then((av) => {
        console.log('[Masajistas] 📦 Respuesta availability (date):', av);
        if (av) {
          if (av.type === 'punctual') {
            setInfoMsg(
              `Ya existe una disponibilidad para el día ${selectedDate.toLocaleDateString()} definida manualmente.`,
            );
          } else if (av.type === 'weekday') {
            const name = weekdayNames[(av.weekday ?? 1) - 1];
            setInfoMsg(`Utiliza la disponibilidad de masajistas por defecto del ${name}.`);
          }
          setCells(rangesToCells(av.ranges));
        } else {
          setInfoMsg('No hay disponibilidad definida para ese día.');
          setCells(Array(25).fill(0));
        }
      });
    }
  }, [mode, selectedDate]);

  useEffect(() => {
    if (mode === 'weekday') {
      console.log('[Masajistas] 📅 Modo "weekday" – weekday seleccionado:', selectedWeekday);
      // Simular día para obtener disponibilidad
      const tempDate = new Date();
      const weekdayToDate = new Date(tempDate.setDate(tempDate.getDate() + (((selectedWeekday - 1 - (tempDate.getDay() + 6) % 7) + 7) % 7)));
      console.log('[Masajistas]  └─ fecha simulada para consulta:', {
        iso: weekdayToDate.toISOString(),
        local: weekdayToDate,
      });
      const iso = toLocalISODate(weekdayToDate);
      getDayAvailability(iso).then((av) => {
        console.log('[Masajistas] 📦 Respuesta availability (weekday):', av);
        if (av && av.type === 'weekday') {
          setInfoMsg(`Disponibilidad por defecto encontrada para ${weekdayNames[selectedWeekday - 1]}.`);
          setCells(rangesToCells(av.ranges));
        } else {
          setInfoMsg(`No hay disponibilidad definida para el ${weekdayNames[selectedWeekday - 1]}.`);
          setCells(Array(25).fill(0));
        }
      });
    }
  }, [mode, selectedWeekday]);

  // ------------------------------------------------------------------
  // Guardar
  // ------------------------------------------------------------------
  const handleSave = async () => {
    const ranges = cellsToRanges(cells);
    console.log('[Masajistas] 💾 Guardar – payload a enviar:', {
      pendingSave,
      selectedDate,
      selectedWeekday,
      ranges,
    });
    try {
      if (pendingSave === 'date' && selectedDate) {
        await saveAvailability({ date: selectedDate }, ranges);
      } else if (pendingSave === 'weekday') {
        await saveAvailability({ weekday: selectedWeekday }, ranges);
      }
    } catch (err) {
      // eslint-disable-next-line no-console
      console.error('Error guardando disponibilidad', err);
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
            <DatePicker value={selectedDate} onChange={setSelectedDate} />
          </div>
        ) : (
          <div style={{ marginTop: '0.5rem' }}>
            <select
              value={selectedWeekday}
              onChange={(e) => setSelectedWeekday(Number(e.target.value))}
            >
              {weekdayNames.map((n, idx) => (
                <option key={idx + 1} value={idx + 1}>
                  {n}
                </option>
              ))}
            </select>
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
        disabled={mode === 'date' && !selectedDate}
      />

      <DefaultDialog
        open={openDlg}
        onClose={() => setOpenDlg(false)}
        onSave={handleSave}
        title={
          pendingSave === 'weekday'
            ? `Guardar configuración para todos los ${weekdayNames[selectedWeekday - 1]}?`
            : `Guardar configuración para el día ${selectedDate?.toLocaleDateString()}`
        }
      >
        {pendingSave === 'weekday' ? (
          <p>
            ¿Seguro que quieres guardar esta configuración de masajistas para todos los{' '}
            {weekdayNames[selectedWeekday - 1]}?
          </p>
        ) : (
          <p>
            ¿Seguro que quieres guardar esta configuración concreta para el día{' '}
            {selectedDate?.toLocaleDateString()}?
          </p>
        )}
      </DefaultDialog>
    </div>
  );
};

export default MasajistasPage; 