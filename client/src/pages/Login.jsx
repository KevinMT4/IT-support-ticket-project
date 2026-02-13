import { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import apiClient from "../api/client";
import Alert from "../components/Alert";
import "../styles/Auth.css";

const Login = () => {
    const location = useLocation();
    const [isLogin, setIsLogin] = useState(location.pathname === "/login");
    const [loginData, setLoginData] = useState({ email: "", password: "" });
    const [registerData, setRegisterData] = useState({
        username: "",
        email: "",
        first_name: "",
        last_name: "",
        departamento: "",
        password: "",
        password_confirm: "",
    });
    const [departamentos, setDepartamentos] = useState([]);
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);
    const [loadingDepartments, setLoadingDepartments] = useState(false);
    const { login, register } = useAuth();
    const navigate = useNavigate();

    useEffect(() => {
        setIsLogin(location.pathname === "/login");
    }, [location.pathname]);

    const loadDepartamentos = async () => {
        if (departamentos.length > 0) return;
        setLoadingDepartments(true);
        try {
            const data = await apiClient.getDepartamentos();
            setDepartamentos(data);
        } catch (err) {
            setError("Error al cargar los departamentos");
        } finally {
            setLoadingDepartments(false);
        }
    };

    const handleToggle = () => {
        const newMode = !isLogin;
        setError("");
        if (newMode) {
            navigate("/registro");
            loadDepartamentos();
        } else {
            navigate("/login");
        }
    };

    const handleLoginSubmit = async (e) => {
        e.preventDefault();
        setError("");
        setLoading(true);

        if (!loginData.email || !loginData.password) {
            setError("Por favor completa todos los campos");
            setLoading(false);
            return;
        }

        const result = await login(loginData.email, loginData.password);

        if (result.success) {
            navigate("/tickets");
        } else {
            setError(result.error || "Error al iniciar sesión");
        }

        setLoading(false);
    };

    const handleRegisterSubmit = async (e) => {
        e.preventDefault();
        setError("");

        if (
            !registerData.username ||
            !registerData.email ||
            !registerData.departamento ||
            !registerData.password ||
            !registerData.password_confirm
        ) {
            setError("Por favor completa los campos requeridos");
            return;
        }

        if (registerData.password !== registerData.password_confirm) {
            setError("Las contraseñas no coinciden");
            return;
        }

        if (registerData.password.length < 8) {
            setError("La contraseña debe tener al menos 8 caracteres");
            return;
        }

        setLoading(true);

        const dataToSubmit = {
            ...registerData,
            departamento: parseInt(registerData.departamento),
        };

        const result = await register(dataToSubmit);

        if (result.success) {
            navigate("/tickets");
        } else {
            setError(result.error || "Error al registrar usuario");
        }

        setLoading(false);
    };

    return (
        <div className="auth-container">
            <div className={`auth-wrapper ${isLogin ? "login-mode" : "register-mode"}`}>
                <div className="auth-form-section">
                    {isLogin ? (
                        <div className="form-content">
                            <div className="auth-logo-container">
                                <img
                                    src="/src/assets/image.png"
                                    alt="COFATECH"
                                    className="auth-logo"
                                />
                            </div>
                            <h2 className="auth-title">Iniciar Sesión</h2>
                            <p className="auth-subtitle">Inicia sesión para continuar</p>

                            <form onSubmit={handleLoginSubmit} className="auth-form">
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
                                        value={loginData.email}
                                        onChange={(e) =>
                                            setLoginData({ ...loginData, email: e.target.value })
                                        }
                                        placeholder="correo@ejemplo.com"
                                        disabled={loading}
                                    />
                                </div>

                                <div className="form-group">
                                    <label htmlFor="password">Contraseña</label>
                                    <input
                                        type="password"
                                        id="password"
                                        value={loginData.password}
                                        onChange={(e) =>
                                            setLoginData({ ...loginData, password: e.target.value })
                                        }
                                        placeholder="Ingresa tu contraseña"
                                        disabled={loading}
                                    />
                                </div>

                                <button
                                    type="submit"
                                    className="btn-auth-submit"
                                    disabled={loading}
                                >
                                    {loading ? "Iniciando sesión..." : "Iniciar Sesión"}
                                </button>
                            </form>
                        </div>
                    ) : (
                        <div className="form-content">
                            <div className="auth-logo-container">
                                <img
                                    src="/src/assets/image.png"
                                    alt="COFATECH"
                                    className="auth-logo"
                                />
                            </div>
                            <h2 className="auth-title">Crear Cuenta</h2>
                            <p className="auth-subtitle">Regístrate para acceder al sistema</p>

                            <form onSubmit={handleRegisterSubmit} className="auth-form">
                                {error && (
                                    <Alert
                                        type="error"
                                        message={error}
                                        onClose={() => setError("")}
                                    />
                                )}

                                <div className="form-group">
                                    <label htmlFor="username">Usuario *</label>
                                    <input
                                        type="text"
                                        id="username"
                                        value={registerData.username}
                                        onChange={(e) =>
                                            setRegisterData({
                                                ...registerData,
                                                username: e.target.value,
                                            })
                                        }
                                        placeholder="Nombre de usuario"
                                        disabled={loading}
                                        required
                                    />
                                </div>

                                <div className="form-group">
                                    <label htmlFor="register-email">Correo Electrónico *</label>
                                    <input
                                        type="email"
                                        id="register-email"
                                        value={registerData.email}
                                        onChange={(e) =>
                                            setRegisterData({ ...registerData, email: e.target.value })
                                        }
                                        placeholder="correo@ejemplo.com"
                                        disabled={loading}
                                        required
                                    />
                                </div>

                                <div className="form-group">
                                    <label htmlFor="departamento">Departamento *</label>
                                    <select
                                        id="departamento"
                                        value={registerData.departamento}
                                        onChange={(e) =>
                                            setRegisterData({
                                                ...registerData,
                                                departamento: e.target.value,
                                            })
                                        }
                                        disabled={loading || loadingDepartments}
                                        required
                                    >
                                        <option value="">Selecciona un departamento</option>
                                        {departamentos.map((dept) => (
                                            <option key={dept.id} value={dept.id}>
                                                {dept.nombre}
                                            </option>
                                        ))}
                                    </select>
                                </div>

                                <div className="form-row">
                                    <div className="form-group">
                                        <label htmlFor="first_name">Nombre</label>
                                        <input
                                            type="text"
                                            id="first_name"
                                            value={registerData.first_name}
                                            onChange={(e) =>
                                                setRegisterData({
                                                    ...registerData,
                                                    first_name: e.target.value,
                                                })
                                            }
                                            placeholder="Tu nombre"
                                            disabled={loading}
                                        />
                                    </div>

                                    <div className="form-group">
                                        <label htmlFor="last_name">Apellido</label>
                                        <input
                                            type="text"
                                            id="last_name"
                                            value={registerData.last_name}
                                            onChange={(e) =>
                                                setRegisterData({
                                                    ...registerData,
                                                    last_name: e.target.value,
                                                })
                                            }
                                            placeholder="Tu apellido"
                                            disabled={loading}
                                        />
                                    </div>
                                </div>

                                <div className="form-group">
                                    <label htmlFor="register-password">Contraseña *</label>
                                    <input
                                        type="password"
                                        id="register-password"
                                        value={registerData.password}
                                        onChange={(e) =>
                                            setRegisterData({
                                                ...registerData,
                                                password: e.target.value,
                                            })
                                        }
                                        placeholder="Mínimo 8 caracteres"
                                        disabled={loading}
                                        required
                                    />
                                </div>

                                <div className="form-group">
                                    <label htmlFor="password_confirm">Confirmar Contraseña *</label>
                                    <input
                                        type="password"
                                        id="password_confirm"
                                        value={registerData.password_confirm}
                                        onChange={(e) =>
                                            setRegisterData({
                                                ...registerData,
                                                password_confirm: e.target.value,
                                            })
                                        }
                                        placeholder="Repite tu contraseña"
                                        disabled={loading}
                                        required
                                    />
                                </div>

                                <button
                                    type="submit"
                                    className="btn-auth-submit"
                                    disabled={loading}
                                >
                                    {loading ? "Creando cuenta..." : "Crear Cuenta"}
                                </button>
                            </form>
                        </div>
                    )}
                </div>

                <div className="auth-panel-section">
                    <div className="panel-content">
                        <h2 className="panel-title">
                            {isLogin ? "¡Hola, Bienvenido!" : "¡Bienvenido de vuelta!"}
                        </h2>
                        <p className="panel-subtitle">
                            {isLogin ? "¿No tienes cuenta?" : "¿Ya tienes cuenta?"}
                        </p>
                        <button onClick={handleToggle} className="btn-panel-toggle">
                            {isLogin ? "Registrarse" : "Iniciar Sesión"}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Login;
