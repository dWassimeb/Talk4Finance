// frontend/src/components/Auth/Register.jsx
import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { Bot, Lock, Mail, User, Sparkles } from 'lucide-react';

const Register = () => {
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    password: '',
    confirmPassword: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      setLoading(false);
      return;
    }

    const result = await register(formData.email, formData.username, formData.password);

    if (result.success) {
      navigate('/chat');
    } else {
      setError(result.error);
    }

    setLoading(false);
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-cyan-50 flex items-center justify-center px-4 relative overflow-hidden">
      {/* Background Elements */}
      <div className="absolute inset-0">
        <div className="absolute top-20 left-20 w-72 h-72 bg-gradient-to-r from-[#00ACB5]/20 to-[#00929A]/20 rounded-full blur-3xl"></div>
        <div className="absolute bottom-20 right-20 w-96 h-96 bg-gradient-to-r from-blue-400/20 to-cyan-400/20 rounded-full blur-3xl"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-80 h-80 bg-gradient-to-r from-purple-400/10 to-pink-400/10 rounded-full blur-3xl"></div>
      </div>

      <div className="relative max-w-md w-full">
        {/* Main Card */}
        <div className="bg-white/80 backdrop-blur-xl rounded-3xl shadow-2xl border border-white/20 p-8">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="w-16 h-16 bg-gradient-to-br from-[#00ACB5] to-[#00929A] rounded-2xl flex items-center justify-center mx-auto mb-6 relative">
              <Bot className="w-8 h-8 text-white" />
              <div className="absolute -inset-1 bg-gradient-to-r from-[#00ACB5] to-[#00929A] rounded-2xl blur opacity-25 animate-pulse"></div>
            </div>

            <h1 className="text-3xl font-bold bg-gradient-to-r from-[#00ACB5] to-[#00929A] bg-clip-text text-transparent mb-2">
              Talk4Finance
            </h1>
            <p className="text-gray-600 mb-2">Create Your Account</p>
            <div className="flex items-center justify-center space-x-1 text-sm text-gray-500">
              <Sparkles className="w-4 h-4" />
              <span>Join the Future of Finance</span>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {error && (
              <div className="bg-red-50/80 backdrop-blur-sm border border-red-200/50 text-red-700 px-4 py-3 rounded-2xl">
                {error}
              </div>
            )}

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Email Address
                </label>
                <div className="relative">
                  <Mail className="absolute left-4 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <input
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    required
                    className="w-full pl-12 pr-4 py-4 bg-white/50 backdrop-blur-sm border border-gray-200/50 rounded-2xl focus:ring-2 focus:ring-[#00ACB5]/20 focus:border-[#00ACB5]/50 transition-all duration-200"
                    placeholder="Enter your email"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Username
                </label>
                <div className="relative">
                  <User className="absolute left-4 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <input
                    type="text"
                    name="username"
                    value={formData.username}
                    onChange={handleChange}
                    required
                    className="w-full pl-12 pr-4 py-4 bg-white/50 backdrop-blur-sm border border-gray-200/50 rounded-2xl focus:ring-2 focus:ring-[#00ACB5]/20 focus:border-[#00ACB5]/50 transition-all duration-200"
                    placeholder="Choose a username"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Password
                </label>
                <div className="relative">
                  <Lock className="absolute left-4 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <input
                    type="password"
                    name="password"
                    value={formData.password}
                    onChange={handleChange}
                    required
                    className="w-full pl-12 pr-4 py-4 bg-white/50 backdrop-blur-sm border border-gray-200/50 rounded-2xl focus:ring-2 focus:ring-[#00ACB5]/20 focus:border-[#00ACB5]/50 transition-all duration-200"
                    placeholder="Enter your password"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Confirm Password
                </label>
                <div className="relative">
                  <Lock className="absolute left-4 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <input
                    type="password"
                    name="confirmPassword"
                    value={formData.confirmPassword}
                    onChange={handleChange}
                    required
                    className="w-full pl-12 pr-4 py-4 bg-white/50 backdrop-blur-sm border border-gray-200/50 rounded-2xl focus:ring-2 focus:ring-[#00ACB5]/20 focus:border-[#00ACB5]/50 transition-all duration-200"
                    placeholder="Confirm your password"
                  />
                </div>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="relative w-full bg-gradient-to-r from-[#00ACB5] to-[#00929A] hover:from-[#00929A] hover:to-[#007A80] disabled:from-gray-300 disabled:to-gray-400 text-white font-semibold py-4 px-6 rounded-2xl transition-all duration-200 shadow-lg hover:shadow-xl disabled:shadow-none group"
            >
              <span className="relative z-10">
                {loading ? (
                  <div className="flex items-center justify-center">
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                    Creating account...
                  </div>
                ) : (
                  'Create Account'
                )}
              </span>
              {!loading && (
                <div className="absolute -inset-1 bg-gradient-to-r from-[#00ACB5] to-[#00929A] rounded-2xl blur opacity-25 group-hover:opacity-40 transition-opacity"></div>
              )}
            </button>
          </form>

          <div className="mt-8 text-center">
            <p className="text-gray-600">
              Already have an account?{' '}
              <Link
                to="/login"
                className="text-[#00ACB5] hover:text-[#00929A] font-medium transition-colors duration-200"
              >
                Sign in here
              </Link>
            </p>
          </div>
        </div>

        {/* Features */}
        <div className="mt-8 grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div className="bg-white/60 backdrop-blur-sm rounded-xl p-3 border border-white/20 text-center">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-500/20 to-cyan-500/20 rounded-lg flex items-center justify-center mx-auto mb-2">
              <Sparkles className="w-4 h-4 text-blue-600" />
            </div>
            <p className="text-xs text-gray-600">AI-Powered Analysis</p>
          </div>

          <div className="bg-white/60 backdrop-blur-sm rounded-xl p-3 border border-white/20 text-center">
            <div className="w-8 h-8 bg-gradient-to-br from-emerald-500/20 to-teal-500/20 rounded-lg flex items-center justify-center mx-auto mb-2">
              <Bot className="w-4 h-4 text-emerald-600" />
            </div>
            <p className="text-xs text-gray-600">Smart Insights</p>
          </div>

          <div className="bg-white/60 backdrop-blur-sm rounded-xl p-3 border border-white/20 text-center">
            <div className="w-8 h-8 bg-gradient-to-br from-purple-500/20 to-pink-500/20 rounded-lg flex items-center justify-center mx-auto mb-2">
              <Lock className="w-4 h-4 text-purple-600" />
            </div>
            <p className="text-xs text-gray-600">Secure & Private</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Register;