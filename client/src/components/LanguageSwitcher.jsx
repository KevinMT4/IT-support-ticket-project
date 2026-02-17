import { FiGlobe } from "react-icons/fi";
import { useLanguage } from "../hooks/useLanguage";
import "../styles/LanguageSwitcher.css";

const LanguageSwitcher = () => {
    const { currentLanguage, changeLanguage, getLanguageName } = useLanguage();

    const handleLanguageChange = (lang) => {
        changeLanguage(lang);
    };

    const languages = [
        { code: "es", name: "Español", flag: "🇪🇸" },
        { code: "en", name: "English", flag: "🇬🇧" },
    ];

    return (
        <div
            className="language-switcher"
            role="group"
            aria-label="Language selector"
        >
            <FiGlobe className="language-icon" aria-hidden="true" />
            <div className="language-buttons">
                {languages.map((lang) => (
                    <button
                        key={lang.code}
                        className={`lang-btn ${
                            currentLanguage === lang.code ? "active" : ""
                        }`}
                        onClick={() => handleLanguageChange(lang.code)}
                        title={lang.name}
                        aria-label={`${lang.name} (${lang.code.toUpperCase()})`}
                        aria-pressed={currentLanguage === lang.code}
                    >
                        <span className="lang-flag">{lang.flag}</span>
                        <span className="lang-code">
                            {lang.code.toUpperCase()}
                        </span>
                    </button>
                ))}
            </div>
        </div>
    );
};

export default LanguageSwitcher;
