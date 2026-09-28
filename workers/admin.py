from django.contrib import admin
from .models import District, Municipality, Skill, WorkerProfile

# Register your models here.

admin.site.register(District)
admin.site.register(Municipality)
admin.site.register(Skill)


@admin.register(WorkerProfile)
class WorkerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'daily_rate', 'municipality', 'ward_no', 'nid_status')
    list_filter = ('nid_status', 'municipality__district')
    search_fields = ('user__username', 'nid_number')