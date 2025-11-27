import { Target, DollarSign, Users, Cog, GraduationCap, TrendingUp, ArrowUpRight } from 'lucide-react'
import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, AreaChart, Area } from 'recharts'

// Datos de las 4 perspectivas del Balanced Scorecard
const perspectives = [
  {
    id: 'financiera',
    title: 'Financiera',
    icon: DollarSign,
    color: 'from-green-500 to-emerald-600',
    value: 89,
    trend: '+5%',
    description: 'Rentabilidad y crecimiento sostenible',
    metrics: [
      { label: 'ROI Proyectos', value: 28, target: 30, unit: '%' },
      { label: 'Ingresos Totales', value: 520, target: 500, unit: 'K' },
      { label: 'Margen Utilidad', value: 22, target: 25, unit: '%' }
    ],
    history: [
      { mes: 'Ene', valor: 82 },
      { mes: 'Feb', valor: 84 },
      { mes: 'Mar', valor: 85 },
      { mes: 'Abr', valor: 86 },
      { mes: 'May', valor: 88 },
      { mes: 'Jun', valor: 89 }
    ]
  },
  {
    id: 'clientes',
    title: 'Clientes',
    icon: Users,
    color: 'from-blue-500 to-cyan-600',
    value: 92,
    trend: '+3%',
    description: 'Satisfacción y fidelización',
    metrics: [
      { label: 'NPS Score', value: 68, target: 70, unit: '' },
      { label: 'Retención', value: 92, target: 90, unit: '%' },
      { label: 'Nuevos Clientes', value: 25, target: 20, unit: '' }
    ],
    history: [
      { mes: 'Ene', valor: 88 },
      { mes: 'Feb', valor: 89 },
      { mes: 'Mar', valor: 90 },
      { mes: 'Abr', valor: 90 },
      { mes: 'May', valor: 91 },
      { mes: 'Jun', valor: 92 }
    ]
  },
  {
    id: 'procesos',
    title: 'Procesos Internos',
    icon: Cog,
    color: 'from-purple-500 to-indigo-600',
    value: 87,
    trend: '+4%',
    description: 'Eficiencia y calidad operativa',
    metrics: [
      { label: 'Entregas a Tiempo', value: 92, target: 95, unit: '%' },
      { label: 'Calidad Código', value: 89, target: 85, unit: '%' },
      { label: 'Automatización', value: 75, target: 70, unit: '%' }
    ],
    history: [
      { mes: 'Ene', valor: 82 },
      { mes: 'Feb', valor: 83 },
      { mes: 'Mar', valor: 85 },
      { mes: 'Abr', valor: 85 },
      { mes: 'May', valor: 86 },
      { mes: 'Jun', valor: 87 }
    ]
  },
  {
    id: 'aprendizaje',
    title: 'Aprendizaje y Crecimiento',
    icon: GraduationCap,
    color: 'from-orange-500 to-amber-600',
    value: 85,
    trend: '+6%',
    description: 'Desarrollo del talento y conocimiento',
    metrics: [
      { label: 'Horas Capacitación', value: 36, target: 40, unit: 'h' },
      { label: 'Certificaciones', value: 12, target: 15, unit: '' },
      { label: 'Satisfacción Laboral', value: 88, target: 85, unit: '%' }
    ],
    history: [
      { mes: 'Ene', valor: 78 },
      { mes: 'Feb', valor: 80 },
      { mes: 'Mar', valor: 82 },
      { mes: 'Abr', valor: 83 },
      { mes: 'May', valor: 84 },
      { mes: 'Jun', valor: 85 }
    ]
  }
]



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

const PerspectiveCard = ({ perspective }) => {
  const Icon = perspective.icon
  
  // Preparar datos para el gráfico combinado
  const chartData = perspective.history.map((h, idx) => ({
    mes: h.mes,
    rendimiento: h.valor,
    ...perspective.metrics.reduce((acc, metric, mIdx) => {
      // Simular progreso de cada métrica a lo largo del tiempo
      const progress = metric.value - (6 - idx) * 2
      acc[metric.label] = Math.max(progress, metric.target * 0.7)
      return acc
    }, {})
  }))

  const colors = {
    'green': '#10b981',
    'blue': '#0ea5e9', 
    'purple': '#8b5cf6',
    'orange': '#f59e0b'
  }
  
  const mainColor = perspective.color.includes('green') ? colors.green : 
                    perspective.color.includes('blue') ? colors.blue :
                    perspective.color.includes('purple') ? colors.purple : colors.orange
  
  return (
    <div className="card hover:shadow-lg transition-shadow h-full">
      {/* Header compacto con gradiente */}
      <div className={`bg-gradient-to-r ${perspective.color} p-2 rounded-t-lg -m-4 mb-2`}>
        <div className="flex items-center justify-between text-white">
          <div className="flex items-center space-x-2">
            <Icon className="h-4 w-4" />
            <div>
              <h3 className="font-bold text-xs">{perspective.title}</h3>
            </div>
          </div>
          <div className="text-right">
            <div className="text-xl font-bold">{perspective.value}%</div>
            <div className="flex items-center text-xs">
              <TrendingUp className="h-3 w-3 mr-1" />
              {perspective.trend}
            </div>
          </div>
        </div>
      </div>

      {/* Gráfico principal - más grande y prominente */}
      <div className="mb-2">
        <ResponsiveContainer width="100%" height={140}>
          <LineChart data={chartData}>
            <defs>
              <linearGradient id={`gradient${perspective.id}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={mainColor} stopOpacity={0.3}/>
                <stop offset="95%" stopColor={mainColor} stopOpacity={0.05}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.1} />
            <XAxis dataKey="mes" tick={{ fontSize: 10 }} stroke="#6b7280" />
            <YAxis domain={[60, 100]} tick={{ fontSize: 10 }} stroke="#6b7280" />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: 'rgba(17, 24, 39, 0.95)', 
                border: 'none',
                borderRadius: '6px',
                fontSize: '11px'
              }}
            />
            <Line 
              type="monotone" 
              dataKey="rendimiento" 
              stroke={mainColor}
              strokeWidth={3}
              dot={{ fill: mainColor, r: 4 }}
              activeDot={{ r: 6 }}
              name="Rendimiento"
            />
            {perspective.metrics.map((metric, idx) => (
              <Line
                key={idx}
                type="monotone"
                dataKey={metric.label}
                stroke={mainColor}
                strokeWidth={1.5}
                strokeDasharray="3 3"
                dot={false}
                opacity={0.4}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Métricas en grid compacto */}
      <div className="grid grid-cols-3 gap-1.5">
        {perspective.metrics.map((metric, idx) => {
          const isAboveTarget = metric.value >= metric.target
          const percentage = ((metric.value / metric.target) * 100).toFixed(0)
          
          return (
            <div key={idx} className="text-center p-1.5 bg-gray-50 dark:bg-gray-800 rounded">
              <div className="text-[10px] text-gray-600 dark:text-gray-400 mb-0.5 truncate" title={metric.label}>
                {metric.label}
              </div>
              <div className="flex items-center justify-center space-x-0.5">
                <span className="text-sm font-bold text-gray-900 dark:text-white">
                  {metric.value}{metric.unit}
                </span>
                {isAboveTarget && (
                  <ArrowUpRight className="h-2.5 w-2.5 text-green-500" />
                )}
              </div>
              <div className={`text-[10px] font-medium ${isAboveTarget ? 'text-green-600' : 'text-yellow-600'}`}>
                {percentage}%
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default function BalancedScorecard() {
  return (
    <div className="space-y-3">
      {/* Header compacto */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Balanced Scorecard</h2>
          <p className="text-xs text-gray-500 dark:text-gray-400">
            Vista integral de las 4 perspectivas estratégicas
          </p>
        </div>
      </div>

      {/* Las 4 Perspectivas en grid 2x2 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
        {perspectives.map((perspective) => (
          <PerspectiveCard key={perspective.id} perspective={perspective} />
        ))}
      </div>
    </div>
  )
}
