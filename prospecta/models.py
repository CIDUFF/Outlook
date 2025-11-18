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


class Client(models.Model):
    """Empresas"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          editable=False, verbose_name='ID')
    name = models.CharField(max_length=255, verbose_name='Nome')
    cnpj = models.CharField(max_length=18, unique=True, verbose_name='CNPJ')
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
        ('em_andamento', 'Em Andamento'),
        ('ganha', 'Ganha'),
        ('perdida', 'Perdida'),
        ('cancelada', 'Cancelada'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          editable=False, verbose_name='ID')
    title = models.CharField(max_length=255, verbose_name='Título')
    description = models.TextField(
        blank=True, null=True, verbose_name='Descrição')
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
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pendente', verbose_name='Status')
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



