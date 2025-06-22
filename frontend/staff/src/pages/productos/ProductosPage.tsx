import React, { useEffect, useState } from 'react';
import ReactiveButton from 'reactive-button';
import { DefaultDialog } from '@/components/elements';
import { getBathTypes, updateBathTypePrice, createProduct, getProducts, updateProduct, BathType, Product } from '@/services/productos.service';
import './productos.css';

const TAB_BATHS = 'baths';
const TAB_PRODUCTS = 'products';

const ProductosPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>(TAB_BATHS);
  const [bathTypes, setBathTypes] = useState<BathType[]>([]);
  const [loading, setLoading] = useState(false);
  const [editedPrices, setEditedPrices] = useState<Record<number, string>>({});

  // Dialogo creación producto
  const [openCreateDlg, setOpenCreateDlg] = useState(false);
  const [prodName, setProdName] = useState('');
  const [prodObs, setProdObs] = useState('');
  const [prodDesc, setProdDesc] = useState('');
  const [prodPrice, setProdPrice] = useState('');
  const [prodVisible, setProdVisible] = useState(true);
  const [prodBaths, setProdBaths] = useState<{ bath_type_id: number; quantity: number }[]>([]);

  // Formulario de alta rápida
  const [newBathTypeId, setNewBathTypeId] = useState<number | undefined>(undefined);
  const [newBathQty, setNewBathQty] = useState<number>(1);

  const [products, setProducts] = useState<Product[]>([]);

  // Edición producto
  const [editProduct, setEditProduct] = useState<Product | null>(null);

  // Cargar datos iniciales
  useEffect(() => {
    if (activeTab === TAB_BATHS) {
      fetchBathTypes();
    }
    if (activeTab === TAB_PRODUCTS) {
      fetchProducts();
    }
  }, [activeTab]);

  const fetchBathTypes = async () => {
    try {
      setLoading(true);
      const data = await getBathTypes();
      setBathTypes(data);
    } catch (err) {
      // eslint-disable-next-line no-console
      console.error('Error obteniendo tipos de baño', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchProducts = async () => {
    try {
      const data = await getProducts();
      setProducts(data);
    } catch (err) {
      // eslint-disable-next-line no-console
      console.error('Error obteniendo productos', err);
    }
  };

  const handlePriceChange = (id: number, value: string) => {
    setEditedPrices((prev) => ({ ...prev, [id]: value }));
  };

  const handleSavePrice = async (id: number) => {
    const priceStr = editedPrices[id];
    if (!priceStr) return;
    try {
      await updateBathTypePrice(id, priceStr);
      await fetchBathTypes();
    } catch (err) {
      // eslint-disable-next-line no-console
      console.error('Error actualizando precio', err);
    }
  };

  // --------------------------------------------------------------
  // Gestión de filas de baños en el producto
  // --------------------------------------------------------------
  const addBathRow = () => {
    if (!newBathTypeId) return;
    setProdBaths((prev) => [...prev, { bath_type_id: newBathTypeId, quantity: newBathQty }]);
    setNewBathQty(1);
  };

  const removeBathRow = (index: number) => {
    setProdBaths((prev) => prev.filter((_, i) => i !== index));
  };

  const updateBathRow = (index: number, field: 'bath_type_id' | 'quantity', value: any) => {
    setProdBaths((prev) => prev.map((row, i) => (i === index ? { ...row, [field]: value } : row)));
  };

  const handleCreateProduct = async () => {
    try {
      // Determinar uses_massagist
      const usesMass = prodBaths.some((b) => {
        const bt = bathTypes.find((t) => t.id === b.bath_type_id);
        return bt && bt.massage_type !== 'none';
      });

      await createProduct({
        name: prodName,
        observation: prodObs,
        description: prodDesc,
        price: prodPrice,
        uses_capacity: true,
        uses_massagist: usesMass,
        visible: prodVisible,
        baths: prodBaths,
        hostings: [],
      } as any);

      // Reset
      setOpenCreateDlg(false);
      setProdName('');
      setProdObs('');
      setProdDesc('');
      setProdPrice('');
      setProdBaths([]);

      // recargar lista
      await fetchProducts();
    } catch (err) {
      // eslint-disable-next-line no-console
      console.error('Error creando producto', err);
    }
  };

  // Guardar cambios de producto existente
  const handleSaveEditProduct = async () => {
    if (!editProduct) return;

    try {
      const usesMass = editProduct.baths.some((b) => {
        const bt = bathTypes.find((t) => t.id === b.bath_type_id);
        return bt && bt.massage_type !== 'none';
      });

      await updateProduct(editProduct.id, {
        name: editProduct.name,
        observation: editProduct.observation,
        description: editProduct.description,
        price: editProduct.price,
        uses_capacity: true,
        uses_massagist: usesMass,
        visible: editProduct.visible,
        baths: editProduct.baths,
        hostings: [],
      } as any);

      setEditProduct(null);
      await fetchProducts();
    } catch (err) {
      // eslint-disable-next-line no-console
      console.error('Error actualizando producto', err);
    }
  };

  return (
    <div className="productos-page">
      {/* Tabs */}
      <div className="tabs">
        <button
          className={activeTab === TAB_BATHS ? 'active' : ''}
          onClick={() => setActiveTab(TAB_BATHS)}
        >
          Precio de los Baños
        </button>
        <button
          className={activeTab === TAB_PRODUCTS ? 'active' : ''}
          onClick={() => setActiveTab(TAB_PRODUCTS)}
        >
          Gestión de Productos
        </button>
      </div>

      {/* Content */}
      <div className="tab-content">
        {activeTab === TAB_BATHS && (
          <div className="card">
            {loading ? (
              <p>Cargando…</p>
            ) : (
              <table className="baths-table">
                <thead>
                  <tr>
                    <th>Nombre</th>
                    <th>Tipo masaje</th>
                    <th>Duración masaje</th>
                    <th>Precio (€)</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {bathTypes.map((bt) => (
                    <tr key={bt.id}>
                      <td>{bt.name}</td>
                      <td>{
                        (() => {
                          switch (bt.massage_type) {
                            case 'relax':
                              return 'Relajante';
                            case 'rock':
                              return 'Piedras';
                            case 'exfoliation':
                              return 'Exfoliación';
                            default:
                              return 'Sin masaje';
                          }
                        })()
                      }</td>
                      <td>{bt.massage_duration === '0' ? '—' : `${bt.massage_duration}'`}</td>
                      <td style={{ textAlign: 'center' }}>
                        <input
                          type="number"
                          min={0}
                          step={0.01}
                          defaultValue={bt.price}
                          onChange={(e) => handlePriceChange(bt.id, e.target.value)}
                          style={{ width: '80px' }}
                        />
                      </td>
                      <td>
                        <ReactiveButton
                          buttonState="idle"
                          idleText="Guardar"
                          size="small"
                          style={{ backgroundColor: 'var(--color-primary)' }}
                          onClick={() => handleSavePrice(bt.id)}
                        />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        )}

        {activeTab === TAB_PRODUCTS && (
          <div className="card" style={{ padding: '1rem' }}>
            <ReactiveButton
              idleText="Crear producto"
              style={{ backgroundColor: 'var(--color-primary)' }}
              onClick={() => setOpenCreateDlg(true)}
            />
            {/* Aquí podría ir una tabla de productos existentes… */}
            <table className="baths-table" style={{ marginTop: '1rem' }}>
              <thead>
                <tr>
                  <th>Nombre</th>
                  <th>Precio (€)</th>
                  <th>Visible</th>
                  <th>Masajista</th>
                </tr>
              </thead>
              <tbody>
                {products.map((p) => (
                  <tr key={p.id} onClick={() => setEditProduct(p)} style={{ cursor: 'pointer' }}>
                    <td style={{ textDecoration: 'underline' }}>{p.name}</td>
                    <td style={{ textAlign: 'right' }}>{p.price}</td>
                    <td style={{ textAlign: 'center' }}>{p.visible ? '✓' : '—'}</td>
                    <td style={{ textAlign: 'center' }}>{p.uses_massagist ? '✓' : '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>

            <DefaultDialog
              open={openCreateDlg}
              title="Nuevo producto"
              onClose={() => setOpenCreateDlg(false)}
              onSave={handleCreateProduct}
              saveLabel="Crear"
            >
              <label className="dialog-label">Nombre</label>
              <input className="full-width" value={prodName} onChange={(e) => setProdName(e.target.value)} />

              <label className="dialog-label">Observación interna</label>
              <input className="full-width" value={prodObs} onChange={(e) => setProdObs(e.target.value)} />

              <label className="dialog-label">Descripción</label>
              <textarea className="full-width" rows={3} value={prodDesc} onChange={(e) => setProdDesc(e.target.value)} />

              <label className="dialog-label">Precio (€)</label>
              <input type="number" min={0} step={0.01} value={prodPrice} onChange={(e) => setProdPrice(e.target.value)} />

              <label style={{ display: 'block', marginTop: '0.5rem' }}>
                <input type="checkbox" checked={prodVisible} onChange={(e) => setProdVisible(e.target.checked)} /> Visible en web
              </label>

              <h4>Baños incluidos</h4>

              {/* Formulario rápido para añadir */}
              <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', marginBottom: '1.5rem' }}>
                <select style={{ marginTop: 0 }} value={newBathTypeId ?? bathTypes[0]?.id ?? 0} onChange={(e) => setNewBathTypeId(Number(e.target.value))}>
                  {bathTypes.map((bt) => (
                    <option key={bt.id} value={bt.id}>{bt.name}</option>
                  ))}
                </select>
                <input type="number" min={1} value={newBathQty} onChange={(e)=>setNewBathQty(Number(e.target.value))} style={{ width: '70px' }} />
                <ReactiveButton
                  idleText="Añadir"
                  style={{ backgroundColor: 'var(--color-tertiary, #666)' }}
                  onClick={() => {
                    addBathRow();
                  }}
                />
              </div>

              {/* Tabla de baños añadidos */}
              {prodBaths.length > 0 && (
                <table style={{ width: '100%' }}>
                  <thead>
                    <tr>
                      <th>Tipo de baño</th>
                      <th>Cantidad</th>
                      <th></th>
                    </tr>
                  </thead>
                  <tbody>
                    {prodBaths.map((row, idx) => {
                      const bt = bathTypes.find(b=>b.id===row.bath_type_id);
                      return (
                        <tr key={idx}>
                          <td>{bt ? bt.name : `ID ${row.bath_type_id}`}</td>
                          <td style={{ textAlign:'center' }}>{row.quantity}</td>
                          <td>
                            <ReactiveButton idleText="Eliminar" style={{ backgroundColor: 'var(--color-secondary)' }} size="small" onClick={()=>removeBathRow(idx)} />
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              )}
            </DefaultDialog>

            {/* Dialogo edicion */}
            {editProduct && (
              <DefaultDialog
                open={true}
                title={`Editar: ${editProduct.name}`}
                onClose={() => setEditProduct(null)}
                onSave={handleSaveEditProduct}
                saveLabel="Guardar"
              >
                <label className="dialog-label">Nombre</label>
                <input className="full-width" value={editProduct.name} onChange={(e)=>setEditProduct({...editProduct, name:e.target.value})} />

                <label className="dialog-label">Observación interna</label>
                <input className="full-width" value={editProduct.observation||''} onChange={(e)=>setEditProduct({...editProduct, observation:e.target.value})} />

                <label className="dialog-label">Descripción</label>
                <textarea className="full-width" rows={3} value={editProduct.description||''} onChange={(e)=>setEditProduct({...editProduct, description:e.target.value})} />

                <label className="dialog-label">Precio (€)</label>
                <input type="number" min={0} step={0.01} value={editProduct.price} onChange={(e)=>setEditProduct({...editProduct, price:e.target.value})} />

                <label style={{ display: 'block', marginTop: '0.5rem' }}>
                  <input type="checkbox" checked={editProduct.visible} onChange={(e)=>setEditProduct({...editProduct, visible:e.target.checked})}/> Visible en web
                </label>

                <h4>Baños incluidos</h4>
                {editProduct.baths.length===0 && <p>No hay baños.</p>}
                {editProduct.baths.length>0 && (
                  <table style={{ width:'100%' }}>
                    <thead><tr><th>Tipo</th><th>Cantidad</th></tr></thead>
                    <tbody>
                      {editProduct.baths.map((b,idx)=>{
                        const bt = bathTypes.find(t=>t.id===b.bath_type_id);
                        return (
                          <tr key={idx}><td>{bt?bt.name:b.bath_type_id}</td><td>{b.quantity}</td></tr>
                        );
                      })}
                    </tbody>
                  </table>
                )}
              </DefaultDialog>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default ProductosPage; 