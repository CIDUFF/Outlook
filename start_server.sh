#!/bin/bash
# Script para iniciar o servidor Django PROSPECTA

cd /home/marcus/desenvolvimento/Outlook
source .venv/bin/activate

# Coletar arquivos estáticos
uv run manage.py collectstatic --noinput

# Executar migrações
uv run manage.py migrate --noinput

# Iniciar servidor
exec uv run manage.py runserver 0.0.0.0:8555
