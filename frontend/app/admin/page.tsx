'use client';

import { useUser, SignIn, SignOutButton } from '@clerk/nextjs';
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { API_ENDPOINTS } from '../lib/api';

interface User {
  id: number;
  clerk_user_id: string;
  email: string | null;
  name: string | null;
  created_at: string;
  body_type: string | null;
  gender: string | null;
  classification_date: string | null;
  workout_plan: string | null;
  meal_plan: string | null;
  plan_date: string | null;
}

export default function AdminDashboard() {
  const { user, isLoaded } = useUser();
  const router = useRouter();
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editingUser, setEditingUser] = useState<string | null>(null);
  const [editForm, setEditForm] = useState({ email: '', name: '' });
  const [clerkKeyConfigured, setClerkKeyConfigured] = useState<boolean | null>(null);
  const [isAdmin, setIsAdmin] = useState<boolean | null>(null);
  const [checkingAdmin, setCheckingAdmin] = useState(true);

  // Check if user is admin
  useEffect(() => {
    const checkAdminStatus = async () => {
      if (!isLoaded) {
        return;
      }

      if (!user?.id) {
        // User not signed in
        setIsAdmin(false);
        setCheckingAdmin(false);
        return;
      }

      try {
        const response = await fetch(API_ENDPOINTS.admin.check, {
          headers: {
            'Authorization': `Bearer ${user.id}`,
          },
        });

        if (response.ok) {
          const data = await response.json();
          setIsAdmin(data.is_admin || false);
        } else {
          setIsAdmin(false);
        }
      } catch (err) {
        console.error('Error checking admin status:', err);
        setIsAdmin(false);
      } finally {
        setCheckingAdmin(false);
      }
    };

    checkAdminStatus();
  }, [isLoaded, user?.id]);

  useEffect(() => {
    if (isLoaded && user?.id && isAdmin === true) {
      fetchUsers();
      checkClerkKeyStatus();
    }
  }, [isLoaded, user?.id, isAdmin]);

  const checkClerkKeyStatus = async () => {
    try {
      const response = await fetch(API_ENDPOINTS.admin.health, {
        headers: {
          'Authorization': `Bearer ${user?.id}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setClerkKeyConfigured(data.clerk_secret_key_configured || false);
      }
    } catch (err) {
      console.error('Error checking Clerk key status:', err);
    }
  };

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const response = await fetch(API_ENDPOINTS.admin.users, {
        headers: {
          'Authorization': `Bearer ${user?.id}`,
        },
      });

      if (!response.ok) {
        if (response.status === 403) {
          setError('Access denied. Admin privileges required.');
          return;
        }
        throw new Error('Failed to fetch users');
      }

      const data = await response.json();
      setUsers(data.users || []);
      setError(null);
    } catch (err) {
      console.error('Error fetching users:', err);
      setError(err instanceof Error ? err.message : 'Failed to load users');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdate = async (clerkUserId: string) => {
    try {
      const response = await fetch(`${API_ENDPOINTS.admin.users}/${clerkUserId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${user?.id}`,
        },
        body: JSON.stringify({
          clerk_user_id: clerkUserId,
          email: editForm.email || null,
          name: editForm.name || null,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to update user');
      }

      await fetchUsers();
      setEditingUser(null);
      setEditForm({ email: '', name: '' });
      alert('User updated successfully!');
    } catch (err) {
      console.error('Error updating user:', err);
      alert('Failed to update user. Please try again.');
    }
  };

  const handleDelete = async (clerkUserId: string) => {
    if (!confirm(`Are you sure you want to delete user ${clerkUserId}? This will delete them from both the database and Clerk.`)) {
      return;
    }

    try {
      const response = await fetch(`${API_ENDPOINTS.admin.users}/${clerkUserId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${user?.id}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to delete user');
      }

      await fetchUsers();
      alert('User deleted successfully!');
    } catch (err) {
      console.error('Error deleting user:', err);
      alert('Failed to delete user. Please try again.');
    }
  };

  const startEdit = (userData: User) => {
    setEditingUser(userData.clerk_user_id);
    setEditForm({
      email: userData.email || '',
      name: userData.name || '',
    });
  };

  if (!isLoaded || checkingAdmin) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-900 via-gray-900 to-pink-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading...</div>
      </div>
    );
  }

  // If user is not signed in, show sign in
  if (!user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-900 via-gray-900 to-pink-900 flex items-center justify-center p-4">
        <div className="bg-white/10 backdrop-blur-xl rounded-3xl p-8 max-w-md w-full border border-white/20">
          <h2 className="text-2xl font-bold text-white mb-4 text-center">🔐 Admin Access Required</h2>
          <p className="text-gray-300 text-center mb-6">
            Please sign in with an admin account to access the admin dashboard.
          </p>
          <div className="flex justify-center">
            <SignIn 
              routing="hash"
              appearance={{
                elements: {
                  rootBox: "mx-auto",
                  card: "bg-transparent shadow-none",
                }
              }}
            />
          </div>
        </div>
      </div>
    );
  }

  // If user is signed in but not admin, show admin login prompt
  if (isAdmin === false) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-900 via-gray-900 to-pink-900 flex items-center justify-center p-4">
        <div className="bg-white/10 backdrop-blur-xl rounded-3xl p-8 max-w-md w-full border border-white/20">
          <h2 className="text-2xl font-bold text-white mb-4 text-center">🔐 Admin Access Required</h2>
          <p className="text-gray-300 text-center mb-4">
            You are currently signed in as a regular user. To access the admin dashboard, please sign out and sign in with an admin account.
          </p>
          <div className="space-y-4">
            <div className="bg-yellow-500/20 border border-yellow-500/50 rounded-lg p-4">
              <p className="text-yellow-200 text-sm text-center">
                Current User: <span className="font-mono text-xs">{user.emailAddresses[0]?.emailAddress || user.id}</span>
              </p>
            </div>
            <div className="flex flex-col gap-3">
              <button
                onClick={() => router.push('/dashboard')}
                className="bg-white/10 hover:bg-white/20 text-white px-4 py-2 rounded-lg border border-white/20 transition-all"
              >
                ← Back to Dashboard
              </button>
              <div className="bg-red-500/20 border border-red-500/50 rounded-lg p-3">
                <p className="text-red-200 text-sm text-center mb-2">Sign out to use admin account:</p>
                <div className="flex justify-center">
                  <SignOutButton>
                    <button className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg transition-all">
                      Sign Out
                    </button>
                  </SignOutButton>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-gray-900 to-pink-900">
      {/* Header */}
      <div className="bg-black/20 backdrop-blur-xl border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 py-6 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-400 via-pink-400 to-purple-600 bg-clip-text text-transparent">
              🔐 Admin Dashboard
            </h1>
            <p className="text-gray-400 text-sm mt-1">Manage users and their data</p>
          </div>
          <button
            onClick={() => router.push('/dashboard')}
            className="bg-white/10 hover:bg-white/20 text-white px-4 py-2 rounded-lg border border-white/20 transition-all"
          >
            ← Back to Dashboard
          </button>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Admin Clerk User ID */}
        <div className="bg-white/10 backdrop-blur-xl border border-white/20 rounded-xl p-4 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm mb-1">Admin Clerk User ID</p>
              <p className="text-white font-mono text-lg">{user?.id || 'Not available'}</p>
            </div>
            {user?.id && (
              <button
                onClick={() => {
                  navigator.clipboard.writeText(user.id);
                  alert('✅ Clerk User ID copied to clipboard!');
                }}
                className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg transition-all"
              >
                📋 Copy
              </button>
            )}
          </div>
        </div>

        {/* Clerk Secret Key Warning */}
        {clerkKeyConfigured === false && (
          <div className="bg-orange-500/20 border border-orange-500/50 rounded-xl p-4 mb-6">
            <p className="text-orange-300 font-semibold mb-2">⚠️ Clerk Secret Key Not Configured</p>
            <p className="text-orange-200 text-sm mb-2">
              Users are currently being deleted from the database only, but <strong>NOT from Clerk</strong>.
            </p>
            <p className="text-orange-200 text-sm mb-3">
              To enable full deletion (database + Clerk), add <code className="bg-black/30 px-2 py-1 rounded">CLERK_SECRET_KEY</code> to <code className="bg-black/30 px-2 py-1 rounded">backend/.env</code>
            </p>
            <div className="bg-black/30 rounded-lg p-3 mb-2">
              <code className="text-orange-200 text-sm">
                CLERK_SECRET_KEY=sk_test_xxxxx
              </code>
            </div>
            <p className="text-orange-200 text-xs">
              📖 See <code className="bg-black/30 px-2 py-1 rounded">CLERK_SECRET_KEY_SETUP.md</code> for instructions on how to get your Clerk Secret Key.
            </p>
          </div>
        )}

        {error && (
          <div className="bg-red-500/20 border border-red-500/50 rounded-xl p-4 mb-6">
            <p className="text-red-300">{error}</p>
          </div>
        )}

        {/* Stats */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white/10 backdrop-blur-xl rounded-2xl p-6 border border-white/20">
            <div className="text-3xl mb-2">👥</div>
            <div className="text-2xl font-bold text-white">{users.length}</div>
            <div className="text-gray-400 text-sm">Total Users</div>
          </div>
          <div className="bg-white/10 backdrop-blur-xl rounded-2xl p-6 border border-white/20">
            <div className="text-3xl mb-2">🎯</div>
            <div className="text-2xl font-bold text-white">
              {users.filter(u => u.body_type).length}
            </div>
            <div className="text-gray-400 text-sm">With Classifications</div>
          </div>
          <div className="bg-white/10 backdrop-blur-xl rounded-2xl p-6 border border-white/20">
            <div className="text-3xl mb-2">💪</div>
            <div className="text-2xl font-bold text-white">
              {users.filter(u => u.workout_plan).length}
            </div>
            <div className="text-gray-400 text-sm">With Plans</div>
          </div>
        </div>

        {/* Users Table */}
        <div className="bg-white/10 backdrop-blur-xl rounded-3xl p-8 shadow-2xl border border-white/20">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-white">Users</h2>
            <button
              onClick={fetchUsers}
              disabled={loading}
              className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg disabled:opacity-50 transition-all"
            >
              {loading ? '🔄 Loading...' : '🔄 Refresh'}
            </button>
          </div>

          {loading ? (
            <div className="text-center py-12">
              <div className="text-white text-xl">Loading users...</div>
            </div>
          ) : users.length === 0 ? (
            <div className="text-center py-12">
              <div className="text-gray-400">No users found</div>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-white/20">
                    <th className="text-left py-3 px-4 text-gray-300">Clerk ID</th>
                    <th className="text-left py-3 px-4 text-gray-300">Email</th>
                    <th className="text-left py-3 px-4 text-gray-300">Name</th>
                    <th className="text-left py-3 px-4 text-gray-300">Body Type</th>
                    <th className="text-left py-3 px-4 text-gray-300">Gender</th>
                    <th className="text-left py-3 px-4 text-gray-300">Created</th>
                    <th className="text-left py-3 px-4 text-gray-300">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((userData) => (
                    <tr key={userData.id} className="border-b border-white/10 hover:bg-white/5">
                      <td className="py-3 px-4 text-gray-300 text-sm font-mono">
                        {userData.clerk_user_id.substring(0, 20)}...
                      </td>
                      <td className="py-3 px-4 text-white">
                        {editingUser === userData.clerk_user_id ? (
                          <input
                            type="email"
                            value={editForm.email}
                            onChange={(e) => setEditForm({ ...editForm, email: e.target.value })}
                            className="bg-white/10 border border-white/20 rounded px-2 py-1 text-white text-sm w-full"
                            placeholder="Email"
                          />
                        ) : (
                          userData.email || '-'
                        )}
                      </td>
                      <td className="py-3 px-4 text-white">
                        {editingUser === userData.clerk_user_id ? (
                          <input
                            type="text"
                            value={editForm.name}
                            onChange={(e) => setEditForm({ ...editForm, name: e.target.value })}
                            className="bg-white/10 border border-white/20 rounded px-2 py-1 text-white text-sm w-full"
                            placeholder="Name"
                          />
                        ) : (
                          userData.name || '-'
                        )}
                      </td>
                      <td className="py-3 px-4 text-white capitalize">
                        {userData.body_type || '-'}
                      </td>
                      <td className="py-3 px-4 text-white capitalize">
                        {userData.gender ? (userData.gender === 'female' ? '👩 Female' : '👨 Male') : '-'}
                      </td>
                      <td className="py-3 px-4 text-gray-400 text-sm">
                        {userData.created_at ? new Date(userData.created_at).toLocaleDateString() : '-'}
                      </td>
                      <td className="py-3 px-4">
                        {editingUser === userData.clerk_user_id ? (
                          <div className="flex gap-2">
                            <button
                              onClick={() => handleUpdate(userData.clerk_user_id)}
                              className="bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded text-sm"
                            >
                              ✓ Save
                            </button>
                            <button
                              onClick={() => {
                                setEditingUser(null);
                                setEditForm({ email: '', name: '' });
                              }}
                              className="bg-gray-600 hover:bg-gray-700 text-white px-3 py-1 rounded text-sm"
                            >
                              ✕ Cancel
                            </button>
                          </div>
                        ) : (
                          <div className="flex gap-2">
                            <button
                              onClick={() => startEdit(userData)}
                              className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-sm"
                            >
                              ✏️ Edit
                            </button>
                            <button
                              onClick={() => handleDelete(userData.clerk_user_id)}
                              className="bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded text-sm"
                            >
                              🗑️ Delete
                            </button>
                          </div>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

