import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

// Import translation files
// Path: from frontend/src/i18n/config.ts to citizen/i18n/locales/ (3 levels up to citizen/)
import enCommon from '../../../i18n/locales/en/common.json';
import hiCommon from '../../../i18n/locales/hi/common.json';
import enAuth from '../../../i18n/locales/en/auth.json';
import hiAuth from '../../../i18n/locales/hi/auth.json';
import enDashboard from '../../../i18n/locales/en/dashboard.json';
import hiDashboard from '../../../i18n/locales/hi/dashboard.json';
import enPayments from '../../../i18n/locales/en/payments.json';
import enSettings from '../../../i18n/locales/en/settings.json';
import enSearch from '../../../i18n/locales/en/search.json';

const resources = {
  en: {
    common: enCommon,
    auth: enAuth,
    dashboard: enDashboard,
    payments: enPayments,
    settings: enSettings,
    search: enSearch,
  },
  hi: {
    common: hiCommon,
    auth: hiAuth,
    dashboard: hiDashboard,
    payments: enPayments, // TODO: Add Hindi translations
    settings: enSettings, // TODO: Add Hindi translations
    search: enSearch, // TODO: Add Hindi translations
  },
};

i18n
  .use(LanguageDetector) // Detect user language
  .use(initReactI18next) // Pass i18n instance to react-i18next
  .init({
    resources,
    fallbackLng: 'en', // Fallback language if translation is missing
    debug: import.meta.env.DEV, // Enable debug mode in development
    interpolation: {
      escapeValue: false, // React already escapes by default
    },
    ns: ['common', 'auth', 'dashboard', 'payments', 'settings', 'search'], // Namespaces to load
    defaultNS: 'common', // Default namespace
    detection: {
      order: ['querystring', 'cookie', 'localStorage', 'sessionStorage', 'navigator', 'htmlTag'],
      caches: ['cookie', 'localStorage'],
      lookupCookie: 'i18next',
      lookupLocalStorage: 'i18nextLng',
    },
    react: {
      useSuspense: true, // Enable React.Suspense for translations
    },
  });

export default i18n;

