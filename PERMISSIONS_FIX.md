# Correção da Matriz de Permissões

## Problema Identificado

A matriz de permissões não estava salvando as permissões corretamente. Todas as permissões eram salvas como `false` independentemente do estado dos checkboxes no formulário.

## Causa Raiz

Incompatibilidade na geração de nomes de campos HTML entre o template e a view:

- **Template** (`permissions_matrix.html`): Usava `{{ permission|slugify }}` que transforma espaços em **hífens**
  - Exemplo: `admin_gerenciar-usuarios`

- **View** (`admin_views.py`): Usava `.replace(' ', '_')` que transforma espaços em **underscores**
  - Exemplo: `admin_gerenciar_usuarios`

Quando o formulário era submetido, a view procurava por nomes de campos que não existiam no POST, resultando em todas as permissões sendo definidas como `false`.

## Solução Implementada

### 1. Correção da View (`prospecta/admin_views.py`)

Substituído o método de normalização para usar `slugify` (consistente com o template):

```python
from django.utils.text import slugify

# ANTES:
field_name = f"{role}_{permission.lower().replace(' ', '_')}"

# DEPOIS:
field_name = f"{role}_{slugify(permission)}"
```

### 2. Restauração de Permissões Padrão

Criado comando de gerenciamento para facilitar a restauração:

```bash
# Resetar todas as permissões
python manage.py reset_permissions

# Resetar apenas um role específico
python manage.py reset_permissions --role admin
python manage.py reset_permissions --role gerente
```

## Estrutura de Permissões Padrão

### Admin (13/13 permissões)
- Gerenciar Usuários ✓
- Acessar Painel Admin ✓
- Criar Oportunidades ✓
- Editar Oportunidades ✓
- Deletar Oportunidades ✓
- Atribuir Oportunidades ✓
- Gerenciar Etapas ✓
- Gerenciar Atividades ✓
- Gerenciar Contatos ✓
- Gerenciar Clientes ✓
- Ver Relatórios ✓
- Exportar Dados ✓
- Configurar Sistema ✓

### Gerente (9/13 permissões)
- Criar Oportunidades ✓
- Editar Oportunidades ✓
- Atribuir Oportunidades ✓
- Gerenciar Etapas ✓
- Gerenciar Atividades ✓
- Gerenciar Contatos ✓
- Gerenciar Clientes ✓
- Ver Relatórios ✓
- Exportar Dados ✓

### Analista (2/13 permissões)
- Criar Oportunidades ✓
- Ver Relatórios ✓

### Visitante (0/13 permissões)
- Somente leitura (nenhuma permissão especial)

## Verificação no Banco de Dados

Para verificar as permissões salvas:

```sql
-- Ver todas as permissões de um role
SELECT 
    role,
    jsonb_object_keys(permissions) as permissao,
    permissions->>jsonb_object_keys(permissions) as habilitada
FROM tab_permissions_matrix
WHERE role = 'admin'
ORDER BY permissao;

-- Contar permissões habilitadas por role
SELECT 
    role,
    COUNT(*) FILTER (WHERE value::text = 'true') as habilitadas,
    COUNT(*) as total
FROM tab_permissions_matrix,
     jsonb_each(permissions)
GROUP BY role
ORDER BY role;
```

## Arquivos Modificados

1. **`prospecta/admin_views.py`** - Linha 310
   - Correção da função `permissions_matrix()` para usar `slugify` consistentemente

2. **`prospecta/management/commands/reset_permissions.py`** (novo)
   - Comando para restaurar permissões padrão

## Testando a Correção

1. Acesse: http://localhost:8555/matriz-permissoes/
2. Marque/desmarque alguns checkboxes
3. Clique em "Salvar Permissões"
4. Recarregue a página - os checkboxes devem manter o estado salvo
5. Verifique os cards no rodapé mostrando a contagem correta de permissões

## Schema da Tabela

```sql
\d tab_permissions_matrix

Coluna      | Tipo                     | Descrição
------------|--------------------------|----------------------------------
id          | bigint (PK)              | Identificador único
role        | varchar(20) UNIQUE       | Papel (admin/gerente/analista/visitante)
permissions | jsonb                    | Dicionário de permissões
created_at  | timestamp with time zone | Data de criação
updated_at  | timestamp with time zone | Data de última atualização
```

## Notas Importantes

- As permissões são armazenadas em formato JSON no campo `permissions`
- Cada role tem um registro único na tabela (constraint `UNIQUE` no campo `role`)
- O campo `permissions` é um dicionário onde as chaves são nomes de permissões e os valores são booleanos
- A view usa `update_or_create()` para garantir que não haja duplicatas

## Data da Correção

24 de novembro de 2025
