import en from './locales/en.json';
import mr from './locales/mr.json';
import hi from './locales/hi.json';

// Translation catalogs
const translations: Record<string, Record<string, string>> = {
  en,
  mr,
  hi
};

/**
 * Get translated string for a given key and locale
 * @param key - Dot-notation key for nested translation (e.g., "navigation.dashboard")
 * @param locale - Locale code (en, mr, hi)
 * @returns Translated string or fallback to English
 */
export function t(key: string, locale: string = 'en'): string {
  // Fallback to English if locale not supported
  const availableLocale = translations[locale] || translations.en;

  // Split key by dots for nested object traversal
  const keys = key.split('.');
  let current: any = availableLocale;

  // Traverse the nested object
  for (const k of keys) {
    if (current[k] !== undefined && current[k] !== null) {
      current = current[k];
    } else {
      // Key not found, try fallback to English
      if (locale === 'en') {
        return key; // Return key as last resort
      }
      // Try English fallback
      const enKeys = key.split('.');
      let enCurrent: any = translations.en;
      for (const ek of enKeys) {
        if (enCurrent[ek] !== undefined && enCurrent[ek] !== null) {
          enCurrent = enCurrent[ek];
        } else {
          return key; // Not found even in English
        }
      }
      return enCurrent;
    }
  }

  return typeof current === 'string' ? current : key;
}

// Export for use in other files
export default { t };