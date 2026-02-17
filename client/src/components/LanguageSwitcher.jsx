import { useTranslation } from "react-i18next";
import { FiGlobe } from "react-icons/fi";
import "../styles/LanguageSwitcher.css";

const LanguageSwitcher = () => {
    const { i18n } = useTranslation();

    const handleLanguageChange = (lang) => {
        i18n.changeLanguage(lang);
        localStorage.setItem("language", lang);
    };

    return (
        <div className="language-switcher">
            <button
                className={`lang-btn ${i18n.language === "es" ? "active" : ""}`}
                onClick={() => handleLanguageChange("es")}
                title="Español"
            >
                ES
            </button>
            <div className="lang-separator">|</div>
            <button
                className={`lang-btn ${i18n.language === "en" ? "active" : ""}`}
                onClick={() => handleLanguageChange("en")}
                title="English"
            >
                EN
            </button>
        </div>
    );
};

export default LanguageSwitcher;
