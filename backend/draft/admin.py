from django.contrib import admin
from .models import DraftSession, DraftPick


@admin.register(DraftSession)
class DraftSessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'status', 'num_teams', 'num_rounds', 'scoring_format', 'created_at']
    list_filter = ['status', 'scoring_format']


@admin.register(DraftPick)
class DraftPickAdmin(admin.ModelAdmin):
    list_display = ['session', 'overall_pick', 'round_number', 'team_number', 'player', 'is_user']
    list_filter = ['session', 'is_user']
