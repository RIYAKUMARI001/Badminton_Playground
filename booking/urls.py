from django.urls import path

from . import views

app_name = "booking"

urlpatterns = [
    path("", views.home, name="home"),
    path("availability/", views.availability_view, name="availability"),
    path("book/", views.create_booking_view, name="create_booking"),
    path("bookings/", views.booking_history_view, name="booking_history"),
    path("pricing-quote/", views.pricing_quote_view, name="pricing_quote"),

    # Auth
    path("signup/", views.signup_view, name="signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
]