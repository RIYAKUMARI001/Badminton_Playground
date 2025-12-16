from datetime import date, time, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from booking.models import Coach, CoachAvailability, Court, Equipment, PricingRule


class Command(BaseCommand):
    help = "Seed initial data for courts, equipment, coaches, and pricing rules"

    def handle(self, *args, **options):
        # Update or create courts
        courts_data = [
            {"name": "Court 1", "court_type": Court.INDOOR, "hourly_rate": 400},
            {"name": "Court 2", "court_type": Court.INDOOR, "hourly_rate": 400},
            {"name": "Court 3", "court_type": Court.OUTDOOR, "hourly_rate": 300},
            {"name": "Court 4", "court_type": Court.OUTDOOR, "hourly_rate": 300},
        ]
        courts = []
        for data in courts_data:
            court, created = Court.objects.update_or_create(
                name=data["name"],
                defaults={"court_type": data["court_type"], "hourly_rate": data["hourly_rate"], "is_active": True}
            )
            courts.append(court)
        self.stdout.write(self.style.SUCCESS(f"Created/Updated {len(courts)} courts"))

        # Update or create equipment
        equipment_data = [
            {"name": "Racket", "total_quantity": 20, "rental_price": 50},
            {"name": "Shoes", "total_quantity": 10, "rental_price": 30},
        ]
        equipment = []
        for data in equipment_data:
            eq, created = Equipment.objects.update_or_create(
                name=data["name"],
                defaults={"total_quantity": data["total_quantity"], "rental_price": data["rental_price"], "is_active": True}
            )
            equipment.append(eq)
        self.stdout.write(self.style.SUCCESS(f"Created {len(equipment)} equipment types"))

        coaches = [
            Coach.objects.create(name="Coach A", hourly_rate=500),
            Coach.objects.create(name="Coach B", hourly_rate=600),
            Coach.objects.create(name="Coach C", hourly_rate=700),
        ]
        self.stdout.write(self.style.SUCCESS(f"Created {len(coaches)} coaches"))

        start_date = timezone.localdate()
        for d in range(0, 7):
            day = start_date + timedelta(days=d)
            for coach in coaches:
                CoachAvailability.objects.create(
                    coach=coach,
                    date=day,
                    start_time=time(8, 0),
                    end_time=time(20, 0),
                )
        self.stdout.write(self.style.SUCCESS("Created coach availability for next 7 days"))

        PricingRule.objects.create(
            name="Peak hours 6-9 PM",
            rule_type=PricingRule.PEAK_HOUR,
            percentage_adjustment=30,
            peak_start=time(18, 0),
            peak_end=time(21, 0),
        )
        PricingRule.objects.create(
            name="Weekend premium",
            rule_type=PricingRule.WEEKEND,
            percentage_adjustment=20,
        )
        PricingRule.objects.create(
            name="Indoor court premium",
            rule_type=PricingRule.INDOOR_PREMIUM,
            percentage_adjustment=15,
        )
        self.stdout.write(self.style.SUCCESS("Created pricing rules"))


