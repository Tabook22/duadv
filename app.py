#!/usr/bin/env python3
"""
Dhofar University Student Management System
Main Application Entry Point
"""

from app import create_app
import os

import socket

app = create_app()

def find_available_port(preferred_port=5000, fallback_port=5001):
    env_port = os.getenv('PORT')
    if env_port:
        return int(env_port)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        if s.connect_ex(('127.0.0.1', preferred_port)) != 0:
            return preferred_port
    print(f"Port {preferred_port} is currently in use. Falling back to port {fallback_port}.")
    return fallback_port

if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    port = find_available_port()
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
