from django.contrib import admin
from .models import Job, Review

# Register your models here.
admin.site.register(Review)
@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("worker", "employer", "agreed_wage", "status", "created_at")
    list_filter = ("status",)