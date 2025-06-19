import React, { useEffect, useState } from 'react';
import { FiArrowUp } from 'react-icons/fi';

/*
  Botón flotante para volver al inicio de la página.
  - Aparece tras hacer scroll 200 px.
  - Scroll suave al hacer clic.
*/
const SCROLL_THRESHOLD = 200;

const BackToTop: React.FC = () => {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const onScroll = () => {
      setVisible(window.pageYOffset > SCROLL_THRESHOLD);
    };
    window.addEventListener('scroll', onScroll);
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  const handleClick = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  if (!visible) return null;

  return (
    <button
      onClick={handleClick}
      aria-label="Volver al inicio"
      style={{
        position: 'fixed',
        right: '1.25rem',
        bottom: '1.25rem',
        width: '40px',
        height: '40px',
        borderRadius: '50%',
        background: 'var(--color-primary)',
        color: 'var(--color-white)',
        border: 'none',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        boxShadow: '0 4px 8px rgba(0,0,0,0.15)',
        cursor: 'pointer',
        zIndex: 1000,
      }}
    >
      <FiArrowUp />
    </button>
  );
};

export default BackToTop; 