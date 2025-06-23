import React, { useEffect, useState } from 'react';
import ManagementTable, { ColumnDef } from '@/components/managetable/ManagementTable';
import { getReservas } from '@/services/reservas.service';
import { Booking } from '@/services/cuadrante.service';
import { getProducts, Product } from '@/services/productos.service';

const ReservasPage: React.FC = () => {
  const [rows, setRows] = useState<Booking[]>([]);
  const [loading, setLoading] = useState(false);
  const [prodMap, setProdMap] = useState<Record<number,string>>({});
  const [clientMap, setClientMap] = useState<Record<number,string>>({});

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        const data = await getReservas();
        setRows(data);
        // cargar productos para mapear nombres
        const baseUrl = (import.meta.env.VITE_API_URL ?? '').replace(/\/$/, '');
        const clientDataPromise: Promise<any[]> = window.fetch(`${baseUrl}/clientes/`).then((r) => r.json());
        const [prods, clients] = await Promise.all([
          getProducts(),
          clientDataPromise,
        ]);
        const map: Record<number,string> = {};
        prods.forEach((p: Product)=>{map[p.id]=p.name;});
        setProdMap(map);

        const cMap: Record<number,string> = {};
        clients.forEach((c:any)=>{cMap[c.id]=`${c.name} ${c.surname??''}`.trim();});
        setClientMap(cMap);
      } catch (err) {
        // eslint-disable-next-line no-console
        console.error('Error cargando reservas', err);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  const columns: ColumnDef<Booking>[] = [
    { header: 'Pedido', accessor: 'internal_order_id' },
    { header: 'Estado', accessor: (r) => {
      if (r.checked_out) return 'Finalizada';
      if (r.checked_in) return 'Registrada';
      return 'Pendiente';
    }},
    { header: 'Producto', accessor: (r) => prodMap[r.product_id] ?? `Prod ${r.product_id}` },
    { header: 'Fecha', accessor: (r) => r.booking_date?.substring(0,10) },
    { header: 'Hora', accessor: (r)=> r.hour?.substring(0,5) },
    { header: 'Cliente', accessor: (r)=> clientMap[r.client_id] ?? r.client_id },
    { header: 'Coste', accessor: 'amount_pending' },
    { header: 'Personas', accessor: 'people' },
    { header: 'Creación', accessor: (r)=> r.created_at?.substring(0,16).replace('T',' ') },
  ];

  return (
    <div style={{ padding:'1rem' }}>
      <h2>Reservas</h2>
      {loading ? <p>Cargando…</p> : <ManagementTable columns={columns} rows={rows} />}
    </div>
  );
};

export default ReservasPage; 