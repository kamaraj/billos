import { X, Printer, Share2 } from 'lucide-react'
import { useRef } from 'react'

const InvoiceModal = ({ invoice, onClose, tenantName = 'Doha Hypermarket' }) => {
    if (!invoice) return null

    // Print functionality
    const printRef = useRef()

    const handlePrint = () => {
        window.print()
    }

    const formatCurrency = (amount) => {
        return new Intl.NumberFormat('en-QA', {
            style: 'currency',
            currency: 'QAR',
            maximumFractionDigits: 2
        }).format(amount)
    }

    const formatDate = (dateStr) => {
        if (!dateStr) return ''
        return new Date(dateStr).toLocaleDateString('en-QA', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        })
    }

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal invoice-modal-content" onClick={e => e.stopPropagation()}>
                <div className="modal-header no-print">
                    <h3 className="modal-title">Invoice Details</h3>
                    <div style={{ display: 'flex', gap: '8px' }}>
                        <button className="btn btn-secondary btn-sm" onClick={handlePrint}>
                            <Printer size={16} /> Print
                        </button>
                        <button className="modal-close" onClick={onClose}>
                            <X size={20} />
                        </button>
                    </div>
                </div>

                <div className="modal-body printable-area" ref={printRef}>
                    {/* Invoice Header */}
                    <div className="invoice-header">
                        <div className="invoice-brand">
                            <h1>{tenantName}</h1>
                            <p>West Bay, Doha, Qatar</p>
                            <p>Phone: +974 4444 5555</p>
                        </div>
                        <div className="invoice-meta">
                            <h2>INVOICE</h2>
                            <div className="meta-row">
                                <span>Invoice No:</span>
                                <strong>{invoice.invoice_no}</strong>
                            </div>
                            <div className="meta-row">
                                <span>Date:</span>
                                <strong>{formatDate(invoice.invoice_date)}</strong>
                            </div>
                            <div className="meta-row">
                                <span>Status:</span>
                                <strong>{invoice.payment_status}</strong>
                            </div>
                        </div>
                    </div>

                    <div className="invoice-divider"></div>

                    {/* Bill To */}
                    <div className="invoice-section">
                        <h3>Bill To:</h3>
                        {invoice.customer_name ? (
                            <div>
                                <p className="font-bold">{invoice.customer_name}</p>
                                {invoice.customer_phone && <p>Phone: {invoice.customer_phone}</p>}
                            </div>
                        ) : (
                            <p>Walk-in Customer</p>
                        )}
                    </div>

                    {/* Items Table */}
                    <div className="invoice-table-container">
                        <table className="invoice-table">
                            <thead>
                                <tr>
                                    <th>#</th>
                                    <th>Item</th>
                                    <th className="text-right">Qty</th>
                                    <th className="text-right">Price</th>
                                    <th className="text-right">Total</th>
                                </tr>
                            </thead>
                            <tbody>
                                {invoice.items && invoice.items.map((item, index) => (
                                    <tr key={index}>
                                        <td>{index + 1}</td>
                                        <td>
                                            <div className="item-name">{item.product_name}</div>
                                            {item.discount_amount > 0 && <div className="item-disc">Disc: {item.discount_percent}%</div>}
                                        </td>
                                        <td className="text-right">{item.qty} {item.unit}</td>
                                        <td className="text-right">{formatCurrency(item.unit_price)}</td>
                                        <td className="text-right">{formatCurrency(item.total)}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>

                    {/* Totals */}
                    <div className="invoice-footer">
                        <div className="invoice-notes">
                            {invoice.notes && (
                                <>
                                    <h4>Notes:</h4>
                                    <p>{invoice.notes}</p>
                                </>
                            )}
                        </div>
                        <div className="invoice-totals">
                            <div className="total-row">
                                <span>Subtotal:</span>
                                <span>{formatCurrency(invoice.subtotal)}</span>
                            </div>
                            {invoice.discount_amount > 0 && (
                                <div className="total-row discount">
                                    <span>Discount:</span>
                                    <span>-{formatCurrency(invoice.discount_amount)}</span>
                                </div>
                            )}
                            {invoice.tax_amount > 0 && (
                                <div className="total-row">
                                    <span>Tax:</span>
                                    <span>{formatCurrency(invoice.tax_amount)}</span>
                                </div>
                            )}
                            <div className="total-row grand-total">
                                <span>Total:</span>
                                <span>{formatCurrency(invoice.total_amount)}</span>
                            </div>
                            <div className="total-row">
                                <span>Paid:</span>
                                <span>{formatCurrency(invoice.paid_amount)}</span>
                            </div>
                            <div className="total-row balance">
                                <span>Balance:</span>
                                <span>{formatCurrency(invoice.balance_amount)}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <style>{`
                .invoice-modal-content {
                    max-width: 800px;
                    width: 95%;
                    background: white;
                    color: black;
                }
                .printable-area {
                    padding: 40px;
                    font-family: 'Inter', sans-serif;
                }
                .invoice-header {
                    display: flex;
                    justify-content: space-between;
                    margin-bottom: 30px;
                }
                .invoice-brand h1 {
                    font-size: 24px;
                    color: #333;
                    margin-bottom: 5px;
                }
                .invoice-brand p {
                    color: #666;
                    font-size: 14px;
                    margin: 0;
                }
                .invoice-meta {
                    text-align: right;
                }
                .invoice-meta h2 {
                    font-size: 24px;
                    color: #6366f1;
                    margin-bottom: 10px;
                    letter-spacing: 2px;
                }
                .meta-row {
                    display: flex;
                    justify-content: flex-end;
                    gap: 15px;
                    margin-bottom: 5px;
                }
                .invoice-divider {
                    height: 2px;
                    background: #f1f5f9;
                    margin: 20px 0;
                }
                .invoice-section {
                    margin-bottom: 30px;
                }
                .invoice-section h3 {
                    font-size: 14px;
                    text-transform: uppercase;
                    color: #64748b;
                    margin-bottom: 8px;
                }
                .invoice-table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 30px;
                }
                .invoice-table th {
                    text-align: left;
                    padding: 12px;
                    background: #f8fafc;
                    border-bottom: 2px solid #e2e8f0;
                    color: #475569;
                    font-weight: 600;
                    font-size: 12px;
                    text-transform: uppercase;
                }
                .invoice-table td {
                    padding: 12px;
                    border-bottom: 1px solid #e2e8f0;
                    color: #334155;
                }
                .text-right { text-align: right; }
                .invoice-footer {
                    display: flex;
                    justify-content: space-between;
                }
                .invoice-totals {
                    width: 300px;
                }
                .total-row {
                    display: flex;
                    justify-content: space-between;
                    padding: 8px 0;
                    border-bottom: 1px solid #f1f5f9;
                }
                .total-row.grand-total {
                    font-weight: 800;
                    font-size: 18px;
                    border-top: 2px solid #e2e8f0;
                    border-bottom: none;
                    margin-top: 10px;
                    padding-top: 15px;
                }
                
                @media print {
                    body * {
                        visibility: hidden;
                    }
                    .printable-area, .printable-area * {
                        visibility: visible;
                    }
                    .modal-overlay {
                        background: none;
                        position: absolute;
                        top: 0;
                        left: 0;
                        width: 100%;
                        height: 100%;
                        display: block;
                    }
                    .modal {
                        border: none;
                        background: white;
                        box-shadow: none;
                        position: absolute;
                        top: 0;
                        left: 0;
                        width: 100%;
                        max-width: 100%;
                    }
                    .no-print { display: none; }
                }
            `}</style>
        </div>
    )
}

export default InvoiceModal
