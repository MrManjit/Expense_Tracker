# Expense Tracker

A modern, professional expense tracking application built with Django, featuring a beautiful glassmorphism UI design.

## Features

- 📊 **Dashboard**: Overview of expenses with filtering by year/month
- ➕ **Quick Add**: Fast expense entry with category and subcategory selection
- 📱 **Responsive**: Works perfectly on all devices
- 🎨 **Modern UI**: Glassmorphism design with smooth animations
- 🔐 **User Authentication**: Secure login system
- 📈 **Statistics**: Monthly and yearly expense summaries
- 📋 **Expense Lists**: View and manage all expenses

## 🚀 Deployment to Render

### Prerequisites
- A [Render](https://render.com) account
- Your project pushed to GitHub

### Step-by-Step Deployment

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Create New Web Service on Render**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository

3. **Configure Build Settings**
   - **Name**: `expense-tracker` (or your preferred name)
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
   - **Start Command**: `python manage.py runserver 0.0.0.0:$PORT`

4. **Environment Variables**
   Add these environment variables in Render:
   ```
   DJANGO_SETTINGS_MODULE=Expense_Tracker.settings
   DEBUG=False
   SECRET_KEY=your-super-secret-key-here
   ALLOWED_HOSTS=your-app-name.onrender.com
   ```

5. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment to complete
   - Your app will be live at `https://your-app-name.onrender.com`

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/expense-tracker.git
   cd expense-tracker
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Open http://127.0.0.1:8000 in your browser
   - Login with your superuser credentials

## 📁 Project Structure

```
expense-tracker/
├── Expense_Tracker/          # Django project settings
│   ├── settings.py          # Main settings (configured for production)
│   ├── urls.py             # URL configuration
│   └── wsgi.py             # WSGI application
├── ledger/                  # Main Django app
│   ├── models.py           # Database models
│   ├── views.py            # View logic
│   ├── forms.py            # Django forms
│   ├── templates/          # HTML templates
│   └── static/             # CSS, JS, images
├── requirements.txt         # Python dependencies
├── runtime.txt             # Python version for Render
├── render.yaml             # Render deployment config
└── README.md              # This file
```

## 🛠️ Technologies Used

- **Backend**: Django 4.2
- **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript
- **Database**: SQLite (production-ready)
- **Styling**: Custom CSS with glassmorphism effects
- **Icons**: Font Awesome 6
- **Deployment**: Render (free tier)

## 📧 Support

If you encounter any issues during deployment, please check:
- Render build logs for error messages
- Django settings configuration
- Environment variables setup

## 📄 License

This project is open source and available under the [MIT License](LICENSE).