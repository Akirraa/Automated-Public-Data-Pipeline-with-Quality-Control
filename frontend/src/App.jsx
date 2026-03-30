import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Database, UploadCloud, BarChart2, Hash, Layers, TrendingUp } from 'lucide-react';
import { BarChart, Bar, LineChart, Line, AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend } from 'recharts';
import KPICard from './components/KPICard';
import DataTable from './components/DataTable';

function App() {
  const [dataPayload, setDataPayload] = useState({ entity: [], time: [] });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [uploadStatus, setUploadStatus] = useState("");
  const fileInputRef = useRef(null);

  const fetchMetrics = async () => {
    try {
      setLoading(true);
      const response = await axios.get('http://localhost:8000/api/metrics');
      if (response.data.error) throw new Error(response.data.error);
      setDataPayload(response.data);
      setError(null);
    } catch (err) {
      if (dataPayload.entity.length === 0) setError(err.message || 'No data generated. Please upload a dataset.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMetrics();
  }, []);

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setUploadStatus("Uploading & Triggering Auto-ETL...");
    const formData = new FormData();
    formData.append("file", file);

    try {
      await axios.post('http://localhost:8000/api/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setUploadStatus("Processing Models... Generating Temporal AI Forecast in 8s.");
      
      setTimeout(() => {
         fetchMetrics();
         setUploadStatus("");
      }, 8000);

    } catch (err) {
      setUploadStatus("");
      setError("Failed to upload file.");
    }
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const entityData = dataPayload.entity || [];
  const timeData = dataPayload.time || [];

  const columns = entityData.length > 0 ? Object.keys(entityData[0]) : [];
  const numericColumns = entityData.length > 0 ? columns.filter(col => typeof entityData[0][col] === 'number') : [];
  const labelColumn = columns.includes('entity_name') ? 'entity_name' : (columns[0] || '');

  // Calculate dynamic KPIs representing whole dataset scale
  const kpis = numericColumns.slice(0, 4).map(numCol => {
    const total = entityData.reduce((acc, row) => acc + (row[numCol] || 0), 0);
    return { name: numCol, value: total };
  });

  return (
    <div className="dashboard-layout">
      <header className="dashboard-header glass-card" style={{ display: 'flex', flexWrap: 'wrap', gap: '20px' }}>
        <Database className="header-icon" size={28} />
        <h1>Executive BI Platform & Flow Forensics</h1>
        
        <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: '15px' }}>
          <input 
            type="file" 
            accept=".csv" 
            style={{ display: 'none' }} 
            ref={fileInputRef}
            onChange={handleFileUpload} 
          />
          <button 
             onClick={() => fileInputRef.current.click()}
             style={{ padding: '10px 20px', borderRadius: '8px', background: 'rgba(56, 189, 248, 0.2)', border: '1px solid rgba(56, 189, 248, 0.4)', color: '#38bdf8', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 'bold', transition: 'all 0.3s' }}
          >
             <UploadCloud size={20} /> Deploy Dataset
          </button>
          
          {uploadStatus && <span style={{ color: '#38bdf8', fontSize: '0.85rem' }}>{uploadStatus}</span>}
          {loading && <span className="badge">SYNCING METRICS</span>}
        </div>
      </header>
      
      <main className="dashboard-content">
        {error && !loading && entityData.length === 0 && (
           <div className="glass-card" style={{ padding: '30px', textAlign: 'center', color: '#94a3b8' }}>
              <Layers size={48} style={{ marginBottom: '15px', color: '#1e293b' }}/>
              <h2>Awaiting Telemetry Architecture</h2>
              <p>{error}</p>
           </div>
        )}

        {entityData.length > 0 && (
          <>
            <section className="kpi-grid">
              {kpis.map((kpi, idx) => (
                <KPICard 
                   key={idx} 
                   title={`Total ${kpi.name.replace(/_/g, ' ')}`} 
                   value={Number(kpi.value.toFixed(1)).toLocaleString()} 
                   icon={idx % 2 === 0 ? BarChart2 : TrendingUp} 
                />
              ))}
            </section>

            <section className="bento-grid">
            {timeData.length > 0 && (
               <div className="chart-container glass-card" style={{ gridColumn: '1 / -1', minHeight: '340px' }}>
                 <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0'}}>
                    <h2>Progression Over Time</h2>
                    <span style={{fontSize: '0.75rem', color: '#94a3b8'}}>Temporal Representation</span>
                 </div>
                 <div className="chart-wrapper">
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart data={timeData} margin={{ top: 15, right: 20, left: 0, bottom: 0 }}>
                        <defs>
                           <linearGradient id="colorMetric" x1="0" y1="0" x2="0" y2="1">
                             <stop offset="5%" stopColor="#38bdf8" stopOpacity={0.4}/>
                             <stop offset="95%" stopColor="#38bdf8" stopOpacity={0}/>
                           </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" vertical={false} />
                        <XAxis dataKey="time_period" stroke="#64748b" tick={{fill: '#64748b', fontSize: 11}} minTickGap={30} />
                        <YAxis stroke="#64748b" tick={{fill: '#64748b', fontSize: 11}} width={90} />
                        <Tooltip 
                          contentStyle={{ backgroundColor: 'rgba(15, 23, 42, 0.95)', border: '1px solid rgba(255, 255, 255, 0.1)', borderRadius: '8px', color: '#fff', fontSize: '12px' }}
                          itemStyle={{ color: '#38bdf8' }}
                        />
                        <Legend wrapperStyle={{ fontSize: '12px' }}/>
                        {numericColumns.slice(0, 1).map((col) => (
                          <Area key={col} type="monotone" dataKey={col} stroke="#38bdf8" strokeWidth={2} fillOpacity={1} fill="url(#colorMetric)" />
                        ))}
                        {numericColumns.slice(1, 2).map((col) => (
                          <Area key={col} type="monotone" dataKey={col} stroke="#818cf8" strokeWidth={1.5} fillOpacity={0} />
                        ))}
                      </AreaChart>
                    </ResponsiveContainer>
                 </div>
               </div>
            )}

              <div className="chart-container glass-card" style={{ minHeight: '380px' }}>
                <h2>Top Contributors</h2>
                <div className="chart-wrapper">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={entityData.slice(0, 10)} margin={{ top: 10, right: 10, left: -20, bottom: 0 }} layout="vertical">
                      <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" horizontal={false} />
                      <XAxis type="number" stroke="#64748b" tick={{fill: '#64748b', fontSize: 11}} />
                      <YAxis type="category" dataKey={labelColumn} stroke="#e2e8f0" tick={{fill: '#e2e8f0', fontSize: 11}} width={100} />
                      <Tooltip 
                        contentStyle={{ backgroundColor: 'rgba(15, 23, 42, 0.95)', border: '1px solid rgba(255, 255, 255, 0.1)', borderRadius: '8px', color: '#fff', fontSize: '12px' }}
                        itemStyle={{ color: '#38bdf8' }}
                      />
                      {numericColumns.slice(0, 2).map((col, i) => (
                        <Bar key={col} dataKey={col} fill={i === 0 ? "#38bdf8" : "#818cf8"} radius={[0, 4, 4, 0]} barSize={16} />
                      ))}
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              <div className="table-wrapper glass-card">
                 <DataTable data={entityData} columns={columns} />
              </div>
            </section>
          </>
        )}
      </main>
    </div>
  );
}

export default App;
