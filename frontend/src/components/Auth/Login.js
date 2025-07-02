// frontend/src/components/Auth/Login.js
import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import {
  Bot, Lock, Mail, Sparkles, TrendingUp, BarChart3,
  DollarSign, Shield, Eye, EyeOff, AlertCircle, LogIn,
  Zap, Target, Brain, Rocket
} from 'lucide-react';

const Login = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    const result = await login(formData.email, formData.password);

    if (result.success) {
      navigate('/chat');
    } else {
      setError(result.error || 'Login failed. Please try again.');
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
    <div className="min-h-screen bg-gradient-to-br from-[#F8FFFE] via-[#E6F7F8] to-[#D4F4F7] flex items-center justify-center px-4 py-8 relative overflow-hidden">
      {/* Animated Background Elements */}
      <div className="absolute inset-0">
        <div className="absolute top-20 left-20 w-96 h-96 bg-gradient-to-r from-[#00ACB5]/30 to-[#00929A]/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-20 right-20 w-80 h-80 bg-gradient-to-r from-[#00929A]/20 to-[#007A80]/30 rounded-full blur-3xl animate-pulse" style={{animationDelay: '1s'}}></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-72 h-72 bg-gradient-to-r from-[#00ACB5]/10 to-[#00929A]/10 rounded-full blur-3xl animate-pulse" style={{animationDelay: '2s'}}></div>
      </div>

      {/* Floating Elements */}
      <div className="absolute top-10 left-10 w-4 h-4 bg-[#00ACB5]/60 rounded-full animate-bounce"></div>
      <div className="absolute top-32 right-20 w-3 h-3 bg-[#00929A]/60 rounded-full animate-bounce" style={{animationDelay: '0.5s'}}></div>
      <div className="absolute bottom-32 left-32 w-5 h-5 bg-[#007A80]/60 rounded-full animate-bounce" style={{animationDelay: '1s'}}></div>
      <div className="absolute top-1/4 right-1/3 w-2 h-2 bg-[#00ACB5]/40 rounded-full animate-bounce" style={{animationDelay: '1.5s'}}></div>

      <div className="relative max-w-6xl w-full">
        <div className="grid lg:grid-cols-2 gap-12 items-center">

          {/* Left Side - Welcome Back & Stats */}
          <div className="space-y-8 text-center lg:text-left">
            {/* Main Branding */}
            <div className="space-y-6">
              <div className="flex items-center justify-center lg:justify-start space-x-3">
                <div className="relative">
                  <div className="w-16 h-16 bg-gradient-to-br from-[#00ACB5] to-[#00929A] rounded-2xl flex items-center justify-center">
                    <Bot className="w-8 h-8 text-white" />
                  </div>
                  <div className="absolute -inset-1 bg-gradient-to-r from-[#00ACB5] to-[#00929A] rounded-2xl blur opacity-25 animate-pulse"></div>
                </div>
                <div>
                  <h1 className="text-4xl font-bold bg-gradient-to-r from-[#00ACB5] to-[#00929A] bg-clip-text text-transparent">
                    Talk4Finance
                  </h1>
                  <p className="text-gray-600">Your AI Financial Agent</p>
                </div>
              </div>

              <div className="space-y-4">
                <h2 className="text-3xl font-bold text-gray-900">
                  Welcome Back to the <span className="text-[#00ACB5]">Future of Finance</span>
                </h2>
                <p className="text-lg text-gray-600 leading-relaxed">
                  Continue your journey with AI-powered financial intelligence.
                  Access insights, analytics, and data like never before.
                </p>
              </div>
            </div>

            {/* Stats Cards */}
            <div className="grid grid-cols-2 gap-4">
              <div className="group p-6 bg-white/70 backdrop-blur-xl rounded-2xl border border-white/30 hover:bg-white/80 transition-all duration-300 hover:shadow-lg hover:scale-105 text-center">
                <div className="w-12 h-12 bg-gradient-to-br from-[#00ACB5]/20 to-[#00929A]/20 rounded-xl flex items-center justify-center mx-auto mb-3 group-hover:scale-110 transition-transform">
                  <Zap className="w-6 h-6 text-[#00ACB5]" />
                </div>
                <div className="text-2xl font-bold text-gray-900 mb-1">10x</div>
                <p className="text-sm text-gray-600">Faster Analysis</p>
              </div>

              <div className="group p-6 bg-white/70 backdrop-blur-xl rounded-2xl border border-white/30 hover:bg-white/80 transition-all duration-300 hover:shadow-lg hover:scale-105 text-center">
                <div className="w-12 h-12 bg-gradient-to-br from-[#00ACB5]/20 to-[#00929A]/20 rounded-xl flex items-center justify-center mx-auto mb-3 group-hover:scale-110 transition-transform">
                  <Target className="w-6 h-6 text-[#00ACB5]" />
                </div>
                <div className="text-2xl font-bold text-gray-900 mb-1">95%</div>
                <p className="text-sm text-gray-600">Accuracy Rate</p>
              </div>

              <div className="group p-6 bg-white/70 backdrop-blur-xl rounded-2xl border border-white/30 hover:bg-white/80 transition-all duration-300 hover:shadow-lg hover:scale-105 text-center">
                <div className="w-12 h-12 bg-gradient-to-br from-[#00ACB5]/20 to-[#00929A]/20 rounded-xl flex items-center justify-center mx-auto mb-3 group-hover:scale-110 transition-transform">
                  <Brain className="w-6 h-6 text-[#00ACB5]" />
                </div>
                <div className="text-2xl font-bold text-gray-900 mb-1">AI</div>
                <p className="text-sm text-gray-600">Powered Insights</p>
              </div>

              <div className="group p-6 bg-white/70 backdrop-blur-xl rounded-2xl border border-white/30 hover:bg-white/80 transition-all duration-300 hover:shadow-lg hover:scale-105 text-center">
                <div className="w-12 h-12 bg-gradient-to-br from-[#00ACB5]/20 to-[#00929A]/20 rounded-xl flex items-center justify-center mx-auto mb-3 group-hover:scale-110 transition-transform">
                  <Rocket className="w-6 h-6 text-[#00ACB5]" />
                </div>
                <div className="text-2xl font-bold text-gray-900 mb-1">24/7</div>
                <p className="text-sm text-gray-600">Always Available</p>
              </div>
            </div>

            {/* Feature Highlights */}
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-gray-900 flex items-center">
                <Sparkles className="w-5 h-5 text-[#00ACB5] mr-2" />
                What's New Today
              </h3>
              <div className="space-y-3">
                <div className="flex items-center space-x-3 p-3 bg-white/60 backdrop-blur-sm rounded-xl border border-white/20">
                  <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
                    <TrendingUp className="w-4 h-4 text-green-600" />
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">Enhanced Revenue Analytics</p>
                    <p className="text-xs text-gray-600">New predictive models available</p>
                  </div>
                </div>
                <div className="flex items-center space-x-3 p-3 bg-white/60 backdrop-blur-sm rounded-xl border border-white/20">
                  <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                    <BarChart3 className="w-4 h-4 text-blue-600" />
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">Real-time Dashboard Updates</p>
                    <p className="text-xs text-gray-600">Live data streaming now active</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Right Side - Login Form */}
          <div className="relative">
            <div className="bg-white/90 backdrop-blur-xl rounded-3xl shadow-2xl border border-white/30 p-8 relative overflow-hidden">
              {/* Form Background Pattern */}
              <div className="absolute inset-0 bg-gradient-to-br from-[#00ACB5]/5 to-[#00929A]/5"></div>

              {/* Form Content */}
              <div className="relative z-10">
                <div className="text-center mb-8">
                  <div className="w-12 h-12 bg-gradient-to-br from-[#00ACB5] to-[#00929A] rounded-xl flex items-center justify-center mx-auto mb-4">
                    <LogIn className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="text-2xl font-bold text-gray-900 mb-2">Sign In</h3>
                  <p className="text-gray-600">Access your financial intelligence dashboard</p>
                </div>

                <form onSubmit={handleSubmit} className="space-y-6">
                  {error && (
                    <div className="bg-red-50/80 backdrop-blur-sm border border-red-200/50 text-red-700 px-4 py-3 rounded-xl flex items-start space-x-2">
                      <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
                      <span className="text-sm">{error}</span>
                    </div>
                  )}

                  {/* Email Field */}
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
                        className="w-full pl-12 pr-4 py-3 bg-white/80 backdrop-blur-sm border border-gray-200/50 rounded-xl focus:ring-2 focus:ring-[#00ACB5]/30 focus:border-[#00ACB5] transition-all duration-200"
                        placeholder="Enter your email"
                      />
                    </div>
                  </div>

                  {/* Password Field */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Password
                    </label>
                    <div className="relative">
                      <Lock className="absolute left-4 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                      <input
                        type={showPassword ? "text" : "password"}
                        name="password"
                        value={formData.password}
                        onChange={handleChange}
                        required
                        className="w-full pl-12 pr-12 py-3 bg-white/80 backdrop-blur-sm border border-gray-200/50 rounded-xl focus:ring-2 focus:ring-[#00ACB5]/30 focus:border-[#00ACB5] transition-all duration-200"
                        placeholder="Enter your password"
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                      >
                        {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                      </button>
                    </div>
                  </div>

                  {/* Submit Button */}
                  <button
                    type="submit"
                    disabled={loading}
                    className="relative w-full bg-gradient-to-r from-[#00ACB5] to-[#00929A] hover:from-[#00929A] hover:to-[#007A80] disabled:from-gray-300 disabled:to-gray-400 text-white font-semibold py-3 px-6 rounded-xl transition-all duration-200 shadow-lg hover:shadow-xl disabled:shadow-none group overflow-hidden"
                  >
                    <span className="relative z-10 flex items-center justify-center">
                      {loading ? (
                        <>
                          <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                          Signing in...
                        </>
                      ) : (
                        <>
                          <LogIn className="w-5 h-5 mr-2" />
                          Sign In
                        </>
                      )}
                    </span>
                    {!loading && (
                      <div className="absolute inset-0 bg-gradient-to-r from-[#00ACB5] to-[#00929A] transform scale-x-0 group-hover:scale-x-100 transition-transform origin-left duration-300"></div>
                    )}
                  </button>

                  {/* Quick Access Notice */}
                  <div className="bg-blue-50/80 backdrop-blur-sm border border-blue-200/50 text-blue-700 px-4 py-3 rounded-xl">
                    <div className="flex items-start space-x-2">
                      <Shield className="w-5 h-5 flex-shrink-0 mt-0.5" />
                      <div className="text-sm">
                        <p className="font-medium">Secure Access</p>
                        <p className="text-blue-600">Your data is protected with enterprise-grade security and encryption.</p>
                      </div>
                    </div>
                  </div>
                </form>

                {/* Register Link */}
                <div className="mt-8 text-center">
                  <p className="text-gray-600">
                    Don't have an account?{' '}
                    <Link
                      to="/register"
                      className="text-[#00ACB5] hover:text-[#00929A] font-medium transition-colors duration-200"
                    >
                      Create one here
                    </Link>
                  </p>
                </div>

                {/* Additional Help */}
                <div className="mt-6 pt-6 border-t border-gray-200/50">
                  <div className="text-center space-y-2">
                    <p className="text-xs text-gray-500">Need help accessing your account?</p>
                    <div className="flex justify-center space-x-4 text-xs">
                      <button className="text-[#00ACB5] hover:text-[#00929A] transition-colors">
                        Forgot Password?
                      </button>
                      <span className="text-gray-300">|</span>
                      <button className="text-[#00ACB5] hover:text-[#00929A] transition-colors">
                        Contact Support
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;