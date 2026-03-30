import React from 'react';

export default function KPICard({ title, value, icon: Icon, trend }) {
  return (
    <div className="glass-card kpi-card">
      <div className="kpi-header">
        <h3 className="kpi-title">{title}</h3>
        {Icon && <Icon className="kpi-icon" size={20} />}
      </div>
      <div className="kpi-body">
        <span className="kpi-value">{value}</span>
        {trend && (
          <span className={`kpi-trend ${trend > 0 ? 'positive' : 'negative'}`}>
            {trend > 0 ? '+' : ''}{trend}%
          </span>
        )}
      </div>
    </div>
  );
}
