import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import OLAPDashboard from './pages/OLAPDashboard'
import BalancedScorecard from './pages/BalancedScorecard'
import PredictiveModel from './pages/PredictiveModel'

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="olap" element={<OLAPDashboard />} />
          <Route path="balanced-scorecard" element={<BalancedScorecard />} />
          <Route path="predictive-model" element={<PredictiveModel />} />
        </Route>
      </Routes>
    </Router>
  )
}

export default App
