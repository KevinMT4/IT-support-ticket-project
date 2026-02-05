import requests
from typing import Optional, Dict, List, Any
from config import API_BASE_URL


class APIClient:
    def __init__(self):
        self.base_url = API_BASE_URL
        self.token: Optional[str] = None
        self.user_data: Optional[Dict] = None

    def _get_headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Token {self.token}"
        return headers

    def login(self, username: str, password: str) -> tuple[bool, str]:
        try:
            response = requests.post(
                f"{self.base_url}/login/",
                json={"username": username, "password": password}
            )
            if response.status_code == 200:
                data = response.json()
                self.token = data["token"]
                self.user_data = data["user"]
                return True, "Login exitoso"
            else:
                error = response.json().get("error", "Error desconocido")
                return False, error
        except Exception as e:
            return False, f"Error de conexión: {str(e)}"

    def logout(self) -> bool:
        try:
            if self.token:
                requests.post(
                    f"{self.base_url}/logout/",
                    headers=self._get_headers()
                )
            self.token = None
            self.user_data = None
            return True
        except Exception:
            return False

    def get_tickets(self) -> tuple[bool, Any]:
        try:
            response = requests.get(
                f"{self.base_url}/tickets/",
                headers=self._get_headers()
            )
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, "Error al obtener tickets"
        except Exception as e:
            return False, f"Error de conexión: {str(e)}"

    def get_ticket(self, ticket_id: int) -> tuple[bool, Any]:
        try:
            response = requests.get(
                f"{self.base_url}/tickets/{ticket_id}/",
                headers=self._get_headers()
            )
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, "Error al obtener ticket"
        except Exception as e:
            return False, f"Error de conexión: {str(e)}"

    def create_ticket(self, data: Dict) -> tuple[bool, Any]:
        try:
            response = requests.post(
                f"{self.base_url}/tickets/",
                json=data,
                headers=self._get_headers()
            )
            if response.status_code == 201:
                return True, response.json()
            else:
                error = response.json() if response.content else "Error desconocido"
                return False, error
        except Exception as e:
            return False, f"Error de conexión: {str(e)}"

    def update_ticket_estado(self, ticket_id: int, estado: str) -> tuple[bool, Any]:
        try:
            response = requests.post(
                f"{self.base_url}/tickets/{ticket_id}/update_estado/",
                json={"estado": estado},
                headers=self._get_headers()
            )
            if response.status_code == 200:
                return True, response.json()
            else:
                error = response.json().get("error", "Error desconocido")
                return False, error
        except Exception as e:
            return False, f"Error de conexión: {str(e)}"

    def get_departamentos(self) -> tuple[bool, Any]:
        try:
            response = requests.get(
                f"{self.base_url}/departamentos/",
                headers=self._get_headers()
            )
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, "Error al obtener departamentos"
        except Exception as e:
            return False, f"Error de conexión: {str(e)}"

    def get_motivos(self, departamento_id: Optional[int] = None) -> tuple[bool, Any]:
        try:
            url = f"{self.base_url}/motivos/"
            if departamento_id:
                url += f"?departamento={departamento_id}"

            response = requests.get(url, headers=self._get_headers())
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, "Error al obtener motivos"
        except Exception as e:
            return False, f"Error de conexión: {str(e)}"

    def is_authenticated(self) -> bool:
        return self.token is not None

    def is_superuser(self) -> bool:
        return self.user_data and self.user_data.get("rol") == "superuser"
