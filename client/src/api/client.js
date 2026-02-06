const API_BASE_URL = '/api';

class ApiClient {
  constructor() {
    this.baseURL = API_BASE_URL;
    this.token = localStorage.getItem('authToken');
  }

  setToken(token) {
    this.token = token;
    if (token) {
      localStorage.setItem('authToken', token);
    } else {
      localStorage.removeItem('authToken');
    }
  }

  getToken() {
    return this.token || localStorage.getItem('authToken');
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
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

  async login(username, password) {
    const data = await this.request('/login/', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
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

  async updateTicketStatus(id, estado) {
    return this.request(`/tickets/${id}/update_estado/`, {
      method: 'POST',
      body: JSON.stringify({ estado }),
    });
  }

  async getDepartamentos() {
    return this.request('/departamentos/');
  }

  async getMotivos(departamentoId = null) {
    const query = departamentoId ? `?departamento=${departamentoId}` : '';
    return this.request(`/motivos/${query}`);
  }
}

export default new ApiClient();
