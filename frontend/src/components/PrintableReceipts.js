import React from 'react';
import { Card } from "@/components/ui/card";

// Función para convertir números a letras
const numberToWords = (num) => {
  const units = ['', 'uno', 'dos', 'tres', 'cuatro', 'cinco', 'seis', 'siete', 'ocho', 'nueve'];
  const teens = ['diez', 'once', 'doce', 'trece', 'catorce', 'quince', 'dieciséis', 'diecisiete', 'dieciocho', 'diecinueve'];
  const tens = ['', '', 'veinte', 'treinta', 'cuarenta', 'cincuenta', 'sesenta', 'setenta', 'ochenta', 'noventa'];
  const hundreds = ['', 'ciento', 'doscientos', 'trescientos', 'cuatrocientos', 'quinientos', 'seiscientos', 'setecientos', 'ochocientos', 'novecientos'];

  if (num === 0) return 'cero';
  if (num === 100) return 'cien';

  let words = '';
  const integerPart = Math.floor(num);
  const decimalPart = Math.round((num - integerPart) * 100);

  // Miles
  if (integerPart >= 1000) {
    const thousands = Math.floor(integerPart / 1000);
    if (thousands === 1) {
      words += 'mil ';
    } else {
      words += numberToWords(thousands) + ' mil ';
    }
  }

  const remainder = integerPart % 1000;

  // Centenas
  if (remainder >= 100) {
    const hundredsDigit = Math.floor(remainder / 100);
    words += hundreds[hundredsDigit] + ' ';
  }

  const lastTwo = remainder % 100;

  // Decenas y unidades
  if (lastTwo >= 20) {
    const tensDigit = Math.floor(lastTwo / 10);
    const unitsDigit = lastTwo % 10;
    words += tens[tensDigit];
    if (unitsDigit > 0) {
      words += ' y ' + units[unitsDigit];
    }
  } else if (lastTwo >= 10) {
    words += teens[lastTwo - 10];
  } else if (lastTwo > 0) {
    words += units[lastTwo];
  }

  if (decimalPart > 0) {
    words += ` con ${decimalPart}/100`;
  }

  return words.trim();
};

const formatCurrency = (amount) => {
  return new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' }).format(amount);
};

const Receipt = ({ receiptNumber, employeeName, amount, weekStart, weekEnd }) => {
  const today = new Date().toLocaleDateString('es-AR', { 
    day: '2-digit', 
    month: '2-digit', 
    year: 'numeric' 
  });

  const amountInWords = numberToWords(amount);

  return (
    <div className="receipt-container">
      <div className="receipt-border">
        <div className="receipt-header">
          <div className="company-name">PMD ARQUITECTURA</div>
          <div className="receipt-number">Recibo N° {receiptNumber}</div>
        </div>

        <div className="receipt-date">
          Fecha: {today}
        </div>

        <div className="receipt-body">
          <div className="receipt-line">
            <span className="label">Recibí de:</span>
            <span className="value underline">PMD ARQUITECTURA</span>
          </div>

          <div className="receipt-line">
            <span className="label">La suma de:</span>
            <span className="value underline">{formatCurrency(amount)}</span>
          </div>

          <div className="receipt-line">
            <span className="label">En letras:</span>
            <span className="value underline uppercase">{amountInWords} PESOS</span>
          </div>

          <div className="receipt-line">
            <span className="label">En concepto de:</span>
            <span className="value underline">Pago de salarios - Semana del {weekStart} al {weekEnd}</span>
          </div>

          <div className="receipt-line full-line">
            <span className="label">En carácter de:</span>
            <span className="value underline">Pago total y definitivo</span>
          </div>
        </div>

        <div className="receipt-footer">
          <div className="signature-section">
            <div className="signature-line">_____________________________</div>
            <div className="signature-label">Firma del empleado</div>
          </div>

          <div className="signature-section">
            <div className="employee-name">{employeeName}</div>
            <div className="signature-label">Aclaración</div>
          </div>

          <div className="signature-section">
            <div className="signature-line">_____________________________</div>
            <div className="signature-label">DNI</div>
          </div>
        </div>

        <div className="receipt-note">
          Sin otro particular, saluda atentamente.
        </div>
      </div>
    </div>
  );
};

const PrintableReceipts = ({ receipts, weekStart }) => {
  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('es-AR', { day: '2-digit', month: '2-digit', year: 'numeric' });
  };

  const getWeekEnd = (startDate) => {
    const date = new Date(startDate);
    date.setDate(date.getDate() + 6);
    return date.toISOString().split('T')[0];
  };

  const weekEnd = getWeekEnd(weekStart);

  return (
    <div className="print-container">
      <style>{`
        @media print {
          body * {
            visibility: hidden;
          }
          
          .print-container,
          .print-container * {
            visibility: visible;
          }
          
          .print-container {
            position: absolute;
            left: 0;
            top: 0;
            width: 100%;
          }

          @page {
            size: A4;
            margin: 10mm;
          }
        }

        .receipt-container {
          width: 100%;
          height: 19%;
          margin-bottom: 1%;
          page-break-inside: avoid;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .receipt-border {
          width: 100%;
          padding: 12px;
          border: 2px solid #1e40af;
          border-radius: 4px;
          background: white;
          font-family: 'Arial', sans-serif;
        }

        .receipt-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 8px;
          padding-bottom: 8px;
          border-bottom: 2px solid #1e40af;
        }

        .company-name {
          font-size: 16px;
          font-weight: bold;
          color: #1e40af;
          letter-spacing: 1px;
        }

        .receipt-number {
          font-size: 12px;
          font-weight: bold;
          color: #475569;
        }

        .receipt-date {
          text-align: right;
          font-size: 11px;
          margin-bottom: 8px;
          color: #475569;
        }

        .receipt-body {
          margin: 12px 0;
        }

        .receipt-line {
          display: flex;
          margin-bottom: 6px;
          font-size: 11px;
          align-items: baseline;
        }

        .receipt-line.full-line {
          flex-direction: column;
        }

        .receipt-line .label {
          font-weight: 600;
          color: #334155;
          min-width: 100px;
          margin-right: 8px;
        }

        .receipt-line .value {
          flex: 1;
          color: #1e293b;
        }

        .receipt-line .underline {
          border-bottom: 1px solid #cbd5e1;
          padding-bottom: 2px;
          display: inline-block;
          min-height: 16px;
        }

        .receipt-line .uppercase {
          text-transform: uppercase;
        }

        .receipt-footer {
          display: flex;
          justify-content: space-between;
          margin-top: 16px;
          margin-bottom: 8px;
        }

        .signature-section {
          flex: 1;
          text-align: center;
        }

        .signature-line {
          margin-bottom: 2px;
          font-size: 10px;
          color: #1e293b;
        }

        .employee-name {
          font-weight: bold;
          margin-bottom: 2px;
          font-size: 11px;
          color: #1e293b;
        }

        .signature-label {
          font-size: 9px;
          color: #64748b;
          font-style: italic;
        }

        .receipt-note {
          text-align: center;
          font-size: 9px;
          color: #64748b;
          font-style: italic;
          margin-top: 8px;
        }

        /* Screen preview styles */
        @media screen {
          .print-container {
            background: #f1f5f9;
            padding: 20px;
            max-width: 210mm;
            margin: 0 auto;
          }
        }
      `}</style>

      {receipts.map((receipt, index) => (
        <Receipt
          key={index}
          receiptNumber={receipt.receiptNumber}
          employeeName={receipt.employeeName}
          amount={receipt.amount}
          weekStart={formatDate(weekStart)}
          weekEnd={formatDate(weekEnd)}
        />
      ))}
    </div>
  );
};

export default PrintableReceipts;
