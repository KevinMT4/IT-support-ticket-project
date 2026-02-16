import { useEffect, useRef, useState } from 'react';
import { playNotificationSound } from '../utils/sounds';

const STORAGE_KEY = 'ticket_notifications_state';

const getStoredState = () => {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      return JSON.parse(stored);
    }
  } catch (e) {
    console.error('Error loading notification state:', e);
  }
  return { notifiedTickets: {}, lastUpdate: Date.now() };
};

const saveStoredState = (state) => {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  } catch (e) {
    console.error('Error saving notification state:', e);
  }
};

export const useTicketNotifications = (tickets, isSuperuser = false) => {
  const [notifications, setNotifications] = useState([]);
  const previousTicketsRef = useRef(null);
  const isFirstLoadRef = useRef(true);
  const notifiedStateRef = useRef(getStoredState());

  useEffect(() => {
    const state = notifiedStateRef.current;
    const now = Date.now();
    const oneHour = 60 * 60 * 1000;

    if (now - state.lastUpdate > oneHour) {
      notifiedStateRef.current = { notifiedTickets: {}, lastUpdate: now };
      saveStoredState(notifiedStateRef.current);
    }
  }, []);

  useEffect(() => {
    if (isFirstLoadRef.current) {
      previousTicketsRef.current = tickets;
      isFirstLoadRef.current = false;
      return;
    }

    if (!previousTicketsRef.current || tickets.length === 0) {
      previousTicketsRef.current = tickets;
      return;
    }

    const changes = [];
    const notifiedState = notifiedStateRef.current.notifiedTickets;

    tickets.forEach(ticket => {
      const previousTicket = previousTicketsRef.current.find(t => t.id === ticket.id);
      const ticketKey = `ticket-${ticket.id}`;

      if (!previousTicket) {
        if (isSuperuser && !notifiedState[ticketKey]) {
          changes.push({
            id: `${ticket.id}-nuevo-${Date.now()}`,
            ticketId: ticket.id,
            type: 'nuevo',
            message: `Nuevo ticket. ${ticket.usuario_nombre}: "${ticket.asunto}"`,
            newValue: ticket.asunto,
          });
          notifiedState[ticketKey] = {
            created: true,
            estado: ticket.estado,
            prioridad: ticket.prioridad,
          };
        }
      } else {
        const ticketState = notifiedState[ticketKey] || {
          estado: previousTicket.estado,
          prioridad: previousTicket.prioridad,
        };

        if (previousTicket.estado !== ticket.estado) {
          const stateChangeKey = `${ticketKey}-estado-${ticket.estado}`;
          if (!notifiedState[stateChangeKey]) {
            changes.push({
              id: `${ticket.id}-estado-${Date.now()}`,
              ticketId: ticket.id,
              type: 'estado',
              message: `Ticket "${ticket.asunto}" Estado cambiado a "${ticket.estado_display}"`,
              previousValue: previousTicket.estado_display,
              newValue: ticket.estado_display,
            });
            notifiedState[stateChangeKey] = true;
            ticketState.estado = ticket.estado;
          }
        }

        if (previousTicket.prioridad !== ticket.prioridad) {
          const priorityChangeKey = `${ticketKey}-prioridad-${ticket.prioridad}`;
          if (!notifiedState[priorityChangeKey]) {
            changes.push({
              id: `${ticket.id}-prioridad-${Date.now()}`,
              ticketId: ticket.id,
              type: 'prioridad',
              message: `Ticket "${ticket.asunto}": Prioridad cambiada a "${ticket.prioridad_display}"`,
              previousValue: previousTicket.prioridad_display,
              newValue: ticket.prioridad_display,
            });
            notifiedState[priorityChangeKey] = true;
            ticketState.prioridad = ticket.prioridad;
          }
        }

        notifiedState[ticketKey] = ticketState;
      }
    });

    if (changes.length > 0) {
      playNotificationSound();
      setNotifications(prev => [...prev, ...changes]);
      notifiedStateRef.current.lastUpdate = Date.now();
      saveStoredState(notifiedStateRef.current);
    }

    previousTicketsRef.current = tickets;
  }, [tickets, isSuperuser]);

  const removeNotification = (notificationId) => {
    setNotifications(prev => prev.filter(n => n.id !== notificationId));
  };

  return { notifications, removeNotification };
};
