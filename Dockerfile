# Verwende Python 3.11 als Basis-Image
FROM python:3.11-slim

# Setze Arbeitsverzeichnis
WORKDIR /app

# Installiere System-Abhängigkeiten für PuLP (CBC Solver) und Build-Tools
# gcc/g++ als Fallback falls keine Binary-Wheels verfügbar sind
RUN apt-get update && apt-get install -y \
    coinor-cbc \
    gcc \
    g++ \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Kopiere requirements.txt (falls vorhanden) oder erstelle eine
COPY requirements.txt* ./

# Installiere Python-Abhängigkeiten (only binary wheels, no compilation)
RUN pip install --no-cache-dir --only-binary=:all: \
    flask==3.0.0 \
    pulp==2.7.0 \
    numpy==1.26.4 \
    pytz==2024.1 \
    cachetools==5.3.2 \
    requests==2.31.0

# Lade das batcontrol wheel-file von GitHub herunter und installiere es
RUN wget https://github.com/muexxl/batcontrol/releases/download/0.5.5/batcontrol-0.5.5-py3-none-any.whl \
    && pip install --no-cache-dir batcontrol-0.5.5-py3-none-any.whl \
    && rm batcontrol-0.5.5-py3-none-any.whl

# Kopiere Anwendungsdateien
COPY . .

# Exponiere Port 5000 für Flask
EXPOSE 5000

# Setze Umgebungsvariablen für Flask
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Starte die Flask-Anwendung
CMD ["python", "app.py"]
