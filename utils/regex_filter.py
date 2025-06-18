# utils/regex_filter.py

import re

# Regex pattern for Indian number plates
INDIAN_PLATE_REGEX = r"^[A-Z]{2}[0-9]{2}[A-Z]{1,2}[0-9]{4}$"

def is_valid_plate(plate):
    """
    Returns True if the plate matches Indian number plate format.
    """
    plate = plate.upper().replace(" ", "").strip()  # Normalize
    return re.match(INDIAN_PLATE_REGEX, plate) is not None
