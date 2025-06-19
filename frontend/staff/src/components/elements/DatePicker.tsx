import React from 'react';
import ReactDatePicker from 'react-datepicker';
import { es } from 'date-fns/locale';
import 'react-datepicker/dist/react-datepicker.css';
import './react-datepicker-overrides.css';

// Wrapper con configuración corporativa

export interface DatePickerWrapperProps {
  value: Date | null;
  onChange: (date: Date | null) => void;
  inline?: boolean;
  className?: string;
  placeholderText?: string;
  wrapperClassName?: string;
}

const DatePicker: React.FC<DatePickerWrapperProps> = ({ value, onChange, inline, wrapperClassName, ...rest }) => (
  <ReactDatePicker
    locale={es}
    dateFormat="dd/MM/yyyy"
    selected={value}
    onChange={(date) => onChange(date as Date | null)}
    inline={inline}
    wrapperClassName={wrapperClassName}
    showMonthDropdown
    showYearDropdown
    dropdownMode="select"
    placeholderText="dd/mm/aaaa"
    isClearable
    {...rest}
  />
);

export default DatePicker; 