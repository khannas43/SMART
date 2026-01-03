import { Payment, ServiceApplication } from '@/types/api';
import { TFunction } from 'i18next';

/**
 * Generate and download a payment receipt as PDF
 * Creates an HTML receipt and triggers browser print/save as PDF
 */
export const generatePaymentReceipt = (payment: Payment): void => {
  const receiptHTML = `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Payment Receipt - ${payment.transactionId}</title>
  <style>
    @media print {
      @page {
        size: A4;
        margin: 20mm;
      }
    }
    body {
      font-family: Arial, sans-serif;
      max-width: 800px;
      margin: 0 auto;
      padding: 20px;
      color: #333;
    }
    .header {
      text-align: center;
      border-bottom: 3px solid #1976d2;
      padding-bottom: 20px;
      margin-bottom: 30px;
    }
    .header h1 {
      color: #1976d2;
      margin: 0;
      font-size: 28px;
    }
    .header p {
      margin: 5px 0;
      color: #666;
    }
    .receipt-info {
      background: #f5f5f5;
      padding: 20px;
      border-radius: 8px;
      margin-bottom: 30px;
    }
    .info-row {
      display: flex;
      justify-content: space-between;
      padding: 10px 0;
      border-bottom: 1px solid #ddd;
    }
    .info-row:last-child {
      border-bottom: none;
    }
    .info-label {
      font-weight: bold;
      color: #555;
    }
    .info-value {
      color: #333;
      text-align: right;
    }
    .amount-section {
      background: #e3f2fd;
      padding: 20px;
      border-radius: 8px;
      margin: 30px 0;
      text-align: center;
    }
    .amount-label {
      font-size: 14px;
      color: #666;
      margin-bottom: 10px;
    }
    .amount-value {
      font-size: 36px;
      font-weight: bold;
      color: #1976d2;
    }
    .footer {
      margin-top: 40px;
      padding-top: 20px;
      border-top: 2px solid #ddd;
      text-align: center;
      color: #666;
      font-size: 12px;
    }
    .status-badge {
      display: inline-block;
      padding: 5px 15px;
      border-radius: 20px;
      font-weight: bold;
      font-size: 12px;
    }
    .status-success {
      background: #4caf50;
      color: white;
    }
    .status-pending {
      background: #ff9800;
      color: white;
    }
    .status-failed {
      background: #f44336;
      color: white;
    }
  </style>
</head>
<body>
  <div class="header">
    <h1>SMART Citizen Portal</h1>
    <p>Government of Rajasthan</p>
    <p>Payment Receipt</p>
  </div>

  <div class="receipt-info">
    <div class="info-row">
      <span class="info-label">Transaction ID:</span>
      <span class="info-value">${payment.transactionId}</span>
    </div>
    <div class="info-row">
      <span class="info-label">Payment Date:</span>
      <span class="info-value">${new Date(payment.initiatedAt || payment.createdAt || '').toLocaleString('en-IN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })}</span>
    </div>
    <div class="info-row">
      <span class="info-label">Payment Method:</span>
      <span class="info-value">${payment.paymentMethod}</span>
    </div>
    <div class="info-row">
      <span class="info-label">Status:</span>
      <span class="info-value">
        <span class="status-badge status-${payment.status.toLowerCase()}">${payment.status}</span>
      </span>
    </div>
    ${payment.description ? `
    <div class="info-row">
      <span class="info-label">Description:</span>
      <span class="info-value">${payment.description}</span>
    </div>
    ` : ''}
  </div>

  <div class="amount-section">
    <div class="amount-label">Amount Paid</div>
    <div class="amount-value">₹${payment.amount.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</div>
  </div>

  <div class="footer">
    <p>This is a computer-generated receipt. No signature required.</p>
    <p>For any queries, please contact support at support@rajasthan.gov.in</p>
    <p>Generated on: ${new Date().toLocaleString('en-IN')}</p>
  </div>
</body>
</html>
  `;

  // Create a blob and download
  const blob = new Blob([receiptHTML], { type: 'text/html' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `payment-receipt-${payment.transactionId}.html`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);

  // Also open in new window for printing
  const printWindow = window.open('', '_blank');
  if (printWindow) {
    printWindow.document.write(receiptHTML);
    printWindow.document.close();
    // Auto-print after a short delay
    setTimeout(() => {
      printWindow.print();
    }, 250);
  }
};

/**
 * Generate and download a payment receipt as PDF (with translations)
 * Creates an HTML receipt and triggers browser print/save as PDF
 */
export const generatePaymentReceiptPdf = (
  payment: Payment,
  application: ServiceApplication | null,
  t: TFunction
): void => {
  const paymentDate = payment.initiatedAt || payment.createdAt;
  const formattedDate = paymentDate
    ? new Date(paymentDate).toLocaleDateString('en-IN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      })
    : 'N/A';

  const applicationDetails = application
    ? `
    <div class="info-row">
      <span class="info-label">${t('payments.receipt.applicationNumber', { defaultValue: 'Application Number' })}:</span>
      <span class="info-value">${application.applicationNumber || 'N/A'}</span>
    </div>
    <div class="info-row">
      <span class="info-label">${t('payments.receipt.serviceType', { defaultValue: 'Service Type' })}:</span>
      <span class="info-value">${application.serviceType || 'N/A'}</span>
    </div>
    ${application.scheme ? `
    <div class="info-row">
      <span class="info-label">${t('payments.receipt.scheme', { defaultValue: 'Scheme' })}:</span>
      <span class="info-value">${application.scheme.name || 'N/A'}</span>
    </div>
    ` : ''}
  `
    : `<div class="info-row">
      <span class="info-label">${t('payments.receipt.standalonePayment', { defaultValue: 'Type' })}:</span>
      <span class="info-value">${t('payments.receipt.standalonePayment', { defaultValue: 'Standalone Payment' })}</span>
    </div>`;

  const receiptHTML = `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${t('payments.receipt.title', { defaultValue: 'Payment Receipt' })} - ${payment.transactionId}</title>
  <style>
    @media print {
      @page {
        size: A4;
        margin: 20mm;
      }
    }
    body {
      font-family: Arial, sans-serif;
      max-width: 800px;
      margin: 0 auto;
      padding: 20px;
      color: #333;
    }
    .header {
      text-align: center;
      border-bottom: 3px solid #1976d2;
      padding-bottom: 20px;
      margin-bottom: 30px;
    }
    .header h1 {
      color: #1976d2;
      margin: 0;
      font-size: 28px;
    }
    .header p {
      margin: 5px 0;
      color: #666;
    }
    .receipt-info {
      background: #f5f5f5;
      padding: 20px;
      border-radius: 8px;
      margin-bottom: 30px;
    }
    .info-row {
      display: flex;
      justify-content: space-between;
      padding: 10px 0;
      border-bottom: 1px solid #ddd;
    }
    .info-row:last-child {
      border-bottom: none;
    }
    .info-label {
      font-weight: bold;
      color: #555;
    }
    .info-value {
      color: #333;
      text-align: right;
    }
    .amount-section {
      background: #e3f2fd;
      padding: 20px;
      border-radius: 8px;
      margin: 30px 0;
      text-align: center;
    }
    .amount-label {
      font-size: 14px;
      color: #666;
      margin-bottom: 10px;
    }
    .amount-value {
      font-size: 36px;
      font-weight: bold;
      color: #1976d2;
    }
    .footer {
      margin-top: 40px;
      padding-top: 20px;
      border-top: 2px solid #ddd;
      text-align: center;
      color: #666;
      font-size: 12px;
    }
    .status-badge {
      display: inline-block;
      padding: 5px 15px;
      border-radius: 20px;
      font-weight: bold;
      font-size: 12px;
    }
    .status-success, .status-completed {
      background: #4caf50;
      color: white;
    }
    .status-pending, .status-processing {
      background: #ff9800;
      color: white;
    }
    .status-failed, .status-cancelled {
      background: #f44336;
      color: white;
    }
  </style>
</head>
<body>
  <div class="header">
    <h1>${t('common.appName', { defaultValue: 'SMART Citizen Portal' })}</h1>
    <p>${t('payments.receipt.governmentOfRajasthan', { defaultValue: 'Government of Rajasthan' })}</p>
    <p>${t('payments.receipt.title', { defaultValue: 'Payment Receipt' })}</p>
  </div>

  <div class="receipt-info">
    <div class="info-row">
      <span class="info-label">${t('payments.receipt.transactionId', { defaultValue: 'Transaction ID' })}:</span>
      <span class="info-value">${payment.transactionId}</span>
    </div>
    <div class="info-row">
      <span class="info-label">${t('payments.receipt.date', { defaultValue: 'Payment Date' })}:</span>
      <span class="info-value">${formattedDate}</span>
    </div>
    <div class="info-row">
      <span class="info-label">${t('payments.receipt.amount', { defaultValue: 'Amount' })}:</span>
      <span class="info-value">${payment.currency} ${payment.amount.toFixed(2)}</span>
    </div>
    <div class="info-row">
      <span class="info-label">${t('payments.receipt.method', { defaultValue: 'Payment Method' })}:</span>
      <span class="info-value">${payment.paymentMethod}</span>
    </div>
    <div class="info-row">
      <span class="info-label">${t('payments.receipt.status', { defaultValue: 'Status' })}:</span>
      <span class="info-value">
        <span class="status-badge status-${payment.status.toLowerCase()}">${payment.status}</span>
      </span>
    </div>
    ${payment.description ? `
    <div class="info-row">
      <span class="info-label">${t('payments.receipt.description', { defaultValue: 'Description' })}:</span>
      <span class="info-value">${payment.description}</span>
    </div>
    ` : ''}
    ${applicationDetails}
  </div>

  <div class="amount-section">
    <div class="amount-label">${t('payments.receipt.amountPaid', { defaultValue: 'Amount Paid' })}</div>
    <div class="amount-value">₹${payment.amount.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</div>
  </div>

  <div class="footer">
    <p>${t('payments.receipt.note', { defaultValue: 'This is a computer-generated receipt. No signature required.' })}</p>
    <p>${t('payments.receipt.generatedOn', { defaultValue: 'Generated on' })}: ${new Date().toLocaleString('en-IN')}</p>
  </div>
</body>
</html>
  `;

  // Create a blob URL for the receipt HTML
  const blob = new Blob([receiptHTML], { type: 'text/html;charset=utf-8' });
  const blobUrl = URL.createObjectURL(blob);
  
  // Try to open in new window and trigger print dialog
  try {
    const printWindow = window.open(blobUrl, '_blank', 'width=800,height=600');
    
    if (printWindow) {
      // Wait for window to load, then trigger print
      const triggerPrint = () => {
        try {
          if (printWindow && !printWindow.closed) {
            // Focus the window first
            printWindow.focus();
            // Small delay to ensure window is ready
            setTimeout(() => {
              if (printWindow && !printWindow.closed) {
                printWindow.print();
              }
            }, 500);
          }
        } catch (err) {
          console.error('Error triggering print:', err);
          // Fallback to direct download if print fails
          downloadReceiptFile(blobUrl, payment.transactionId);
        }
      };
      
      // Check if window loaded
      if (printWindow.document && printWindow.document.readyState === 'complete') {
        triggerPrint();
      } else {
        // Wait for load event
        printWindow.onload = () => {
          triggerPrint();
        };
        
        // Fallback timeout
        setTimeout(() => {
          if (printWindow && !printWindow.closed) {
            triggerPrint();
          }
        }, 2000);
      }
    } else {
      // Popup blocked - fallback to direct download
      downloadReceiptFile(blobUrl, payment.transactionId);
    }
  } catch (error) {
    console.warn('Could not open print window, using direct download:', error);
    downloadReceiptFile(blobUrl, payment.transactionId);
  }
  
  // Helper function to download receipt file
  function downloadReceiptFile(url: string, transactionId: string) {
    const link = document.createElement('a');
    link.href = url;
    link.download = `payment-receipt-${transactionId}.html`;
    link.style.display = 'none';
    document.body.appendChild(link);
    link.click();
    setTimeout(() => {
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    }, 100);
  }
};

