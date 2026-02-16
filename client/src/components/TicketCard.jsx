import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import "../styles/TicketCard.css";

const TicketCard = ({ ticket }) => {
    const { isSuperuser } = useAuth();

    const formatDate = (dateString) => {
        if (!dateString) return "N/A";
        const date = new Date(dateString);
        return date.toLocaleDateString("es-ES", {
            year: "numeric",
            month: "short",
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
        };
        return classes[estado] || "status-open";
    };

    const handleDownloadPDF = async (e) => {
        e.preventDefault();
        e.stopPropagation();

        try {
            const token = localStorage.getItem("authToken");
            const API_BASE_URL = import.meta.env.VITE_API_PROXY_PATH || "/api";

            const response = await fetch(
                `${API_BASE_URL}/reportes/pdf-ticket/${ticket.id}/`,
                {
                    method: "GET",
                    headers: {
                        Authorization: `Token ${token}`,
                    },
                },
            );

            if (!response.ok) {
                throw new Error("Error al generar el PDF");
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = `ticket_${ticket.id}_${new Date().toISOString().split("T")[0]}.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } catch (err) {
            console.error("Error al descargar el PDF:", err);
        }
    };

    return (
        <Link to={`/tickets/${ticket.id}`} className="ticket-link">
            <div className="ticket-card">
                <div className="ticket-header">
                    <div className="ticket-badges">
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
                    {isSuperuser() && (
                        <button
                            className="ticket-download-btn"
                            onClick={handleDownloadPDF}
                            title="Descargar PDF"
                            aria-label="Descargar PDF del ticket"
                        >
                            <svg
                                width="20"
                                height="20"
                                viewBox="0 0 24 24"
                                fill="none"
                                stroke="currentColor"
                                strokeWidth="2"
                                strokeLinecap="round"
                                strokeLinejoin="round"
                            >
                                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                                <polyline points="7 10 12 15 17 10"></polyline>
                                <line x1="12" y1="15" x2="12" y2="3"></line>
                            </svg>
                        </button>
                    )}
                </div>
                <h3 className="ticket-title">{ticket.asunto}</h3>
                <p className="ticket-content">
                    {ticket.contenido.substring(0, 150)}...
                </p>
                <div className="ticket-footer">
                    <div className="ticket-info">
                        <span className="ticket-department">
                            {ticket.usuario_departamento_nombre}
                        </span>
                        {ticket.motivo_nombre && (
                            <span className="ticket-reason">
                                {" "}
                                • {ticket.motivo_nombre}
                            </span>
                        )}
                    </div>
                    <div className="ticket-date">
                        {formatDate(ticket.fecha_creacion)}
                    </div>
                </div>
            </div>
        </Link>
    );
};

export default TicketCard;
