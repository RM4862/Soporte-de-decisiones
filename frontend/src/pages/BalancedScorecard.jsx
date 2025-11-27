import { TrendingUp, TrendingDown, Target, DollarSign, Users, Cog, GraduationCap, CheckCircle, AlertTriangle } from 'lucide-react'
import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, Cell } from 'recharts'

// Datos de las 4 perspectivas del Balanced Scorecard
const financialPerspective = {
  title: 'Perspectiva Financiera',
  icon: DollarSign,
  color: 'bg-green-500',
  objectives: [
    {
      name: 'Incrementar Rentabilidad',
      target: 25,
      current: 22,
      unit: '%',
      status: 'warning',
      keyResults: [
        { kr: 'ROI de proyectos', target: 30, current: 28 },
        { kr: 'Margen de utilidad', target: 25, current: 22 },
        { kr: 'Reducción de costos', target: 15, current: 12 },
      ]
    },
    {
      name: 'Crecimiento de Ingresos',
      target: 500000,
      current: 520000,
      unit: '$',
      status: 'success',
      keyResults: [
        { kr: 'Ingresos recurrentes', target: 300000, current: 340000 },
        { kr: 'Nuevos contratos', target: 15, current: 18 },
        { kr: 'Upselling clientes', target: 10, current: 12 },
      ]
    }
  ]
}

const customerPerspective = {
  title: 'Perspectiva de Clientes',
  icon: Users,
  color: 'bg-blue-500',
  objectives: [
    {
      name: 'Satisfacción del Cliente',
      target: 95,
      current: 94,
      unit: '%',
      status: 'warning',
      keyResults: [
        { kr: 'NPS Score', target: 70, current: 68 },
        { kr: 'Tasa de retención', target: 90, current: 92 },
        { kr: 'Recomendaciones', target: 25, current: 22 },
      ]
    },
    {
      name: 'Adquisición de Clientes',
      target: 20,
      current: 25,
      unit: 'clientes',
      status: 'success',
      keyResults: [
        { kr: 'Leads calificados', target: 50, current: 58 },
        { kr: 'Tasa de conversión', target: 40, current: 43 },
        { kr: 'Tiempo de cierre', target: 30, current: 28 },
      ]
    }
  ]
}

const internalProcessPerspective = {
  title: 'Perspectiva de Procesos Internos',
  icon: Cog,
  color: 'bg-purple-500',
  objectives: [
    {
      name: 'Excelencia Operativa',
      target: 90,
      current: 87,
      unit: '%',
      status: 'warning',
      keyResults: [
        { kr: 'Entregas a tiempo', target: 95, current: 92 },
        { kr: 'Calidad de código', target: 85, current: 89 },
        { kr: 'Cobertura de pruebas', target: 90, current: 94 },
      ]
    },
    {
      name: 'Innovación y Mejora',
      target: 85,
      current: 88,
      unit: '%',
      status: 'success',
      keyResults: [
        { kr: 'Nuevas tecnologías adoptadas', target: 5, current: 6 },
        { kr: 'Mejoras implementadas', target: 20, current: 23 },
        { kr: 'Automatización', target: 70, current: 75 },
      ]
    }
  ]
}

const learningPerspective = {
  title: 'Perspectiva de Aprendizaje y Crecimiento',
  icon: GraduationCap,
  color: 'bg-orange-500',
  objectives: [
    {
      name: 'Desarrollo del Talento',
      target: 90,
      current: 85,
      unit: '%',
      status: 'warning',
      keyResults: [
        { kr: 'Horas de capacitación', target: 40, current: 36 },
        { kr: 'Certificaciones obtenidas', target: 15, current: 12 },
        { kr: 'Satisfacción laboral', target: 85, current: 88 },
      ]
    },
    {
      name: 'Gestión del Conocimiento',
      target: 80,
      current: 82,
      unit: '%',
      status: 'success',
      keyResults: [
        { kr: 'Documentación actualizada', target: 90, current: 92 },
        { kr: 'Reutilización de código', target: 60, current: 65 },
        { kr: 'Colaboración en equipo', target: 85, current: 87 },
      ]
    }
  ]
}

// Datos para el gráfico radar
const radarData = [
  {
    perspective: 'Financiera',
    value: 89,
    fullMark: 100,
  },
  {
    perspective: 'Clientes',
    value: 92,
    fullMark: 100,
  },
  {
    perspective: 'Procesos',
    value: 87,
    fullMark: 100,
  },
  {
    perspective: 'Aprendizaje',
    value: 85,
    fullMark: 100,
  },
]

// Datos para gráfico de cumplimiento de OKRs
const okrCompletionData = [
  { trimestre: 'Q1', financiera: 85, clientes: 88, procesos: 82, aprendizaje: 80 },
  { trimestre: 'Q2', financiera: 87, clientes: 90, procesos: 85, aprendizaje: 83 },
  { trimestre: 'Q3', financiera: 88, clientes: 91, procesos: 86, aprendizaje: 84 },
  { trimestre: 'Q4', financiera: 89, clientes: 92, procesos: 87, aprendizaje: 85 },
]

const PerspectiveCard = ({ perspective }) => {
  const Icon = perspective.icon
  
  return (
    <div className="card">
      <div className="flex items-center mb-2">
        <div className={`${perspective.color} p-1.5 rounded-lg mr-2`}>
          <Icon className="h-4 w-4 text-white" />
        </div>
        <h3 className="text-sm font-semibold text-gray-900 dark:text-white">
          {perspective.title}
        </h3>
      </div>
      
      <div className="space-y-2.5">
        {perspective.objectives.map((objective, idx) => (
          <div key={idx} className="border-l-2 border-primary-500 pl-2">
            <div className="flex items-start justify-between mb-1">
              <div className="flex-1">
                <h4 className="font-semibold text-xs text-gray-800 dark:text-gray-200">
                  {objective.name}
                </h4>
                <div className="flex items-center mt-0.5 space-x-1.5">
                  <span className="text-base font-bold text-gray-900 dark:text-white">
                    {typeof objective.current === 'number' && objective.current > 1000 
                      ? `$${(objective.current / 1000).toFixed(0)}K` 
                      : objective.current}{objective.unit}
                  </span>
                  <span className="text-xs text-gray-500">
                    / {typeof objective.target === 'number' && objective.target > 1000 
                      ? `$${(objective.target / 1000).toFixed(0)}K` 
                      : objective.target}{objective.unit}
                  </span>
                </div>
              </div>
              {objective.status === 'success' ? (
                <CheckCircle className="h-4 w-4 text-green-500 flex-shrink-0" />
              ) : (
                <AlertTriangle className="h-4 w-4 text-yellow-500 flex-shrink-0" />
              )}
            </div>
            
            <div className="w-full bg-gray-200 rounded-full h-1.5 mb-1.5">
              <div
                className={`h-1.5 rounded-full ${
                  objective.status === 'success' ? 'bg-green-500' : 'bg-yellow-500'
                }`}
                style={{
                  width: `${Math.min((objective.current / objective.target) * 100, 100)}%`
                }}
              ></div>
            </div>
            
            <div className="space-y-0.5">
              {objective.keyResults.map((kr, krIdx) => (
                <div key={krIdx} className="flex items-center justify-between text-xs">
                  <span className="text-gray-600 dark:text-gray-400 truncate mr-2">{kr.kr}</span>
                  <div className="flex items-center space-x-1 flex-shrink-0">
                    <span className="font-medium text-gray-900 dark:text-white">
                      {kr.current}
                    </span>
                    <span className="text-gray-500">/{kr.target}</span>
                    {kr.current >= kr.target ? (
                      <TrendingUp className="h-3 w-3 text-green-500" />
                    ) : (
                      <TrendingDown className="h-3 w-3 text-yellow-500" />
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default function BalancedScorecard() {
  return (
    <div className="space-y-3">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Balanced Scorecard</h2>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Monitoreo estratégico de OKRs alineados a la visión empresarial
        </p>
      </div>

      {/* Strategic Vision Banner */}
      <div className="card bg-gradient-to-r from-primary-600 to-primary-800 text-white">
        <div className="flex items-start">
          <Target className="h-5 w-5 mr-2 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="text-base font-bold mb-1">Visión Estratégica</h3>
            <p className="text-xs text-primary-50 leading-relaxed">
              Ser una empresa líder en el desarrollo de software inteligente que impulse la transformación 
              digital a través de soluciones confiables, medibles y centradas en la toma de decisiones 
              basadas en datos.
            </p>
          </div>
        </div>
      </div>

      {/* Overall Performance Radar */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
        <div className="card">
          <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-2">
            Rendimiento Global por Perspectiva
          </h3>
          <ResponsiveContainer width="100%" height={180}>
            <RadarChart data={radarData}>
              <PolarGrid />
              <PolarAngleAxis dataKey="perspective" tick={{ fontSize: 11 }} />
              <PolarRadiusAxis angle={90} domain={[0, 100]} tick={{ fontSize: 10 }} />
              <Radar name="Rendimiento" dataKey="value" stroke="#0ea5e9" fill="#0ea5e9" fillOpacity={0.6} />
              <Tooltip contentStyle={{ fontSize: '11px' }} />
            </RadarChart>
          </ResponsiveContainer>
          <div className="mt-2 text-center">
            <p className="text-xs text-gray-600 dark:text-gray-400">
              Promedio: <span className="font-bold text-primary-600">88.25%</span>
            </p>
          </div>
        </div>

        <div className="card">
          <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-2">
            Evolución de Cumplimiento de OKRs
          </h3>
          <ResponsiveContainer width="100%" height={180}>
            <BarChart data={okrCompletionData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="trimestre" tick={{ fontSize: 11 }} />
              <YAxis domain={[0, 100]} tick={{ fontSize: 10 }} />
              <Tooltip contentStyle={{ fontSize: '11px' }} />
              <Legend wrapperStyle={{ fontSize: '11px' }} />
              <Bar dataKey="financiera" fill="#10b981" name="Financ." />
              <Bar dataKey="clientes" fill="#0ea5e9" name="Client." />
              <Bar dataKey="procesos" fill="#8b5cf6" name="Proc." />
              <Bar dataKey="aprendizaje" fill="#f59e0b" name="Aprend." />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Four Perspectives */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
        <PerspectiveCard perspective={financialPerspective} />
        <PerspectiveCard perspective={customerPerspective} />
        <PerspectiveCard perspective={internalProcessPerspective} />
        <PerspectiveCard perspective={learningPerspective} />
      </div>

      {/* Strategic Initiatives */}
      <div className="card">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-2">
          Iniciativas Estratégicas en Curso
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
          <div className="p-2 border border-gray-200 dark:border-gray-700 rounded-lg">
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs font-semibold text-gray-900 dark:text-white">
                Certificación ISO 9001
              </span>
              <span className="text-xs px-1 py-0.5 bg-blue-100 text-blue-800 rounded-full">
                En Progreso
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-1 mb-1">
              <div className="bg-blue-600 h-1 rounded-full" style={{ width: '65%' }}></div>
            </div>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              Impacto: Procesos, Clientes
            </p>
          </div>

          <div className="p-2 border border-gray-200 dark:border-gray-700 rounded-lg">
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs font-semibold text-gray-900 dark:text-white">
                Programa Certificaciones
              </span>
              <span className="text-xs px-1 py-0.5 bg-green-100 text-green-800 rounded-full">
                Activo
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-1 mb-1">
              <div className="bg-green-600 h-1 rounded-full" style={{ width: '80%' }}></div>
            </div>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              Impacto: Aprendizaje, Procesos
            </p>
          </div>

          <div className="p-2 border border-gray-200 dark:border-gray-700 rounded-lg">
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs font-semibold text-gray-900 dark:text-white">
                Expansión Regional
              </span>
              <span className="text-xs px-1 py-0.5 bg-yellow-100 text-yellow-800 rounded-full">
                Planificado
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-1 mb-1">
              <div className="bg-yellow-600 h-1 rounded-full" style={{ width: '30%' }}></div>
            </div>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              Impacto: Financiera, Clientes
            </p>
          </div>
        </div>
      </div>

      {/* Strategic Insights */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        <div className="card bg-green-50 dark:bg-green-900/20 border-l-4 border-green-600">
          <h4 className="text-xs font-semibold text-green-900 dark:text-green-100 mb-1">
            Fortalezas Estratégicas
          </h4>
          <ul className="space-y-0.5 text-xs text-green-800 dark:text-green-200">
            <li>• Superación de meta de adquisición de clientes (125%)</li>
            <li>• Excelente gestión del conocimiento (102.5%)</li>
            <li>• Alta tasa de innovación y adopción tecnológica</li>
            <li>• Crecimiento sostenido de ingresos recurrentes</li>
          </ul>
        </div>

        <div className="card bg-yellow-50 dark:bg-yellow-900/20 border-l-4 border-yellow-600">
          <h4 className="text-xs font-semibold text-yellow-900 dark:text-yellow-100 mb-1">
            Áreas de Mejora
          </h4>
          <ul className="space-y-0.5 text-xs text-yellow-800 dark:text-yellow-200">
            <li>• Incrementar margen de rentabilidad (88% del objetivo)</li>
            <li>• Mejorar NPS Score para alcanzar meta de satisfacción</li>
            <li>• Aumentar horas de capacitación del personal</li>
            <li>• Optimizar entregas a tiempo en proyectos</li>
          </ul>
        </div>
      </div>
    </div>
  )
}
