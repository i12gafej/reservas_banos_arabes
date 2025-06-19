import React, { useState } from 'react';
import ReactiveButton from 'reactive-button';

const ElementsTest: React.FC = () => {
  const [state, setState] = useState<'idle' | 'loading' | 'success'>('idle');

  const handleClick = () => {
    setState('loading');
    setTimeout(() => setState('success'), 1500);
  };

  return (
    <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
      <ReactiveButton
        buttonState={state}
        onClick={handleClick}
        style={{ backgroundColor: 'var(--color-primary)' }}
        idleText="Guardar"
        loadingText="Guardando..."
        successText="Guardado"
      />

      <ReactiveButton style={{ backgroundColor: 'var(--color-secondary)', color: 'var(--color-white)' }} idleText="Cancelar" />
      <ReactiveButton style={{ backgroundColor: 'var(--color-edit)', color: 'var(--color-black)' }} idleText="Añadir" />
      <ReactiveButton style={{ backgroundColor: 'var(--color-tertiary-1)' }} idleText="Extra 1" />
      <ReactiveButton style={{ backgroundColor: 'var(--color-tertiary-2)', color: 'var(--color-black)' }} idleText="Extra 2" />
    </div>
  );
};

export default ElementsTest; 