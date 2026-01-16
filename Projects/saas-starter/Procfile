web: cd backend && gunicorn config.wsgi:application --workers 3 --worker-class sync --timeout 60 --bind 0.0.0.0:8000
release: cd backend && python manage.py migrate
