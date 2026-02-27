import { useEffect, useRef, useCallback } from "react";

const getEnvMinutes = (name, defaultMinutes) => {
    const raw = import.meta.env[name];
    const n = Number(raw);
    if (Number.isFinite(n) && n > 0) return n;
    return defaultMinutes;
};

const INACTIVITY_TIMEOUT = getEnvMinutes('VITE_INACTIVITY_TIMEOUT_MINUTES', 40) * 60 * 1000;
const WARNING_TIME = getEnvMinutes('VITE_WARNING_TIME_MINUTES', 2) * 60 * 1000;

export const useSessionTimeout = (onTimeout, onWarning) => {
    const timeoutIdRef = useRef(null);
    const warningIdRef = useRef(null);
    const lastActivityRef = useRef(Date.now());

    const clearTimers = useCallback(() => {
        if (timeoutIdRef.current) {
            clearTimeout(timeoutIdRef.current);
            timeoutIdRef.current = null;
        }
        if (warningIdRef.current) {
            clearTimeout(warningIdRef.current);
            warningIdRef.current = null;
        }
    }, []);

    const resetTimer = useCallback(() => {
        clearTimers();
        lastActivityRef.current = Date.now();

        if (onWarning) {
            warningIdRef.current = setTimeout(() => {
                onWarning();
            }, INACTIVITY_TIMEOUT - WARNING_TIME);
        }

        timeoutIdRef.current = setTimeout(() => {
            onTimeout();
        }, INACTIVITY_TIMEOUT);
    }, [clearTimers, onTimeout, onWarning]);

    const handleActivity = useCallback(() => {
        const now = Date.now();
        const timeSinceLastActivity = now - lastActivityRef.current;

        if (timeSinceLastActivity > 1000) {
            resetTimer();
        }
    }, [resetTimer]);

    useEffect(() => {
        const events = [
            "mousedown",
            "mousemove",
            "keypress",
            "scroll",
            "touchstart",
            "click",
        ];

        resetTimer();

        events.forEach((event) => {
            document.addEventListener(event, handleActivity, { passive: true });
        });

        return () => {
            clearTimers();
            events.forEach((event) => {
                document.removeEventListener(event, handleActivity);
            });
        };
    }, [handleActivity, resetTimer, clearTimers]);

    return { resetTimer, clearTimers };
};
