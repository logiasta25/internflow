# Internship Management Platform

A complete Internship Management Platform built with **Django** and **Oracle DBMS**.

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 4.2 (Python) |
| Database | Oracle XE (via `oracledb`) |
| Frontend | Django Templates + Vanilla CSS |
| Auth | Django built-in authentication |
| File Uploads | Pillow + Django MEDIA settings |

---

## Prerequisites

- Python 3.10+
- Oracle Database XE (or Standard/Enterprise)
- Oracle Instant Client (for thick mode, optional)
- pip

---

## Oracle Database Setup

### 1. Install Oracle XE

Download and install [Oracle Database XE](https://www.oracle.com/database/technologies/appdev/xe.html).

Default connection details:
- **Host**: localhost
- **Port**: 1521
- **SID/Service**: xe

### 2. Create a Database User

Connect as `SYS` or `SYSTEM` using SQL*Plus or SQL Developer:

```sql
CREATE USER internship_user IDENTIFIED BY your_password;
GRANT CONNECT, RESOURCE, CREATE SESSION TO internship_user;
GRANT UNLIMITED TABLESPACE TO internship_user;
```

### 3. Update settings.py

Edit `internship_platform/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.oracle',
        'NAME': 'localhost:1521/xe',
        'USER': 'internship_user',       # <-- your DB user
        'PASSWORD': 'your_password',     # <-- your DB password
    }
}
```

---

## Installation & Running

### 1. Clone / Navigate to the project

```bash
cd internship_platform
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run migrations

```bash
python manage.py migrate
```

### 4. Create a superuser (Admin)

```bash
python manage.py createsuperuser
```

### 5. Start the development server

```bash
python manage.py runserver
```

Visit **http://127.0.0.1:8000/**

---

## Platform URLs

| URL | Description |
|-----|-------------|
| `/` | Homepage |
| `/register/` | Student registration |
| `/login/` | Login |
| `/logout/` | Logout |
| `/internships/` | Internship listings (search & filter) |
| `/internships/<id>/` | Internship detail + application |
| `/internships/<id>/apply/` | Submit application |
| `/application/<id>/withdraw/` | Withdraw application |
| `/dashboard/` | Student application dashboard |
| `/profile/` | Student profile management |
| `/admin/` | Django admin panel |
| `/admin-dashboard/` | Custom stats page (admin only) |

---

## Additional Management Commands

### Deactivate expired internships

Run this daily (or via a cron job / task scheduler):

```bash
python manage.py deactivate_expired
```

This marks all internships whose `last_date` has passed as `is_active=False`.

---

## Email Notifications

Email are printed to the console (development mode). Look for output in the terminal after an admin changes an application status.

To configure real email, update `settings.py`:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your@email.com'
EMAIL_HOST_PASSWORD = 'your_password'
```

---

## User Roles

| Role | Access |
|------|--------|
| **Admin** (superuser/staff) | Django Admin panel, Custom admin dashboard, all operations |
| **Student** (regular user) | Register, browse, apply, dashboard, profile |
