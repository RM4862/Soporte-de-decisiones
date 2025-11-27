import { useState } from 'react'
import { Calculator, Lock, TrendingUp, AlertCircle, Info, FileText, Search, Database, CheckCircle, Target, Calendar, Users, Shield, BarChart2 } from 'lucide-react'
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceLine, Area, AreaChart } from 'recharts'

// Configuración del API Backend
const API_URL = 'http://localhost:5000'
const AUTH_KEY = 'changeme'

export default function PredictiveModel() {
  const [authenticated, setAuthenticated] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  
  // Filtros para buscar proyectos similares
  const [filters, setFilters] = useState({
    metodologia: '',
    horas_invertidas_min: '',
    horas_invertidas_max: '',
    presupuesto_min: '',
    presupuesto_max: '',
    duracion_dias_min: '',
    duracion_dias_max: '',
    entregables_count_min: '',
    entregables_count_max: '',
    num_tecnologias_emergentes_min: '',
    num_tecnologias_emergentes_max: '',
    estado: ['Completado']
  })
  
  const [predictionData, setPredictionData] = useState(null)

  // Simulación simple de autenticación
  const handleAuth = () => {
    const password = prompt('Ingrese contraseña de responsable de proyecto:')
    if (password === 'admin123') {
      setAuthenticated(true)
    } else {
      alert('Acceso denegado. Solo para responsables de proyecto.')
    }
  }

  const handleFilterChange = (field, value) => {
    setFilters(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const calculatePrediction = async () => {
    setLoading(true)
    setError(null)
    
    try {
      // Preparar filtros limpiando valores vacíos
      const cleanFilters = {}
      Object.keys(filters).forEach(key => {
        if (filters[key] !== '' && filters[key] !== null && filters[key] !== undefined) {
          // Convertir a números los campos numéricos
          if (key.includes('min') || key.includes('max') || key.includes('count')) {
            const numValue = Number(filters[key])
            if (!isNaN(numValue)) {
              cleanFilters[key] = numValue
            }
          } else {
            cleanFilters[key] = filters[key]
          }
        }
      })

      // Llamada al API Backend
      const response = await fetch(`${API_URL}/predict_filtered`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': AUTH_KEY
        },
        body: JSON.stringify({
          auth_key: AUTH_KEY,
          filters: cleanFilters
        })
      })

      if (!response.ok) {
        const errorData = await response.json()
        const errorMessage = errorData.error || 'Error al obtener la predicción'
        
        // Mensaje más amigable si no hay datos
        if (errorMessage.includes('No matching data')) {
          throw new Error('No se encontraron proyectos similares con esos filtros. Intenta:\n• Quitar algunos filtros para ampliar la búsqueda\n• Dejar todos los campos vacíos para usar todos los proyectos\n• Ajustar los rangos de valores')
        }
        
        throw new Error(errorMessage)
      }

      const data = await response.json()
      
      console.log('📊 Datos recibidos del API:', data)
      console.log('📊 tiempo_data existe?', !!data.tiempo_data)
      console.log('📊 tiempo_data length:', data.tiempo_data?.length)
      
      // Procesar datos para visualización
      const processedData = {
        ...data,
        // Convertir tiempo_data del API a formato de gráfico
        weeklyDistribution: data.tiempo_data ? data.tiempo_data.map(item => ({
          week: item.tiempo,
          defects: item.defectos_esperados,
          cumulative: item.defectos_acumulados
        })) : [],
        // Calcular distribución por severidad estimada
        defectDistribution: [
          { severidad: 'Críticos', cantidad: Math.round(data.expected_defects * 0.05), color: '#ef4444', porcentaje: 5 },
          { severidad: 'Mayores', cantidad: Math.round(data.expected_defects * 0.15), color: '#f59e0b', porcentaje: 15 },
          { severidad: 'Menores', cantidad: Math.round(data.expected_defects * 0.35), color: '#10b981', porcentaje: 35 },
          { severidad: 'Triviales', cantidad: Math.round(data.expected_defects * 0.45), color: '#6366f1', porcentaje: 45 },
        ],
        // Determinar nivel de riesgo
        riskLevel: data.expected_defects > 15 ? 'alto' : data.expected_defects > 8 ? 'medio' : 'bajo',
        // Calcular métricas adicionales
        peakWeek: Math.round(data.sigma * Math.sqrt(2)),
        totalDefectsEstimated: Math.round(data.expected_defects * data.duracion_semanas)
      }
      
      console.log('📊 processedData.weeklyDistribution:', processedData.weeklyDistribution)
      console.log('📊 weeklyDistribution length:', processedData.weeklyDistribution?.length)
      
      setPredictionData(processedData)
      
    } catch (err) {
      setError(err.message || 'Error al conectar con el servidor')
      console.error('Error en predicción:', err)
    } finally {
      setLoading(false)
    }
  }

  if (!authenticated) {
    return (
      <div className="flex items-center justify-center min-h-[500px]">
        <div className="card max-w-md w-full text-center">
          <div className="flex justify-center mb-4">
            <div className="p-3 bg-red-100 rounded-full">
              <Lock className="h-10 w-10 text-red-600" />
            </div>
          </div>
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
            Acceso Restringido
          </h2>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
            Esta herramienta de predicción está disponible únicamente para responsables de proyecto.
            Por favor, autentíquese para continuar.
          </p>
          <button onClick={handleAuth} className="btn-primary w-full">
            Autenticar como Responsable
          </button>
          <p className="mt-3 text-xs text-gray-500">
            Pista: usuario: admin, contraseña: admin123
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            Modelo Predictivo de Defectos
          </h2>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Predicción basada en Distribución de Rayleigh
          </p>
        </div>
        <div className="flex items-center space-x-2 text-green-600">
          <Lock className="h-4 w-4" />
          <span className="text-xs font-medium">Sesión Autenticada</span>
        </div>
      </div>

      {/* Input Form */}
      <div className="card">
        {/* Filtros Principales */}
        <details open className="mb-4">
          <summary className="cursor-pointer text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-primary-600 mb-2">
            Filtros de Búsqueda
          </summary>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 mt-2">
            <div>
              <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                Metodología *
              </label>
              <select
                value={filters.metodologia}
                onChange={(e) => handleFilterChange('metodologia', e.target.value)}
                className="w-full px-2 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
              >
                <option value="">Todas las metodologías</option>
                <option value="Scrum">Scrum</option>
                <option value="Waterfall">Waterfall (Cascada)</option>
                <option value="Kanban">Kanban</option>
                <option value="XP">Extreme Programming (XP)</option>
                <option value="RUP">RUP</option>
                <option value="DevOps">DevOps</option>
                <option value="Agile">Agile (Genérico)</option>
              </select>
              <p className="mt-0.5 text-xs text-gray-500">Metodología del proyecto</p>
            </div>

            <div>
              <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                Horas Invertidas Mínimas
              </label>
              <input
                type="number"
                value={filters.horas_invertidas_min}
                onChange={(e) => handleFilterChange('horas_invertidas_min', e.target.value)}
                placeholder="Ej: 2500"
                className="w-full px-2 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
                min="0"
              />
              <p className="mt-0.5 text-xs text-gray-500">Horas mínimas similares</p>
            </div>

            <div>
              <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                Horas Invertidas Máximas
              </label>
              <input
                type="number"
                value={filters.horas_invertidas_max}
                onChange={(e) => handleFilterChange('horas_invertidas_max', e.target.value)}
                placeholder="Ej: 3500"
                className="w-full px-2 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
                min="0"
              />
              <p className="mt-0.5 text-xs text-gray-500">Horas máximas similares</p>
            </div>

            <div>
              <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                Duración Mínima (días)
              </label>
              <input
                type="number"
                value={filters.duracion_dias_min}
                onChange={(e) => handleFilterChange('duracion_dias_min', e.target.value)}
                placeholder="Ej: 90"
                className="w-full px-2 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
                min="1"
              />
              <p className="mt-0.5 text-xs text-gray-500">Duración mínima del proyecto</p>
            </div>

            <div>
              <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                Duración Máxima (días)
              </label>
              <input
                type="number"
                value={filters.duracion_dias_max}
                onChange={(e) => handleFilterChange('duracion_dias_max', e.target.value)}
                placeholder="Ej: 180"
                className="w-full px-2 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
                min="1"
              />
              <p className="mt-0.5 text-xs text-gray-500">Duración máxima del proyecto</p>
            </div>

            <div>
              <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                Presupuesto Mínimo
              </label>
              <input
                type="number"
                value={filters.presupuesto_min}
                onChange={(e) => handleFilterChange('presupuesto_min', e.target.value)}
                placeholder="Ej: 50000"
                className="w-full px-2 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
                min="0"
                step="1000"
              />
              <p className="mt-0.5 text-xs text-gray-500">Presupuesto mínimo (USD)</p>
            </div>
          </div>
        </details>

        {/* Filtros Avanzados */}
        <details className="mb-4">
          <summary className="cursor-pointer text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-primary-600 mb-2">
            + Filtros Avanzados (Opcional)
          </summary>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 mt-2">
            <div>
              <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                Presupuesto Máximo
              </label>
              <input
                type="number"
                value={filters.presupuesto_max}
                onChange={(e) => handleFilterChange('presupuesto_max', e.target.value)}
                placeholder="Ej: 150000"
                className="w-full px-2 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
                min="0"
                step="1000"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                Entregables Mínimos
              </label>
              <input
                type="number"
                value={filters.entregables_count_min}
                onChange={(e) => handleFilterChange('entregables_count_min', e.target.value)}
                placeholder="Ej: 5"
                className="w-full px-2 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
                min="0"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                Entregables Máximos
              </label>
              <input
                type="number"
                value={filters.entregables_count_max}
                onChange={(e) => handleFilterChange('entregables_count_max', e.target.value)}
                placeholder="Ej: 15"
                className="w-full px-2 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
                min="0"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                Tecnologías Emergentes Mín.
              </label>
              <input
                type="number"
                value={filters.num_tecnologias_emergentes_min}
                onChange={(e) => handleFilterChange('num_tecnologias_emergentes_min', e.target.value)}
                placeholder="Ej: 1"
                className="w-full px-2 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
                min="0"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                Tecnologías Emergentes Máx.
              </label>
              <input
                type="number"
                value={filters.num_tecnologias_emergentes_max}
                onChange={(e) => handleFilterChange('num_tecnologias_emergentes_max', e.target.value)}
                placeholder="Ej: 5"
                className="w-full px-2 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
                min="0"
              />
            </div>
          </div>
        </details>

        {error && (
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-3 mb-4">
            <div className="flex items-center">
              <AlertCircle className="h-4 w-4 text-red-600 mr-2" />
              <p className="text-xs text-red-800 dark:text-red-200">{error}</p>
            </div>
          </div>
        )}

        <div className="flex items-center gap-3">
          <button 
            onClick={calculatePrediction} 
            disabled={loading}
            className="btn-primary text-sm px-4 py-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <>
                <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full mr-2 inline-block"></div>
                Buscando proyectos similares...
              </>
            ) : (
              <>
                <Database className="h-4 w-4 mr-1.5 inline" />
                Predecir Defectos
              </>
            )}
          </button>
          
          {predictionData && (
            <span className="text-xs text-gray-600 dark:text-gray-400">
              ✓ {predictionData.proyectos_analizados} proyectos similares encontrados
            </span>
          )}
        </div>
      </div>

      {/* Results */}
      {predictionData && (
        <>
          {/* Metadata Banner */}
          <div className="card bg-green-50 dark:bg-green-900/20 border-l-4 border-green-600">
            <div className="flex items-center justify-between flex-wrap gap-2">
              <div className="flex items-center">
                <CheckCircle className="h-5 w-5 text-green-600 mr-2" />
                <span className="text-sm font-semibold text-green-900 dark:text-green-100">
                  Predicción basada en {predictionData.proyectos_analizados} proyectos históricos
                </span>
              </div>
              <div className="flex items-center gap-2 flex-wrap">
                {predictionData.metodologias?.map((metod, idx) => (
                  <span key={idx} className="px-2 py-0.5 bg-green-100 dark:bg-green-800 text-green-800 dark:text-green-100 text-xs rounded-full">
                    {metod}
                  </span>
                ))}
              </div>
            </div>
            {predictionData.note && (
              <p className="text-xs text-green-700 dark:text-green-200 mt-1 ml-7">
                ℹ️ {predictionData.note}
              </p>
            )}
          </div>

          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
            <div className="card bg-gradient-to-br from-blue-500 to-blue-600 text-white">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs opacity-90 mb-0.5">Defectos Esperados</p>
                  <p className="text-2xl font-bold">{predictionData.expected_defects?.toFixed(2)}</p>
                  <p className="text-xs opacity-75 mt-0.5">defectos/semana</p>
                </div>
                <TrendingUp className="h-8 w-8 opacity-80" />
              </div>
            </div>

            <div className="card bg-gradient-to-br from-purple-500 to-purple-600 text-white">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs opacity-90 mb-0.5">Parámetro σ (Sigma)</p>
                  <p className="text-2xl font-bold">{predictionData.sigma?.toFixed(2)}</p>
                  <p className="text-xs opacity-75 mt-0.5">semanas</p>
                </div>
                <BarChart2 className="h-8 w-8 opacity-80" />
              </div>
            </div>

            <div className="card bg-gradient-to-br from-orange-500 to-orange-600 text-white">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs opacity-90 mb-0.5">Duración del Proyecto</p>
                  <p className="text-2xl font-bold">{predictionData.duracion_semanas}</p>
                  <p className="text-xs opacity-75 mt-0.5">semanas</p>
                </div>
                <Calendar className="h-8 w-8 opacity-80" />
              </div>
            </div>

            <div className={`card bg-gradient-to-br ${
              predictionData.riskLevel === 'alto' ? 'from-red-500 to-red-600' :
              predictionData.riskLevel === 'medio' ? 'from-yellow-500 to-yellow-600' :
              'from-green-500 to-green-600'
            } text-white`}>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs opacity-90 mb-0.5">Nivel de Riesgo</p>
                  <p className="text-2xl font-bold capitalize">{predictionData.riskLevel}</p>
                  <p className="text-xs opacity-75 mt-0.5">
                    ~{predictionData.totalDefectsEstimated} defectos totales
                  </p>
                </div>
                <AlertCircle className="h-8 w-8 opacity-80" />
              </div>
            </div>
          </div>

          {/* Percentiles */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div className="card">
              <div className="flex items-center mb-2">
                <Target className="h-4 w-4 text-primary-600 mr-1.5" />
                <h4 className="text-sm font-semibold text-gray-900 dark:text-white">
                  Percentil 90 (P90)
                </h4>
              </div>
              <p className="text-2xl font-bold text-gray-900 dark:text-white mb-1">
                {predictionData.p90?.toFixed(2)} defectos/semana
              </p>
              <p className="text-xs text-gray-600 dark:text-gray-400">
                90% de las semanas tendrán menos de este valor de defectos
              </p>
            </div>

            <div className="card">
              <div className="flex items-center mb-2">
                <Target className="h-4 w-4 text-red-600 mr-1.5" />
                <h4 className="text-sm font-semibold text-gray-900 dark:text-white">
                  Percentil 95 (P95)
                </h4>
              </div>
              <p className="text-2xl font-bold text-gray-900 dark:text-white mb-1">
                {predictionData.p95?.toFixed(2)} defectos/semana
              </p>
              <p className="text-xs text-gray-600 dark:text-gray-400">
                95% de las semanas tendrán menos de este valor de defectos
              </p>
            </div>
          </div>

          {/* Main Chart */}
          <div className="card">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center">
                <TrendingUp className="h-5 w-5 text-primary-600 mr-2" />
                <h3 className="text-base font-semibold text-gray-900 dark:text-white">
                  Distribución de Defectos por Semana
                </h3>
              </div>
              <span className="text-xs text-gray-600 dark:text-gray-400">
                Semana pico: ~{predictionData.peakWeek}
              </span>
            </div>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={predictionData.weeklyDistribution}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.1} />
                  <XAxis 
                    dataKey="week" 
                    stroke="#6B7280" 
                    fontSize={11}
                    label={{ value: 'Semana del Proyecto', position: 'insideBottom', offset: -5, fontSize: 11 }}
                  />
                  <YAxis 
                    stroke="#6B7280" 
                    fontSize={11}
                    label={{ value: 'Defectos Esperados', angle: -90, position: 'insideLeft', fontSize: 11 }}
                  />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: 'rgba(17, 24, 39, 0.9)', 
                      border: '1px solid #374151',
                      borderRadius: '8px',
                      fontSize: '12px'
                    }}
                    labelFormatter={(value) => `Semana ${value}`}
                    formatter={(value) => [value.toFixed(2), 'Defectos']}
                  />
                  <Legend wrapperStyle={{ fontSize: '11px' }} />
                  <Line 
                    type="monotone" 
                    dataKey="defects" 
                    stroke="#3B82F6" 
                    strokeWidth={2}
                    name="Defectos Esperados"
                    dot={{ fill: '#3B82F6', r: 2 }}
                    activeDot={{ r: 4 }}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="cumulative" 
                    stroke="#10B981" 
                    strokeWidth={2}
                    name="Defectos Acumulados"
                    dot={{ fill: '#10B981', r: 2 }}
                    strokeDasharray="5 5"
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
            <p className="text-xs text-gray-600 dark:text-gray-400 mt-2 text-center">
              📊 Modelo compatible con todas las metodologías (Scrum, Waterfall, Kanban, RUP, XP, DevOps)
            </p>
          </div>
        </>
      )}
    </div>
  )
}
