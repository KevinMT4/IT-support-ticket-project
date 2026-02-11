import { useState, useEffect } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import apiClient from "../api/client";
import Layout from "../components/Layout";
import Loading from "../components/Loading";
import Alert from "../components/Alert";
import "../styles/TicketDetail.css";

const TicketDetail = () => {
    const { id } = useParams();
    const [ticket, setTicket] = useState(null);
    const [loading, setLoading] = useState(true);
    const [updating, setUpdating] = useState(false);
    const [error, setError] = useState(null);
    const [successMessage, setSuccessMessage] = useState("");
    const { isSuperuser } = useAuth();
    const navigate = useNavigate();

    useEffect(() => {
        loadTicket();
    }, [id]);

    const loadTicket = async () => {
        try {
            setLoading(true);
            const data = await apiClient.getTicket(id);
            setTicket(data);
            setError(null);
        } catch (err) {
            setError("Error al cargar el ticket");
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleStatusChange = async (newStatus) => {
        try {
            setUpdating(true);
            const updatedTicket = await apiClient.updateTicketStatus(
                id,
                newStatus,
            );
            setTicket(updatedTicket);
            setSuccessMessage("Estado actualizado correctamente");
            setTimeout(() => setSuccessMessage(""), 3000);
        } catch (err) {
            setError("Error al actualizar el estado");
            console.error(err);
        } finally {
            setUpdating(false);
        }
    };

    const formatDate = (dateString) => {
        if (!dateString) return "N/A";
        const date = new Date(dateString);
        return date.toLocaleDateString("es-ES", {
            year: "numeric",
            month: "long",
            day: "numeric",
            hour: "2-digit",
            minute: "2-digit",
        });
    };

    const getPriorityClass = (prioridad) => {
        const classes = {
            baja: "priority-low",
            media: "priority-medium",
            alta: "priority-high",
            urgente: "priority-urgent",
        };
        return classes[prioridad] || "priority-medium";
    };

    const getStatusClass = (estado) => {
        const classes = {
            abierto: "status-open",
            en_proceso: "status-in-progress",
            resuelto: "status-resolved",
            cerrado: "status-closed",
        };
        return classes[estado] || "status-open";
    };

    if (loading) {
        return (
            <Layout>
                <Loading />
            </Layout>
        );
    }

    if (error && !ticket) {
        return (
            <Layout>
                <div className="error-container">
                    <p>{error}</p>
                    <button
                        onClick={() => navigate("/tickets")}
                        className="btn-back"
                    >
                        Volver a Tickets
                    </button>
                </div>
            </Layout>
        );
    }

    return (
        <Layout>
            <div className="ticket-detail-container">
                <div className="ticket-detail-header">
                    <Link to="/tickets" className="back-link">
                        ← Volver a Tickets
                    </Link>
                    <div className="header-content">
                        <div className="header-left">
                            <h1>Ticket #{ticket.id}</h1>
                            <div className="ticket-badges-detail">
                                <span
                                    className={`badge priority-badge ${getPriorityClass(ticket.prioridad)}`}
                                >
                                    {ticket.prioridad_display}
                                </span>
                                <span
                                    className={`badge status-badge ${getStatusClass(ticket.estado)}`}
                                >
                                    {ticket.estado_display}
                                </span>
                            </div>
                        </div>
                    </div>
                </div>

                {successMessage && (
                    <Alert
                        type="success"
                        message={successMessage}
                        onClose={() => setSuccessMessage("")}
                    />
                )}
                {error && (
                    <Alert
                        type="error"
                        message={error}
                        onClose={() => setError(null)}
                    />
                )}

                <div className="ticket-detail-content">
                    <div className="ticket-main">
                        <div className="ticket-section">
                            <h2 className="ticket-subject">{ticket.asunto}</h2>
                            <div className="ticket-meta">
                                <span>Creado por: {ticket.usuario_nombre}</span>
                                <span>•</span>
                                <span>{formatDate(ticket.fecha_creacion)}</span>
                            </div>
                        </div>

                        <div className="ticket-section">
                            <h3>Descripción</h3>
                            <div className="ticket-description">
                                {ticket.contenido}
                            </div>
                        </div>

                        {isSuperuser() && (
                            <div className="ticket-section">
                                <h3>Actualizar Estado</h3>
                                <div className="status-buttons">
                                    <button
                                        className={`status-btn ${ticket.estado === "abierto" ? "active" : ""}`}
                                        onClick={() =>
                                            handleStatusChange("abierto")
                                        }
                                        disabled={
                                            updating ||
                                            ticket.estado === "abierto"
                                        }
                                    >
                                        Abierto
                                    </button>
                                    <button
                                        className={`status-btn ${ticket.estado === "en_proceso" ? "active" : ""}`}
                                        onClick={() =>
                                            handleStatusChange("en_proceso")
                                        }
                                        disabled={
                                            updating ||
                                            ticket.estado === "en_proceso"
                                        }
                                    >
                                        En Proceso
                                    </button>
                                    <button
                                        className={`status-btn ${ticket.estado === "resuelto" ? "active" : ""}`}
                                        onClick={() =>
                                            handleStatusChange("resuelto")
                                        }
                                        disabled={
                                            updating ||
                                            ticket.estado === "resuelto"
                                        }
                                    >
                                        Resuelto
                                    </button>
                                    <button
                                        className={`status-btn ${ticket.estado === "cerrado" ? "active" : ""}`}
                                        onClick={() =>
                                            handleStatusChange("cerrado")
                                        }
                                        disabled={
                                            updating ||
                                            ticket.estado === "cerrado"
                                        }
                                    >
                                        Cerrado
                                    </button>
                                </div>
                            </div>
                        )}
                    </div>

                    <div className="ticket-sidebar">
                        <div className="info-card">
                            <h3>Información</h3>
                            <div className="info-item">
                                <span className="info-label">Departamento</span>
                                <span className="info-value">
                                    {ticket.usuario_departamento_nombre}
                                </span>
                            </div>
                            {ticket.motivo_nombre && (
                                <div className="info-item">
                                    <span className="info-label">Motivo</span>
                                    <span className="info-value">
                                        {ticket.motivo_nombre}
                                    </span>
                                </div>
                            )}
                            <div className="info-item">
                                <span className="info-label">Prioridad</span>
                                <span className="info-value">
                                    {ticket.prioridad_display}
                                </span>
                            </div>
                            <div className="info-item">
                                <span className="info-label">Estado</span>
                                <span className="info-value">
                                    {ticket.estado_display}
                                </span>
                            </div>
                            <div className="info-item">
                                <span className="info-label">Creado</span>
                                <span className="info-value">
                                    {formatDate(ticket.fecha_creacion)}
                                </span>
                            </div>
                            {ticket.fecha_cierre && (
                                <div className="info-item">
                                    <span className="info-label">Cerrado</span>
                                    <span className="info-value">
                                        {formatDate(ticket.fecha_cierre)}
                                    </span>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </Layout>
    );
};

export default TicketDetail;
