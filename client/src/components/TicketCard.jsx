import { Link } from "react-router-dom";
import "../styles/TicketCard.css";

const TicketCard = ({ ticket }) => {
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
            cerrado: "status-closed",
        };
        return classes[estado] || "status-open";
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
