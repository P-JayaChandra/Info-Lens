import React, { useState, useEffect } from 'react';
import { Settings as SettingsIcon, User, Shield, Eye, Bell, Moon, Sun, Save, Check } from 'lucide-react';
import { Button } from '../../components/common/Button';
import { Input } from '../../components/common/Input';
import { Badge } from '../../components/common/Badge';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../context/ToastContext';
import { settingsApi } from '../../api/settingsApi';
import { USE_FIXTURES } from '../../api/client';

export function SettingsPage() {
  const { user } = useAuth();
  const { addToast } = useToast();

  const [settings, setSettings] = useState({
    theme: 'light',
    fontSize: 'medium',
    defaultSummaryLength: 'detailed',
    citationHighlighting: true,
    autoScrollChat: true,
    privacyMode: 'strict',
  });

  const [fullName, setFullName] = useState(user?.fullName || '');
  const [email, setEmail] = useState(user?.email || '');
  const [isLoading, setIsLoading] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    async function loadSettings() {
      try {
        const res = await settingsApi.getSettings();
        setSettings((prev) => ({ ...prev, ...res }));
      } catch (err) {
        console.warn('Failed to load user settings:', err);
      }
    }
    loadSettings();
  }, []);

  const handleSaveSettings = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      await settingsApi.updateSettings(settings);
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
      addToast('Preferences updated successfully.', 'success');
    } catch (err) {
      addToast(err.message || 'Failed to save settings.', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6 text-left animate-fade-in max-w-4xl mx-auto">
      {/* Settings Header */}
      <div className="flex items-center justify-between bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
        <div>
          <h2 className="text-2xl font-extrabold text-slate-900 tracking-tight flex items-center gap-2">
            <SettingsIcon className="w-6 h-6 text-indigo-600" />
            System & Workspace Settings
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Configure research workspace preferences, accessibility, and citation display.
          </p>
        </div>
        <Badge variant={USE_FIXTURES ? 'amber' : 'emerald'}>
          {USE_FIXTURES ? 'Dev Local Settings' : 'Persisted on Backend'}
        </Badge>
      </div>

      <form onSubmit={handleSaveSettings} className="space-y-6">
        {/* Profile & Account Section */}
        <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs space-y-4">
          <div className="flex items-center gap-2 pb-3 border-b border-slate-100">
            <User className="w-5 h-5 text-indigo-600" />
            <h3 className="text-base font-bold text-slate-900">User Profile & Account</h3>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Input
              label="Full Name"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
            />
            <Input
              label="Email Address"
              type="email"
              value={email}
              disabled
              helperText="Managed via authentication provider"
            />
          </div>
        </div>

        {/* Accessibility & Appearance */}
        <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs space-y-4">
          <div className="flex items-center gap-2 pb-3 border-b border-slate-100">
            <Eye className="w-5 h-5 text-indigo-600" />
            <h3 className="text-base font-bold text-slate-900">Appearance & Accessibility</h3>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            <div className="space-y-2">
              <label className="text-xs font-bold uppercase tracking-wider text-slate-700">
                Interface Theme
              </label>
              <div className="flex items-center gap-3">
                <label className="flex items-center gap-2 text-xs font-semibold cursor-pointer">
                  <input
                    type="radio"
                    name="theme"
                    value="light"
                    checked={settings.theme === 'light'}
                    onChange={() => setSettings({ ...settings, theme: 'light' })}
                    className="text-indigo-600"
                  />
                  <span>Light Workspace (Recommended)</span>
                </label>
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-xs font-bold uppercase tracking-wider text-slate-700">
                Reader Font Size
              </label>
              <select
                value={settings.fontSize}
                onChange={(e) => setSettings({ ...settings, fontSize: e.target.value })}
                className="w-full text-xs bg-slate-50 border border-slate-300 rounded-lg p-2"
              >
                <option value="small">Small (13px)</option>
                <option value="medium">Medium (15px)</option>
                <option value="large">Large (18px)</option>
              </select>
            </div>
          </div>
        </div>

        {/* Research & Grounding Preferences */}
        <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs space-y-4">
          <div className="flex items-center gap-2 pb-3 border-b border-slate-100">
            <Shield className="w-5 h-5 text-indigo-600" />
            <h3 className="text-base font-bold text-slate-900">Research & Citation Preferences</h3>
          </div>

          <div className="space-y-3">
            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={settings.citationHighlighting}
                onChange={(e) => setSettings({ ...settings, citationHighlighting: e.target.checked })}
                className="w-4 h-4 text-indigo-600 rounded"
              />
              <span className="text-xs text-slate-800 font-medium">
                Auto-highlight source passage in Document Reader when clicking citations
              </span>
            </label>

            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={settings.autoScrollChat}
                onChange={(e) => setSettings({ ...settings, autoScrollChat: e.target.checked })}
                className="w-4 h-4 text-indigo-600 rounded"
              />
              <span className="text-xs text-slate-800 font-medium">
                Auto-scroll chat messages on streaming response
              </span>
            </label>
          </div>
        </div>

        {/* Save Bar */}
        <div className="flex items-center justify-end gap-3 pt-2">
          <Button type="submit" variant="primary" size="lg" isLoading={isLoading} icon={saved ? Check : Save}>
            {saved ? 'Saved!' : 'Save Preferences'}
          </Button>
        </div>
      </form>
    </div>
  );
}
