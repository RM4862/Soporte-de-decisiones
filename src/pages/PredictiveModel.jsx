import { useState } from 'react'
import { Calculator, Lock, TrendingUp, AlertCircle, Info, FileText } from 'lucide-react'
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceLine } from 'recharts'

// Función para calcular la distribución de Rayleigh
const calculateRayleigh = (t, sigma) => {
  return (t / (sigma ** 2)) * Math.exp(-(t ** 2) / (2 * sigma ** 2))
}

// Función para calcular defectos acumulados
const calculateCumulativeDefects = (t, sigma, totalDefects) => {
  return totalDefects * (1 - Math.exp(-(t ** 2) / (2 * sigma ** 2)))
}

export default function PredictiveModel() {
  const [authenticated, setAuthenticated] = useState(false)
  const [projectSize, setProjectSize] = useState(10000) // KLOC
  const [complexity, setComplexity] = useState('media')
  const [teamExperience, setTeamExperience] = useState('media')
  const [projectDuration, setProjectDuration] = useState(12) // meses
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

  const calculatePrediction = () => {
    // Factores de complejidad
    const complexityFactors = {
      baja: 0.8,
      media: 1.0,
      alta: 1.3,
      'muy-alta': 1.6
    }

    // Factores de experiencia
    const experienceFactors = {
      baja: 1.4,
      media: 1.0,
      alta: 0.7,
      experto: 0.5
    }

    // Calcular defectos estimados base (usando modelo empírico)
    const baseDefectRate = 40 // defectos por KLOC
    const adjustedDefectRate = baseDefectRate * 
      complexityFactors[complexity] * 
      experienceFactors[teamExperience]
    
    const totalEstimatedDefects = Math.round((projectSize / 1000) * adjustedDefectRate)

    // Parámetro sigma de Rayleigh (relacionado con el punto de máxima densidad)
    // Típicamente el pico de defectos ocurre alrededor del 40-60% del proyecto
    const sigma = projectDuration * 0.35

    // Generar datos para la curva de Rayleigh
    const timePoints = []
    for (let t = 0; t <= projectDuration; t += 0.5) {
      const density = calculateRayleigh(t, sigma)
      const cumulative = calculateCumulativeDefects(t, sigma, totalEstimatedDefects)
      const defectsAtTime = Math.round(density * totalEstimatedDefects * 1000)
      
      timePoints.push({
        mes: t.toFixed(1),
        densidad: (density * 100).toFixed(2),
        defectosAcumulados: Math.round(cumulative),
        defectosNuevos: defectsAtTime,
        criticalThreshold: totalEstimatedDefects * 0.8
      })
    }

    // Calcular estadísticas
    const peakTime = sigma * Math.sqrt(2) // Tiempo de máxima densidad
    const peakDefects = Math.max(...timePoints.map(p => p.defectosNuevos))
    
    // Distribución por severidad (estimada)
    const defectDistribution = [
      { severidad: 'Críticos', cantidad: Math.round(totalEstimatedDefects * 0.05), color: '#ef4444' },
      { severidad: 'Mayores', cantidad: Math.round(totalEstimatedDefects * 0.15), color: '#f59e0b' },
      { severidad: 'Menores', cantidad: Math.round(totalEstimatedDefects * 0.35), color: '#10b981' },
      { severidad: 'Triviales', cantidad: Math.round(totalEstimatedDefects * 0.45), color: '#6366f1' },
    ]

    setPredictionData({
      totalEstimatedDefects,
      sigma,
      peakTime,
      peakDefects,
      timePoints,
      defectDistribution,
      riskLevel: totalEstimatedDefects > 500 ? 'alto' : totalEstimatedDefects > 200 ? 'medio' : 'bajo'
    })
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

      {/* Info Banner */}
      <div className="card bg-blue-50 dark:bg-blue-900/20 border-l-4 border-blue-600">
        <div className="flex items-start">
          <Info className="h-5 w-5 text-blue-600 mr-2 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="text-sm font-semibold text-blue-900 dark:text-blue-100 mb-1">
              Acerca del Modelo de Rayleigh
            </h3>
            <p className="text-xs text-blue-800 dark:text-blue-200">
              La distribución de Rayleigh es ampliamente utilizada en ingeniería de software para modelar 
              la densidad de defectos a lo largo del ciclo de vida del proyecto. El modelo asume que los 
              defectos siguen un patrón predecible: pocos al inicio, un pico en la fase media, y una 
              disminución hacia el final del proyecto.
            </p>
          </div>
        </div>
      </div>

      {/* Input Form */}
      <div className="card">
        <div className="flex items-center mb-3">
          <Calculator className="h-5 w-5 text-primary-600 mr-2" />
          <h3 className="text-base font-semibold text-gray-900 dark:text-white">
            Parámetros del Proyecto
          </h3>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
          <div>
            <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
              Tamaño del Proyecto (LOC)
            </label>
            <input
              type="number"
              value={projectSize}
              onChange={(e) => setProjectSize(Number(e.target.value))}
              className="w-full px-2 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
              min="1000"
              step="1000"
            />
            <p className="mt-0.5 text-xs text-gray-500">Líneas de código estimadas</p>
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
              Complejidad del Proyecto
            </label>
            <select
              value={complexity}
              onChange={(e) => setComplexity(e.target.value)}
              className="w-full px-2 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
            >
              <option value="baja">Baja</option>
              <option value="media">Media</option>
              <option value="alta">Alta</option>
              <option value="muy-alta">Muy Alta</option>
            </select>
            <p className="mt-0.5 text-xs text-gray-500">Complejidad técnica y funcional</p>
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
              Experiencia del Equipo
            </label>
            <select
              value={teamExperience}
              onChange={(e) => setTeamExperience(e.target.value)}
              className="w-full px-2 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
            >
              <option value="baja">Baja (0-1 años)</option>
              <option value="media">Media (2-3 años)</option>
              <option value="alta">Alta (4-6 años)</option>
              <option value="experto">Experto (7+ años)</option>
            </select>
            <p className="mt-0.5 text-xs text-gray-500">Nivel de experiencia promedio</p>
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
              Duración del Proyecto (meses)
            </label>
            <input
              type="number"
              value={projectDuration}
              onChange={(e) => setProjectDuration(Number(e.target.value))}
              className="w-full px-2 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
              min="1"
              max="36"
            />
            <p className="mt-0.5 text-xs text-gray-500">Duración estimada</p>
          </div>
        </div>

        <div className="mt-4">
          <button onClick={calculatePrediction} className="btn-primary text-sm px-4 py-2">
            <TrendingUp className="h-4 w-4 mr-1.5 inline" />
            Calcular Predicción
          </button>
        </div>
      </div>

      {/* Results */}
      {predictionData && (
        <>
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
            <div className="card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs text-gray-600 dark:text-gray-400">Defectos Estimados</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white mt-0.5">
                    {predictionData.totalEstimatedDefects}
                  </p>
                </div>
                <AlertCircle className="h-8 w-8 text-red-500" />
              </div>
            </div>

            <div className="card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs text-gray-600 dark:text-gray-400">Pico de Defectos</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white mt-0.5">
                    {predictionData.peakTime.toFixed(1)}m
                  </p>
                </div>
                <TrendingUp className="h-8 w-8 text-orange-500" />
              </div>
            </div>

            <div className="card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs text-gray-600 dark:text-gray-400">Parámetro σ</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white mt-0.5">
                    {predictionData.sigma.toFixed(2)}
                  </p>
                </div>
                <Calculator className="h-8 w-8 text-blue-500" />
              </div>
            </div>

            <div className="card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs text-gray-600 dark:text-gray-400">Nivel de Riesgo</p>
                  <p className={`text-xl font-bold mt-0.5 ${
                    predictionData.riskLevel === 'alto' ? 'text-red-600' :
                    predictionData.riskLevel === 'medio' ? 'text-yellow-600' :
                    'text-green-600'
                  }`}>
                    {predictionData.riskLevel.toUpperCase()}
                  </p>
                </div>
                <div className={`h-8 w-8 rounded-full flex items-center justify-center ${
                  predictionData.riskLevel === 'alto' ? 'bg-red-100' :
                  predictionData.riskLevel === 'medio' ? 'bg-yellow-100' :
                  'bg-green-100'
                }`}>
                  <AlertCircle className={`h-5 w-5 ${
                    predictionData.riskLevel === 'alto' ? 'text-red-600' :
                    predictionData.riskLevel === 'medio' ? 'text-yellow-600' :
                    'text-green-600'
                  }`} />
                </div>
              </div>
            </div>
          </div>

          {/* Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div className="card">
              <h3 className="text-base font-semibold text-gray-900 dark:text-white mb-3">
                Curva de Rayleigh - Defectos Acumulados
              </h3>
              <ResponsiveContainer width="100%" height={220}>
                <LineChart data={predictionData.timePoints}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="mes" label={{ value: 'Tiempo (meses)', position: 'insideBottom', offset: -5 }} />
                  <YAxis label={{ value: 'Defectos Acumulados', angle: -90, position: 'insideLeft' }} />
                  <Tooltip />
                  <Legend />
                  <ReferenceLine 
                    x={predictionData.peakTime.toFixed(1)} 
                    stroke="red" 
                    label="Pico" 
                    strokeDasharray="3 3" 
                  />
                  <Line 
                    type="monotone" 
                    dataKey="defectosAcumulados" 
                    stroke="#0ea5e9" 
                    strokeWidth={2}
                    name="Defectos Acumulados"
                    dot={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>

            <div className="card">
              <h3 className="text-base font-semibold text-gray-900 dark:text-white mb-3">
                Tasa de Detección de Defectos
              </h3>
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={predictionData.timePoints.filter((_, i) => i % 2 === 0)}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="mes" label={{ value: 'Tiempo (meses)', position: 'insideBottom', offset: -5 }} />
                  <YAxis label={{ value: 'Defectos Nuevos', angle: -90, position: 'insideLeft' }} />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="defectosNuevos" fill="#10b981" name="Defectos Nuevos por Período" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Defect Distribution */}
          <div className="card">
            <h3 className="text-base font-semibold text-gray-900 dark:text-white mb-3">
              Distribución Estimada por Severidad
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {predictionData.defectDistribution.map((item) => (
                <div key={item.severidad} className="p-3 rounded-lg border-2" style={{ borderColor: item.color }}>
                  <p className="text-xs text-gray-600 dark:text-gray-400">{item.severidad}</p>
                  <p className="text-xl font-bold mt-0.5" style={{ color: item.color }}>
                    {item.cantidad}
                  </p>
                  <p className="text-xs text-gray-500 mt-0.5">
                    {((item.cantidad / predictionData.totalEstimatedDefects) * 100).toFixed(1)}%
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Recommendations */}
          <div className="card bg-purple-50 dark:bg-purple-900/20 border-l-4 border-purple-600">
            <div className="flex items-start">
              <FileText className="h-5 w-5 text-purple-600 mr-2 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="text-sm font-semibold text-purple-900 dark:text-purple-100 mb-1.5">
                  Recomendaciones Basadas en la Predicción
                </h3>
                <ul className="space-y-1.5 text-xs text-purple-800 dark:text-purple-200">
                  <li>
                    • <strong>Reforzar Testing:</strong> Incrementar la cobertura de pruebas especialmente 
                    entre los meses {Math.floor(predictionData.peakTime - 2)} y {Math.ceil(predictionData.peakTime + 2)}, 
                    donde se espera el pico de defectos.
                  </li>
                  <li>
                    • <strong>Revisiones de Código:</strong> Implementar revisiones de código más frecuentes 
                    durante la fase crítica para detectar defectos tempranamente.
                  </li>
                  <li>
                    • <strong>Asignación de Recursos:</strong> Planificar recursos adicionales de QA para el 
                    período de mayor densidad de defectos.
                  </li>
                  <li>
                    • <strong>Monitoreo Continuo:</strong> Comparar defectos reales vs. predichos mensualmente 
                    para ajustar el modelo y estrategias de calidad.
                  </li>
                  {predictionData.riskLevel === 'alto' && (
                    <li className="text-red-700 dark:text-red-300">
                      • <strong>⚠️ Alerta:</strong> Nivel de riesgo alto. Considerar reducir alcance, 
                      aumentar experiencia del equipo, o extender timeline del proyecto.
                    </li>
                  )}
                </ul>
              </div>
            </div>
          </div>

          {/* Technical Details */}
          <div className="card">
            <h3 className="text-base font-semibold text-gray-900 dark:text-white mb-2">
              Detalles Técnicos del Modelo
            </h3>
            <div className="bg-gray-50 dark:bg-gray-700 p-3 rounded-lg font-mono text-xs">
              <p className="text-gray-700 dark:text-gray-300 mb-1">
                <strong>Función de Densidad de Rayleigh:</strong>
              </p>
              <p className="text-gray-600 dark:text-gray-400 mb-3">
                f(t) = (t / σ²) × e^(−t² / 2σ²)
              </p>
              <p className="text-gray-700 dark:text-gray-300 mb-1">
                <strong>Defectos Acumulados:</strong>
              </p>
              <p className="text-gray-600 dark:text-gray-400 mb-3">
                F(t) = Total × (1 − e^(−t² / 2σ²))
              </p>
              <p className="text-gray-700 dark:text-gray-300">
                <strong>Parámetros del modelo:</strong>
              </p>
              <ul className="text-gray-600 dark:text-gray-400 mt-1.5 space-y-0.5">
                <li>• σ (sigma) = {predictionData.sigma.toFixed(2)} meses</li>
                <li>• Tiempo del pico = σ√2 = {predictionData.peakTime.toFixed(2)} meses</li>
                <li>• Total de defectos estimados = {predictionData.totalEstimatedDefects}</li>
              </ul>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
