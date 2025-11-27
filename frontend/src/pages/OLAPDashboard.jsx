import { useState } from 'react'
import { Filter, Download, RefreshCw } from 'lucide-react'
import { BarChart, Bar, LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

// Datos simulados del cubo OLAP multidimensional
const timeSeriesData = [
  { periodo: 'Q1 2024', ingresos: 125000, proyectos: 8, calidad: 92, clientes: 15 },
  { periodo: 'Q2 2024', ingresos: 148000, proyectos: 12, calidad: 94, clientes: 18 },
  { periodo: 'Q3 2024', ingresos: 165000, proyectos: 15, calidad: 95, clientes: 22 },
  { periodo: 'Q4 2024', ingresos: 182000, proyectos: 18, calidad: 96, clientes: 25 },
]

const projectsByTechnology = [
  { tecnologia: 'React', proyectos: 12, horas: 2400, defectos: 8 },
  { tecnologia: 'Angular', proyectos: 8, horas: 1800, defectos: 12 },
  { tecnologia: 'Vue.js', proyectos: 6, horas: 1200, defectos: 5 },
  { tecnologia: 'Node.js', proyectos: 15, horas: 3000, defectos: 10 },
  { tecnologia: 'Python', proyectos: 10, horas: 2200, defectos: 7 },
  { tecnologia: 'Java', proyectos: 9, horas: 2500, defectos: 15 },
]

const clientSegmentation = [
  { segmento: 'Gobierno', proyectos: 8, valor: 85000, satisfaccion: 96 },
  { segmento: 'Educación', proyectos: 12, valor: 65000, satisfaccion: 94 },
  { segmento: 'Manufactura', proyectos: 10, valor: 95000, satisfaccion: 92 },
  { segmento: 'Servicios', proyectos: 15, valor: 75000, satisfaccion: 93 },
  { segmento: 'Retail', proyectos: 8, valor: 55000, satisfaccion: 91 },
]

const qualityMetrics = [
  { mes: 'Ene', coberturaPruebas: 85, defectosReportados: 15, tiempoResolucion: 48 },
  { mes: 'Feb', coberturaPruebas: 87, defectosReportados: 12, tiempoResolucion: 42 },
  { mes: 'Mar', coberturaPruebas: 89, defectosReportados: 10, tiempoResolucion: 38 },
  { mes: 'Abr', coberturaPruebas: 91, defectosReportados: 8, tiempoResolucion: 36 },
  { mes: 'May', coberturaPruebas: 92, defectosReportados: 7, tiempoResolucion: 32 },
  { mes: 'Jun', coberturaPruebas: 94, defectosReportados: 5, tiempoResolucion: 28 },
]

export default function OLAPDashboard() {
  const [selectedDimension, setSelectedDimension] = useState('tiempo')
  const [selectedMetric, setSelectedMetric] = useState('ingresos')

  const dimensions = [
    { id: 'tiempo', label: 'Dimensión Temporal' },
    { id: 'tecnologia', label: 'Dimensión Tecnológica' },
    { id: 'cliente', label: 'Dimensión Cliente' },
    { id: 'calidad', label: 'Dimensión Calidad' },
  ]

  const metrics = [
    { id: 'ingresos', label: 'Ingresos' },
    { id: 'proyectos', label: 'Proyectos' },
    { id: 'calidad', label: 'Índice de Calidad' },
    { id: 'eficiencia', label: 'Eficiencia Operativa' },
  ]

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">OLAP Analytics</h2>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Análisis multidimensional de KPIs mediante cubo OLAP
          </p>
        </div>
        <div className="flex space-x-2">
          <button className="btn-secondary flex items-center text-sm px-3 py-1.5">
            <RefreshCw className="h-3 w-3 mr-1" />
            Actualizar
          </button>
          <button className="btn-primary flex items-center text-sm px-3 py-1.5">
            <Download className="h-3 w-3 mr-1" />
            Exportar
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="card">
        <div className="flex items-center mb-3">
          <Filter className="h-4 w-4 text-gray-500 mr-2" />
          <h3 className="text-base font-semibold text-gray-900 dark:text-white">
            Configuración de Análisis OLAP
          </h3>
        </div>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
          <div>
            <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
              Dimensión de Análisis
            </label>
            <select
              value={selectedDimension}
              onChange={(e) => setSelectedDimension(e.target.value)}
              className="w-full px-2 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
            >
              {dimensions.map((dim) => (
                <option key={dim.id} value={dim.id}>
                  {dim.label}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
              Métrica Principal
            </label>
            <select
              value={selectedMetric}
              onChange={(e) => setSelectedMetric(e.target.value)}
              className="w-full px-2 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
            >
              {metrics.map((metric) => (
                <option key={metric.id} value={metric.id}>
                  {metric.label}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
              Período
            </label>
            <select className="w-full px-2 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500">
              <option>Último Trimestre</option>
              <option>Último Semestre</option>
              <option>Último Año</option>
              <option>Todo el Período</option>
            </select>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
              Agregación
            </label>
            <select className="w-full px-2 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500">
              <option>Suma</option>
              <option>Promedio</option>
              <option>Máximo</option>
              <option>Mínimo</option>
            </select>
          </div>
        </div>
      </div>

      {/* Dimensión Temporal */}
      {selectedDimension === 'tiempo' && (
        <>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div className="card">
              <h3 className="text-base font-semibold text-gray-900 dark:text-white mb-3">
                Evolución de Ingresos y Proyectos
              </h3>
              <ResponsiveContainer width="100%" height={220}>
                <AreaChart data={timeSeriesData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="periodo" />
                  <YAxis yAxisId="left" />
                  <YAxis yAxisId="right" orientation="right" />
                  <Tooltip />
                  <Legend />
                  <Area yAxisId="left" type="monotone" dataKey="ingresos" stroke="#0ea5e9" fill="#0ea5e9" fillOpacity={0.6} name="Ingresos ($)" />
                  <Area yAxisId="right" type="monotone" dataKey="proyectos" stroke="#10b981" fill="#10b981" fillOpacity={0.6} name="Proyectos" />
                </AreaChart>
              </ResponsiveContainer>
            </div>

            <div className="card">
              <h3 className="text-base font-semibold text-gray-900 dark:text-white mb-3">
                Índice de Calidad y Crecimiento de Clientes
              </h3>
              <ResponsiveContainer width="100%" height={220}>
                <LineChart data={timeSeriesData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="periodo" />
                  <YAxis yAxisId="left" />
                  <YAxis yAxisId="right" orientation="right" />
                  <Tooltip />
                  <Legend />
                  <Line yAxisId="left" type="monotone" dataKey="calidad" stroke="#8b5cf6" strokeWidth={2} name="Calidad (%)" />
                  <Line yAxisId="right" type="monotone" dataKey="clientes" stroke="#f59e0b" strokeWidth={2} name="Clientes" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </>
      )}

      {/* Dimensión Tecnológica */}
      {selectedDimension === 'tecnologia' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <div className="card">
            <h3 className="text-base font-semibold text-gray-900 dark:text-white mb-3">
              Proyectos por Tecnología
            </h3>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={projectsByTechnology} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis dataKey="tecnologia" type="category" width={80} />
                <Tooltip />
                <Legend />
                <Bar dataKey="proyectos" fill="#0ea5e9" name="Proyectos" />
                <Bar dataKey="defectos" fill="#ef4444" name="Defectos" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="card">
            <h3 className="text-base font-semibold text-gray-900 dark:text-white mb-3">
              Horas Invertidas por Tecnología
            </h3>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={projectsByTechnology}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="tecnologia" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="horas" fill="#10b981" name="Horas" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Dimensión Cliente */}
      {selectedDimension === 'cliente' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <div className="card">
            <h3 className="text-base font-semibold text-gray-900 dark:text-white mb-3">
              Distribución por Segmento de Cliente
            </h3>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={clientSegmentation}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="segmento" />
                <YAxis yAxisId="left" />
                <YAxis yAxisId="right" orientation="right" />
                <Tooltip />
                <Legend />
                <Bar yAxisId="left" dataKey="proyectos" fill="#0ea5e9" name="Proyectos" />
                <Bar yAxisId="right" dataKey="valor" fill="#10b981" name="Valor ($)" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="card">
            <h3 className="text-base font-semibold text-gray-900 dark:text-white mb-3">
              Satisfacción por Segmento
            </h3>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={clientSegmentation}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="segmento" />
                <YAxis domain={[80, 100]} />
                <Tooltip />
                <Legend />
                <Bar dataKey="satisfaccion" fill="#8b5cf6" name="Satisfacción (%)" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Dimensión Calidad */}
      {selectedDimension === 'calidad' && (
        <>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div className="card">
              <h3 className="text-base font-semibold text-gray-900 dark:text-white mb-3">
                Evolución de Cobertura de Pruebas
              </h3>
              <ResponsiveContainer width="100%" height={220}>
                <AreaChart data={qualityMetrics}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="mes" />
                  <YAxis domain={[80, 100]} />
                  <Tooltip />
                  <Legend />
                  <Area type="monotone" dataKey="coberturaPruebas" stroke="#10b981" fill="#10b981" fillOpacity={0.6} name="Cobertura (%)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>

            <div className="card">
              <h3 className="text-base font-semibold text-gray-900 dark:text-white mb-3">
                Defectos y Tiempo de Resolución
              </h3>
              <ResponsiveContainer width="100%" height={220}>
                <LineChart data={qualityMetrics}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="mes" />
                  <YAxis yAxisId="left" />
                  <YAxis yAxisId="right" orientation="right" />
                  <Tooltip />
                  <Legend />
                  <Line yAxisId="left" type="monotone" dataKey="defectosReportados" stroke="#ef4444" strokeWidth={2} name="Defectos" />
                  <Line yAxisId="right" type="monotone" dataKey="tiempoResolucion" stroke="#f59e0b" strokeWidth={2} name="Tiempo Resolución (hrs)" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </>
      )}

      {/* Tabla de Drill-Down */}
      <div className="card">
        <h3 className="text-base font-semibold text-gray-900 dark:text-white mb-3">
          Análisis Detallado - Drill Down
        </h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">
                  Dimensión
                </th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">
                  Proyectos
                </th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase hidden sm:table-cell">
                  Ingresos
                </th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase hidden md:table-cell">
                  Calidad
                </th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">
                  Tendencia
                </th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              <tr className="hover:bg-gray-50 dark:hover:bg-gray-700">
                <td className="px-4 py-3 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                  Q4 2024
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                  18
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400 hidden sm:table-cell">
                  $182,000
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400 hidden md:table-cell">
                  96%
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-sm">
                  <span className="text-green-600 font-medium">↑ 12%</span>
                </td>
              </tr>
              <tr className="hover:bg-gray-50 dark:hover:bg-gray-700">
                <td className="px-4 py-3 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                  React
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                  12
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400 hidden sm:table-cell">
                  $85,000
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400 hidden md:table-cell">
                  94%
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-sm">
                  <span className="text-green-600 font-medium">↑ 8%</span>
                </td>
              </tr>
              <tr className="hover:bg-gray-50 dark:hover:bg-gray-700">
                <td className="px-4 py-3 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                  Manufactura
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                  10
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400 hidden sm:table-cell">
                  $95,000
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400 hidden md:table-cell">
                  92%
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-sm">
                  <span className="text-green-600 font-medium">↑ 5%</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Insights */}
      <div className="card bg-primary-50 dark:bg-primary-900/20 border-l-4 border-primary-600">
        <h3 className="text-base font-semibold text-primary-900 dark:text-primary-100 mb-2">
          Insights del Análisis OLAP
        </h3>
        <ul className="space-y-1.5 text-xs text-primary-800 dark:text-primary-200">
          <li>• Los ingresos han crecido un 45% en el último año, impulsados principalmente por proyectos en el sector manufactura</li>
          <li>• La tecnología React muestra la mejor relación calidad/defectos con un promedio de 0.67 defectos por proyecto</li>
          <li>• El segmento de Gobierno presenta la mayor satisfacción (96%) pero requiere más tiempo de desarrollo</li>
          <li>• La cobertura de pruebas ha mejorado 9 puntos porcentuales, correlacionando con una reducción del 67% en defectos críticos</li>
        </ul>
      </div>
    </div>
  )
}
