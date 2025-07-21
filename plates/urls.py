from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload_video, name='upload_video'),
    path('plates/', views.plates_page, name='plates_page'),
    path("download_csv/", views.download_csv, name="download_csv"),
     path('download/image/<int:plate_id>/', views.download_car_image, name='download_car_image'),
    path('download/video/<int:plate_id>/', views.download_car_video, name='download_car_video'),
]
