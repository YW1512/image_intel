from datetime import datetime


def create_report(images_data, map_html, timeline_html, analysis):
    """
    Assembles all components into a single HTML report.
    Receives:
        - images_data: list of dicts from extract_all
        - map_html: HTML string from create_map
        - timeline_html: HTML string from create_timeline
        - analysis: dict from analyze
    Returns: full HTML string
    """

    now = datetime.now().strftime("%d/%m/%Y %H:%M")

    insights_html = ""
    for insight in analysis.get("insights", []):
        insights_html += "<li>" + insight + "</li>"

    cameras_html = ""
    for cam in analysis.get("unique_cameras", []):
        cameras_html += '<span class="badge">' + cam + '</span> '

    date_range = analysis.get("date_range")
    date_range_html = ""
    if date_range:
        date_range_html = '''
        <div class="stat-card">
            <div class="stat-number">''' + date_range["start"] + '''</div>
            <div>תאריך התחלה</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">''' + date_range["end"] + '''</div>
            <div>תאריך סיום</div>
        </div>'''

    images_table_html = ""
    for img in images_data:
        gps_text = ""
        if img.get("has_gps"):
            gps_text = str(round(img["latitude"], 4)) + ", " + str(round(img["longitude"], 4))
        else:
            gps_text = "אין GPS"

        cam_text = img.get("camera_model") or "לא ידוע"
        dt_text = img.get("datetime") or "לא ידוע"

        images_table_html += '''
        <tr>
            <td>''' + img.get("filename", "") + '''</td>
            <td>''' + dt_text + '''</td>
            <td>''' + cam_text + '''</td>
            <td>''' + gps_text + '''</td>
        </tr>'''

    html = '''<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>Image Intel Report</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
            direction: rtl;
        }
        .header {
            background: #1B4F72;
            color: white;
            padding: 30px;
            border-radius: 10px;
            text-align: center;
        }
        .header h1 { margin: 0 0 10px 0; font-size: 2em; }
        .header p { margin: 0; color: #AED6F1; }
        .section {
            background: white;
            padding: 20px;
            margin: 20px 0;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .section h2 {
            color: #1B4F72;
            border-bottom: 2px solid #AED6F1;
            padding-bottom: 10px;
        }
        .stats {
            display: flex;
            gap: 20px;
            justify-content: center;
            flex-wrap: wrap;
        }
        .stat-card {
            background: #E8F4FD;
            padding: 15px 25px;
            border-radius: 8px;
            text-align: center;
            min-width: 100px;
        }
        .stat-number {
            font-size: 2em;
            font-weight: bold;
            color: #1B4F72;
        }
        .badge {
            background: #2E86AB;
            color: white;
            padding: 5px 10px;
            border-radius: 15px;
            margin: 3px;
            display: inline-block;
            font-size: 0.9em;
        }
        ul { line-height: 2; }
        li { margin-bottom: 5px; }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 10px;
            text-align: right;
        }
        th {
            background: #1B4F72;
            color: white;
        }
        tr:nth-child(even) { background: #f9f9f9; }
        .footer {
            text-align: center;
            color: #888;
            margin-top: 30px;
            padding: 20px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Image Intel Report</h1>
        <p>''' + now + ''' :נוצר ב</p>
    </div>

    <div class="section">
        <h2>סיכום</h2>
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">''' + str(analysis.get("total_images", 0)) + '''</div>
                <div>תמונות</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">''' + str(analysis.get("images_with_gps", 0)) + '''</div>
                <div>עם GPS</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">''' + str(len(analysis.get("unique_cameras", []))) + '''</div>
                <div>מכשירים</div>
            </div>
            ''' + date_range_html + '''
        </div>
    </div>

    <div class="section">
        <h2>תובנות מרכזיות</h2>
        <ul>''' + insights_html + '''</ul>
    </div>

    <div class="section">
        <h2>מפה</h2>
        ''' + (map_html or "<p>אין נתוני GPS להצגה</p>") + '''
    </div>

    <div class="section">
        <h2>ציר זמן</h2>
        ''' + (timeline_html or "<p>אין נתוני זמן להצגה</p>") + '''
    </div>

    <div class="section">
        <h2>מכשירים</h2>
        ''' + (cameras_html or "<p>לא זוהו מכשירים</p>") + '''
    </div>

    <div class="section">
        <h2>פירוט תמונות</h2>
        <table>
            <tr>
                <th>קובץ</th>
                <th>תאריך ושעה</th>
                <th>מכשיר</th>
                <th>מיקום</th>
            </tr>
            ''' + images_table_html + '''
        </table>
    </div>

    <div class="footer">
        Image Intel | האקתון 2025
    </div>
</body>
</html>'''

    return html

if __name__ == "__main__":
    from extractor import extract_all
    from analyzer import analyze
    from map_view import create_map
    from timeline import create_timeline

    images_data = extract_all("../images")

    analysis = analyze(images_data)
    map_html = create_map(images_data)
    timeline_html = create_timeline(images_data)

    html = create_report(images_data, map_html, timeline_html, analysis)

    with open("test_report.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("Report saved to test_report.html")
