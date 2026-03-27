import { Routes, Route } from 'react-router-dom';
import { useAuth } from './auth';
import Navbar from './components/Navbar';
import ProtectedRoute from './components/ProtectedRoute';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Incidents from './pages/Incidents';
import IncidentDetail from './pages/IncidentDetail';
import ReportIncident from './pages/ReportIncident';

export default function App() {
  const { user } = useAuth();

  return (
    <div className="min-h-screen bg-gray-50">
      {user && <Navbar />}
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/incidents"
          element={
            <ProtectedRoute>
              <Incidents />
            </ProtectedRoute>
          }
        />
        <Route
          path="/incidents/:id"
          element={
            <ProtectedRoute>
              <IncidentDetail />
            </ProtectedRoute>
          }
        />
        <Route
          path="/report"
          element={
            <ProtectedRoute>
              <ReportIncident />
            </ProtectedRoute>
          }
        />
      </Routes>
    </div>
  );
}
