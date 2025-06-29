import React, { useState, useEffect } from 'react';
import ReactiveButton from 'reactive-button';
import { DefaultDialog } from '@/components/elements';
import { findSimilarClients, Client } from '@/services/clientes.service';

interface ClientSelectionModalProps {
  open: boolean;
  onClose: () => void;
  searchData: {
    name: string;
    surname: string;
    email: string;
    phone_number: string;
  };
  onClientSelected: (clientId: number) => void;
  onNewClientData: (clientData: {
    name: string;
    surname: string;
    email: string;
    phone_number: string;
  }) => void;
}

type FieldSource = 'existing' | 'new';

interface NewClientForm {
  name: string;
  surname: string;
  email: string;
  phone_number: string;
  nameSource: FieldSource;
  surnameSource: FieldSource;
  emailSource: FieldSource;
  phoneSource: FieldSource;
}

const ClientSelectionModal: React.FC<ClientSelectionModalProps> = ({
  open,
  onClose,
  searchData,
  onClientSelected,
  onNewClientData,
}) => {
  const [loading, setLoading] = useState(false);
  const [similarClients, setSimilarClients] = useState<Client[]>([]);
  const [selectedClient, setSelectedClient] = useState<Client | null>(null);
  const [showNewClientForm, setShowNewClientForm] = useState(false);
  const [newClientForm, setNewClientForm] = useState<NewClientForm>({
    name: searchData.name,
    surname: searchData.surname,
    email: searchData.email,
    phone_number: searchData.phone_number,
    nameSource: 'new',
    surnameSource: 'new',
    emailSource: 'new',
    phoneSource: 'new',
  });

  // Cargar clientes similares cuando se abre el modal
  useEffect(() => {
    if (open) {
      loadSimilarClients();
    }
  }, [open, searchData]);

  const loadSimilarClients = async () => {
    setLoading(true);
    try {
      const clients = await findSimilarClients(searchData);
      setSimilarClients(clients);
      if (clients.length > 0) {
        setSelectedClient(clients[0]);
      }
    } catch (error) {
      console.error('Error cargando clientes similares:', error);
      setSimilarClients([]);
    } finally {
      setLoading(false);
    }
  };

  const handleUseExistingClient = () => {
    if (selectedClient) {
      onClientSelected(selectedClient.id);
      onClose();
    }
  };

  const handleCreateNewClient = () => {
    setShowNewClientForm(true);
    // Resetear formulario con datos del cliente seleccionado como opción
    if (selectedClient) {
      setNewClientForm({
        name: searchData.name,
        surname: searchData.surname,
        email: searchData.email,
        phone_number: searchData.phone_number,
        nameSource: 'new',
        surnameSource: 'new',
        emailSource: 'new',
        phoneSource: 'new',
      });
    }
  };

  const handleCancelNewClient = () => {
    setShowNewClientForm(false);
  };

  const handleConfirmNewClient = () => {
    // Construir datos finales del nuevo cliente
    const finalClientData = {
      name: newClientForm.nameSource === 'existing' && selectedClient ? selectedClient.name : newClientForm.name,
      surname: newClientForm.surnameSource === 'existing' && selectedClient ? (selectedClient.surname || '') : newClientForm.surname,
      email: newClientForm.emailSource === 'existing' && selectedClient ? (selectedClient.email || '') : newClientForm.email,
      phone_number: newClientForm.phoneSource === 'existing' && selectedClient ? (selectedClient.phone_number || '') : newClientForm.phone_number,
    };

    onNewClientData(finalClientData);
    onClose();
  };

  const updateNewClientField = (field: keyof NewClientForm, value: string | FieldSource) => {
    setNewClientForm(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const getFieldValue = (field: 'name' | 'surname' | 'email' | 'phone_number'): string => {
    const sourceField = `${field}Source` as keyof NewClientForm;
    const source = newClientForm[sourceField] as FieldSource;
    
    if (source === 'existing' && selectedClient) {
      return (selectedClient[field] || '') as string;
    }
    return newClientForm[field];
  };

  const getMatchBadges = (client: Client): string[] => {
    if (!client.match_info) return [];
    
    const badges: string[] = [];
    if (client.match_info.email) badges.push('📧 Email');
    if (client.match_info.phone) badges.push('📞 Teléfono');
    if (client.match_info.name) badges.push('👤 Nombre');
    if (client.match_info.surname) badges.push('👥 Apellidos');
    if (client.match_info.name_surname_combo) badges.push('🔗 Nombre+Apellidos');
    
    return badges;
  };

  if (!open) return null;

  return (
    <DefaultDialog
      open={open}
      title={showNewClientForm ? "Crear Nuevo Cliente" : "Cliente Existente Encontrado"}
      onClose={onClose}
      width="900px"
    >
      {loading ? (
        <p>Buscando clientes similares...</p>
      ) : showNewClientForm ? (
        // Formulario de nuevo cliente
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

            {/* Nombre */}
            <div style={{ fontWeight: 'bold' }}>Nombre:</div>
            <label style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <input
                type="radio"
                name="nameSource"
                checked={newClientForm.nameSource === 'existing'}
                onChange={() => updateNewClientField('nameSource', 'existing')}
                disabled={!selectedClient?.name}
              />
              <span style={{ marginLeft: '0.25rem', fontSize: '0.8rem' }}>{selectedClient?.name || 'N/A'}</span>
            </label>
            <label style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <input
                type="radio"
                name="nameSource"
                checked={newClientForm.nameSource === 'new'}
                onChange={() => updateNewClientField('nameSource', 'new')}
              />
              <span style={{ marginLeft: '0.25rem', fontSize: '0.8rem' }}>{searchData.name || 'N/A'}</span>
            </label>

            {/* Apellidos */}
            <div style={{ fontWeight: 'bold' }}>Apellidos:</div>
            <label style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <input
                type="radio"
                name="surnameSource"
                checked={newClientForm.surnameSource === 'existing'}
                onChange={() => updateNewClientField('surnameSource', 'existing')}
                disabled={!selectedClient?.surname}
              />
              <span style={{ marginLeft: '0.25rem', fontSize: '0.8rem' }}>{selectedClient?.surname || 'N/A'}</span>
            </label>
            <label style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <input
                type="radio"
                name="surnameSource"
                checked={newClientForm.surnameSource === 'new'}
                onChange={() => updateNewClientField('surnameSource', 'new')}
              />
              <span style={{ marginLeft: '0.25rem', fontSize: '0.8rem' }}>{searchData.surname || 'N/A'}</span>
            </label>

            {/* Email */}
            <div style={{ fontWeight: 'bold' }}>Email:</div>
            <label style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <input
                type="radio"
                name="emailSource"
                checked={newClientForm.emailSource === 'existing'}
                onChange={() => updateNewClientField('emailSource', 'existing')}
                disabled={!selectedClient?.email}
              />
              <span style={{ marginLeft: '0.25rem', fontSize: '0.8rem' }}>{selectedClient?.email || 'N/A'}</span>
            </label>
            <label style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <input
                type="radio"
                name="emailSource"
                checked={newClientForm.emailSource === 'new'}
                onChange={() => updateNewClientField('emailSource', 'new')}
              />
              <span style={{ marginLeft: '0.25rem', fontSize: '0.8rem' }}>{searchData.email || 'N/A'}</span>
            </label>

            {/* Teléfono */}
            <div style={{ fontWeight: 'bold' }}>Teléfono:</div>
            <label style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <input
                type="radio"
                name="phoneSource"
                checked={newClientForm.phoneSource === 'existing'}
                onChange={() => updateNewClientField('phoneSource', 'existing')}
                disabled={!selectedClient?.phone_number}
              />
              <span style={{ marginLeft: '0.25rem', fontSize: '0.8rem' }}>{selectedClient?.phone_number || 'N/A'}</span>
            </label>
            <label style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <input
                type="radio"
                name="phoneSource"
                checked={newClientForm.phoneSource === 'new'}
                onChange={() => updateNewClientField('phoneSource', 'new')}
              />
              <span style={{ marginLeft: '0.25rem', fontSize: '0.8rem' }}>{searchData.phone_number || 'N/A'}</span>
            </label>
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
              onClick={handleCancelNewClient}
            />
            <ReactiveButton
              style={{ backgroundColor: 'var(--color-primary)' }}
              idleText="Crear Cliente"
              onClick={handleConfirmNewClient}
            />
          </div>
        </div>
      ) : similarClients.length === 0 ? (
        <p>No se encontraron clientes similares. Se procederá a crear un cliente nuevo.</p>
      ) : (
        // Vista principal de selección
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
                  onClick={() => setSelectedClient(client)}
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
                <p style={{ fontSize: '1rem', color: '#333', marginBottom: '1rem' }}>
                  <strong>Ya existe un cliente con esta información:</strong>
                </p>
                
                <div style={{ marginBottom: '1rem' }}>
                  <p><strong>Nombre:</strong> {selectedClient.name} {selectedClient.surname}</p>
                  <p><strong>Teléfono:</strong> {selectedClient.phone_number || 'No disponible'}</p>
                  <p><strong>Correo:</strong> {selectedClient.email || 'No disponible'}</p>
                  <p><strong>Fecha creación:</strong> {selectedClient.created_at ? new Date(selectedClient.created_at).toLocaleDateString('es-ES') : 'No disponible'}</p>
                </div>

                <p style={{ marginBottom: '1.5rem', color: '#666' }}>
                  ¿Te gustaría utilizar este cliente para la reserva, o prefieres crear uno nuevo?
                </p>

                {/* Botones principales */}
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  <ReactiveButton
                    style={{ backgroundColor: '#6c757d' }}
                    idleText="Crear uno nuevo"
                    onClick={handleCreateNewClient}
                  />
                  <ReactiveButton
                    style={{ backgroundColor: 'var(--color-primary)' }}
                    idleText="Utilizar este cliente"
                    onClick={handleUseExistingClient}
                  />
                </div>
              </div>
            ) : (
              <p>Selecciona un cliente de la lista para ver su información.</p>
            )}
          </div>
        </div>
      )}
    </DefaultDialog>
  );
};

export default ClientSelectionModal;
