from django.urls import path
from . import views

app_name = 'members'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('members/', views.member_list, name='member_list'),
    path('members/<int:member_id>/', views.member_detail, name='member_detail'),
    path('members/<int:member_id>/card/', views.member_card_pdf, name='member_card_pdf'),  # NEW
    path('reports/members/', views.members_pdf, name='members_pdf'),
    path('reports/prayers/', views.prayer_requests_pdf, name='prayer_requests_pdf'),
    path('reports/birthdays/', views.birthdays_pdf, name='birthdays_pdf'),
]