from django.contrib import admin
from django.contrib.auth.models import User
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta

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
    list_display = ("name", "court_type", "hourly_rate", "is_active")
    list_filter = ("court_type", "is_active")
    search_fields = ("name",)
    list_editable = ("is_active", "hourly_rate")


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ("name", "total_quantity", "rental_price", "is_active")
    search_fields = ("name",)
    list_editable = ("is_active", "rental_price", "total_quantity")


@admin.register(Coach)
class CoachAdmin(admin.ModelAdmin):
    list_display = ("name", "hourly_rate", "is_active")
    search_fields = ("name",)
    list_editable = ("is_active", "hourly_rate")


@admin.register(CoachAvailability)
class CoachAvailabilityAdmin(admin.ModelAdmin):
    list_display = ("coach", "date", "start_time", "end_time")
    list_filter = ("coach", "date")
    search_fields = ("coach__name",)


class BookingEquipmentInline(admin.TabularInline):
    model = BookingEquipment
    extra = 0


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("id", "customer_name", "date", "start_time", "end_time", "court", "coach", "status", "total_price")
    list_filter = ("status", "court", "coach", "date")
    search_fields = ("customer_name", "id")
    inlines = [BookingEquipmentInline]
    readonly_fields = ("created_at", "total_price")


@admin.register(PricingRule)
class PricingRuleAdmin(admin.ModelAdmin):
    list_display = ("name", "rule_type", "percentage_adjustment", "is_active")
    list_filter = ("rule_type", "is_active")
    list_editable = ("is_active", "percentage_adjustment")


@admin.register(WaitlistEntry)
class WaitlistAdmin(admin.ModelAdmin):
    list_display = ("customer_name", "date", "start_time", "court", "created_at", "notified")
    list_filter = ("court", "date", "notified")
    search_fields = ("customer_name",)


# Custom admin dashboard view
class CustomAdminSite(admin.AdminSite):
    site_header = "Badminton Booking Administration"
    site_title = "Badminton Booking Admin"
    index_title = "Dashboard"
    
    def index(self, request, extra_context=None):
        # Get dashboard data
        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())
        month_start = today.replace(day=1)
        
        # Recent bookings
        recent_bookings = Booking.objects.select_related('court').order_by('-created_at')[:5]
        
        # User statistics
        user_count = User.objects.count()
        active_users_today = User.objects.filter(last_login__date=today).count()
        
        # Revenue data
        revenue_today = Booking.objects.filter(
            date=today, 
            status=Booking.CONFIRMED
        ).aggregate(total=Sum('total_price'))['total'] or 0
        
        revenue_week = Booking.objects.filter(
            date__gte=week_start,
            date__lte=today,
            status=Booking.CONFIRMED
        ).aggregate(total=Sum('total_price'))['total'] or 0
        
        revenue_month = Booking.objects.filter(
            date__gte=month_start,
            date__lte=today,
            status=Booking.CONFIRMED
        ).aggregate(total=Sum('total_price'))['total'] or 0
        
        # System status
        court_count = Court.objects.filter(is_active=True).count()
        equipment_count = Equipment.objects.filter(is_active=True).count()
        coach_count = Coach.objects.filter(is_active=True).count()
        waitlist_count = WaitlistEntry.objects.count()
        
        extra_context = extra_context or {}
        extra_context.update({
            'booking_list': recent_bookings,
            'user_count': user_count,
            'active_users_today': active_users_today,
            'revenue_today': revenue_today,
            'revenue_week': revenue_week,
            'revenue_month': revenue_month,
            'court_count': court_count,
            'equipment_count': equipment_count,
            'coach_count': coach_count,
            'waitlist_count': waitlist_count,
        })
        
        return super().index(request, extra_context)


# Create custom admin site instance
custom_admin_site = CustomAdminSite(name='custom_admin')


# Register models with custom admin site
custom_admin_site.register(Court, CourtAdmin)
custom_admin_site.register(Equipment, EquipmentAdmin)
custom_admin_site.register(Coach, CoachAdmin)
custom_admin_site.register(CoachAvailability, CoachAvailabilityAdmin)
custom_admin_site.register(Booking, BookingAdmin)
custom_admin_site.register(PricingRule, PricingRuleAdmin)
custom_admin_site.register(WaitlistEntry, WaitlistAdmin)