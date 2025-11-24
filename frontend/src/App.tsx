import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import LessonView from './pages/LessonView'
import TestView from './pages/TestView'
import TestResult from './pages/TestResult'
import PrivateRoute from './components/common/PrivateRoute'
import AdminRoute from './components/common/AdminRoute'
import AdminCourses from './pages/admin/AdminCourses'
import AdminCourseModules from './pages/admin/AdminCourseModules'
import AdminModules from './pages/admin/AdminModules'
import AdminLessons from './pages/admin/AdminLessons'
import AdminTestEditor from './pages/admin/AdminTestEditor'

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
          <Route
            path="/admin/courses"
            element={
              <AdminRoute>
                <AdminCourses />
              </AdminRoute>
            }
          />
          <Route
            path="/admin/courses/:courseId/modules"
            element={
              <AdminRoute>
                <AdminCourseModules />
              </AdminRoute>
            }
          />
          <Route
            path="/admin/modules"
            element={
              <AdminRoute>
                <AdminModules />
              </AdminRoute>
            }
          />
          <Route
            path="/admin/modules/:moduleId/lessons"
            element={
              <AdminRoute>
                <AdminLessons />
              </AdminRoute>
            }
          />
          <Route
            path="/admin/modules/:moduleId/test"
            element={
              <AdminRoute>
                <AdminTestEditor />
              </AdminRoute>
            }
          />
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  )
}

export default App


