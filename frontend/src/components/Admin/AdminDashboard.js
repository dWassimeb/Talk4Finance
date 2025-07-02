// frontend/src/components/Admin/AdminDashboard.jsx
import React, { useState, useEffect } from 'react';
import {
  X, Users, UserCheck, UserX, Clock, Shield, Mail, Calendar,
  Search, Filter, MoreVertical, Crown, AlertCircle, CheckCircle2,
  XCircle, Pause, RefreshCw, Eye, Trash2, Settings, UserPlus
} from 'lucide-react';
import { authService } from '../../services/auth';
import { useAuth } from '../../hooks/useAuth';

const AdminDashboard = ({ isOpen, onClose }) => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('users');
  const [users, setUsers] = useState([]);
  const [pendingUsers, setPendingUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [message, setMessage] = useState({ type: '', text: '' });
  const [selectedUser, setSelectedUser] = useState(null);
  const [showActionModal, setShowActionModal] = useState(false);
  const [actionType, setActionType] = useState('');
  const [rejectionReason, setRejectionReason] = useState('');

  useEffect(() => {
    if (isOpen) {
      fetchUsers();
      fetchPendingUsers();
    }
  }, [isOpen]);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const response = await authService.getAllUsers();
      setUsers(response);
    } catch (error) {
      setMessage({
        type: 'error',
        text: 'Failed to fetch users'
      });
    } finally {
      setLoading(false);
    }
  };

  const fetchPendingUsers = async () => {
    try {
      const response = await authService.getPendingUsers();
      setPendingUsers(response);
    } catch (error) {
      console.error('Failed to fetch pending users:', error);
    }
  };

  const handleUserAction = async (userId, action, reason = null) => {
    try {
      setLoading(true);
      if (action === 'approve' || action === 'reject') {
        await authService.approveUser(userId, action, reason);
      } else if (action === 'delete') {
        await authService.deleteUser(userId);
      } else if (action === 'demote') {
        await authService.updateUserRole(userId, 'user');
      } else {
        // For status updates (suspend, activate, etc.)
        await authService.updateUserStatus(userId, action);
      }

      setMessage({
        type: 'success',
        text: `User ${action}d successfully!`
      });

      fetchUsers();
      fetchPendingUsers();
      setShowActionModal(false);
      setSelectedUser(null);
      setRejectionReason('');
    } catch (error) {
      setMessage({
        type: 'error',
        text: error.response?.data?.detail || `Failed to ${action} user`
      });
    } finally {
      setLoading(false);
    }
  };

  const handlePromoteToAdmin = async (userId) => {
    try {
      setLoading(true);
      // This would require a new backend endpoint
      await authService.updateUserRole(userId, 'admin');
      setMessage({
        type: 'success',
        text: 'User promoted to admin successfully!'
      });
      fetchUsers();
    } catch (error) {
      setMessage({
        type: 'error',
        text: 'Failed to promote user'
      });
    } finally {
      setLoading(false);
    }
  };

  const openActionModal = (user, action) => {
    setSelectedUser(user);
    setActionType(action);
    setShowActionModal(true);
  };

  const filteredUsers = users.filter(user => {
    const matchesSearch = user.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         user.email.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || user.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const getStatusIcon = (status) => {
    switch (status) {
      case 'approved': return <CheckCircle2 className="w-4 h-4 text-green-500" />;
      case 'pending': return <Clock className="w-4 h-4 text-yellow-500" />;
      case 'rejected': return <XCircle className="w-4 h-4 text-red-500" />;
      case 'suspended': return <Pause className="w-4 h-4 text-orange-500" />;
      default: return <AlertCircle className="w-4 h-4 text-gray-500" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'approved': return 'bg-green-100 text-green-800';
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'rejected': return 'bg-red-100 text-red-800';
      case 'suspended': return 'bg-orange-100 text-orange-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-7xl max-h-[95vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 bg-gradient-to-r from-[#00ACB5] to-[#00929A]">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-white/20 rounded-xl flex items-center justify-center">
              <Shield className="w-6 h-6 text-white" />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-white">Admin Dashboard</h2>
              <p className="text-white/80 text-sm">Manage users and system settings</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-white/20 rounded-xl transition-colors duration-200 text-white"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-gray-200 bg-gray-50/50">
          <button
            onClick={() => setActiveTab('users')}
            className={`flex-1 px-6 py-4 text-sm font-medium transition-colors duration-200 ${
              activeTab === 'users'
                ? 'text-[#00ACB5] border-b-2 border-[#00ACB5] bg-white'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            <Users className="w-4 h-4 inline mr-2" />
            All Users ({users.length})
          </button>
          <button
            onClick={() => setActiveTab('pending')}
            className={`flex-1 px-6 py-4 text-sm font-medium transition-colors duration-200 ${
              activeTab === 'pending'
                ? 'text-[#00ACB5] border-b-2 border-[#00ACB5] bg-white'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            <Clock className="w-4 h-4 inline mr-2" />
            Pending Approval ({pendingUsers.length})
          </button>
          <button
            onClick={() => setActiveTab('settings')}
            className={`flex-1 px-6 py-4 text-sm font-medium transition-colors duration-200 ${
              activeTab === 'settings'
                ? 'text-[#00ACB5] border-b-2 border-[#00ACB5] bg-white'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            <Settings className="w-4 h-4 inline mr-2" />
            Settings
          </button>
        </div>

        {/* Content */}
        <div className="p-6 max-h-[70vh] overflow-y-auto">
          {/* Message */}
          {message.text && (
            <div className={`mb-6 p-4 rounded-xl flex items-center space-x-2 ${
              message.type === 'success'
                ? 'bg-green-50 text-green-700 border border-green-200'
                : 'bg-red-50 text-red-700 border border-red-200'
            }`}>
              {message.type === 'success' ?
                <CheckCircle2 className="w-5 h-5" /> :
                <AlertCircle className="w-5 h-5" />
              }
              <span>{message.text}</span>
            </div>
          )}

          {/* Users Tab */}
          {activeTab === 'users' && (
            <div className="space-y-6">
              {/* Filters */}
              <div className="flex flex-wrap gap-4">
                <div className="flex-1 min-w-64">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                    <input
                      type="text"
                      placeholder="Search users..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-[#00ACB5] focus:border-transparent"
                    />
                  </div>
                </div>
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-[#00ACB5] focus:border-transparent"
                >
                  <option value="all">All Status</option>
                  <option value="approved">Approved</option>
                  <option value="pending">Pending</option>
                  <option value="rejected">Rejected</option>
                  <option value="suspended">Suspended</option>
                </select>
                <button
                  onClick={fetchUsers}
                  disabled={loading}
                  className="flex items-center space-x-2 px-4 py-3 bg-[#00ACB5] hover:bg-[#00929A] disabled:bg-gray-300 text-white rounded-xl transition-all duration-200"
                >
                  <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                  <span>Refresh</span>
                </button>
              </div>

              {/* Users List */}
              <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">User</th>
                        <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                        <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Role</th>
                        <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Joined</th>
                        <th className="px-6 py-4 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {filteredUsers.map((userItem) => (
                        <tr key={userItem.id} className="hover:bg-gray-50">
                          <td className="px-6 py-4">
                            <div className="flex items-center space-x-3">
                              <div className="w-10 h-10 bg-gradient-to-br from-[#00ACB5] to-[#00929A] rounded-lg flex items-center justify-center">
                                {userItem.role === 'admin' ?
                                  <div className="w-5 h-5 bg-gradient-to-br from-amber-500 to-yellow-600 rounded flex items-center justify-center">
                                    <Crown className="w-3 h-3 text-white" />
                                  </div> :
                                  <Users className="w-5 h-5 text-white" />
                                }
                              </div>
                              <div>
                                <p className="text-sm font-medium text-gray-900">{userItem.username}</p>
                                <p className="text-sm text-gray-500">{userItem.email}</p>
                              </div>
                            </div>
                          </td>
                          <td className="px-6 py-4">
                            <div className="flex items-center space-x-2">
                              {getStatusIcon(userItem.status)}
                              <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(userItem.status)}`}>
                                {userItem.status}
                              </span>
                            </div>
                          </td>
                          <td className="px-6 py-4">
                            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                              userItem.role === 'admin' ? 'bg-gradient-to-r from-amber-100 to-yellow-100 text-amber-800 border border-amber-200' : 'bg-blue-100 text-blue-800'
                            }`}>
                              {userItem.role}
                            </span>
                          </td>
                          <td className="px-6 py-4 text-sm text-gray-500">
                            {new Date(userItem.created_at).toLocaleDateString()}
                          </td>
                          <td className="px-6 py-4 text-right">
                            <div className="flex items-center justify-end space-x-2">
                              {userItem.status === 'pending' && (
                                <>
                                  <button
                                    onClick={() => handleUserAction(userItem.id, 'approve')}
                                    className="p-2 text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                                    title="Approve User"
                                  >
                                    <UserCheck className="w-4 h-4" />
                                  </button>
                                  <button
                                    onClick={() => openActionModal(userItem, 'reject')}
                                    className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                                    title="Reject User"
                                  >
                                    <UserX className="w-4 h-4" />
                                  </button>
                                </>
                              )}
                              {userItem.status === 'approved' && userItem.role !== 'admin' && (
                                <>
                                  <button
                                    onClick={() => handleUserAction(userItem.id, 'suspended')}
                                    className="p-2 text-orange-600 hover:bg-orange-50 rounded-lg transition-colors"
                                    title="Suspend User"
                                  >
                                    <Pause className="w-4 h-4" />
                                  </button>
                                  <button
                                    onClick={() => handlePromoteToAdmin(userItem.id)}
                                    className="p-2 text-amber-600 hover:bg-gradient-to-r hover:from-amber-50 hover:to-yellow-50 rounded-lg transition-all duration-200"
                                    title="Promote to Admin"
                                  >
                                    <div className="w-4 h-4 bg-gradient-to-br from-amber-500 to-yellow-600 rounded flex items-center justify-center">
                                      <Crown className="w-2.5 h-2.5 text-white" />
                                    </div>
                                  </button>
                                  <button
                                    onClick={() => openActionModal(userItem, 'delete')}
                                    className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                                    title="Delete User"
                                  >
                                    <Trash2 className="w-4 h-4" />
                                  </button>
                                </>
                              )}
                              {userItem.status === 'approved' && userItem.role === 'admin' && userItem.id !== user?.id && (
                                <>
                                  <button
                                    onClick={() => openActionModal(userItem, 'demote')}
                                    className="p-2 text-orange-600 hover:bg-orange-50 rounded-lg transition-colors"
                                    title="Remove Admin Privileges"
                                  >
                                    <UserX className="w-4 h-4" />
                                  </button>
                                  <button
                                    onClick={() => openActionModal(userItem, 'delete')}
                                    className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                                    title="Delete User"
                                  >
                                    <Trash2 className="w-4 h-4" />
                                  </button>
                                </>
                              )}
                              {userItem.status === 'suspended' && (
                                <button
                                  onClick={() => handleUserAction(userItem.id, 'approved')}
                                  className="p-2 text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                                  title="Reactivate User"
                                >
                                  <UserCheck className="w-4 h-4" />
                                </button>
                              )}
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* Pending Users Tab */}
          {activeTab === 'pending' && (
            <div className="space-y-6">
              {pendingUsers.length === 0 ? (
                <div className="text-center py-12">
                  <UserPlus className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No Pending Users</h3>
                  <p className="text-gray-500">All user registrations have been processed.</p>
                </div>
              ) : (
                <div className="grid gap-4">
                  {pendingUsers.map((userItem) => (
                    <div key={userItem.id} className="bg-white rounded-xl border border-gray-200 p-6">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                          <div className="w-12 h-12 bg-yellow-100 rounded-xl flex items-center justify-center">
                            <Clock className="w-6 h-6 text-yellow-600" />
                          </div>
                          <div>
                            <h3 className="text-lg font-medium text-gray-900">{userItem.username}</h3>
                            <p className="text-gray-500">{userItem.email}</p>
                            <p className="text-sm text-gray-400">
                              Registered: {new Date(userItem.created_at).toLocaleDateString()}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-3">
                          <button
                            onClick={() => handleUserAction(userItem.id, 'approve')}
                            disabled={loading}
                            className="flex items-center space-x-2 px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-300 text-white rounded-lg transition-all duration-200"
                          >
                            <UserCheck className="w-4 h-4" />
                            <span>Approve</span>
                          </button>
                          <button
                            onClick={() => openActionModal(userItem, 'reject')}
                            disabled={loading}
                            className="flex items-center space-x-2 px-4 py-2 bg-red-600 hover:bg-red-700 disabled:bg-gray-300 text-white rounded-lg transition-all duration-200"
                          >
                            <UserX className="w-4 h-4" />
                            <span>Reject</span>
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Settings Tab */}
          {activeTab === 'settings' && (
            <div className="space-y-6">
              <div className="bg-white rounded-xl border border-gray-200 p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Email Configuration</h3>
                <p className="text-gray-500 mb-4">Configure email settings for user notifications.</p>
                <button className="px-4 py-2 bg-[#00ACB5] hover:bg-[#00929A] text-white rounded-lg transition-colors">
                  Configure Email Settings
                </button>
              </div>

              <div className="bg-white rounded-xl border border-gray-200 p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">System Settings</h3>
                <p className="text-gray-500 mb-4">Manage system-wide configurations and preferences.</p>
                <button className="px-4 py-2 bg-[#00ACB5] hover:bg-[#00929A] text-white rounded-lg transition-colors">
                  Manage Settings
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Action Modal */}
      {showActionModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-60 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md">
            <div className="p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                {actionType === 'reject' ? 'Reject User' :
                 actionType === 'delete' ? 'Delete User Account' :
                 actionType === 'demote' ? 'Remove Admin Privileges' :
                 'Confirm Action'}
              </h3>
              <p className="text-gray-500 mb-4">
                {actionType === 'reject' ?
                  `Are you sure you want to reject ${selectedUser?.username}?` :
                 actionType === 'delete' ?
                  `⚠️ This will permanently delete ${selectedUser?.username} and ALL their data (conversations, messages, etc.). This action cannot be undone!` :
                 actionType === 'demote' ?
                  `Remove admin privileges from ${selectedUser?.username}? They will become a regular user.` :
                  `Are you sure you want to ${actionType} ${selectedUser?.username}?`
                }
              </p>

              {actionType === 'reject' && (
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Rejection Reason
                  </label>
                  <textarea
                    value={rejectionReason}
                    onChange={(e) => setRejectionReason(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#00ACB5] focus:border-transparent"
                    rows="3"
                    placeholder="Provide a reason for rejection..."
                  />
                </div>
              )}

              <div className="flex items-center justify-end space-x-3">
                <button
                  onClick={() => setShowActionModal(false)}
                  className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={() => handleUserAction(selectedUser.id, actionType, rejectionReason)}
                  disabled={loading || (actionType === 'reject' && !rejectionReason.trim())}
                  className={`px-4 py-2 disabled:bg-gray-300 text-white rounded-lg transition-colors ${
                    actionType === 'delete' ? 'bg-red-600 hover:bg-red-700' :
                    actionType === 'demote' ? 'bg-orange-600 hover:bg-orange-700' :
                    'bg-red-600 hover:bg-red-700'
                  }`}
                >
                  {loading ? 'Processing...' :
                   actionType === 'delete' ? 'Delete Permanently' :
                   actionType === 'demote' ? 'Remove Admin' :
                   'Confirm'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminDashboard;