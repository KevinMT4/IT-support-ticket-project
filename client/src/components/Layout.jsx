import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import ConfirmModal from "./ConfirmModal";
import "../styles/Layout.css";

const Layout = ({ children }) => {
    const { user, logout, isSuperuser } = useAuth();
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
                        Sistema de Tickets
                    </Link>
                    <div className="navbar-menu">
                        <Link to="/tickets" className="navbar-link">
                            Mis Tickets
                        </Link>
                        {!isSuperuser() && (
                            <Link to="/tickets/new" className="navbar-link">
                                Crear Ticket
                            </Link>
                        )}
                        {user && (
                            <div className="navbar-user">
                                <span className="user-info">
                                    {user.first_name || user.username}
                                    {isSuperuser() && (
                                        <span className="badge-superuser">
                                            Admin
                                        </span>
                                    )}
                                </span>
                                <button
                                    onClick={handleLogoutClick}
                                    className="btn-logout"
                                >
                                    Cerrar Sesión
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
                title="Cerrar sesión"
                message="¿Estás seguro que deseas cerrar sesión?"
            />
        </div>
    );
};

export default Layout;
