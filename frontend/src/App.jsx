import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Database, UploadCloud, BarChart2, Hash, Layers, TrendingUp, Download, Terminal, CheckCircle2, AlertCircle, Link, Plus, Trash2, RefreshCw, Activity } from 'lucide-react';
import { BarChart, Bar, LineChart, Line, AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend } from 'recharts';
import KPICard from './components/KPICard';
import DataTable from './components/DataTable';

function App() {
  const [dataPayload, setDataPayload] = useState({ entity: [], time: [] });
  const [status, setStatus] = useState({ phase: 'Idle', message: 'Awaiting dataset...', progress: 0 });
  const [logs, setLogs] = useState("");
  const [sources, setSources] = useState([]);
  const [newSource, setNewSource] = useState({ name: '', url: '' });
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('dashboard');
  const fileInputRef = useRef(null);
  const logRef = useRef(null);

  const fetchMetrics = async () => {
    try {
      const { data } = await axios.get('http://localhost:8000/api/metrics');
      if (data.error) throw new Error(data.error);
      setDataPayload(data);
      setError(null);
    } catch (err) {
      if (dataPayload.entity.length === 0) setError(err.message || 'Data unavailable.');
    }
  };

  const fetchStatus = async () => {
    try {
      const { data } = await axios.get('http://localhost:8000/api/status');
      setStatus(data);
      if (data.phase === 'Completed') fetchMetrics();
    } catch (err) { console.error("Status error"); }
  };

  const fetchLogs = async () => {
    try {
      const { data } = await axios.get('http://localhost:8000/api/logs');
      setLogs(data.logs);
      if (logRef.current) logRef.current.scrollTop = logRef.current.scrollHeight;
    } catch (err) { console.error("Log error"); }
  };

  const fetchSources = async () => {
    try {
      const { data } = await axios.get('http://localhost:8000/api/sources');
      setSources(data);
    } catch (err) { console.error("Sources error"); }
  };

  useEffect(() => {
    fetchMetrics();
    fetchSources();
    const interval = setInterval(() => {
      fetchStatus();
      fetchLogs();
      if (activeTab === 'sources') fetchSources();
    }, 2000);
    return () => clearInterval(interval);
  }, [activeTab]);

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const formData = new FormData();
    formData.append("file", file);
    try {
       await axios.post('http://localhost:8000/api/upload', formData);
       setActiveTab('dashboard');
    } catch (err) { setError("Upload failed"); }
  };

  const addSource = async () => {
    if (!newSource.name || !newSource.url) return;
    try {
       await axios.post('http://localhost:8000/api/sources', newSource);
       setNewSource({ name: '', url: '' });
       fetchSources();
    } catch (err) { alert("Failed to add source"); }
  };

  const deleteSource = async (id) => {
    try {
       await axios.delete(`http://localhost:8000/api/sources/${id}`);
       fetchSources();
    } catch (err) { alert("Delete failed"); }
  };

  const triggerSync = async () => {
    try {
       await axios.post('http://localhost:8000/api/sources/sync');
       setActiveTab('dashboard');
    } catch (err) { alert("Sync failed"); }
  };

  const entityData = dataPayload.entity || [];
  const timeData = dataPayload.time || [];
  const columns = entityData.length > 0 ? Object.keys(entityData[0]) : [];
  const numericColumns = entityData.length > 0 ? columns.filter(col => typeof entityData[0][col] === 'number') : [];
  const labelColumn = columns.includes('entity_name') ? 'entity_name' : (columns[0] || '');

  return (
    <div className="dashboard-layout">
      <header className="dashboard-header glass-card">
        <Database className="header-icon" size={28} />
        <h1>Auto-ETL Intelligence Suite</h1>
        
        <nav className="header-nav">
           <button onClick={() => setActiveTab('dashboard')} className={activeTab === 'dashboard' ? 'active' : ''}>Dashboard</button>
           <button onClick={() => setActiveTab('sources')} className={activeTab === 'sources' ? 'active' : ''}>Data Sources</button>
        </nav>

        <div className="header-actions">
          <input type="file" style={{ display: 'none' }} ref={fileInputRef} onChange={handleFileUpload} />
          <button onClick={() => fileInputRef.current.click()} className="upload-btn">
             <UploadCloud size={18} /> Ingest Local
          </button>
          
          <div className="download-group">
            <button onClick={() => {
                navigator.clipboard.writeText('http://localhost:8000/api/pbi');
                alert('Power BI Direct Link copied!');
            }} className="icon-btn" title="Power BI Sync"><Link size={18} /></button>
            <a href="http://localhost:8000/api/download/csv" className="icon-btn" title="CSV"><Download size={18} /></a>
          </div>
        </div>
      </header>

      {status.phase !== 'Idle' && status.phase !== 'Completed' && (
        <section className="status-tracker glass-card">
           <div className="tracker-header">
              <span className="phase-badge">{status.phase}</span>
              <p>{status.message}</p>
              <span className="progress-pct">{status.progress}%</span>
           </div>
           <div className="progress-bar"><div className="progress-fill" style={{ width: `${status.progress}%` }}></div></div>
        </section>
      )}
      
      <main className="dashboard-content">
        {activeTab === 'dashboard' ? (
          <>
            {entityData.length > 0 ? (
              <>
                <section className="kpi-grid">
                  {numericColumns.slice(0, 4).map((col, idx) => (
                    <KPICard 
                       key={idx} 
                       title={`Total ${col.replace(/_/g, ' ')}`} 
                       value={entityData.reduce((acc, row) => acc + (row[col] || 0), 0).toLocaleString()} 
                       icon={idx % 2 === 0 ? Activity : TrendingUp} 
                    />
                  ))}
                </section>

                <section className="bento-grid">
                   <div className="chart-container glass-card" style={{ gridColumn: '1 / -1' }}>
                      <h2>Temporal Progression Vectors</h2>
                      <div className="chart-wrapper">
                         <ResponsiveContainer width="100%" height={300}>
                            <AreaChart data={timeData}>
                               <defs><linearGradient id="colorMetric" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#38bdf8" stopOpacity={0.3}/><stop offset="95%" stopColor="#38bdf8" stopOpacity={0}/></linearGradient></defs>
                               <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" vertical={false} />
                               <XAxis dataKey="time_period" stroke="#64748b" tick={{fontSize: 10}} minTickGap={40} />
                               <YAxis stroke="#64748b" tick={{fontSize: 10}} />
                               <Tooltip contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #1e293b' }} />
                               <Area type="monotone" dataKey={numericColumns[0]} stroke="#38bdf8" fill="url(#colorMetric)" strokeWidth={2} />
                            </AreaChart>
                         </ResponsiveContainer>
                      </div>
                   </div>

                   <div className="chart-container glass-card">
                      <h2>Top Contributors</h2>
                      <div className="chart-wrapper">
                         <ResponsiveContainer width="100%" height={350}>
                            <BarChart data={entityData.slice(0, 10)} layout="vertical">
                               <XAxis type="number" hide /><YAxis type="category" dataKey={labelColumn} stroke="#94a3b8" tick={{fontSize: 11}} width={100} />
                               <Tooltip cursor={{fill: '#ffffff05'}} contentStyle={{backgroundColor: '#0f172a'}} />
                               <Bar dataKey={numericColumns[0]} fill="#38bdf8" radius={[0, 4, 4, 0]} />
                            </BarChart>
                         </ResponsiveContainer>
                      </div>
                   </div>

                   <div className="table-wrapper glass-card"><DataTable data={entityData} columns={columns} /></div>

                   <div className="log-viewer glass-card" style={{ gridColumn: '1 / -1' }}>
                      <div className="log-header"><Terminal size={14} /> <span>Pipeline Records</span><div className="status-dot"></div></div>
                      <pre ref={logRef}>{logs || "Trace stream initializing..."}</pre>
                   </div>
                </section>
              </>
            ) : (
              <div className="glass-card error-hero"><AlertCircle size={48} color="#ef4444" /><h2>Standby</h2><p>{error || "Awaiting dataset ingestion..."}</p></div>
            )}
          </>
        ) : (
          <section className="sources-container">
             <div className="source-form glass-card">
                <h3>Link New Public Source</h3>
                <div className="form-row">
                   <input placeholder="Source Name (e.g., OWID COVID)" value={newSource.name} onChange={e => setNewSource({...newSource, name: e.target.value})} />
                   <input placeholder="CSV direct URL" value={newSource.url} onChange={e => setNewSource({...newSource, url: e.target.value})} />
                   <button onClick={addSource} className="upload-btn"><Plus size={18} /> Link Source</button>
                </div>
             </div>

             <div className="sources-list-container glass-card">
                <div className="list-header">
                   <h3>Linked Registries</h3>
                   <button onClick={triggerSync} className="upload-btn accent"><RefreshCw size={18} /> Global Sync Now</button>
                </div>
                <table className="sources-table">
                   <thead><tr><th>Source Name</th><th>Endpoint URL</th><th>Last Sync</th><th>Status</th><th>Actions</th></tr></thead>
                   <tbody>
                      {sources.map(s => (
                        <tr key={s.id}>
                           <td className="font-bold">{s.name}</td>
                           <td className="url-cell">{s.url}</td>
                           <td>{s.last_sync}</td>
                           <td><span className={`badge ${s.status === 'Success' ? 'success' : ''}`}>{s.status}</span></td>
                           <td><button onClick={() => deleteSource(s.id)} className="icon-btn danger"><Trash2 size={16} /></button></td>
                        </tr>
                      ))}
                   </tbody>
                </table>
             </div>
          </section>
        )}
      </main>
    </div>
  );
}

export default App;
