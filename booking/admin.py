from django.contrib import admin

from .models import (
    Booking,
    BookingEquipment,
    Coach,
    CoachAvailability,
    Court,
    Equipment,
    PricingRule,
    WaitlistEntry,
)


@admin.register(Court)
class CourtAdmin(admin.ModelAdmin):
    list_display = ("name", "court_type", "is_active")
    list_filter = ("court_type", "is_active")


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ("name", "total_quantity", "is_active")


@admin.register(Coach)
class CoachAdmin(admin.ModelAdmin):
    list_display = ("name", "hourly_rate", "is_active")


@admin.register(CoachAvailability)
class CoachAvailabilityAdmin(admin.ModelAdmin):
    list_display = ("coach", "date", "start_time", "end_time")
    list_filter = ("coach", "date")


class BookingEquipmentInline(admin.TabularInline):
    model = BookingEquipment
    extra = 0


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("id", "customer_name", "date", "start_time", "end_time", "court", "coach", "status")
    list_filter = ("status", "court", "coach", "date")
    inlines = [BookingEquipmentInline]


@admin.register(PricingRule)
class PricingRuleAdmin(admin.ModelAdmin):
    list_display = ("name", "rule_type", "percentage_adjustment", "is_active")
    list_filter = ("rule_type", "is_active")


@admin.register(WaitlistEntry)
class WaitlistAdmin(admin.ModelAdmin):
    list_display = ("customer_name", "date", "start_time", "court", "created_at", "notified")


