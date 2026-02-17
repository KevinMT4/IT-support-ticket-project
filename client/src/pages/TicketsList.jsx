import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { FiDownload } from "react-icons/fi";
import { useAuth } from "../context/AuthContext";
import apiClient from "../api/client";
import Layout from "../components/Layout";
import TicketCard from "../components/TicketCard";
import Loading from "../components/Loading";
import Alert from "../components/Alert";
import ToastContainer from "../components/ToastContainer";
import { useTicketNotifications } from "../hooks/useTicketNotifications";
import "../styles/TicketsList.css";

const TicketsList = () => {
    const [tickets, setTickets] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [filter, setFilter] = useState("all");
    const { isSuperuser } = useAuth();
    const { notifications, removeNotification } = useTicketNotifications(
        tickets,
        isSuperuser(),
    );

    useEffect(() => {
        loadTickets();

        const interval = setInterval(() => {
            loadTickets();
        }, 2000);

        const handleVisibilityChange = () => {
            if (!document.hidden) {
                loadTickets();
            }
        };

        const handleFocus = () => {
            loadTickets();
        };

        document.addEventListener("visibilitychange", handleVisibilityChange);
        window.addEventListener("focus", handleFocus);

        return () => {
            clearInterval(interval);
            document.removeEventListener(
                "visibilitychange",
                handleVisibilityChange,
            );
            window.removeEventListener("focus", handleFocus);
        };
    }, []);

    const loadTickets = async () => {
        try {
            const data = await apiClient.getTickets();
            setTickets(data);
            setError(null);
        } catch (err) {
            setError("Error al cargar los tickets");
            console.error(err);
        } finally {
            if (loading) setLoading(false);
        }
    };

    const filteredTickets = tickets.filter((ticket) => {
        if (filter === "all") return true;
        return ticket.estado === filter;
    });

    const getTicketStats = () => {
        return {
            total: tickets.length,
            abierto: tickets.filter((t) => t.estado === "abierto").length,
            en_proceso: tickets.filter((t) => t.estado === "en_proceso").length,
            resuelto: tickets.filter((t) => t.estado === "resuelto").length,
        };
    };

    const stats = getTicketStats();

    const handleDownloadPDF = async () => {
        try {
            const token = localStorage.getItem("authToken");
            const API_BASE_URL = import.meta.env.VITE_API_PROXY_PATH || "/api";

            const response = await fetch(
                `${API_BASE_URL}/reportes/pdf-estadisticas/`,
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
            a.download = `reporte_tickets_${new Date().toISOString().split("T")[0]}.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } catch (err) {
            setError("Error al descargar el reporte PDF");
            console.error(err);
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
            <ToastContainer
                notifications={notifications}
                onRemove={removeNotification}
            />
            <div className="tickets-container">
                <div className="tickets-header">
                    <div>
                        <h1>Mis Tickets</h1>
                        <p className="subtitle">
                            {isSuperuser()
                                ? "Todos los tickets del sistema"
                                : "Tickets que has creado"}
                        </p>
                    </div>
                    <div className="header-actions">
                        {isSuperuser() && (
                            <button
                                className="btn-pdf"
                                onClick={handleDownloadPDF}
                            >
                                <FiDownload /> PDF Semanal
                            </button>
                        )}
                        {!isSuperuser() && (
                            <Link to="/tickets/new" className="btn-create">
                                + Nuevo Ticket
                            </Link>
                        )}
                    </div>
                </div>

                <div className="stats-grid">
                    <div
                        className={`stat-card stat-clickable ${filter === "all" ? "active" : ""}`}
                        onClick={() => setFilter("all")}
                    >
                        <div className="stat-value">{stats.total}</div>
                        <div className="stat-label">Total</div>
                    </div>
                    <div
                        className={`stat-card stat-open stat-clickable ${filter === "abierto" ? "active" : ""}`}
                        onClick={() => setFilter("abierto")}
                    >
                        <div className="stat-value">{stats.abierto}</div>
                        <div className="stat-label">Abiertos</div>
                    </div>
                    <div
                        className={`stat-card stat-progress stat-clickable ${filter === "en_proceso" ? "active" : ""}`}
                        onClick={() => setFilter("en_proceso")}
                    >
                        <div className="stat-value">{stats.en_proceso}</div>
                        <div className="stat-label">En Proceso</div>
                    </div>
                    <div
                        className={`stat-card stat-resolved stat-clickable ${filter === "resuelto" ? "active" : ""}`}
                        onClick={() => setFilter("resuelto")}
                    >
                        <div className="stat-value">{stats.resuelto}</div>
                        <div className="stat-label">Resueltos</div>
                    </div>
                </div>

                {error && (
                    <Alert
                        type="error"
                        message={error}
                        onClose={() => setError(null)}
                    />
                )}

                {filteredTickets.length === 0 ? (
                    <div className="empty-state">
                        <p>No hay tickets para mostrar</p>
                        {!isSuperuser() && (
                            <Link
                                to="/tickets/new"
                                className="btn-create-empty"
                            >
                                Crear primer ticket
                            </Link>
                        )}
                    </div>
                ) : (
                    <div className="tickets-grid">
                        {filteredTickets.map((ticket) => (
                            <TicketCard key={ticket.id} ticket={ticket} />
                        ))}
                    </div>
                )}
            </div>
        </Layout>
    );
};

export default TicketsList;
