# Badminton Court Booking System

A comprehensive web application for booking badminton courts, equipment, and coaches with dynamic pricing rules. Built with Django and Bootstrap.

## 🎯 Features

### Core Functionality
- **Multi-resource Booking**: Reserve courts, rent equipment, and book coaches in a single transaction
- **Dynamic Pricing Engine**: Configurable pricing rules that adjust costs based on:
  - Time of day (peak hours)
  - Day of week (weekend premiums)
  - Court type (indoor/outdoor)
- **Real-time Availability**: Instant checking of court, equipment, and coach availability
- **Waitlist System**: Automatic enrollment in waitlists when resources are unavailable
- **Booking Management**: View and manage your booking history

### User Experience
- **Responsive Design**: Mobile-friendly interface with modern UI components
- **Interactive Booking**: Visual calendar and time slot selection
- **Live Pricing Quotes**: Real-time price calculation as you configure your booking
- **User Authentication**: Secure signup and login system
- **Intuitive Navigation**: Clean, easy-to-use interface

### Admin Capabilities
- **Resource Management**: Add/edit courts, equipment, coaches via Django admin
- **Pricing Configuration**: Create and modify pricing rules without code changes
- **Booking Oversight**: View and manage all bookings
- **Data Insights**: Access to booking statistics and reports
- **Enhanced Admin Interface**: Improved Django admin with search, filters, and inline editing

## 🏗️ Architecture

### Database Design
The system uses a normalized relational model with these key entities:

- **Court**: Indoor/outdoor badminton courts with hourly rates
- **Equipment**: Rentable items (rackets, shuttlecocks) with inventory tracking
- **Coach**: Professional coaches with hourly rates and availability windows
- **Booking**: Core reservation entity linking users to resources
- **PricingRule**: Configurable rules that modify base prices
- **WaitlistEntry**: Queue system for oversubscribed time slots

### Pricing Engine
The pricing system calculates costs dynamically:
1. Compute base price from court rate + coach rate × duration
2. Apply active pricing rules (peak hour, weekend, indoor premium)
3. Add equipment rental fees
4. Return final total with detailed breakdown

Rules compound multiplicatively, allowing flexible pricing strategies.

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- pip package manager
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd badminton-booking-system
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run database migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create a superuser account**
   ```bash
   python manage.py createsuperuser
   ```

6. **Seed initial data**
   ```bash
   python manage.py seed_data
   ```

7. **Start the development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   - Main site: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/

### Project Structure
```
badminton-booking/
├── badminton_booking/      # Django project settings
├── booking/                # Main application
│   ├── models.py           # Data models
│   ├── views.py            # Request handlers
│   ├── forms.py            # Form definitions
│   ├── admin.py            # Admin configuration
│   └── templates/          # HTML templates
├── static/                 # CSS, JavaScript, images
├── templates/              # Base templates
├── manage.py               # Django CLI utility
└── requirements.txt        # Python dependencies
```

## 🔧 Key Enhancements

### Admin Panel Improvements
- Enhanced Django admin with custom list displays for better data visualization
- Added search functionality across all models for quick data lookup
- Implemented inline editing for frequently changed fields
- Added filters for efficient data management
- Improved usability with better form layouts and navigation

### Frontend Enhancements
- Refined booking interface with improved user experience
- Enhanced form validation and error handling
- Better responsive design for mobile devices
- Improved visual feedback for user actions

## 🛠️ Configuration

### Environment Variables
- `SECRET_KEY`: Django secret key (change in production)
- `DEBUG`: Toggle debug mode (True/False)
- `DATABASE_URL`: Database connection string (optional)

### Admin Configuration
Access the Django admin panel to configure:
- Courts and their types/rates
- Equipment inventory
- Coach profiles and availability
- Pricing rules and adjustments
- Active bookings and waitlist entries

## 🧪 Testing

Run the test suite with:
```bash
python manage.py test
```

## 📦 Deployment

### Production Checklist
- [ ] Change `SECRET_KEY`
- [ ] Set `DEBUG = False`
- [ ] Configure production database
- [ ] Set up static file serving
- [ ] Configure email backend
- [ ] Set up SSL/HTTPS

### Heroku Deployment
1. Create a new Heroku app
2. Connect to your GitHub repository
3. Add Python buildpack
4. Set environment variables
5. Deploy branch

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Django framework
- Bootstrap CSS library
- Font Awesome icons