# Funcionalidade de Parcerias em Oportunidades

## Resumo da Implementação

Foi adicionada a funcionalidade de **Parcerias** no módulo de Oportunidades do sistema PROSPECTA. Agora é possível associar uma ou várias empresas como parceiras em cada oportunidade de venda.

## Alterações Realizadas

### 1. Modelo de Dados (`prospecta/models.py`)

- **Campo adicionado**: `partnerships` no modelo `Opportunity`
  - Tipo: `ManyToManyField` com a tabela `Client`
  - Permite múltiplas parcerias por oportunidade
  - Campo opcional (blank=True)
  - Related name: `partnerships_opportunities`

### 2. Migração de Banco de Dados

- **Arquivo**: `prospecta/migrations/0013_opportunity_partnerships.py`
- **Status**: Aplicada com sucesso
- **Operação**: Criação da tabela intermediária para relacionamento many-to-many

### 3. Views (`prospecta/views.py`)

#### `opportunity_create`
- Adicionado tratamento para receber lista de IDs de parcerias via `request.POST.getlist('partnerships')`
- Parcerias são vinculadas após salvar a oportunidade (ManyToMany)
- Histórico registra nomes das parcerias adicionadas

#### `opportunity_update`
- Atualiza parcerias usando `opportunity.partnerships.set(partnerships_ids)`
- Histórico registra as parcerias atualizadas

### 4. Templates

#### `opportunities/form.html`
- Adicionado campo `<select multiple>` para seleção de parcerias
- Interface com lista de empresas disponíveis
- Instrução para usuário usar Ctrl/Command para seleção múltipla
- Parcerias pré-selecionadas são mantidas ao editar

#### `opportunities/detail.html`
- Nova seção "Parcerias" exibindo:
  - Nome da empresa parceira
  - CNPJ (quando disponível)
  - Telefone (quando disponível)
  - Email (quando disponível)
- Cards organizados em grid responsivo (1/2/3 colunas)
- Mensagem amigável quando não há parcerias

#### `opportunities/list.html`
- Nova coluna "Parcerias" na tabela de listagem
- Badge azul com ícone de handshake mostrando quantidade de parcerias
- Tooltip ao passar mouse exibindo nomes das empresas parceiras

#### `components/opportunities_table.html` (novo arquivo)
- Template para filtros HTMX
- Inclui coluna de parcerias com mesmo formato da listagem principal

### 5. Admin (`prospecta/admin.py`)

- Adicionado `filter_horizontal = ('partnerships',)` no `OpportunityAdmin`
- Interface administrativa permite seleção facilitada de múltiplas parcerias

## Como Usar

### Criar Oportunidade com Parcerias

1. Acesse "Nova Oportunidade"
2. Preencha os campos obrigatórios (Título, Cliente)
3. Na seção "Parcerias", selecione uma ou mais empresas:
   - **Windows**: Segure Ctrl + clique
   - **Mac**: Segure Command + clique
4. Salve a oportunidade

### Editar Parcerias

1. Acesse a oportunidade
2. Clique em "Editar"
3. Modifique a seleção de parcerias no campo múltiplo
4. Salve as alterações

### Visualizar Parcerias

- **Listagem**: Coluna "Parcerias" mostra badge com quantidade
- **Detalhes**: Seção dedicada exibe cards com informações completas

## Validações e Regras

- Campo **opcional** - oportunidades podem existir sem parcerias
- **Sem limite** de quantidade de parcerias por oportunidade
- Parcerias são empresas da tabela `Client` (mesma do campo Cliente)
- Histórico registra criação/atualização de parcerias
- Parcerias são preservadas ao editar outros campos da oportunidade

## Estrutura do Banco de Dados

```sql
-- Tabela intermediária criada automaticamente
CREATE TABLE "prospecta_opportunity_partnerships" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "opportunity_id" char(32) NOT NULL REFERENCES "tab_opportunities" ("id"),
    "client_id" char(32) NOT NULL REFERENCES "tab_clients" ("id")
);
```

## Interface Administrativa

No Django Admin (`/admin/prospecta/opportunity/`):
- Widget horizontal para seleção de parcerias
- Busca e filtro facilitados
- Exibição das parcerias vinculadas

## Considerações Técnicas

- **Performance**: Usar `select_related` ou `prefetch_related` ao listar oportunidades com parcerias
- **Exemplo**:
  ```python
  opportunities = Opportunity.objects.prefetch_related('partnerships').all()
  ```

## Próximas Melhorias Sugeridas

1. Filtro por parcerias na listagem de oportunidades
2. Relatório de parcerias mais frequentes
3. Dashboard com análise de parcerias
4. Notificações para empresas parceiras
5. Permissões customizadas para visualização de parcerias
