import { useEffect, useRef, useState } from 'react';
import { playNotificationSound } from '../utils/sounds';

export const useTicketNotifications = (tickets) => {
  const [notifications, setNotifications] = useState([]);
  const previousTicketsRef = useRef(null);
  const isFirstLoadRef = useRef(true);

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

    tickets.forEach(ticket => {
      const previousTicket = previousTicketsRef.current.find(t => t.id === ticket.id);

      if (previousTicket) {
        if (previousTicket.estado !== ticket.estado) {
          changes.push({
            id: `${ticket.id}-estado-${Date.now()}`,
            ticketId: ticket.id,
            type: 'estado',
            message: `Ticket #${ticket.id}: Estado cambiado a "${ticket.estado_display}"`,
            previousValue: previousTicket.estado_display,
            newValue: ticket.estado_display,
          });
        }

        if (previousTicket.prioridad !== ticket.prioridad) {
          changes.push({
            id: `${ticket.id}-prioridad-${Date.now()}`,
            ticketId: ticket.id,
            type: 'prioridad',
            message: `Ticket #${ticket.id}: Prioridad cambiada a "${ticket.prioridad_display}"`,
            previousValue: previousTicket.prioridad_display,
            newValue: ticket.prioridad_display,
          });
        }
      }
    });

    if (changes.length > 0) {
      playNotificationSound();
      setNotifications(prev => [...prev, ...changes]);
    }

    previousTicketsRef.current = tickets;
  }, [tickets]);

  const removeNotification = (notificationId) => {
    setNotifications(prev => prev.filter(n => n.id !== notificationId));
  };

  return { notifications, removeNotification };
};
