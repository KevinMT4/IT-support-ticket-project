import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import Alert from "../components/Alert";
import "../styles/Login.css";

const Login = () => {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);
    const { login } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError("");
        setLoading(true);

        if (!email || !password) {
            setError("Por favor completa todos los campos");
            setLoading(false);
            return;
        }

        const result = await login(email, password);

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
                <div className="login-logo-container">
                    <img
                        src="/src/assets/image.png"
                        alt="COFATECH"
                        className="login-logo"
                    />
                </div>
                <p className="login-subtitle">Inicia sesión para continuar</p>

                <form onSubmit={handleSubmit} className="login-form">
                    {error && (
                        <Alert
                            type="error"
                            message={error}
                            onClose={() => setError("")}
                        />
                    )}

                    <div className="form-group">
                        <label htmlFor="email">Email</label>
                        <input
                            type="email"
                            id="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            placeholder="correo@ejemplo.com"
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
