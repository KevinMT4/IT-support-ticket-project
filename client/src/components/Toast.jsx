import { useEffect } from "react";
import { useLanguage } from "../hooks/useLanguage";
import "../styles/Toast.css";

const Toast = ({ message, type = "info", onClose, duration = 4000 }) => {
    const { t } = useLanguage();

    useEffect(() => {
        const timer = setTimeout(() => {
            onClose();
        }, duration);

        return () => clearTimeout(timer);
    }, [duration, onClose]);

    const getIcon = () => {
        switch (type) {
            case "success":
                return (
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                        <path
                            d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z"
                            fill="currentColor"
                        />
                    </svg>
                );
            case "info":
                return (
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                        <path
                            d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"
                            fill="currentColor"
                        />
                    </svg>
                );
            case "warning":
                return (
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                        <path
                            d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"
                            fill="currentColor"
                        />
                    </svg>
                );
            default:
                return (
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                        <path
                            d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 11c-.55 0-1-.45-1-1V8c0-.55.45-1 1-1s1 .45 1 1v4c0 .55-.45 1-1 1zm1 4h-2v-2h2v2z"
                            fill="currentColor"
                        />
                    </svg>
                );
        }
    };

    return (
        <div className={`toast toast-${type}`} role="alert" aria-live="polite">
            <div className="toast-icon" aria-hidden="true">
                {getIcon()}
            </div>
            <div className="toast-message">{message}</div>
            <button
                className="toast-close"
                onClick={onClose}
                aria-label={t("messages.close")}
            >
                <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                    <path
                        d="M14 4L4 14M4 4l10 10"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                    />
                </svg>
            </button>
        </div>
    );
};

export default Toast;
