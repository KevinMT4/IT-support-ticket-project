import { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useLanguage } from "../hooks/useLanguage";
import { useAuth } from "../context/AuthContext";
import apiClient from "../api/client";
import Alert from "../components/Alert";
import "../styles/Auth.css";

const Login = () => {
    const location = useLocation();
    const { t } = useLanguage();
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
    const [showLoginPassword, setShowLoginPassword] = useState(false);
    const [showRegisterPassword, setShowRegisterPassword] = useState(false);
    const [showPasswordConfirm, setShowPasswordConfirm] = useState(false);
    const { login, register } = useAuth();
    const navigate = useNavigate();

    useEffect(() => {
        setIsLogin(location.pathname === "/login");
    }, [location.pathname]);

    useEffect(() => {
        if (location.state?.sessionExpired) {
            setError(t("session.sessionExpired"));
            navigate(location.pathname, { replace: true, state: {} });
        }
    }, [location.state, t, navigate, location.pathname]);

    const loadDepartamentos = async () => {
        if (departamentos.length > 0) return;
        setLoadingDepartments(true);
        try {
            const data = await apiClient.getDepartamentos();
            setDepartamentos(data);
        } catch (err) {
            setError(t("auth.loginError"));
        } finally {
            setLoadingDepartments(false);
        }
    };

    const handleToggle = () => {
        setError("");
        if (isLogin) {
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
            setError(t("form.required"));
            setLoading(false);
            return;
        }

        const result = await login(loginData.email, loginData.password);

        if (result.success) {
            navigate("/tickets");
        } else {
            setError(result.error || t("auth.loginError"));
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
            setError(t("form.required"));
            return;
        }

        if (registerData.password !== registerData.password_confirm) {
            setError(t("auth.passwordsNotMatch"));
            return;
        }

        if (registerData.password.length < 8) {
            setError(t("auth.passwordMinLength"));
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
            setError(result.error || t("auth.registerError"));
        }

        setLoading(false);
    };

    return (
        <div className="auth-container">
            <div
                className={`auth-wrapper ${isLogin ? "login-mode" : "register-mode"}`}
            >
                <div className="auth-form-section">
                    {isLogin ? (
                        <div className="form-content">
                            <div className="auth-logo-container">
                                <img
                                    src="/image.png"
                                    alt="COFATECH"
                                    className="auth-logo"
                                />
                            </div>
                            <h2 className="auth-title">{t("auth.login")}</h2>

                            <form
                                onSubmit={handleLoginSubmit}
                                className="auth-form"
                            >
                                {error && (
                                    <Alert
                                        type="error"
                                        message={error}
                                        onClose={() => setError("")}
                                    />
                                )}

                                <div className="form-group">
                                    <label htmlFor="email">
                                        {t("auth.email")}
                                    </label>
                                    <input
                                        type="email"
                                        id="email"
                                        value={loginData.email}
                                        onChange={(e) =>
                                            setLoginData({
                                                ...loginData,
                                                email: e.target.value,
                                            })
                                        }
                                        placeholder={t(
                                            "form.placeholders.email",
                                        )}
                                        disabled={loading}
                                    />
                                </div>

                                <div className="form-group">
                                    <label htmlFor="password">
                                        {t("auth.password")}
                                    </label>
                                    <div className="password-input-wrapper">
                                        <input
                                            type={
                                                showLoginPassword
                                                    ? "text"
                                                    : "password"
                                            }
                                            id="password"
                                            value={loginData.password}
                                            onChange={(e) =>
                                                setLoginData({
                                                    ...loginData,
                                                    password: e.target.value,
                                                })
                                            }
                                            placeholder={t(
                                                "form.placeholders.password",
                                            )}
                                            disabled={loading}
                                        />
                                        <button
                                            type="button"
                                            className="password-toggle-btn"
                                            onClick={() =>
                                                setShowLoginPassword(
                                                    !showLoginPassword,
                                                )
                                            }
                                            disabled={loading}
                                            title={
                                                showLoginPassword
                                                    ? t("auth.hidePassword")
                                                    : t("auth.showPassword")
                                            }
                                        >
                                            {showLoginPassword ? (
                                                <svg
                                                    width="18"
                                                    height="18"
                                                    viewBox="0 0 24 24"
                                                    fill="none"
                                                    stroke="currentColor"
                                                    strokeWidth="2"
                                                >
                                                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                                                    <circle
                                                        cx="12"
                                                        cy="12"
                                                        r="3"
                                                    ></circle>
                                                </svg>
                                            ) : (
                                                <svg
                                                    width="18"
                                                    height="18"
                                                    viewBox="0 0 24 24"
                                                    fill="none"
                                                    stroke="currentColor"
                                                    strokeWidth="2"
                                                >
                                                    <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
                                                    <line
                                                        x1="1"
                                                        y1="1"
                                                        x2="23"
                                                        y2="23"
                                                    ></line>
                                                </svg>
                                            )}
                                        </button>
                                    </div>
                                </div>

                                <button
                                    type="submit"
                                    className="btn-auth-submit"
                                    disabled={loading}
                                >
                                    {loading
                                        ? t("common.loading")
                                        : t("auth.login")}
                                </button>
                            </form>
                        </div>
                    ) : (
                        <div className="form-content">
                            <div className="auth-logo-container">
                                <img
                                    src="/image.png"
                                    alt="COFATECH"
                                    className="auth-logo"
                                />
                            </div>
                            <h2 className="auth-title">{t("auth.register")}</h2>

                            <form
                                onSubmit={handleRegisterSubmit}
                                className="auth-form"
                            >
                                {error && (
                                    <Alert
                                        type="error"
                                        message={error}
                                        onClose={() => setError("")}
                                    />
                                )}

                                <div className="form-row">
                                    <div className="form-group">
                                        <label htmlFor="username">
                                            {t("auth.username")} *
                                        </label>
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
                                            placeholder={t(
                                                "form.placeholders.username",
                                            )}
                                            disabled={loading}
                                            required
                                        />
                                    </div>

                                    <div className="form-group">
                                        <label htmlFor="register-email">
                                            {t("auth.email")} *
                                        </label>
                                        <input
                                            type="email"
                                            id="register-email"
                                            value={registerData.email}
                                            onChange={(e) =>
                                                setRegisterData({
                                                    ...registerData,
                                                    email: e.target.value,
                                                })
                                            }
                                            placeholder={t(
                                                "form.placeholders.email",
                                            )}
                                            disabled={loading}
                                            required
                                        />
                                    </div>
                                </div>

                                <div className="form-group">
                                    <label htmlFor="departamento">
                                        {t("auth.department")} *
                                    </label>
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
                                        <option value="">
                                            {t("form.selectDepartment")}
                                        </option>
                                        {departamentos.map((dept) => (
                                            <option
                                                key={dept.id}
                                                value={dept.id}
                                            >
                                                {dept.nombre}
                                            </option>
                                        ))}
                                    </select>
                                </div>

                                <div className="form-row">
                                    <div className="form-group">
                                        <label htmlFor="first_name">
                                            {t("auth.firstName")}
                                        </label>
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
                                            placeholder={t(
                                                "form.placeholders.firstName",
                                            )}
                                            disabled={loading}
                                        />
                                    </div>

                                    <div className="form-group">
                                        <label htmlFor="last_name">
                                            {t("auth.lastName")}
                                        </label>
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
                                            placeholder={t(
                                                "form.placeholders.lastName",
                                            )}
                                            disabled={loading}
                                        />
                                    </div>
                                </div>

                                <div className="form-row">
                                    <div className="form-group">
                                        <label htmlFor="register-password">
                                            {t("auth.password")} *
                                        </label>
                                        <div className="password-input-wrapper">
                                            <input
                                                type={
                                                    showRegisterPassword
                                                        ? "text"
                                                        : "password"
                                                }
                                                id="register-password"
                                                value={registerData.password}
                                                onChange={(e) =>
                                                    setRegisterData({
                                                        ...registerData,
                                                        password:
                                                            e.target.value,
                                                    })
                                                }
                                                placeholder={t(
                                                    "form.placeholders.passwordMinimum",
                                                )}
                                                disabled={loading}
                                                required
                                            />
                                            <button
                                                type="button"
                                                className="password-toggle-btn"
                                                onClick={() =>
                                                    setShowRegisterPassword(
                                                        !showRegisterPassword,
                                                    )
                                                }
                                                disabled={loading}
                                                title={
                                                    showRegisterPassword
                                                        ? t("auth.hidePassword")
                                                        : t("auth.showPassword")
                                                }
                                            >
                                                {showRegisterPassword ? (
                                                    <svg
                                                        width="18"
                                                        height="18"
                                                        viewBox="0 0 24 24"
                                                        fill="none"
                                                        stroke="currentColor"
                                                        strokeWidth="2"
                                                    >
                                                        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                                                        <circle
                                                            cx="12"
                                                            cy="12"
                                                            r="3"
                                                        ></circle>
                                                    </svg>
                                                ) : (
                                                    <svg
                                                        width="18"
                                                        height="18"
                                                        viewBox="0 0 24 24"
                                                        fill="none"
                                                        stroke="currentColor"
                                                        strokeWidth="2"
                                                    >
                                                        <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
                                                        <line
                                                            x1="1"
                                                            y1="1"
                                                            x2="23"
                                                            y2="23"
                                                        ></line>
                                                    </svg>
                                                )}
                                            </button>
                                        </div>
                                    </div>

                                    <div className="form-group">
                                        <label htmlFor="password_confirm">
                                            {t("auth.confirmPassword")} *
                                        </label>
                                        <div className="password-input-wrapper">
                                            <input
                                                type={
                                                    showPasswordConfirm
                                                        ? "text"
                                                        : "password"
                                                }
                                                id="password_confirm"
                                                value={
                                                    registerData.password_confirm
                                                }
                                                onChange={(e) =>
                                                    setRegisterData({
                                                        ...registerData,
                                                        password_confirm:
                                                            e.target.value,
                                                    })
                                                }
                                                placeholder={t(
                                                    "form.placeholders.confirmPassword",
                                                )}
                                                disabled={loading}
                                                required
                                            />
                                            <button
                                                type="button"
                                                className="password-toggle-btn"
                                                onClick={() =>
                                                    setShowPasswordConfirm(
                                                        !showPasswordConfirm,
                                                    )
                                                }
                                                disabled={loading}
                                                title={
                                                    showPasswordConfirm
                                                        ? t("auth.hidePassword")
                                                        : t("auth.showPassword")
                                                }
                                            >
                                                {showPasswordConfirm ? (
                                                    <svg
                                                        width="18"
                                                        height="18"
                                                        viewBox="0 0 24 24"
                                                        fill="none"
                                                        stroke="currentColor"
                                                        strokeWidth="2"
                                                    >
                                                        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                                                        <circle
                                                            cx="12"
                                                            cy="12"
                                                            r="3"
                                                        ></circle>
                                                    </svg>
                                                ) : (
                                                    <svg
                                                        width="18"
                                                        height="18"
                                                        viewBox="0 0 24 24"
                                                        fill="none"
                                                        stroke="currentColor"
                                                        strokeWidth="2"
                                                    >
                                                        <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
                                                        <line
                                                            x1="1"
                                                            y1="1"
                                                            x2="23"
                                                            y2="23"
                                                        ></line>
                                                    </svg>
                                                )}
                                            </button>
                                        </div>
                                    </div>
                                </div>

                                <button
                                    type="submit"
                                    className="btn-auth-submit"
                                    disabled={loading}
                                >
                                    {loading
                                        ? t("common.loading")
                                        : t("auth.register")}
                                </button>
                            </form>
                        </div>
                    )}
                </div>

                <div className="auth-panel-section">
                    <div className="panel-content">
                        <h2 className="panel-title">
                            {isLogin
                                ? t("auth.welcomeGreeting")
                                : t("auth.welcomeBack")}
                        </h2>
                        <p className="panel-subtitle">
                            {isLogin
                                ? t("auth.dontHaveAccount")
                                : t("auth.haveAccount")}
                        </p>
                        <button
                            onClick={handleToggle}
                            className="btn-panel-toggle"
                        >
                            {isLogin ? t("auth.register") : t("auth.login")}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Login;
