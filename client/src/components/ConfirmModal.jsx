import { useLanguage } from "../hooks/useLanguage";
import "../styles/ConfirmModal.css";

const ConfirmModal = ({ isOpen, onClose, onConfirm, title, message }) => {
    const { t } = useLanguage();

    if (!isOpen) return null;

    return (
        <div
            className="modal-overlay"
            onClick={onClose}
            role="dialog"
            aria-modal="true"
            aria-labelledby="modal-title"
        >
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                <h3 id="modal-title" className="modal-title">
                    {title}
                </h3>
                <p className="modal-message">{message}</p>
                <div className="modal-actions">
                    <button
                        onClick={onClose}
                        className="btn-modal-cancel"
                        aria-label={t("form.cancel")}
                    >
                        {t("form.cancel")}
                    </button>
                    <button
                        onClick={onConfirm}
                        className="btn-modal-confirm"
                        aria-label={t("form.confirm")}
                    >
                        {t("form.confirm")}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default ConfirmModal;
