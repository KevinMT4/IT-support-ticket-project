import { useState, useEffect } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useLanguage } from "../hooks/useLanguage";
import apiClient from "../api/client";
import Layout from "../components/Layout";
import Loading from "../components/Loading";
import Alert from "../components/Alert";
import { playSuccessSound } from "../utils/sounds";
import "../styles/TicketDetail.css";

const TicketDetail = () => {
    const { id } = useParams();
    const [ticket, setTicket] = useState(null);
    const [loading, setLoading] = useState(true);
    const [updating, setUpdating] = useState(false);
    const [error, setError] = useState(null);
    const [successMessage, setSuccessMessage] = useState("");
    const [showResolutionModal, setShowResolutionModal] = useState(false);
    const [resolutionText, setResolutionText] = useState("");
    const [resolutionImages, setResolutionImages] = useState([]);
    const [uploadingImage, setUploadingImage] = useState(false);
    const [selectedImageIndex, setSelectedImageIndex] = useState(null);
    const { isSuperuser } = useAuth();
    const { t, currentLanguage } = useLanguage();
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
            setError(t("ticketDetail.errorLoadingTicket"));
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleStatusChange = async (newStatus) => {
        if (newStatus === "resuelto") {
            setShowResolutionModal(true);
            return;
        }

        try {
            setUpdating(true);
            const updatedTicket = await apiClient.updateTicketStatus(
                id,
                newStatus,
            );
            setTicket(updatedTicket);
            playSuccessSound();
            setSuccessMessage(t("messages.stateUpdatedSuccessfully"));
            setTimeout(() => setSuccessMessage(""), 3000);
        } catch (err) {
            setError(t("messages.errorUpdatingStatus"));
            console.error(err);
        } finally {
            setUpdating(false);
        }
    };

    const handlePriorityChange = async (newPriority) => {
        try {
            setUpdating(true);
            const updatedTicket = await apiClient.updateTicketPriority(
                id,
                newPriority,
            );
            setTicket(updatedTicket);
            playSuccessSound();
            setSuccessMessage(t("messages.priorityUpdatedSuccessfully"));
            setTimeout(() => setSuccessMessage(""), 3000);
        } catch (err) {
            setError(t("messages.errorUpdatingPriority"));
            console.error(err);
        } finally {
            setUpdating(false);
        }
    };

    const handleImageUpload = async (event) => {
        const files = Array.from(event.target.files);

        for (const file of files) {
            try {
                setUploadingImage(true);
                // Crear una previsualización local mientras se sube
                const reader = new FileReader();
                reader.onload = (e) => {
                    // Agregar previsualización local temporalmente
                    setResolutionImages((prev) => [
                        ...prev,
                        {
                            url: e.target.result,
                            isLocal: true,
                            fileName: file.name,
                        },
                    ]);
                };
                reader.readAsDataURL(file);

                // Subir a servidor
                const formData = new FormData();
                formData.append("imagen", file);
                const response = await apiClient.uploadImage(formData);

                // Reemplazar previsualización con URL del servidor
                setResolutionImages((prev) => {
                    const index = prev.findIndex(
                        (img) => img.fileName === file.name && img.isLocal,
                    );
                    if (index !== -1) {
                        const updated = [...prev];
                        updated[index] = { url: response.url, isLocal: false };
                        return updated;
                    }
                    return [...prev, { url: response.url, isLocal: false }];
                });
            } catch (err) {
                setError(t("messages.errorUploadingImage"));
                console.error(err);
                // Remover la previsualización si falla la subida
                setResolutionImages((prev) =>
                    prev.filter((img) => img.fileName !== file.name),
                );
            } finally {
                setUploadingImage(false);
            }
        }
    };

    const removeImage = (index) => {
        setResolutionImages(resolutionImages.filter((_, i) => i !== index));
        setSelectedImageIndex(null);
    };

    const handleResolutionSubmit = async () => {
        try {
            setUpdating(true);
            // Mapear solo las URLs del servidor (no las previsualizaciones locales)
            const serverImages = resolutionImages
                .filter((img) => !img.isLocal)
                .map((img) => img.url);

            const updatedTicket = await apiClient.updateTicketStatus(
                id,
                "resuelto",
                {
                    solucion_texto: resolutionText,
                    solucion_imagenes: serverImages,
                },
            );
            setTicket(updatedTicket);
            playSuccessSound();
            setSuccessMessage(t("messages.stateUpdatedSuccessfully"));
            setTimeout(() => setSuccessMessage(""), 3000);
            setShowResolutionModal(false);
            setResolutionText("");
            setResolutionImages([]);
        } catch (err) {
            setError(t("messages.errorUpdatingStatus"));
            console.error(err);
        } finally {
            setUpdating(false);
        }
    };

    const formatDate = (dateString) => {
        if (!dateString) return "N/A";
        const date = new Date(dateString);
        const locale = currentLanguage === "es" ? "es-ES" : "en-US";
        return date.toLocaleDateString(locale, {
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
        };
        return classes[estado] || "status-open";
    };

    const translatePriority = (prioridad) => {
        const translations = {
            baja: t("priority.low"),
            media: t("priority.medium"),
            alta: t("priority.high"),
            urgente: t("priority.urgent"),
        };
        return translations[prioridad] || prioridad;
    };

    const translateStatus = (estado) => {
        const translations = {
            abierto: t("status.open"),
            en_proceso: t("status.inProgress"),
            resuelto: t("status.resolved"),
        };
        return translations[estado] || estado;
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
                        {t("ticket.backToTickets")}
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
                        {t("ticket.backToTickets")}
                    </Link>
                    <div className="header-content">
                        <div className="header-left">
                            <h1>{t("ticket.details")}</h1>
                            <div className="ticket-badges-detail">
                                <span
                                    className={`badge priority-badge ${getPriorityClass(ticket.prioridad)}`}
                                >
                                    {translatePriority(ticket.prioridad)}
                                </span>
                                <span
                                    className={`badge status-badge ${getStatusClass(ticket.estado)}`}
                                >
                                    {translateStatus(ticket.estado)}
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
                                <span>
                                    {t("ticketDetail.createdBy")}:{" "}
                                    {ticket.usuario_nombre}
                                </span>
                                <span>•</span>
                                <span>{formatDate(ticket.fecha_creacion)}</span>
                            </div>
                        </div>

                        <div className="ticket-section">
                            <h3>{t("ticketDetail.description")}</h3>
                            <div className="ticket-description">
                                {ticket.contenido}
                            </div>
                        </div>

                        {ticket.estado === "resuelto" &&
                            (ticket.solucion_texto ||
                                (ticket.solucion_imagenes &&
                                    ticket.solucion_imagenes.length > 0)) && (
                                <div className="ticket-section">
                                    <h3>
                                        {t("ticketDetail.resolutionDetails")}
                                    </h3>
                                    {ticket.solucion_texto && (
                                        <div className="ticket-description">
                                            {ticket.solucion_texto}
                                        </div>
                                    )}
                                    {ticket.solucion_imagenes &&
                                        ticket.solucion_imagenes.length > 0 && (
                                            <div className="solution-images-container">
                                                {ticket.solucion_imagenes.map(
                                                    (url, index) => (
                                                        <div
                                                            key={index}
                                                            className="solution-image-thumb"
                                                            onClick={() =>
                                                                setSelectedImageIndex(
                                                                    index,
                                                                )
                                                            }
                                                        >
                                                            <img
                                                                src={url}
                                                                alt={`Imagen de solución ${index + 1}`}
                                                                title={t(
                                                                    "ticketDetail.clickToEnlarge",
                                                                )}
                                                            />
                                                        </div>
                                                    ),
                                                )}
                                            </div>
                                        )}
                                </div>
                            )}

                        {isSuperuser() && (
                            <>
                                <div className="ticket-section">
                                    <h3>{t("ticketDetail.updatePriority")}</h3>
                                    <div className="status-buttons">
                                        <button
                                            className={`status-btn priority-btn ${ticket.prioridad === "baja" ? "active priority-low" : ""}`}
                                            onClick={() =>
                                                handlePriorityChange("baja")
                                            }
                                            disabled={
                                                updating ||
                                                ticket.prioridad === "baja"
                                            }
                                        >
                                            {t("priority.low")}
                                        </button>
                                        <button
                                            className={`status-btn priority-btn ${ticket.prioridad === "media" ? "active priority-medium" : ""}`}
                                            onClick={() =>
                                                handlePriorityChange("media")
                                            }
                                            disabled={
                                                updating ||
                                                ticket.prioridad === "media"
                                            }
                                        >
                                            {t("priority.medium")}
                                        </button>
                                        <button
                                            className={`status-btn priority-btn ${ticket.prioridad === "alta" ? "active priority-high" : ""}`}
                                            onClick={() =>
                                                handlePriorityChange("alta")
                                            }
                                            disabled={
                                                updating ||
                                                ticket.prioridad === "alta"
                                            }
                                        >
                                            {t("priority.high")}
                                        </button>
                                        <button
                                            className={`status-btn priority-btn ${ticket.prioridad === "urgente" ? "active priority-urgent" : ""}`}
                                            onClick={() =>
                                                handlePriorityChange("urgente")
                                            }
                                            disabled={
                                                updating ||
                                                ticket.prioridad === "urgente"
                                            }
                                        >
                                            {t("priority.urgent")}
                                        </button>
                                    </div>
                                </div>

                                <div className="ticket-section">
                                    <h3>{t("ticketDetail.updateStatus")}</h3>
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
                                            {t("status.open")}
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
                                            {t("status.inProgress")}
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
                                            {t("status.resolved")}
                                        </button>
                                    </div>
                                </div>
                            </>
                        )}
                    </div>

                    <div className="ticket-sidebar">
                        <div className="info-card">
                            <h3>{t("ticketDetail.information")}</h3>
                            <div className="info-item">
                                <span className="info-label">
                                    {t("ticket.department")}
                                </span>
                                <span className="info-value">
                                    {ticket.usuario_departamento_nombre}
                                </span>
                            </div>
                            {ticket.motivo_nombre && (
                                <div className="info-item">
                                    <span className="info-label">
                                        {t("ticket.reason")}
                                    </span>
                                    <span className="info-value">
                                        {ticket.motivo_nombre}
                                    </span>
                                </div>
                            )}
                            <div className="info-item">
                                <span className="info-label">
                                    {t("ticket.priority")}
                                </span>
                                <span className="info-value">
                                    {translatePriority(ticket.prioridad)}
                                </span>
                            </div>
                            <div className="info-item">
                                <span className="info-label">
                                    {t("ticket.status")}
                                </span>
                                <span className="info-value">
                                    {translateStatus(ticket.estado)}
                                </span>
                            </div>
                            <div className="info-item">
                                <span className="info-label">
                                    {t("ticketDetail.created")}
                                </span>
                                <span className="info-value">
                                    {formatDate(ticket.fecha_creacion)}
                                </span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {showResolutionModal && (
                <div className="modal-overlay">
                    <div className="modal-content">
                        <h3>{t("ticketDetail.resolutionModalTitle")}</h3>
                        <div className="modal-body">
                            <div className="form-group">
                                <label htmlFor="resolutionText">
                                    {t("ticketDetail.resolutionText")}
                                </label>
                                <textarea
                                    id="resolutionText"
                                    value={resolutionText}
                                    onChange={(e) =>
                                        setResolutionText(e.target.value)
                                    }
                                    placeholder={t(
                                        "ticketDetail.resolutionTextPlaceholder",
                                    )}
                                    rows="4"
                                />
                            </div>
                            <div className="form-group">
                                <label htmlFor="resolutionImages">
                                    {t("ticketDetail.resolutionImages")}
                                </label>
                                <input
                                    type="file"
                                    id="resolutionImages"
                                    multiple
                                    accept="image/*"
                                    onChange={handleImageUpload}
                                    disabled={uploadingImage}
                                />
                                {uploadingImage && (
                                    <p className="uploading-text">
                                        {t("ticketDetail.uploading")}
                                    </p>
                                )}
                                {resolutionImages.length > 0 && (
                                    <div className="image-preview">
                                        {resolutionImages.map(
                                            (imageObj, index) => (
                                                <div
                                                    key={index}
                                                    className="image-item"
                                                >
                                                    <div className="image-wrapper">
                                                        <img
                                                            src={imageObj.url}
                                                            alt={`Imagen ${index + 1}`}
                                                            onClick={() =>
                                                                setSelectedImageIndex(
                                                                    index,
                                                                )
                                                            }
                                                            style={{
                                                                cursor: "pointer",
                                                            }}
                                                            title={t(
                                                                "ticketDetail.clickToPreview",
                                                            )}
                                                        />
                                                        {imageObj.isLocal && (
                                                            <span className="uploading-badge">
                                                                {t(
                                                                    "ticketDetail.uploading",
                                                                )}
                                                            </span>
                                                        )}
                                                    </div>
                                                    <button
                                                        type="button"
                                                        onClick={() =>
                                                            removeImage(index)
                                                        }
                                                        className="remove-image-btn"
                                                        disabled={
                                                            imageObj.isLocal
                                                        }
                                                    >
                                                        ×
                                                    </button>
                                                </div>
                                            ),
                                        )}
                                    </div>
                                )}
                            </div>
                        </div>
                        <div className="modal-actions">
                            <button
                                onClick={() => setShowResolutionModal(false)}
                                className="btn-secondary"
                            >
                                {t("common.cancel")}
                            </button>
                            <button
                                onClick={handleResolutionSubmit}
                                className="btn-primary"
                                disabled={updating}
                            >
                                {updating
                                    ? t("common.saving")
                                    : t("common.save")}
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Galería modal para ver imágenes en grande */}
            {selectedImageIndex !== null && ticket?.solucion_imagenes && (
                <div
                    className="image-gallery-modal"
                    onClick={() => setSelectedImageIndex(null)}
                >
                    <div
                        className="gallery-content"
                        onClick={(e) => e.stopPropagation()}
                    >
                        <button
                            className="gallery-close-btn"
                            onClick={() => setSelectedImageIndex(null)}
                        >
                            ✕
                        </button>
                        <button
                            className="gallery-nav-btn gallery-prev"
                            onClick={() =>
                                setSelectedImageIndex(
                                    (selectedImageIndex -
                                        1 +
                                        ticket.solucion_imagenes.length) %
                                        ticket.solucion_imagenes.length,
                                )
                            }
                        >
                            ‹
                        </button>
                        <img
                            src={ticket.solucion_imagenes[selectedImageIndex]}
                            alt={`Imagen ${selectedImageIndex + 1}`}
                            className="gallery-image"
                        />
                        <button
                            className="gallery-nav-btn gallery-next"
                            onClick={() =>
                                setSelectedImageIndex(
                                    (selectedImageIndex + 1) %
                                        ticket.solucion_imagenes.length,
                                )
                            }
                        >
                            ›
                        </button>
                        <div className="gallery-counter">
                            {selectedImageIndex + 1} /{" "}
                            {ticket.solucion_imagenes.length}
                        </div>
                    </div>
                </div>
            )}

            {/* Galería modal para imágenes en el modal de resolución */}
            {selectedImageIndex !== null &&
                showResolutionModal &&
                resolutionImages.length > 0 && (
                    <div
                        className="image-gallery-modal"
                        onClick={() => setSelectedImageIndex(null)}
                    >
                        <div
                            className="gallery-content"
                            onClick={(e) => e.stopPropagation()}
                        >
                            <button
                                className="gallery-close-btn"
                                onClick={() => setSelectedImageIndex(null)}
                            >
                                ✕
                            </button>
                            <button
                                className="gallery-nav-btn gallery-prev"
                                onClick={() =>
                                    setSelectedImageIndex(
                                        (selectedImageIndex -
                                            1 +
                                            resolutionImages.length) %
                                            resolutionImages.length,
                                    )
                                }
                            >
                                ‹
                            </button>
                            <img
                                src={resolutionImages[selectedImageIndex].url}
                                alt={`Imagen ${selectedImageIndex + 1}`}
                                className="gallery-image"
                            />
                            <button
                                className="gallery-nav-btn gallery-next"
                                onClick={() =>
                                    setSelectedImageIndex(
                                        (selectedImageIndex + 1) %
                                            resolutionImages.length,
                                    )
                                }
                            >
                                ›
                            </button>
                            <div className="gallery-counter">
                                {selectedImageIndex + 1} /{" "}
                                {resolutionImages.length}
                            </div>
                        </div>
                    </div>
                )}
        </Layout>
    );
};

export default TicketDetail;
