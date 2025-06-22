import React, { useEffect, useState } from 'react';
import ManagementTable, { ColumnDef } from '@/components/managetable/ManagementTable';
import { getClientes, Client } from '@/services/clientes.service';

const ClientesPage: React.FC = () => {
  const [rows, setRows] = useState<Client[]>([]);
  const [loading, setLoading] = useState(false);

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

  const columns: ColumnDef<Client>[] = [
    { header: 'ID', accessor: 'id', width: 60 },
    { header: 'Nombre', accessor: (c) => `${c.name} ${c.surname ?? ''}` },
    { header: 'Email', accessor: 'email' },
    { header: 'Teléfono', accessor: 'phone_number' },
    { header: 'Registro', accessor: (c) => c.created_at?.substring(0, 16).replace('T', ' ') },
  ];

  return (
    <div style={{ padding: '1rem' }}>
      <h2>Clientes</h2>
      {loading ? <p>Cargando…</p> : <ManagementTable columns={columns} rows={rows} />}
    </div>
  );
};

export default ClientesPage; 