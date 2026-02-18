import { useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useSessionTimeout } from "../hooks/useSessionTimeout";
import SessionWarningModal from "./SessionWarningModal";

const SessionTimeoutHandler = () => {
    const { user, logout, showSessionWarning, setShowSessionWarning } = useAuth();
    const navigate = useNavigate();
    const location = useLocation();

    const handleTimeout = async () => {
        await logout(true);
        navigate("/login", {
            replace: true,
            state: { sessionExpired: true }
        });
    };

    const handleWarning = () => {
        if (user && location.pathname !== "/login" && location.pathname !== "/registro") {
            setShowSessionWarning(true);
        }
    };

    const { resetTimer } = useSessionTimeout(
        user && location.pathname !== "/login" && location.pathname !== "/registro" ? handleTimeout : () => {},
        user && location.pathname !== "/login" && location.pathname !== "/registro" ? handleWarning : null
    );

    const handleContinueSession = () => {
        setShowSessionWarning(false);
        resetTimer();
    };

    const handleLogoutNow = async () => {
        setShowSessionWarning(false);
        await logout();
        navigate("/login");
    };

    return user && showSessionWarning ? (
        <SessionWarningModal
            isOpen={showSessionWarning}
            onContinue={handleContinueSession}
            onLogout={handleLogoutNow}
        />
    ) : null;
};

export default SessionTimeoutHandler;
