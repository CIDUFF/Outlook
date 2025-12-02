#!/bin/bash
# Script para gerenciar os serviços do PROSPECTA em produção

PROJECT_DIR="/home/marcus/desenvolvimento/Outlook"
WEB_SERVICE="prospecta-web"
TASKS_SERVICE="prospecta-tasks"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[OK]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERRO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[AVISO]${NC} $1"
}

case "$1" in
    install)
        echo "Instalando serviços PROSPECTA..."
        sudo cp "$PROJECT_DIR/prospecta-web.service" "/etc/systemd/system/"
        sudo cp "$PROJECT_DIR/prospecta-tasks.service" "/etc/systemd/system/"
        sudo systemctl daemon-reload
        sudo systemctl enable "$WEB_SERVICE"
        sudo systemctl enable "$TASKS_SERVICE"
        print_status "Serviços instalados! Use: ./prospecta.sh start"
        ;;
    start)
        echo "Iniciando PROSPECTA..."
        sudo systemctl start "$WEB_SERVICE"
        sudo systemctl start "$TASKS_SERVICE"
        sleep 2
        echo ""
        echo "=== Status dos Serviços ==="
        sudo systemctl is-active "$WEB_SERVICE" && print_status "Web Server (Gunicorn)" || print_error "Web Server"
        sudo systemctl is-active "$TASKS_SERVICE" && print_status "Background Tasks" || print_error "Background Tasks"
        echo ""
        echo "Acesse: https://prospecta.cid-uff.net/"
        ;;
    stop)
        echo "Parando PROSPECTA..."
        sudo systemctl stop "$WEB_SERVICE"
        sudo systemctl stop "$TASKS_SERVICE"
        print_status "Serviços parados"
        ;;
    restart)
        echo "Reiniciando PROSPECTA..."
        sudo systemctl restart "$WEB_SERVICE"
        sudo systemctl restart "$TASKS_SERVICE"
        sleep 2
        $0 status
        ;;
    status)
        echo "=== Status do PROSPECTA ==="
        echo ""
        echo "Web Server (Gunicorn):"
        sudo systemctl status "$WEB_SERVICE" --no-pager -l | head -15
        echo ""
        echo "Background Tasks:"
        sudo systemctl status "$TASKS_SERVICE" --no-pager -l | head -15
        ;;
    logs)
        echo "=== Logs do PROSPECTA ==="
        echo ""
        echo "--- Gunicorn Access (últimas 20 linhas) ---"
        tail -20 "$PROJECT_DIR/logs/gunicorn_access.log" 2>/dev/null || echo "(sem logs ainda)"
        echo ""
        echo "--- Gunicorn Errors (últimas 20 linhas) ---"
        tail -20 "$PROJECT_DIR/logs/gunicorn_error.log" 2>/dev/null || echo "(sem erros)"
        echo ""
        echo "--- Background Tasks (últimas 20 linhas) ---"
        tail -20 "$PROJECT_DIR/logs/background_tasks.log" 2>/dev/null || echo "(sem logs ainda)"
        ;;
    logs-follow)
        echo "Seguindo logs em tempo real (Ctrl+C para sair)..."
        tail -f "$PROJECT_DIR/logs/gunicorn_access.log" "$PROJECT_DIR/logs/gunicorn_error.log" "$PROJECT_DIR/logs/background_tasks.log"
        ;;
    deploy)
        echo "=== Deploy do PROSPECTA ==="
        echo ""
        
        # 1. Atualizar código (se usar git)
        print_warning "Atualizando código..."
        cd "$PROJECT_DIR"
        git pull origin master 2>/dev/null && print_status "Código atualizado" || print_warning "Git pull falhou ou não configurado"
        
        # 2. Instalar dependências
        print_warning "Instalando dependências..."
        uv sync && print_status "Dependências instaladas"
        
        # 3. Migrações
        print_warning "Executando migrações..."
        uv run manage.py migrate && print_status "Migrações aplicadas"
        
        # 4. Coletar estáticos
        print_warning "Coletando arquivos estáticos..."
        uv run manage.py collectstatic --noinput && print_status "Estáticos coletados"
        
        # 5. Reiniciar serviços
        print_warning "Reiniciando serviços..."
        sudo systemctl restart "$WEB_SERVICE"
        sudo systemctl restart "$TASKS_SERVICE"
        sleep 2
        
        # 6. Verificar status
        echo ""
        $0 status
        echo ""
        print_status "Deploy concluído!"
        ;;
    uninstall)
        echo "Removendo serviços PROSPECTA..."
        sudo systemctl stop "$WEB_SERVICE" 2>/dev/null
        sudo systemctl stop "$TASKS_SERVICE" 2>/dev/null
        sudo systemctl disable "$WEB_SERVICE" 2>/dev/null
        sudo systemctl disable "$TASKS_SERVICE" 2>/dev/null
        sudo rm -f "/etc/systemd/system/$WEB_SERVICE.service"
        sudo rm -f "/etc/systemd/system/$TASKS_SERVICE.service"
        sudo systemctl daemon-reload
        print_status "Serviços removidos"
        ;;
    dev)
        echo "Iniciando em modo desenvolvimento..."
        cd "$PROJECT_DIR"
        uv run manage.py runserver 8555
        ;;
    shell)
        echo "Abrindo Django shell..."
        cd "$PROJECT_DIR"
        uv run manage.py shell
        ;;
    *)
        echo "PROSPECTA - Sistema de Gestão de Oportunidades"
        echo ""
        echo "Uso: $0 {comando}"
        echo ""
        echo "Comandos disponíveis:"
        echo "  install     - Instala os serviços systemd"
        echo "  start       - Inicia todos os serviços"
        echo "  stop        - Para todos os serviços"
        echo "  restart     - Reinicia todos os serviços"
        echo "  status      - Mostra status dos serviços"
        echo "  logs        - Mostra últimas linhas dos logs"
        echo "  logs-follow - Segue logs em tempo real"
        echo "  deploy      - Executa deploy completo (git pull, migrate, collectstatic, restart)"
        echo "  uninstall   - Remove os serviços"
        echo "  dev         - Inicia servidor de desenvolvimento"
        echo "  shell       - Abre Django shell"
        exit 1
        ;;
esac
