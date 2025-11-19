Dieses Projekt ist zum Simulieren einer aktiven Steuerung bei der Batterie bei dynamischen Strompreisen gegen eine statische Nutzung der Batterie Punkt und gegen die Berechnung / Nutzung bei den habe ich einen Strompreis und ohne aktive Steuerung.

## Deployment

Das Projekt verfügt über eine automatische Deployment-Pipeline, die bei jedem Push auf den `main` Branch ausgelöst wird. Die Pipeline führt folgende Schritte auf dem Remote-Server aus:

1. Repository-Code aktualisieren
2. Docker-Images mit `docker-compose build` erstellen
3. Container mit `docker-compose up -d` starten
4. Alte Docker-Images aufräumen

### Erforderliche GitHub Secrets

Für das automatische Deployment müssen folgende Secrets in den GitHub Repository Settings konfiguriert werden:

- `DEPLOY_HOST`: Hostname oder IP-Adresse des Remote-Servers
- `DEPLOY_USER`: SSH-Benutzername für den Remote-Server
- `DEPLOY_SSH_KEY`: SSH Private Key für die Authentifizierung
- `DEPLOY_PATH`: Pfad zum Projektverzeichnis auf dem Remote-Server
- `DEPLOY_PORT`: (Optional) SSH-Port, Standard ist 22

## Parameter

- Wir arbeiten auf Basis von Stundenwerten
- Es wird der Börsenstrom Plus statische Aufschläge plus Mehrwertsteuer verwendet als Zeitreihe auf der Stundenwerte
- Es gibt einen statischen Strompreis als Referenz
- Es wird ein Lastprofil mit Verbrauch in Wh pro Stunde vorgeschlagen


## Modell 1 - Linearer Verbrauch - statischer Preis

Im Modell 1 wird simuliert was an PV Leistung in die Batterie und in dein Haus Verbrauch gespeist wird und im späteren Verlauf bei Bedarf aus der Batterie herausgenommen wird.

## Modell 2 - Linearer Verbrauch - dynamischer Preis

Eine gegebene Reihe an dynamischen Strompreisen wird gegen einen linearen Verbrauch gehalten und damit wird simuliert wie eine ungesteuerte Batterie den persönlichen Strompreis beeinflusst. Am Ende der Zeitreihen soll ein nach Verbrauch gewichteter Preis herauskommen.

## Modell 3 - aktive Steuerung - dynamischer Preis

Hier wird die Batterie entlang das dynamischen Strompreises verwendet das bedeutet dass bei einem hohen Strompreis die Batterie entladen wird Komma bei einem niedrigen Strompreis wird unter Umständen erst das Netz verwendet und dann erst die Batterie. Gegebenenfalls wird sogar aus dem Netz nachgeladen.

