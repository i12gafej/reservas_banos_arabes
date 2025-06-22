import React, { useState, useEffect } from 'react';
import ReactiveButton from 'reactive-button';
import { DefaultDialog, DatePicker } from '@/components/elements';
import { useForm, Controller } from 'react-hook-form';
import PhoneInput from 'react-phone-input-2';
import esLocale from 'react-phone-input-2/lang/es.json';
import 'react-phone-input-2/lib/style.css';
import { getCapacity, updateCapacity, Capacity, createStaffBooking, StaffBath } from '@/services/cuadrante.service';
import './cuadrante.css';

const CuadrantePage: React.FC = () => {
  const [capacity, setCapacity] = useState<Capacity | null>(null);
  const aforo = capacity?.value ?? null;
  const [openDlg, setOpenDlg] = useState(false);
  const [draftAforo, setDraftAforo] = useState<number | ''>(aforo ?? '');

  // Fecha cuadrante
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);

  const handleSaveAforo = async () => {
    if (draftAforo === '') {
      setOpenDlg(false);
      return;
    }
    try {
      if (!capacity) return;
      const updated = await updateCapacity(capacity.id, Number(draftAforo));
      setCapacity(updated);
    } catch (err) {
      console.error('Error actualizando aforo', err);
    } finally {
      setOpenDlg(false);
    }
  };

  // Cargar aforo inicial
  useEffect(() => {
    console.log('BASE_URL:', import.meta.env.VITE_API_URL);
    console.log('Llamada a getCapacity…');
    getCapacity()
      .then((cap) => {
        // Debug: mostramos la respuesta completa en consola
        // eslint-disable-next-line no-console
        console.log('Respuesta de getCapacity:', cap);
        setCapacity(cap);
      })
      .catch((err) => console.error('Error obteniendo aforo', err));
  }, []);

  // React Hook Form para reserva
  type FormInputs = {
    name: string;
    surname: string;
    phone: string;
    email: string;
    day: Date | null;
    hour: string;
    people: number;
    force: boolean;
    massage60Relax: number;
    massage60Piedra: number;
    massage60Exfol: number;
    massage30Relax: number;
    massage30Piedra: number;
    massage30Exfol: number;
    massage15Relax: number;
    sendWhatsapp: boolean;
    comments: string;
  };

  const {
    register,
    handleSubmit,
    control,
    reset,
  } = useForm<FormInputs>({
    defaultValues: {
      hour: '10:00',
      people: undefined as any,
      massage60Relax: 0,
      massage60Piedra: 0,
      massage60Exfol: 0,
      massage30Relax: 0,
      massage30Piedra: 0,
      massage30Exfol: 0,
      massage15Relax: 0,
    } as any,
  });

  const onSubmit = async (data: FormInputs) => {
    try {
      // Construir array de baths
      const baths: StaffBath[] = [];
      const pushBath = (type: 'relax' | 'exfoliation' | 'rock', minutes: '60' | '30' | '15', qty: number) => {
        if (qty && qty > 0) {
          baths.push({ massage_type: type, minutes, quantity: qty });
        }
      };

      pushBath('relax', '60', data.massage60Relax);
      pushBath('rock', '60', data.massage60Piedra);
      pushBath('exfoliation', '60', data.massage60Exfol);
      pushBath('relax', '30', data.massage30Relax);
      pushBath('rock', '30', data.massage30Piedra);
      pushBath('exfoliation', '30', data.massage30Exfol);
      pushBath('relax', '15', data.massage15Relax);

      const payload = {
        name: data.name,
        surname: data.surname,
        phone_number: data.phone,
        email: data.email,
        date: data.day ? data.day.toISOString().substring(0, 10) : new Date().toISOString().substring(0, 10),
        hour: data.hour + ':00',
        people: data.people,
        baths,
        comment: data.comments,
        send_whatsapp: data.sendWhatsapp,
      };

      const created = await createStaffBooking(payload);
      console.log('Reserva creada', created);
      reset();
    } catch (err) {
      console.error('Error creando reserva', err);
    }
  };

  return (
    <div className="cuadrante-page">
      {/* Grid principal */}
      <div className="cuadrante-grid">
        {/* Panel izquierdo */}
        <aside>
          <div className="card">
            <h3>Aforo</h3>
            <p className="aforo-text">
              {aforo !== null
                ? `El aforo actual es de ${aforo} entradas a baños.`
                : 'No hay aforo establecido.'}
            </p>
            <ReactiveButton
              style={{ backgroundColor: 'var(--color-primary)' }}
              idleText="Establecer nuevo aforo"
              onClick={() => {
                setDraftAforo(aforo ?? '');
                setOpenDlg(true);
              }}
              width={"100%"}
            />
          </div>

          <div className="card" style={{ marginTop: '1rem' }}>
            <h3>Ver cuadrante</h3>
            <DatePicker 
            value={selectedDate} 
            onChange={setSelectedDate} 
            wrapperClassName="picker-dia"
            placeholderText="Selecciona fecha" />
            <div style={{ marginTop: '0.75rem' }}>
              <ReactiveButton
                style={{ backgroundColor: 'var(--color-primary)' }}
                idleText="Ver cuadrante"
                width={"100%"}
              />
            </div>
          </div>
        </aside>

        {/* Panel derecho */}
        <main>
          <div className="card" style={{ height: '100%' }}>
            <h3>Reservar Baños</h3>
            <form onSubmit={handleSubmit(onSubmit)}>
              {/* 4-column grid */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem', width: '100%'}}>
                {/* Col 1: cliente */}
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', width: '100%' }}>
                  <h4>Cliente</h4>
                  <input placeholder="Nombre" {...register('name')} className="full-width" />
                  <input placeholder="Apellidos" {...register('surname')} className="full-width" style={{ marginTop: '0.5rem' }} />
                  <input placeholder="Email" type="email" {...register('email')} className="full-width" style={{ marginTop: '0.5rem', marginBottom: '0.7rem' }} />
                  {/* Teléfono con prefijo */}
                  <Controller
                    control={control}
                    name="phone"
                    render={({ field }) => (
                      <PhoneInput
                        {...field}
                        country={'es'}
                        localization={esLocale}
                        placeholder="Teléfono"
                        enableSearch
                        searchPlaceholder="Buscar..."
                        
                        
                      />
                    )}
                  />
                  
                </div>

                {/* Col 2: fecha, hora, personas */}
                <div  style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', width: '100%' }}>
                  <h4>Día y hora</h4>
                  <Controller
                    control={control}
                    name="day"
                    render={({ field }) => <DatePicker value={field.value} onChange={field.onChange} wrapperClassName="picker-dia"/>}
                  />
                  <select {...register('hour')} className="full-width" style={{ marginTop: '0.5rem' }}>
                    {Array.from({ length: 25 }, (_, i) => 10 * 60 + i * 30)
                      .filter((m) => m <= 22 * 60)
                      .map((m) => {
                        const h = Math.floor(m / 60);
                        const min = m % 60;
                        const label = `${h.toString().padStart(2, '0')}:${min.toString().padStart(2, '0')}`;
                        return (
                          <option key={label} value={label}>
                            {label}
                          </option>
                        );
                      })}
                  </select>
                  <input placeholder="Personas" aria-label="Personas" type="number" min={1} {...register('people', { valueAsNumber: true, min: 1 })} className="full-width" style={{ marginTop: '0.5rem', width: '68%' }} />
                  <label style={{ display: 'flex', alignItems: 'center', marginTop: '0.5rem' }}>
                    <input type="checkbox" {...register('force')} /> <span style={{fontSize: '0.87rem'}}>Forzar reserva</span>
                  </label>
                </div>

                {/* Col 3: masaje grid */}
                <div>
                  <h4>Reserva Masaje</h4>
                  <table style={{ width: '100%', textAlign: 'center' }}>
                    <thead>
                      <tr>
                        <th></th>
                        <th>RELAX</th>
                        <th>PIEDRA</th>
                        <th>EXFOL</th>
                      </tr>
                    </thead>
                    <tbody>
                      {[60, 30, 15].map((dur) => (
                        <tr key={dur} style={{}}>
                          <td className="massage-table">{dur}&apos;</td>
                          {['Relax', 'Piedra', 'Exfol'].map((tipo) => {
                            const nameKey = (`massage${dur}${tipo}` as keyof FormInputs);
                            if (dur === 15 && tipo !== 'Relax') {
                              return <td key={tipo}></td>;
                            }
                            return (
                              <td key={tipo}>
                                <input type="number" min={0} {...register(nameKey as any)} style={{ width: '50%' }} />
                              </td>
                            );
                          })}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {/* Col 4: whatsapp & comentarios */}
                <div>
                  <h4>Otros</h4>
                  <label style={{ display: 'flex', alignItems: 'center' }}>
                    <input type="checkbox" {...register('sendWhatsapp')} /> <span style={{fontSize: '0.87rem'}}>Enviar WhatsApp</span>
                  </label>
                  <textarea
                    {...register('comments')}
                    rows={5}
                    placeholder="Comentarios"
                    className="full-width"
                    style={{ marginTop: '0.5rem' }}
                  />
                  <ReactiveButton
                  style={{ backgroundColor: 'var(--color-primary)', marginTop: '0.5rem' }}
                  idleText="Insertar"
                  type="submit"
                  width={"100%"}
                />
                </div>
              </div>
            </form>
          </div>
        </main>
      </div>

      {/* Dialogo nuevo aforo */}
      <DefaultDialog
        open={openDlg}
        title="Establecer nuevo aforo"
        onClose={() => setOpenDlg(false)}
        onSave={handleSaveAforo}
      >
        <label style={{ display: 'block', marginBottom: '0.5rem' }}>
          Aforo máximo:
          <input
            type="number"
            min={0}
            value={draftAforo}
            onChange={(e) =>
              setDraftAforo(e.target.value === '' ? '' : Number(e.target.value))
            }
            style={{ width: '50%', padding: '0.4rem', marginTop: '0.25rem', marginLeft: '1rem'}}
          />
        </label>
      </DefaultDialog>
    </div>
  );
};

export default CuadrantePage; 