import React, { useState, useEffect } from 'react';
import ReactiveButton from 'reactive-button';
import { DefaultDialog, DatePicker } from '@/components/elements';
import { GeneralSearch } from '@/components/common';
import { useForm, Controller, useWatch } from 'react-hook-form';
import PhoneInput from 'react-phone-input-2';
import esLocale from 'react-phone-input-2/lang/es.json';
import 'react-phone-input-2/lib/style.css';
import { findSimilarClients, Client as ClienteService } from '@/services/clientes.service';
import { getCapacity, updateCapacity, Capacity, createStaffBooking, StaffBath, calculateCuadrante, CuadranteCalculated, getBookingsByDate, Booking, getClientById, Client, getGiftVoucherContentTypeId, getMassageReservationsForDate } from '@/services/cuadrante.service';
import { getConstraintByDate, saveConstraintForDate, constraintRangesToCells, Constraint } from '@/services/restricciones.service';
import TimeGrid from '@/components/timetable/TimeGrid';
import BookGrid, { BookRow } from '@/components/timetable/BookGrid';
import { MassageGrid, MassageReservation } from '@/components/timetable';
import './cuadrante.css';
import { toLocalISODate } from '@/utils/date';

const CuadrantePage: React.FC = () => {
  const [capacity, setCapacity] = useState<Capacity | null>(null);
  const aforo = capacity?.value ?? null;
  const [openDlg, setOpenDlg] = useState(false);
  const [draftAforo, setDraftAforo] = useState<number | ''>(aforo ?? '');

  // Fecha cuadrante
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);
  const [cuadranteData, setCuadranteData] = useState<CuadranteCalculated | null>(null);
  const [loadingCuadrante, setLoadingCuadrante] = useState(false);
  const [bookings, setBookings] = useState<BookRow[]>([]);
  const [massageReservations, setMassageReservations] = useState<MassageReservation[]>([]);
  
  // Restricciones
  const [constraintCells, setConstraintCells] = useState<boolean[]>(Array(25).fill(false));
  const [constraintChanged, setConstraintChanged] = useState(false);
  const [savingConstraints, setSavingConstraints] = useState(false);

  // Cheque regalo
  const [selectedGiftVoucher, setSelectedGiftVoucher] = useState<number | null>(null);
  const [selectedGiftVoucherProductId, setSelectedGiftVoucherProductId] = useState<number | null>(null);

  // Modal de selección de clientes
  const [showClientModal, setShowClientModal] = useState(false);
  const [loadingClients, setLoadingClients] = useState(false);
  const [similarClients, setSimilarClients] = useState<ClienteService[]>([]);
  const [selectedClient, setSelectedClient] = useState<ClienteService | null>(null);
  const [showNewClientForm, setShowNewClientForm] = useState(false);
  const [clientSelectionData, setClientSelectionData] = useState<{
    name: string;
    surname: string;
    email: string;
    phone_number: string;
  } | null>(null);


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

  const handleVerCuadrante = async () => {
    if (!selectedDate) {
      alert('Por favor selecciona una fecha');
      return;
    }
    
    setLoadingCuadrante(true);
    try {
      const dateStr = toLocalISODate(selectedDate);
      
      // Cargar cuadrante, reservas, restricciones y masajes en paralelo
      const [cuadranteData, bookingsData, constraintData, massageData] = await Promise.all([
        calculateCuadrante(dateStr),
        getBookingsByDate(dateStr),
        getConstraintByDate(dateStr),
        getMassageReservationsForDate(dateStr)
      ]);
      
      setCuadranteData(cuadranteData);
      
      // Convertir reservas al formato de BookGrid
      let convertedBookings = bookingsData.map(convertBookingToBookRow);
      
      // Cargar información de todos los clientes únicos
      const uniqueClientIds = [...new Set(bookingsData.map(b => b.client_id))];
      const clientPromises = uniqueClientIds.map(async (clientId) => {
        try {
          const client = await getClientById(clientId);
          return { clientId, client };
        } catch (error) {
          console.error(`Error cargando cliente ${clientId}:`, error);
          return { clientId, client: null };
        }
      });
      
      const clientResults = await Promise.all(clientPromises);
      const clientMap = new Map(
        clientResults
          .filter(result => result.client !== null)
          .map(result => [result.clientId, result.client])
      );
      
      // Actualizar las reservas con la información de los clientes
      convertedBookings = convertedBookings.map(booking => {
        const client = clientMap.get(booking.clientId);
        if (client) {
          return {
            ...booking,
            clientName: `${client.name} ${client.surname}`.trim(),
            clientInfo: {
              name: client.name,
              surname: client.surname,
              phone_number: client.phone_number,
              email: client.email,
              created_at: client.created_at,
            }
          };
        }
        return booking;
      });
      
      setBookings(convertedBookings);
      
      // Cargar reservas de masajes
      setMassageReservations(massageData);
      
      // Cargar restricciones
      if (constraintData) {
        const cells = constraintRangesToCells(constraintData.ranges);
        setConstraintCells(cells);
      } else {
        setConstraintCells(Array(25).fill(false));
      }
      setConstraintChanged(false);
      
    } catch (err) {
      console.error('Error cargando cuadrante', err);
      alert('Error al cargar el cuadrante');
    } finally {
      setLoadingCuadrante(false);
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
    setValue,
    getValues,
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

      // VALIDACIÓN: Verificar que no hay más masajes que personas
      const totalMassages = baths.reduce((total, bath) => total + bath.quantity, 0);
      if (totalMassages > data.people) {
        alert(`Hay más masajes (${totalMassages}) que personas (${data.people}). Por favor, reduce la cantidad de masajes o aumenta el número de personas.`);
        return;
      }

      // CRÍTICO: Agregar baños sin masaje para las personas restantes
      const peopleWithoutMassage = data.people - totalMassages;
      if (peopleWithoutMassage > 0) {
        baths.push({ 
          massage_type: 'none', 
          minutes: '0', 
          quantity: peopleWithoutMassage 
        });
      }

      // Si no hay masajes, agregar baños sin masaje para todas las personas
      if (baths.length === 0) {
        baths.push({
          massage_type: 'none',
          minutes: '0',
          quantity: data.people
        });
      }

      // Verificar si existen clientes similares (solo si no es desde cheque regalo)
      // NOTA: No usamos selectedClientId aquí porque queremos que el formulario 
      // responda a los cambios del usuario después de errores
      if (!selectedGiftVoucher) {
        const searchData = {
          name: data.name,
          surname: data.surname,
          email: data.email,
          phone_number: data.phone,
        };

        try {
          const clients = await findSimilarClients(searchData);
          if (clients.length > 0) {
            // Mostrar modal de selección
            setClientSelectionData(searchData);
            setSimilarClients(clients);
            setSelectedClient(clients[0]);
            setShowClientModal(true);
            return; // Pausar aquí hasta que el usuario decida
          }
        } catch (err) {
          console.error('Error buscando clientes similares:', err);
        }
      }

      // Si no hay clientes similares o es desde cheque regalo, crear reserva normalmente
      await createBookingWithNewClient(data, baths);
    } catch (err) {
      console.error('Error creando reserva', err);
      alert('Error al insertar reserva');
    }
  };

  // Función auxiliar para crear reserva con client_id existente
  const createBookingWithClientId = async (data: FormInputs, baths: StaffBath[], clientId: number) => {
    try {
      const payload: any = {
        client_id: clientId,
        date: data.day ? toLocalISODate(data.day) : toLocalISODate(new Date()),
        hour: data.hour + ':00',
        people: data.people,
        comment: data.comments,
        force: data.force,  // Usar el valor del checkbox
        send_whatsapp: data.sendWhatsapp,
      };

      // Si se ha seleccionado un cheque regalo, usar su producto y agregar información del creator
      if (selectedGiftVoucher && selectedGiftVoucherProductId) {
        const contentTypeId = await getGiftVoucherContentTypeId();
        payload.creator_type_id = contentTypeId;
        payload.creator_id = selectedGiftVoucher;
        payload.product_id = selectedGiftVoucherProductId;
      } else {
        payload.baths = baths;
      }

      const created = await createStaffBooking(payload);
      console.log('Reserva creada', created);
      alert('Reserva insertada correctamente');
      // Solo limpiar formulario si la reserva se insertó correctamente
      resetForm();
    } catch (err) {
      console.error('Error creando reserva con client_id:', err);
      
      // Extraer mensaje de error del backend
      let errorMessage = 'Error desconocido';
      if (err instanceof Error) {
        errorMessage = err.message;
        // Si el error contiene JSON del backend, extraer el detail
        try {
          const errorParts = errorMessage.split(' – ');
          if (errorParts.length > 1) {
            const jsonPart = errorParts[errorParts.length - 1];
            const errorData = JSON.parse(jsonPart);
            if (errorData.detail) {
              errorMessage = errorData.detail;
            }
          }
        } catch {
          // Si no se puede parsear, usar el mensaje original
        }
      }
      
      // Mostrar mensaje de error específico
      if (errorMessage.includes('No se puede reservar') || 
          errorMessage.includes('No hay suficiente aforo') || 
          errorMessage.includes('restricciones horarias')) {
        alert(`Error de validación: ${errorMessage}`);
      } else {
        alert(`Error al insertar reserva: ${errorMessage}`);
      }
      
      // Limpiar solo estados internos, mantener datos del formulario para correcciones
      resetInternalStates();
    }
  };

  // Función auxiliar para crear reserva con datos de nuevo cliente
  const createBookingWithNewClient = async (data: FormInputs, baths: StaffBath[]) => {
    try {
      const payload: any = {
        name: data.name,
        surname: data.surname,
        phone_number: data.phone,
        email: data.email,
        date: data.day ? toLocalISODate(data.day) : toLocalISODate(new Date()),
        hour: data.hour + ':00',
        people: data.people,
        comment: data.comments,
        force: data.force,  // Usar el valor del checkbox
      };

      // Si se ha seleccionado un cheque regalo, usar su producto y agregar información del creator
      if (selectedGiftVoucher && selectedGiftVoucherProductId) {
        const contentTypeId = await getGiftVoucherContentTypeId();
        payload.creator_type_id = contentTypeId;
        payload.creator_id = selectedGiftVoucher;
        payload.product_id = selectedGiftVoucherProductId;
      } else {
        payload.baths = baths;
      }

      const created = await createStaffBooking(payload);
      console.log('Reserva creada', created);
      alert('Reserva insertada correctamente');
      // Solo limpiar formulario si la reserva se insertó correctamente
      resetForm();
    } catch (err) {
      console.error('Error creando reserva con nuevos datos:', err);
      
      // Extraer mensaje de error del backend
      let errorMessage = 'Error desconocido';
      if (err instanceof Error) {
        errorMessage = err.message;
        // Si el error contiene JSON del backend, extraer el detail
        try {
          const errorParts = errorMessage.split(' – ');
          if (errorParts.length > 1) {
            const jsonPart = errorParts[errorParts.length - 1];
            const errorData = JSON.parse(jsonPart);
            if (errorData.detail) {
              errorMessage = errorData.detail;
            }
          }
        } catch {
          // Si no se puede parsear, usar el mensaje original
        }
      }
      
      // Mostrar mensaje de error específico
      if (errorMessage.includes('No se puede reservar') || 
          errorMessage.includes('No hay suficiente aforo') || 
          errorMessage.includes('restricciones horarias')) {
        alert(`Error de validación: ${errorMessage}`);
      } else {
        alert(`Error al insertar reserva: ${errorMessage}`);
      }
      
      // Limpiar solo estados internos, mantener datos del formulario para correcciones
      resetInternalStates();
    }
  };

  // Función para resetear solo los estados internos (sin tocar el formulario)
  const resetInternalStates = () => {
    setSelectedGiftVoucher(null);
    setSelectedGiftVoucherProductId(null);
    setClientSelectionData(null);
    setSimilarClients([]);
    setSelectedClient(null);
    setShowNewClientForm(false);
    setShowClientModal(false);
  };

  // Función para resetear el formulario y estados
  const resetForm = () => {
    reset();
    resetInternalStates();
  };

  // Guardar restricciones
  const handleSaveConstraints = async () => {
    if (!selectedDate) {
      alert('Por favor selecciona una fecha');
      return;
    }
    
    setSavingConstraints(true);
    try {
      await saveConstraintForDate(selectedDate, constraintCells);
      setConstraintChanged(false);
      alert('Restricciones guardadas correctamente');
    } catch (err) {
      console.error('Error guardando restricciones', err);
      alert('Error al guardar las restricciones');
    } finally {
      setSavingConstraints(false);
    }
  };

  // Manejar selección de cliente desde el buscador general
  const handleClientSelect = (clientData: {
    name: string;
    surname: string;
    phone_number: string;
    email: string;
  }) => {
    // Autocompletar campos del formulario
    setValue('name', clientData.name);
    setValue('surname', clientData.surname);
    setValue('phone', clientData.phone_number);
    setValue('email', clientData.email);
    // Limpiar cheque regalo si se selecciona un cliente normal
    setSelectedGiftVoucher(null);
    setSelectedGiftVoucherProductId(null);
  };

  // Manejar selección de cheque regalo
  const handleGiftVoucherSelect = (giftVoucherId: number, clientData: {
    name: string;
    surname: string;
    phone_number: string;
    email: string;
  }, productBaths?: Array<{
    massage_type: 'relax' | 'rock' | 'exfoliation' | 'none';
    massage_duration: '15' | '30' | '60' | '0';
    quantity: number;
  }>, people?: number, productId?: number) => {
    // Autocompletar campos del formulario con datos del cliente
    setValue('name', clientData.name);
    setValue('surname', clientData.surname);
    setValue('phone', clientData.phone_number);
    setValue('email', clientData.email);
    
    // Autocompletar número de personas
    if (people) {
      setValue('people', people);
    }
    
    // Limpiar campos de masaje
    setValue('massage60Relax', 0);
    setValue('massage60Piedra', 0);
    setValue('massage60Exfol', 0);
    setValue('massage30Relax', 0);
    setValue('massage30Piedra', 0);
    setValue('massage30Exfol', 0);
    setValue('massage15Relax', 0);
    
    // Autocompletar masajes desde el producto del cheque regalo
    if (productBaths) {
      productBaths.forEach(bath => {
        if (bath.massage_type === 'none') return; // Saltar baños sin masaje
        
        const fieldName = `massage${bath.massage_duration}${bath.massage_type === 'relax' ? 'Relax' : 
          bath.massage_type === 'rock' ? 'Piedra' : 'Exfol'}` as keyof FormInputs;
        
        setValue(fieldName as any, bath.quantity);
      });
    }
    
    // Establecer cheque regalo seleccionado
    setSelectedGiftVoucher(giftVoucherId);
    setSelectedGiftVoucherProductId(productId || null);
  };

  // Manejar cambios en las restricciones
  const handleConstraintChange = (newCells: (string | number | React.ReactNode | boolean)[]) => {
    const booleanCells = newCells.map(cell => Boolean(cell));
    setConstraintCells(booleanCells);
    setConstraintChanged(true);
  };

  // Funciones para el modal de selección de clientes
  const handleUseExistingClient = async () => {
    if (selectedClient) {
      setShowClientModal(false);
      // Crear reserva directamente con el cliente seleccionado
      const formData = getFormData();
      if (formData) {
        // Construir baths igual que en onSubmit
        const baths: StaffBath[] = [];
        const pushBath = (type: 'relax' | 'exfoliation' | 'rock', minutes: '60' | '30' | '15', qty: number) => {
          if (qty && qty > 0) {
            baths.push({ massage_type: type, minutes, quantity: qty });
          }
        };

        pushBath('relax', '60', formData.massage60Relax);
        pushBath('rock', '60', formData.massage60Piedra);
        pushBath('exfoliation', '60', formData.massage60Exfol);
        pushBath('relax', '30', formData.massage30Relax);
        pushBath('rock', '30', formData.massage30Piedra);
        pushBath('exfoliation', '30', formData.massage30Exfol);
        pushBath('relax', '15', formData.massage15Relax);

        const totalMassages = baths.reduce((total, bath) => total + bath.quantity, 0);
        const peopleWithoutMassage = formData.people - totalMassages;
        if (peopleWithoutMassage > 0) {
          baths.push({ 
            massage_type: 'none', 
            minutes: '0', 
            quantity: peopleWithoutMassage 
          });
        }

        if (baths.length === 0) {
          baths.push({
            massage_type: 'none',
            minutes: '0',
            quantity: formData.people
          });
        }

        await createBookingWithClientId(formData, baths, selectedClient.id);
      }
    }
  };

  const handleCreateNewClientFromModal = () => {
    setShowNewClientForm(true);
  };

  const handleCancelNewClient = () => {
    setShowNewClientForm(false);
  };

  const handleConfirmNewClient = async (finalClientData: {
    name: string;
    surname: string;
    email: string;
    phone_number: string;
  }) => {
    // Actualizar los campos del formulario con los datos finales
    setValue('name', finalClientData.name);
    setValue('surname', finalClientData.surname);
    setValue('email', finalClientData.email);
    setValue('phone', finalClientData.phone_number);

    setShowClientModal(false);
    setShowNewClientForm(false);
    
    // Obtener datos actuales del formulario y crear reserva
    const formData = getFormData();
    if (formData) {
      // Actualizar formData con los nuevos datos del cliente
      const updatedFormData = {
        ...formData,
        name: finalClientData.name,
        surname: finalClientData.surname,
        email: finalClientData.email,
        phone: finalClientData.phone_number,
      };

      // Construir baths igual que en onSubmit
      const baths: StaffBath[] = [];
      const pushBath = (type: 'relax' | 'exfoliation' | 'rock', minutes: '60' | '30' | '15', qty: number) => {
        if (qty && qty > 0) {
          baths.push({ massage_type: type, minutes, quantity: qty });
        }
      };

      pushBath('relax', '60', updatedFormData.massage60Relax);
      pushBath('rock', '60', updatedFormData.massage60Piedra);
      pushBath('exfoliation', '60', updatedFormData.massage60Exfol);
      pushBath('relax', '30', updatedFormData.massage30Relax);
      pushBath('rock', '30', updatedFormData.massage30Piedra);
      pushBath('exfoliation', '30', updatedFormData.massage30Exfol);
      pushBath('relax', '15', updatedFormData.massage15Relax);

      const totalMassages = baths.reduce((total, bath) => total + bath.quantity, 0);
      const peopleWithoutMassage = updatedFormData.people - totalMassages;
      if (peopleWithoutMassage > 0) {
        baths.push({ 
          massage_type: 'none', 
          minutes: '0', 
          quantity: peopleWithoutMassage 
        });
      }

      if (baths.length === 0) {
        baths.push({
          massage_type: 'none',
          minutes: '0',
          quantity: updatedFormData.people
        });
      }

      await createBookingWithNewClient(updatedFormData, baths);
    }
  };

  const handleCloseClientModal = () => {
    setShowClientModal(false);
    setShowNewClientForm(false);
    setClientSelectionData(null);
    setSimilarClients([]);
    setSelectedClient(null);
  };

  // Función auxiliar para obtener datos del formulario
  const getFormData = (): FormInputs | null => {
    const formData = getValues();
    return formData;
  };

  // Preparar datos para TimeGrid
  const prepareTimeGridData = () => {
    if (!cuadranteData) return [];

    return [
      {
        key: 'ocupacion',
        label: 'Ocupación',
        values: cuadranteData.timeSlots.map(slot => slot.ocupacion),
      },
      {
        key: 'disponibles',
        label: 'Disponibles',
        values: cuadranteData.timeSlots.map(slot => slot.disponibles),
      },
      {
        key: 'masajistas',
        label: 'Masajistas',
        values: cuadranteData.timeSlots.map(slot => slot.masajistasDisponibles),
      },
      {
        key: 'minutosOcupados',
        label: 'Minutos Ocupados',
        values: cuadranteData.timeSlots.map(slot => slot.minutosOcupados),
      },
      {
        key: 'minutosDisponibles',
        label: 'Minutos Disponibles',
        values: cuadranteData.timeSlots.map(slot => slot.minutosDisponibles),
      },
      {
        key: 'restricciones',
        label: 'Restricciones',
        values: constraintCells,
        editable: true,
        checkboxRow: true,
        onValuesChange: handleConstraintChange,
      },
    ];
  };

  // Función para convertir Booking a BookRow
  const convertBookingToBookRow = (booking: Booking): BookRow => {
    const today = new Date();
    const bookingDate = new Date(booking.booking_date);
    const isPastDate = bookingDate < today;
    
    // Determinar si está pagado (amount_pending es 0 o null)
    const isPaid = !booking.amount_pending || parseFloat(booking.amount_pending) === 0;
    
    return {
      id: booking.id?.toString() || '',
      clientId: booking.client_id,
      clientName: `${booking.client_id}`, // Por ahora solo el ID, se actualizará con la información del cliente
      entryTime: booking.hour || '00:00:00',
      people: booking.people,
      isPaid,
      hasCheckout: booking.checked_out,
      isPastDate,
      createdAt: booking.created_at || new Date().toISOString(),
    };
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

          <div className="card">
            <h3>Ver cuadrante</h3>
            <DatePicker 
            value={selectedDate} 
            onChange={(date) => setSelectedDate(date as Date | null)} 
            wrapperClassName="picker-dia"
            placeholderText="Selecciona fecha" />
            <div style={{ marginTop: '0.75rem' }}>
              <ReactiveButton
                style={{ backgroundColor: 'var(--color-primary)' }}
                idleText={loadingCuadrante ? "Cargando..." : "Ver cuadrante"}
                onClick={handleVerCuadrante}
                loading={loadingCuadrante}
                width={"100%"}
              />
            </div>
          </div>
        </aside>

        {/* Panel derecho */}
        <main>
            <div className="card">
              <h3>Reservar Baños</h3>
              
              {/* Buscador General */}
              <div style={{ marginBottom: '1.5rem' }}>
                
                <GeneralSearch 
                  onClientSelect={handleClientSelect}
                  onGiftVoucherSelect={handleGiftVoucherSelect}
                  placeholder="Buscar por nombre, teléfono, email, ID de reserva, cheque regalo..."
                />
                <p style={{ fontSize: '0.875rem', color: '#64748b', marginTop: '0.25rem' }}>
                  Busca clientes, reservas o cheques regalo para autocompletar los datos del formulario
                </p>
              </div>
              
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
                    {selectedGiftVoucher && (
                      <div style={{ 
                        marginBottom: '1rem', 
                        padding: '0.75rem', 
                        backgroundColor: '#f0f9ff', 
                        border: '1px solid #0ea5e9', 
                        borderRadius: '6px',
                        color: '#0369a1'
                      }}>
                        🎁 Usando cheque regalo con ID #{selectedGiftVoucher}
                        <button
                          type="button"
                          onClick={() => {
                            setSelectedGiftVoucher(null);
                            setSelectedGiftVoucherProductId(null);
                          }}
                          style={{
                            marginLeft: '0.5rem',
                            padding: '0.25rem 0.5rem',
                            backgroundColor: '#ef4444',
                            color: 'white',
                            border: 'none',
                            borderRadius: '4px',
                            fontSize: '0.75rem',
                            cursor: 'pointer'
                          }}
                        >
                          ✕ Limpiar
                        </button>
                      </div>
                    )}
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
                                  <input 
                                    type="number" 
                                    min={0} 
                                    {...register(nameKey as any, { valueAsNumber: true, min: 0 })} 
                                    style={{ width: '50%' }} 
                                    disabled={selectedGiftVoucher !== null}
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
                    style={{ backgroundColor: hasValidationError ? '#9ca3af' : 'var(--color-primary)', marginTop: '0.5rem' }}
                    idleText={hasValidationError ? "Corrige los errores primero" : "Insertar"}
                    type="submit"
                    width={"100%"}
                    disabled={hasValidationError}
                  />
                  </div>
                </div>
              </form>
            </div>
        </main>
      </div>

      {/* Cuadrante */}
      {loadingCuadrante && <p style={{ textAlign: 'center' }}>Cargando cuadrante...</p>}
      {!loadingCuadrante && cuadranteData && (
        <div className="card" style={{ marginTop: '2rem' }}>
          <h3>Cuadrante - {cuadranteData.date}</h3>
          <p>Aforo: {cuadranteData.capacity} personas</p>
          <TimeGrid
            rows={prepareTimeGridData()}
            start="10:00"
            end="22:00"
            stepMinutes={30}
            columnWidth={40}
          />
          
          {/* Botón para guardar restricciones */}
          {constraintChanged && (
            <div style={{ marginTop: '1rem' }}>
              <ReactiveButton
                style={{ backgroundColor: 'var(--color-secondary)' }}
                idleText={savingConstraints ? "Guardando..." : "Guardar restricciones de reservas"}
                onClick={handleSaveConstraints}
                loading={savingConstraints}
                disabled={savingConstraints}
              />
            </div>
          )}
          
          {/* Tabla de reservas */}
          {bookings.length > 0 && (
            <div style={{ marginTop: '2rem' }}>
              <h4>Reservas del día</h4>
              <BookGrid 
                books={bookings} 
                onBookingChanged={handleVerCuadrante}
              />
            </div>
          )}
          
          {/* Lista de masajes */}
          <MassageGrid 
            reservations={massageReservations} 
            selectedDate={selectedDate ? toLocalISODate(selectedDate) : undefined}
          />
        </div>
      )}

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

      {/* Modal de selección de clientes */}
      <DefaultDialog
        open={showClientModal}
        title={showNewClientForm ? "Crear Nuevo Cliente" : "Cliente Existente Encontrado"}
        onClose={handleCloseClientModal}
        width="900px"
      >
        {loadingClients ? (
          <p>Buscando clientes similares...</p>
        ) : showNewClientForm ? (
          // Formulario de nuevo cliente
          <ClientNewForm 
            selectedClient={selectedClient}
            searchData={clientSelectionData || { name: '', surname: '', email: '', phone_number: '' }}
            onConfirm={handleConfirmNewClient}
            onCancel={handleCancelNewClient}
          />
        ) : similarClients.length === 0 ? (
          <p>No se encontraron clientes similares. Se procederá a crear un cliente nuevo.</p>
        ) : (
          // Vista principal de selección
          <ClientSelectionContent
            similarClients={similarClients}
            selectedClient={selectedClient}
            onClientSelect={setSelectedClient}
            onUseExisting={handleUseExistingClient}
            onCreateNew={handleCreateNewClientFromModal}
            searchData={clientSelectionData || { name: '', surname: '', email: '', phone_number: '' }}
            onConfirmNewClient={handleConfirmNewClient}
          />
        )}
      </DefaultDialog>
    </div>
  );
};

// Componente auxiliar para el contenido de selección de clientes
const ClientSelectionContent: React.FC<{
  similarClients: ClienteService[];
  selectedClient: ClienteService | null;
  onClientSelect: (client: ClienteService) => void;
  onUseExisting: () => void;
  onCreateNew: () => void;
  searchData: { name: string; surname: string; email: string; phone_number: string };
  onConfirmNewClient: (data: { name: string; surname: string; email: string; phone_number: string }) => void;
}> = ({ similarClients, selectedClient, onClientSelect, onUseExisting, onCreateNew, searchData, onConfirmNewClient }) => {
  const [showNewClientForm, setShowNewClientForm] = React.useState(false);
  const getMatchBadges = (client: ClienteService): string[] => {
    if (!client.match_info) return [];
    
    const badges: string[] = [];
    if (client.match_info.email) badges.push('📧 Email');
    if (client.match_info.phone) badges.push('📞 Teléfono');
    if (client.match_info.name) badges.push('👤 Nombre');
    if (client.match_info.surname) badges.push('👥 Apellidos');
    if (client.match_info.name_surname_combo) badges.push('🔗 Nombre+Apellidos');
    
    return badges;
  };

  const handleCreateNewClick = () => {
    setShowNewClientForm(true);
  };

  const handleCancelNewClient = () => {
    setShowNewClientForm(false);
  };

  const handleConfirmNewClient = (finalData: { name: string; surname: string; email: string; phone_number: string }) => {
    onConfirmNewClient(finalData);
  };

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '300px 1fr', gap: '1rem', height: '400px' }}>
      {/* Lista de clientes (izquierda) */}
      <div style={{ border: '1px solid #ddd', borderRadius: '4px', overflow: 'hidden' }}>
        <h4 style={{ margin: 0, padding: '0.75rem', backgroundColor: '#f5f5f5', borderBottom: '1px solid #ddd' }}>
          CLIENTES
        </h4>
        <div style={{ height: '350px', overflowY: 'auto' }}>
          {similarClients.map((client) => (
            <div
              key={client.id}
              onClick={() => onClientSelect(client)}
              style={{
                padding: '0.75rem',
                borderBottom: '1px solid #eee',
                cursor: 'pointer',
                backgroundColor: selectedClient?.id === client.id ? '#e3f2fd' : 'white',
              }}
            >
              <div style={{ fontWeight: 'bold', fontSize: '0.9rem' }}>
                {client.name} {client.surname}
              </div>
              <div style={{ fontSize: '0.8rem', color: '#666', marginTop: '0.25rem' }}>
                {client.email || 'Sin email'} | {client.phone_number || 'Sin teléfono'}
              </div>
              
              {/* Badges de coincidencias */}
              <div style={{ marginTop: '0.5rem' }}>
                {getMatchBadges(client).map((badge, index) => (
                  <span
                    key={index}
                    style={{
                      display: 'inline-block',
                      fontSize: '0.7rem',
                      padding: '0.2rem 0.4rem',
                      backgroundColor: '#e0f7fa',
                      color: '#00695c',
                      borderRadius: '3px',
                      marginRight: '0.25rem',
                      marginBottom: '0.25rem',
                    }}
                  >
                    {badge}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Panel derecho con información del cliente seleccionado */}
      <div style={{ border: '1px solid #ddd', borderRadius: '4px', padding: '1rem' }}>
        {selectedClient ? (
          <div>
            <p style={{ fontSize: '0.9rem', color: '#333', marginBottom: '0.75rem' }}>
              <strong>Ya existe un cliente con esta información:</strong>
            </p>
            
            <div style={{ marginBottom: '0.75rem', fontSize: '0.85rem' }}>
              <p style={{ margin: '0.25rem 0' }}><strong>Nombre:</strong> {selectedClient.name} {selectedClient.surname}</p>
              <p style={{ margin: '0.25rem 0' }}><strong>Teléfono:</strong> {selectedClient.phone_number || 'No disponible'}</p>
              <p style={{ margin: '0.25rem 0' }}><strong>Correo:</strong> {selectedClient.email || 'No disponible'}</p>
              <p style={{ margin: '0.25rem 0' }}><strong>Fecha creación:</strong> {selectedClient.created_at ? new Date(selectedClient.created_at).toLocaleDateString('es-ES') : 'No disponible'}</p>
            </div>

            {!showNewClientForm && (
              <>
                <p style={{ marginBottom: '1rem', color: '#666', fontSize: '0.85rem' }}>
                  ¿Te gustaría utilizar este cliente para la reserva, o prefieres crear uno nuevo?
                </p>

                {/* Botones principales */}
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  <ReactiveButton
                    style={{ backgroundColor: '#6c757d' }}
                    idleText="Crear uno nuevo"
                    onClick={handleCreateNewClick}
                  />
                  <ReactiveButton
                    style={{ backgroundColor: 'var(--color-primary)' }}
                    idleText="Utilizar este cliente"
                    onClick={onUseExisting}
                  />
                </div>
              </>
            )}

            {showNewClientForm && (
              <ClientNewFormInline 
                selectedClient={selectedClient}
                searchData={searchData}
                onConfirm={handleConfirmNewClient}
                onCancel={handleCancelNewClient}
              />
            )}
          </div>
        ) : (
          <p>Selecciona un cliente de la lista para ver su información.</p>
        )}
      </div>
    </div>
  );
};

// Componente auxiliar para el formulario de nuevo cliente
const ClientNewForm: React.FC<{
  selectedClient: ClienteService | null;
  searchData: { name: string; surname: string; email: string; phone_number: string };
  onConfirm: (data: { name: string; surname: string; email: string; phone_number: string }) => void;
  onCancel: () => void;
}> = ({ selectedClient, searchData, onConfirm, onCancel }) => {
  type FieldSource = 'existing' | 'new';
  
  const [sources, setSources] = React.useState<{
    nameSource: FieldSource;
    surnameSource: FieldSource;
    emailSource: FieldSource;
    phoneSource: FieldSource;
  }>({
    nameSource: 'new',
    surnameSource: 'new',
    emailSource: 'new',
    phoneSource: 'new',
  });

  const getFieldValue = (field: 'name' | 'surname' | 'email' | 'phone_number'): string => {
    const sourceField = `${field === 'phone_number' ? 'phone' : field}Source` as keyof typeof sources;
    const source = sources[sourceField];
    
    if (source === 'existing' && selectedClient) {
      return (selectedClient[field] || '') as string;
    }
    return searchData[field] || '';
  };

  const handleConfirm = () => {
    const finalData = {
      name: getFieldValue('name'),
      surname: getFieldValue('surname'),
      email: getFieldValue('email'),
      phone_number: getFieldValue('phone_number'),
    };
    onConfirm(finalData);
  };

  const updateSource = (field: keyof typeof sources, value: FieldSource) => {
    setSources(prev => ({ ...prev, [field]: value }));
  };

  return (
    <div>
      <p style={{ marginBottom: '1rem', color: '#666' }}>
        Selecciona qué datos usar para el nuevo cliente:
      </p>
      
      {selectedClient && (
        <div style={{ marginBottom: '1.5rem', padding: '1rem', backgroundColor: '#f9f9f9', borderRadius: '4px' }}>
          <h4>Cliente seleccionado: {selectedClient.name} {selectedClient.surname}</h4>
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 150px 150px', gap: '0.5rem', alignItems: 'center' }}>
        {/* Headers */}
        <div></div>
        <div style={{ textAlign: 'center', fontWeight: 'bold', fontSize: '0.9rem' }}>Del cliente existente</div>
        <div style={{ textAlign: 'center', fontWeight: 'bold', fontSize: '0.9rem' }}>Del formulario nuevo</div>

        {/* Campos */}
        {[
          { field: 'nameSource', label: 'Nombre:', existing: selectedClient?.name, new: searchData.name },
          { field: 'surnameSource', label: 'Apellidos:', existing: selectedClient?.surname, new: searchData.surname },
          { field: 'emailSource', label: 'Email:', existing: selectedClient?.email, new: searchData.email },
          { field: 'phoneSource', label: 'Teléfono:', existing: selectedClient?.phone_number, new: searchData.phone_number },
        ].map(({ field, label, existing, new: newValue }) => (
          <React.Fragment key={field}>
            <div style={{ fontWeight: 'bold' }}>{label}</div>
            <label style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <input
                type="radio"
                name={field}
                checked={sources[field as keyof typeof sources] === 'existing'}
                onChange={() => updateSource(field as keyof typeof sources, 'existing')}
                disabled={!existing}
              />
              <span style={{ marginLeft: '0.25rem', fontSize: '0.8rem' }}>{existing || 'N/A'}</span>
            </label>
            <label style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <input
                type="radio"
                name={field}
                checked={sources[field as keyof typeof sources] === 'new'}
                onChange={() => updateSource(field as keyof typeof sources, 'new')}
              />
              <span style={{ marginLeft: '0.25rem', fontSize: '0.8rem' }}>{newValue || 'N/A'}</span>
            </label>
          </React.Fragment>
        ))}
      </div>

      {/* Vista previa del nuevo cliente */}
      <div style={{ marginTop: '1.5rem', padding: '1rem', backgroundColor: '#e8f4fd', borderRadius: '4px' }}>
        <h4>Vista previa del nuevo cliente:</h4>
        <p><strong>Nombre:</strong> {getFieldValue('name')}</p>
        <p><strong>Apellidos:</strong> {getFieldValue('surname')}</p>
        <p><strong>Email:</strong> {getFieldValue('email')}</p>
        <p><strong>Teléfono:</strong> {getFieldValue('phone_number')}</p>
      </div>

      {/* Botones del formulario de nuevo cliente */}
      <div style={{ display: 'flex', gap: '0.5rem', marginTop: '1.5rem', justifyContent: 'flex-end' }}>
        <ReactiveButton
          style={{ backgroundColor: '#6c757d' }}
          idleText="Cancelar"
          onClick={onCancel}
        />
        <ReactiveButton
          style={{ backgroundColor: 'var(--color-primary)' }}
          idleText="Crear Cliente"
          onClick={handleConfirm}
        />
      </div>
    </div>
  );
};

// Componente auxiliar para el formulario de nuevo cliente inline
const ClientNewFormInline: React.FC<{
  selectedClient: ClienteService | null;
  searchData: { name: string; surname: string; email: string; phone_number: string };
  onConfirm: (data: { name: string; surname: string; email: string; phone_number: string }) => void;
  onCancel: () => void;
}> = ({ selectedClient, searchData, onConfirm, onCancel }) => {
  type FieldSource = 'existing' | 'new';
  
  const [sources, setSources] = React.useState<{
    nameSource: FieldSource;
    surnameSource: FieldSource;
    emailSource: FieldSource;
    phoneSource: FieldSource;
  }>({
    nameSource: 'new',
    surnameSource: 'new',
    emailSource: 'new',
    phoneSource: 'new',
  });

  const getFieldValue = (field: 'name' | 'surname' | 'email' | 'phone_number'): string => {
    const sourceField = `${field === 'phone_number' ? 'phone' : field}Source` as keyof typeof sources;
    const source = sources[sourceField];
    
    if (source === 'existing' && selectedClient) {
      return (selectedClient[field] || '') as string;
    }
    return searchData[field] || '';
  };

  const handleConfirm = () => {
    const finalData = {
      name: getFieldValue('name'),
      surname: getFieldValue('surname'),
      email: getFieldValue('email'),
      phone_number: getFieldValue('phone_number'),
    };
    onConfirm(finalData);
  };

  const updateSource = (field: keyof typeof sources, value: FieldSource) => {
    setSources(prev => ({ ...prev, [field]: value }));
  };

  return (
    <div style={{ marginTop: '1rem', borderTop: '1px solid #eee', paddingTop: '1rem' }}>
      <p style={{ marginBottom: '0.75rem', color: '#666', fontSize: '0.85rem' }}>
        Selecciona qué datos usar para el nuevo cliente:
      </p>
      
      <div style={{ display: 'grid', gridTemplateColumns: '80px 1fr 1fr', gap: '0.25rem', alignItems: 'center', fontSize: '0.8rem' }}>
        {/* Headers */}
        <div></div>
        <div style={{ textAlign: 'center', fontWeight: 'bold' }}>Existente</div>
        <div style={{ textAlign: 'center', fontWeight: 'bold' }}>Nuevo</div>

        {/* Campos */}
        {[
          { field: 'nameSource', label: 'Nombre:', existing: selectedClient?.name, new: searchData.name },
          { field: 'surnameSource', label: 'Apellidos:', existing: selectedClient?.surname, new: searchData.surname },
          { field: 'emailSource', label: 'Email:', existing: selectedClient?.email, new: searchData.email },
          { field: 'phoneSource', label: 'Teléfono:', existing: selectedClient?.phone_number, new: searchData.phone_number },
        ].map(({ field, label, existing, new: newValue }) => (
          <React.Fragment key={field}>
            <div style={{ fontWeight: 'bold', fontSize: '0.75rem' }}>{label}</div>
            <label style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '0.25rem' }}>
              <input
                type="radio"
                name={field}
                checked={sources[field as keyof typeof sources] === 'existing'}
                onChange={() => updateSource(field as keyof typeof sources, 'existing')}
                disabled={!existing}
                style={{ marginRight: '0.25rem' }}
              />
              <span style={{ fontSize: '0.7rem' }}>{existing || 'N/A'}</span>
            </label>
            <label style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '0.25rem' }}>
              <input
                type="radio"
                name={field}
                checked={sources[field as keyof typeof sources] === 'new'}
                onChange={() => updateSource(field as keyof typeof sources, 'new')}
                style={{ marginRight: '0.25rem' }}
              />
              <span style={{ fontSize: '0.7rem' }}>{newValue || 'N/A'}</span>
            </label>
          </React.Fragment>
        ))}
      </div>

      {/* Vista previa del nuevo cliente */}
      <div style={{ marginTop: '0.75rem', padding: '0.5rem', backgroundColor: '#e8f4fd', borderRadius: '4px' }}>
        <h4 style={{ margin: '0 0 0.5rem 0', fontSize: '0.8rem' }}>Vista previa:</h4>
        <div style={{ fontSize: '0.75rem' }}>
          <span><strong>Nombre:</strong> {getFieldValue('name')} {getFieldValue('surname')} | </span>
          <span><strong>Email:</strong> {getFieldValue('email')} | </span>
          <span><strong>Teléfono:</strong> {getFieldValue('phone_number')}</span>
        </div>
      </div>

      {/* Botones del formulario de nuevo cliente */}
      <div style={{ display: 'flex', gap: '0.5rem', marginTop: '1rem', justifyContent: 'flex-end' }}>
        <ReactiveButton
          style={{ backgroundColor: '#6c757d' }}
          idleText="Cancelar"
          onClick={onCancel}
        />
        <ReactiveButton
          style={{ backgroundColor: 'var(--color-primary)' }}
          idleText="Crear Cliente"
          onClick={handleConfirm}
        />
      </div>
    </div>
  );
};

export default CuadrantePage;