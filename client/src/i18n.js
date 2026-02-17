import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import esTranslations from "./locales/es.json";
import enTranslations from "./locales/en.json";

// Obtener el idioma guardado en localStorage o usar español por defecto
const savedLanguage = localStorage.getItem("language") || "es";

i18n.use(initReactI18next).init({
    resources: {
        es: { translation: esTranslations },
        en: { translation: enTranslations },
    },
    lng: savedLanguage,
    fallbackLng: "es",
    interpolation: {
        escapeValue: false,
    },
});

export default i18n;
