// frontend/src/App.js - NO BASENAME (nginx handles subpath)
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ChatProvider } from './context/ChatContext';
import { useAuth } from './hooks/useAuth';
import Login from './components/Auth/Login';
import Register from './components/Auth/Register';
import ChatInterface from './components/Chat/ChatInterface';
import './styles/globals.css';

console.log('🚀 App.js file loaded');

function App() {
  console.log('🚀 App component rendering');
  console.log('🔍 Current location:', window.location.href);

  // NO BASENAME - nginx strips /talk4finance/ before forwarding to FastAPI
  return (
    <AuthProvider>
      <ChatProvider>
        <Router>
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
  console.log('🔒 ProtectedRoute rendering');
  const { user, loading } = useAuth();

  console.log('🔒 Auth state:', { user: !!user, loading });

  if (loading) {
    console.log('🔒 Showing loading spinner');
    return <div className="flex items-center justify-center min-h-screen">
      <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
    </div>;
  }

  console.log('🔒 Auth check complete, user:', !!user);
  return user ? children : <Navigate to="/login" replace />;
}

export default App;