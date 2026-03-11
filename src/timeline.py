import matplotlib.colors as mcolors
from datetime import datetime

def create_timeline(images_data):
    dated_images = [img for img in images_data if img.get("datetime")]
    dated_images.sort(key=lambda x: x["datetime"])

    dates = [img["datetime"].split(" ")[0] for img in dated_images]
    dates_set = sorted(list(set(dates)))

    colors = list(mcolors.TABLEAU_COLORS.values())
    date_color = {date: colors[i % len(colors)] for i, date in enumerate(dates_set)}
    date_color['None'] = '#000000'

    brands = [img.get("camera_make") for img in images_data if img.get("camera_make")]
    brands_set = set(brands)
    icons = ["fa-solid fa-mobile", "fa-regular fa-mobile", "fa-light fa-mobile", "fa-thin fa-mobile"]
    brands_icon = {brand: icons[i % len(icons)] for i, brand in enumerate(brands_set)}

    html = """
    <style>
        .timeline-box { transition: all 0.3s ease; }
        .timeline-box:hover { background-color: #f9f9f9 !important; box-shadow: 0 4px 8px rgba(0,0,0,0.2) !important; }
        .extra-details { display: none; } 
        .timeline-box:hover .extra-details { display: block; } 
    </style>
    """

    html += '<div style="position:relative; padding:20px; overflow:auto;">'
    html += '<div style="position:absolute; left:50%; width:2px; height:100%; background:#333; transform:translateX(-50%);"></div>'

    previous_time = None

    for i, img in enumerate(dated_images):
        current_time = datetime.strptime(img["datetime"], "%Y-%m-%d %H:%M:%S")

        if previous_time:
            diff = current_time - previous_time
            if diff.total_seconds() >= 12 * 3600:
                html += f'<div style="text-align:center; color:#e74c3c; font-weight:bold; margin: 20px 0; clear:both;">&#9888; פער של {diff.total_seconds() / 3600:.1f} שעות</div>'

        side = "left" if i % 2 == 0 else "right"
        date_key = img["datetime"].split(" ")[0]
        make = img.get("camera_make")
        icon_class = brands_icon.get(make, "fa-solid fa-image")

        box_style = f"width:40%; padding:15px; border-radius:8px; background:#ffffff; box-shadow: 0 2px 4px rgba(0,0,0,0.1); position:relative; float:{side}; clear:both; margin-bottom:20px; box-sizing: border-box;"

        if side == "left":
            box_style += " margin-right:55%; text-align:right;"
        else:
            box_style += " margin-left:55%; text-align:left;"

        html += f'''
        <div class="timeline-box" style="{box_style}">
            <strong style="color: {date_color.get(date_key, "#000")}; font-size:1.1em;">{img["datetime"]}</strong><br>
            <span style="color:#555;">{img.get("filename", "Unknown")}</span><br>
            <small style="color:#888;"><i class="{icon_class}"></i> {img.get("camera_model", "Unknown")}</small>

            <div class="extra-details">
                <hr>
                <span>{img.get("camera_make", "Unknown")}, {img.get("filename", "Unknown")}</span>
            </div>
        </div>'''

        previous_time = current_time

    html += '<div style="clear:both;"></div></div>'
    return html