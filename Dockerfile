FROM python:3.11-slim
# Build arguments
ARG GPT_API_KEY
ENV GPT_API_KEY=${GPT_API_KEY}
# Variables d'environnement
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app
ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app
# Installer Node.js 18 + dépendances système
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    g++ \
    make \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
# Vérifier les installations
RUN python --version && node --version && npm --version
# Installer les dépendances Python
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r backend/requirements.txt
# Installer les dépendances frontend
COPY frontend/package*.json ./frontend/
RUN cd frontend && npm install
# Copier le code source
COPY backend/ ./backend/
COPY frontend/ ./frontend/
# Créer les dossiers nécessaires
RUN mkdir -p /app/data /app/logs
# Copier et configurer le script de démarrage
COPY start.sh ./
RUN chmod +x start.sh
# Exposer les ports
EXPOSE 8000 3000
CMD ["./start.sh"]