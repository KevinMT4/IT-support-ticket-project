import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useAuth } from "../context/AuthContext";
import LanguageSwitcher from "./LanguageSwitcher";
import ConfirmModal from "./ConfirmModal";
import "../styles/Layout.css";

const Layout = ({ children }) => {
    const { user, logout, isSuperuser } = useAuth();
    const { t } = useTranslation();
    const navigate = useNavigate();
    const [showLogoutModal, setShowLogoutModal] = useState(false);

    const handleLogoutClick = () => {
        setShowLogoutModal(true);
    };

    const handleLogoutConfirm = async () => {
        setShowLogoutModal(false);
        await logout();
        navigate("/login");
    };

    const handleLogoutCancel = () => {
        setShowLogoutModal(false);
    };

    return (
        <div className="layout">
            <nav className="navbar">
                <div className="navbar-container">
                    <Link to="/tickets" className="navbar-brand">
                        <img
                            src="/src/assets/image.png"
                            alt="COFATECH"
                            className="navbar-logo"
                        />
                    </Link>
                    <div className="navbar-menu">
                        <Link to="/tickets" className="navbar-link">
                            {t("common.myTickets")}
                        </Link>
                        {!isSuperuser() && (
                            <Link to="/tickets/new" className="navbar-link">
                                {t("common.createNewTicket")}
                            </Link>
                        )}
                        {user && (
                            <div className="navbar-user">
                                <span className="user-info">
                                    {user.first_name || user.username}
                                    {isSuperuser() && (
                                        <span className="badge-superuser">
                                            {t("common.admin")}
                                        </span>
                                    )}
                                </span>
                                <LanguageSwitcher />
                                <button
                                    onClick={handleLogoutClick}
                                    className="btn-logout"
                                >
                                    {t("common.logout")}
                                </button>
                            </div>
                        )}
                    </div>
                </div>
            </nav>
            <main className="main-content">{children}</main>
            <ConfirmModal
                isOpen={showLogoutModal}
                onClose={handleLogoutCancel}
                onConfirm={handleLogoutConfirm}
                title={t("common.closeSession")}
                message={t("common.areYouSure")}
            />
        </div>
    );
};

export default Layout;
