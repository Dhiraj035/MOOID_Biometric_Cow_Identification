import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";

import ProtectedRoute from "./components/ProtectedRoute";
import Layout from "./components/Layout";

import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import RegisterCow from "./pages/RegisterCow";
import IdentifyCow from "./pages/IdentifyCow";
import Cows from "./pages/Cows";
import RecognitionHistory from "./pages/RecognitionHistory";
import Profile from "./pages/Profile";
import SettingsPage from "./pages/SettingsPage";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* PROTECTED ROUTES */}
        <Route path="/dashboard" element={<ProtectedRoute><Layout><Dashboard /></Layout></ProtectedRoute>} />
        <Route path="/identify" element={<ProtectedRoute><Layout><IdentifyCow /></Layout></ProtectedRoute>} />
        <Route path="/register-cow" element={<ProtectedRoute><Layout><RegisterCow /></Layout></ProtectedRoute>} />
        <Route path="/cows" element={<ProtectedRoute><Layout><Cows /></Layout></ProtectedRoute>} />
        <Route path="/history" element={<ProtectedRoute><Layout><RecognitionHistory /></Layout></ProtectedRoute>} />
        <Route path="/profile" element={<ProtectedRoute><Layout><Profile /></Layout></ProtectedRoute>} />
        <Route path="/settings" element={<ProtectedRoute><Layout><SettingsPage /></Layout></ProtectedRoute>} />

        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;