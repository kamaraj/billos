import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { Receipt, Eye, EyeOff } from 'lucide-react'

function Login() {
    const [isRegister, setIsRegister] = useState(false)
    const [showPassword, setShowPassword] = useState(false)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')

    const [formData, setFormData] = useState({
        phone: '',
        password: '',
        name: '',
        business_name: '',
        business_type: 'retail',
        is_gst_enabled: false
    })

    const { login, register } = useAuth()
    const navigate = useNavigate()

    const handleChange = (e) => {
        const { name, value, type, checked } = e.target
        setFormData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }))
    }

    const handleSubmit = async (e) => {
        e.preventDefault()
        setError('')
        setLoading(true)

        try {
            if (isRegister) {
                await register(formData)
            } else {
                await login(formData.phone, formData.password)
            }
            navigate('/')
        } catch (err) {
            setError(err.response?.data?.detail || 'Something went wrong')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div style={{
            minHeight: '100vh',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%)',
            padding: 'var(--space-lg)'
        }}>
            <div style={{
                width: '100%',
                maxWidth: '420px',
                background: 'var(--color-bg-card)',
                borderRadius: 'var(--radius-xl)',
                border: '1px solid var(--color-border)',
                padding: 'var(--space-2xl)',
                boxShadow: 'var(--shadow-lg)'
            }}>
                {/* Header */}
                <div style={{ textAlign: 'center', marginBottom: 'var(--space-xl)' }}>
                    <div style={{
                        width: 64,
                        height: 64,
                        background: 'var(--gradient-primary)',
                        borderRadius: 'var(--radius-xl)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        margin: '0 auto var(--space-lg)'
                    }}>
                        <Receipt size={32} color="white" />
                    </div>
                    <h1 style={{ marginBottom: 'var(--space-xs)' }}>BillOS</h1>
                    <p style={{ color: 'var(--color-text-secondary)' }}>
                        {isRegister ? 'Create your business account' : 'Welcome back! Sign in to continue'}
                    </p>
                </div>

                {/* Error */}
                {error && (
                    <div className="alert alert-danger" style={{ marginBottom: 'var(--space-lg)' }}>
                        {error}
                    </div>
                )}

                {/* Form */}
                <form onSubmit={handleSubmit}>
                    {isRegister && (
                        <>
                            <div className="form-group">
                                <label className="form-label">Your Name</label>
                                <input
                                    type="text"
                                    name="name"
                                    className="form-input"
                                    placeholder="Enter your name"
                                    value={formData.name}
                                    onChange={handleChange}
                                    required
                                />
                            </div>

                            <div className="form-group">
                                <label className="form-label">Business Name</label>
                                <input
                                    type="text"
                                    name="business_name"
                                    className="form-input"
                                    placeholder="Enter business name"
                                    value={formData.business_name}
                                    onChange={handleChange}
                                    required
                                />
                            </div>

                            <div className="form-group">
                                <label className="form-label">Business Type</label>
                                <select
                                    name="business_type"
                                    className="form-input form-select"
                                    value={formData.business_type}
                                    onChange={handleChange}
                                >
                                    <option value="retail">Retail / Kirana</option>
                                    <option value="medical">Medical / Pharmacy</option>
                                    <option value="wholesale">Wholesale</option>
                                    <option value="hardware">Hardware / Electrical</option>
                                    <option value="textile">Textile / Garments</option>
                                    <option value="food">Food / Restaurant</option>
                                    <option value="other">Other</option>
                                </select>
                            </div>
                        </>
                    )}

                    <div className="form-group">
                        <label className="form-label">Phone Number</label>
                        <input
                            type="tel"
                            name="phone"
                            className="form-input"
                            placeholder="Enter your phone number"
                            value={formData.phone}
                            onChange={handleChange}
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label className="form-label">Password</label>
                        <div style={{ position: 'relative' }}>
                            <input
                                type={showPassword ? 'text' : 'password'}
                                name="password"
                                className="form-input"
                                placeholder="Enter password"
                                value={formData.password}
                                onChange={handleChange}
                                required
                                style={{ paddingRight: '44px' }}
                            />
                            <button
                                type="button"
                                onClick={() => setShowPassword(!showPassword)}
                                style={{
                                    position: 'absolute',
                                    right: 'var(--space-md)',
                                    top: '50%',
                                    transform: 'translateY(-50%)',
                                    background: 'none',
                                    border: 'none',
                                    color: 'var(--color-text-muted)',
                                    cursor: 'pointer'
                                }}
                            >
                                {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                            </button>
                        </div>
                    </div>

                    {isRegister && (
                        <div className="form-group">
                            <label style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-sm)', cursor: 'pointer' }}>
                                <input
                                    type="checkbox"
                                    name="is_gst_enabled"
                                    checked={formData.is_gst_enabled}
                                    onChange={handleChange}
                                />
                                <span style={{ color: 'var(--color-text-secondary)' }}>Enable GST billing</span>
                            </label>
                        </div>
                    )}

                    <button
                        type="submit"
                        className="btn btn-primary btn-lg"
                        disabled={loading}
                        style={{ width: '100%', marginTop: 'var(--space-md)' }}
                    >
                        {loading ? 'Please wait...' : (isRegister ? 'Create Account' : 'Sign In')}
                    </button>
                </form>

                {/* Toggle */}
                <div style={{ textAlign: 'center', marginTop: 'var(--space-xl)' }}>
                    <span style={{ color: 'var(--color-text-secondary)' }}>
                        {isRegister ? 'Already have an account?' : "Don't have an account?"}
                    </span>{' '}
                    <button
                        onClick={() => setIsRegister(!isRegister)}
                        style={{
                            background: 'none',
                            border: 'none',
                            color: 'var(--color-primary-light)',
                            cursor: 'pointer',
                            fontWeight: 600
                        }}
                    >
                    </button>
                </div>

                {/* Demo Credentials */}
                {!isRegister && (
                    <div style={{ marginTop: 'var(--space-xl)', paddingTop: 'var(--space-lg)', borderTop: '1px solid var(--color-border)' }}>
                        <p style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginBottom: 'var(--space-md)', textAlign: 'center', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                            Demo Credentials
                        </p>
                        <div style={{ display: 'grid', gap: 'var(--space-sm)' }}>
                            {[
                                { name: "Abdulla Al-Thani", role: "Owner", phone: "97411112222", pass: "pass" },
                                { name: "Mohammed Ali", role: "Manager", phone: "97433334444", pass: "pass" },
                                { name: "Pareekutty", role: "Cashier", phone: "97455556666", pass: "pass" }
                            ].map(user => (
                                <button
                                    key={user.phone}
                                    type="button"
                                    onClick={() => setFormData(prev => ({ ...prev, phone: user.phone, password: user.pass }))}
                                    className="btn btn-secondary"
                                    style={{ justifyContent: 'space-between', padding: 'var(--space-sm) var(--space-md)', textAlign: 'left' }}
                                >
                                    <div>
                                        <div style={{ fontWeight: 600, fontSize: '0.875rem' }}>{user.name}</div>
                                        <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>{user.role} • {user.phone}</div>
                                    </div>
                                    <div className="btn-icon" style={{ width: 24, height: 24, background: 'var(--color-bg)', border: '1px solid var(--color-border)' }}>
                                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                            <polyline points="9 18 15 12 9 6"></polyline>
                                        </svg>
                                    </div>
                                </button>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </div>
    )
}

export default Login
