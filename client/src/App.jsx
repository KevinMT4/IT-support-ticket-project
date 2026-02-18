import {
    BrowserRouter as Router,
    Routes,
    Route,
    Navigate,
} from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";
import SessionTimeoutHandler from "./components/SessionTimeoutHandler";
import Login from "./pages/Login";
import TicketsList from "./pages/TicketsList";
import CreateTicket from "./pages/CreateTicket";
import TicketDetail from "./pages/TicketDetail";

function App() {
    return (
        <Router>
            <AuthProvider>
                <SessionTimeoutHandler />
                <Routes>
                    <Route path="/login" element={<Login />} />
                    <Route path="/registro" element={<Login />} />
                    <Route
                        path="/tickets"
                        element={
                            <ProtectedRoute>
                                <TicketsList />
                            </ProtectedRoute>
                        }
                    />
                    <Route
                        path="/tickets/new"
                        element={
                            <ProtectedRoute>
                                <CreateTicket />
                            </ProtectedRoute>
                        }
                    />
                    <Route
                        path="/tickets/:id"
                        element={
                            <ProtectedRoute>
                                <TicketDetail />
                            </ProtectedRoute>
                        }
                    />
                    <Route
                        path="/"
                        element={<Navigate to="/tickets" replace />}
                    />
                </Routes>
            </AuthProvider>
        </Router>
    );
}

export default App;
