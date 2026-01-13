import { useState, useEffect } from 'react'
import api from '../utils/api'
import {
    TrendingUp,
    TrendingDown,
    DollarSign,
    ShoppingBag,
    AlertTriangle,
    Users,
    Package,
    ArrowUpRight,
    ArrowDownRight
} from 'lucide-react'

function Dashboard() {
    const [summary, setSummary] = useState(null)
    const [trends, setTrends] = useState([])
    const [topProducts, setTopProducts] = useState([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        fetchDashboard()
    }, [])

    const fetchDashboard = async () => {
        try {
            const [summaryRes, trendsRes, productsRes] = await Promise.all([
                api.get('/api/dashboard/summary'),
                api.get('/api/dashboard/trends?days=7'),
                api.get('/api/dashboard/top-products?limit=5')
            ])

            setSummary(summaryRes.data)
            setTrends(trendsRes.data.trends)
            setTopProducts(productsRes.data)
        } catch (err) {
            console.error('Dashboard fetch error:', err)
        } finally {
            setLoading(false)
        }
    }

    const formatCurrency = (amount) => {
        return new Intl.NumberFormat('en-QA', {
            style: 'currency',
            currency: 'QAR',
            maximumFractionDigits: 2
        }).format(amount)
    }

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
                <h1 className="page-title">Dashboard</h1>
                <p className="page-subtitle">
                    {new Date().toLocaleDateString('en-QA', {
                        weekday: 'long',
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric'
                    })}
                </p>
            </header>

            <div className="page-content">
                {/* Stats Grid */}
                <div className="stats-grid">
                    {/* Today's Sales */}
                    <div className="stat-card">
                        <div className="stat-icon primary">
                            <DollarSign size={24} />
                        </div>
                        <div className="card-title">Today's Sales</div>
                        <div className="card-value">{formatCurrency(summary?.today?.sales || 0)}</div>
                        <div style={{ marginTop: 'var(--space-sm)', display: 'flex', alignItems: 'center', gap: 'var(--space-sm)' }}>
                            {summary?.comparison?.vs_yesterday_pct >= 100 ? (
                                <span className="card-change positive">
                                    <ArrowUpRight size={14} />
                                    {Math.round(summary?.comparison?.vs_yesterday_pct - 100)}% vs yesterday
                                </span>
                            ) : (
                                <span className="card-change negative">
                                    <ArrowDownRight size={14} />
                                    {Math.round(100 - (summary?.comparison?.vs_yesterday_pct || 0))}% vs yesterday
                                </span>
                            )}
                        </div>
                    </div>

                    {/* Cash Collected */}
                    <div className="stat-card">
                        <div className="stat-icon success">
                            <TrendingUp size={24} />
                        </div>
                        <div className="card-title">Cash Collected</div>
                        <div className="card-value">{formatCurrency(summary?.today?.cash_collected || 0)}</div>
                        <div style={{ marginTop: 'var(--space-sm)', color: 'var(--color-text-secondary)', fontSize: '0.875rem' }}>
                            {summary?.today?.invoice_count || 0} invoices today
                        </div>
                    </div>

                    {/* Outstanding */}
                    <div className="stat-card">
                        <div className="stat-icon warning">
                            <Users size={24} />
                        </div>
                        <div className="card-title">Total Outstanding</div>
                        <div className="card-value">{formatCurrency(summary?.alerts?.total_outstanding || 0)}</div>
                        <div style={{ marginTop: 'var(--space-sm)', color: 'var(--color-text-secondary)', fontSize: '0.875rem' }}>
                            {summary?.alerts?.overdue_customers || 0} overdue customers
                        </div>
                    </div>

                    {/* Low Stock */}
                    <div className="stat-card">
                        <div className="stat-icon danger">
                            <Package size={24} />
                        </div>
                        <div className="card-title">Low Stock Items</div>
                        <div className="card-value">{summary?.alerts?.low_stock_items || 0}</div>
                        <div style={{ marginTop: 'var(--space-sm)', color: 'var(--color-text-secondary)', fontSize: '0.875rem' }}>
                            Items need restocking
                        </div>
                    </div>
                </div>

                {/* Charts Section */}
                <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 'var(--space-xl)' }}>
                    {/* Sales Trend */}
                    <div className="card">
                        <div className="card-header">
                            <h3 className="card-title">7-Day Sales Trend</h3>
                        </div>
                        <div style={{ marginTop: 'var(--space-lg)' }}>
                            <div style={{ display: 'flex', alignItems: 'flex-end', gap: 'var(--space-md)', height: 200 }}>
                                {trends.map((day, i) => {
                                    const maxSales = Math.max(...trends.map(t => t.sales), 1)
                                    const height = (day.sales / maxSales) * 160

                                    return (
                                        <div key={i} style={{ flex: 1, textAlign: 'center' }}>
                                            <div
                                                style={{
                                                    height: `${height}px`,
                                                    background: i === trends.length - 1 ? 'var(--gradient-primary)' : 'var(--color-border)',
                                                    borderRadius: 'var(--radius-sm)',
                                                    marginBottom: 'var(--space-sm)',
                                                    transition: 'height 0.3s ease'
                                                }}
                                            />
                                            <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>{day.day}</div>
                                            <div style={{ fontSize: '0.625rem', color: 'var(--color-text-secondary)', marginTop: 2 }}>
                                                {formatCurrency(day.sales).replace('QAR', '').replace('QR', '').trim()}
                                            </div>
                                        </div>
                                    )
                                })}
                            </div>
                        </div>
                    </div>

                    {/* Top Products */}
                    <div className="card">
                        <div className="card-header">
                            <h3 className="card-title">Top Products</h3>
                        </div>
                        <div style={{ marginTop: 'var(--space-md)' }}>
                            {topProducts.length === 0 ? (
                                <div className="empty-state">
                                    <p>No sales data yet</p>
                                </div>
                            ) : (
                                topProducts.map((product, i) => (
                                    <div
                                        key={product.product_id}
                                        style={{
                                            display: 'flex',
                                            alignItems: 'center',
                                            justifyContent: 'space-between',
                                            padding: 'var(--space-md)',
                                            borderBottom: i < topProducts.length - 1 ? '1px solid var(--color-border)' : 'none'
                                        }}
                                    >
                                        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-md)' }}>
                                            <div style={{
                                                width: 32,
                                                height: 32,
                                                borderRadius: 'var(--radius-md)',
                                                background: 'var(--color-bg)',
                                                display: 'flex',
                                                alignItems: 'center',
                                                justifyContent: 'center',
                                                fontSize: '0.875rem',
                                                fontWeight: 600,
                                                color: 'var(--color-primary-light)'
                                            }}>
                                                {i + 1}
                                            </div>
                                            <div>
                                                <div style={{ fontWeight: 500, fontSize: '0.875rem' }}>{product.product_name}</div>
                                                <div style={{ color: 'var(--color-text-muted)', fontSize: '0.75rem' }}>
                                                    {product.qty_sold} units
                                                </div>
                                            </div>
                                        </div>
                                        <div style={{ fontWeight: 600, color: 'var(--color-success)' }}>
                                            {formatCurrency(product.revenue)}
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>
                    </div>
                </div>

                {/* Quick Actions */}
                <div style={{ marginTop: 'var(--space-xl)' }}>
                    <h3 style={{ marginBottom: 'var(--space-lg)' }}>Quick Actions</h3>
                    <div style={{ display: 'flex', gap: 'var(--space-md)' }}>
                        <a href="/billing" className="btn btn-primary btn-lg">
                            <ShoppingBag size={20} />
                            New Bill
                        </a>
                        <a href="/products" className="btn btn-secondary btn-lg">
                            <Package size={20} />
                            Add Product
                        </a>
                        <a href="/customers" className="btn btn-secondary btn-lg">
                            <Users size={20} />
                            Add Customer
                        </a>
                    </div>
                </div>
            </div>
        </>
    )
}

export default Dashboard
