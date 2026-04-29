# Base image khafta w saria
FROM python:3.11-slim

# Set working directory gowa el container
WORKDIR /app

# Copy requirements w satab-ha
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy el code w el JSON file
COPY main.py .
COPY food_db.json .

# Efta7 port 8000
EXPOSE 8000

# Run el API
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]