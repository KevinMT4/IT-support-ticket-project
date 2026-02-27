import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import LanguageDetector from "i18next-browser-languagedetector";
import esTranslations from "./locales/es.json";
import enTranslations from "./locales/en.json";

// Detectar idioma: localStorage -> navegador -> español por defecto
const detectLanguage = () => {
    const savedLanguage = localStorage.getItem("language");
    if (savedLanguage) return savedLanguage;

    const browserLang = navigator.language || navigator.userLanguage;
    if (browserLang.startsWith("es")) return "es";
    if (browserLang.startsWith("en")) return "en";
    return "es";
};

const initialLanguage = detectLanguage();

i18n.use(initReactI18next).init({
    resources: {
        es: { translation: esTranslations },
        en: { translation: enTranslations },
    },
    lng: initialLanguage,
    fallbackLng: "es",
    interpolation: {
        escapeValue: false,
    },
    react: {
        useSuspense: false,
    },
});

// Actualizar atributo lang del HTML cuando cambie el idioma
i18n.on("languageChanged", (lng) => {
    document.documentElement.lang = lng;
    document.documentElement.dir = lng === "ar" ? "rtl" : "ltr";
});

// Establecer idioma inicial en el documento
document.documentElement.lang = initialLanguage;

export default i18n;
