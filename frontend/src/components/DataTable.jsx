import React from 'react';

export default function DataTable({ data, columns }) {
  if (!data || data.length === 0) return <div className="empty-state" style={{padding: '20px', color: '#94a3b8'}}>No data available</div>;

  const displayCols = columns.slice(0, 5);

  return (
    <div className="table-container">
      <table className="data-table">
        <thead>
          <tr>
            <th style={{ width: '40px' }}>#</th>
            {displayCols.map(col => (
               <th key={col}>{col.replace(/_/g, ' ')}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, index) => (
            <tr key={index}>
              <td style={{ color: '#64748b' }}>{index + 1}</td>
              {displayCols.map(col => (
                <td key={`${index}-${col}`} className={col === displayCols[0] ? "font-bold" : ""}>
                   {typeof row[col] === 'number' 
                      ? Number(row[col]).toLocaleString(undefined, { maximumFractionDigits: 1 })
                      : String(row[col])}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
