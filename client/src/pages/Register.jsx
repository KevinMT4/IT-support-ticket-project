import { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import apiClient from "../api/client";
import Alert from "../components/Alert";
import "../styles/Register.css";

const Register = () => {
    const [formData, setFormData] = useState({
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
    const [loadingDepartments, setLoadingDepartments] = useState(true);
    const { register } = useAuth();
    const navigate = useNavigate();

    useEffect(() => {
        loadDepartamentos();
    }, []);

    const loadDepartamentos = async () => {
        try {
            const data = await apiClient.getDepartamentos();
            setDepartamentos(data);
        } catch (err) {
            setError("Error al cargar los departamentos");
            console.error(err);
        } finally {
            setLoadingDepartments(false);
        }
    };

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData((prev) => ({
            ...prev,
            [name]: value,
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError("");

        if (
            !formData.username ||
            !formData.email ||
            !formData.departamento ||
            !formData.password ||
            !formData.password_confirm
        ) {
            setError("Por favor completa los campos requeridos");
            return;
        }

        if (formData.password !== formData.password_confirm) {
            setError("Las contraseñas no coinciden");
            return;
        }

        if (formData.password.length < 8) {
            setError("La contraseña debe tener al menos 8 caracteres");
            return;
        }

        setLoading(true);

        const dataToSubmit = {
            ...formData,
            departamento: parseInt(formData.departamento),
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
        <div className="register-container">
            <div className="register-box">
                <h1 className="register-title">Crear Cuenta</h1>
                <p className="register-subtitle">
                    Regístrate para acceder al sistema
                </p>

                <form onSubmit={handleSubmit} className="register-form">
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
                            name="username"
                            value={formData.username}
                            onChange={handleChange}
                            placeholder="Nombre de usuario"
                            disabled={loading}
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="email">Correo Electrónico *</label>
                        <input
                            type="email"
                            id="email"
                            name="email"
                            value={formData.email}
                            onChange={handleChange}
                            placeholder="correo@ejemplo.com"
                            disabled={loading}
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="departamento">Departamento *</label>
                        <select
                            id="departamento"
                            name="departamento"
                            value={formData.departamento}
                            onChange={handleChange}
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
                                name="first_name"
                                value={formData.first_name}
                                onChange={handleChange}
                                placeholder="Tu nombre"
                                disabled={loading}
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="last_name">Apellido</label>
                            <input
                                type="text"
                                id="last_name"
                                name="last_name"
                                value={formData.last_name}
                                onChange={handleChange}
                                placeholder="Tu apellido"
                                disabled={loading}
                            />
                        </div>
                    </div>

                    <div className="form-group">
                        <label htmlFor="password">Contraseña *</label>
                        <input
                            type="password"
                            id="password"
                            name="password"
                            value={formData.password}
                            onChange={handleChange}
                            placeholder="Mínimo 8 caracteres"
                            disabled={loading}
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="password_confirm">
                            Confirmar Contraseña *
                        </label>
                        <input
                            type="password"
                            id="password_confirm"
                            name="password_confirm"
                            value={formData.password_confirm}
                            onChange={handleChange}
                            placeholder="Repite tu contraseña"
                            disabled={loading}
                            required
                        />
                    </div>

                    <button
                        type="submit"
                        className="btn-register"
                        disabled={loading}
                    >
                        {loading ? "Creando cuenta..." : "Crear Cuenta"}
                    </button>
                </form>

                <p className="register-footer">
                    ¿Ya tienes cuenta?{" "}
                    <Link to="/login" className="link-login">
                        Inicia sesión aquí
                    </Link>
                </p>
            </div>
        </div>
    );
};

export default Register;
