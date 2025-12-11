from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


class UserProfile(models.Model):
    """Perfil estendido do usuário com roles e permissões"""
    ROLE_CHOICES = [
        ('admin', 'Administrador'),
        ('gerente', 'Gerente'),
        ('analista', 'Analista'),
        ('visitante', 'Visitante'),
    ]

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='profile', verbose_name='Usuário')
    role = models.CharField(
        max_length=20, choices=ROLE_CHOICES, default='visitante', verbose_name='Papel')
    department = models.CharField(
        max_length=100, blank=True, null=True, verbose_name='Departamento')
    phone = models.CharField(max_length=20, blank=True,
                             null=True, verbose_name='Telefone')
    avatar = models.ImageField(
        upload_to='avatars/', blank=True, null=True, verbose_name='Avatar')
    bio = models.TextField(blank=True, null=True, verbose_name='Biografia')
    is_active = models.BooleanField(default=True, verbose_name='Ativo')
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name='Atualizado em')

    class Meta:
        db_table = 'tab_user_profiles'
        verbose_name = 'Perfil de Usuário'
        verbose_name_plural = 'Perfis de Usuário'

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_role_display()}"

    def is_admin(self):
        return self.role == 'admin'

    def is_manager(self):
        return self.role in ['admin', 'gerente']

    def is_analyst(self):
        return self.role in ['admin', 'gerente', 'analista']

    def is_visitor(self):
        return self.role == 'visitante'

    def can_write(self):
        """Retorna True se o usuário pode escrever/editar/deletar"""
        return self.role in ['admin', 'gerente', 'analista']

    def can_read(self):
        """Retorna True se o usuário pode ler (todos podem)"""
        return True

    def has_permission(self, permission_name):
        """
        Verifica se o usuário tem uma permissão específica baseada na PermissionsMatrix.
        Admins sempre têm todas as permissões.

        Args:
            permission_name: Nome da permissão (ex: 'Criar Oportunidades')
        Returns:
            bool: True se o usuário tem a permissão
        """
        # Admins têm todas as permissões
        if self.role == 'admin':
            return True

        try:
            # Importa aqui para evitar importação circular
            from prospecta.models import PermissionsMatrix
            matrix = PermissionsMatrix.objects.filter(role=self.role).first()
            if matrix and matrix.permissions:
                return matrix.permissions.get(permission_name, False)
        except Exception:
            pass

        return False

    def get_all_permissions(self):
        """
        Retorna todas as permissões do usuário baseadas na PermissionsMatrix.
        Admins recebem todas as permissões como True.

        Returns:
            dict: Dicionário de permissões {nome: bool}
        """
        default_permissions = {
            'Visualizar Dashboard': True,
            'Criar Oportunidades': False,
            'Editar Oportunidades': False,
            'Excluir Oportunidades': False,
            'Criar Clientes': False,
            'Editar Clientes': False,
            'Excluir Clientes': False,
            'Criar Atividades': False,
            'Editar Atividades': False,
            'Excluir Atividades': False,
            'Aprovar Atividades': False,
            'Gerenciar Usuários': False,
            'Gerenciar Permissões': False,
            'Ver Relatórios': False,
            'Exportar Dados': False,
        }

        # Admins têm todas as permissões
        if self.role == 'admin':
            return {k: True for k in default_permissions}

        try:
            from prospecta.models import PermissionsMatrix
            matrix = PermissionsMatrix.objects.filter(role=self.role).first()
            if matrix and matrix.permissions:
                # Merge permissões padrão com as da matriz
                permissions = default_permissions.copy()
                permissions.update(matrix.permissions)
                return permissions
        except Exception:
            pass

        return default_permissions


class Client(models.Model):
    """Empresas"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          editable=False, verbose_name='ID')
    name = models.CharField(max_length=255, verbose_name='Nome')
    razao_social = models.CharField(max_length=255, blank=True, null=True, verbose_name='Razão Social')
    cnpj = models.CharField(max_length=18, blank=True, null=True, verbose_name='CNPJ')
    address = models.TextField(blank=True, null=True, verbose_name='Endereço')
    phone = models.CharField(max_length=20, blank=True,
                             null=True, verbose_name='Telefone')
    email = models.EmailField(blank=True, null=True, verbose_name='E-mail')
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name='Criado em')

    class Meta:
        db_table = 'tab_clients'
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'

    def __str__(self):
        return self.name


class Contact(models.Model):
    """Contatos dos clientes"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          editable=False, verbose_name='ID')
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name='contacts', verbose_name='Cliente')
    name = models.CharField(max_length=255, verbose_name='Nome')
    email = models.EmailField(blank=True, null=True, verbose_name='E-mail')
    phone = models.CharField(max_length=20, blank=True,
                             null=True, verbose_name='Telefone')
    position = models.CharField(
        max_length=100, blank=True, null=True, verbose_name='Cargo')
    notes = models.TextField(blank=True, null=True, verbose_name='Observações')
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name='Criado em')

    class Meta:
        db_table = 'tab_contacts'
        verbose_name = 'Contato'
        verbose_name_plural = 'Contatos'

    def __str__(self):
        return f"{self.name} - {self.client.name}"


class SalesModel(models.Model):
    """Modelos de venda"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          editable=False, verbose_name='ID')
    name = models.CharField(max_length=255, verbose_name='Nome')
    description = models.TextField(
        blank=True, null=True, verbose_name='Descrição')
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name='Criado em')

    class Meta:
        db_table = 'tab_sales_models'
        verbose_name = 'Modelo de Venda'
        verbose_name_plural = 'Modelos de Venda'

    def __str__(self):
        return self.name


class Opportunity(models.Model):
    """Oportunidades de venda"""
    STATUS_CHOICES = [
        ('aberta', 'Aberta'),
        ('atrasada', 'Atrasada'),
        ('ganha', 'Ganha'),
        ('perdida', 'Perdida'),
        ('suspensa', 'Suspensa'),
        ('cancelada', 'Cancelada'),
    ]

    ESTAGIO_CHOICES = [
        ('outlook', 'Outlook'),
        ('proposta', 'Proposta'),
        ('projeto', 'Projeto'),
    ]

    FASE_CHOICES = [
        ('lead_contato_inicial', 'Lead/Contato inicial'),
        ('qualificacao', 'Qualificação'),
        ('diagnostico_entendimento', 'Diagnóstico/Entendimento do Escopo'),
        ('desenho_solucao', 'Desenho da Solução/Pré-proposta'),
        ('proposta_enviada', 'Proposta Enviada'),
        ('negociacao_ajustes', 'Negociação/Ajustes'),
        ('acordo_verbal', 'Acordo Verbal/Intenção de Fechar'),
        ('projeto_fechado', 'Projeto Fechado'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          editable=False, verbose_name='ID')
    title = models.CharField(max_length=255, verbose_name='Título')
    description = models.TextField(
        blank=True, null=True, verbose_name='Descrição')
    notes = models.TextField(
        blank=True, null=True, verbose_name='Observações')
    produto = models.CharField(
        max_length=255, blank=True, null=True, verbose_name='Produto')
    client = models.ForeignKey(Client, on_delete=models.CASCADE,
                               related_name='opportunities', verbose_name='Cliente')
    partnerships = models.ManyToManyField(
        Client, blank=True, related_name='partnerships_opportunities', verbose_name='Parcerias')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                   related_name='opportunities_created', verbose_name='Criado por')
    responsible_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                         related_name='opportunities_responsible', verbose_name='Usuário Responsável')
    sales_model = models.ForeignKey(SalesModel, on_delete=models.SET_NULL,
                                    null=True, related_name='opportunities', verbose_name='Modelo de Venda')
    value_brl = models.DecimalField(
        max_digits=15, decimal_places=2, blank=True, null=True, verbose_name='Valor (R$)')
    expected_delivery_date = models.DateField(
        blank=True, null=True, verbose_name='Data de Entrega Esperada')
    delivery_date = models.DateField(
        blank=True, null=True, verbose_name='Data de Entrega')
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='aberta', verbose_name='Status')
    estagio = models.CharField(
        max_length=20, choices=ESTAGIO_CHOICES, blank=True, null=True, verbose_name='Estágio')
    fase = models.CharField(
        max_length=50, choices=FASE_CHOICES, blank=True, null=True, verbose_name='Fase')
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name='Atualizado em')

    class Meta:
        db_table = 'tab_opportunities'
        verbose_name = 'Oportunidade'
        verbose_name_plural = 'Oportunidades'

    def __str__(self):
        return self.title


class Stage(models.Model):
    """Etapas de uma oportunidade"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          editable=False, verbose_name='ID')
    opportunity = models.ForeignKey(
        Opportunity, on_delete=models.CASCADE, related_name='stages', verbose_name='Oportunidade')
    name = models.CharField(max_length=255, verbose_name='Nome')
    order = models.IntegerField(verbose_name='Ordem')
    responsible_user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='stages_responsible', verbose_name='Responsável pela Etapa')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL,
                                   null=True, related_name='stages_created', verbose_name='Criado por')
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name='Atualizado em')

    class Meta:
        db_table = 'tab_stages'
        verbose_name = 'Etapa'
        verbose_name_plural = 'Etapas'
        ordering = ['order']

    def __str__(self):
        return f"{self.opportunity.title} - {self.name}"


class Activity(models.Model):
    """Atividades dentro de etapas em oportunidades"""
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('em_andamento', 'Em Andamento'),
        ('aguardando_verificacao', 'Aguardando Verificação'),
        ('concluida', 'Concluída'),
        ('cancelada', 'Cancelada'),
    ]

    ACTIVITY_TYPE_CHOICES = [
        ('tarefa', 'Tarefa'),
        ('reuniao', 'Reunião'),
        ('ligacao', 'Ligação'),
        ('email', 'Email'),
        ('proposta', 'Proposta'),
        ('follow_up', 'Follow-up'),
        ('outro', 'Outro'),
    ]

    APPROVAL_STATUS_CHOICES = [
        ('nao_aplicavel', 'Não Aplicável'),
        ('pendente', 'Pendente'),
        ('submetida', 'Submetida para Verificação'),
        ('aprovada', 'Aprovada'),
        ('reprovada', 'Reprovada'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          editable=False, verbose_name='ID')
    stage = models.ForeignKey(
        Stage, on_delete=models.CASCADE, related_name='activities', verbose_name='Etapa')
    title = models.CharField(max_length=255, verbose_name='Título')
    description = models.TextField(
        blank=True, null=True, verbose_name='Descrição')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                    related_name='activities_assigned', verbose_name='Atribuída para')
    delegated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                     related_name='activities_delegated', verbose_name='Delegada por')
    # Novos campos para fluxo de verificação/aprovação
    verifier = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='activities_to_verify', verbose_name='Verificador')
    previous_assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                             related_name='activities_previously_assigned', verbose_name='Responsável Anterior')
    completion_notes = models.TextField(
        blank=True, null=True, verbose_name='Notas de Conclusão')
    rejection_reason = models.TextField(
        blank=True, null=True, verbose_name='Motivo da Reprovação')
    submission_date = models.DateTimeField(
        blank=True, null=True, verbose_name='Data de Submissão')
    approval_status = models.CharField(
        max_length=20, choices=APPROVAL_STATUS_CHOICES, default='nao_aplicavel', verbose_name='Status de Aprovação')
    assigned_at = models.DateTimeField(
        blank=True, null=True, verbose_name='Data da Atribuição')
    status = models.CharField(
        max_length=30, choices=STATUS_CHOICES, default='pendente', verbose_name='Status')
    activity_type = models.CharField(
        max_length=20, choices=ACTIVITY_TYPE_CHOICES, default='tarefa', verbose_name='Tipo de Atividade')
    start_date = models.DateField(
        blank=True, null=True, verbose_name='Data de Início')
    expected_date = models.DateField(
        blank=True, null=True, verbose_name='Data Esperada')
    end_date = models.DateField(
        blank=True, null=True, verbose_name='Data de Conclusão')
    approved = models.BooleanField(default=False, verbose_name='Aprovada')
    approval_date = models.DateTimeField(
        blank=True, null=True, verbose_name='Data de Aprovação')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='activities_approved', verbose_name='Aprovada por')
    # Reunião associada (opcional)
    meeting = models.ForeignKey(
        'Meeting', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='activities', verbose_name='Reunião Associada')
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name='Atualizado em')

    class Meta:
        db_table = 'tab_activities'
        verbose_name = 'Atividade'
        verbose_name_plural = 'Atividades'

    def __str__(self):
        return self.title

    def can_be_submitted_for_verification(self):
        """Verifica se a atividade pode ser submetida para verificação"""
        return self.status in ['em_andamento', 'pendente'] and self.approval_status in ['nao_aplicavel', 'pendente', 'reprovada']

    def can_be_verified(self):
        """Verifica se a atividade está aguardando verificação"""
        return self.approval_status == 'submetida' and self.status == 'aguardando_verificacao'


class OpportunityHistory(models.Model):
    """Histórico de mudanças em oportunidades"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          editable=False, verbose_name='ID')
    opportunity = models.ForeignKey(
        Opportunity, on_delete=models.CASCADE, related_name='history', verbose_name='Oportunidade')
    changed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, verbose_name='Alterado por')
    change_type = models.CharField(
        max_length=100, verbose_name='Tipo de Alteração')
    change_details = models.TextField(verbose_name='Detalhes da Alteração')
    changed_at = models.DateTimeField(
        auto_now_add=True, verbose_name='Alterado em')

    class Meta:
        db_table = 'tab_opportunity_history'
        verbose_name = 'Histórico de Oportunidade'
        verbose_name_plural = 'Históricos de Oportunidade'
        ordering = ['-changed_at']

    def __str__(self):
        return f"{self.opportunity.title} - {self.change_type}"


class StageHistory(models.Model):
    """Histórico de mudanças em etapas"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          editable=False, verbose_name='ID')
    stage = models.ForeignKey(
        Stage, on_delete=models.CASCADE, related_name='history', verbose_name='Etapa')
    changed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, verbose_name='Alterado por')
    change_type = models.CharField(
        max_length=100, verbose_name='Tipo de Alteração')
    change_details = models.TextField(verbose_name='Detalhes da Alteração')
    changed_at = models.DateTimeField(
        auto_now_add=True, verbose_name='Alterado em')

    class Meta:
        db_table = 'tab_stage_history'
        verbose_name = 'Histórico de Etapa'
        verbose_name_plural = 'Históricos de Etapa'
        ordering = ['-changed_at']

    def __str__(self):
        return f"{self.stage.name} - {self.change_type}"


class ActivityHistory(models.Model):
    """Histórico de mudanças em atividades"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          editable=False, verbose_name='ID')
    activity = models.ForeignKey(
        Activity, on_delete=models.CASCADE, related_name='history', verbose_name='Atividade')
    changed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, verbose_name='Alterado por')
    change_type = models.CharField(
        max_length=100, verbose_name='Tipo de Alteração')
    change_details = models.TextField(verbose_name='Detalhes da Alteração')
    changed_at = models.DateTimeField(
        auto_now_add=True, verbose_name='Alterado em')

    class Meta:
        db_table = 'tab_activity_history'
        verbose_name = 'Histórico de Atividade'
        verbose_name_plural = 'Históricos de Atividade'
        ordering = ['-changed_at']

    def __str__(self):
        return f"{self.activity.title} - {self.change_type}"


class OpportunityParticipant(models.Model):
    """Participantes adicionados a uma oportunidade para receber notificações"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          editable=False, verbose_name='ID')
    opportunity = models.ForeignKey(
        Opportunity, on_delete=models.CASCADE, related_name='participants', verbose_name='Oportunidade')
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='opportunity_participations', verbose_name='Participante')
    added_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='participants_added', verbose_name='Adicionado por')
    added_at = models.DateTimeField(
        auto_now_add=True, verbose_name='Adicionado em')
    notify_on_update = models.BooleanField(
        default=True, verbose_name='Notificar em Atualizações')

    class Meta:
        db_table = 'tab_opportunity_participants'
        verbose_name = 'Participante de Oportunidade'
        verbose_name_plural = 'Participantes de Oportunidade'
        unique_together = ('opportunity', 'user')
        ordering = ['added_at']

    def __str__(self):
        return f"{self.opportunity.title} - {self.user.get_full_name()}"


class PermissionsMatrix(models.Model):
    """Matriz de permissões customizável por role"""
    role = models.CharField(
        max_length=20,
        choices=UserProfile.ROLE_CHOICES,
        unique=True,
        verbose_name='Papel'
    )
    permissions = models.JSONField(
        default=dict,
        verbose_name='Permissões',
        help_text='Dicionário de permissões e seus valores (True/False)'
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name='Atualizado em')

    class Meta:
        db_table = 'tab_permissions_matrix'
        verbose_name = 'Matriz de Permissões'
        verbose_name_plural = 'Matrizes de Permissões'

    def __str__(self):
        return f"Permissões - {self.get_role_display()}"


# ============================================================================
# DOCUMENTOS E ANEXOS
# ============================================================================

class OpportunityCustomValue(models.Model):
    """Valores customizados associados a uma oportunidade"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          editable=False, verbose_name='ID')
    opportunity = models.ForeignKey(
        Opportunity, on_delete=models.CASCADE, related_name='custom_values', verbose_name='Oportunidade')
    label = models.CharField(max_length=255, verbose_name='Legenda')
    value = models.DecimalField(
        max_digits=15, decimal_places=2, verbose_name='Valor (R$)')
    order = models.IntegerField(default=0, verbose_name='Ordem')
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name='Atualizado em')

    class Meta:
        db_table = 'tab_opportunity_custom_values'
        verbose_name = 'Valor Customizado da Oportunidade'
        verbose_name_plural = 'Valores Customizados das Oportunidades'
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"{self.opportunity.title} - {self.label}: R$ {self.value}"


class OpportunityDocument(models.Model):
    """Documentos anexados às oportunidades"""
    DOCUMENT_TYPE_CHOICES = [
        ('proposta', 'Proposta Comercial'),
        ('contrato', 'Contrato'),
        ('apresentacao', 'Apresentação'),
        ('orcamento', 'Orçamento'),
        ('especificacao', 'Especificação Técnica'),
        ('ata', 'Ata de Reunião'),
        ('outro', 'Outro'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          editable=False, verbose_name='ID')
    opportunity = models.ForeignKey(
        Opportunity, on_delete=models.CASCADE, related_name='documents', verbose_name='Oportunidade')
    title = models.CharField(max_length=255, verbose_name='Título')
    document_type = models.CharField(
        max_length=20, choices=DOCUMENT_TYPE_CHOICES, default='outro', verbose_name='Tipo')
    file = models.FileField(
        upload_to='opportunities/documents/', verbose_name='Arquivo')
    description = models.TextField(
        blank=True, null=True, verbose_name='Descrição')
    uploaded_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='uploaded_documents', verbose_name='Enviado por')
    is_public = models.BooleanField(default=False, verbose_name='Público')
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name='Atualizado em')

    class Meta:
        db_table = 'tab_opportunity_documents'
        verbose_name = 'Documento da Oportunidade'
        verbose_name_plural = 'Documentos das Oportunidades'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.opportunity.title}"


class ActivityAttachment(models.Model):
    """Anexos em atividades"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          editable=False, verbose_name='ID')
    activity = models.ForeignKey(
        Activity, on_delete=models.CASCADE, related_name='attachments', verbose_name='Atividade')
    file = models.FileField(
        upload_to='activities/attachments/', verbose_name='Arquivo')
    description = models.TextField(
        blank=True, null=True, verbose_name='Descrição')
    uploaded_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='uploaded_attachments', verbose_name='Enviado por')
    created_at = models.DateTimeField(
        default=timezone.now, verbose_name='Criado em')

    class Meta:
        db_table = 'tab_activity_attachments'
        verbose_name = 'Anexo da Atividade'
        verbose_name_plural = 'Anexos das Atividades'
        ordering = ['-created_at']

    def __str__(self):
        return f"Anexo - {self.activity.title}"


# ============================================================================
# AGENDA E REUNIÕES
# ============================================================================

class Meeting(models.Model):
    """Reuniões vinculadas a oportunidades"""
    MEETING_TYPE_CHOICES = [
        ('presencial', 'Presencial'),
        ('virtual', 'Virtual (Online)'),
        ('telefonema', 'Telefonema'),
    ]

    STATUS_CHOICES = [
        ('agendada', 'Agendada'),
        ('em_andamento', 'Em Andamento'),
        ('concluida', 'Concluída'),
        ('cancelada', 'Cancelada'),
        ('remarcada', 'Remarcada'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          editable=False, verbose_name='ID')
    opportunity = models.ForeignKey(
        Opportunity, on_delete=models.CASCADE, related_name='meetings', verbose_name='Oportunidade')
    title = models.CharField(max_length=255, verbose_name='Título')
    description = models.TextField(
        blank=True, null=True, verbose_name='Descrição')
    meeting_type = models.CharField(
        max_length=20, choices=MEETING_TYPE_CHOICES, default='virtual', verbose_name='Tipo')
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='agendada', verbose_name='Status')

    # Data e hora
    start_datetime = models.DateTimeField(verbose_name='Data/Hora Início')
    end_datetime = models.DateTimeField(verbose_name='Data/Hora Fim')

    # Participantes
    organizer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='organized_meetings', verbose_name='Organizador')
    attendees = models.ManyToManyField(
        User, related_name='attending_meetings', blank=True, verbose_name='Participantes')

    # Local ou link
    location = models.CharField(
        max_length=500, blank=True, null=True, verbose_name='Local/Link')

    # Notas e resultados
    notes = models.TextField(blank=True, null=True, verbose_name='Notas')
    action_items = models.TextField(
        blank=True, null=True, verbose_name='Itens de Ação')

    created_at = models.DateTimeField(
        default=timezone.now, verbose_name='Criado em')
    updated_at = models.DateTimeField(
        default=timezone.now, verbose_name='Atualizado em')

    class Meta:
        db_table = 'tab_meetings'
        verbose_name = 'Reunião'
        verbose_name_plural = 'Reuniões'
        ordering = ['-start_datetime']

    def __str__(self):
        return f"{self.title} - {self.start_datetime.strftime('%d/%m/%Y %H:%M')}"


# ============================================================================
# NOTIFICAÇÕES DO SISTEMA
# ============================================================================

class Notification(models.Model):
    """Notificações in-app e por email"""
    NOTIFICATION_TYPE_CHOICES = [
        ('activity_assigned', 'Atividade Atribuída'),
        ('activity_reassigned', 'Atividade Reatribuída'),
        ('activity_submitted', 'Atividade Submetida para Verificação'),
        ('activity_approved', 'Atividade Aprovada'),
        ('activity_rejected', 'Atividade Reprovada'),
        ('activity_reminder', 'Lembrete de Atividade'),
        ('activity_comment', 'Comentário em Atividade'),
        ('opportunity_update', 'Atualização de Oportunidade'),
        ('general', 'Notificação Geral'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Baixa'),
        ('normal', 'Normal'),
        ('high', 'Alta'),
        ('urgent', 'Urgente'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          editable=False, verbose_name='ID')
    recipient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='notifications', verbose_name='Destinatário')
    sender = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='notifications_sent', verbose_name='Remetente')
    notification_type = models.CharField(
        max_length=50, choices=NOTIFICATION_TYPE_CHOICES, default='general', verbose_name='Tipo')
    priority = models.CharField(
        max_length=10, choices=PRIORITY_CHOICES, default='normal', verbose_name='Prioridade')
    title = models.CharField(max_length=255, verbose_name='Título')
    message = models.TextField(verbose_name='Mensagem')

    # Relacionamentos opcionais
    related_activity = models.ForeignKey(
        Activity, on_delete=models.CASCADE, null=True, blank=True,
        related_name='notifications', verbose_name='Atividade Relacionada')
    related_opportunity = models.ForeignKey(
        Opportunity, on_delete=models.CASCADE, null=True, blank=True,
        related_name='notifications', verbose_name='Oportunidade Relacionada')

    # Status
    is_read = models.BooleanField(default=False, verbose_name='Lida')
    read_at = models.DateTimeField(
        blank=True, null=True, verbose_name='Lida em')
    email_sent = models.BooleanField(
        default=False, verbose_name='Email Enviado')
    email_sent_at = models.DateTimeField(
        blank=True, null=True, verbose_name='Email Enviado em')

    # URL para redirecionamento
    action_url = models.CharField(
        max_length=500, blank=True, null=True, verbose_name='URL de Ação')

    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name='Criado em')

    class Meta:
        db_table = 'tab_notifications'
        verbose_name = 'Notificação'
        verbose_name_plural = 'Notificações'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['recipient', 'created_at']),
        ]

    def __str__(self):
        return f"{self.title} - {self.recipient.get_full_name()}"

    def mark_as_read(self):
        """Marca a notificação como lida"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])


class ActivityComment(models.Model):
    """Comentários nas atividades para comunicação entre responsável e verificador"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          editable=False, verbose_name='ID')
    activity = models.ForeignKey(
        Activity, on_delete=models.CASCADE, related_name='comments', verbose_name='Atividade')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='activity_comments', verbose_name='Autor')
    content = models.TextField(verbose_name='Conteúdo')
    is_system_message = models.BooleanField(
        default=False, verbose_name='Mensagem do Sistema')
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name='Atualizado em')

    class Meta:
        db_table = 'tab_activity_comments'
        verbose_name = 'Comentário de Atividade'
        verbose_name_plural = 'Comentários de Atividades'
        ordering = ['created_at']

    def __str__(self):
        return f"Comentário de {self.author.get_full_name()} em {self.activity.title}"


# ============================================================================
# STATUS DE OPORTUNIDADES (CONFIGURÁVEL)
# ============================================================================

class OpportunityStatus(models.Model):
    """Status configuráveis para oportunidades"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          editable=False, verbose_name='ID')
    name = models.CharField(max_length=100, unique=True, verbose_name='Nome')
    slug = models.SlugField(max_length=100, unique=True, verbose_name='Slug',
                            help_text='Identificador único (ex: em_andamento)')
    color = models.CharField(max_length=50, default='gray', verbose_name='Cor',
                             help_text='Cor do badge (ex: blue, green, red, yellow, purple, gray)')
    icon = models.CharField(max_length=50, blank=True, null=True, verbose_name='Ícone',
                            help_text='Classe do ícone FontAwesome (ex: fa-check)')
    description = models.TextField(blank=True, null=True, verbose_name='Descrição')
    order = models.IntegerField(default=0, verbose_name='Ordem',
                                help_text='Ordem de exibição na lista')
    is_active = models.BooleanField(default=True, verbose_name='Ativo')
    is_default = models.BooleanField(default=False, verbose_name='Padrão',
                                     help_text='Status padrão para novas oportunidades')
    is_closed = models.BooleanField(default=False, verbose_name='Fechado',
                                    help_text='Indica se o status representa uma oportunidade fechada')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

    class Meta:
        db_table = 'tab_opportunity_status'
        verbose_name = 'Status de Oportunidade'
        verbose_name_plural = 'Status de Oportunidades'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Se este status é marcado como padrão, remove o padrão dos outros
        if self.is_default:
            OpportunityStatus.objects.filter(is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)

    @classmethod
    def get_default(cls):
        """Retorna o status padrão ou o primeiro status ativo"""
        default = cls.objects.filter(is_default=True, is_active=True).first()
        if not default:
            default = cls.objects.filter(is_active=True).first()
        return default

    @classmethod
    def get_choices(cls):
        """Retorna choices para uso em formulários"""
        return [(s.slug, s.name) for s in cls.objects.filter(is_active=True)]
