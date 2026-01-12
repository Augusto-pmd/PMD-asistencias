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

const Receipt = ({ receiptNumber, employeeName, amount, weekStart, weekEnd, grossSalary, lateDiscount, advances, netPayment, isContractor, project }) => {
  const today = new Date().toLocaleDateString('es-AR', { 
    day: '2-digit', 
    month: '2-digit', 
    year: 'numeric' 
  });

  const amountInWords = numberToWords(netPayment);
  const personType = isContractor ? 'contratista' : 'empleado';
  const conceptText = isContractor 
    ? `Certificación semanal - Obra: ${project || 'Sin asignar'} - Semana del ${weekStart} al ${weekEnd}`
    : `Pago de salarios - Semana del ${weekStart} al ${weekEnd}`;

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
            <span className="value underline">{formatCurrency(netPayment)}</span>
          </div>

          <div className="receipt-line">
            <span className="label">En letras:</span>
            <span className="value underline uppercase">{amountInWords} PESOS</span>
          </div>

          <div className="receipt-line">
            <span className="label">En concepto de:</span>
            <span className="value underline">{conceptText}</span>
          </div>

          <div className="receipt-breakdown">
            <div className="breakdown-title">{isContractor ? 'Detalle de certificación:' : 'Liquidación del período:'}</div>
            <div className="breakdown-item">
              <span>{isContractor ? 'Monto certificado:' : 'Salario bruto:'}</span>
              <span>{formatCurrency(grossSalary)}</span>
            </div>
            {!isContractor && lateDiscount > 0 && (
              <div className="breakdown-item deduction">
                <span>Descuento por tardanzas:</span>
                <span>- {formatCurrency(lateDiscount)}</span>
              </div>
            )}
            {!isContractor && advances && advances.length > 0 && (
              <>
                <div className="breakdown-subtitle">Adelantos descontados:</div>
                {advances.map((advance, idx) => (
                  <div key={idx} className="breakdown-item deduction">
                    <span>• {advance.date} {advance.description ? `(${advance.description})` : ''}</span>
                    <span>- {formatCurrency(advance.amount)}</span>
                  </div>
                ))}
              </>
            )}
            <div className="breakdown-total">
              <span>Total a cobrar:</span>
              <span>{formatCurrency(netPayment)}</span>
            </div>
          </div>

          <div className="receipt-line full-line">
            <span className="label">En carácter de:</span>
            <span className="value underline">Pago total y definitivo</span>
          </div>
        </div>

        <div className="receipt-footer">
          <div className="signature-section">
            <div className="signature-line">_____________________________</div>
            <div className="signature-label">Firma del {personType}</div>
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
          padding: 10px;
          border: 2px solid #1e40af;
          border-radius: 4px;
          background: white;
          font-family: 'Arial', sans-serif;
        }

        .receipt-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 6px;
          padding-bottom: 6px;
          border-bottom: 2px solid #1e40af;
        }

        .company-name {
          font-size: 14px;
          font-weight: bold;
          color: #1e40af;
          letter-spacing: 1px;
        }

        .receipt-number {
          font-size: 11px;
          font-weight: bold;
          color: #475569;
        }

        .receipt-date {
          text-align: right;
          font-size: 10px;
          margin-bottom: 6px;
          color: #475569;
        }

        .receipt-body {
          margin: 10px 0;
        }

        .receipt-line {
          display: flex;
          margin-bottom: 4px;
          font-size: 10px;
          align-items: baseline;
        }

        .receipt-line.full-line {
          flex-direction: column;
        }

        .receipt-line .label {
          font-weight: 600;
          color: #334155;
          min-width: 90px;
          margin-right: 6px;
          font-size: 9px;
        }

        .receipt-line .value {
          flex: 1;
          color: #1e293b;
          font-size: 9px;
        }

        .receipt-line .underline {
          border-bottom: 1px solid #cbd5e1;
          padding-bottom: 2px;
          display: inline-block;
          min-height: 14px;
        }

        .receipt-line .uppercase {
          text-transform: uppercase;
        }

        .receipt-breakdown {
          margin: 10px 0;
          padding: 6px;
          background: #f8fafc;
          border: 1px solid #cbd5e1;
          border-radius: 4px;
        }

        .breakdown-title {
          font-weight: bold;
          font-size: 9px;
          color: #1e40af;
          margin-bottom: 4px;
          text-transform: uppercase;
        }

        .breakdown-subtitle {
          font-weight: 600;
          font-size: 8px;
          color: #475569;
          margin-top: 4px;
          margin-bottom: 2px;
        }

        .breakdown-item {
          display: flex;
          justify-content: space-between;
          font-size: 8px;
          margin-bottom: 2px;
          color: #1e293b;
        }

        .breakdown-item.deduction {
          color: #dc2626;
        }

        .breakdown-total {
          display: flex;
          justify-content: space-between;
          font-size: 9px;
          font-weight: bold;
          margin-top: 4px;
          padding-top: 4px;
          border-top: 2px solid #1e40af;
          color: #1e40af;
        }

        .receipt-footer {
          display: flex;
          justify-content: space-between;
          margin-top: 10px;
          margin-bottom: 6px;
        }

        .signature-section {
          flex: 1;
          text-align: center;
        }

        .signature-line {
          margin-bottom: 2px;
          font-size: 9px;
          color: #1e293b;
        }

        .employee-name {
          font-weight: bold;
          margin-bottom: 2px;
          font-size: 10px;
          color: #1e293b;
        }

        .signature-label {
          font-size: 8px;
          color: #64748b;
          font-style: italic;
        }

        .receipt-note {
          text-align: center;
          font-size: 8px;
          color: #64748b;
          font-style: italic;
          margin-top: 6px;
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
          grossSalary={receipt.grossSalary}
          lateDiscount={receipt.lateDiscount}
          advances={receipt.advances}
          netPayment={receipt.netPayment}
        />
      ))}
    </div>
  );
};

export default PrintableReceipts;
