import React, { ReactNode, useEffect } from 'react';
import ReactDOM from 'react-dom';
import { FiX } from 'react-icons/fi';
import ReactiveButton from 'reactive-button';

import './default-dialog.css';

interface DefaultDialogProps {
  open: boolean;
  title?: string;
  children: ReactNode;
  onClose: () => void;
  onSave?: () => void;
  saveLabel?: string;
  cancelLabel?: string;
}

const DefaultDialog: React.FC<DefaultDialogProps> = ({
  open,
  title,
  children,
  onClose,
  onSave,
  saveLabel = 'Guardar',
  cancelLabel = 'Cancelar',
}) => {
  // Evitar scroll del fondo mientras el modal está abierto
  useEffect(() => {
    if (open) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
    };
  }, [open]);

  if (!open) return null;

  return ReactDOM.createPortal(
    <div className="dialog-overlay" role="dialog" aria-modal="true">
      <div className="dialog-box">
        {/* Cabecera */}
        <div className="dialog-header">
          {title && <h2 className="dialog-title">{title}</h2>}
          <button className="dialog-close" onClick={onClose} aria-label="Cerrar">
            <FiX />
          </button>
        </div>

        {/* Contenido */}
        <div className="dialog-content">{children}</div>

        {/* Pie */}
        <div className="dialog-footer">
          <ReactiveButton
            style={{ backgroundColor: 'var(--color-secondary)' }}
            idleText={cancelLabel}
            onClick={onClose}
          />
          {onSave && (
            <ReactiveButton
              style={{ backgroundColor: 'var(--color-primary)', marginLeft: '0.5rem' }}
              idleText={saveLabel}
              onClick={onSave}
            />
          )}
        </div>
      </div>
    </div>,
    document.body
  );
};

export default DefaultDialog; 