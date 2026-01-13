import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import {
    LayoutDashboard,
    Receipt,
    Package,
    Users,
    FileText,
    Settings,
    LogOut,
    TrendingUp,
    AlertTriangle
} from 'lucide-react'

function Layout({ children }) {
    const { user, logout } = useAuth()
    const navigate = useNavigate()

    const handleLogout = () => {
        logout()
        navigate('/login')
    }

    return (
        <div className="app-container">
            {/* Sidebar */}
            <aside className="sidebar">
                <div className="sidebar-header">
                    <div className="logo">
                        <div className="logo-icon">
                            <Receipt size={24} color="white" />
                        </div>
                        <span className="logo-text">BillOS</span>
                    </div>
                </div>

                <nav className="sidebar-nav">
                    <div className="nav-section">
                        <div className="nav-section-title">Main</div>
                        <NavLink to="/" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                            <LayoutDashboard size={20} />
                            Dashboard
                        </NavLink>
                        <NavLink to="/billing" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                            <Receipt size={20} />
                            Quick Billing
                        </NavLink>
                    </div>

                    <div className="nav-section">
                        <div className="nav-section-title">Manage</div>
                        <NavLink to="/products" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                            <Package size={20} />
                            Products
                        </NavLink>
                        <NavLink to="/customers" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                            <Users size={20} />
                            Customers
                        </NavLink>
                        <NavLink to="/invoices" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                            <FileText size={20} />
                            Invoices
                        </NavLink>
                    </div>

                    <div className="nav-section">
                        <div className="nav-section-title">Insights</div>
                        <NavLink to="/reports" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                            <TrendingUp size={20} />
                            Reports
                        </NavLink>
                        <NavLink to="/alerts" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                            <AlertTriangle size={20} />
                            Alerts
                        </NavLink>
                    </div>
                </nav>

                {/* User section */}
                <div style={{ padding: 'var(--space-lg)', borderTop: '1px solid var(--color-border)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-md)', marginBottom: 'var(--space-md)' }}>
                        <div style={{
                            width: 40, height: 40, borderRadius: 'var(--radius-full)',
                            background: 'var(--gradient-primary)', display: 'flex',
                            alignItems: 'center', justifyContent: 'center', fontWeight: 700
                        }}>
                            {user?.name?.charAt(0).toUpperCase() || 'U'}
                        </div>
                        <div>
                            <div style={{ fontWeight: 600, fontSize: '0.875rem' }}>{user?.name || 'User'}</div>
                            <div style={{ color: 'var(--color-text-muted)', fontSize: '0.75rem' }}>{user?.role || 'Owner'}</div>
                        </div>
                    </div>
                    <button className="nav-link" onClick={handleLogout} style={{ width: '100%' }}>
                        <LogOut size={20} />
                        Logout
                    </button>
                </div>
            </aside>

            {/* Main content */}
            <main className="main-content">
                {children}
            </main>
        </div>
    )
}

export default Layout
