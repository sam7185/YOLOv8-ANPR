# utils/api_platerecognizer.py

import requests
import os

PLATERECOGNIZER_API_TOKEN = "Token 9ca257db77f16745ffde4e79e28e63c906bbe821"
PLATERECOGNIZER_ENDPOINT = "https://api.platerecognizer.com/v1/plate-reader/"
REGIONS = ["in"]  # Change this if your dataset is from a different country

def extract_plate_text(image_path):
    if not os.path.exists(image_path):
        print(f"[ERROR] Image not found: {image_path}")
        return None

    with open(image_path, 'rb') as fp:
        response = requests.post(
            PLATERECOGNIZER_ENDPOINT,
            data=dict(regions=REGIONS),
            files=dict(upload=fp),
            headers={'Authorization': PLATERECOGNIZER_API_TOKEN}
        )

    if response.status_code == 200:
        result = response.json()
        if result['results']:
            best_match = result['results'][0]
            plate = best_match['plate']
            box = best_match['box']
            score = best_match['score']
            return {
                'plate': plate,
                'score': score
            }
        else:
            return None
    else:
        print(f"[ERROR] API call failed: {response.status_code}")
        return None
