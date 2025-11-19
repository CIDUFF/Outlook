# 🚀 Guia Rápido - Página de Ajuda para Administradores

## Acesso

A página de ajuda está disponível em:
- **URL**: `/gerenciar/ajuda/`
- **Acesso**: Somente para usuários com role **admin**
- **No Menu**: Administração → Ajuda

## Conteúdo da Página

### 📋 Tab 1: Visão Geral
Informações gerais sobre PROSPECTA:
- O que é o sistema
- Objetivo principal
- Estatísticas atuais
- Links rápidos para principais áreas

### 🔄 Tab 2: Fluxo de Oportunidades
Explicação completa do ciclo de vida:
1. **Criação** - Como uma oportunidade é criada
2. **Etapas** - Estrutura de stages sequenciais
3. **Atividades** - Tarefas dentro de cada etapa
4. **Aprovações** - Como funcionam as aprovações
5. **Conclusão** - Finalização da oportunidade

### 🔐 Tab 3: Permissões
Detalhamento do sistema de roles:
- **Admin**: Acesso total
- **Gerente**: Gerencia seu time
- **Analista**: Executa atividades
- **Visitante**: Apenas leitura

Com acesso direto à matriz de permissões editável.

### 👥 Tab 4: Gerenciar Usuários
Tutorial prático para:
- Criar novo usuário
- Editar usuário existente
- Desativar/Ativar usuários
- Boas práticas

### 💡 Tab 5: Dicas e Boas Práticas
6 dicas principais para melhor uso:
1. Organize bem as etapas
2. Use aprovações estrategicamente
3. Monitore relatórios
4. Mantenha segurança
5. Mantenha dados limpos
6. Treine sua equipe

---

## 📄 Documentação Completa

Para documentação detalhada, consulte:
- **Arquivo**: `FLUXO_REGRAS_NEGOCIO.md`
- **Local**: Raiz do projeto
- **Conteúdo**: 379 linhas com análise completa

---

## 🎯 Fluxo Recomendado de Uso

1. **Primeiro Acesso**: Leia a Aba "Visão Geral"
2. **Entender Fluxo**: Acesse "Fluxo de Oportunidades"
3. **Configurar Sistema**: Revise "Permissões" e edite a matriz conforme necessário
4. **Criar Usuários**: Use "Gerenciar Usuários"
5. **Aprender Dicas**: Consulte "Dicas e Boas Práticas"

---

## ⚡ Ações Rápidas da Página

Direto da página de ajuda, você pode acessar:
- **Ir para Painel** → Dashboard administrativo
- **Gerenciar Usuários** → Lista de usuários
- **Matriz de Permissões** → Editar permissões
- **Documentação** → Repositório GitHub

---

## 🔍 Tópicos Principais Explicados

### Status de Oportunidade
- **Aberta**: Recém-criada, aguardando ação
- **Em Andamento**: Processando etapas
- **Ganha**: Finalizada com sucesso
- **Perdida**: Oportunidade rejeitada
- **Cancelada**: Cancelada pelo usuário

### Estados de Atividade
- **Pendente**: Aguardando início
- **Em Progresso**: Sendo executada
- **Aguardando Aprovação**: Requer aprovação
- **Bloqueada**: Problema identificado
- **Concluída**: Finalizada com sucesso

### Regras Críticas
1. ✅ Aprovações são obrigatórias onde definido
2. ✅ Etapas devem ser completadas em sequência
3. ✅ Toda mudança é auditada
4. ✅ Dados históricos nunca são deletados
5. ✅ Permissões são verificadas em cada ação

---

## 🆘 Problemas Comuns

### "Não consigo acessar a página de ajuda"
- Verifique se seu usuário tem role = **admin**
- Se não, solicite ao admin para alterar seu role

### "A matriz de permissões está desatualizada"
- Qualquer mudança na matriz é salva no banco
- Clique em "Editar Matriz" e verifique

### "Um usuário foi deletado e quero recuperar"
- **Importante**: Use desativar em vez de deletar!
- Se deletado, dados históricos ainda existem
- Contate o admin do banco de dados

---

## 📞 Suporte

Para mais informações:
- Consulte `FLUXO_REGRAS_NEGOCIO.md`
- Verifique exemplos de uso na documentação
- Revise as boas práticas na Tab 5

---

**Versão**: 1.0.0  
**Última atualização**: 17 de novembro de 2025  
**Status**: ✅ Ativo e Testado
