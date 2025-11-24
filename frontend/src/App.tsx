import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import LessonView from './pages/LessonView'
import TestView from './pages/TestView'
import TestResult from './pages/TestResult'
import PrivateRoute from './components/common/PrivateRoute'

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/dashboard"
            element={
              <PrivateRoute>
                <Dashboard />
              </PrivateRoute>
            }
          />
          <Route
            path="/modules/:moduleId/lesson"
            element={
              <PrivateRoute>
                <LessonView />
              </PrivateRoute>
            }
          />
          <Route
            path="/modules/:moduleId/test"
            element={
              <PrivateRoute>
                <TestView />
              </PrivateRoute>
            }
          />
          <Route
            path="/modules/:moduleId/result"
            element={
              <PrivateRoute>
                <TestResult />
              </PrivateRoute>
            }
          />
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  )
}

export default App


