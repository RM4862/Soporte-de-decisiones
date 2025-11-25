import { ArrowUpRight, ArrowDownRight, Users, DollarSign, TrendingUp, AlertCircle } from 'lucide-react'
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

const kpiData = [
  { title: 'Proyectos Activos', value: '12', change: '+15%', trend: 'up', icon: TrendingUp },
  { title: 'Ingresos Mensuales', value: '$45,230', change: '+23%', trend: 'up', icon: DollarSign },
  { title: 'Clientes Satisfechos', value: '94%', change: '+5%', trend: 'up', icon: Users },
  { title: 'Defectos Críticos', value: '3', change: '-12%', trend: 'down', icon: AlertCircle },
]

const projectsData = [
  { name: 'Ene', proyectos: 8, completados: 6 },
  { name: 'Feb', proyectos: 10, completados: 7 },
  { name: 'Mar', proyectos: 12, completados: 9 },
  { name: 'Abr', proyectos: 11, completados: 10 },
  { name: 'May', proyectos: 13, completados: 11 },
  { name: 'Jun', proyectos: 12, completados: 10 },
]

const defectsData = [
  { name: 'Críticos', value: 3, color: '#ef4444' },
  { name: 'Mayores', value: 8, color: '#f59e0b' },
  { name: 'Menores', value: 15, color: '#10b981' },
  { name: 'Triviales', value: 24, color: '#6366f1' },
]

export default function Dashboard() {
  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Dashboard Principal</h2>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Resumen ejecutivo de los indicadores clave de desempeño
        </p>
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
            Proyectos por Mes
          </h3>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={projectsData}>
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
            Distribución de Defectos
          </h3>
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie
                data={defectsData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {defectsData.map((entry, index) => (
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
              <tr>
                <td className="px-4 py-3 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                  Sistema ERP Manufactura
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400 hidden sm:table-cell">
                  Industrias ABC
                </td>
                <td className="px-4 py-3 whitespace-nowrap">
                  <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                    En Desarrollo
                  </span>
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400 hidden md:table-cell">
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div className="bg-primary-600 h-2 rounded-full" style={{ width: '75%' }}></div>
                  </div>
                </td>
              </tr>
              <tr>
                <td className="px-4 py-3 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                  App Móvil E-Commerce
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400 hidden sm:table-cell">
                  Comercial XYZ
                </td>
                <td className="px-4 py-3 whitespace-nowrap">
                  <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                    Testing
                  </span>
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400 hidden md:table-cell">
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div className="bg-primary-600 h-2 rounded-full" style={{ width: '90%' }}></div>
                  </div>
                </td>
              </tr>
              <tr>
                <td className="px-4 py-3 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                  Portal de Gestión Académica
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400 hidden sm:table-cell">
                  Universidad DEF
                </td>
                <td className="px-4 py-3 whitespace-nowrap">
                  <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-yellow-100 text-yellow-800">
                    Planificación
                  </span>
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400 hidden md:table-cell">
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div className="bg-primary-600 h-2 rounded-full" style={{ width: '25%' }}></div>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
