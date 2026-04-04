from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('internships/', views.internship_list, name='internship_list'),
    path('internships/<int:pk>/', views.internship_detail, name='internship_detail'),
    path('internships/<int:pk>/apply/', views.apply_internship, name='apply_internship'),
    path('application/<int:pk>/withdraw/', views.withdraw_application, name='withdraw_application'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # Custom Admin Application URLs
    path('admin-dashboard/applications/', views.admin_application_list, name='admin_application_list'),
    path('admin-dashboard/applications/<int:pk>/update/', views.admin_application_update, name='admin_application_update'),
    
    # Custom Admin Internship URLs
    path('admin-dashboard/internships/', views.admin_internship_list, name='admin_internship_list'),
    path('admin-dashboard/internships/create/', views.admin_internship_create, name='admin_internship_create'),
    path('admin-dashboard/internships/<int:pk>/update/', views.admin_internship_update, name='admin_internship_update'),
    path('admin-dashboard/internships/<int:pk>/delete/', views.admin_internship_delete, name='admin_internship_delete'),
    
    # Custom Admin Company URLs
    path('admin-dashboard/companies/', views.admin_company_list, name='admin_company_list'),
    path('admin-dashboard/companies/create/', views.admin_company_create, name='admin_company_create'),
    path('admin-dashboard/companies/<int:pk>/update/', views.admin_company_update, name='admin_company_update'),
    path('admin-dashboard/companies/<int:pk>/delete/', views.admin_company_delete, name='admin_company_delete'),
]
