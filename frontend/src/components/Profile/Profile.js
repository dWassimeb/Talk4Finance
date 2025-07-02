// frontend/src/components/Profile/Profile.js
import React, { useState } from 'react';
import { useAuth } from '../../hooks/useAuth';
import { User, Mail, Lock, Save, Eye, EyeOff } from 'lucide-react';
import { authService } from '../../services/auth';

const Profile = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('profile');
  const [showCurrentPassword, setShowCurrentPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });

  const [profileData, setProfileData] = useState({
    username: user?.username || '',
    email: user?.email || '',
  });

  const [passwordData, setPasswordData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
  });

  const handleProfileChange = (e) => {
    setProfileData({
      ...profileData,
      [e.target.name]: e.target.value,
    });
  };

  const handlePasswordChange = (e) => {
    setPasswordData({
      ...passwordData,
      [e.target.name]: e.target.value,
    });
  };

  const handleProfileSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage({ type: '', text: '' });

    try {
      await authService.updateProfile(profileData);
      setMessage({ type: 'success', text: 'Profile updated successfully!' });
    } catch (error) {
      setMessage({
        type: 'error',
        text: error.response?.data?.detail || 'Failed to update profile.'
      });
    } finally {
      setLoading(false);
    }
  };

  const handlePasswordSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage({ type: '', text: '' });

    if (passwordData.newPassword !== passwordData.confirmPassword) {
      setMessage({ type: 'error', text: 'New passwords do not match.' });
      setLoading(false);
      return;
    }

    try {
      await authService.changePassword({
        current_password: passwordData.currentPassword,
        new_password: passwordData.newPassword
      });
      setMessage({ type: 'success', text: 'Password changed successfully!' });
      setPasswordData({ currentPassword: '', newPassword: '', confirmPassword: '' });
    } catch (error) {
      setMessage({
        type: 'error',
        text: error.response?.data?.detail || 'Failed to change password.'
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="bg-white/80 backdrop-blur-sm rounded-3xl shadow-xl border border-white/20 overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-[#00ACB5] to-[#00929A] px-6 py-4">
          <h1 className="text-2xl font-bold text-white">Profile Settings</h1>
          <p className="text-white/80">Manage your account preferences</p>
        </div>

        {/* Tabs */}
        <div className="border-b border-gray-200/50">
          <nav className="flex">
            <button
              onClick={() => setActiveTab('profile')}
              className={`px-6 py-4 text-sm font-medium border-b-2 transition-colors ${
                activeTab === 'profile'
                  ? 'border-[#00ACB5] text-[#00ACB5]'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              Profile Information
            </button>
            <button
              onClick={() => setActiveTab('password')}
              className={`px-6 py-4 text-sm font-medium border-b-2 transition-colors ${
                activeTab === 'password'
                  ? 'border-[#00ACB5] text-[#00ACB5]'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              Change Password
            </button>
          </nav>
        </div>

        <div className="p-6">
          {message.text && (
            <div className={`mb-6 p-4 rounded-lg ${
              message.type === 'success'
                ? 'bg-green-50 text-green-700 border border-green-200'
                : 'bg-red-50 text-red-700 border border-red-200'
            }`}>
              {message.text}
            </div>
          )}

          {activeTab === 'profile' && (
            <form onSubmit={handleProfileSubmit} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Username
                </label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <input
                    type="text"
                    name="username"
                    value={profileData.username}
                    onChange={handleProfileChange}
                    className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#00ACB5] focus:border-transparent"
                    placeholder="Enter your username"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Email
                </label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <input
                    type="email"
                    name="email"
                    value={profileData.email}
                    onChange={handleProfileChange}
                    className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#00ACB5] focus:border-transparent"
                    placeholder="Enter your email"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-gradient-to-r from-[#00ACB5] to-[#00929A] hover:from-[#00929A] hover:to-[#007A80] disabled:from-gray-300 disabled:to-gray-400 text-white font-semibold py-3 px-4 rounded-lg transition-all duration-200"
              >
                <div className="flex items-center justify-center">
                  <Save className="w-5 h-5 mr-2" />
                  {loading ? 'Updating...' : 'Update Profile'}
                </div>
              </button>
            </form>
          )}

          {activeTab === 'password' && (
            <form onSubmit={handlePasswordSubmit} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Current Password
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <input
                    type={showCurrentPassword ? 'text' : 'password'}
                    name="currentPassword"
                    value={passwordData.currentPassword}
                    onChange={handlePasswordChange}
                    className="w-full pl-10 pr-12 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#00ACB5] focus:border-transparent"
                    placeholder="Enter current password"
                  />
                  <button
                    type="button"
                    onClick={() => setShowCurrentPassword(!showCurrentPassword)}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    {showCurrentPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  New Password
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <input
                    type={showNewPassword ? 'text' : 'password'}
                    name="newPassword"
                    value={passwordData.newPassword}
                    onChange={handlePasswordChange}
                    className="w-full pl-10 pr-12 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#00ACB5] focus:border-transparent"
                    placeholder="Enter new password"
                  />
                  <button
                    type="button"
                    onClick={() => setShowNewPassword(!showNewPassword)}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    {showNewPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Confirm New Password
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <input
                    type="password"
                    name="confirmPassword"
                    value={passwordData.confirmPassword}
                    onChange={handlePasswordChange}
                    className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#00ACB5] focus:border-transparent"
                    placeholder="Confirm new password"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-gradient-to-r from-[#00ACB5] to-[#00929A] hover:from-[#00929A] hover:to-[#007A80] disabled:from-gray-300 disabled:to-gray-400 text-white font-semibold py-3 px-4 rounded-lg transition-all duration-200"
              >
                <div className="flex items-center justify-center">
                  <Lock className="w-5 h-5 mr-2" />
                  {loading ? 'Changing...' : 'Change Password'}
                </div>
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};

export default Profile;