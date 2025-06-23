// frontend/src/App.js - FIXED FOR REVERSE PROXY

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
  return (
    <AuthProvider>
      <ChatProvider>
        <Router basename="/talk4finance">
          <div className="App">
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/chat" element={<ProtectedRoute><ChatInterface /></ProtectedRoute>} />
              {/* FIXED: Don't auto-redirect to /chat, redirect to login if not authenticated */}
              <Route path="/" element={<ProtectedRouteOrLogin />} />
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

// FIXED: New component to handle root route properly
function ProtectedRouteOrLogin() {
  const { user, loading } = useAuth();

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen">
      <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
    </div>;
  }

  // If user is authenticated, go to chat, otherwise go to login
  return user ? <Navigate to="/chat" replace /> : <Navigate to="/login" replace />;
}

export default App;