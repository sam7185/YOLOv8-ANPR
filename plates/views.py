import os
from django.shortcuts import render, redirect
from django.conf import settings
from django.core.files.storage import default_storage
from django.utils import timezone
from main import run_pipeline
from django.http import HttpResponse
from .models import DetectedPlate
from django.db.models import Q
import csv
from main import run_pipeline  # We'll define this to call main.py logic

VIDEO_DIR = os.path.join(settings.BASE_DIR, 'video_input')
OUTPUT_VIDEO_PATH = os.path.join(settings.BASE_DIR, 'output_video', 'annotated_output.mp4')

def home(request):
    return render(request, 'plates/home.html')

def upload_video(request):
    if request.method == 'POST':
        video_file = request.FILES['video']
        entry_y = int(request.POST.get('entry_line_y'))
        exit_y = int(request.POST.get('exit_line_y'))

        # Ensure video_input directory exists
        os.makedirs(VIDEO_DIR, exist_ok=True)

        # Delete old videos
        for f in os.listdir(VIDEO_DIR):
            os.remove(os.path.join(VIDEO_DIR, f))

        # Save new video
        filename = f"{timezone.now().strftime('%Y%m%d%H%M%S')}_{video_file.name}"
        video_path = os.path.join(VIDEO_DIR, filename)
        with open(video_path, 'wb+') as dest:
            for chunk in video_file.chunks():
                dest.write(chunk)

        # Call YOLO pipeline directly
        run_pipeline(
            video_path=video_path,
            output_video_path=OUTPUT_VIDEO_PATH,
            entry_line_y=entry_y,
            exit_line_y=exit_y
        )

        return redirect('plates_page')  # Plates page we'll build next

    return redirect('home')

def plates_page(request):
    # Get filter parameters
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    plate_number = request.GET.get("plate_number")
    vehicle_type = request.GET.get("vehicle_type")

    # Build query
    filters = Q()
    if start_date:
        filters &= Q(timestamp__date__gte=start_date)
    if end_date:
        filters &= Q(timestamp__date__lte=end_date)
    if plate_number:
        filters &= Q(plate_number__icontains=plate_number)
    if vehicle_type:
        filters &= Q(vehicle_type__icontains=vehicle_type)

    # Get filtered data
    plates = DetectedPlate.objects.filter(filters).order_by("-timestamp")

    return render(request, "plates/plates.html", {"plates": plates})

def download_csv(request):
    plates = DetectedPlate.objects.all().order_by("-timestamp")

    # Create CSV response
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="detected_plates.csv"'

    writer = csv.writer(response)
    writer.writerow(["Plate Number", "Vehicle Type", "Timestamp", "Image Path", "Video Path"])

    for plate in plates:
        writer.writerow([
            plate.plate_number,
            plate.vehicle_type,
            plate.timestamp,
            os.path.basename(plate.car_image_path),
            os.path.basename(plate.car_video_path),
        ])

    return response
