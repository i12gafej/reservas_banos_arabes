import React, { useMemo, useState } from 'react';
import ReactiveButton from 'reactive-button';
import './management-table.css';

export interface ColumnDef<T> {
  header: string;
  accessor?: keyof T | ((row: T) => React.ReactNode);
  width?: string | number;
}

interface Props<T> {
  columns: ColumnDef<T>[];
  rows: T[];
  onRowClick?: (row: T) => void;
  pageSizeOptions?: number[]; // default [10,25,50,100]
}

function ManagementTable<T extends { id?: number | string }>({
  columns,
  rows,
  onRowClick,
  pageSizeOptions = [10, 25, 50, 100],
}: Props<T>) {
  const [search, setSearch] = useState('');
  const [pageSize, setPageSize] = useState(pageSizeOptions[0]);
  const [page, setPage] = useState(1);

  // Filtrado simple por stringify
  const filtered = useMemo(() => {
    if (!search) return rows;
    return rows.filter((r) => JSON.stringify(r).toLowerCase().includes(search.toLowerCase()));
  }, [search, rows]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / pageSize));
  const currentPage = Math.min(page, totalPages);

  const sliceStart = (currentPage - 1) * pageSize;
  const pageRows = filtered.slice(sliceStart, sliceStart + pageSize);

  // Helpers nav
  const pagesToShow = () => {
    const maxButtons = 5;
    const res: number[] = [];
    if (totalPages <= maxButtons) {
      for (let i = 1; i <= totalPages; i++) res.push(i);
      return res;
    }
    if (currentPage <= 3) {
      return [1, 2, 3, 4, 5];
    }
    if (currentPage >= totalPages - 2) {
      return [totalPages - 4, totalPages - 3, totalPages - 2, totalPages - 1, totalPages];
    }
    return [currentPage - 2, currentPage - 1, currentPage, currentPage + 1, currentPage + 2];
  };

  return (
    <div className="mgmt-table">
      {/* Buscador y page size */}
      <div className="table-toolbar">
        <input
          type="text"
          placeholder="Buscar…"
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            setPage(1);
          }}
        />
        <select
          value={pageSize}
          onChange={(e) => {
            setPageSize(Number(e.target.value));
            setPage(1);
          }}
        >
          {pageSizeOptions.map((opt) => (
            <option key={opt} value={opt}>{opt}</option>
          ))}
        </select>
      </div>

      {/* Tabla */}
      <table className="baths-table small-font">
        <thead>
          <tr>
            {columns.map((col) => (
              <th key={col.header} style={{ width: col.width }}>{col.header}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {pageRows.map((row, idx) => (
            <tr
              key={idx}
              onClick={() => onRowClick && onRowClick(row)}
              style={onRowClick ? { cursor: 'pointer' } : undefined}
            >
              {columns.map((col) => {
                let cell: React.ReactNode;
                if (typeof col.accessor === 'function') {
                  cell = col.accessor(row);
                } else if (col.accessor) {
                  // @ts-ignore
                  cell = row[col.accessor];
                } else {
                  cell = '';
                }
                return <td key={col.header}>{cell}</td>;
              })}
            </tr>
          ))}
          {pageRows.length === 0 && (
            <tr><td colSpan={columns.length} style={{ textAlign:'center' }}>Sin registros</td></tr>
          )}
        </tbody>
      </table>

      {/* Paginación */}
      <div className="pagination-bar">
        <span className="info-text">
          Mostrando {filtered.length === 0 ? 0 : sliceStart + 1} a {Math.min(sliceStart + pageSize, filtered.length)} de {filtered.length} registros
        </span>
        <div className="nav-buttons">
          <ReactiveButton
            idleText="≪"
            size="small"
            style={{ backgroundColor: 'var(--color-tertiary,#666)' }}
            disabled={currentPage === 1}
            onClick={() => setPage(1)}
          />
          <ReactiveButton
            idleText="‹"
            size="small"
            style={{ backgroundColor: 'var(--color-tertiary,#666)' }}
            disabled={currentPage === 1}
            onClick={() => setPage((p) => Math.max(1, p - 1))}
          />
          {pagesToShow().map((p) => (
            <button
              key={p}
              className={`page-btn ${p === currentPage ? 'active' : ''}`}
              onClick={() => setPage(p)}
            >
              {p}
            </button>
          ))}
          <ReactiveButton
            idleText="›"
            size="small"
            style={{ backgroundColor: 'var(--color-tertiary,#666)' }}
            disabled={currentPage === totalPages}
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
          />
          <ReactiveButton
            idleText="≫"
            size="small"
            style={{ backgroundColor: 'var(--color-tertiary,#666)' }}
            disabled={currentPage === totalPages}
            onClick={() => setPage(totalPages)}
          />
        </div>
      </div>
    </div>
  );
}

export default ManagementTable; 