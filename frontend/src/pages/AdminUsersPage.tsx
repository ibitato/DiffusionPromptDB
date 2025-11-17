/**
 * Admin Users Management Page
 */

import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Header } from '../components/layout/Header';
import { adminUsersService, AdminUser } from '../services/adminUsers.service';
import { useToast } from '../hooks/useToast';
import { Loading } from '../components/ui/Loading';

export const AdminUsersPage = () => {
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState({
    username: '',
    email: '',
    role: 'user' as 'admin' | 'user',
    password: '',
    full_name: '',
  });
  const toast = useToast();
  const { t } = useTranslation();

  const loadUsers = async () => {
    try {
      const data = await adminUsersService.list();
      setUsers(data);
    } catch (error) {
      toast.error(t('adminUsers.errors.load'));
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadUsers();
  }, []);

  const handleCreate = async () => {
    try {
      await adminUsersService.create(form);
      toast.success(t('adminUsers.messages.created'));
      setShowCreate(false);
      setForm({ username: '', email: '', role: 'user', password: '', full_name: '' });
      loadUsers();
    } catch (error) {
      toast.error(t('adminUsers.errors.create'));
    }
  };

  const handleToggleActive = async (user: AdminUser) => {
    try {
      await adminUsersService.update(user.id, { is_active: !user.is_active });
      loadUsers();
    } catch (error) {
      toast.error(t('adminUsers.errors.update'));
    }
  };

  const handleResetPassword = async (user: AdminUser) => {
    const newPassword = prompt(t('adminUsers.prompts.newPassword', { username: user.username }));
    if (!newPassword) {
      return;
    }
    try {
      await adminUsersService.resetPassword(user.id, newPassword);
      toast.success(t('adminUsers.messages.passwordReset'));
    } catch (error) {
      toast.error(t('adminUsers.errors.password'));
    }
  };

  const handleDelete = async (user: AdminUser) => {
    if (!confirm(t('adminUsers.prompts.delete', { username: user.username }))) return;
    try {
      await adminUsersService.remove(user.id);
      toast.success(t('adminUsers.messages.deleted'));
      loadUsers();
    } catch (error) {
      toast.error(t('adminUsers.errors.delete'));
    }
  };

  return (
    <div className="min-h-screen bg-slate-900">
      <Header />
      <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold text-white">{t('adminUsers.title')}</h1>
            <p className="text-gray-400">{t('adminUsers.subtitle')}</p>
          </div>
          <button
            onClick={() => setShowCreate(true)}
            className="px-4 py-2 bg-violet-600 hover:bg-violet-700 text-white rounded-lg"
          >
            {t('adminUsers.actions.new')}
          </button>
        </div>

        {isLoading ? (
          <div className="flex justify-center">
            <Loading size="lg" text="Loading users..." />
          </div>
        ) : (
          <div className="bg-slate-800 border border-slate-700 rounded-lg overflow-hidden">
            <table className="min-w-full divide-y divide-slate-700">
              <thead className="bg-slate-700">
                <tr>
                  <th className="px-4 py-3 text-left text-xs text-gray-300 uppercase">
                    {t('adminUsers.table.user')}
                  </th>
                  <th className="px-4 py-3 text-left text-xs text-gray-300 uppercase">
                    {t('adminUsers.table.email')}
                  </th>
                  <th className="px-4 py-3 text-left text-xs text-gray-300 uppercase">
                    {t('adminUsers.table.role')}
                  </th>
                  <th className="px-4 py-3 text-left text-xs text-gray-300 uppercase">
                    {t('adminUsers.table.status')}
                  </th>
                  <th className="px-4 py-3 text-left text-xs text-gray-300 uppercase">
                    {t('adminUsers.table.actions')}
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-700">
                {users.map((user) => (
                  <tr key={user.id} className="text-gray-300">
                    <td className="px-4 py-3">{user.username}</td>
                    <td className="px-4 py-3">{user.email}</td>
                    <td className="px-4 py-3 capitalize">{user.role}</td>
                    <td className="px-4 py-3">
                      <span
                        className={`px-2 py-1 rounded-full text-xs ${
                          user.is_active ? 'bg-green-600/30 text-green-300' : 'bg-red-600/30 text-red-300'
                        }`}
                      >
                        {user.is_active ? t('adminUsers.status.active') : t('adminUsers.status.disabled')}
                      </span>
                    </td>
                    <td className="px-4 py-3 space-x-2">
                      <button
                        onClick={() => handleToggleActive(user)}
                        className="text-sm text-blue-400 hover:text-blue-300"
                      >
                        {user.is_active ? t('adminUsers.actions.disable') : t('adminUsers.actions.enable')}
                      </button>
                      <button
                        onClick={() => handleResetPassword(user)}
                        className="text-sm text-yellow-400 hover:text-yellow-300"
                      >
                        {t('adminUsers.actions.resetPassword')}
                      </button>
                      <button
                        onClick={() => handleDelete(user)}
                        className="text-sm text-red-400 hover:text-red-300"
                      >
                        {t('adminUsers.actions.delete')}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {showCreate && (
          <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
            <div className="bg-slate-800 p-6 rounded-xl border border-slate-700 w-full max-w-lg">
              <h3 className="text-xl font-semibold text-white mb-4">{t('adminUsers.create.title')}</h3>
              <div className="space-y-3">
                <input
                  value={form.username}
                  onChange={(e) => setForm({ ...form, username: e.target.value })}
                  placeholder={t('adminUsers.fields.username')}
                  className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
                />
                <input
                  value={form.email}
                  onChange={(e) => setForm({ ...form, email: e.target.value })}
                  placeholder={t('adminUsers.fields.email')}
                  className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
                />
                <input
                  value={form.full_name}
                  onChange={(e) => setForm({ ...form, full_name: e.target.value })}
                  placeholder={t('adminUsers.fields.fullName')}
                  className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
                />
                <select
                  value={form.role}
                  onChange={(e) => setForm({ ...form, role: e.target.value as 'admin' | 'user' })}
                  className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
                >
                  <option value="user">{t('adminUsers.roles.user')}</option>
                  <option value="admin">{t('adminUsers.roles.admin')}</option>
                </select>
                <input
                  type="password"
                  value={form.password}
                  onChange={(e) => setForm({ ...form, password: e.target.value })}
                  placeholder={t('adminUsers.fields.password')}
                  className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
                />
              </div>
              <div className="flex justify-end gap-3 mt-6">
                <button
                  onClick={() => setShowCreate(false)}
                  className="px-4 py-2 bg-slate-700 text-white rounded-lg"
                >
                  {t('common.cancel')}
                </button>
                <button
                  onClick={handleCreate}
                  className="px-4 py-2 bg-violet-600 hover:bg-violet-700 text-white rounded-lg"
                >
                  {t('adminUsers.actions.create')}
                </button>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};
