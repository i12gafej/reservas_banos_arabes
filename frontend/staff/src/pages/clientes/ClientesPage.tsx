import React, { useEffect, useState } from 'react';
import ReactiveButton from 'reactive-button';
import ManagementTable, { ColumnDef } from '@/components/managetable/ManagementTable';
import { DefaultDialog } from '@/components/elements';
import { getClientes, Client, getDuplicatesPreview, unifyClients, DuplicatesPreview, UnificationResult } from '@/services/clientes.service';

const ClientesPage: React.FC = () => {
  const [rows, setRows] = useState<Client[]>([]);
  const [loading, setLoading] = useState(false);
  
  // Estados para unificación de clientes
  const [showUnificationDialog, setShowUnificationDialog] = useState(false);
  const [duplicatesPreview, setDuplicatesPreview] = useState<DuplicatesPreview | null>(null);
  const [loadingPreview, setLoadingPreview] = useState(false);
  const [unifying, setUnifying] = useState(false);
  const [unificationResult, setUnificationResult] = useState<UnificationResult | null>(null);

  useEffect(() => {
    const load = async () => {
      try {
        setLoading(true);
        const data = await getClientes();
        setRows(data);
      } catch (err) {
        // eslint-disable-next-line no-console
        console.error('Error cargando clientes', err);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  // Función para abrir el diálogo y cargar vista previa
  const handleOpenUnificationDialog = async () => {
    setShowUnificationDialog(true);
    setLoadingPreview(true);
    setUnificationResult(null);
    
    try {
      const preview = await getDuplicatesPreview();
      setDuplicatesPreview(preview);
    } catch (err) {
      console.error('Error cargando vista previa de duplicados:', err);
      alert('Error al cargar la vista previa de duplicados');
    } finally {
      setLoadingPreview(false);
    }
  };

  // Función para ejecutar la unificación
  const handleUnifyClients = async () => {
    // Validaciones antes de ejecutar
    if (unifying || loadingPreview) {
      return;
    }
    
    if (!duplicatesPreview || duplicatesPreview.total_groups === 0) {
      alert('No hay clientes duplicados para unificar');
      return;
    }
    
    setUnifying(true);
    try {
      const result = await unifyClients();
      setUnificationResult(result);
      
      if (result.success) {
        // Recargar la lista de clientes
        const data = await getClientes();
        setRows(data);
      }
    } catch (err) {
      console.error('Error durante la unificación:', err);
      alert('Error durante la unificación de clientes');
    } finally {
      setUnifying(false);
    }
  };

  // Función para cerrar el diálogo
  const handleCloseDialog = () => {
    setShowUnificationDialog(false);
    setDuplicatesPreview(null);
    setUnificationResult(null);
  };

  const columns: ColumnDef<Client>[] = [
    { header: 'ID', accessor: 'id', width: 60 },
    { header: 'Nombre', accessor: (c) => `${c.name} ${c.surname ?? ''}` },
    { header: 'Email', accessor: 'email' },
    { header: 'Teléfono', accessor: 'phone_number' },
    { header: 'Registro', accessor: (c) => c.created_at?.substring(0, 16).replace('T', ' ') },
  ];

  return (
    <div style={{ padding: '1rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <h2>Clientes</h2>
        <ReactiveButton
          style={{ backgroundColor: 'var(--color-secondary)' }}
          idleText="🔄 Unificar Clientes Duplicados"
          onClick={handleOpenUnificationDialog}
          disabled={loading}
        />
      </div>
      
      {loading ? <p>Cargando…</p> : <ManagementTable columns={columns} rows={rows} />}

      {/* Modal de Unificación */}
      <DefaultDialog
        open={showUnificationDialog}
        title="Unificar Clientes Duplicados"
        onClose={handleCloseDialog}
        onSave={unificationResult ? undefined : handleUnifyClients}
        saveLabel={unificationResult ? undefined : (unifying ? "Unificando..." : "Ejecutar Unificación")}
      >
        {loadingPreview ? (
          <p>Cargando vista previa de duplicados...</p>
        ) : unificationResult ? (
          <div>
            <h4 style={{ color: unificationResult.success ? 'green' : 'red' }}>
              {unificationResult.success ? '✅ Unificación Completada' : '❌ Error en Unificación'}
            </h4>
            <p>{unificationResult.message}</p>
            {unificationResult.success && (
              <ul>
                <li>Grupos unificados: {unificationResult.unified_groups}</li>
                <li>Clientes eliminados: {unificationResult.clients_removed}</li>
                <li>Reservas actualizadas: {unificationResult.books_updated}</li>
                <li>Cheques regalo actualizados: {unificationResult.gift_vouchers_updated}</li>
              </ul>
            )}
          </div>
        ) : duplicatesPreview ? (
          <div>
            {duplicatesPreview.total_groups === 0 ? (
              <p>🎉 No se encontraron clientes duplicados en el sistema.</p>
            ) : (
              <div>
                <p>
                  <strong>Se encontraron {duplicatesPreview.total_groups} grupos</strong> con un total de{' '}
                  <strong>{duplicatesPreview.total_duplicates} clientes duplicados</strong>.
                </p>
                
                <div style={{ maxHeight: '400px', overflowY: 'auto', border: '1px solid #ddd', borderRadius: '4px', padding: '1rem' }}>
                  {duplicatesPreview.groups.map((group, index) => (
                    <div key={index} style={{ marginBottom: '1rem', padding: '0.5rem', backgroundColor: '#f9f9f9', borderRadius: '4px' }}>
                      <p><strong>📧 {group.email}</strong> | <strong>📞 {group.phone}</strong></p>
                      
                      <div style={{ marginLeft: '1rem' }}>
                        <p style={{ color: 'green' }}>
                          <strong>✅ Cliente principal:</strong> {group.main_client.name} {group.main_client.surname} (ID: {group.main_client.id})
                        </p>
                        
                        <p style={{ color: 'red' }}>
                          <strong>🗑️ Se eliminarán:</strong>{' '}
                          {group.duplicates.map(d => `${d.name} ${d.surname} (ID: ${d.id})`).join(', ')}
                        </p>
                        
                        <p style={{ fontSize: '0.9rem', color: '#666' }}>
                          📝 Reservas a actualizar: {group.books_to_update} | 🎁 Cheques a actualizar: {group.vouchers_to_update}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
                
                <p style={{ marginTop: '1rem', fontWeight: 'bold', color: '#d9534f' }}>
                  ⚠️ Esta acción es irreversible. ¿Deseas continuar?
                </p>
              </div>
            )}
          </div>
        ) : null}
      </DefaultDialog>
    </div>
  );
};

export default ClientesPage; 