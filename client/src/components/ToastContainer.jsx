import Toast from './Toast';
import '../styles/ToastContainer.css';

const ToastContainer = ({ notifications, onRemove }) => {
  if (notifications.length === 0) return null;

  return (
    <div className="toast-container">
      {notifications.map((notification) => (
        <Toast
          key={notification.id}
          message={notification.message}
          type="info"
          onClose={() => onRemove(notification.id)}
        />
      ))}
    </div>
  );
};

export default ToastContainer;
