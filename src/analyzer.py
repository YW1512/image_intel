import math
from datetime import datetime


def distance(p1: list[float], p2: list[float]):
    lat1, lon1 = map(math.radians, p1)
    lat2, lon2 = map(math.radians, p2)

    a = math.sin((lat2-lat1)/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin((lon2-lon1)/2)**2
    return 6371 * 2 * math.asin(math.sqrt(a))


def basic_stats(images_data):
    """Returns basic stats: total images, GPS count, unique cameras, date range."""

    image_count = len(images_data)

    images_w_gps = 0
    for img in images_data:
        if img['has_gps']:
            images_w_gps += 1

    device_types = list({img['camera_model'] for img in images_data if img['camera_model']})

    date_times = [img['datetime'] for img in images_data if img['datetime']]

    date_range = None
    if date_times:
        date_times.sort()

        date_range = {
            "start": date_times[0].split(" ")[0],
            "end": date_times[-1].split(" ")[0]
        }

    return {
        "total_images": image_count,
        "images_with_gps": images_w_gps,
        "unique_cameras": device_types,
        "date_range": date_range
    }


def detect_camera_switches(images_data):
    """Detects camera switches by sorting images by time and comparing consecutive pairs."""

    sorted_images = sorted([img for img in images_data if img["datetime"]], key=lambda x: x["datetime"])

    switches = []
    for i in range(1, len(sorted_images)):
        prev_cam = sorted_images[i-1].get("camera_model")
        curr_cam = sorted_images[i].get("camera_model")
        if prev_cam and curr_cam and prev_cam != curr_cam: # בדיקה אם יש מודל בתמונה הקודמת, בתמונה הנוכחית והאם התמונה הקודמת שווה לתמונה הנוכחית, אם שווה זה אומר שלא הוחלף מכשיר.
            switches.append({
                "date": sorted_images[i]["datetime"], # מכניס למילון את התאריך והשעה של התמונה הראשונה במכשיר החדש.
                "from": prev_cam,
                "to": curr_cam
            })
    return switches


def detect_time_gaps(images_data):
    """Finds large time gaps (12+ hours) between consecutive images."""

    sorted_images = sorted([img for img in images_data if img["datetime"]], key=lambda x: x["datetime"])

    gaps = []
    for i in range(1, len(sorted_images)):
        prev_time = datetime.strptime(sorted_images[i-1]["datetime"], "%Y-%m-%d %H:%M:%S")
        curr_time = datetime.strptime(sorted_images[i]["datetime"], "%Y-%m-%d %H:%M:%S")

        diff = curr_time - prev_time
        diff_hours = diff.total_seconds() / 3600

        if diff_hours >= 12:
            gaps.append({
                "from": sorted_images[i-1]["datetime"],
                "to": sorted_images[i]["datetime"],
                "hours": round(diff_hours, 1)
            })
    return gaps


def find_close_locations(images_data):
    """Groups images that are close to each other (less than 1 km apart)."""

    gps_images = [img for img in images_data if img["has_gps"]]
    close_locations = []

    for img in gps_images:
        added = False
        point = [img["latitude"], img["longitude"]]

        for location in close_locations:
            for ref in location:
                ref_point = [ref["latitude"], ref["longitude"]]
                if distance(point, ref_point) < 1:
                    location.append(img)
                    added = True
                    break
            if added:
                break

        if not added:
            close_locations.append([img])

    return [c for c in close_locations if len(c) > 1]



def detect_revisits(images_data):
    """Finds locations the agent revisited - geographically close but far apart in time."""

    # ממיין לפי זמן, רק תמונות עם GPS ו-datetime
    sorted_images = sorted([img for img in images_data if img["has_gps"] and img["datetime"]], key=lambda x: x["datetime"])

    revisits = []

    for i in range(len(sorted_images)): # משווה כל תמונה מול כל תמונה קודמת (לא רצופה).
        for j in range(i):
            p1 = [sorted_images[i]["latitude"], sorted_images[i]["longitude"]]
            p2 = [sorted_images[j]["latitude"], sorted_images[j]["longitude"]]

            if distance(p1, p2) < 1:
                t1 = datetime.strptime(sorted_images[j]["datetime"], "%Y-%m-%d %H:%M:%S")
                t2 = datetime.strptime(sorted_images[i]["datetime"], "%Y-%m-%d %H:%M:%S")
                diff_hours = (t2 - t1).total_seconds() / 3600

                if diff_hours >= 6:
                    revisits.append({
                        "location_lat": sorted_images[i]["latitude"],
                        "location_lon": sorted_images[i]["longitude"],
                        "first_visit": sorted_images[j]["datetime"],
                        "return_visit": sorted_images[i]["datetime"]
                    })
    return revisits


def detect_movement_speed(images_data):
    """Calculates movement speed between consecutive images and estimates transport method."""

    sorted_images = sorted([img for img in images_data if img["has_gps"] and img["datetime"]], key=lambda x: x["datetime"])

    movements = []

    for i in range(1, len(sorted_images)):
        p1 = [sorted_images[i-1]["latitude"], sorted_images[i-1]["longitude"]]
        p2 = [sorted_images[i]["latitude"], sorted_images[i]["longitude"]]

        dist_km = distance(p1, p2)

        t1 = datetime.strptime(sorted_images[i-1]["datetime"], "%Y-%m-%d %H:%M:%S")
        t2 = datetime.strptime(sorted_images[i]["datetime"], "%Y-%m-%d %H:%M:%S")
        diff_hours = (t2 - t1).total_seconds() / 3600

        if diff_hours <= 0 or dist_km < 0.1: # מדלג אם אין הפרש זמן (חלוקה באפס) או אם לא זז
            continue

        speed_kmh = dist_km / diff_hours

        if speed_kmh < 7:
            transport = "רגלית"
        elif speed_kmh < 35:
            transport = "אופניים או תחבורה ציבורית"
        elif speed_kmh < 160:
            transport = "רכב"
        else:
            transport = "רכבת או טיסה"

        movements.append({
            "from": sorted_images[i-1]["filename"],
            "to": sorted_images[i]["filename"],
            "distance_km": round(dist_km, 1),
            "speed_kmh": round(speed_kmh, 1),
            "transport": transport
        })
    return movements


def detect_active_hours(images_data):
    """Identifies which hours the agent is active (morning/afternoon/evening/night)."""

    hour_counts = {"בוקר (06-12)": 0, "צהריים (12-18)": 0, "ערב (18-00)": 0, "לילה (00-06)": 0}

    for img in images_data:
        if not img["datetime"]:
            continue
        hour = int(img["datetime"].split(" ")[1].split(":")[0])

        if 6 <= hour < 12:
            hour_counts["בוקר (06-12)"] += 1
        elif 12 <= hour < 18:
            hour_counts["צהריים (12-18)"] += 1
        elif 18 <= hour < 24:
            hour_counts["ערב (18-00)"] += 1
        else:
            hour_counts["לילה (00-06)"] += 1

    return hour_counts


def most_used_camera(images_data):
    """Finds the camera model that took the most photos."""

    camera_counts = {}
    for img in images_data:
        model = img.get("camera_model")
        if model:
            if model in camera_counts:
                camera_counts[model] += 1
            else:
                camera_counts[model] = 1

    if not camera_counts:
        return None

    top_camera = max(camera_counts, key=lambda k: camera_counts[k])
    return {"camera": top_camera, "count": camera_counts[top_camera]}


def busiest_day(images_data):
    """Finds the day with the most photos taken."""

    day_counts = {}
    for img in images_data:
        if not img["datetime"]:
            continue
        day = img["datetime"].split(" ")[0]
        if day in day_counts:
            day_counts[day] += 1
        else:
            day_counts[day] = 1

    if not day_counts:
        return None

    top_day = max(day_counts, key=lambda k: day_counts[k])
    return {"date": top_day, "count": day_counts[top_day]}


def analyze(images_data):
    """
    Main function - runs all analyses and returns a combined result.
    Receives: list of dicts from extract_all
    Returns: dict with stats + list of insights
    """

    if not images_data:
        return {
            "total_images": 0,
            "images_with_gps": 0,
            "unique_cameras": [],
            "date_range": None,
            "insights": ["לא נמצאו תמונות לניתוח"]
        }

    stats = basic_stats(images_data)
    switches = detect_camera_switches(images_data)
    gaps = detect_time_gaps(images_data)
    clusters = find_close_locations(images_data)
    revisits = detect_revisits(images_data)
    movements = detect_movement_speed(images_data)
    active_hours = detect_active_hours(images_data)
    top_camera = most_used_camera(images_data)
    top_day = busiest_day(images_data)

    insights = []

    # תובנות על מכשירים
    if len(stats["unique_cameras"]) > 1:
        insights.append("נמצאו " + str(len(stats["unique_cameras"])) + " מכשירים שונים")

    # המכשיר הכי נפוץ
    if top_camera and stats["total_images"] > 1:
        insights.append("רוב התמונות צולמו ב-" + top_camera["camera"] + " (" + str(top_camera["count"]) + " תמונות)")

    # היום הכי עמוס
    if top_day and top_day["count"] > 1:
        insights.append("היום הכי פעיל: " + top_day["date"] + " עם " + str(top_day["count"]) + " תמונות")

    # מוצא את הזמן הכי פעיל
    if active_hours:
        peak_time = max(active_hours, key=lambda k: active_hours[k])
        if active_hours[peak_time] > 0:
            insights.append("עיקר הפעילות בשעות ה" + peak_time)

    # תובנות על החלפות מכשירים
    for sw in switches:
        date_part = sw["date"].split(" ")[0]
        insights.append("הסוכן החליף מכשיר ב-" + date_part + " מ-" + sw["from"] + " ל-" + sw["to"])

    # תובנות על פערי זמן
    for gap in gaps:
        insights.append("פער של " + str(gap["hours"]) + " שעות בין " + gap["from"] + " ל-" + gap["to"])

    # תובנות על ריכוזים גיאוגרפיים
    if clusters:
        insights.append("נמצאו " + str(len(clusters)) + " אזורים עם ריכוז תמונות")

    # תובנות על חזרה למיקום
    for rev in revisits:
        insights.append("הסוכן חזר למיקום (" + str(rev["location_lat"]) + ", " + str(rev["location_lon"]) + ")")

    # תובנות על תנועה ואמצעי תחבורה
    for mov in movements:
        insights.append(
            "תנועה של " + str(mov["distance_km"]) + " ק\"מ"
            + " במהירות " + str(mov["speed_kmh"]) + " קמ\"ש"
            + " - ככל הנראה " + mov["transport"]
        )

    # אם לא נמצאו תובנות מיוחדות
    if not insights:
        insights.append("לא נמצאו דפוסים חריגים")

    return {
        "total_images": stats["total_images"],
        "images_with_gps": stats["images_with_gps"],
        "unique_cameras": stats["unique_cameras"],
        "date_range": stats["date_range"],
        "insights": insights
    }


# --- נתוני בדיקה ---
fake_data = [
    {"filename": "test1.jpg", "latitude": 32.0853, "longitude": 34.7818,
     "has_gps": True, "camera_make": "Samsung", "camera_model": "Galaxy S23",
     "datetime": "2025-01-12 08:30:00"},
    {"filename": "test2.jpg", "latitude": 31.7683, "longitude": 35.2137,
     "has_gps": True, "camera_make": "Apple", "camera_model": "Galaxy S23",
     "datetime": "2025-01-13 09:00:00"},
    {"filename": "test2.jpg", "latitude": 29.7683, "longitude": 35.2137,
     "has_gps": True, "camera_make": "Apple", "camera_model": "iPhone 15 Pro",
     "datetime": "2025-01-13 09:00:00"},
    {"filename": "test2.jpg", "latitude": 30.7683, "longitude": 35.2137,
     "has_gps": True, "camera_make": "Apple", "camera_model": "iPhone 15 Pro",
     "datetime": "2025-01-13 09:00:00"}
]