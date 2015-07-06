Cool idée surtout pour 2.:
Je suis à A je dois aller à B à telle heure (dep ou arrivée).
1. Propose moi tous les trajets en comptant le velib (dispo quelle statio etc.).
2. Tient moi à jour si la station que tu m'a donnée est vide/remplie (donner meilleure solution).

# on raspberry:
  - sending SMS to the request server using server http
  - automatic configuration (no hard coded links in config_gammu.txt)
  - when receiving a GET request, sends a SMS

# on the other server:
  - tests.py : write some tests for existing backends
  - complete all backends
  - automatically run handleSMS.py when receiving a GET request
