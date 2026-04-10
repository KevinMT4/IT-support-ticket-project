import os
import MySQLdb
from MySQLdb import Error
from django.conf import settings


def create_database_if_not_exists():
    """
    Crea la base de datos MySQL automáticamente si no existe.
    Se ejecuta al iniciar la aplicación Django.
    """
    db_config = settings.DATABASES['default']

    db_name = db_config.get('NAME')
    db_user = db_config.get('USER')
    db_password = db_config.get('PASSWORD')
    db_host = db_config.get('HOST')
    db_port = int(db_config.get('PORT', 3306))

    try:
        connection = MySQLdb.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            passwd=db_password,
        )

        cursor = connection.cursor()

        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")

        connection.commit()
        print(f"Base de datos '{db_name}' lista.")

        cursor.close()
        connection.close()

    except Error as e:
        print(f"Error al crear la base de datos: {e}")
        raise
