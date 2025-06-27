import React, { useEffect, useState } from 'react';
import ReactiveButton from 'reactive-button';
import { useForm, Controller, useWatch } from 'react-hook-form';
import PhoneInput from 'react-phone-input-2';
import esLocale from 'react-phone-input-2/lang/es.json';
import 'react-phone-input-2/lib/style.css';
import ManagementTable, { ColumnDef } from '@/components/managetable/ManagementTable';
import { getCheques, GiftVoucherWithDetails, createGiftVoucher, CreateGiftVoucherRequest, StaffBathRequest } from '@/services/cheques.service';
import '../cuadrante/cuadrante.css';

type FormInputs = {
  // Datos comprador
  buyerName: string;
  buyerSurname: string;
  buyerEmail: string;
  buyerPhone: string;
  
  // Datos recibidor
  recipientName: string;
  recipientSurname: string;
  recipientEmail: string;
  
  // Datos adicionales
  giftName: string;
  giftDescription: string;
  people: number;
  
  // Masajes
  massage60Relax: number;
  massage60Piedra: number;
  massage60Exfol: number;
  massage30Relax: number;
  massage30Piedra: number;
  massage30Exfol: number;
  massage15Relax: number;
  
  // Otros
  sendWhatsappBuyer: boolean;
};

const ChequesPage: React.FC = () => {
  // Estados para la lista de cheques
  const [cheques, setCheques] = useState<GiftVoucherWithDetails[]>([]);
  const [loading, setLoading] = useState(false);
  const [creating, setCreating] = useState(false);

  const {
    register,
    handleSubmit,
    control,
    reset,
  } = useForm<FormInputs>({
    defaultValues: {
      people: undefined as any,
      massage60Relax: 0,
      massage60Piedra: 0,
      massage60Exfol: 0,
      massage30Relax: 0,
      massage30Piedra: 0,
      massage30Exfol: 0,
      massage15Relax: 0,
      sendWhatsappBuyer: false,
    },
  });

  // Observar cambios en tiempo real para validación
  const people = useWatch({ control, name: 'people' }) || 0;
  const massage60Relax = useWatch({ control, name: 'massage60Relax' }) || 0;
  const massage60Piedra = useWatch({ control, name: 'massage60Piedra' }) || 0;
  const massage60Exfol = useWatch({ control, name: 'massage60Exfol' }) || 0;
  const massage30Relax = useWatch({ control, name: 'massage30Relax' }) || 0;
  const massage30Piedra = useWatch({ control, name: 'massage30Piedra' }) || 0;
  const massage30Exfol = useWatch({ control, name: 'massage30Exfol' }) || 0;
  const massage15Relax = useWatch({ control, name: 'massage15Relax' }) || 0;

  // Calcular totales en tiempo real
  const totalMassages = Number(massage60Relax) + Number(massage60Piedra) + Number(massage60Exfol) + 
                       Number(massage30Relax) + Number(massage30Piedra) + Number(massage30Exfol) + 
                       Number(massage15Relax);
  
  const hasValidationError = Number(people) > 0 && totalMassages > Number(people);

  // Cargar datos de cheques
  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        const data = await getCheques();
        setCheques(data);
      } catch (err) {
        console.error('Error cargando cheques', err);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  const onSubmit = async (data: FormInputs) => {
    try {
      setCreating(true);
      
      // Construir array de baths
      const baths: StaffBathRequest[] = [];
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

      // Contar total de masajes
      const totalMassages = baths.reduce((total, bath) => total + bath.quantity, 0);
      
      // VALIDACIÓN: Verificar que no hay más masajes que personas
      if (data.people < totalMassages) {
        alert(`Hay más masajes (${totalMassages}) que personas (${data.people}). Por favor, reduce la cantidad de masajes o aumenta el número de personas.`);
        return;
      }
      
      // Agregar baños sin masaje para las personas restantes
      const peopleWithoutMassage = data.people - totalMassages;
      if (peopleWithoutMassage > 0) {
        baths.push({
          massage_type: 'none',
          minutes: '0',
          quantity: peopleWithoutMassage
        });
      }

      // Si no hay masajes ni baños, agregar baños sin masaje para todas las personas
      if (baths.length === 0) {
        baths.push({
          massage_type: 'none',
          minutes: '0',
          quantity: data.people
        });
      }

      const payload: CreateGiftVoucherRequest = {
        buyer_name: data.buyerName,
        buyer_surname: data.buyerSurname,
        buyer_phone: data.buyerPhone,
        buyer_email: data.buyerEmail,
        recipient_name: data.recipientName,
        recipient_surname: data.recipientSurname,
        recipient_email: data.recipientEmail,
        gift_name: data.giftName,
        gift_description: data.giftDescription,
        people: data.people,
        baths,
        send_whatsapp_buyer: data.sendWhatsappBuyer,
      };

      const created = await createGiftVoucher(payload);
      console.log('Cheque regalo creado:', created);
      
      alert('Cheque regalo creado exitosamente');
      reset();
      
      // Recargar la lista después de crear
      const newData = await getCheques();
      setCheques(newData);
    } catch (err) {
      console.error('Error creando cheque regalo:', err);
      alert('Error al crear el cheque regalo');
    } finally {
      setCreating(false);
    }
  };

  // Definir columnas para la tabla de cheques
  const columns: ColumnDef<GiftVoucherWithDetails>[] = [
    { header: 'Código', accessor: 'code' },
    { 
      header: 'Estado', 
      accessor: (r) => {
        switch (r.status) {
          case 'pending_payment':
            return 'Pendiente pago';
          case 'paid':
            return 'Pagado';
          case 'used':
            return 'Usado';
          default:
            return r.status;
        }
      }
    },
    { header: 'Producto', accessor: (r) => r.product_name || `Prod ${r.product_id}` },
    { header: 'Fecha compra', accessor: (r) => r.bought_date?.substring(0, 10) || r.created_at?.substring(0, 10) },
    { 
      header: 'Comprador', 
      accessor: (r) => r.buyer_name && r.buyer_surname 
        ? `${r.buyer_name} ${r.buyer_surname}`.trim() 
        : r.buyer_name || `ID ${r.buyer_client_id}`
    },
    { header: 'Teléfono comprador', accessor: (r) => r.buyer_phone || 'N/A' },
    { header: 'Email comprador', accessor: (r) => r.buyer_email || 'N/A' },
    { 
      header: 'Destino', 
      accessor: (r) => r.recipients_name 
        ? `${r.recipients_name} ${r.recipients_surname ?? ''}`.trim() 
        : 'N/A' 
    },
    { header: 'Email destino', accessor: (r) => r.recipients_email || 'N/A' },
    { header: 'Precio', accessor: (r) => `€${r.price}` },
    { header: 'Personas', accessor: 'people' },
  ];

  return (
    <div className="cuadrante-page">
      <div className="card">
        <h3>Crear Cheque Regalo</h3>
        
        <form onSubmit={handleSubmit(onSubmit)}>
          {/* Grid de 5 columnas */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '1rem', width: '100%'}}>
                
                {/* Columna 1: Datos comprador */}
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', width: '100%' }}>
                  <h4>Datos Comprador</h4>
                  <input 
                    placeholder="Nombre comprador" 
                    {...register('buyerName', { required: true })} 
                    className="full-width" 
                  />
                  <input 
                    placeholder="Apellidos comprador" 
                    {...register('buyerSurname')} 
                    className="full-width" 
                    style={{ marginTop: '0.5rem' }} 
                  />
                  <input 
                    placeholder="Email comprador" 
                    type="email" 
                    {...register('buyerEmail', { required: true })} 
                    className="full-width" 
                    style={{ marginTop: '0.5rem', marginBottom: '0.7rem' }} 
                  />
                  <Controller
                    control={control}
                    name="buyerPhone"
                    render={({ field }) => (
                      <PhoneInput
                        {...field}
                        country={'es'}
                        localization={esLocale}
                        placeholder="Teléfono comprador"
                        enableSearch
                        searchPlaceholder="Buscar..."
                      />
                    )}
                  />
                </div>

                {/* Columna 2: Datos recibidor */}
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', width: '100%' }}>
                  <h4>Datos Recibidor</h4>
                  <input 
                    placeholder="Nombre recibidor" 
                    {...register('recipientName')} 
                    className="full-width" 
                  />
                  <input 
                    placeholder="Apellidos recibidor" 
                    {...register('recipientSurname')} 
                    className="full-width" 
                    style={{ marginTop: '0.5rem' }} 
                  />
                  <input 
                    placeholder="Email recibidor" 
                    type="email" 
                    {...register('recipientEmail')} 
                    className="full-width" 
                    style={{ marginTop: '0.5rem' }} 
                  />
                </div>

                {/* Columna 3: Datos adicionales */}
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', width: '100%' }}>
                  <h4>Datos Adicionales</h4>
                  <input 
                    placeholder="Nombre del cheque" 
                    {...register('giftName', { required: true })} 
                    className="full-width" 
                  />
                  <textarea 
                    placeholder="Descripción del cheque" 
                    {...register('giftDescription')} 
                    className="full-width" 
                    rows={3}
                    style={{ marginTop: '0.5rem', marginBottom: '0.5rem' }}
                  />
                  
                  <input 
                    placeholder="Personas" 
                    aria-label="Personas"
                    type="number" 
                    min={1} 
                    {...register('people', { valueAsNumber: true, min: 1 })} 
                    className="full-width" 
                    style={{ marginTop: '0.5rem' }}
                  />
                </div>

                {/* Columna 4: Masaje */}
  <div>
                  <h4>Añadir Masaje</h4>
                  <table className="massage-table" style={{ width: '100%', textAlign: 'center' }}>
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
                        <tr key={dur}>
                          <td className="massage-table">{dur}&apos;</td>
                          {['Relax', 'Piedra', 'Exfol'].map((tipo) => {
                            const nameKey = (`massage${dur}${tipo}` as keyof FormInputs);
                            if (dur === 15 && tipo !== 'Relax') {
                              return <td key={tipo}></td>;
                            }
                            return (
                              <td key={tipo}>
                                <input 
                                  type="number" 
                                  min={0} 
                                  {...register(nameKey as any, { valueAsNumber: true, min: 0 })} 
                                  style={{ width: '50%' }} 
                                />
                              </td>
                            );
                          })}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  
                  {/* Mensaje de validación */}
                  {hasValidationError && (
                    <div style={{
                      marginTop: '0.5rem',
                      padding: '0.5rem',
                      backgroundColor: '#fee2e2',
                      border: '1px solid #fca5a5',
                      borderRadius: '4px',
                      color: '#dc2626',
                      fontSize: '0.875rem',
                      textAlign: 'center'
                    }}>
                      ⚠️ Hay más masajes ({totalMassages}) que personas ({people})
                    </div>
                  )}
                  
                  {/* Información de ayuda */}
                  <div style={{
                    marginTop: '0.5rem',
                    fontSize: '0.75rem',
                    color: '#64748b',
                    textAlign: 'center'
                  }}>
                    Total masajes: {totalMassages} | Personas: {people}
                  </div>
                                 </div>

                 {/* Columna 5: Otros */}
                 <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', width: '100%' }}>
                   <h4>Otros</h4>
                   <label style={{ display: 'flex', alignItems: 'center', marginBottom: '1rem' }}>
                     <input type="checkbox" {...register('sendWhatsappBuyer')} /> 
                     <span style={{fontSize: '0.87rem', marginLeft: '0.5rem'}}>Enviar WhatsApp a comprador para pago</span>
                   </label>
                   
                   <ReactiveButton
                     style={{ backgroundColor: hasValidationError ? '#9ca3af' : 'var(--color-primary)' }}
                     idleText={creating ? "Creando..." : hasValidationError ? "Corrige los errores primero" : "Crear Cheque Regalo"}
                     type="submit"
                     width="100%"
                     loading={creating}
                     disabled={creating || hasValidationError}
                   />
               </div>
             </div>
           </form>
         </div>
         
         {/* Tabla de Cheques Regalo */}
         <div className="card" style={{ marginTop: '2rem' }}>
           <h3>Lista de Cheques Regalo</h3>
           {loading ? (
             <p>Cargando cheques...</p>
           ) : (
             <ManagementTable columns={columns} rows={cheques} />
           )}
         </div>
  </div>
);
};

export default ChequesPage; 