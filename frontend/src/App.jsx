import { useState, useEffect } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Billing from './pages/Billing'
import Products from './pages/Products'
import Customers from './pages/Customers'
import Invoices from './pages/Invoices'
import Reports from './pages/Reports'
import Alerts from './pages/Alerts'
import { AuthProvider, useAuth } from './context/AuthContext'

function ProtectedRoute({ children }) {
    const { token, loading } = useAuth()

    if (loading) {
        return (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh' }}>
                <div className="loading-spinner"></div>
            </div>
        )
    }

    if (!token) {
        return <Navigate to="/login" replace />
    }

    return children
}

function AppRoutes() {
    const { token } = useAuth()

    return (
        <Routes>
            <Route path="/login" element={token ? <Navigate to="/" replace /> : <Login />} />
            <Route path="/" element={
                <ProtectedRoute>
                    <Layout>
                        <Dashboard />
                    </Layout>
                </ProtectedRoute>
            } />
            <Route path="/billing" element={
                <ProtectedRoute>
                    <Layout>
                        <Billing />
                    </Layout>
                </ProtectedRoute>
            } />
            <Route path="/products" element={
                <ProtectedRoute>
                    <Layout>
                        <Products />
                    </Layout>
                </ProtectedRoute>
            } />
            <Route path="/customers" element={
                <ProtectedRoute>
                    <Layout>
                        <Customers />
                    </Layout>
                </ProtectedRoute>
            } />
            <Route path="/invoices" element={
                <ProtectedRoute>
                    <Layout>
                        <Invoices />
                    </Layout>
                </ProtectedRoute>
            } />
            <Route path="/reports" element={
                <ProtectedRoute>
                    <Layout>
                        <Reports />
                    </Layout>
                </ProtectedRoute>
            } />
            <Route path="/alerts" element={
                <ProtectedRoute>
                    <Layout>
                        <Alerts />
                    </Layout>
                </ProtectedRoute>
            } />
        </Routes>
    )
}

function App() {
    return (
        <AuthProvider>
            <AppRoutes />
        </AuthProvider>
    )
}

export default App
