import Toast from "./Toast";
import "../styles/ToastContainer.css";

const ToastContainer = ({ notifications, onRemove }) => {
    if (notifications.length === 0) return null;

    const getNotificationType = (notification) => {
        if (notification.type === "nuevo") return "success";
        if (notification.type === "estado") return "info";
        if (notification.type === "prioridad") return "warning";
        return "info";
    };

    return (
        <div className="toast-container">
            {notifications.map((notification) => (
                <Toast
                    key={notification.id}
                    message={notification.message}
                    type={getNotificationType(notification)}
                    onClose={() => onRemove(notification.id)}
                />
            ))}
        </div>
    );
};

export default ToastContainer;
