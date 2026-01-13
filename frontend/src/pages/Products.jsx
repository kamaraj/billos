import { useState, useEffect } from 'react'
import api from '../utils/api'
import { Plus, Search, Edit2, Package, AlertTriangle, X } from 'lucide-react'

function Products() {
    const [products, setProducts] = useState([])
    const [loading, setLoading] = useState(true)
    const [search, setSearch] = useState('')
    const [showModal, setShowModal] = useState(false)
    const [editProduct, setEditProduct] = useState(null)
    const [formData, setFormData] = useState({
        name: '',
        sku: '',
        category: '',
        cost_price: '',
        selling_price: '',
        gst_rate: '18',
        reorder_level: '10',
        unit: 'PCS',
        initial_stock: '0'
    })

    useEffect(() => {
        fetchProducts()
    }, [])

    const fetchProducts = async () => {
        try {
            const res = await api.get('/api/products/')
            setProducts(res.data)
        } catch (err) {
            console.error('Fetch error:', err)
        } finally {
            setLoading(false)
        }
    }

    const handleChange = (e) => {
        const { name, value } = e.target
        setFormData(prev => ({ ...prev, [name]: value }))
    }

    const handleSubmit = async (e) => {
        e.preventDefault()

        try {
            const data = {
                ...formData,
                cost_price: parseFloat(formData.cost_price) || 0,
                selling_price: parseFloat(formData.selling_price),
                gst_rate: parseFloat(formData.gst_rate),
                reorder_level: parseFloat(formData.reorder_level),
                initial_stock: parseFloat(formData.initial_stock)
            }

            if (editProduct) {
                await api.put(`/api/products/${editProduct.id}`, data)
            } else {
                await api.post('/api/products/', data)
            }

            fetchProducts()
            closeModal()
        } catch (err) {
            console.error('Save error:', err)
            alert(err.response?.data?.detail || 'Failed to save product')
        }
    }

    const openModal = (product = null) => {
        if (product) {
            setEditProduct(product)
            setFormData({
                name: product.name,
                sku: product.sku || '',
                category: product.category || '',
                cost_price: product.cost_price.toString(),
                selling_price: product.selling_price.toString(),
                gst_rate: product.gst_rate.toString(),
                reorder_level: product.reorder_level.toString(),
                unit: product.unit,
                initial_stock: '0'
            })
        } else {
            setEditProduct(null)
            setFormData({
                name: '',
                sku: '',
                category: '',
                cost_price: '',
                selling_price: '',
                gst_rate: '18',
                reorder_level: '10',
                unit: 'PCS',
                initial_stock: '0'
            })
        }
        setShowModal(true)
    }

    const closeModal = () => {
        setShowModal(false)
        setEditProduct(null)
    }

    const formatCurrency = (amount) => {
        return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR',
            maximumFractionDigits: 0
        }).format(amount)
    }

    const filteredProducts = products.filter(p =>
        p.name.toLowerCase().includes(search.toLowerCase()) ||
        (p.sku || '').toLowerCase().includes(search.toLowerCase()) ||
        (p.category || '').toLowerCase().includes(search.toLowerCase())
    )

    if (loading) {
        return (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh' }}>
                <div className="loading-spinner"></div>
            </div>
        )
    }

    return (
        <>
            <header className="page-header">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                        <h1 className="page-title">Products</h1>
                        <p className="page-subtitle">{products.length} products in inventory</p>
                    </div>
                    <button className="btn btn-primary" onClick={() => openModal()}>
                        <Plus size={20} />
                        Add Product
                    </button>
                </div>
            </header>

            <div className="page-content">
                {/* Search */}
                <div className="search-container" style={{ marginBottom: 'var(--space-xl)', maxWidth: 400 }}>
                    <Search size={20} className="search-icon" />
                    <input
                        type="text"
                        className="form-input search-input"
                        placeholder="Search products..."
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                    />
                </div>

                {/* Products table */}
                <div className="table-container">
                    <table className="table">
                        <thead>
                            <tr>
                                <th>Product</th>
                                <th>SKU</th>
                                <th>Category</th>
                                <th>Price</th>
                                <th>Stock</th>
                                <th>GST</th>
                                <th>Status</th>
                                <th></th>
                            </tr>
                        </thead>
                        <tbody>
                            {filteredProducts.map(product => (
                                <tr key={product.id}>
                                    <td>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-md)' }}>
                                            <div style={{
                                                width: 40,
                                                height: 40,
                                                borderRadius: 'var(--radius-md)',
                                                background: 'var(--color-bg)',
                                                display: 'flex',
                                                alignItems: 'center',
                                                justifyContent: 'center'
                                            }}>
                                                <Package size={20} style={{ color: 'var(--color-primary-light)' }} />
                                            </div>
                                            <div>
                                                <div style={{ fontWeight: 600 }}>{product.name}</div>
                                                <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>
                                                    {product.unit}
                                                </div>
                                            </div>
                                        </div>
                                    </td>
                                    <td>{product.sku || '-'}</td>
                                    <td>{product.category || '-'}</td>
                                    <td>
                                        <div>{formatCurrency(product.selling_price)}</div>
                                        <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>
                                            Cost: {formatCurrency(product.cost_price)}
                                        </div>
                                    </td>
                                    <td>
                                        <span style={{
                                            color: product.current_stock <= product.reorder_level
                                                ? 'var(--color-danger)'
                                                : 'var(--color-text)'
                                        }}>
                                            {product.current_stock}
                                        </span>
                                    </td>
                                    <td>{product.gst_rate}%</td>
                                    <td>
                                        {product.current_stock <= product.reorder_level ? (
                                            <span className="badge badge-warning">
                                                <AlertTriangle size={12} style={{ marginRight: 4 }} />
                                                Low Stock
                                            </span>
                                        ) : (
                                            <span className="badge badge-success">In Stock</span>
                                        )}
                                    </td>
                                    <td>
                                        <button
                                            className="btn btn-icon btn-secondary"
                                            onClick={() => openModal(product)}
                                        >
                                            <Edit2 size={16} />
                                        </button>
                                    </td>
                                </tr>
                            ))}

                            {filteredProducts.length === 0 && (
                                <tr>
                                    <td colSpan={8}>
                                        <div className="empty-state">
                                            <p>No products found</p>
                                        </div>
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Modal */}
            {showModal && (
                <div className="modal-overlay" onClick={closeModal}>
                    <div className="modal" onClick={e => e.stopPropagation()}>
                        <div className="modal-header">
                            <h3 className="modal-title">{editProduct ? 'Edit Product' : 'Add Product'}</h3>
                            <button className="modal-close" onClick={closeModal}>
                                <X size={24} />
                            </button>
                        </div>

                        <form onSubmit={handleSubmit}>
                            <div className="modal-body">
                                <div className="form-group">
                                    <label className="form-label">Product Name *</label>
                                    <input
                                        type="text"
                                        name="name"
                                        className="form-input"
                                        value={formData.name}
                                        onChange={handleChange}
                                        required
                                    />
                                </div>

                                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-md)' }}>
                                    <div className="form-group">
                                        <label className="form-label">SKU</label>
                                        <input
                                            type="text"
                                            name="sku"
                                            className="form-input"
                                            value={formData.sku}
                                            onChange={handleChange}
                                        />
                                    </div>
                                    <div className="form-group">
                                        <label className="form-label">Category</label>
                                        <input
                                            type="text"
                                            name="category"
                                            className="form-input"
                                            value={formData.category}
                                            onChange={handleChange}
                                        />
                                    </div>
                                </div>

                                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-md)' }}>
                                    <div className="form-group">
                                        <label className="form-label">Cost Price</label>
                                        <input
                                            type="number"
                                            name="cost_price"
                                            className="form-input"
                                            value={formData.cost_price}
                                            onChange={handleChange}
                                            step="0.01"
                                        />
                                    </div>
                                    <div className="form-group">
                                        <label className="form-label">Selling Price *</label>
                                        <input
                                            type="number"
                                            name="selling_price"
                                            className="form-input"
                                            value={formData.selling_price}
                                            onChange={handleChange}
                                            step="0.01"
                                            required
                                        />
                                    </div>
                                </div>

                                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 'var(--space-md)' }}>
                                    <div className="form-group">
                                        <label className="form-label">GST Rate %</label>
                                        <select
                                            name="gst_rate"
                                            className="form-input form-select"
                                            value={formData.gst_rate}
                                            onChange={handleChange}
                                        >
                                            <option value="0">0%</option>
                                            <option value="5">5%</option>
                                            <option value="12">12%</option>
                                            <option value="18">18%</option>
                                            <option value="28">28%</option>
                                        </select>
                                    </div>
                                    <div className="form-group">
                                        <label className="form-label">Unit</label>
                                        <select
                                            name="unit"
                                            className="form-input form-select"
                                            value={formData.unit}
                                            onChange={handleChange}
                                        >
                                            <option value="PCS">Pieces</option>
                                            <option value="KG">Kilograms</option>
                                            <option value="LTR">Litres</option>
                                            <option value="MTR">Meters</option>
                                            <option value="BOX">Box</option>
                                        </select>
                                    </div>
                                    <div className="form-group">
                                        <label className="form-label">Reorder Level</label>
                                        <input
                                            type="number"
                                            name="reorder_level"
                                            className="form-input"
                                            value={formData.reorder_level}
                                            onChange={handleChange}
                                        />
                                    </div>
                                </div>

                                {!editProduct && (
                                    <div className="form-group">
                                        <label className="form-label">Initial Stock</label>
                                        <input
                                            type="number"
                                            name="initial_stock"
                                            className="form-input"
                                            value={formData.initial_stock}
                                            onChange={handleChange}
                                        />
                                    </div>
                                )}
                            </div>

                            <div className="modal-footer">
                                <button type="button" className="btn btn-secondary" onClick={closeModal}>
                                    Cancel
                                </button>
                                <button type="submit" className="btn btn-primary">
                                    {editProduct ? 'Update' : 'Add Product'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </>
    )
}

export default Products
