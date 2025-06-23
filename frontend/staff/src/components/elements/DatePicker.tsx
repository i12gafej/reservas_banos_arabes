import React from 'react';
import ReactDatePicker from 'react-datepicker';
import { es } from 'date-fns/locale';
import 'react-datepicker/dist/react-datepicker.css';
import './react-datepicker-overrides.css';

// Wrapper con configuración corporativa

export interface DatePickerWrapperProps {
  value: Date | null | Date[];
  onChange: (date: Date | null | Date[]) => void;
  inline?: boolean;
  className?: string;
  placeholderText?: string;
  wrapperClassName?: string;
  multiselection?: boolean;
}

const DatePicker: React.FC<DatePickerWrapperProps> = ({ 
  value, 
  onChange, 
  inline, 
  wrapperClassName, 
  multiselection = false,
  ...rest 
}) => {
  const handleChange = (date: Date | Date[] | null) => {
    if (multiselection) {
      // Para selección múltiple, manejar la lógica de agregar/quitar fechas
      if (Array.isArray(value)) {
        if (date && !Array.isArray(date)) {
          // Verificar si la fecha ya está seleccionada
          const isAlreadySelected = value.some(selectedDate => 
            selectedDate.toDateString() === date.toDateString()
          );
          
          if (isAlreadySelected) {
            // Si ya está seleccionada, quitarla
            const newDates = value.filter(selectedDate => 
              selectedDate.toDateString() !== date.toDateString()
            );
            onChange(newDates);
          } else {
            // Si no está seleccionada, agregarla
            onChange([...value, date]);
          }
        } else if (Array.isArray(date)) {
          onChange(date);
        } else {
          onChange([]);
        }
      } else {
        // Si value no es array, convertir a array
        if (date && !Array.isArray(date)) {
          onChange([date]);
        } else if (Array.isArray(date)) {
          onChange(date);
        } else {
          onChange([]);
        }
      }
    } else {
      // Para selección única, devolver Date | null
      if (Array.isArray(date)) {
        onChange(date.length > 0 ? date[0] : null);
      } else {
        onChange(date);
      }
    }
  };

  // Para selección múltiple, usar el primer elemento como selected
  const getSelectedValue = (): Date | null => {
    if (multiselection) {
      if (Array.isArray(value)) {
        return value.length > 0 ? value[0] : null;
      } else if (value) {
        return value;
      } else {
        return null;
      }
    } else {
      if (Array.isArray(value)) {
        return value.length > 0 ? value[0] : null;
      } else {
        return value;
      }
    }
  };

  // Para selección múltiple, mostrar fechas ya seleccionadas como deshabilitadas
  const filterDate = (date: Date) => {
    if (!multiselection) return true;
    
    if (Array.isArray(value)) {
      // Permitir seleccionar fechas que ya están seleccionadas (para quitarlas)
      return true;
    }
    return true;
  };

  // Renderizar fechas seleccionadas en el calendario
  const renderDayContents = (day: number, date: Date) => {
    if (!multiselection || !Array.isArray(value)) {
      return day;
    }

    const isSelected = value.some(selectedDate => 
      selectedDate.toDateString() === date.toDateString()
    );

    if (isSelected) {
      return (
        <div style={{
          backgroundColor: '#007bff',
          color: 'white',
          borderRadius: '50%',
          width: '24px',
          height: '24px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '12px',
          fontWeight: 'bold'
        }}>
          {day}
        </div>
      );
    }

    return day;
  };

  return (
    <div>
      <ReactDatePicker
        locale={es}
        dateFormat="dd/MM/yyyy"
        selected={getSelectedValue()}
        onChange={handleChange}
        inline={inline}
        wrapperClassName={wrapperClassName}
        showMonthDropdown
        showYearDropdown
        dropdownMode="select"
        placeholderText="dd/mm/aaaa"
        isClearable={!multiselection}
        filterDate={multiselection ? filterDate : undefined}
        renderDayContents={multiselection ? renderDayContents : undefined}
        {...rest}
      />
      {multiselection && Array.isArray(value) && value.length > 0 && (
        <div style={{ marginTop: '0.5rem', fontSize: '0.8rem', color: '#666' }}>
          <strong>Fechas seleccionadas:</strong> {value.length}
          <div style={{ marginTop: '0.25rem' }}>
            {value.map((date, index) => (
              <span key={index} style={{ 
                display: 'inline-block', 
                marginRight: '0.5rem',
                padding: '0.25rem 0.5rem',
                backgroundColor: '#f8f9fa',
                borderRadius: '4px',
                fontSize: '0.75rem'
              }}>
                {date.toLocaleDateString('es-ES')}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default DatePicker; 