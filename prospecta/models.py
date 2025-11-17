from django.db import models
from django.contrib.auth.models import User
import uuid

class Client(models.Model):
    """Clientes"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    cnpj = models.CharField(max_length=18, unique=True)
    address = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tab_clients'

    def __str__(self):
        return self.name

class Contact(models.Model):
    """Contatos dos clientes"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='contacts')
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    position = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tab_contacts'

    def __str__(self):
        return f"{self.name} - {self.client.name}"

class Team(models.Model):
    """Times/Equipes"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='teams_created')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tab_teams'

    def __str__(self):
        return self.name

class SalesModel(models.Model):
    """Modelos de venda"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tab_sales_models'

    def __str__(self):
        return self.name

class Opportunity(models.Model):
    """Oportunidades de venda"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='opportunities')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='opportunities_created')
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, related_name='opportunities')
    sales_model = models.ForeignKey(SalesModel, on_delete=models.SET_NULL, null=True, related_name='opportunities')
    value_brl = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    expected_delivery_date = models.DateField(blank=True, null=True)
    delivery_date = models.DateField(blank=True, null=True)
    STATUS_CHOICES = [
        ('aberta', 'Aberta'),
        ('em_andamento', 'Em Andamento'),
        ('ganha', 'Ganha'),
        ('perdida', 'Perdida'),
        ('cancelada', 'Cancelada'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='aberta')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tab_opportunities'

    def __str__(self):
        return self.title

class Stage(models.Model):
    """Etapas de uma oportunidade"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE, related_name='stages')
    name = models.CharField(max_length=255)
    order = models.IntegerField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='stages_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tab_stages'
        ordering = ['order']

    def __str__(self):
        return f"{self.opportunity.title} - {self.name}"

class Activity(models.Model):
    """Atividades dentro das etapas"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE, related_name='activities')
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, related_name='activities')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='activities_assigned')
    delegated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='activities_delegated')
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('em_andamento', 'Em Andamento'),
        ('concluida', 'Concluída'),
        ('cancelada', 'Cancelada'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    start_date = models.DateField(blank=True, null=True)
    expected_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    approved = models.BooleanField(default=False)
    approval_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tab_activities'

    def __str__(self):
        return self.title

class OpportunityHistory(models.Model):
    """Histórico de mudanças em oportunidades"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE, related_name='history')
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    change_type = models.CharField(max_length=100)
    change_details = models.TextField()
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tab_opportunity_history'
        ordering = ['-changed_at']

    def __str__(self):
        return f"{self.opportunity.title} - {self.change_type}"

class StageHistory(models.Model):
    """Histórico de mudanças em etapas"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE, related_name='history')
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    change_type = models.CharField(max_length=100)
    change_details = models.TextField()
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tab_stage_history'
        ordering = ['-changed_at']

    def __str__(self):
        return f"{self.stage.name} - {self.change_type}"

class ActivityHistory(models.Model):
    """Histórico de mudanças em atividades"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='history')
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    change_type = models.CharField(max_length=100)
    change_details = models.TextField()
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tab_activity_history'
        ordering = ['-changed_at']

    def __str__(self):
        return f"{self.activity.title} - {self.change_type}"