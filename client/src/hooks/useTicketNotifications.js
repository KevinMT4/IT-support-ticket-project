import { useEffect, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { playNotificationSound } from '../utils/sounds';

const STORAGE_KEY = 'ticket_last_known_state';

const getStoredState = () => {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      return JSON.parse(stored);
    }
  } catch (e) {
    console.error('Error loading notification state:', e);
  }
  return { ticketStates: {}, lastUpdate: Date.now() };
};

const saveStoredState = (state) => {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  } catch (e) {
    console.error('Error saving notification state:', e);
  }
};

export const useTicketNotifications = (tickets, isSuperuser = false) => {
  const { t } = useTranslation();
  const [notifications, setNotifications] = useState([]);
  const previousTicketsRef = useRef(null);
  const isFirstLoadRef = useRef(true);
  const knownStateRef = useRef(getStoredState());

  useEffect(() => {
    const state = knownStateRef.current;
    const now = Date.now();
    const oneHour = 60 * 60 * 1000;

    if (now - state.lastUpdate > oneHour) {
      knownStateRef.current = { ticketStates: {}, lastUpdate: now };
      saveStoredState(knownStateRef.current);
    }
  }, []);

  useEffect(() => {
    if (isFirstLoadRef.current) {
      previousTicketsRef.current = tickets;
      isFirstLoadRef.current = false;

      tickets.forEach(ticket => {
        const ticketKey = `ticket-${ticket.id}`;
        if (!knownStateRef.current.ticketStates[ticketKey]) {
          knownStateRef.current.ticketStates[ticketKey] = {
            estado: ticket.estado,
            prioridad: ticket.prioridad,
            created: true,
          };
        }
      });
      saveStoredState(knownStateRef.current);
      return;
    }

    if (!previousTicketsRef.current || tickets.length === 0) {
      previousTicketsRef.current = tickets;
      return;
    }

    const changes = [];
    const ticketStates = knownStateRef.current.ticketStates;

    tickets.forEach(ticket => {
      const previousTicket = previousTicketsRef.current.find(t => t.id === ticket.id);
      const ticketKey = `ticket-${ticket.id}`;

      if (!previousTicket) {
        if (isSuperuser && !ticketStates[ticketKey]) {
          changes.push({
            id: `${ticket.id}-nuevo-${Date.now()}`,
            ticketId: ticket.id,
            type: 'nuevo',
            message: `${t('notifications.newTicket')}. ${ticket.usuario_nombre}: "${ticket.asunto}"`,
            newValue: ticket.asunto,
          });
          ticketStates[ticketKey] = {
            estado: ticket.estado,
            prioridad: ticket.prioridad,
            created: true,
          };
        }
      } else {
        if (!ticketStates[ticketKey]) {
          ticketStates[ticketKey] = {
            estado: previousTicket.estado,
            prioridad: previousTicket.prioridad,
          };
        }

        if (previousTicket.estado !== ticket.estado) {
          const statusTranslations = {
            'abierto': t('status.open'),
            'en_proceso': t('status.inProgress'),
            'resuelto': t('status.resolved')
          };
          const translatedStatus = statusTranslations[ticket.estado] || ticket.estado_display;

          changes.push({
            id: `${ticket.id}-estado-${Date.now()}-${Math.random()}`,
            ticketId: ticket.id,
            type: 'estado',
            message: `${t('notifications.ticket')} "${ticket.asunto}": ${t('notifications.statusChangedTo')} "${translatedStatus}"`,
            previousValue: previousTicket.estado_display,
            newValue: ticket.estado_display,
          });
          ticketStates[ticketKey].estado = ticket.estado;
        }

        if (previousTicket.prioridad !== ticket.prioridad) {
          const priorityTranslations = {
            'baja': t('priority.low'),
            'media': t('priority.medium'),
            'alta': t('priority.high'),
            'urgente': t('priority.urgent')
          };
          const translatedPriority = priorityTranslations[ticket.prioridad] || ticket.prioridad_display;

          changes.push({
            id: `${ticket.id}-prioridad-${Date.now()}-${Math.random()}`,
            ticketId: ticket.id,
            type: 'prioridad',
            message: `${t('notifications.ticket')} "${ticket.asunto}": ${t('notifications.priorityChangedTo')} "${translatedPriority}"`,
            previousValue: previousTicket.prioridad_display,
            newValue: ticket.prioridad_display,
          });
          ticketStates[ticketKey].prioridad = ticket.prioridad;
        }
      }
    });

    if (changes.length > 0) {
      playNotificationSound();
      setNotifications(prev => [...prev, ...changes]);
      knownStateRef.current.lastUpdate = Date.now();
      saveStoredState(knownStateRef.current);
    }

    previousTicketsRef.current = tickets;
  }, [tickets, isSuperuser, t]);

  const removeNotification = (notificationId) => {
    setNotifications(prev => prev.filter(n => n.id !== notificationId));
  };

  return { notifications, removeNotification };
};
