import { NavLink } from 'react-router-dom'
import { LayoutDashboard, Database, Target, TrendingUp, Building2 } from 'lucide-react'

export default function Sidebar() {
  const navigation = [
    { name: 'Dashboard', href: '/', icon: LayoutDashboard },
    { name: 'OLAP Analytics', href: '/olap', icon: Database },
    { name: 'Balanced Scorecard', href: '/balanced-scorecard', icon: Target },
    { name: 'Modelo Predictivo', href: '/predictive-model', icon: TrendingUp },
  ]

  return (
    <div className="hidden md:flex md:flex-shrink-0">
      <div className="flex flex-col w-56">
        <div className="flex flex-col flex-grow pt-4 pb-3 overflow-y-auto bg-primary-800 dark:bg-gray-800">
          <div className="flex items-center flex-shrink-0 px-3 mb-4">
            <Building2 className="h-7 w-7 text-white mr-2" />
            <div className="text-white">
              <div className="font-bold text-base">BUAP Software</div>
              <div className="text-xs text-primary-200">DSS</div>
            </div>
          </div>
          <nav className="mt-3 flex-1 flex flex-col px-2 space-y-1">
            {navigation.map((item) => (
              <NavLink
                key={item.name}
                to={item.href}
                className={({ isActive }) =>
                  `group flex items-center px-2 py-1.5 text-sm font-medium rounded-md transition-colors ${
                    isActive
                      ? 'bg-primary-900 text-white'
                      : 'text-primary-100 hover:bg-primary-700 hover:text-white'
                  }`
                }
              >
                <item.icon className="mr-2 flex-shrink-0 h-5 w-5" aria-hidden="true" />
                {item.name}
              </NavLink>
            ))}
          </nav>
          <div className="flex-shrink-0 flex border-t border-primary-700 p-3">
            <div className="text-xs text-primary-200">
              <p className="font-semibold text-white mb-1">Misión</p>
              <p className="line-clamp-2">Desarrollar soluciones de software de alta calidad mediante innovación tecnológica.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
