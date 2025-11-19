# PROSPECTA - Fluxo e Regras de Negócio

## 📋 Visão Geral do Sistema

**PROSPECTA** é um sistema de gestão de oportunidades e vendas que segue um modelo estruturado de etapas (stages) e atividades. Cada oportunidade percorre um caminho predefinido com aprovações obrigatórias.

---

## 🔄 Fluxo Principal de Oportunidades

### 1. **Criação de Oportunidade**
- **Quem pode criar**: Admins, Gerentes, Analistas e Vendedores
- **O que deve ser informado**:
  - Título da oportunidade
  - Cliente (CNPJ único)
  - Valor em BRL
  - Data esperada de entrega
  - Modelo de vendas (definir qual)

- **O que acontece**:
  - Oportunidade criada com status `aberta`
  - Usuário criador se torna `responsible_user` (responsável)
  - Primeira etapa (Stage) é criada automaticamente
  - Histórico de criação é registrado

---

### 2. **Estrutura de Etapas (Stages)**

Cada oportunidade contém **N etapas** ordenadas sequencialmente:

| Propriedade | Descrição |
|-------------|-----------|
| **order** | Número da sequência (1, 2, 3...) |
| **title** | Nome da etapa (ex: "Prospecção", "Qualificação") |
| **description** | Detalhes sobre o que fazer nesta etapa |
| **duration_days** | Quantos dias esta etapa deve durar |
| **status** | não_iniciada, em_progresso, concluída, pausada |

**Fluxo de Status de Etapa**:
```
não_iniciada → em_progresso → concluída → [próxima etapa]
     ↓              ↓              ↓
    Criar    Executar Atividades  Aprovação necessária
```

---

### 3. **Atividades dentro de Etapas**

Cada etapa contém **atividades** (tarefas) que devem ser completadas:

| Propriedade | Regra |
|-------------|-------|
| **title** | Título descritivo da atividade |
| **description** | O que fazer |
| **assigned_to** | Qual usuário responsável (pode ser time) |
| **status** | pendente, em_progresso, concluída, bloqueada |
| **requires_approval** | Precisa de aprovação para passar? |
| **approved_by** | Quem aprovou (se necessário) |
| **approval_date** | Data da aprovação |

**Regra Crítica**: Se `requires_approval=True`, a atividade SÓ passa para `concluída` se um **Gerente ou Admin** aprovar.

---

### 4. **Transição de Etapas**

Uma etapa só pode avançar para a próxima se:

1. ✅ Todas as atividades estarem `concluída`
2. ✅ Se houver atividades com `requires_approval=True`, todas precisam ter `approved_by` preenchido
3. ✅ Status da etapa mudar de `em_progresso` → `concluída`
4. ✅ A próxima etapa será automaticamente iniciada (ou criada se não existir)

**Se alguma atividade falhar**:
- Status volta para `em_progresso`
- Gerador de história registra tentativa de conclusão
- Atividade é marcada como `bloqueada` se necessário

---

### 5. **Status de Oportunidade**

```
aberta → em_andamento → ganha → [arquivada]
         ↓
      perdida → [arquivada]
         ↓
      cancelada → [arquivada]
```

| Status | Quando | Ação |
|--------|--------|------|
| **aberta** | Recém-criada | Espera primeira atividade |
| **em_andamento** | Primeira etapa iniciada | Sistema processando etapas |
| **ganha** | Última etapa concluída com sucesso | Oportunidade finalizada com ganho |
| **perdida** | Usuário marca como perdida | Análise de fallback |
| **cancelada** | Usuário cancela | Sem ganho nem perda |

---

## 👥 Sistema de Permissões e Roles

### Hierarquia de Usuários

```
┌─────────────────────────────────────────────────┐
│              ADMINISTRADOR (admin)               │
│  • Acesso a tudo                                │
│  • Pode ver/editar todos usuários e dados       │
│  • Pode aprovar atividades                      │
│  • Acesso ao painel administrativo              │
└─────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────┐
│              GERENTE (gerente)                  │
│  • Cria e edita oportunidades de sua equipe    │
│  • Aprova atividades                            │
│  • Vê relatórios de vendas                      │
│  • Gerencia seu time de vendedores              │
└─────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────┐
│               ANALISTA (analista)               │
│  • Executa atividades atribuídas                │
│  • Vê oportunidades pertencentes a seu gerente  │
│  • Não pode aprovar atividades                  │
│  • Acesso limitado a relatórios                 │
└─────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────┐
│              VISITANTE (visitante)              │
│  • Apenas leitura                               │
│  • Não pode criar ou editar                     │
│  • Acesso para consulta                         │
└─────────────────────────────────────────────────┘
```

### Matriz de Permissões

| Ação | Admin | Gerente | Analista | Visitante |
|------|:-----:|:-------:|:--------:|:---------:|
| Ver todas oportunidades | ✅ | ❌ | ❌ | ❌ |
| Ver oportunidades do time | ✅ | ✅ | ✅ | ❌ |
| Criar oportunidade | ✅ | ✅ | ✅ | ❌ |
| Editar oportunidade | ✅ | ✅ | ❌ | ❌ |
| Executar atividade | ✅ | ✅ | ✅ | ❌ |
| Aprovar atividade | ✅ | ✅ | ❌ | ❌ |
| Gerenciar usuários | ✅ | ❌ | ❌ | ❌ |
| Ver relatórios | ✅ | ✅ | ✅ | ❌ |
| Editar matriz de permissões | ✅ | ❌ | ❌ | ❌ |

---

## 🎯 Regras de Negócio Críticas

### 1. **Regra de Clientes (CNPJ Único)**
- ✅ Cada cliente deve ter CNPJ único no sistema
- ❌ Não permitir duplicação de CNPJ
- 📝 Se cliente já existe, reutilizar em nova oportunidade

### 2. **Regra de Responsabilidade**
- Um usuário pode ter **múltiplas oportunidades** como responsável
- Gerentes veem oportunidades que **criaram ou são responsáveis**
- Analistas veem oportunidades **atribuídas a eles** apenas

### 3. **Regra de Aprovação**
- Atividades com `requires_approval=True` **precisam de aprovação explícita**
- Apenas **Gerentes ou Admins** podem aprovar
- Aprovação registra: **quem aprovou**, **quando aprovou**, **comentário (opcional)**

### 4. **Regra de Auditoria**
- **Toda mudança** é registrada em histórico:
  - OpportunityHistory (mudanças em oportunidade)
  - StageHistory (mudanças em etapa)
  - ActivityHistory (mudanças em atividade)
- Histórico inclui: **usuário**, **tipo de mudança**, **valores antigos → novos**, **timestamp**

### 5. **Regra de Timeline**
- Cada etapa tem `duration_days` (duração esperada)
- Se duração exceder, marcar como **atrasada** em relatório
- Alerta automático quando atingir 80% do tempo

### 6. **Regra de Participantes**
- Oportunidade pode ter **múltiplos participantes** (através de OpportunityParticipant)
- Cada participante pode ter **função diferente** (vendedor, suporte, etc)
- Todos participantes veem a oportunidade mas com **permissões limitadas**

---

## 📊 Estados e Transições de Atividade

```
                    ┌─────────────────┐
                    │    PENDENTE     │
                    │  (recém-criada) │
                    └────────┬────────┘
                             │
                    (usuário clica iniciar)
                             ↓
                    ┌─────────────────┐
                    │  EM_PROGRESSO   │
                    │ (trabalhando)   │
                    └────────┬────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
   (completa)        (requires_approval)   (bloqueada)
         │                   │                   │
         ↓                   ↓                   ↓
    ┌────────┐        ┌────────────┐      ┌──────────┐
    │CONCLUÍDA│        │AGUARDANDO  │      │BLOQUEADA │
    │         │        │APROVAÇÃO   │      │          │
    └────────┘        └─────┬──────┘      └──────────┘
                             │
                (admin/gerente aprova)
                             ↓
                        ┌─────────┐
                        │CONCLUÍDA│
                        └─────────┘
```

---

## 🔔 Notificações e Alertas

### Quando gerar notificação:
1. ✉️ Atividade atribuída a um usuário
2. ⏰ Atividade próximo do deadline
3. ⚠️ Atividade bloqueada
4. ✅ Atividade aprovada/rejeitada
5. 📈 Etapa concluída
6. 🎯 Oportunidade ganha/perdida
7. 👤 Novo participante adicionado

---

## 📈 Relatórios Disponíveis

### 1. **Relatório de Oportunidades**
- Por status (aberta, em_andamento, ganha, perdida, cancelada)
- Por usuário responsável
- Por valor total
- Timeline vs expectativa

### 2. **Relatório de Atividades**
- Pendentes
- Em progresso
- Atrasadas
- Bloqueadas
- Por pessoa

### 3. **Relatório de Desempenho**
- Taxa de conversão (ganha/total)
- Tempo médio por etapa
- Usuários mais produtivos
- Clientes com mais oportunidades

---

## 🛠️ Manutenção do Sistema

### Backups Automáticos
- Dados históricos nunca são deletados (apenas soft delete)
- Oportunidades canceladas ficam marcadas mas não são removidas
- Histórico serve como auditoria completa

### Sincronização com Sistemas Externos
- ✅ OAuth: Google, GitHub (para login)
- 🔄 Integrações futuras: CRM, ERP, Email

### Performance
- Índices em: user_id, status, created_at
- Paginação em listas (20 itens por página)
- Cache de dashboard (atualiza a cada 5 minutos)

---

## 📝 Exemplos de Uso

### Exemplo 1: Fluxo Completo de Oportunidade

```
1. Vendedor JOÃO cria oportunidade "Venda XYZ Corporation"
   ↓ [OportunityHistory: CRIADA]
   
2. Sistema cria Etapa 1: "Prospecção" (7 dias)
   ↓ [StageHistory: CRIADA]
   
3. Atividade 1: "Agendar reunião" → atribuída a JOÃO
   ↓ [ActivityHistory: CRIADA]
   
4. JOÃO marca como em_progresso + conclui
   ↓ Precisa aprovação? SIM → Aguarda GERENTE
   
5. GERENTE aprova atividade
   ↓ [ActivityHistory: APROVADA por GERENTE]
   
6. Atividade 1 marcada como CONCLUÍDA
   ↓ Etapa 1 continua, próxima atividade
   
7. Atividade 2 "Enviar proposta" concluída sem aprovação
   ↓ [ActivityHistory: CONCLUÍDA]
   
8. Todas atividades de Etapa 1 concluídas
   ↓ Sistema marca Etapa 1 como CONCLUÍDA
   ↓ Cria Etapa 2: "Negociação" (14 dias)
   
...continua até última etapa...

N. Última atividade aprovada
   ↓ Oportunidade marcada como GANHA
   ↓ [OportunityHistory: FINALIZADA - GANHA]
   ↓ Notificação enviada para JOÃO e seu GERENTE
```

### Exemplo 2: Atividade Bloqueada

```
1. Analista MARIA tem atividade "Validar dados"
   ↓ [ActivityHistory: CRIADA]

2. MARIA marca como em_progresso, encontra erro
   ↓ Clica "Bloquear" e descreve problema

3. Sistema marca como BLOQUEADA
   ↓ Notificação enviada para GERENTE

4. GERENTE CARLOS resolve o problema
   ↓ Clica "Desbloquear" e comenta solução

5. MARIA pode tentar novamente
   ↓ Marca como em_progresso

6. MARIA marca como concluída
   ↓ [ActivityHistory: CONCLUÍDA]
```

---

## 🔐 Segurança e Conformidade

- ✅ CSRF Protection (todas POST requerem token)
- ✅ SQL Injection Prevention (Django ORM)
- ✅ Rate Limiting (em desenvolvimento)
- ✅ Auditoria completa de ações
- ✅ Soft delete (dados não são realmente deletados)
- ✅ Controle de acesso por role

---

## 📱 Interfaces e Endpoints

### Admin Dashboard
- `/admin/` - Painel administrativo Django
- `/gerenciar/` - Painel customizado PROSPECTA
- `/gerenciar/permissoes/` - Matriz de permissões editável
- `/gerenciar/usuarios/` - Gerenciamento de usuários

### Operacional
- `/oportunidades/` - Listar oportunidades
- `/oportunidades/criar/` - Criar nova oportunidade
- `/oportunidades/<id>/` - Detalhe da oportunidade
- `/atividades/` - Listar atividades
- `/relatórios/` - Visualizar relatórios

---

## 🎓 Conclusão

O PROSPECTA segue um modelo **estruturado e auditável** onde:
- 🎯 Cada oportunidade segue um caminho predefinido
- ✅ Aprovações são obrigatórias onde necessário
- 📝 Tudo é registrado para auditoria
- 👥 Permissões são claramente definidas por role
- 📊 Dados estão sempre disponíveis para relatórios

**Objetivo**: Garantir rastreabilidade total, responsabilidade clara e eficiência operacional.
