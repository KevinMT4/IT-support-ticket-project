import { createContext, useState, useContext, useEffect } from "react";
import apiClient from "../api/client";

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const token = localStorage.getItem("authToken");
        const userData = localStorage.getItem("userData");

        if (token && userData) {
            try {
                setUser(JSON.parse(userData));
            } catch (error) {
                localStorage.removeItem("userData");
            }
        }
        setLoading(false);
    }, []);

    const login = async (email, password) => {
        try {
            const data = await apiClient.login(email, password);
            setUser(data.user);
            localStorage.setItem("userData", JSON.stringify(data.user));
            return { success: true };
        } catch (error) {
            return { success: false, error: error.message };
        }
    };

    const register = async (userData) => {
        try {
            const data = await apiClient.register(userData);
            setUser(data.user);
            localStorage.setItem("userData", JSON.stringify(data.user));
            return { success: true };
        } catch (error) {
            return { success: false, error: error.message };
        }
    };

    const logout = async () => {
        await apiClient.logout();
        setUser(null);
        localStorage.removeItem("userData");
    };

    const isSuperuser = () => {
        return user?.rol === "superuser";
    };

    return (
        <AuthContext.Provider
            value={{ user, login, register, logout, loading, isSuperuser }}
        >
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error("useAuth must be used within an AuthProvider");
    }
    return context;
};
