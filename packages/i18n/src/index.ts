import en from './locales/en.json';
import mr from './locales/mr.json';
import hi from './locales/hi.json';

type LocaleRecord = Record<string, unknown>;

// Translation catalogs
const translations: Record<string, LocaleRecord> = {
  en: en as LocaleRecord,
  mr: mr as LocaleRecord,
  hi: hi as LocaleRecord,
};

function getNestedValue(obj: unknown, path: string): string | null {
  const keys = path.split('.');
  let current: unknown = obj;

  for (const k of keys) {
    if (current && typeof current === 'object' && k in (current as Record<string, unknown>)) {
      current = (current as Record<string, unknown>)[k];
    } else {
      return null;
    }
  }

  return typeof current === 'string' ? current : null;
}

/**
 * Get translated string for a given key and locale
 * @param key - Dot-notation key for nested translation (e.g., "navigation.dashboard")
 * @param locale - Locale code (en, mr, hi)
 * @returns Translated string or fallback to English
 */
export function t(key: string, locale = 'en'): string {
  const targetCatalog = translations[locale] || translations.en;
  const translated = getNestedValue(targetCatalog, key);

  if (translated !== null) {
    return translated;
  }

  // Fallback to English if not found in requested locale
  if (locale !== 'en') {
    const enFallback = getNestedValue(translations.en, key);
    if (enFallback !== null) return enFallback;
  }

  return key;
}

export default { t };