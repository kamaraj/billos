import { useState, useEffect } from 'react'
import api from '../utils/api'
import { Search, Plus, ShoppingCart, Minus, X, Check } from 'lucide-react'

function Billing() {
    const [products, setProducts] = useState([])
    const [customers, setCustomers] = useState([])
    const [cart, setCart] = useState([])
    const [selectedCustomer, setSelectedCustomer] = useState(null)
    const [search, setSearch] = useState('')
    const [loading, setLoading] = useState(true)
    const [showSuccess, setShowSuccess] = useState(false)

    useEffect(() => {
        fetchData()
    }, [])

    const fetchData = async () => {
        try {
            const [productsRes, customersRes] = await Promise.all([
                api.get('/api/products'),
                api.get('/api/customers')
            ])
            // API returns { items: [...], total: N }
            setProducts(productsRes.data.items || [])
            setCustomers(customersRes.data.items || [])
        } catch (err) {
            console.error('Fetch error:', err)
        } finally {
            setLoading(false)
        }
    }

    const addToCart = (product) => {
        const existing = cart.find(item => item.product_id === product.id)

        if (existing) {
            if (existing.qty < product.stock) { // Use 'stock' from API, not 'current_stock'
                setCart(cart.map(item =>
                    item.product_id === product.id
                        ? { ...item, qty: item.qty + 1 }
                        : item
                ))
            }
        } else {
            if (product.stock > 0) {
                setCart([...cart, {
                    product_id: product.id,
                    product_name: product.name,
                    unit_price: product.price, // API returns 'price'
                    qty: 1,
                    stock: product.stock,
                    gst_rate: 0 // Mock API doesn't have tax yet
                }])
            }
        }
    }

    const updateQty = (productId, delta) => {
        setCart(cart.map(item => {
            if (item.product_id === productId) {
                const newQty = item.qty + delta
                if (newQty <= 0) return null
                if (newQty > item.stock) return item
                return { ...item, qty: newQty }
            }
            return item
        }).filter(Boolean))
    }

    const removeFromCart = (productId) => {
        setCart(cart.filter(item => item.product_id !== productId))
    }

    const getSubtotal = () => {
        return cart.reduce((sum, item) => sum + (item.unit_price * item.qty), 0)
    }

    const getTax = () => {
        return cart.reduce((sum, item) => {
            const itemTotal = item.unit_price * item.qty
            return sum + (itemTotal * (item.gst_rate / 100))
        }, 0)
    }

    const getTotal = () => {
        return getSubtotal() + getTax()
    }

    const handleCheckout = async (paymentMode) => {
        if (cart.length === 0) return

        try {
            const invoiceData = {
                customer_id: selectedCustomer?.id || null,
                invoice_type: 'SALE',
                is_gst_invoice: cart.some(item => item.gst_rate > 0),
                items: cart.map(item => ({
                    product_id: item.product_id,
                    qty: item.qty,
                    unit_price: item.unit_price,
                    discount_percent: 0
                })),
                discount_percent: 0,
                discount_amount: 0,
                payment_mode: paymentMode,
                paid_amount: paymentMode === 'CREDIT' ? 0 : getTotal()
            }

            await api.post('/api/invoices/', invoiceData)

            setCart([])
            setSelectedCustomer(null)
            setShowSuccess(true)
            setTimeout(() => setShowSuccess(false), 3000)

            // Refresh products for updated stock
            fetchData()
        } catch (err) {
            console.error('Checkout error:', err)
            alert(err.response?.data?.detail || 'Failed to create invoice')
        }
    }

    const formatCurrency = (amount) => {
        return new Intl.NumberFormat('en-QA', {
            style: 'currency',
            currency: 'QAR',
            maximumFractionDigits: 2
        }).format(amount)
    }

    const filteredProducts = products.filter(p =>
        p.name.toLowerCase().includes(search.toLowerCase()) ||
        (p.sku || '').toLowerCase().includes(search.toLowerCase())
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
                        <h1 className="page-title">Quick Billing</h1>
                        <p className="page-subtitle">Create invoice in seconds</p>
                    </div>

                    {/* Customer selector */}
                    <select
                        className="form-input form-select"
                        style={{ width: 250 }}
                        value={selectedCustomer?.id || ''}
                        onChange={(e) => {
                            const customer = customers.find(c => c.id === e.target.value)
                            setSelectedCustomer(customer || null)
                        }}
                    >
                        <option value="">Walk-in Customer</option>
                        {customers.map(c => (
                            <option key={c.id} value={c.id}>{c.name} ({c.phone})</option>
                        ))}
                    </select>
                </div>
            </header>

            <div className="page-content">
                {/* Success message */}
                {showSuccess && (
                    <div className="alert alert-success" style={{ marginBottom: 'var(--space-lg)' }}>
                        <Check size={20} />
                        Invoice created successfully!
                    </div>
                )}

                <div className="billing-container">
                    {/* Products section */}
                    <div>
                        {/* Search */}
                        <div className="search-container" style={{ marginBottom: 'var(--space-lg)' }}>
                            <Search size={20} className="search-icon" />
                            <input
                                type="text"
                                className="form-input search-input"
                                placeholder="Search products by name or SKU..."
                                value={search}
                                onChange={(e) => setSearch(e.target.value)}
                            />
                        </div>

                        {/* Products grid */}
                        <div className="products-grid">
                            {filteredProducts.map(product => {
                                const inCart = cart.find(item => item.product_id === product.id)

                                return (
                                    <div
                                        key={product.id}
                                        className={`product-card ${inCart ? 'selected' : ''}`}
                                        onClick={() => addToCart(product)}
                                    >
                                        <div className="product-name">{product.name}</div>
                                        <div className="product-price">{formatCurrency(product.price)}</div>
                                        <div className="product-stock">
                                            Stock: {product.stock}
                                            {inCart && <span style={{ color: 'var(--color-success)' }}> • In cart: {inCart.qty}</span>}
                                        </div>
                                        {/* Mock Low stock check */}
                                        {product.stock <= 10 && (
                                            <span className="badge badge-warning" style={{ marginTop: 'var(--space-sm)' }}>
                                                Low Stock
                                            </span>
                                        )}
                                    </div>
                                )
                            })}

                            {filteredProducts.length === 0 && (
                                <div className="empty-state" style={{ gridColumn: '1 / -1' }}>
                                    <p>No products found</p>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Cart panel */}
                    <div className="cart-panel">
                        <div className="cart-header">
                            <h3 style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-sm)' }}>
                                <ShoppingCart size={20} />
                                Cart ({cart.length})
                            </h3>
                        </div>

                        <div className="cart-items">
                            {cart.length === 0 ? (
                                <div className="empty-state">
                                    <p>Add products to cart</p>
                                </div>
                            ) : (
                                cart.map(item => (
                                    <div key={item.product_id} className="cart-item">
                                        <div className="cart-item-info">
                                            <div className="cart-item-name">{item.product_name}</div>
                                            <div className="cart-item-price">
                                                {formatCurrency(item.unit_price)} × {item.qty} = {formatCurrency(item.unit_price * item.qty)}
                                            </div>
                                        </div>
                                        <div className="qty-control">
                                            <button className="qty-btn" onClick={() => updateQty(item.product_id, -1)}>
                                                <Minus size={16} />
                                            </button>
                                            <span className="qty-value">{item.qty}</span>
                                            <button className="qty-btn" onClick={() => updateQty(item.product_id, 1)}>
                                                <Plus size={16} />
                                            </button>
                                            <button
                                                className="qty-btn"
                                                onClick={() => removeFromCart(item.product_id)}
                                                style={{ marginLeft: 'var(--space-sm)', color: 'var(--color-danger)' }}
                                            >
                                                <X size={16} />
                                            </button>
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>

                        <div className="cart-footer">
                            {/* Totals */}
                            <div style={{ marginBottom: 'var(--space-md)' }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 'var(--space-sm)' }}>
                                    <span style={{ color: 'var(--color-text-secondary)' }}>Subtotal</span>
                                    <span>{formatCurrency(getSubtotal())}</span>
                                </div>
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 'var(--space-sm)' }}>
                                    <span style={{ color: 'var(--color-text-secondary)' }}>Tax (VAT)</span>
                                    <span>{formatCurrency(getTax())}</span>
                                </div>
                            </div>

                            <div className="cart-total">
                                <span className="cart-total-label">Total</span>
                                <span className="cart-total-value">{formatCurrency(getTotal())}</span>
                            </div>

                            {/* Payment buttons */}
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-sm)' }}>
                                <button
                                    className="btn btn-success"
                                    onClick={() => handleCheckout('CASH')}
                                    disabled={cart.length === 0}
                                >
                                    Cash
                                </button>
                                <button
                                    className="btn btn-primary"
                                    onClick={() => handleCheckout('UPI')}
                                    disabled={cart.length === 0}
                                >
                                    UPI
                                </button>
                                <button
                                    className="btn btn-secondary"
                                    onClick={() => handleCheckout('CARD')}
                                    disabled={cart.length === 0}
                                >
                                    Card
                                </button>
                                <button
                                    className="btn btn-secondary"
                                    onClick={() => handleCheckout('CREDIT')}
                                    disabled={cart.length === 0 || !selectedCustomer}
                                    title={!selectedCustomer ? 'Select a customer for credit sale' : ''}
                                >
                                    Credit
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </>
    )
}

export default Billing
