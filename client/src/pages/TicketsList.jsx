import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import apiClient from '../api/client';
import Layout from '../components/Layout';
import TicketCard from '../components/TicketCard';
import Loading from '../components/Loading';
import Alert from '../components/Alert';
import '../styles/TicketsList.css';

const TicketsList = () => {
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('all');
  const { isSuperuser } = useAuth();

  useEffect(() => {
    loadTickets();
  }, []);

  const loadTickets = async () => {
    try {
      setLoading(true);
      const data = await apiClient.getTickets();
      setTickets(data);
      setError(null);
    } catch (err) {
      setError('Error al cargar los tickets');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const filteredTickets = tickets.filter((ticket) => {
    if (filter === 'all') return true;
    return ticket.estado === filter;
  });

  const getTicketStats = () => {
    return {
      total: tickets.length,
      abierto: tickets.filter((t) => t.estado === 'abierto').length,
      en_proceso: tickets.filter((t) => t.estado === 'en_proceso').length,
      resuelto: tickets.filter((t) => t.estado === 'resuelto').length,
      cerrado: tickets.filter((t) => t.estado === 'cerrado').length,
    };
  };

  const stats = getTicketStats();

  if (loading) {
    return (
      <Layout>
        <Loading />
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="tickets-container">
        <div className="tickets-header">
          <div>
            <h1>Mis Tickets</h1>
            <p className="subtitle">
              {isSuperuser() ? 'Todos los tickets del sistema' : 'Tickets que has creado'}
            </p>
          </div>
          <Link to="/tickets/new" className="btn-create">
            + Nuevo Ticket
          </Link>
        </div>

        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-value">{stats.total}</div>
            <div className="stat-label">Total</div>
          </div>
          <div className="stat-card stat-open">
            <div className="stat-value">{stats.abierto}</div>
            <div className="stat-label">Abiertos</div>
          </div>
          <div className="stat-card stat-progress">
            <div className="stat-value">{stats.en_proceso}</div>
            <div className="stat-label">En Proceso</div>
          </div>
          <div className="stat-card stat-resolved">
            <div className="stat-value">{stats.resuelto}</div>
            <div className="stat-label">Resueltos</div>
          </div>
          <div className="stat-card stat-closed">
            <div className="stat-value">{stats.cerrado}</div>
            <div className="stat-label">Cerrados</div>
          </div>
        </div>

        <div className="filters">
          <button
            className={`filter-btn ${filter === 'all' ? 'active' : ''}`}
            onClick={() => setFilter('all')}
          >
            Todos
          </button>
          <button
            className={`filter-btn ${filter === 'abierto' ? 'active' : ''}`}
            onClick={() => setFilter('abierto')}
          >
            Abiertos
          </button>
          <button
            className={`filter-btn ${filter === 'en_proceso' ? 'active' : ''}`}
            onClick={() => setFilter('en_proceso')}
          >
            En Proceso
          </button>
          <button
            className={`filter-btn ${filter === 'resuelto' ? 'active' : ''}`}
            onClick={() => setFilter('resuelto')}
          >
            Resueltos
          </button>
          <button
            className={`filter-btn ${filter === 'cerrado' ? 'active' : ''}`}
            onClick={() => setFilter('cerrado')}
          >
            Cerrados
          </button>
        </div>

        {error && <Alert type="error" message={error} onClose={() => setError(null)} />}

        {filteredTickets.length === 0 ? (
          <div className="empty-state">
            <p>No hay tickets para mostrar</p>
            <Link to="/tickets/new" className="btn-create-empty">
              Crear primer ticket
            </Link>
          </div>
        ) : (
          <div className="tickets-grid">
            {filteredTickets.map((ticket) => (
              <TicketCard key={ticket.id} ticket={ticket} />
            ))}
          </div>
        )}
      </div>
    </Layout>
  );
};

export default TicketsList;
