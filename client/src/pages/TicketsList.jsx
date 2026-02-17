import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { FiDownload } from "react-icons/fi";
import { useTranslation } from "react-i18next";
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
    const { t } = useTranslation();
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
            setError(t("common.errorLoadingTickets"));
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
            setError(t("messages.pdfDownloadError"));
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
                        <h1>{t("common.myTickets")}</h1>
                        <p className="subtitle">
                            {isSuperuser()
                                ? t("common.allTicketsInSystem")
                                : t("common.ticketsYouCreated")}
                        </p>
                    </div>
                    <div className="header-actions">
                        {isSuperuser() && (
                            <button
                                className="btn-pdf"
                                onClick={handleDownloadPDF}
                            >
                                <FiDownload /> {t("common.pdfWeekly")}
                            </button>
                        )}
                        {!isSuperuser() && (
                            <Link to="/tickets/new" className="btn-create">
                                {t("common.createNewTicket")}
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
                        <div className="stat-label">{t("stats.total")}</div>
                    </div>
                    <div
                        className={`stat-card stat-open stat-clickable ${filter === "abierto" ? "active" : ""}`}
                        onClick={() => setFilter("abierto")}
                    >
                        <div className="stat-value">{stats.abierto}</div>
                        <div className="stat-label">{t("stats.open")}</div>
                    </div>
                    <div
                        className={`stat-card stat-progress stat-clickable ${filter === "en_proceso" ? "active" : ""}`}
                        onClick={() => setFilter("en_proceso")}
                    >
                        <div className="stat-value">{stats.en_proceso}</div>
                        <div className="stat-label">
                            {t("stats.inProgress")}
                        </div>
                    </div>
                    <div
                        className={`stat-card stat-resolved stat-clickable ${filter === "resuelto" ? "active" : ""}`}
                        onClick={() => setFilter("resuelto")}
                    >
                        <div className="stat-value">{stats.resuelto}</div>
                        <div className="stat-label">{t("stats.resolved")}</div>
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
                        <p>{t("common.noTicketsToShow")}</p>
                        {!isSuperuser() && (
                            <Link
                                to="/tickets/new"
                                className="btn-create-empty"
                            >
                                {t("common.createOne")}
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
