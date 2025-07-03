// frontend/src/components/Auth/Register.jsx - Enhanced with better messaging
import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import {
  Bot, Lock, Mail, User, Sparkles, TrendingUp, BarChart3,
  DollarSign, Shield, CheckCircle, AlertCircle, Eye, EyeOff,
  Clock, UserCheck, ArrowRight, RotateCcw
} from 'lucide-react';
import { authService } from '../../services/auth';

const Register = () => {
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    password: '',
    confirmPassword: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [registrationSuccess, setRegistrationSuccess] = useState(false);
  const [passwordChecks, setPasswordChecks] = useState({
    length: false,
    uppercase: false,
    lowercase: false,
    number: false
  });
  const navigate = useNavigate();

  const validatePassword = (password) => {
    const checks = {
      length: password.length >= 8,
      uppercase: /[A-Z]/.test(password),
      lowercase: /[a-z]/.test(password),
      number: /\d/.test(password)
    };
    setPasswordChecks(checks);
    return Object.values(checks).every(Boolean);
  };

  const validateEmail = (email) => {
    return email.endsWith('@docaposte.fr') || email.endsWith('@softeam.fr');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setRegistrationSuccess(false);

    // Validation
    if (!validateEmail(formData.email)) {
      setError('Email must be from @docaposte.fr or @softeam.fr domain');
      setLoading(false);
      return;
    }

    if (!validatePassword(formData.password)) {
      setError('Password does not meet requirements');
      setLoading(false);
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      setLoading(false);
      return;
    }

    try {
      // Call the API directly instead of using auth context
      const response = await authService.register(
        formData.email,
        formData.username,
        formData.password
      );

      // Registration successful - show success state
      setRegistrationSuccess(true);
      setError('');

      // REMOVED: Automatic redirect - now it stays on success page

    } catch (err) {
      console.error('Registration error:', err);

      // Extract error message from response
      let errorMessage = 'Registration failed. Please try again.';

      if (err.response?.data?.detail) {
        errorMessage = err.response.data.detail;
      } else if (err.response?.data?.message) {
        errorMessage = err.response.data.message;
      } else if (err.message) {
        errorMessage = err.message;
      }

      setError(errorMessage);
      setRegistrationSuccess(false);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });

    if (name === 'password') {
      validatePassword(value);
    }

    // Clear error when user starts typing
    if (error) setError('');
  };

  // ENHANCED: Success state with manual navigation buttons
  if (registrationSuccess) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-[#F8FFFE] via-[#E6F7F8] to-[#D4F4F7] flex items-center justify-center px-4 py-8">
        <div className="max-w-md w-full">
          <div className="bg-white/90 backdrop-blur-xl rounded-3xl shadow-2xl border border-white/30 p-8 text-center">
            <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-green-600 rounded-2xl flex items-center justify-center mx-auto mb-6">
              <UserCheck className="w-8 h-8 text-white" />
            </div>

            <h2 className="text-2xl font-bold text-gray-900 mb-4">Registration Successful!</h2>

            <div className="bg-blue-50/80 backdrop-blur-sm border border-blue-200/50 text-blue-700 px-6 py-4 rounded-xl mb-6">
              <div className="flex items-start space-x-3">
                <Clock className="w-6 h-6 flex-shrink-0 mt-0.5" />
                <div className="text-left">
                  <p className="font-semibold mb-2">Account Under Review</p>
                  <p className="text-sm text-blue-600">
                    Your account has been created and is awaiting administrator approval.
                    You'll receive an email notification once your account is activated.
                  </p>
                </div>
              </div>
            </div>

            <div className="space-y-3 text-sm text-gray-600 mb-8">
              <p>✅ Account created successfully</p>
              <p>📧 Admin notification sent</p>
              <p>⏳ Approval pending</p>
            </div>

            {/* ADDED: Manual navigation buttons */}
            <div className="space-y-3">
              <button
                onClick={() => navigate('/login', {
                  state: {
                    message: 'Registration successful! Please wait for admin approval before signing in.',
                    type: 'info'
                  }
                })}
                className="w-full bg-gradient-to-r from-[#00ACB5] to-[#00929A] hover:from-[#00929A] hover:to-[#007A80] text-white font-semibold py-3 px-6 rounded-2xl transition-all duration-200 transform hover:scale-[1.02] flex items-center justify-center group"
              >
                <span>Go to Sign In</span>
                <ArrowRight className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />
              </button>

              <button
                onClick={() => {
                  setRegistrationSuccess(false);
                  setFormData({
                    email: '',
                    username: '',
                    password: '',
                    confirmPassword: ''
                  });
                  setPasswordChecks({
                    length: false,
                    uppercase: false,
                    lowercase: false,
                    number: false
                  });
                }}
                className="w-full text-gray-600 hover:text-gray-800 font-medium py-2 transition-colors flex items-center justify-center group"
              >
                <RotateCcw className="w-4 h-4 mr-2 group-hover:rotate-180 transition-transform duration-300" />
                Register Another Account
              </button>
            </div>

            {/* ADDED: Additional help text */}
            <div className="mt-6 pt-6 border-t border-gray-200">
              <p className="text-xs text-gray-500 mb-2">
                Need help with your registration?
              </p>
              <p className="text-xs text-gray-400">
                Contact administrator:
                <a
                  href="mailto:mohamed-ouassime.el-yamani@docaposte.fr"
                  className="text-[#00ACB5] hover:text-[#00929A] ml-1 underline"
                >
                  mohamed-ouassime.el-yamani@docaposte.fr
                </a>
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

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

      <div className="relative max-w-6xl w-full">
        <div className="grid lg:grid-cols-2 gap-12 items-center">

          {/* Left Side - Branding & Features */}
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
                  Join the Future of <span className="text-[#00ACB5]">Financial Intelligence</span>
                </h2>
                <p className="text-lg text-gray-600 leading-relaxed">
                  Experience next-generation AI-powered financial analysis and insights.
                  Transform how you interact with financial data.
                </p>
              </div>
            </div>

            {/* Feature Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              <div className="group p-6 bg-white/70 backdrop-blur-xl rounded-2xl border border-white/30 hover:bg-white/80 transition-all duration-300 hover:shadow-lg hover:scale-105">
                <div className="w-12 h-12 bg-gradient-to-br from-[#00ACB5]/20 to-[#00929A]/20 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                  <TrendingUp className="w-6 h-6 text-[#00ACB5]" />
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">Smart Analytics</h3>
                <p className="text-sm text-gray-600">Advanced AI-driven financial analysis and trend prediction</p>
              </div>

              <div className="group p-6 bg-white/70 backdrop-blur-xl rounded-2xl border border-white/30 hover:bg-white/80 transition-all duration-300 hover:shadow-lg hover:scale-105">
                <div className="w-12 h-12 bg-gradient-to-br from-[#00ACB5]/20 to-[#00929A]/20 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                  <BarChart3 className="w-6 h-6 text-[#00ACB5]" />
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">Real-time Insights</h3>
                <p className="text-sm text-gray-600">Instant access to comprehensive financial metrics and KPIs</p>
              </div>

              <div className="group p-6 bg-white/70 backdrop-blur-xl rounded-2xl border border-white/30 hover:bg-white/80 transition-all duration-300 hover:shadow-lg hover:scale-105">
                <div className="w-12 h-12 bg-gradient-to-br from-[#00ACB5]/20 to-[#00929A]/20 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                  <DollarSign className="w-6 h-6 text-[#00ACB5]" />
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">Revenue Optimization</h3>
                <p className="text-sm text-gray-600">Identify opportunities and optimize financial performance</p>
              </div>

              <div className="group p-6 bg-white/70 backdrop-blur-xl rounded-2xl border border-white/30 hover:bg-white/80 transition-all duration-300 hover:shadow-lg hover:scale-105">
                <div className="w-12 h-12 bg-gradient-to-br from-[#00ACB5]/20 to-[#00929A]/20 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                  <Shield className="w-6 h-6 text-[#00ACB5]" />
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">Enterprise Security</h3>
                <p className="text-sm text-gray-600">Bank-level security with role-based access control</p>
              </div>
            </div>
          </div>

          {/* Right Side - Registration Form */}
          <div className="relative">
            <div className="bg-white/90 backdrop-blur-xl rounded-3xl shadow-2xl border border-white/30 p-8 relative overflow-hidden">
              {/* Form Background Pattern */}
              <div className="absolute inset-0 bg-gradient-to-br from-[#00ACB5]/5 to-[#00929A]/5"></div>

              {/* Form Content */}
              <div className="relative z-10">
                <div className="text-center mb-8">
                  <div className="w-12 h-12 bg-gradient-to-br from-[#00ACB5] to-[#00929A] rounded-xl flex items-center justify-center mx-auto mb-4">
                    <Sparkles className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="text-2xl font-bold text-gray-900 mb-2">Create Your Account</h3>
                  <p className="text-gray-600">Join the financial intelligence revolution</p>
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
                        placeholder="your.email@docaposte.fr"
                      />
                    </div>
                    <p className="mt-1 text-xs text-gray-500">Must be @docaposte.fr or @softeam.fr domain</p>
                  </div>

                  {/* Username Field */}
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
                        className="w-full pl-12 pr-4 py-3 bg-white/80 backdrop-blur-sm border border-gray-200/50 rounded-xl focus:ring-2 focus:ring-[#00ACB5]/30 focus:border-[#00ACB5] transition-all duration-200"
                        placeholder="Choose a unique username"
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
                        placeholder="Create a strong password"
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                      >
                        {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                      </button>
                    </div>

                    {/* Password Requirements */}
                    <div className="mt-3 space-y-2">
                      <div className="grid grid-cols-2 gap-2 text-xs">
                        <div className={`flex items-center space-x-1 ${passwordChecks.length ? 'text-green-600' : 'text-gray-400'}`}>
                          <CheckCircle className="w-3 h-3" />
                          <span>8+ characters</span>
                        </div>
                        <div className={`flex items-center space-x-1 ${passwordChecks.uppercase ? 'text-green-600' : 'text-gray-400'}`}>
                          <CheckCircle className="w-3 h-3" />
                          <span>Uppercase</span>
                        </div>
                        <div className={`flex items-center space-x-1 ${passwordChecks.lowercase ? 'text-green-600' : 'text-gray-400'}`}>
                          <CheckCircle className="w-3 h-3" />
                          <span>Lowercase</span>
                        </div>
                        <div className={`flex items-center space-x-1 ${passwordChecks.number ? 'text-green-600' : 'text-gray-400'}`}>
                          <CheckCircle className="w-3 h-3" />
                          <span>Number</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Confirm Password Field */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Confirm Password
                    </label>
                    <div className="relative">
                      <Lock className="absolute left-4 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                      <input
                        type={showConfirmPassword ? "text" : "password"}
                        name="confirmPassword"
                        value={formData.confirmPassword}
                        onChange={handleChange}
                        required
                        className="w-full pl-12 pr-12 py-3 bg-white/80 backdrop-blur-sm border border-gray-200/50 rounded-xl focus:ring-2 focus:ring-[#00ACB5]/30 focus:border-[#00ACB5] transition-all duration-200"
                        placeholder="Confirm your password"
                      />
                      <button
                        type="button"
                        onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                        className="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                      >
                        {showConfirmPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
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
                          Creating account...
                        </>
                      ) : (
                        <>
                          <Sparkles className="w-5 h-5 mr-2" />
                          Create Account
                        </>
                      )}
                    </span>
                    {!loading && (
                      <div className="absolute inset-0 bg-gradient-to-r from-[#00ACB5] to-[#00929A] transform scale-x-0 group-hover:scale-x-100 transition-transform origin-left duration-300"></div>
                    )}
                  </button>

                  {/* Info Notice */}
                  <div className="bg-blue-50/80 backdrop-blur-sm border border-blue-200/50 text-blue-700 px-4 py-3 rounded-xl">
                    <div className="flex items-start space-x-2">
                      <Shield className="w-5 h-5 flex-shrink-0 mt-0.5" />
                      <div className="text-sm">
                        <p className="font-medium">Secure Registration Process</p>
                        <p className="text-blue-600">All accounts require administrator approval for security purposes.</p>
                      </div>
                    </div>
                  </div>
                </form>

                {/* Login Link */}
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
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Register;