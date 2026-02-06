import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import "../styles/Login.css";

const Login = () => {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);
    const { login } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError("");
        setLoading(true);

        if (!username || !password) {
            setError("Por favor completa todos los campos");
            setLoading(false);
            return;
        }

        const result = await login(username, password);

        if (result.success) {
            navigate("/tickets");
        } else {
            setError(result.error || "Error al iniciar sesión");
        }

        setLoading(false);
    };

    return (
        <div className="login-container">
            <div className="login-box">
                <h1 className="login-title">Sistema de Tickets</h1>
                <p className="login-subtitle">Inicia sesión para continuar</p>

                <form onSubmit={handleSubmit} className="login-form">
                    {error && <div className="error-message">{error}</div>}

                    <div className="form-group">
                        <label htmlFor="username">Usuario</label>
                        <input
                            type="text"
                            id="username"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            placeholder="Ingresa tu usuario"
                            disabled={loading}
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="password">Contraseña</label>
                        <input
                            type="password"
                            id="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder="Ingresa tu contraseña"
                            disabled={loading}
                        />
                    </div>

                    <button
                        type="submit"
                        className="btn-login"
                        disabled={loading}
                    >
                        {loading ? "Iniciando sesión..." : "Iniciar Sesión"}
                    </button>
                </form>

                <p className="login-footer">
                    ¿No tienes cuenta?{" "}
                    <Link to="/registro" className="link-register">
                        Regístrate aquí
                    </Link>
                </p>
            </div>
        </div>
    );
};

export default Login;
