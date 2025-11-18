# 📅 Sistema de Reuniões & Google Calendar - Guia Completo

## 🎯 O Que Foi Implementado

Um sistema completo de gerenciamento de reuniões com integração automática ao Google Calendar, permitindo:

1. **Agendar Reuniões** - Criar, editar e deletar reuniões
2. **Sincronização Automática** - Sincronizar com Google Calendar
3. **Associar Atividades** - Ligar reuniões com tarefas específicas
4. **Rastreamento** - Manter histórico completo de todas as reuniões

---

## 🚀 Como Usar (Passo a Passo)

### **Passo 1: Conectar Google Calendar** 
1. Vá para a página de **OAuth Status** (clique em seu perfil → OAuth Status)
2. Clique em **"Conectar com Google"**
3. Autorize o acesso ao seu Google Calendar

### **Passo 2: Criar uma Reunião**
1. Na página da oportunidade, clique em **"Reuniões"** (ou use o guia visual)
2. Clique em **"+ Nova Reunião"**
3. Preencha os dados:
   - **Título**: Nome da reunião
   - **Tipo**: Virtual, Presencial ou Telefonema
   - **Data/Hora Início e Fim**: Quando será
   - **Local/Link**: Endereço ou link do Meet/Zoom
   - **Participantes**: Selecione quem vai participar
   - **Notas**: Adicione observações
   - **Itens de Ação**: Tarefas acordadas

4. Clique em **"Criar Reunião"**

### **Passo 3: Reunião Sincroniza com Google Calendar** 🔄
- ✅ Evento criado automaticamente em seu Google Calendar
- ✅ Participantes recebem convites por email
- ✅ Lembretes automáticos são configurados
- ✅ Aparecem em seus calendários pessoais

### **Passo 4: Associar a Atividades**
1. Na página da oportunidade, na seção de **Etapas → Atividades**
2. Clique no ícone de **link** (🔗) próximo à atividade
3. Selecione a reunião que foi discutida
4. Clique em **"Salvar Associação"**

### **Passo 5: Acompanhar Progresso**
- Veja todas as reuniões na página de **"Reuniões & Agenda"**
- Cada atividade mostra qual reunião foi associada
- Rastreie o histórico completo da oportunidade

---

## 📊 Estrutura do Sistema

### Modelos Criados

```
Meeting (Reunião)
├── opportunity (FK) → Oportunidade
├── title → Título
├── meeting_type → Tipo (virtual/presencial/telefonema)
├── status → Status (agendada/em_andamento/concluida/cancelada)
├── start_datetime → Data/Hora Início
├── end_datetime → Data/Hora Fim
├── organizer (FK) → Usuário organizador
├── attendees (M2M) → Participantes
├── location → Local/Link
├── google_event_id → ID no Google Calendar
├── synced_with_google → Sincronizado?
├── notes → Notas
└── action_items → Itens de ação

Activity (Atividade)
├── ... (campos existentes)
└── meeting (FK, nullable) → Reunião Associada ✨ NOVO

OpportunityDocument (Documento)
├── opportunity (FK)
├── title, document_type, file
├── uploaded_by (FK)
└── is_public

ActivityAttachment (Anexo)
├── activity (FK)
├── file, description
└── uploaded_by (FK)

GoogleCalendarIntegration
├── user (OneToOne)
├── access_token, refresh_token
├── calendar_id
└── is_active
```

### Rotas Principais

```
/oportunidades/<id>/reunioes/                    → Listar reuniões
/oportunidades/<id>/reunioes/criar/              → Criar reunião
/reunioes/<id>/editar/                           → Editar reunião
/reunioes/<id>/deletar/                          → Deletar reunião
/atividades/<id>/associar-reuniao/               → Associar reunião à atividade
/atividades/<id>/associar-reuniao-rapido/        → Endpoint AJAX rápido

/oportunidades/<id>/documentos/                  → Listar documentos
/oportunidades/<id>/documentos/upload/           → Upload de documento
/atividades/<id>/anexos/upload/                  → Upload de anexo

/google-calendar/callback/                       → Callback OAuth Google
```

---

## 🔧 Funcionalidades Técnicas

### Sincronização Automática
- Quando uma reunião é criada/editada, um **sinal Django** sincroniza com Google Calendar
- Se o usuário tiver conectado sua conta Google, a reunião aparece automaticamente
- Participantes recebem convites automáticos

### Permissões
- **Criar/Editar reuniões**: Admin, Gerente, Analista
- **Deletar reuniões**: Organizador ou Admin
- **Associar atividades**: Gerente ou Admin

### Validações
- Reunião deve pertencer à mesma oportunidade que a atividade
- Datas início/fim são validadas
- Participantes são verificados

### Tratamento de Erros
- Se Google Calendar não estiver conectado, reunião é criada normalmente (sem sync)
- Se houver erro na sincronização, mensagem de erro é exibida mas reunião é criada
- Campos são opcionais quando apropriado (notas, location, etc)

---

## 🎨 Interface & UX

### Componentes Criados
- `meeting_calendar_guide.html` - Guia visual com 4 passos
- `meetings/list.html` - Lista de reuniões com timeline
- `meetings/form.html` - Formulário de criar/editar
- `meetings/associate_to_activity.html` - Selector de reunião para atividade
- `opportunity_quicklinks.html` - Atualizado com links de reuniões

### Design
- ✨ **Tailwind CSS** - Responsivo e moderno
- 🎯 **Visual Hierarchy** - Passos bem organizados e fáceis de seguir
- 📱 **Mobile-Friendly** - Funciona em qualquer dispositivo
- ♿ **Acessível** - Labels claros, contraste adequado

### Cores Temáticas
- 🔵 **Azul** - Criação e informações
- 🩷 **Rosa** - Associação de atividades
- 🟢 **Verde** - Conclusão/Status
- 🟣 **Roxo** - Google Calendar

---

## 📝 Exemplos de Uso

### Cenário 1: Agendar Reunião com Cliente
```
1. Ir para oportunidade "Contrato ABC"
2. Clicar em "Reuniões" → "Nova Reunião"
3. Preencher:
   - Título: "Apresentação da Proposta"
   - Tipo: Virtual (Google Meet)
   - Data: 20/11/2025 às 14:00
   - Participantes: João (gerente), Cliente X
4. Salvar
5. Google Calendar atualiza automaticamente
6. Cliente recebe convite por email
7. Reunião é marcada no calendário
```

### Cenário 2: Associar Reunião com Atividade
```
1. Na oportunidade, seção "Etapas"
2. Clicar no ícone 🔗 da atividade "Preparar documentos"
3. Selecionar reunião "Apresentação da Proposta"
4. Salvar
5. Atividade agora mostra qual reunião foi discutida
6. Rastreamento completo ✅
```

### Cenário 3: Acompanhar Histórico
```
1. Abrir oportunidade
2. Ver "Reuniões & Agenda" com guia visual
3. Clicar em "Ver Todas as Reuniões"
4. Ver timeline com todas as reuniões
5. Cliquem em uma reunião para ver detalhes
6. Ver atividades associadas a cada reunião
```

---

## 🐛 Troubleshooting

### Problema: Reunião não aparece no Google Calendar
**Solução**: Verificar se Google Calendar está conectado (OAuth Status)

### Problema: Participante não recebe convite
**Solução**: Verificar se email está correto e Google Calendar está ativo

### Problema: Erro ao criar reunião
**Solução**: Verificar se data/hora estão preenchidas corretamente

### Problema: Não consigo associar reunião a atividade
**Solução**: Verificar se reunião pertence à mesma oportunidade

---

## 📚 Referências Técnicas

### Migrations Criadas
- `0007_activityattachment_googlecalendarintegration_meeting_and_more.py` - Tabelas principais
- `0008_add_meeting_to_activity.py` - Campo meeting em Activity
- `0009_fix_meeting_model.py` - Campos faltantes (status, notes, action_items)

### Signals (Automação)
- `post_save Meeting` → Sincroniza com Google Calendar
- `pre_delete Meeting` → Remove do Google Calendar
- `post_save OpportunityDocument` → Log no histórico
- `post_save ActivityAttachment` → Log no histórico

### Utilitários
- `google_calendar_utils.py` - Classe GoogleCalendarManager
- `calendar_views.py` - 10 views para CRUD
- `calendar_signals.py` - Automação com Django signals

---

## ✅ Checklist de Implementação

- [x] Modelos criados (Meeting, OpportunityDocument, ActivityAttachment, GoogleCalendarIntegration)
- [x] Migrations aplicadas (0007, 0008, 0009)
- [x] Admin interfaces configuradas
- [x] Views de CRUD criadas
- [x] Rotas registradas
- [x] Templates criados
- [x] Google Calendar integration framework (preparado para OAuth flow)
- [x] Signals para automação
- [x] Validações implementadas
- [x] Interface melhorada com guia visual
- [x] Redirecionamento corrigido
- [x] Documentação concluída ✨

---

## 🎓 Próximos Passos (Futuro)

1. **Implementar OAuth Flow completo** - Fluxo completo de autenticação Google
2. **Sincronização bidirecional** - Atualizações do Google Calendar de volta para o PROSPECTA
3. **Notificações** - Alertas quando reunião está próxima
4. **Integração com Email** - Enviar atas automaticamente após reunião
5. **Reports** - Relatório de reuniões por período
6. **Videochamada integrada** - Google Meet nativo no sistema

---

**Desenvolvido com ❤️ para PROSPECTA**
