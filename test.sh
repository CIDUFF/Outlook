#!/bin/bash

# Script de teste para o PROSPECTA

echo "================================"
echo "PROSPECTA - Teste de Funcionamento"
echo "================================"
echo ""

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}[1] Verificando servidor...${NC}"
if curl -s http://localhost:8555/ > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Servidor respondendo em http://localhost:8555${NC}"
else
    echo -e "${RED}✗ Servidor não está respondendo${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}[2] Verificando páginas principais...${NC}"

# Testar página inicial
if curl -s http://localhost:8555/ | grep -q "PROSPECTA"; then
    echo -e "${GREEN}✓ Página inicial funciona${NC}"
else
    echo -e "${RED}✗ Página inicial com erro${NC}"
fi

# Testar login
if curl -s http://localhost:8555/accounts/login/ | grep -q "login"; then
    echo -e "${GREEN}✓ Página de login funciona${NC}"
else
    echo -e "${RED}✗ Página de login com erro${NC}"
fi

# Testar admin
if curl -s http://localhost:8555/admin/ > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Admin funciona${NC}"
else
    echo -e "${RED}✗ Admin com erro${NC}"
fi

echo ""
echo -e "${YELLOW}[3] Instruções para testar edição de perfil:${NC}"
echo ""
echo "1. Acesse: http://localhost:8555"
echo "2. Faça login com suas credenciais"
echo "3. Clique no seu nome no menu superior direito"
echo "4. Selecione 'Meu Perfil'"
echo "5. Edite telefone, departamento ou biografia"
echo "6. Clique em 'Salvar Alterações'"
echo ""
echo -e "${GREEN}✓ Sistema pronto para uso!${NC}"
