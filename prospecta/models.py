from django.db import models
from django.contrib.auth.models import User
import uuid


class UserProfile(models.Model):
    """Perfil estendido do usuário com roles e permissões"""
    ROLE_CHOICES = [
        ('admin', 'Administrador'),
        ('gerente', 'Gerente de Vendas'),
        ('vendedor', 'Vendedor'),
        ('analista', 'Analista'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name='Usuário')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='vendedor', verbose_name='Papel')
    department = models.CharField(max_length=100, blank=True, null=True, verbose_name='Departamento')
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='Telefone')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='Avatar')
    bio = models.TextField(blank=True, null=True, verbose_name='Biografia')
    is_active = models.BooleanField(default=True, verbose_name='Ativo')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

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

    def is_seller(self):
        return self.role in ['admin', 'gerente', 'vendedor']

class Client(models.Model):
    """Clientes"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name='ID')
    name = models.CharField(max_length=255, verbose_name='Nome')
    cnpj = models.CharField(max_length=18, unique=True, verbose_name='CNPJ')
    address = models.TextField(blank=True, null=True, verbose_name='Endereço')
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='Telefone')
    email = models.EmailField(blank=True, null=True, verbose_name='E-mail')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')

    class Meta:
        db_table = 'tab_clients'
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

    def __str__(self):
        return self.name

class Contact(models.Model):
    """Contatos dos clientes"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name='ID')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='contacts', verbose_name='Cliente')
    name = models.CharField(max_length=255, verbose_name='Nome')
    email = models.EmailField(blank=True, null=True, verbose_name='E-mail')
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='Telefone')
    position = models.CharField(max_length=100, blank=True, null=True, verbose_name='Cargo')
    notes = models.TextField(blank=True, null=True, verbose_name='Observações')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')

    class Meta:
        db_table = 'tab_contacts'
        verbose_name = 'Contato'
        verbose_name_plural = 'Contatos'

    def __str__(self):
        return f"{self.name} - {self.client.name}"

class SalesModel(models.Model):
    """Modelos de venda"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name='ID')
    name = models.CharField(max_length=255, verbose_name='Nome')
    description = models.TextField(blank=True, null=True, verbose_name='Descrição')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')

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
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name='ID')
    title = models.CharField(max_length=255, verbose_name='Título')
    description = models.TextField(blank=True, null=True, verbose_name='Descrição')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='opportunities', verbose_name='Cliente')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='opportunities_created', verbose_name='Criado por')
    responsible_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='opportunities_responsible', verbose_name='Usuário Responsável')
    sales_model = models.ForeignKey(SalesModel, on_delete=models.SET_NULL, null=True, related_name='opportunities', verbose_name='Modelo de Venda')
    value_brl = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, verbose_name='Valor (R$)')
    expected_delivery_date = models.DateField(blank=True, null=True, verbose_name='Data de Entrega Esperada')
    delivery_date = models.DateField(blank=True, null=True, verbose_name='Data de Entrega')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='aberta', verbose_name='Status')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

    class Meta:
        db_table = 'tab_opportunities'
        verbose_name = 'Oportunidade'
        verbose_name_plural = 'Oportunidades'

    def __str__(self):
        return self.title

class Stage(models.Model):
    """Etapas de uma oportunidade"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name='ID')
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE, related_name='stages', verbose_name='Oportunidade')
    name = models.CharField(max_length=255, verbose_name='Nome')
    order = models.IntegerField(verbose_name='Ordem')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='stages_created', verbose_name='Criado por')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

    class Meta:
        db_table = 'tab_stages'
        verbose_name = 'Etapa'
        verbose_name_plural = 'Etapas'
        ordering = ['order']

    def __str__(self):
        return f"{self.opportunity.title} - {self.name}"

class Activity(models.Model):
    """Atividades dentro das etapas"""
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('em_andamento', 'Em Andamento'),
        ('concluida', 'Concluída'),
        ('cancelada', 'Cancelada'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name='ID')
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE, related_name='activities', verbose_name='Etapa')
    title = models.CharField(max_length=255, verbose_name='Título')
    description = models.TextField(blank=True, null=True, verbose_name='Descrição')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='activities_assigned', verbose_name='Atribuída para')
    delegated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='activities_delegated', verbose_name='Delegada por')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente', verbose_name='Status')
    start_date = models.DateField(blank=True, null=True, verbose_name='Data de Início')
    expected_date = models.DateField(blank=True, null=True, verbose_name='Data Esperada')
    end_date = models.DateField(blank=True, null=True, verbose_name='Data de Conclusão')
    approved = models.BooleanField(default=False, verbose_name='Aprovada')
    approval_date = models.DateTimeField(blank=True, null=True, verbose_name='Data de Aprovação')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

    class Meta:
        db_table = 'tab_activities'
        verbose_name = 'Atividade'
        verbose_name_plural = 'Atividades'

    def __str__(self):
        return self.title

class OpportunityHistory(models.Model):
    """Histórico de mudanças em oportunidades"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name='ID')
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE, related_name='history', verbose_name='Oportunidade')
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='Alterado por')
    change_type = models.CharField(max_length=100, verbose_name='Tipo de Alteração')
    change_details = models.TextField(verbose_name='Detalhes da Alteração')
    changed_at = models.DateTimeField(auto_now_add=True, verbose_name='Alterado em')

    class Meta:
        db_table = 'tab_opportunity_history'
        verbose_name = 'Histórico de Oportunidade'
        verbose_name_plural = 'Históricos de Oportunidade'
        ordering = ['-changed_at']

    def __str__(self):
        return f"{self.opportunity.title} - {self.change_type}"

class StageHistory(models.Model):
    """Histórico de mudanças em etapas"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name='ID')
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE, related_name='history', verbose_name='Etapa')
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='Alterado por')
    change_type = models.CharField(max_length=100, verbose_name='Tipo de Alteração')
    change_details = models.TextField(verbose_name='Detalhes da Alteração')
    changed_at = models.DateTimeField(auto_now_add=True, verbose_name='Alterado em')

    class Meta:
        db_table = 'tab_stage_history'
        verbose_name = 'Histórico de Etapa'
        verbose_name_plural = 'Históricos de Etapa'
        ordering = ['-changed_at']

    def __str__(self):
        return f"{self.stage.name} - {self.change_type}"

class ActivityHistory(models.Model):
    """Histórico de mudanças em atividades"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name='ID')
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='history', verbose_name='Atividade')
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='Alterado por')
    change_type = models.CharField(max_length=100, verbose_name='Tipo de Alteração')
    change_details = models.TextField(verbose_name='Detalhes da Alteração')
    changed_at = models.DateTimeField(auto_now_add=True, verbose_name='Alterado em')

    class Meta:
        db_table = 'tab_activity_history'
        verbose_name = 'Histórico de Atividade'
        verbose_name_plural = 'Históricos de Atividade'
        ordering = ['-changed_at']

    def __str__(self):
        return f"{self.activity.title} - {self.change_type}"