from math import degrees
from tkinter import image_names

from PIL import Image
from PIL.ExifTags import TAGS
from pathlib import Path


"""
extractor.py - שליפת EXIF מתמונות
צוות 1, זוג A

ראו docs/api_contract.md לפורמט המדויק של הפלט.

"""

def dms_to_decimal(dms_tuple, ref):
    degrees=float(dms_tuple[0])
    minutes=float(dms_tuple[1])
    seconds=float(dms_tuple[2])

    decimal=degrees+(minutes/60)+(seconds/3600)
    if ref in ["s","w",b"s",b"w"]:
        decimal=-decimal
    return decimal

def has_gps(data):
    return "GPSInfo" in data and len(data["GPSInfo"])>0


def latitude(data: dict):
    gps_info=data.get("GPSInfo")
    if gps_info and 2 in gps_info and 1 in gps_info:
        return dms_to_decimal(gps_info[2],gps_info[1])
    return None

def longitude(data: dict):
    gps_info=data.get("GPSInfo")
    if gps_info and 4 in gps_info and 3 in gps_info:
        return dms_to_decimal(gps_info[4],gps_info[3])
    return None

def datatime(data: dict):
    dt_str=data.get("DateTime")
    if dt_str:
        data_part, time_part=dt_str.split(' ')
        data_part=data_part.replace(':','-')
        return f"{data_part} {time_part}"
    return None

def camera_make(data: dict):
    make=data.get("Make")
    if make:
        return str(make).strip("\x00")
    return None

def camera_model(data: dict):
    model=data.get("Model")
    if model:
        return str(model).strip("\x00")



def extract_metadata(image_path):
    """
    שולף EXIF מתמונה בודדת.

    Args:
        image_path: נתיב לקובץ תמונה

    Returns:
        dict עם: filename, datetime, latitude, longitude,
              camera_make, camera_model, has_gps
    """
    path = Path(image_path)

    # תיקון: טיפול בתמונה בלי EXIF - בלי זה, exif.items() נופל עם AttributeError
    try:
        img = Image.open(image_path)
        exif = img._getexif()
    except Exception:
        exif = None

    if exif is None:
        return {
            "filename": path.name,
            "datetime": None,
            "latitude": None,
            "longitude": None,
            "camera_make": None,
            "camera_model": None,
            "has_gps": False
        }

    data = {}
    for tag_id, value in exif.items():
        tag = TAGS.get(tag_id, tag_id)
        data[tag] = value

    # תיקון: הוסר print(data) שהיה כאן - הדפיס את כל ה-EXIF הגולמי על כל תמונה

    exif_dict = {
        "filename": path.name,
        "datetime": datatime(data),
        "latitude": latitude(data),
        "longitude": longitude(data),
        "camera_make": camera_make(data),
        "camera_model": camera_model(data),
        "has_gps": has_gps(data) and (longitude(data) != None) and (latitude(data) != None)
    }
    return exif_dict


def extract_all(folder_path):
    """
    שולף EXIF מכל התמונות בתיקייה.

    Args:
        folder_path: נתיב לתיקייה

    Returns:
        list של dicts (כמו extract_metadata)
    """
    results=[]
    path=Path(folder_path)
    for image_file in path.glob("*"):
        if image_file.suffix.lower() in [".jpg",".jpeg"]:
            metadata=extract_metadata(str(image_file))
            results.append(metadata)

    return results
