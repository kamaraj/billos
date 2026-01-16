import { useState, useEffect } from 'react'
import api from '../utils/api'
import { Search, FileText, DollarSign, Clock, CheckCircle, Eye } from 'lucide-react'
import InvoiceModal from '../components/InvoiceModal'

function Invoices() {
    const [invoices, setInvoices] = useState([])
    const [summary, setSummary] = useState(null)
    const [loading, setLoading] = useState(true)
    const [search, setSearch] = useState('')
    const [statusFilter, setStatusFilter] = useState('')
    const [selectedInvoice, setSelectedInvoice] = useState(null)

    useEffect(() => {
        fetchData()
    }, [statusFilter])

    const handleViewInvoice = async (id) => {
        try {
            const res = await api.get(`/api/invoices/${id}`)
            setSelectedInvoice(res.data)
        } catch (err) {
            console.error('Error fetching invoice details:', err)
        }
    }

    const fetchData = async () => {
        try {
            const params = {}
            if (statusFilter) params.payment_status = statusFilter

            const [invoicesRes, summaryRes] = await Promise.all([
                api.get('/api/invoices', { params }),
                api.get('/api/invoices/summary')
            ])

            setInvoices(invoicesRes.data.items || [])
            setSummary(summaryRes.data)
        } catch (err) {
            console.error('Fetch error:', err)
        } finally {
            setLoading(false)
        }
    }

    const formatCurrency = (amount) => {
        return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR',
            maximumFractionDigits: 0
        }).format(amount)
    }

    const formatDate = (dateStr) => {
        return new Date(dateStr).toLocaleDateString('en-IN', {
            day: '2-digit',
            month: 'short',
            year: 'numeric'
        })
    }

    const filteredInvoices = invoices.filter(inv =>
        inv.invoice_no.toLowerCase().includes(search.toLowerCase()) ||
        (inv.customer_name || '').toLowerCase().includes(search.toLowerCase())
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
                <h1 className="page-title">Invoices</h1>
                <p className="page-subtitle">View and manage all invoices</p>
            </header>

            <div className="page-content">
                {/* Summary Stats */}
                <div className="stats-grid" style={{ marginBottom: 'var(--space-xl)' }}>
                    <div className="stat-card">
                        <div className="stat-icon primary">
                            <DollarSign size={24} />
                        </div>
                        <div className="card-title">Today's Sales</div>
                        <div className="card-value">{formatCurrency(summary?.total_sales || 0)}</div>
                        <div style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)', marginTop: 'var(--space-sm)' }}>
                            {summary?.total_invoices || 0} invoices
                        </div>
                    </div>

                    <div className="stat-card">
                        <div className="stat-icon success">
                            <CheckCircle size={24} />
                        </div>
                        <div className="card-title">Cash Collected</div>
                        <div className="card-value">{formatCurrency(summary?.cash_collected || 0)}</div>
                    </div>

                    <div className="stat-card">
                        <div className="stat-icon warning">
                            <Clock size={24} />
                        </div>
                        <div className="card-title">Outstanding</div>
                        <div className="card-value">{formatCurrency(summary?.outstanding || 0)}</div>
                    </div>

                    <div className="stat-card">
                        <div className="stat-icon info">
                            <FileText size={24} />
                        </div>
                        <div className="card-title">GST Collected</div>
                        <div className="card-value">{formatCurrency(summary?.total_tax || 0)}</div>
                    </div>
                </div>

                {/* Filters */}
                <div style={{ display: 'flex', gap: 'var(--space-md)', marginBottom: 'var(--space-xl)' }}>
                    <div className="search-container" style={{ flex: 1, maxWidth: 400 }}>
                        <Search size={20} className="search-icon" />
                        <input
                            type="text"
                            className="form-input search-input"
                            placeholder="Search by invoice no or customer..."
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                        />
                    </div>

                    <select
                        className="form-input form-select"
                        style={{ width: 180 }}
                        value={statusFilter}
                        onChange={(e) => setStatusFilter(e.target.value)}
                    >
                        <option value="">All Status</option>
                        <option value="PAID">Paid</option>
                        <option value="PARTIAL">Partial</option>
                        <option value="UNPAID">Unpaid</option>
                    </select>
                </div>

                {/* Invoices table */}
                <div className="table-container">
                    <table className="table">
                        <thead>
                            <tr>
                                <th>Invoice</th>
                                <th>Date</th>
                                <th>Customer</th>
                                <th>Amount</th>
                                <th>Paid</th>
                                <th>Balance</th>
                                <th>Status</th>
                                <th style={{ width: 80 }}>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filteredInvoices.map(invoice => (
                                <tr key={invoice.id}>
                                    <td>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-md)' }}>
                                            <div style={{
                                                width: 40,
                                                height: 40,
                                                borderRadius: 'var(--radius-md)',
                                                background: invoice.is_gst_invoice ? 'rgba(99, 102, 241, 0.2)' : 'var(--color-bg)',
                                                display: 'flex',
                                                alignItems: 'center',
                                                justifyContent: 'center'
                                            }}>
                                                <FileText size={20} style={{ color: 'var(--color-primary-light)' }} />
                                            </div>
                                            <div>
                                                <div style={{ fontWeight: 600 }}>{invoice.invoice_no}</div>
                                                {invoice.is_gst_invoice && (
                                                    <span className="badge badge-info" style={{ marginTop: 2 }}>GST</span>
                                                )}
                                            </div>
                                        </div>
                                    </td>
                                    <td>{formatDate(invoice.date || invoice.invoice_date)}</td>
                                    <td>{invoice.customer || invoice.customer_name || 'Walk-in'}</td>
                                    <td style={{ fontWeight: 600 }}>{formatCurrency(invoice.total || invoice.total_amount)}</td>
                                    <td style={{ color: 'var(--color-success)' }}>
                                        {formatCurrency(invoice.paid_amount || (invoice.status === 'PAID' ? (invoice.total || invoice.total_amount) : 0))}
                                    </td>
                                    <td style={{
                                        color: (invoice.balance_amount || 0) > 0 ? 'var(--color-warning)' : 'var(--color-text-muted)'
                                    }}>
                                        {formatCurrency(invoice.balance_amount || (invoice.status === 'PENDING' ? (invoice.total || invoice.total_amount) : 0))}
                                    </td>
                                    <td>
                                        {(invoice.status === 'PAID' || invoice.payment_status === 'PAID') && (
                                            <span className="badge badge-success">Paid</span>
                                        )}
                                        {(invoice.status === 'PARTIAL' || invoice.payment_status === 'PARTIAL') && (
                                            <span className="badge badge-warning">Partial</span>
                                        )}
                                        {(invoice.status === 'PENDING' || invoice.payment_status === 'UNPAID') && (
                                            <span className="badge badge-danger">Unpaid</span>
                                        )}
                                    </td>
                                    <td>
                                        <button
                                            className="btn btn-secondary btn-icon"
                                            onClick={() => handleViewInvoice(invoice.id)}
                                            style={{ width: 32, height: 32 }}
                                        >
                                            <Eye size={16} />
                                        </button>
                                    </td>
                                </tr>
                            ))}

                            {filteredInvoices.length === 0 && (
                                <tr>
                                    <td colSpan={8}>
                                        <div className="empty-state">
                                            <p>No invoices found</p>
                                        </div>
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

            {selectedInvoice && (
                <InvoiceModal
                    invoice={selectedInvoice}
                    onClose={() => setSelectedInvoice(null)}
                />
            )}
        </>
    )
}

export default Invoices
