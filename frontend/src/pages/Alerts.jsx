import { useState, useEffect } from 'react'
import api from '../utils/api'
import {
    AlertTriangle,
    PackageX,
    UserX,
    Bell,
    CheckCircle
} from 'lucide-react'

function Alerts() {
    const [lowStock, setLowStock] = useState([])
    const [outstanding, setOutstanding] = useState([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        fetchAlerts()
    }, [])

    const fetchAlerts = async () => {
        setLoading(true)
        try {
            const [stockRes, outstandingRes] = await Promise.all([
                api.get('/api/products/alerts/low-stock'),
                api.get('/api/customers/outstanding?min_days=1')
            ])

            setLowStock(stockRes.data)
            setOutstanding(outstandingRes.data)
        } catch (err) {
            console.error('Alerts fetch error:', err)
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
            <div className="loading-container">
                <div className="loading-spinner"></div>
            </div>
        )
    }

    // Combined Alert Count
    const totalAlerts = lowStock.length + outstanding.length;

    return (
        <>
            <header className="page-header">
                <div>
                    <h1 className="page-title">Alerts & Actions</h1>
                    <p className="page-subtitle">
                        {totalAlerts > 0
                            ? `${totalAlerts} items require your attention`
                            : 'All systems operational'}
                    </p>
                </div>
            </header>

            <div className="page-content">
                {totalAlerts === 0 && (
                    <div className="empty-state">
                        <CheckCircle size={48} className="text-success" />
                        <h3>You're all caught up!</h3>
                        <p>No inventory issues or overdue payments found.</p>
                    </div>
                )}

                {/* Low Stock Alerts */}
                {lowStock.length > 0 && (
                    <div className="card mb-large border-danger">
                        <div className="card-header bg-danger-light text-danger">
                            <h3 className="card-title flex items-center gap-2">
                                <PackageX size={20} />
                                Low Stock Inventory
                            </h3>
                            <span className="badge badge-danger">{lowStock.length} Items</span>
                        </div>
                        <div className="table-container">
                            <table className="table">
                                <thead>
                                    <tr>
                                        <th>Product Name</th>
                                        <th className="text-right">Current Stock</th>
                                        <th className="text-right">Reorder Level</th>
                                        <th className="text-right">Deficit</th>
                                        <th className="text-right">Action</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {lowStock.map((item) => (
                                        <tr key={item.product_id}>
                                            <td className="font-medium text-danger">{item.product_name}</td>
                                            <td className="text-right">{item.current_stock}</td>
                                            <td className="text-right text-muted">{item.reorder_level}</td>
                                            <td className="text-right font-bold text-danger">-{item.deficit}</td>
                                            <td className="text-right">
                                                <a href="/products" className="btn btn-sm btn-secondary">Restock</a>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                )}

                {/* Overdue Payments */}
                {outstanding.length > 0 && (
                    <div className="card border-warning">
                        <div className="card-header bg-warning-light text-warning-dark">
                            <h3 className="card-title flex items-center gap-2">
                                <UserX size={20} />
                                Outstanding Payments
                            </h3>
                            <span className="badge badge-warning">{outstanding.length} Customers</span>
                        </div>
                        <div className="table-container">
                            <table className="table">
                                <thead>
                                    <tr>
                                        <th>Customer</th>
                                        <th>Phone</th>
                                        <th>Risk Tag</th>
                                        <th className="text-right">Days Overdue</th>
                                        <th className="text-right">Amount Due</th>
                                        <th className="text-right">Action</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {outstanding.map((cust) => (
                                        <tr key={cust.customer_id}>
                                            <td>
                                                <div className="font-medium">{cust.customer_name}</div>
                                            </td>
                                            <td>{cust.phone}</td>
                                            <td>
                                                <span className={`badge ${cust.risk_tag === 'HIGH_RISK' ? 'badge-danger' :
                                                        cust.risk_tag === 'LOW_RISK' ? 'badge-success' : 'badge-warning'
                                                    }`}>
                                                    {cust.risk_tag.replace('_', ' ')}
                                                </span>
                                            </td>
                                            <td className="text-right">{cust.days_overdue} days</td>
                                            <td className="text-right font-bold">{formatCurrency(cust.due_amount)}</td>
                                            <td className="text-right">
                                                <a href="/billing" className="btn btn-sm btn-primary">Collect</a>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                )}
            </div>
        </>
    )
}

export default Alerts
