import { useState, useEffect } from 'react'
import { ArrowUpRight, ArrowDownRight, Users, DollarSign, TrendingUp, AlertCircle, RefreshCw } from 'lucide-react'
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

const API_URL = 'http://localhost:5000'

export default function Dashboard() {
  const [dashboardData, setDashboardData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch(`${API_URL}/api/dashboard/summary`)
      if (!response.ok) throw new Error('Error al cargar datos del dashboard')
      const data = await response.json()
      setDashboardData(data)
    } catch (err) {
      setError(err.message)
      console.error('Error fetching dashboard:', err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="animate-spin h-8 w-8 border-4 border-primary-600 border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-sm text-gray-600 dark:text-gray-400">Cargando datos del dashboard...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="card bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <AlertCircle className="h-5 w-5 text-red-600 mr-2" />
            <p className="text-sm text-red-800 dark:text-red-200">{error}</p>
          </div>
          <button onClick={fetchDashboardData} className="btn-primary text-sm">
            <RefreshCw className="h-4 w-4 mr-1" />
            Reintentar
          </button>
        </div>
      </div>
    )
  }

  if (!dashboardData) return null

  const kpiData = [
    { 
      title: 'Proyectos Activos', 
      value: dashboardData.kpis.proyectos_activos.value, 
      change: `${dashboardData.kpis.proyectos_activos.change >= 0 ? '+' : ''}${dashboardData.kpis.proyectos_activos.change}%`, 
      trend: dashboardData.kpis.proyectos_activos.trend, 
      icon: TrendingUp 
    },
    { 
      title: 'Ingresos Mensuales', 
      value: `$${(dashboardData.kpis.ingresos_mensuales.value / 1000).toFixed(1)}K`, 
      change: `${dashboardData.kpis.ingresos_mensuales.change >= 0 ? '+' : ''}${dashboardData.kpis.ingresos_mensuales.change}%`, 
      trend: dashboardData.kpis.ingresos_mensuales.trend, 
      icon: DollarSign 
    },
    { 
      title: 'Clientes Satisfechos', 
      value: `${dashboardData.kpis.satisfaccion.value}%`, 
      change: `+${dashboardData.kpis.satisfaccion.change}%`, 
      trend: dashboardData.kpis.satisfaccion.trend, 
      icon: Users 
    },
    { 
      title: 'Defectos Críticos', 
      value: dashboardData.kpis.defectos_criticos.value, 
      change: `${dashboardData.kpis.defectos_criticos.change >= 0 ? '+' : ''}${dashboardData.kpis.defectos_criticos.change}%`, 
      trend: dashboardData.kpis.defectos_criticos.trend, 
      icon: AlertCircle 
    },
  ]
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Dashboard Principal</h2>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Resumen ejecutivo de los indicadores clave de desempeño
          </p>
        </div>
        <button onClick={fetchDashboardData} className="btn-secondary text-sm" disabled={loading}>
          <RefreshCw className={`h-4 w-4 mr-1 ${loading ? 'animate-spin' : ''}`} />
          Actualizar
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        {kpiData.map((kpi) => (
          <div key={kpi.title} className="card">
            <div className="flex items-center justify-between">
              <div className="min-w-0 flex-1">
                <p className="text-xs font-medium text-gray-600 dark:text-gray-400 truncate">{kpi.title}</p>
                <p className="mt-1 text-2xl font-semibold text-gray-900 dark:text-white">{kpi.value}</p>
              </div>
              <div className={`p-2 rounded-full ${kpi.trend === 'up' ? 'bg-green-100' : 'bg-red-100'}`}>
                <kpi.icon className={`h-5 w-5 ${kpi.trend === 'up' ? 'text-green-600' : 'text-red-600'}`} />
              </div>
            </div>
            <div className="mt-2 flex items-center">
              {kpi.trend === 'up' ? (
                <ArrowUpRight className="h-3 w-3 text-green-500" />
              ) : (
                <ArrowDownRight className="h-3 w-3 text-red-500" />
              )}
              <span className={`ml-1 text-xs font-medium ${kpi.trend === 'up' ? 'text-green-600' : 'text-red-600'}`}>
                {kpi.change}
              </span>
              <span className="ml-1 text-xs text-gray-500 hidden sm:inline">vs mes anterior</span>
            </div>
          </div>
        ))}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="card">
          <h3 className="text-base font-semibold text-gray-900 dark:text-white mb-3">
            Proyectos por Mes (Últimos 6 meses)
          </h3>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={dashboardData.proyectos_mes}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="proyectos" fill="#0ea5e9" name="Proyectos Iniciados" />
              <Bar dataKey="completados" fill="#10b981" name="Proyectos Completados" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <h3 className="text-base font-semibold text-gray-900 dark:text-white mb-3">
            Distribución de Defectos Activos
          </h3>
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie
                data={dashboardData.defectos_severidad}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {dashboardData.defectos_severidad.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Recent Projects Table */}
      <div className="card">
        <h3 className="text-base font-semibold text-gray-900 dark:text-white mb-3">
          Proyectos Recientes
        </h3>
        <div className="overflow-x-auto -mx-4 sm:mx-0">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Proyecto
                </th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider hidden sm:table-cell">
                  Cliente
                </th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Estado
                </th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider hidden md:table-cell">
                  Progreso
                </th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              {dashboardData.proyectos_recientes.map((proyecto, idx) => {
                const estadoColors = {
                  'Completado': 'bg-green-100 text-green-800',
                  'En Desarrollo': 'bg-blue-100 text-blue-800',
                  'Testing': 'bg-purple-100 text-purple-800',
                  'En Progreso': 'bg-blue-100 text-blue-800',
                  'Planificación': 'bg-yellow-100 text-yellow-800',
                  'Cancelado': 'bg-red-100 text-red-800'
                }
                return (
                  <tr key={idx}>
                    <td className="px-4 py-3 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                      {proyecto.proyecto}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400 hidden sm:table-cell">
                      {proyecto.cliente}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${estadoColors[proyecto.estado] || 'bg-gray-100 text-gray-800'}`}>
                        {proyecto.estado}
                      </span>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400 hidden md:table-cell">
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div className="bg-primary-600 h-2 rounded-full" style={{ width: `${proyecto.progreso}%` }}></div>
                      </div>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
