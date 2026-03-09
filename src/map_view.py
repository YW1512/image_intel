"""
map_view.py - יצירת מפה אינטראקטיבית
צוות 1, זוג B

ראו docs/api_contract.md לפורמט הקלט והפלט.

=== תיקונים ===
1. חישוב מרכז המפה - היה עובר על images_data (כולל תמונות בלי GPS) במקום gps_image, נופל עם None
2. הסרת CustomIcon שלא עובד (filename זה לא נתיב שהדפדפן מכיר)
3. הסרת m.save() - לפי API contract צריך להחזיר HTML string, לא לשמור קובץ
4. הסרת fake_data מגוף הקובץ - הועבר ל-if __name__
5. תיקון color_index - היה מתקדם על כל תמונה במקום רק על מכשיר חדש
6. הוספת מקרא מכשירים
"""

import folium
from folium.map import Icon
from itertools import cycle

def sort_by_time(arr):
    """
    ממיין נתוני תמונות לפי תאריך ושעה.
    Args:
        arr: רשימת מילונים, של נתוני התמונות.

    Returns:
        איטרבל ממויין של התמונות.
    """
    return sorted(arr, key=lambda item: item.get("datetime", ''))


def create_map(images_data):
    """
    יוצר מפה אינטראקטיבית עם כל המיקומים.

    Args:
        images_data: רשימת מילונים מ-extract_all

    Returns:
        string של HTML (המפה)
    """

    images_w_gps = [img for img in images_data if img['has_gps']]

    if not images_w_gps:
        return "<h2>No GPS data found</h2>"

    c_latitude = sum(img['latitude'] for img in images_w_gps)  / len(images_w_gps)
    c_longitude = sum(img['longitude'] for img in images_w_gps) / len(images_w_gps)

    map_view = folium.Map(location=[c_latitude, c_longitude], zoom_start=8)

    color_cycle = cycle(list(Icon.color_options))

    color_map = {}
    points = []

    for image in images_w_gps:
        if image['camera_model'] not in color_map:
            color_map[image['camera_model']] = next(color_cycle)

    for image in images_w_gps:
        points.append([image['latitude'], image['longitude']])
        folium.Marker(
            location=[image['latitude'], image['longitude']],
            popup=(f'file name: {image["filename"]}\n'
                   f'date: {image["datetime"]}\n'
                   f'device: {image["camera_make"]} - {image["camera_model"]}'),
            icon = folium.Icon(color=color_map[image['camera_model']])
        ).add_to(map_view)

    folium.PolyLine(points).add_to(map_view)

    return map_view._repr_html_()




if __name__ == "__main__":
    # תיקון: fake_data הועבר לכאן מגוף הקובץ - כדי שלא ירוץ בכל import
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
    html = create_map(sort_by_time(fake_data))
    with open("test_map.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Map saved to test_map.html")
