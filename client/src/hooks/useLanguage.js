import { useTranslation } from "react-i18next";
import { useCallback, useState, useEffect } from "react";

/**
 * Hook personalizado para manejar cambios de idioma
 * Proporciona funciones para cambiar el idioma y obtener información del actual
 */
export const useLanguage = () => {
    const { i18n, t } = useTranslation();
    const [currentLanguage, setCurrentLanguage] = useState(i18n.language || "es");

    // Escuchar cambios de idioma en i18n
    useEffect(() => {
        const handleLanguageChanged = (lng) => {
            setCurrentLanguage(lng);
        };

        i18n.on("languageChanged", handleLanguageChanged);

        // Sincronizar estado inicial
        setCurrentLanguage(i18n.language || "es");

        return () => {
            i18n.off("languageChanged", handleLanguageChanged);
        };
    }, [i18n]);

    // whenever the currentLanguage state is updated we also inform the
    // API client so that it will send the appropriate Accept-Language
    // header on subsequent requests.  this keeps the backend and frontend
    // in sync without having to append ``?lang=`` to every call.
    useEffect(() => {
        import("../api/client").then(({ default: apiClient }) => {
            if (apiClient && apiClient.setLanguage) {
                apiClient.setLanguage(currentLanguage);
            }
        });
    }, [currentLanguage]);

    const changeLanguage = useCallback(
        (lang) => {
            if (["es", "en"].includes(lang)) {
                i18n.changeLanguage(lang);
                localStorage.setItem("language", lang);
            }
        },
        [i18n],
    );

    const isLanguage = useCallback(
        (lang) => currentLanguage === lang,
        [currentLanguage],
    );

    const getLanguageName = useCallback((lang) => {
        const names = {
            es: "Español",
            en: "English",
        };
        return names[lang] || lang;
    }, []);

    return {
        currentLanguage,
        changeLanguage,
        isLanguage,
        t,
        i18n,
        getLanguageName,
    };
};
