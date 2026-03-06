#!/usr/bin/env python3
"""
Script para configurar OAuth2 con Gmail.

Este script te guiará a través del proceso de configuración de OAuth2 para Gmail.

Pasos:
1. Ir a Google Cloud Console (https://console.cloud.google.com)
2. Crear un nuevo proyecto o seleccionar uno existente
3. Habilitar Gmail API
4. Crear credenciales OAuth 2.0
5. Descargar el archivo credentials.json
6. Ejecutar este script para generar el token de acceso
"""

import os
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from pathlib import Path

SCOPES = ['https://www.googleapis.com/auth/gmail.send']


def setup_oauth():
    """Configura OAuth2 para Gmail."""
    base_dir = Path(__file__).resolve().parent
    credentials_path = base_dir / 'credentials.json'
    token_path = base_dir / 'token.pickle'

    print("=" * 60)
    print("CONFIGURACIÓN DE OAUTH2 PARA GMAIL")
    print("=" * 60)
    print()

    if not credentials_path.exists():
        print("ERROR: No se encontró el archivo credentials.json")
        print()
        print("Por favor, sigue estos pasos:")
        print()
        print("1. Ve a Google Cloud Console:")
        print("   https://console.cloud.google.com")
        print()
        print("2. Crea un nuevo proyecto o selecciona uno existente")
        print()
        print("3. Habilita Gmail API:")
        print("   - En el menú, ve a 'APIs y servicios' > 'Biblioteca'")
        print("   - Busca 'Gmail API' y haz clic en 'Habilitar'")
        print()
        print("4. Crea credenciales OAuth 2.0:")
        print("   - Ve a 'APIs y servicios' > 'Credenciales'")
        print("   - Haz clic en '+ CREAR CREDENCIALES' > 'ID de cliente de OAuth'")
        print("   - Tipo de aplicación: 'Aplicación de escritorio'")
        print("   - Dale un nombre (ej: 'Sistema de Tickets')")
        print("   - Haz clic en 'Crear'")
        print()
        print("5. Descarga las credenciales:")
        print("   - Haz clic en el icono de descarga")
        print("   - Guarda el archivo como 'credentials.json'")
        print("   - Colócalo en la raíz del proyecto:")
        print(f"     {credentials_path}")
        print()
        return False

    print("✓ Archivo credentials.json encontrado")
    print()

    creds = None

    if token_path.exists():
        print("Se encontró un token existente. ¿Quieres regenerarlo? (s/n): ", end='')
        response = input().strip().lower()
        if response != 's':
            print("Configuración cancelada.")
            return False
        os.remove(token_path)

    print()
    print("Iniciando proceso de autorización...")
    print()
    print("IMPORTANTE:")
    print("- Se abrirá una ventana del navegador")
    print("- Inicia sesión con tu cuenta de Gmail")
    print("- Acepta los permisos solicitados")
    print("- Si aparece 'Esta app no está verificada', haz clic en 'Opciones avanzadas'")
    print("  y luego en 'Ir a [nombre del proyecto] (no seguro)'")
    print()

    try:
        flow = InstalledAppFlow.from_client_secrets_file(str(credentials_path), SCOPES)
        creds = flow.run_local_server(port=0)

        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)

        print()
        print("=" * 60)
        print("✓ CONFIGURACIÓN EXITOSA")
        print("=" * 60)
        print()
        print(f"Token de acceso guardado en: {token_path}")
        print()
        print("El sistema de emails ahora está configurado con OAuth2.")
        print("No necesitas configurar EMAIL_HOST_USER ni EMAIL_HOST_PASSWORD.")
        print()
        print("NOTA: El token se renovará automáticamente cuando expire.")
        print()
        return True

    except Exception as e:
        print()
        print("=" * 60)
        print("ERROR EN LA CONFIGURACIÓN")
        print("=" * 60)
        print()
        print(f"Error: {e}")
        print()
        return False


if __name__ == '__main__':
    success = setup_oauth()
    exit(0 if success else 1)
