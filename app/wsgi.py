"""
Ponto de entrada WSGI
Ponto de entrada principal para servidores WSGI como Gunicorn ou uWSGI.
"""
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

# Determina qual configuração usar
config_name = os.getenv("FLASK_ENV", "development")

# Cria aplicação Flask
from app import create_app
app = create_app(config_name)

# Cria aplicação Celery
from tasks.celery_app import make_celery
celery = make_celery(app)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.getenv("PORT", 5000)))