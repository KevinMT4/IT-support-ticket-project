import { useState, useEffect } from "react";
import { useLanguage } from "../hooks/useLanguage";
import "../styles/SessionWarningModal.css";

const SessionWarningModal = ({ isOpen, onContinue, onLogout }) => {
    const { t } = useLanguage();
    const [countdown, setCountdown] = useState(120);

    useEffect(() => {
        if (!isOpen) return;

        setCountdown(120);

        const interval = setInterval(() => {
            setCountdown((prev) => {
                if (prev <= 1) {
                    clearInterval(interval);
                    onLogout();
                    return 0;
                }
                return prev - 1;
            });
        }, 1000);

        return () => clearInterval(interval);
    }, [isOpen, onLogout]);

    if (!isOpen) return null;

    const minutes = Math.floor(countdown / 60);
    const seconds = countdown % 60;

    return (
        <div className="session-modal-overlay" role="dialog" aria-modal="true">
            <div className="session-modal-content">
                <div className="session-modal-icon">
                    <svg
                        width="48"
                        height="48"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                    >
                        <circle cx="12" cy="12" r="10"></circle>
                        <polyline points="12 6 12 12 16 14"></polyline>
                    </svg>
                </div>
                <h3 className="session-modal-title">
                    {t("session.warningTitle")}
                </h3>
                <p className="session-modal-message">
                    {t("session.warningMessage")}
                </p>
                <div className="session-modal-countdown">
                    {minutes}:{seconds.toString().padStart(2, "0")}
                </div>
                <div className="session-modal-actions">
                    <button
                        onClick={onLogout}
                        className="btn-session-logout"
                        aria-label={t("common.logout")}
                    >
                        {t("common.logout")}
                    </button>
                    <button
                        onClick={onContinue}
                        className="btn-session-continue"
                        aria-label={t("session.continueSession")}
                    >
                        {t("session.continueSession")}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default SessionWarningModal;
