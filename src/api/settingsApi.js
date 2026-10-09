import { apiClient, apiCall } from './client';

const DEFAULT_SETTINGS = {
  theme: 'light',
  fontSize: 'medium',
  defaultSummaryLength: 'detailed',
  citationHighlighting: true,
  autoScrollChat: true,
  privacyMode: 'strict',
  emailNotifications: false
};

let localSettings = { ...DEFAULT_SETTINGS };

export const settingsApi = {
  getSettings: async () => {
    return apiCall(
      async () => {
        const res = await apiClient.get('/api/settings');
        return res.data;
      },
      () => {
        const saved = localStorage.getItem('infolens_user_settings');
        if (saved) {
          try { return JSON.parse(saved); } catch { /* ignore */ }
        }
        return localSettings;
      }
    );
  },

  updateSettings: async (newSettings) => {
    return apiCall(
      async () => {
        const res = await apiClient.put('/api/settings', newSettings);
        return res.data;
      },
      () => {
        localSettings = { ...localSettings, ...newSettings };
        localStorage.setItem('infolens_user_settings', JSON.stringify(localSettings));
        return localSettings;
      }
    );
  }
};
