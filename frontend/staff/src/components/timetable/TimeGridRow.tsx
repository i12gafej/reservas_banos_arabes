import React, { useState, useRef, forwardRef, useImperativeHandle } from 'react';
import './timetable.css';

export interface TimeGridRowProps {
  /** Etiqueta mostrada en la primera columna */
  label: React.ReactNode;
  /** Array de valores a mostrar en cada intervalo (misma longitud que times) */
  values?: (string | number | React.ReactNode)[];
  /** Tiempo generado por TimeGrid */
  times: string[];
  /** Indica si la fila es editable */
  editable?: boolean;
  /** Callback cuando cambia la selección (solo editable) */
  onSelectionChange?: (indices: number[]) => void;
  /** Callback para actualizar valores; recibe nuevo array completo */
  onValuesChange?: (newValues: (string | number | React.ReactNode)[]) => void;
}

export interface TimeGridRowHandle {
  clearSelection: () => void;
  selectAll: () => void;
  replaceSelected: (kind: 'zero' | 'custom', value?: number) => void;
  getSelectionCount: () => number;
}

const TimeGridRow = forwardRef<TimeGridRowHandle, TimeGridRowProps>(({
  label,
  values = [],
  times,
  editable = false,
  onSelectionChange,
  onValuesChange,
}, ref) => {
  const [selected, setSelected] = useState<Set<number>>(new Set());
  const isSelectingRef = useRef(false);
  const startIndexRef = useRef<number | null>(null);

  // ----------------------------------------------
  // Helpers
  // ----------------------------------------------
  const notify = (newSel: Set<number>) => {
    if (onSelectionChange) {
      onSelectionChange(Array.from(newSel.values()).sort((a, b) => a - b));
    }
  };

  // ----------------------------------------------
  // Handlers selección
  // ----------------------------------------------
  const beginSelect = (idx: number) => {
    if (!editable) return;
    const newSel = new Set([idx]);
    setSelected(newSel);
    notify(newSel);
    isSelectingRef.current = true;
    startIndexRef.current = idx;
  };

  const extendSelect = (idx: number) => {
    if (!editable || !isSelectingRef.current || startIndexRef.current === null) return;
    const [a, b] = [startIndexRef.current, idx].sort((x, y) => x - y);
    const newSel = new Set<number>();
    for (let i = a; i <= b; i++) newSel.add(i);
    setSelected(newSel);
    notify(newSel);
  };

  const endSelect = () => {
    isSelectingRef.current = false;
    startIndexRef.current = null;
  };

  const toggleSelect = (idx: number) => {
    if (!editable) return;
    const newSel = new Set(selected);
    if (newSel.has(idx)) newSel.delete(idx);
    else newSel.add(idx);
    setSelected(newSel);
    notify(newSel);
  };

  // ----------------------------------------------
  // Toolbar actions
  // ----------------------------------------------
  const handleSelectAll = () => {
    const all = new Set<number>();
    for (let i = 0; i < times.length; i++) all.add(i);
    setSelected(all);
    notify(all);
  };

  const handleClear = () => {
    setSelected(new Set());
    notify(new Set());
  };

  // --------------------------------------------------------------
  // Reemplazar valores
  // --------------------------------------------------------------
  const replaceSelected = (kind: 'zero' | 'custom', value = 0) => {
    if (!editable || selected.size === 0 || !onValuesChange) return;
    const newVals = [...values];
    selected.forEach((idx) => {
      if (kind === 'zero') newVals[idx] = 0;
      else if (kind === 'custom') newVals[idx] = value;
    });
    onValuesChange(newVals);
  };

  // expose methods
  useImperativeHandle(ref, () => ({
    clearSelection: handleClear,
    selectAll: handleSelectAll,
    replaceSelected,
    getSelectionCount: () => selected.size,
  }));

  // ----------------------------------------------
  // Render
  // ----------------------------------------------
  React.useEffect(() => {
    if (!editable) return;

    const handleKey = (e: KeyboardEvent) => {
      if (selected.size === 0) return;
      // Evitar si el foco está en un input/textarea/select
      const tag = (e.target as HTMLElement).tagName.toLowerCase();
      if (['input', 'textarea', 'select'].includes(tag)) return;

      if (e.key >= '0' && e.key <= '9') {
        const num = Number(e.key);
        const newVals = [...values];
        selected.forEach((idx) => (newVals[idx] = num));
        onValuesChange?.(newVals);
      }
    };

    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, [selected, values, editable, onValuesChange]);

  return (
    <tr
      className={editable ? 'tg-row-editable' : 'tg-row'}
      onMouseLeave={() => {
        // Si sale del row con botón presionado mantén selección
      }}
    >
      {/* Label col */}
      <th className="tg-label-col tg-sticky-left">{label}</th>

      {/* Celulas */}
      {times.map((t, idx) => {
        const content = values[idx] ?? '';
        const isSel = selected.has(idx);
        return (
          <td
            key={t}
            className={`tg-cell ${isSel ? 'tg-cell-selected' : ''}`}
            onMouseDown={(e) => {
              if (e.button !== 0) return; // left click only
              if (selected.size > 0 && !isSelectingRef.current && !editable) return;
              if (e.shiftKey) beginSelect(idx);
              else if (!isSelectingRef.current) {
                toggleSelect(idx);
                beginSelect(idx);
              }
            }}
            onMouseEnter={() => extendSelect(idx)}
            onMouseUp={endSelect}
            onDoubleClick={() => {
              if (!editable) return;
              // si la celda doble clic ya está seleccionada, usamos conjunto actual; sino solo esa
              const targetSet = selected.has(idx) ? selected : new Set([idx]);
              if (targetSet.size === 0) return;
              const input = prompt('Introduce un número para asignar a las celdas seleccionadas');
              if (input === null) return; // cancelado
              const num = Number(input);
              if (Number.isNaN(num)) {
                alert('Debe introducir un número válido');
                return;
              }
              // Crear copia values y actualizar índices
              const newVals = [...values];
              targetSet.forEach((iSel) => {
                newVals[iSel] = num;
              });
              if (onValuesChange) onValuesChange(newVals);
            }}
          >
            {content}
          </td>
        );
      })}
    </tr>
  );
});

export default TimeGridRow;
