import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import "../styles/Layout.css";

const Layout = ({ children }) => {
    const { user, logout, isSuperuser } = useAuth();
    const navigate = useNavigate();

    const handleLogout = async () => {
        const confirmed = window.confirm(
            "¿Estás seguro de que deseas cerrar sesión?",
        );
        if (confirmed) {
            await logout();
            navigate("/login");
        }
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
                        <Link to="/tickets/new" className="navbar-link">
                            Crear Ticket
                        </Link>
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
                                    onClick={handleLogout}
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
        </div>
    );
};

export default Layout;
