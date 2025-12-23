import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import DashboardLayout from './layouts/DashboardLayout';
import Dashboard from './pages/Dashboard';
import Matches from './pages/Matches';
import Users from './pages/Users';
import Teams from './pages/Teams';
import System from './pages/System';

import Login from './pages/Login';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />

        <Route path="/" element={<DashboardLayout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="matches" element={<Matches />} />
          <Route path="users" element={<Users />} />
          <Route path="teams" element={<Teams />} />
          <Route path="system" element={<System />} />
        </Route>
        {/* Login route would go here outside DashboardLayout */}
      </Routes>
    </BrowserRouter>
  );
}

export default App;
