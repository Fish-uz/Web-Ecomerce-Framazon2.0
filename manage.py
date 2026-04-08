#!/usr/bin/env python
"""
Utilidad de línea de comandos de Django para tareas administrativas.
Este archivo es el puente entre la terminal y el código de tu marketplace.
"""
import os   # Módulo para interactuar con el sistema operativo.
import sys  # Módulo para manejar argumentos de la terminal (como 'runserver').


def main():
    """Ejecuta las tareas administrativas del framework."""
    
    # 1. CONFIGURACIÓN DEL ENTORNO:
    # Le dice a Django dónde encontrar el archivo de configuración (settings.py).
    # En este caso, apunta a 'core.settings'.
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    
    try:
        # 2. IMPORTACIÓN DEL NÚCLEO:
        # Intenta cargar la función que procesa los comandos de Django.
        from django.core.management import execute_from_command_line
        
    except ImportError as exc:
        # 3. MANEJO DE ERRORES:
        # Si Django no está instalado o el entorno virtual no está activo,
        # lanza un error amigable explicando qué pudo fallar.
        raise ImportError(
            "No se pudo importar Django. ¿Estás seguro de que está instalado y "
            "disponible en tu variable de entorno PYTHONPATH? ¿Olvidaste "
            "activar el entorno virtual?"
        ) from exc
    
    # 4. EJECUCIÓN:
    # Toma lo que escribiste en la terminal (ej: 'runserver' o 'migrate')
    # y lo ejecuta dentro del contexto de tu proyecto.
    execute_from_command_line(sys.argv)


# PUNTO DE ENTRADA:
# Asegura que el script solo se ejecute si se llama directamente (no si se importa).
if __name__ == '__main__':
    main()