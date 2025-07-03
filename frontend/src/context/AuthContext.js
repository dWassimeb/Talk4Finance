// frontend/src/context/AuthContext.jsx - Enhanced with better error handling
import React, { createContext, useState, useEffect } from 'react';
import { authService } from '../services/auth';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initializeAuth = async () => {
      console.log('🔐 Initializing authentication...');
      const token = localStorage.getItem('token');

      if (token) {
        console.log('🔐 Token found, fetching user data...');
        try {
          const userData = await authService.getCurrentUser();
          console.log('✅ User data fetched:', userData);
          setUser(userData);
        } catch (error) {
          console.error('❌ Failed to get current user:', error);
          localStorage.removeItem('token');
          setUser(null);
        }
      } else {
        console.log('🔐 No token found');
        setUser(null);
      }

      setLoading(false);
    };

    initializeAuth();
  }, []);

  const login = async (email, password) => {
    try {
      console.log('🔐 Login attempt for:', email);

      // Call the login API
      const response = await authService.login(email, password);
      console.log('🔐 Login API response:', response);

      // Store the token
      localStorage.setItem('token', response.access_token);
      console.log('🔐 Token stored');

      // Get user data
      const userData = await authService.getCurrentUser();
      console.log('🔐 User data fetched:', userData);

      // Set user in context
      setUser(userData);
      console.log('✅ User set in context, login successful');

      return { success: true };

    } catch (error) {
      console.error('❌ Login error:', error);

      // Clear any token that might be stored
      localStorage.removeItem('token');
      setUser(null);

      // Extract error message
      let errorMessage = 'Login failed. Please try again.';

      if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.response?.data?.message) {
        errorMessage = error.response.data.message;
      } else if (error.message) {
        errorMessage = error.message;
      }

      console.error('❌ Login error message:', errorMessage);

      return { success: false, error: errorMessage };
    }
  };

  const register = async (email, username, password) => {
    try {
      console.log('🔐 Registration attempt for:', email);

      const response = await authService.register(email, username, password);
      console.log('🔐 Registration response:', response);

      // Note: For your approval system, don't auto-login after registration
      // Just return success - user needs admin approval first
      return { success: true, message: 'Registration successful. Awaiting admin approval.' };

    } catch (error) {
      console.error('❌ Registration error:', error);

      let errorMessage = 'Registration failed. Please try again.';

      if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.response?.data?.message) {
        errorMessage = error.response.data.message;
      } else if (error.message) {
        errorMessage = error.message;
      }

      return { success: false, error: errorMessage };
    }
  };

  const logout = () => {
    console.log('🔐 Logging out...');
    localStorage.removeItem('token');
    setUser(null);
    console.log('✅ Logout complete');
  };

  const value = {
    user,
    login,
    register,
    logout,
    loading,
    // Add helper functions
    isAuthenticated: !!user,
    isAdmin: user?.role === 'admin',
    userStatus: user?.status
  };

  console.log('🔐 AuthContext state:', {
    user: user ? { id: user.id, email: user.email, role: user.role, status: user.status } : null,
    loading,
    isAuthenticated: !!user
  });

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export { AuthContext };