FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src /app/src
WORKDIR /app/src

EXPOSE 8000

# Usar el servidor de desarrollo de Django en desarrollo
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"] 