import { useState, useEffect } from 'react'
import { Filter, Download, RefreshCw, AlertCircle } from 'lucide-react'
import { 
  BarChart, Bar, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell 
} from 'recharts'

export default function OLAPDashboard() {
  const [selectedDimension, setSelectedDimension] = useState('cliente')
  const [selectedMetric, setSelectedMetric] = useState('ingresos')
  const [selectedPeriod, setSelectedPeriod] = useState('all')
  const [chartData, setChartData] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const dimensions = [
    { id: 'cliente', label: 'Dimensión Cliente' },
    { id: 'tiempo', label: 'Dimensión Temporal' },
    { id: 'etapa', label: 'Dimensión Etapa (Calidad)' },
    { id: 'tecnologia', label: 'Dimensión Tecnológica' },
  ]
  const metrics = [
    { id: 'ingresos', label: 'Ingresos ($)' },
    { id: 'cantidad', label: 'Cantidad Proyectos' },
    { id: 'defectos', label: 'Defectos' },
  ]
  const periods = [
    { id: 'all', label: 'Histórico Completo' },
    { id: '2025', label: 'Año 2025' }, // Ajusta según tus datos generados
    { id: '2024', label: 'Año 2024' },
    { id: '2023', label: 'Año 2023' },
  ]

  const fetchData = async () => {
    setLoading(true); setError(null);
    try {
      const params = new URLSearchParams({ dimension: selectedDimension, metric: selectedMetric, year: selectedPeriod })
      const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000'
      const res = await fetch(`${API_URL}/api/olap/cube?${params}`)
      if (!res.ok) throw new Error('Error API')
      const data = await res.json()
      setChartData(data)
    } catch (err) { setError('Error conectando al backend'); setChartData([]) }
    finally { setLoading(false) }
  }

  useEffect(() => { fetchData() }, [])

  const getXKey = () => {
    if (selectedDimension === 'tiempo') return 'periodo'
    if (selectedDimension === 'etapa') return 'etapa'
    if (selectedDimension === 'tecnologia') return 'tecnologia'
    return 'label'
  }
  
  const formatValue = (val) => selectedMetric === 'ingresos' ? `$${Number(val).toLocaleString()}` : Number(val).toLocaleString()

  return (
    <div className="space-y-4 p-2">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">OLAP Analytics</h2>
        <div className="flex space-x-2">
          <button onClick={fetchData} className="bg-gray-700 hover:bg-gray-600 text-white px-4 py-2 rounded flex items-center">
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} /> Actualizar
          </button>
        </div>
      </div>

      <div className="bg-gray-800 p-4 rounded-lg border border-gray-700">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="text-xs text-gray-400">Dimensión</label>
            <select value={selectedDimension} onChange={e => setSelectedDimension(e.target.value)} className="w-full bg-gray-700 text-white rounded p-2 border border-gray-600">
              {dimensions.map(d => <option key={d.id} value={d.id}>{d.label}</option>)}
            </select>
          </div>
          <div>
            <label className="text-xs text-gray-400">Métrica</label>
            <select value={selectedMetric} onChange={e => setSelectedMetric(e.target.value)} className="w-full bg-gray-700 text-white rounded p-2 border border-gray-600">
              {metrics.map(m => <option key={m.id} value={m.id}>{m.label}</option>)}
            </select>
          </div>
          <div>
            <label className="text-xs text-gray-400">Periodo</label>
            <select value={selectedPeriod} onChange={e => setSelectedPeriod(e.target.value)} className="w-full bg-gray-700 text-white rounded p-2 border border-gray-600">
              {periods.map(p => <option key={p.id} value={p.id}>{p.label}</option>)}
            </select>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* GRÁFICO PRINCIPAL */}
        <div className="bg-gray-800 p-4 rounded-lg border border-gray-700">
          <h3 className="text-white text-sm font-bold mb-4">Distribución Principal</h3>
          <div className="h-64">
            <ResponsiveContainer>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey={getXKey()} stroke="#9CA3AF" fontSize={11} />
                <YAxis stroke="#9CA3AF" fontSize={11} tickFormatter={val => val >= 1000 ? `${val/1000}k` : val}/>
                <Tooltip contentStyle={{backgroundColor: '#1F2937'}} formatter={(val) => formatValue(val)} />
                <Bar dataKey="value" fill="#3B82F6" radius={[4,4,0,0]}>
                   {chartData.map((e, i) => <Cell key={i} fill={selectedDimension==='etapa' && (i===2||i===3) ? '#10B981' : '#3B82F6'} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* GRÁFICO SECUNDARIO */}
        <div className="bg-gray-800 p-4 rounded-lg border border-gray-700">
          <h3 className="text-white text-sm font-bold mb-4">Comparativo / Tendencia</h3>
          <div className="h-64">
            <ResponsiveContainer>
              {selectedDimension === 'tiempo' ? (
                <AreaChart data={chartData}>
                  <defs>
                    <linearGradient id="colorV" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#8B5CF6" stopOpacity={0.8}/><stop offset="95%" stopColor="#8B5CF6" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis dataKey="periodo" stroke="#9CA3AF" fontSize={11} />
                  <YAxis stroke="#9CA3AF" fontSize={11} />
                  <Tooltip contentStyle={{backgroundColor: '#1F2937'}} />
                  <Area type="monotone" dataKey="value" stroke="#8B5CF6" fill="url(#colorV)" />
                </AreaChart>
              ) : (
                <BarChart data={chartData} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" horizontal={true} vertical={false}/>
                  <XAxis type="number" hide />
                  <YAxis dataKey={getXKey()} type="category" stroke="#9CA3AF" width={120} fontSize={10} />
                  <Tooltip contentStyle={{backgroundColor: '#1F2937'}} />
                  {/* AQUÍ ESTABA EL ERROR: Ahora usamos 'value' o 'ingresos' dinámicamente */}
                  <Bar dataKey={selectedMetric === 'cantidad' ? 'ingresos' : 'value'} fill="#10B981" radius={[0,4,4,0]} barSize={15} name="Comparativo" />
                </BarChart>
              )}
            </ResponsiveContainer>
          </div>
        </div>
      </div>
      
      {/* TABLA DRILL DOWN */}
      <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-x-auto">
        <table className="min-w-full text-sm text-gray-400">
          <thead className="bg-gray-700 text-gray-200">
            <tr>
              <th className="p-3 text-left">Dimensión</th>
              <th className="p-3 text-right">Valor Princ.</th>
              <th className="p-3 text-right">Proyectos</th>
              <th className="p-3 text-right">Ingresos</th>
            </tr>
          </thead>
          <tbody>
            {chartData.map((row, i) => (
              <tr key={i} className="border-t border-gray-700 hover:bg-gray-700/50">
                <td className="p-3 text-white">{row[getXKey()] || row.label}</td>
                <td className="p-3 text-right font-bold text-blue-400">{formatValue(row.value)}</td>
                <td className="p-3 text-right">{row.proyectos || 0}</td>
                <td className="p-3 text-right text-green-400">${Number(row.ingresos||0).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}