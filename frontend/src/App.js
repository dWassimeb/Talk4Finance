// frontend/src/App.js - FIXED FOR SUBPATH DEPLOYMENT
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ChatProvider } from './context/ChatContext';
import { useAuth } from './hooks/useAuth';
import Login from './components/Auth/Login';
import Register from './components/Auth/Register';
import ChatInterface from './components/Chat/ChatInterface';
import './styles/globals.css';

function App() {
  // Get basename from environment or default to subpath
  const basename = process.env.REACT_APP_BASENAME || '/talk4finance';

  return (
    <AuthProvider>
      <ChatProvider>
        <Router basename={basename}>
          <div className="App">
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/chat" element={<ProtectedRoute><ChatInterface /></ProtectedRoute>} />
              <Route path="/" element={<Navigate to="/chat" replace />} />
            </Routes>
          </div>
        </Router>
      </ChatProvider>
    </AuthProvider>
  );
}

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();
  
  if (loading) {
    return <div className="flex items-center justify-center min-h-screen">
      <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
    </div>;
  }
  
  return user ? children : <Navigate to="/login" replace />;
}

export default App;