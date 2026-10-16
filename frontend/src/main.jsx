import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './styles.css';

const API = '/api';

const STATUS_FILTERS = ['ALL', 'IN_STOCK', 'LOW_STOCK', 'OUT_OF_STOCK'];

const statusLabel = (status) =>
  ({ IN_STOCK: 'In stock', LOW_STOCK: 'Low stock', OUT_OF_STOCK: 'Out of stock' }[status] || status);

const money = (value) =>
  new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value || 0);

function App() {
  const [products, setProducts] = useState([]);
  const [stats, setStats] = useState({ total: 0, inStock: 0, lowStock: 0, outOfStock: 0, inventoryValue: 0 });
  const [filter, setFilter] = useState('ALL');
  const [showForm, setShowForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const load = async () => {
    try {
      setError('');
      const [productsRes, statsRes] = await Promise.all([
        fetch(`${API}/products`),
        fetch(`${API}/products/stats`)
      ]);
      if (!productsRes.ok || !statsRes.ok) throw new Error('Backend unavailable');
      setProducts(await productsRes.json());
      setStats(await statsRes.json());
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const visible = filter === 'ALL' ? products : products.filter((p) => p.status === filter);

  const createProduct = async (event) => {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    await fetch(`${API}/products`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: form.get('name'),
        sku: form.get('sku'),
        category: form.get('category'),
        quantity: Number(form.get('quantity')),
        reorder_level: Number(form.get('reorder_level')),
        price: Number(form.get('price')),
        supplier: form.get('supplier')
      })
    });
    event.currentTarget.reset();
    setShowForm(false);
    load();
  };

  const restock = async (product) => {
    await fetch(`${API}/products/${product.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ quantity: product.quantity + 10 })
    });
    load();
  };

  const remove = async (product) => {
    await fetch(`${API}/products/${product.id}`, { method: 'DELETE' });
    load();
  };

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-mark">S</span>
          <div>
            <b>StockPilot</b>
            <small>Inventory Control</small>
          </div>
        </div>
        <nav>
          <a className="active">▦ <span>Dashboard</span></a>
          <a>◫ <span>Products</span></a>
          <a>⤓ <span>Suppliers</span></a>
          <a>◌ <span>Activity</span></a>
        </nav>
        <div className="side-bottom">
          <div className="upgrade">
            <strong>Keep shelves stocked.</strong>
            <p>Track every SKU from warehouse to checkout.</p>
          </div>
          <div className="profile">
            <div className="avatar">OP</div>
            <div>
              <b>Ops Team</b>
              <small>Warehouse</small>
            </div>
            <span>⋮</span>
          </div>
        </div>
      </aside>

      <main className="main">
        <header>
          <div>
            <p className="eyebrow">WORKSPACE / INVENTORY</p>
            <h1>Inventory overview</h1>
            <p className="muted">Live stock levels across your catalog.</p>
          </div>
          <button className="primary" onClick={() => setShowForm(true)}>＋ New product</button>
        </header>

        {error && (
          <div className="alert">⚠ {error}. Start the backend and PostgreSQL, then refresh.</div>
        )}

        <section className="stats">
          <Stat label="Total SKUs" value={stats.total} icon="▦" />
          <Stat label="In stock" value={stats.inStock} icon="✓" />
          <Stat label="Low stock" value={stats.lowStock} icon="◔" />
          <Stat label="Inventory value" value={money(stats.inventoryValue)} icon="$" />
        </section>

        <section className="panel">
          <div className="panel-head">
            <div>
              <h2>Products</h2>
              <p className="muted">Current quantities and reorder thresholds.</p>
            </div>
            <div className="filters">
              {STATUS_FILTERS.map((value) => (
                <button
                  key={value}
                  className={filter === value ? 'selected' : ''}
                  onClick={() => setFilter(value)}
                >
                  {value === 'ALL' ? 'All' : statusLabel(value)}
                </button>
              ))}
            </div>
          </div>

          {loading ? (
            <div className="empty">Loading products…</div>
          ) : visible.length === 0 ? (
            <div className="empty">No products yet. Add your first SKU.</div>
          ) : (
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Product</th>
                    <th>Supplier</th>
                    <th>Qty</th>
                    <th>Price</th>
                    <th>Status</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {visible.map((product) => (
                    <tr key={product.id}>
                      <td>
                        <div className="task-title">
                          <span className={`dot ${product.status.toLowerCase()}`}></span>
                          <div>
                            <b>{product.name}</b>
                            <small>
                              {product.sku} · {product.category}
                            </small>
                          </div>
                        </div>
                      </td>
                      <td>{product.supplier}</td>
                      <td>
                        {product.quantity}
                        <small className="muted"> / reorder {product.reorder_level}</small>
                      </td>
                      <td>{money(product.price)}</td>
                      <td>
                        <span className={`badge ${product.status.toLowerCase()}`}>
                          {statusLabel(product.status)}
                        </span>
                      </td>
                      <td className="actions">
                        <button onClick={() => restock(product)}>+10</button>
                        <button className="danger" onClick={() => remove(product)}>Delete</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </main>

      {showForm && (
        <div className="modal-backdrop" onClick={() => setShowForm(false)}>
          <form className="modal" onClick={(event) => event.stopPropagation()} onSubmit={createProduct}>
            <h2>New product</h2>
            <label>Name<input name="name" required maxLength={200} /></label>
            <label>SKU<input name="sku" required maxLength={60} /></label>
            <label>Category<input name="category" defaultValue="General" /></label>
            <div className="row">
              <label>Quantity<input name="quantity" type="number" min="0" defaultValue="0" /></label>
              <label>Reorder level<input name="reorder_level" type="number" min="0" defaultValue="10" /></label>
            </div>
            <div className="row">
              <label>Price<input name="price" type="number" min="0" step="0.01" defaultValue="0" /></label>
              <label>Supplier<input name="supplier" defaultValue="Unassigned" /></label>
            </div>
            <div className="modal-actions">
              <button type="button" onClick={() => setShowForm(false)}>Cancel</button>
              <button className="primary" type="submit">Create product</button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}

function Stat({ label, value, icon }) {
  return (
    <div className="stat">
      <div className="stat-icon">{icon}</div>
      <div>
        <small>{label}</small>
        <strong>{value}</strong>
        <span>Updated just now</span>
      </div>
    </div>
  );
}

createRoot(document.getElementById('root')).render(<App />);
