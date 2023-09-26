from django.urls import path
from .views import RobotCreateView, generate_excel

urlpatterns = [
    path('create-robot/', RobotCreateView.as_view(), name='create_robot'),
    path('generate-excel/', generate_excel, name='generate_excel'),
]