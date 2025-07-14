# Configuration Gunicorn pour le déploiement sur Render
import os

# Nombre de workers (processus)
workers = int(os.environ.get('GUNICORN_WORKERS', 2))

# Type de worker
worker_class = 'sync'

# Timeout pour les requêtes
timeout = 120

# Port d'écoute
bind = f"0.0.0.0:{os.environ.get('PORT', 5000)}"

# Logs
accesslog = '-'
errorlog = '-'
loglevel = 'info'

# Préchargement de l'application
preload_app = True

# Nombre maximum de requêtes par worker avant redémarrage
max_requests = 1000
max_requests_jitter = 50

# Configuration pour les fichiers statiques
static_folder = 'static' 