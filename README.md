# Badminton Court Booking System

This is a complete booking system for badminton courts that helps manage reservations, equipment rentals, and coach bookings - all with dynamic pricing!

## 🤔 What Problem Does This Solve?

Managing a badminton facility can be tricky. You have:
- Multiple courts (indoor/outdoor)
- Equipment to rent (rackets, shuttlecocks)
- Coaches to schedule
- Different pricing for different times/days
- Waitlists when things get busy

This system handles all of that automatically, so you can focus on running your business instead of juggling spreadsheets and phone calls.

## 👀 Quick Glimpse

Here's what the system looks like:

**Booking Interface**
<img width="1843" height="882" alt="Screenshot 2025-12-16 125150" src="https://github.com/user-attachments/assets/ab66c66e-66c0-46d0-bb66-df6ef83c2902" />

*Easy booking with clear availability and pricing*

**Booking Management**
<img width="517" height="713" alt="Screenshot 2025-12-16 125103" src="https://github.com/user-attachments/assets/742da845-595b-40a4-8479-769b741b1cb6" />
<img width="1215" height="777" alt="Screenshot 2025-12-16 125203" src="https://github.com/user-attachments/assets/e3b7b34f-fafe-4f60-9459-eacbd8aca4aa" />
<img width="1238" height="748" alt="Screenshot 2025-12-16 125253" src="https://github.com/user-attachments/assets/3e74dd4f-8925-4f2d-ae6a-a34d7e20ed53" />
<img width="1344" height="391" alt="Screenshot 2025-12-16 125346" src="https://github.com/user-attachments/assets/04231e9f-1049-40cd-bf4e-f4255e82c32b" />

## ✨ Key Features

### For Customers
- **Easy Booking**: Pick a date, time, and court - that's it!
- **See Prices Upfront**: Know exactly what you'll pay before booking
- **Book Extras**: Add equipment or a coach to your booking
- **View History**: See all your past bookings

### For Admins
- **Smart Admin Panel**: Beautiful, easy-to-use dashboard
- **Manage Everything**: Courts, equipment, coaches, pricing rules
- **See Revenue**: Track income and popular time slots
- **Handle Waitlists**: System automatically adds people when spots open

## 🚀 Quick Start

1. **Install Python** (3.8 or newer)
2. **Download this project**
3. **Open terminal/command prompt** in the project folder
4. **Run these commands**:

```bash
# Install required packages
pip install -r requirements.txt

# Set up the database
python manage.py migrate

# Add sample data (courts, equipment, etc.)
python manage.py seed_data

# Create your admin account
python manage.py createsuperuser

# Start the server
python manage.py runserver
```

5. **Open your browser** to:
   - Main site: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/

## 📁 Project Structure

```
badminton-booking/
├── badminton_booking/      # Main settings and configuration
├── booking/                # Core booking functionality
│   ├── models.py           # Database structure (courts, bookings, etc.)
│   ├── views.py            # Page logic (what happens when you visit a page)
│   ├── forms.py            # User input forms
│   ├── admin.py            # Admin panel configuration
│   └── templates/          # Page templates
├── static/                 # Images, CSS, JavaScript
├── templates/              # Base page layouts
├── manage.py               # Django command tool
└── requirements.txt        # Required packages
```

## 🛠️ What We've Improved

### Admin Panel
We made the admin panel look amazing and work better:
- Beautiful green theme that matches the booking site
- Easy search for finding bookings, users, or equipment
- Edit multiple items at once (like changing prices for all courts)
- Dashboard showing recent bookings and revenue
- Better organization of all data

### Booking System
- Cleaner forms for customers
- Better error messages when something goes wrong
- Smoother booking process
- Clear pricing breakdown

### Technical Improvements
- Better code organization
- More reliable booking system
- Proper waitlist handling
- Flexible pricing rules

## 🎯 How Pricing Works

The system calculates prices automatically:
1. **Base Price**: Court hourly rate + coach hourly rate
2. **Dynamic Adjustments**: 
   - Weekend bookings cost more
   - Peak hours (6-9 PM) cost more
   - Indoor courts cost more than outdoor
3. **Equipment**: Added rental fees
4. **Final Total**: All combined with clear breakdown

Admins can easily change these rules anytime without touching code!

Built with:
- Django (web framework)
- Bootstrap (styling)
- Font Awesome (icons)
