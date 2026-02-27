import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useLanguage } from "../hooks/useLanguage";
import { useAuth } from "../context/AuthContext";
import apiClient from "../api/client";
import Layout from "../components/Layout";
import Loading from "../components/Loading";
import Alert from "../components/Alert";
import "../styles/CreateTicket.css";

const CreateTicket = () => {
    const { isSuperuser } = useAuth();
    const { t } = useLanguage();
    const [formData, setFormData] = useState({
        motivo: "",
        asunto: "",
        contenido: "",
    });
    const [departamentoTI, setDepartamentoTI] = useState(null);
    const [motivos, setMotivos] = useState([]);
    const [loading, setLoading] = useState(true);
    const [submitting, setSubmitting] = useState(false);
    const [error, setError] = useState(null);
    const navigate = useNavigate();

    useEffect(() => {
        if (isSuperuser()) {
            navigate("/tickets");
            return;
        }
        loadDepartamentoTI();
    }, [isSuperuser, navigate]);

    const loadDepartamentoTI = async () => {
        try {
            const departamentos = await apiClient.getDepartamentos();
            const tiDept = departamentos.find(
                (d) =>
                    d.nombre.toLowerCase().includes("tecnologia") &&
                    d.nombre.toLowerCase().includes("informacion"),
            );

            if (!tiDept) {
                setError(t("messages.ticketCreatedSuccessfully"));
                setLoading(false);
                return;
            }

            setDepartamentoTI(tiDept);
            await loadMotivos(tiDept.id);
            setLoading(false);
        } catch (err) {
            setError(t("common.errorLoadingTickets"));
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
            setError(t("form.required"));
            return;
        }

        if (!departamentoTI) {
            setError(t("common.errorLoadingTickets"));
            return;
        }

        setSubmitting(true);

        try {
            const ticketData = {
                departamento: departamentoTI.id,
                motivo: formData.motivo ? parseInt(formData.motivo) : null,
                asunto: formData.asunto,
                contenido: formData.contenido,
            };

            await apiClient.createTicket(ticketData);
            navigate("/tickets");
        } catch (err) {
            setError(err.message || t("createTicket.createError"));
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
                    <h1>{t("common.createNewTicket").replace("+ ", "")}</h1>
                    <p className="subtitle">{t("createTicket.subtitle")}</p>
                </div>

                <form onSubmit={handleSubmit} className="ticket-form">
                    {error && (
                        <Alert
                            type="error"
                            message={error}
                            onClose={() => setError(null)}
                        />
                    )}

                    <div className="form-group">
                        <label>{t("ticket.department")}</label>
                        <div className="department-display">
                            {departamentoTI?.nombre || t("common.loading")}
                        </div>
                    </div>

                    <div className="form-group">
                        <label htmlFor="motivo">{t("ticket.reason")}</label>
                        <select
                            id="motivo"
                            name="motivo"
                            value={formData.motivo}
                            onChange={handleChange}
                            disabled={submitting}
                        >
                            <option value="">{t("form.selectReason")}</option>
                            {motivos.map((motivo) => (
                                <option key={motivo.id} value={motivo.id}>
                                    {motivo.nombre}
                                </option>
                            ))}
                        </select>
                    </div>

                    <div className="form-group">
                        <label htmlFor="asunto">
                            {t("ticket.subject")}{" "}
                            <span className="required">*</span>
                        </label>
                        <input
                            type="text"
                            id="asunto"
                            name="asunto"
                            value={formData.asunto}
                            onChange={handleChange}
                            placeholder={t("form.placeholderSubject")}
                            required
                            disabled={submitting}
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="contenido">
                            {t("ticket.description")}{" "}
                            <span className="required">*</span>
                        </label>
                        <textarea
                            id="contenido"
                            name="contenido"
                            value={formData.contenido}
                            onChange={handleChange}
                            placeholder={t("form.placeholderDescription")}
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
                            {t("form.cancel")}
                        </button>
                        <button
                            type="submit"
                            className="btn-submit"
                            disabled={submitting}
                        >
                            {submitting
                                ? t("common.loading")
                                : t("form.createButton")}
                        </button>
                    </div>
                </form>
            </div>
        </Layout>
    );
};

export default CreateTicket;
