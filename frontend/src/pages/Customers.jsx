import { useState, useEffect } from 'react'
import api from '../utils/api'
import { Plus, Search, Users, Phone, AlertTriangle, X } from 'lucide-react'

function Customers() {
    const [customers, setCustomers] = useState([])
    const [loading, setLoading] = useState(true)
    const [search, setSearch] = useState('')
    const [showModal, setShowModal] = useState(false)
    const [editCustomer, setEditCustomer] = useState(null)
    const [formData, setFormData] = useState({
        name: '',
        phone: '',
        email: '',
        address: '',
        credit_limit: '0'
    })

    useEffect(() => {
        fetchCustomers()
    }, [])

    const fetchCustomers = async () => {
        try {
            const res = await api.get('/api/customers/')
            setCustomers(res.data.items || [])
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
                credit_limit: parseFloat(formData.credit_limit) || 0
            }

            if (editCustomer) {
                await api.put(`/api/customers/${editCustomer.id}`, data)
            } else {
                await api.post('/api/customers/', data)
            }

            fetchCustomers()
            closeModal()
        } catch (err) {
            console.error('Save error:', err)
            alert(err.response?.data?.detail || 'Failed to save customer')
        }
    }

    const openModal = (customer = null) => {
        if (customer) {
            setEditCustomer(customer)
            setFormData({
                name: customer.name,
                phone: customer.phone || '',
                email: customer.email || '',
                address: customer.address || '',
                credit_limit: customer.credit_limit.toString()
            })
        } else {
            setEditCustomer(null)
            setFormData({
                name: '',
                phone: '',
                email: '',
                address: '',
                credit_limit: '0'
            })
        }
        setShowModal(true)
    }

    const closeModal = () => {
        setShowModal(false)
        setEditCustomer(null)
    }

    const formatCurrency = (amount) => {
        return new Intl.NumberFormat('en-QA', {
            style: 'currency',
            currency: 'QAR',
            maximumFractionDigits: 2
        }).format(amount)
    }

    const filteredCustomers = customers.filter(c =>
        c.name.toLowerCase().includes(search.toLowerCase()) ||
        (c.phone || '').includes(search)
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
                        <h1 className="page-title">Customers</h1>
                        <p className="page-subtitle">{customers.length} customers</p>
                    </div>
                    <button className="btn btn-primary" onClick={() => openModal()}>
                        <Plus size={20} />
                        Add Customer
                    </button>
                </div>
            </header>

            <div className="page-content">
                {/* Stats */}
                <div className="stats-grid" style={{ marginBottom: 'var(--space-xl)' }}>
                    <div className="stat-card">
                        <div className="stat-icon primary">
                            <Users size={24} />
                        </div>
                        <div className="card-title">Total Customers</div>
                        <div className="card-value">{customers.length}</div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-icon warning">
                            <AlertTriangle size={24} />
                        </div>
                        <div className="card-title">Total Outstanding</div>
                        <div className="card-value">
                            {formatCurrency(customers.reduce((sum, c) => sum + (c.balance || c.current_balance || 0), 0))}
                        </div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-icon danger">
                            <Users size={24} />
                        </div>
                        <div className="card-title">High Risk</div>
                        <div className="card-value">
                            {customers.filter(c => c.risk_tag !== 'NORMAL').length}
                        </div>
                    </div>
                </div>

                {/* Search */}
                <div className="search-container" style={{ marginBottom: 'var(--space-xl)', maxWidth: 400 }}>
                    <Search size={20} className="search-icon" />
                    <input
                        type="text"
                        className="form-input search-input"
                        placeholder="Search customers..."
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                    />
                </div>

                {/* Customers table */}
                <div className="table-container">
                    <table className="table">
                        <thead>
                            <tr>
                                <th>Customer</th>
                                <th>Phone</th>
                                <th>Outstanding</th>
                                <th>Credit Limit</th>
                                <th>Total Purchases</th>
                                <th>Risk</th>
                                <th></th>
                            </tr>
                        </thead>
                        <tbody>
                            {filteredCustomers.map(customer => (
                                <tr key={customer.id}>
                                    <td>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-md)' }}>
                                            <div style={{
                                                width: 40,
                                                height: 40,
                                                borderRadius: 'var(--radius-full)',
                                                background: 'var(--gradient-primary)',
                                                display: 'flex',
                                                alignItems: 'center',
                                                justifyContent: 'center',
                                                fontWeight: 700
                                            }}>
                                                {customer.name.charAt(0).toUpperCase()}
                                            </div>
                                            <div>
                                                <div style={{ fontWeight: 600 }}>{customer.name}</div>
                                                {customer.email && (
                                                    <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>
                                                        {customer.email}
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    </td>
                                    <td>
                                        {customer.phone && (
                                            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-xs)' }}>
                                                <Phone size={14} />
                                                {customer.phone}
                                            </div>
                                        )}
                                    </td>
                                    <td>
                                        <span style={{
                                            color: (customer.balance || 0) > 0 ? 'var(--color-warning)' : 'var(--color-success)',
                                            fontWeight: 600
                                        }}>
                                            {formatCurrency(customer.balance || 0)}
                                        </span>
                                    </td>
                                    <td>{formatCurrency(customer.credit_limit || 0)}</td>
                                    <td>{formatCurrency(customer.total_purchases || 0)}</td>
                                    <td>
                                        {customer.risk_tag === 'HIGH_RISK' ? (
                                            <span className="badge badge-danger">High Risk</span>
                                        ) : (customer.balance || 0) > 0 ? (
                                            <span className="badge badge-warning">Outstanding</span>
                                        ) : (
                                            <span className="badge badge-success">Good</span>
                                        )}
                                    </td>
                                    <td>
                                        <button
                                            className="btn btn-secondary"
                                            style={{ padding: 'var(--space-sm) var(--space-md)' }}
                                            onClick={() => openModal(customer)}
                                        >
                                            View
                                        </button>
                                    </td>
                                </tr>
                            ))}

                            {filteredCustomers.length === 0 && (
                                <tr>
                                    <td colSpan={7}>
                                        <div className="empty-state">
                                            <p>No customers found</p>
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
                            <h3 className="modal-title">{editCustomer ? 'Edit Customer' : 'Add Customer'}</h3>
                            <button className="modal-close" onClick={closeModal}>
                                <X size={24} />
                            </button>
                        </div>

                        <form onSubmit={handleSubmit}>
                            <div className="modal-body">
                                <div className="form-group">
                                    <label className="form-label">Customer Name *</label>
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
                                        <label className="form-label">Phone</label>
                                        <input
                                            type="tel"
                                            name="phone"
                                            className="form-input"
                                            value={formData.phone}
                                            onChange={handleChange}
                                        />
                                    </div>
                                    <div className="form-group">
                                        <label className="form-label">Email</label>
                                        <input
                                            type="email"
                                            name="email"
                                            className="form-input"
                                            value={formData.email}
                                            onChange={handleChange}
                                        />
                                    </div>
                                </div>

                                <div className="form-group">
                                    <label className="form-label">Address</label>
                                    <textarea
                                        name="address"
                                        className="form-input"
                                        rows={3}
                                        value={formData.address}
                                        onChange={handleChange}
                                    />
                                </div>

                                <div className="form-group">
                                    <label className="form-label">Credit Limit (QAR)</label>
                                    <input
                                        type="number"
                                        name="credit_limit"
                                        className="form-input"
                                        value={formData.credit_limit}
                                        onChange={handleChange}
                                    />
                                </div>

                                {editCustomer && (
                                    <div style={{
                                        padding: 'var(--space-md)',
                                        background: 'var(--color-bg)',
                                        borderRadius: 'var(--radius-md)',
                                        marginTop: 'var(--space-md)'
                                    }}>
                                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 'var(--space-sm)' }}>
                                            <span style={{ color: 'var(--color-text-secondary)' }}>Current Balance</span>
                                            <span style={{ fontWeight: 600 }}>{formatCurrency(editCustomer.current_balance)}</span>
                                        </div>
                                        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                            <span style={{ color: 'var(--color-text-secondary)' }}>Total Purchases</span>
                                            <span>{formatCurrency(editCustomer.total_purchases)}</span>
                                        </div>
                                    </div>
                                )}
                            </div>

                            <div className="modal-footer">
                                <button type="button" className="btn btn-secondary" onClick={closeModal}>
                                    Cancel
                                </button>
                                <button type="submit" className="btn btn-primary">
                                    {editCustomer ? 'Update' : 'Add Customer'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </>
    )
}

export default Customers
