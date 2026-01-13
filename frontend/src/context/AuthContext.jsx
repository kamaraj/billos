import { createContext, useContext, useState, useEffect } from 'react'
import api from '../utils/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
    const [token, setToken] = useState(localStorage.getItem('token'))
    const [user, setUser] = useState(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        if (token) {
            // Fetch user profile
            api.get('/api/auth/me')
                .then(res => {
                    setUser(res.data)
                    setLoading(false)
                })
                .catch(() => {
                    logout()
                    setLoading(false)
                })
        } else {
            setLoading(false)
        }
    }, [token])

    const login = async (phone, password) => {
        const response = await api.post('/api/auth/login', { phone, password })
        const { access_token, user_id, tenant_id, user_name, role } = response.data

        localStorage.setItem('token', access_token)
        setToken(access_token)
        setUser({ id: user_id, name: user_name, role, tenant_id })

        return response.data
    }

    const register = async (data) => {
        const response = await api.post('/api/auth/register', data)
        const { access_token, user_id, tenant_id, user_name, role } = response.data

        localStorage.setItem('token', access_token)
        setToken(access_token)
        setUser({ id: user_id, name: user_name, role, tenant_id })

        return response.data
    }

    const logout = () => {
        localStorage.removeItem('token')
        setToken(null)
        setUser(null)
    }

    return (
        <AuthContext.Provider value={{ token, user, loading, login, register, logout }}>
            {children}
        </AuthContext.Provider>
    )
}

export function useAuth() {
    const context = useContext(AuthContext)
    if (!context) {
        throw new Error('useAuth must be used within AuthProvider')
    }
    return context
}
