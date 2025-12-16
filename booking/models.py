from __future__ import annotations

from datetime import time

from django.contrib.auth import get_user_model
from django.db import models, transaction

User = get_user_model()


class Court(models.Model):
    INDOOR = "indoor"
    OUTDOOR = "outdoor"
    COURT_TYPE_CHOICES = [
        (INDOOR, "Indoor"),
        (OUTDOOR, "Outdoor"),
    ]

    name = models.CharField(max_length=100, unique=True)
    court_type = models.CharField(max_length=20, choices=COURT_TYPE_CHOICES)
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, default=400.00)
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name


class Equipment(models.Model):
    name = models.CharField(max_length=100, unique=True)
    total_quantity = models.PositiveIntegerField()
    rental_price = models.DecimalField(max_digits=8, decimal_places=2, default=50.00)
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name


class Coach(models.Model):
    name = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2)
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name


class CoachAvailability(models.Model):
    coach = models.ForeignKey(Coach, on_delete=models.CASCADE, related_name="availabilities")
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        unique_together = ("coach", "date", "start_time", "end_time")

    def __str__(self) -> str:
        return f"{self.coach} {self.date} {self.start_time}-{self.end_time}"


class PricingRule(models.Model):
    PEAK_HOUR = "peak_hour"
    WEEKEND = "weekend"
    INDOOR_PREMIUM = "indoor_premium"

    RULE_TYPE_CHOICES = [
        (PEAK_HOUR, "Peak hour"),
        (WEEKEND, "Weekend"),
        (INDOOR_PREMIUM, "Indoor premium"),
    ]

    name = models.CharField(max_length=100)
    rule_type = models.CharField(max_length=50, choices=RULE_TYPE_CHOICES)
    # Percentage adjustment, e.g. 20 means +20%, -10 means -10%
    percentage_adjustment = models.DecimalField(max_digits=5, decimal_places=2)
    is_active = models.BooleanField(default=True)

    peak_start = models.TimeField(null=True, blank=True)
    peak_end = models.TimeField(null=True, blank=True)

    def __str__(self) -> str:
        return self.name


class Booking(models.Model):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (CONFIRMED, "Confirmed"),
        (CANCELLED, "Cancelled"),
    ]

    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="bookings")
    customer_name = models.CharField(max_length=100)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    court = models.ForeignKey(Court, on_delete=models.PROTECT)
    coach = models.ForeignKey(Coach, null=True, blank=True, on_delete=models.PROTECT)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=CONFIRMED)

    def __str__(self) -> str:
        return f"Booking {self.id} - {self.customer_name}"


class BookingEquipment(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="equipment_items")
    equipment = models.ForeignKey(Equipment, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()

    class Meta:
        unique_together = ("booking", "equipment")

    def __str__(self) -> str:
        return f"{self.equipment} x{self.quantity}"


class WaitlistEntry(models.Model):
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    court = models.ForeignKey(Court, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    customer_name = models.CharField(max_length=100)
    notified = models.BooleanField(default=False)

    class Meta:
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"Waitlist {self.customer_name} {self.date} {self.start_time}"


def is_weekend(date) -> bool:
    return date.weekday() >= 5


def is_peak_hour(rule: PricingRule, start: time, end: time) -> bool:
    if not rule.peak_start or not rule.peak_end:
        return False
    return not (end <= rule.peak_start or start >= rule.peak_end)


def calculate_base_price(court: Court, coach: Coach | None, duration_hours: float) -> float:
    court_base_rate = float(court.hourly_rate)
    coach_rate = float(coach.hourly_rate) if coach else 0
    return duration_hours * (court_base_rate + coach_rate)


def apply_pricing_rules(
    date,
    start: time,
    end: time,
    court: Court,
    base_price: float,
) -> float:
    rules = PricingRule.objects.filter(is_active=True)
    price = base_price
    for rule in rules:
        applies = False
        if rule.rule_type == PricingRule.WEEKEND and is_weekend(date):
            applies = True
        elif rule.rule_type == PricingRule.PEAK_HOUR and is_peak_hour(rule, start, end):
            applies = True
        elif rule.rule_type == PricingRule.INDOOR_PREMIUM and court.court_type == Court.INDOOR:
            applies = True

        if applies:
            price *= 1 + float(rule.percentage_adjustment) / 100.0
    return round(price, 2)


def get_equipment_availability(equipment: Equipment, date, start: time, end: time) -> int:
    booked_qty = (
        BookingEquipment.objects.filter(
            booking__date=date,
            booking__start_time__lt=end,
            booking__end_time__gt=start,
            booking__status=Booking.CONFIRMED,
            equipment=equipment,
        ).aggregate(models.Sum("quantity"))["quantity__sum"]
        or 0
    )
    return max(equipment.total_quantity - booked_qty, 0)


def is_court_available(court: Court, date, start: time, end: time) -> bool:
    overlap = Booking.objects.filter(
        court=court,
        date=date,
        start_time__lt=end,
        end_time__gt=start,
        status=Booking.CONFIRMED,
    ).exists()
    return not overlap


def is_coach_available(coach: Coach, date, start: time, end: time) -> bool:
    if not coach:
        return True
    # must have an availability window that covers this slot
    has_availability = CoachAvailability.objects.filter(
        coach=coach,
        date=date,
        start_time__lte=start,
        end_time__gte=end,
    ).exists()
    if not has_availability:
        return False
    overlap = Booking.objects.filter(
        coach=coach,
        date=date,
        start_time__lt=end,
        end_time__gt=start,
        status=Booking.CONFIRMED,
    ).exists()
    return not overlap


@transaction.atomic
def create_booking_atomic(
    *,
    user: User | None,
    customer_name: str,
    date,
    start,
    end,
    court: Court,
    coach: Coach | None,
    equipment_quantities: dict[int, int],
    allow_waitlist: bool = True,
):
    court = Court.objects.select_for_update().get(pk=court.pk)

    if not is_court_available(court, date, start, end) or not is_coach_available(coach, date, start, end):
        if allow_waitlist:
            WaitlistEntry.objects.create(
                date=date,
                start_time=start,
                end_time=end,
                court=court,
                customer_name=customer_name,
            )
        return None

    equipment_objs = {
        eq.id: Equipment.objects.select_for_update().get(pk=eq_id)
        for eq_id in equipment_quantities.keys()
        for eq in [Equipment(id=eq_id)]
    }

    for eq_id, qty in equipment_quantities.items():
        available = get_equipment_availability(equipment_objs[eq_id], date, start, end)
        if qty > available:
            if allow_waitlist:
                WaitlistEntry.objects.create(
                    date=date,
                    start_time=start,
                    end_time=end,
                    court=court,
                    customer_name=customer_name,
                )
            return None

    duration_hours = (end.hour + end.minute / 60) - (start.hour + start.minute / 60)
    base_price = calculate_base_price(court, coach, duration_hours)
    total_price = apply_pricing_rules(date, start, end, court, base_price)

    booking = Booking.objects.create(
        user=user,
        customer_name=customer_name,
        date=date,
        start_time=start,
        end_time=end,
        court=court,
        coach=coach,
        total_price=total_price,
        status=Booking.CONFIRMED,
    )
    for eq_id, qty in equipment_quantities.items():
        if qty > 0:
            BookingEquipment.objects.create(
                booking=booking,
                equipment=equipment_objs[eq_id],
                quantity=qty,
            )
    return booking


