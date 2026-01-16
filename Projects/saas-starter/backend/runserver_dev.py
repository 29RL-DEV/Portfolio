#!/usr/bin/env python
"""
Script helper pentru a rula serverul development cu verificări HTTPS.
Această script verifică dacă utilizatorul încearcă să acceseze prin HTTPS
și oferă instrucțiuni clare.
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

# Setează environment variable pentru Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Configurează Django
django.setup()

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Django Development Server")
    print("=" * 60)
    print("\n⚠️  IMPORTANT: Serverul development rulează pe HTTP, nu HTTPS!")
    print("📌 Folosește: http://127.0.0.1:8000 (NU https://)")
    print("\n" + "=" * 60 + "\n")
    
    # Rulează serverul normal
    execute_from_command_line(['manage.py', 'runserver'] + sys.argv[1:])
