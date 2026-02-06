import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import apiClient from "../api/client";
import Layout from "../components/Layout";
import Loading from "../components/Loading";
import "../styles/CreateTicket.css";

const CreateTicket = () => {
    const [formData, setFormData] = useState({
        motivo: "",
        asunto: "",
        contenido: "",
        prioridad: "media",
    });
    const [departamentoTI, setDepartamentoTI] = useState(null);
    const [motivos, setMotivos] = useState([]);
    const [loading, setLoading] = useState(true);
    const [submitting, setSubmitting] = useState(false);
    const [error, setError] = useState(null);
    const navigate = useNavigate();

    useEffect(() => {
        loadDepartamentoTI();
    }, []);

    const loadDepartamentoTI = async () => {
        try {
            const departamentos = await apiClient.getDepartamentos();
            const tiDept = departamentos.find(
                (d) =>
                    d.nombre.toLowerCase().includes("tecnolog") ||
                    d.nombre.toLowerCase().includes("ti"),
            );

            if (!tiDept) {
                setError(
                    "No se encontró el departamento de TI. Por favor contacta al administrador.",
                );
                setLoading(false);
                return;
            }

            setDepartamentoTI(tiDept);
            await loadMotivos(tiDept.id);
            setLoading(false);
        } catch (err) {
            setError("Error al cargar departamento de TI");
            setLoading(false);
        }
    };

    const loadMotivos = async (departamentoId) => {
        try {
            const data = await apiClient.getMotivos(departamentoId);
            setMotivos(data);
        } catch (err) {
            console.error("Error al cargar motivos:", err);
            setMotivos([]);
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
        setError(null);

        if (!formData.asunto || !formData.contenido) {
            setError("Por favor completa todos los campos requeridos");
            return;
        }

        if (!departamentoTI) {
            setError("No se pudo cargar el departamento de TI");
            return;
        }

        setSubmitting(true);

        try {
            const ticketData = {
                departamento: departamentoTI.id,
                motivo: formData.motivo ? parseInt(formData.motivo) : null,
                asunto: formData.asunto,
                contenido: formData.contenido,
                prioridad: formData.prioridad,
            };

            const newTicket = await apiClient.createTicket(ticketData);
            navigate(`/tickets/${newTicket.id}`);
        } catch (err) {
            setError(err.message || "Error al crear el ticket");
            setSubmitting(false);
        }
    };

    if (loading) {
        return (
            <Layout>
                <Loading />
            </Layout>
        );
    }

    return (
        <Layout>
            <div className="create-ticket-container">
                <div className="create-ticket-header">
                    <h1>Crear Nuevo Ticket</h1>
                    <p className="subtitle">
                        Completa el formulario para crear un nuevo ticket de
                        soporte
                    </p>
                </div>

                <form onSubmit={handleSubmit} className="ticket-form">
                    {error && <div className="error-message">{error}</div>}

                    <div className="form-group">
                        <label>Departamento</label>
                        <div className="department-display">
                            {departamentoTI?.nombre || "Cargando..."}
                        </div>
                    </div>

                    <div className="form-row">
                        <div className="form-group">
                            <label htmlFor="motivo">Motivo</label>
                            <select
                                id="motivo"
                                name="motivo"
                                value={formData.motivo}
                                onChange={handleChange}
                                disabled={submitting}
                            >
                                <option value="">
                                    Selecciona un motivo (opcional)
                                </option>
                                {motivos.map((motivo) => (
                                    <option key={motivo.id} value={motivo.id}>
                                        {motivo.nombre}
                                    </option>
                                ))}
                            </select>
                        </div>

                        <div className="form-group">
                            <label htmlFor="prioridad">
                                Prioridad <span className="required">*</span>
                            </label>
                            <select
                                id="prioridad"
                                name="prioridad"
                                value={formData.prioridad}
                                onChange={handleChange}
                                required
                                disabled={submitting}
                            >
                                <option value="baja">Baja</option>
                                <option value="media">Media</option>
                                <option value="alta">Alta</option>
                                <option value="urgente">Urgente</option>
                            </select>
                        </div>
                    </div>

                    <div className="form-group">
                        <label htmlFor="asunto">
                            Asunto <span className="required">*</span>
                        </label>
                        <input
                            type="text"
                            id="asunto"
                            name="asunto"
                            value={formData.asunto}
                            onChange={handleChange}
                            placeholder="Describe brevemente el problema"
                            required
                            disabled={submitting}
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="contenido">
                            Descripción <span className="required">*</span>
                        </label>
                        <textarea
                            id="contenido"
                            name="contenido"
                            value={formData.contenido}
                            onChange={handleChange}
                            placeholder="Describe detalladamente el problema o solicitud"
                            rows={8}
                            required
                            disabled={submitting}
                        />
                    </div>

                    <div className="form-actions">
                        <button
                            type="button"
                            className="btn-cancel"
                            onClick={() => navigate("/tickets")}
                            disabled={submitting}
                        >
                            Cancelar
                        </button>
                        <button
                            type="submit"
                            className="btn-submit"
                            disabled={submitting}
                        >
                            {submitting ? "Creando..." : "Crear Ticket"}
                        </button>
                    </div>
                </form>
            </div>
        </Layout>
    );
};

export default CreateTicket;
