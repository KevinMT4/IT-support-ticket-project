import '../styles/ConfirmModal.css';

const ConfirmModal = ({ isOpen, onClose, onConfirm, title, message }) => {
  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <h3 className="modal-title">{title}</h3>
        <p className="modal-message">{message}</p>
        <div className="modal-actions">
          <button onClick={onClose} className="btn-modal-cancel">
            Cancelar
          </button>
          <button onClick={onConfirm} className="btn-modal-confirm">
            Confirmar
          </button>
        </div>
      </div>
    </div>
  );
};

export default ConfirmModal;
