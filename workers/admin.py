from django.contrib import admin, messages
from django.utils.html import format_html

from .models import District, Municipality, Skill, WorkerProfile

admin.site.register(District)
admin.site.register(Skill)

@admin.register(Municipality)
class MunicipalityAdmin(admin.ModelAdmin):
    list_display = ("name", "district")
    list_filter = ("district",)
    search_fields = ("name",)


@admin.register(WorkerProfile)
class WorkerProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "municipality", "ward_no", "daily_rate", "nid_status", "masked_nid")
    list_filter = ("nid_status",)
    search_fields = ("user__username",)
    readonly_fields = ("nid_photo_preview",)
    actions = ["approve_nid", "reject_nid"]

    @admin.display(description="NID number")
    def masked_nid(self, obj):
        if not obj.nid_number:
            return "-"
        return "*" * max(len(obj.nid_number) - 4, 0) + obj.nid_number[-4:]

    @admin.display(description="NID photo preview")
    def nid_photo_preview(self, obj):
        if not obj.nid_photo:
            return "-"
        return format_html('<img src="{}" style="max-width:300px;">', obj.nid_photo.url)

    @admin.action(description="Approve NID (mark as verified)")
    def approve_nid(self, request, queryset):
        approved = 0
        for profile in queryset.filter(nid_status=WorkerProfile.NIDStatus.PENDING):
            if profile.nid_number and profile.nid_photo:
                profile.nid_status = WorkerProfile.NIDStatus.VERIFIED
                profile.save(update_fields=["nid_status"])
                approved += 1

        skipped = queryset.count() - approved
        self.message_user(
            request,
            f"{approved} approved, {skipped} skipped (not pending, or no NID number or photo).",
            messages.SUCCESS if approved else messages.WARNING,
        )

    @admin.action(description="Reject NID")
    def reject_nid(self, request, queryset):
        rejected = queryset.exclude(nid_number="").update(
            nid_status=WorkerProfile.NIDStatus.REJECTED
        )
        self.message_user(request, f"{rejected} rejected.", messages.SUCCESS)