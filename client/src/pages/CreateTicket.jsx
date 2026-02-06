import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import apiClient from '../api/client';
import Layout from '../components/Layout';
import Loading from '../components/Loading';
import '../styles/CreateTicket.css';

const CreateTicket = () => {
  const [formData, setFormData] = useState({
    departamento: '',
    motivo: '',
    asunto: '',
    contenido: '',
    prioridad: 'media',
  });
  const [departamentos, setDepartamentos] = useState([]);
  const [motivos, setMotivos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    loadDepartamentos();
  }, []);

  useEffect(() => {
    if (formData.departamento) {
      loadMotivos(formData.departamento);
    } else {
      setMotivos([]);
      setFormData((prev) => ({ ...prev, motivo: '' }));
    }
  }, [formData.departamento]);

  const loadDepartamentos = async () => {
    try {
      const data = await apiClient.getDepartamentos();
      setDepartamentos(data);
      setLoading(false);
    } catch (err) {
      setError('Error al cargar departamentos');
      setLoading(false);
    }
  };

  const loadMotivos = async (departamentoId) => {
    try {
      const data = await apiClient.getMotivos(departamentoId);
      setMotivos(data);
    } catch (err) {
      console.error('Error al cargar motivos:', err);
      setMotivos([]);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    if (!formData.departamento || !formData.asunto || !formData.contenido) {
      setError('Por favor completa todos los campos requeridos');
      return;
    }

    setSubmitting(true);

    try {
      const ticketData = {
        departamento: parseInt(formData.departamento),
        motivo: formData.motivo ? parseInt(formData.motivo) : null,
        asunto: formData.asunto,
        contenido: formData.contenido,
        prioridad: formData.prioridad,
      };

      const newTicket = await apiClient.createTicket(ticketData);
      navigate(`/tickets/${newTicket.id}`);
    } catch (err) {
      setError(err.message || 'Error al crear el ticket');
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <Layout>
        <Loading />
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="create-ticket-container">
        <div className="create-ticket-header">
          <h1>Crear Nuevo Ticket</h1>
          <p className="subtitle">Completa el formulario para crear un nuevo ticket de soporte</p>
        </div>

        <form onSubmit={handleSubmit} className="ticket-form">
          {error && <div className="error-message">{error}</div>}

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="departamento">
                Departamento <span className="required">*</span>
              </label>
              <select
                id="departamento"
                name="departamento"
                value={formData.departamento}
                onChange={handleChange}
                required
                disabled={submitting}
              >
                <option value="">Selecciona un departamento</option>
                {departamentos.map((dept) => (
                  <option key={dept.id} value={dept.id}>
                    {dept.nombre}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="motivo">Motivo</label>
              <select
                id="motivo"
                name="motivo"
                value={formData.motivo}
                onChange={handleChange}
                disabled={!formData.departamento || submitting}
              >
                <option value="">Selecciona un motivo</option>
                {motivos.map((motivo) => (
                  <option key={motivo.id} value={motivo.id}>
                    {motivo.nombre}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="prioridad">
              Prioridad <span className="required">*</span>
            </label>
            <select
              id="prioridad"
              name="prioridad"
              value={formData.prioridad}
              onChange={handleChange}
              required
              disabled={submitting}
            >
              <option value="baja">Baja</option>
              <option value="media">Media</option>
              <option value="alta">Alta</option>
              <option value="urgente">Urgente</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="asunto">
              Asunto <span className="required">*</span>
            </label>
            <input
              type="text"
              id="asunto"
              name="asunto"
              value={formData.asunto}
              onChange={handleChange}
              placeholder="Describe brevemente el problema"
              required
              disabled={submitting}
            />
          </div>

          <div className="form-group">
            <label htmlFor="contenido">
              Descripción <span className="required">*</span>
            </label>
            <textarea
              id="contenido"
              name="contenido"
              value={formData.contenido}
              onChange={handleChange}
              placeholder="Describe detalladamente el problema o solicitud"
              rows={8}
              required
              disabled={submitting}
            />
          </div>

          <div className="form-actions">
            <button
              type="button"
              className="btn-cancel"
              onClick={() => navigate('/tickets')}
              disabled={submitting}
            >
              Cancelar
            </button>
            <button type="submit" className="btn-submit" disabled={submitting}>
              {submitting ? 'Creando...' : 'Crear Ticket'}
            </button>
          </div>
        </form>
      </div>
    </Layout>
  );
};

export default CreateTicket;
