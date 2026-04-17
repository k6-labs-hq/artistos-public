export type SupportedLanguage = "en" | "es" | "fr" | "de";

const messages = {
  en: {
    unavailableTitle: "{name} is temporarily unavailable",
    unavailableBody: "Refresh the page or try again in a moment.",
  },
  es: {
    unavailableTitle: "{name} no está disponible temporalmente",
    unavailableBody: "Actualiza la página o vuelve a intentarlo en un momento.",
  },
  fr: {
    unavailableTitle: "{name} est temporairement indisponible",
    unavailableBody: "Rafraîchissez la page ou réessayez dans un instant.",
  },
  de: {
    unavailableTitle: "{name} ist vorübergehend nicht verfügbar",
    unavailableBody: "Aktualisieren Sie die Seite oder versuchen Sie es gleich erneut.",
  },
} as const;

export function detectUiLanguage(): SupportedLanguage {
  if (typeof navigator === "undefined") {
    return "en";
  }
  const candidate = navigator.language.slice(0, 2).toLowerCase();
  if (candidate === "es" || candidate === "fr" || candidate === "de") {
    return candidate;
  }
  return "en";
}

export function t(language: SupportedLanguage, key: keyof typeof messages.en, vars?: Record<string, string>) {
  let value = String(messages[language][key] ?? messages.en[key]);
  for (const [name, replacement] of Object.entries(vars || {})) {
    value = value.replace(`{${name}}`, replacement);
  }
  return value;
}