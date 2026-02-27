import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { FiDownload, FiSearch, FiFilter, FiX } from "react-icons/fi";
import { useLanguage } from "../hooks/useLanguage";
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
    const [searchTerm, setSearchTerm] = useState("");
    const [selectedMotivo, setSelectedMotivo] = useState("");
    const [startDate, setStartDate] = useState("");
    const [endDate, setEndDate] = useState("");
    const [motivos, setMotivos] = useState([]);
    const [showFilters, setShowFilters] = useState(false);
    const { isSuperuser } = useAuth();
    const { t, currentLanguage } = useLanguage();
    const { notifications, removeNotification } = useTicketNotifications(
        tickets,
        isSuperuser(),
    );

    useEffect(() => {
        loadTickets();
        if (isSuperuser()) {
            loadMotivos();
        }

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

    const loadMotivos = async () => {
        try {
            const data = await apiClient.getMotivos();
            setMotivos(data);
        } catch (err) {
            console.error("Error loading motivos:", err);
        }
    };

    const filteredTickets = tickets.filter((ticket) => {
        if (filter !== "all" && ticket.estado !== filter) {
            return false;
        }

        if (searchTerm) {
            const search = searchTerm.toLowerCase();
            const matchesSubject = ticket.asunto.toLowerCase().includes(search);
            const matchesContent = ticket.contenido
                .toLowerCase()
                .includes(search);
            const matchesUser = ticket.usuario_nombre
                .toLowerCase()
                .includes(search);

            if (!matchesSubject && !matchesContent && !matchesUser) {
                return false;
            }
        }

        if (selectedMotivo && ticket.motivo !== parseInt(selectedMotivo)) {
            return false;
        }

        if (startDate) {
            const ticketDate = new Date(ticket.fecha_creacion);
            const filterStartDate = new Date(startDate);
            if (ticketDate < filterStartDate) {
                return false;
            }
        }

        if (endDate) {
            const ticketDate = new Date(ticket.fecha_creacion);
            const filterEndDate = new Date(endDate);
            filterEndDate.setHours(23, 59, 59, 999);
            if (ticketDate > filterEndDate) {
                return false;
            }
        }

        return true;
    });

    const clearFilters = () => {
        setSearchTerm("");
        setSelectedMotivo("");
        setStartDate("");
        setEndDate("");
        setFilter("all");
    };

    const hasActiveFilters =
        searchTerm ||
        selectedMotivo ||
        startDate ||
        endDate ||
        filter !== "all";

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
                        "Accept-Language": currentLanguage,
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

                {isSuperuser() && (
                    <div className="filters-section">
                        <button
                            className="btn-toggle-filters"
                            onClick={() => setShowFilters(!showFilters)}
                        >
                            <FiFilter />
                            {showFilters
                                ? t("Ocultar Filtros")
                                : t("Mostrar Filtros")}
                        </button>

                        {showFilters && (
                            <div className="advanced-filters">
                                <div className="filter-row">
                                    <div className="filter-group filter-search">
                                        <label>
                                            <FiSearch />
                                            <input
                                                type="text"
                                                placeholder={t("Buscar")}
                                                value={searchTerm}
                                                onChange={(e) =>
                                                    setSearchTerm(
                                                        e.target.value,
                                                    )
                                                }
                                                className="filter-input"
                                            />
                                        </label>
                                    </div>

                                    <div className="filter-group">
                                        <select
                                            value={selectedMotivo}
                                            onChange={(e) =>
                                                setSelectedMotivo(
                                                    e.target.value,
                                                )
                                            }
                                            className="filter-select"
                                        >
                                            <option value="">
                                                {t("Filtros por Motivo")}
                                            </option>
                                            {motivos.map((motivo) => (
                                                <option
                                                    key={motivo.id}
                                                    value={motivo.id}
                                                >
                                                    {motivo.nombre}
                                                </option>
                                            ))}
                                        </select>
                                    </div>

                                    <div className="filter-group">
                                        <input
                                            type="date"
                                            value={startDate}
                                            onChange={(e) =>
                                                setStartDate(e.target.value)
                                            }
                                            className="filter-input"
                                            placeholder={t("filters.startDate")}
                                        />
                                    </div>

                                    <div className="filter-group">
                                        <input
                                            type="date"
                                            value={endDate}
                                            onChange={(e) =>
                                                setEndDate(e.target.value)
                                            }
                                            className="filter-input"
                                            placeholder={t("filters.endDate")}
                                        />
                                    </div>

                                    {hasActiveFilters && (
                                        <button
                                            className="btn-clear-filters"
                                            onClick={clearFilters}
                                            title={t("filters.clearFilters")}
                                        >
                                            <FiX />
                                            {t("filters.clearFilters")}
                                        </button>
                                    )}
                                </div>

                                <div className="filter-results">
                                    {filteredTickets.length}{" "}
                                    {t("Resultados Encontrados")}
                                </div>
                            </div>
                        )}
                    </div>
                )}

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
