import { useState, useEffect } from 'react'
import api from '../utils/api'
import {
    TrendingUp,
    DollarSign,
    ShoppingBag,
    Users,
    CreditCard,
    Calendar
} from 'lucide-react'

function Reports() {
    const [cashSummary, setCashSummary] = useState(null)
    const [topProducts, setTopProducts] = useState([])
    const [topCustomers, setTopCustomers] = useState([])
    const [loading, setLoading] = useState(true)
    const [limit, setLimit] = useState(10)
    const [dateRange, setDateRange] = useState(30) // days

    useEffect(() => {
        fetchReports()
    }, [limit, dateRange])

    const fetchReports = async () => {
        setLoading(true)
        try {
            const [cashRes, productsRes, customersRes] = await Promise.all([
                api.get('/api/dashboard/cash-summary'),
                api.get(`/api/dashboard/top-products?days=${dateRange}&limit=${limit}`),
                api.get(`/api/dashboard/top-customers?days=${dateRange}&limit=${limit}`)
            ])

            setCashSummary(cashRes.data)
            setTopProducts(productsRes.data)
            setTopCustomers(customersRes.data)
        } catch (err) {
            console.error('Reports fetch error:', err)
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

    if (loading && !cashSummary) {
        return (
            <div className="loading-container">
                <div className="loading-spinner"></div>
            </div>
        )
    }

    return (
        <>
            <header className="page-header">
                <div>
                    <h1 className="page-title">Business Reports</h1>
                    <p className="page-subtitle">Performance insights and analytics</p>
                </div>
                <div className="header-actions">
                    <select
                        value={dateRange}
                        onChange={(e) => setDateRange(Number(e.target.value))}
                        className="form-select"
                        style={{ width: 'auto' }}
                    >
                        <option value="7">Last 7 Days</option>
                        <option value="30">Last 30 Days</option>
                        <option value="90">Last 3 Months</option>
                    </select>
                </div>
            </header>

            <div className="page-content">
                {/* Cash Flow Summary */}
                <section className="mb-large">
                    <h2 className="section-title mb-medium">Today's Cash Flow</h2>
                    <div className="stats-grid">
                        <div className="stat-card">
                            <div className="stat-icon success">
                                <DollarSign size={24} />
                            </div>
                            <div className="card-title">Total Collected</div>
                            <div className="card-value">{formatCurrency(cashSummary?.total_collected || 0)}</div>
                            <div className="card-subtitle">Across all payment modes</div>
                        </div>

                        {cashSummary?.by_payment_mode && Object.entries(cashSummary.by_payment_mode).map(([mode, amount]) => (
                            amount > 0 && (
                                <div key={mode} className="stat-card">
                                    <div className="stat-icon primary">
                                        <CreditCard size={24} />
                                    </div>
                                    <div className="card-title">{mode.toUpperCase()}</div>
                                    <div className="card-value">{formatCurrency(amount)}</div>
                                </div>
                            )
                        ))}
                    </div>
                </section>

                <div className="grid-2-col">
                    {/* Top Selling Products */}
                    <div className="card">
                        <div className="card-header">
                            <h3 className="card-title">Top Selling Products</h3>
                            <ShoppingBag className="text-muted" size={20} />
                        </div>
                        <div className="table-container">
                            <table className="table">
                                <thead>
                                    <tr>
                                        <th>Product</th>
                                        <th className="text-right">Sold</th>
                                        <th className="text-right">Revenue</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {topProducts.length === 0 ? (
                                        <tr>
                                            <td colSpan="3" className="text-center py-large text-muted">No data available</td>
                                        </tr>
                                    ) : (
                                        topProducts.map((p, i) => (
                                            <tr key={i}>
                                                <td>
                                                    <div className="font-medium">{p.product_name}</div>
                                                </td>
                                                <td className="text-right">{p.qty_sold}</td>
                                                <td className="text-right font-medium">{formatCurrency(p.revenue)}</td>
                                            </tr>
                                        ))
                                    )}
                                </tbody>
                            </table>
                        </div>
                    </div>

                    {/* Top Customers */}
                    <div className="card">
                        <div className="card-header">
                            <h3 className="card-title">Top Customers</h3>
                            <Users className="text-muted" size={20} />
                        </div>
                        <div className="table-container">
                            <table className="table">
                                <thead>
                                    <tr>
                                        <th>Customer</th>
                                        <th className="text-right">Invoices</th>
                                        <th className="text-right">Total Spent</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {topCustomers.length === 0 ? (
                                        <tr>
                                            <td colSpan="3" className="text-center py-large text-muted">No data available</td>
                                        </tr>
                                    ) : (
                                        topCustomers.map((c, i) => (
                                            <tr key={i}>
                                                <td>
                                                    <div className="font-medium">{c.customer_name}</div>
                                                </td>
                                                <td className="text-right">{c.invoice_count}</td>
                                                <td className="text-right font-medium">{formatCurrency(c.total_purchases)}</td>
                                            </tr>
                                        ))
                                    )}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </>
    )
}

export default Reports
