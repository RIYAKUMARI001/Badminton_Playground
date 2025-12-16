from __future__ import annotations

from datetime import datetime

from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from .forms import AvailabilitySearchForm, BookingForm, SignUpForm
from .models import (
    Booking,
    Coach,
    Court,
    Equipment,
    apply_pricing_rules,
    calculate_base_price,
    get_equipment_availability,
    is_coach_available,
    is_court_available,
    create_booking_atomic,
)


def home(request: HttpRequest) -> HttpResponse:
    return redirect("booking:availability")


def availability_view(request: HttpRequest) -> HttpResponse:
    form = AvailabilitySearchForm(request.GET or None)
    slots = []
    
    # Get filter parameters
    court_type_filter = request.GET.get("court_type", "")
    search_query = request.GET.get("search", "").strip()
    
    if form.is_valid():
        date = form.cleaned_data["date"]
        courts = Court.objects.filter(is_active=True)
        
        # Apply court type filter
        if court_type_filter and court_type_filter.lower() in ["indoor", "outdoor"]:
            courts = courts.filter(court_type=court_type_filter.lower())
        
        # Apply search filter (by court name)
        if search_query:
            courts = courts.filter(name__icontains=search_query)
        
        for hour in range(6, 22):
            start = datetime.combine(date, datetime.min.time()).replace(hour=hour).time()
            end = datetime.combine(date, datetime.min.time()).replace(hour=hour + 1).time()
            for court in courts:
                court_available = is_court_available(court, date, start, end)
                slots.append(
                    {
                        "date": date,
                        "start": start,
                        "end": end,
                        "court": court,
                        "available": court_available,
                    }
                )
    
    return render(
        request,
        "booking/availability.html",
        {
            "form": form,
            "slots": slots,
            "court_type_filter": court_type_filter,
            "search_query": search_query,
        },
    )


def _extract_equipment_quantities(form: BookingForm) -> dict[int, int]:
    equipment_quantities: dict[int, int] = {}
    for field_name, value in form.cleaned_data.items():
        if field_name.startswith("equipment_") and value:
            equipment_id = int(field_name.split("_", 1)[1])
            equipment_quantities[equipment_id] = value
    return equipment_quantities


def create_booking_view(request: HttpRequest) -> HttpResponse:
    if not request.user.is_authenticated:
        return redirect("booking:login")
    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            customer_name = form.cleaned_data["customer_name"]
            date = form.cleaned_data["date"]
            start = form.cleaned_data["start_time"]
            end = form.cleaned_data["end_time"]
            court: Court = form.cleaned_data["court"]
            coach: Coach | None = form.cleaned_data["coach"]
            equipment_quantities = _extract_equipment_quantities(form)

            booking = create_booking_atomic(
                user=request.user if request.user.is_authenticated else None,
                customer_name=customer_name,
                date=date,
                start=start,
                end=end,
                court=court,
                coach=coach,
                equipment_quantities=equipment_quantities,
                allow_waitlist=True,
            )
            if booking:
                return redirect(reverse("booking:booking_history"))
            return render(
                request,
                "booking/booking_form.html",
                {
                    "form": form,
                    "error": "Selected slot or equipment not available. You have been added to the waitlist.",
                },
            )
    else:
        initial = {}
        date = request.GET.get("date")
        start = request.GET.get("start")
        end = request.GET.get("end")
        court_id = request.GET.get("court")
        if date and start and end and court_id:
            initial["date"] = date
            initial["start_time"] = start
            initial["end_time"] = end
            initial["court"] = court_id
        form = BookingForm(initial=initial)

    return render(request, "booking/booking_form.html", {"form": form})


def booking_history_view(request: HttpRequest) -> HttpResponse:
    if not request.user.is_authenticated:
        return redirect("booking:login")
    bookings = Booking.objects.filter(user=request.user).order_by("-created_at")[:50]
    return render(request, "booking/booking_history.html", {"bookings": bookings})


def pricing_quote_view(request: HttpRequest) -> JsonResponse:
    try:
        date_str = request.GET.get("date")
        start_str = request.GET.get("start_time")
        end_str = request.GET.get("end_time")
        court_id = request.GET.get("court")
        coach_id = request.GET.get("coach")
        if not (date_str and start_str and end_str and court_id):
            raise ValueError("Missing parameters")
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
        start = datetime.strptime(start_str, "%H:%M").time()
        end = datetime.strptime(end_str, "%H:%M").time()
        court = Court.objects.get(pk=court_id)
        coach = Coach.objects.get(pk=coach_id) if coach_id else None
        duration_hours = (end.hour + end.minute / 60) - (start.hour + start.minute / 60)
        
        # Calculate base prices separately
        court_base_rate = float(court.hourly_rate) * duration_hours
        coach_rate = (float(coach.hourly_rate) * duration_hours) if coach else 0
        base_price = court_base_rate + coach_rate

        # Calculate equipment fees
        equipment_fee = 0
        for field_name, value in request.GET.items():
            if field_name.startswith("equipment_") and value:
                try:
                    eq_id = int(field_name.replace("equipment_", ""))
                    equipment = Equipment.objects.get(pk=eq_id)
                    qty = int(value) if value.isdigit() else 1
                    equipment_fee += float(equipment.rental_price) * qty
                except (ValueError, Equipment.DoesNotExist):
                    pass

        # Apply pricing rules and track breakdown
        from .models import PricingRule, is_weekend, is_peak_hour
        
        price = base_price + equipment_fee
        rules_applied = []
        
        active_rules = PricingRule.objects.filter(is_active=True)
        for rule in active_rules:
            applies = False
            if rule.rule_type == PricingRule.WEEKEND and is_weekend(date):
                applies = True
            elif rule.rule_type == PricingRule.PEAK_HOUR and is_peak_hour(rule, start, end):
                applies = True
            elif rule.rule_type == PricingRule.INDOOR_PREMIUM and court.court_type == Court.INDOOR:
                applies = True

            if applies:
                adjustment = price * (float(rule.percentage_adjustment) / 100.0)
                price += adjustment
                rules_applied.append({
                    "name": rule.name,
                    "amount": round(adjustment, 2),
                })

        total = round(price, 2)

        equipment_breakdown = []
        for equipment in Equipment.objects.filter(is_active=True):
            available = get_equipment_availability(equipment, date, start, end)
            equipment_breakdown.append(
                {
                    "id": equipment.id,
                    "name": equipment.name,
                    "available": available,
                }
            )

        return JsonResponse(
            {
                "base_price": round(base_price, 2),
                "total_price": total,
                "equipment": equipment_breakdown,
                "breakdown": {
                    "base_price": round(court_base_rate, 2),
                    "coach_fee": round(coach_rate, 2) if coach else 0,
                    "equipment_fee": round(equipment_fee, 2),
                    "rules": rules_applied,
                },
            }
        )
    except Exception as exc:  # noqa: BLE001
        return JsonResponse({"error": str(exc)}, status=400)


def signup_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("booking:availability")
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("booking:availability")
    else:
        form = SignUpForm()
    return render(request, "accounts/signup.html", {"form": form})


def login_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("booking:availability")
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("booking:availability")
    else:
        form = AuthenticationForm()
    return render(request, "accounts/login.html", {"form": form})


def logout_view(request: HttpRequest) -> HttpResponse:
    """
    Simple logout that also works via GET and sends user back to availability page.
    """
    logout(request)
    return redirect("booking:availability")