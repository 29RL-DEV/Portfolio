# Backend Dockerfile for production
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# system deps
RUN apt-get update && apt-get install -y build-essential libpq-dev gcc && rm -rf /var/lib/apt/lists/*

# install pipenv/requirements
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip setuptools
RUN pip install -r /app/requirements.txt

# copy project
COPY . /app

# collect static (will use environment vars in runtime)
RUN python manage.py collectstatic --noinput || true

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
