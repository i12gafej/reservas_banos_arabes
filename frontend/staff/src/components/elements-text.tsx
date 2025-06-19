import React from 'react';
import { useForm } from 'react-hook-form';

interface FormValues {
  search: string;
  quantity: number | undefined;
  email: string;
  category: string;
}

const ElementsText: React.FC = () => {
  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
  } = useForm<FormValues>({
    defaultValues: {
      search: '',
      quantity: undefined,
      email: '',
      category: '',
    },
  });

  const onSubmit = (data: FormValues) => {
    console.log('Form submit', data);
    alert(JSON.stringify(data, null, 2));
  };

  // Para depuración en tiempo real
  const watched = watch();

  return (
    <form onSubmit={handleSubmit(onSubmit)} style={{ maxWidth: 400 }}>
      {/* Campo de texto */}
      <div style={{ marginBottom: '1rem' }}>
        <label htmlFor="search">Filtro texto</label>
        <input
          id="search"
          type="text"
          placeholder="Buscar..."
          {...register('search', { required: 'Campo requerido' })}
        />
        {errors.search && <p style={{ color: 'red' }}>{errors.search.message}</p>}
      </div>

      {/* Campo numérico */}
      <div style={{ marginBottom: '1rem' }}>
        <label htmlFor="quantity">Cantidad</label>
        <input
          id="quantity"
          type="number"
          min={0}
          {...register('quantity', {
            required: 'Indique una cantidad',
            valueAsNumber: true,
            min: { value: 0, message: 'Debe ser ≥ 0' },
          })}
        />
        {errors.quantity && <p style={{ color: 'red' }}>{errors.quantity.message}</p>}
      </div>

      {/* Campo email */}
      <div style={{ marginBottom: '1rem' }}>
        <label htmlFor="email">Email</label>
        <input
          id="email"
          type="email"
          placeholder="usuario@dominio.com"
          {...register('email', {
            required: 'Email obligatorio',
            pattern: {
              value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
              message: 'Formato de email inválido',
            },
          })}
        />
        {errors.email && <p style={{ color: 'red' }}>{errors.email.message}</p>}
      </div>

      {/* Select */}
      <div style={{ marginBottom: '1rem' }}>
        <label htmlFor="category">Categoría</label>
        <select id="category" {...register('category', { required: 'Seleccione una opción' })}>
          <option value="">-- seleccione --</option>
          <option value="spa">Spa</option>
          <option value="masaje">Masaje</option>
          <option value="producto">Producto</option>
        </select>
        {errors.category && <p style={{ color: 'red' }}>{errors.category.message}</p>}
      </div>

      <button type="submit">Enviar</button>

      {/* Vista de valores en tiempo real */}
      <pre style={{ fontSize: 12, background: '#f4f4f4', padding: '0.5rem' }}>
        {JSON.stringify(watched, null, 2)}
      </pre>
    </form>
  );
};

export default ElementsText; 