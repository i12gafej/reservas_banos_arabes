import React from 'react';
import { useRef, useState } from 'react';
import './timetable.css';
import TimeGridRow, { TimeGridRowProps, TimeGridRowHandle } from './TimeGridRow';
import ReactiveButton from 'reactive-button';

// Genera array de tiempos "HH:MM" desde start hasta end inclusive cada step minutos
function generateTimes(start: string, end: string, stepMinutes: number): string[] {
  const [startH, startM] = start.split(':').map(Number);
  const [endH, endM] = end.split(':').map(Number);
  const result: string[] = [];
  let minutes = startH * 60 + startM;
  const endTotal = endH * 60 + endM;
  while (minutes <= endTotal) {
    const h = Math.floor(minutes / 60)
      .toString()
      .padStart(2, '0');
    const m = (minutes % 60).toString().padStart(2, '0');
    result.push(`${h}:${m}`);
    minutes += stepMinutes;
  }
  return result;
}

export interface TimeGridProps {
  rows: (Omit<TimeGridRowProps, 'times'> & { key?: React.Key })[];
  /** Hora inicial en formato HH:MM */
  start?: string;
  /** Hora final en formato HH:MM (inclusive) */
  end?: string;
  /** Paso en minutos (por defecto 30) */
  stepMinutes?: number;
  /** Ancho fijo de columna en píxeles (aplicado vía CSS variable) */
  columnWidth?: number;
}

const TimeGrid: React.FC<TimeGridProps> = ({
  rows,
  start = '10:00',
  end = '22:00',
  stepMinutes = 30,
  columnWidth = 40,
}) => {
  const times = React.useMemo(
    () => generateTimes(start, end, stepMinutes),
    [start, end, stepMinutes]
  );

  const rowRef = useRef<TimeGridRowHandle | null>(null);
  const [selectionCount, setSelectionCount] = useState(0);

  const handleSelectionChange = (indices: number[]) => {
    setSelectionCount(indices.length);
  };

  // insert selectionChange to first row if editable
  const mappedRows = rows.map((r, idx) => {
    if (idx === 0 && r.editable) {
      return { ...r, onSelectionChange: handleSelectionChange };
    }
    return r;
  });

  // --col-width CSS variable para celdas
  const style: React.CSSProperties = {
    '--col-width': `${columnWidth}px`,
  } as React.CSSProperties;

  return (
    <div className="tg-wrapper" style={style}>
      
      <table className="tg-table">
        <thead>
          <tr>
            <th className="tg-label-col"></th>
            {times.map((t) => (
              <th key={t} className="tg-time-col">
                {t}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {mappedRows.map((rowProps, idx) => (
            <TimeGridRow
              ref={idx === 0 && rowProps.editable ? rowRef : undefined}
              key={rowProps.key ?? idx}
              times={times}
              {...rowProps}
            />
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default TimeGrid;
