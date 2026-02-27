const API_BASE_URL = import.meta.env.VITE_API_PROXY_PATH || '/api';

class ApiClient {
  constructor() {
    this.baseURL = API_BASE_URL;
    this.token = localStorage.getItem('authToken');
    // store the preferred language for API requests; default to spanish
    this.language = localStorage.getItem('language') || 'es';
  }

  setToken(token) {
    this.token = token;
    if (token) {
      localStorage.setItem('authToken', token);
    } else {
      localStorage.removeItem('authToken');
    }
  }

  setLanguage(lang) {
    this.language = lang;
    localStorage.setItem('language', lang);
  }

  getLanguage() {
    return this.language;
  }

  getToken() {
    return this.token || localStorage.getItem('authToken');
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      'Accept-Language': this.language || 'es',
      ...options.headers,
    };

    const token = this.getToken();
    if (token) {
      headers['Authorization'] = `Token ${token}`;
    }

    const config = {
      ...options,
      headers,
    };

    try {
      const response = await fetch(url, config);

      if (!response.ok) {
        const error = await response.json().catch(() => ({ error: 'Error en la petición' }));
        throw new Error(error.error || `Error ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      throw error;
    }
  }

  async login(email, password) {
    const data = await this.request('/login/', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });

    this.setToken(data.token);
    return data;
  }

  async register(userData) {
    const data = await this.request('/registro/', {
      method: 'POST',
      body: JSON.stringify(userData),
    });

    this.setToken(data.token);
    return data;
  }

  async logout() {
    try {
      await this.request('/logout/', { method: 'POST' });
    } finally {
      this.setToken(null);
    }
  }

  async getTickets() {
    return this.request('/tickets/');
  }

  async getTicket(id) {
    return this.request(`/tickets/${id}/`);
  }

  async createTicket(ticketData) {
    return this.request('/tickets/', {
      method: 'POST',
      body: JSON.stringify(ticketData),
    });
  }

  async updateTicketStatus(id, estado, extraData = {}) {
    return this.request(`/tickets/${id}/update_estado/`, {
      method: 'POST',
      body: JSON.stringify({ estado, ...extraData }),
    });
  }

  async updateTicketPriority(id, prioridad) {
    return this.request(`/tickets/${id}/update_prioridad/`, {
      method: 'POST',
      body: JSON.stringify({ prioridad }),
    });
  }

  async getDepartamentos() {
    return this.request('/departamentos/');
  }

  async getMotivos(departamentoId = null) {
    const query = departamentoId ? `?departamento=${departamentoId}` : '';
    return this.request(`/motivos/${query}`);
  }

  async uploadImage(formData) {
    const url = `${this.baseURL}/upload-image/`;
    const headers = {};

    const token = this.getToken();
    if (token) {
      headers['Authorization'] = `Token ${token}`;
    }

    const config = {
      method: 'POST',
      headers,
      body: formData,
    };

    try {
      const response = await fetch(url, config);

      if (!response.ok) {
        const error = await response.json().catch(() => ({ error: 'Error en la petición' }));
        throw new Error(error.error || `Error ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      throw error;
    }
  }
}

export default new ApiClient();
