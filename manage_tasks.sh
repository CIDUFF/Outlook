#!/bin/bash
# Script para configurar e gerenciar o worker de tarefas do PROSPECTA

SERVICE_NAME="prospecta-tasks"
SERVICE_FILE="/home/marcus/desenvolvimento/Outlook/prospecta-tasks.service"
SYSTEMD_PATH="/etc/systemd/system/${SERVICE_NAME}.service"

case "$1" in
    install)
        echo "Instalando serviço ${SERVICE_NAME}..."
        sudo cp "$SERVICE_FILE" "$SYSTEMD_PATH"
        sudo systemctl daemon-reload
        sudo systemctl enable "$SERVICE_NAME"
        echo "Serviço instalado! Use: ./manage_tasks.sh start"
        ;;
    start)
        echo "Iniciando ${SERVICE_NAME}..."
        sudo systemctl start "$SERVICE_NAME"
        sudo systemctl status "$SERVICE_NAME"
        ;;
    stop)
        echo "Parando ${SERVICE_NAME}..."
        sudo systemctl stop "$SERVICE_NAME"
        ;;
    restart)
        echo "Reiniciando ${SERVICE_NAME}..."
        sudo systemctl restart "$SERVICE_NAME"
        sudo systemctl status "$SERVICE_NAME"
        ;;
    status)
        sudo systemctl status "$SERVICE_NAME"
        ;;
    logs)
        echo "=== Últimas 50 linhas do log ==="
        tail -50 /home/marcus/desenvolvimento/Outlook/logs/background_tasks.log
        ;;
    errors)
        echo "=== Últimos erros ==="
        tail -50 /home/marcus/desenvolvimento/Outlook/logs/background_tasks_error.log
        ;;
    uninstall)
        echo "Removendo serviço ${SERVICE_NAME}..."
        sudo systemctl stop "$SERVICE_NAME"
        sudo systemctl disable "$SERVICE_NAME"
        sudo rm -f "$SYSTEMD_PATH"
        sudo systemctl daemon-reload
        echo "Serviço removido!"
        ;;
    run-now)
        echo "Executando worker manualmente (Ctrl+C para parar)..."
        cd /home/marcus/desenvolvimento/Outlook
        uv run manage.py process_tasks
        ;;
    *)
        echo "Uso: $0 {install|start|stop|restart|status|logs|errors|uninstall|run-now}"
        echo ""
        echo "Comandos:"
        echo "  install   - Instala o serviço systemd"
        echo "  start     - Inicia o worker"
        echo "  stop      - Para o worker"
        echo "  restart   - Reinicia o worker"
        echo "  status    - Mostra status do serviço"
        echo "  logs      - Mostra últimas linhas do log"
        echo "  errors    - Mostra últimos erros"
        echo "  uninstall - Remove o serviço"
        echo "  run-now   - Executa manualmente (desenvolvimento)"
        exit 1
        ;;
esac
