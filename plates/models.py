from django.db import models

class DetectedPlate(models.Model):
    plate_text = models.CharField(max_length=20)
    timestamp = models.DateTimeField(auto_now_add=True)
    vehicle_type = models.CharField(max_length=20, blank=True, null=True)

    car_image_path = models.CharField(max_length=255)  # Path to image in /cropped_cars
    car_video_path = models.CharField(max_length=255)  # Path to video in /car_videos

    def __str__(self):
        return self.plate_text
