import json, os, glob
from datetime import datetime

# ============================================================
# TEST OVERRIDE — set TEST_MONTH to any full month name to
# preview that month's content (e.g. "March", "April").
# Set to None to use the real current month.
# ============================================================
TEST_MONTH = None  # e.g. TEST_MONTH = "March"

# Always resolve files relative to this script's location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def generate_html():
    # Read event data
    with open(os.path.join(SCRIPT_DIR, 'events_data.json'), 'r', encoding='utf-8') as f:
        data = json.load(f)

    church = data['church_info']
    messages = data['rotating_messages']
    tabs = data['sidebar_tabs']

    if TEST_MONTH:
        current_month = TEST_MONTH
        current_date = f"{TEST_MONTH} {datetime.now().year}  [TEST]"
    else:
        current_month = datetime.now().strftime('%B')
        current_date = datetime.now().strftime('%B %Y')

    # Sermons are always from the previous month (relative to whatever month is active)
    _month_names = ["January","February","March","April","May","June",
                    "July","August","September","October","November","December"]
    sermon_month = _month_names[_month_names.index(current_month) - 1]

    
    # Helper function to split text into vertical letters
    def vertical_text(word):
        return ''.join(f'<span>{letter}</span>' for letter in word.upper())
    
    def format_date_with_ordinal(date):
        if isinstance(date, int):
            if 11 <= date <= 13:
                suffix = "th"
            else:
                suffix = {1: "st", 2: "nd", 3: "rd"}.get(date % 10, "th")
            return f"{date}{suffix}"
        return str(date)

    def get_slideshow_images():
        image_folder = os.path.join(SCRIPT_DIR, 'slideshow_folder')
        if not os.path.exists(image_folder):
            print(f"Warning: '{image_folder}' folder not found. Creating it.")
            os.makedirs(image_folder)
            return []

        # Get the pictures
        image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.webp']
        image_files = []
        for ext in image_extensions:
            image_files.extend(glob.glob(os.path.join(image_folder, ext)))

        # Convert paths to relative paths for the html
        return [os.path.basename(img) for img in image_files]

    slideshow_images = get_slideshow_images()

    current_birthdays = tabs.get('birthdays', {}).get(current_month, [])
    current_anniversaries = tabs.get('anniversaries', {}).get(current_month, [])

    html_parts = []

    # Create HTML
    html_parts.append(f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{church['name']}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        html, body {{
            height: 100%;
            overflow: hidden;
            margin: 0;
            padding: 0;
        }}

        /* Make sure active content section scrolls properly */
        .content-section.active {{
            height: 100%;
            overflow-y: visible;
        }}

        body {{
            font-family: 'Georgia', serif;
            height: 100vh;
            overflow: hidden;
        }}

        .container {{
            display: flex;
            height: 100vh;
        }}

        /* ============================================
           LEFT CONTAINER - Content + Tabs
           ============================================ */
        .left-container {{
            width: 50%;
            background: #ecf0f1;
            display: flex;
            overflow: hidden;
            order: 1;  /* Show first on desktop (source has it second) */
        }}

        /* Custom icon images */
        .icon-image {{
            width: 48px;
            height: 48px;
            object-fit: contain;
            display: block;
            margin: 0 auto;
        }}

        .tab-buttons {{
            width: 80px;
            background: linear-gradient(135deg, rgba(0, 229, 86), rgba(0, 120, 168));
            display: flex;
            flex-direction: column;
            padding: 15px 0;
            gap: 8px;
            position: sticky;
            top: 0;
            height: 100vh;
            overflow-y: auto;
            scrollbar-width: none;
            -ms-overflow-style: none;
        }}

        .tab-buttons::-webkit-scrollbar{{
            display: none;
        }}
        
        .tab-button {{
            background: #2c3e50;
            color: white;
            border: none;
            padding: 20px 10px;
            margin: 0 10px;
            cursor: pointer;
            border-radius: 8px;
            transition: all 0.3s;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }}
        
        .tab-button:hover {{
            background: #1a252f;
            transform: scale(1.05);
        }}
        
        .tab-button.active {{
            background: #3498db;
        }}
        
        .tab-icon {{
            font-size: 26px;
            margin-bottom: 8px;
        }}
        
        .tab-text {{
            display: flex;
            flex-direction: column;
            align-items: center;
            font-size: 14px;
            font-weight: bold;
            letter-spacing: 1px;
            line-height: 1.4;
        }}
        
        .tab-text span {{
            display: block;
        }}
        
        .content-area {{
            flex: 1;
            background: white;
            padding: 40px;
            overflow-y: auto;
            height: 100vh;
            scrollbar-width: none;
            -ms-overflow-style: none;
        }}
        
        .content-section {{
            display: none;
        }}
        
        .content-section.active {{
            display: block;
            animation: slideIn 0.3s ease;
        }}
        
        @keyframes slideIn {{
            from {{ opacity: 0; transform: translateX(-20px); }}
            to {{ opacity: 1; transform: translateX(0); }}
        }}
        
        .section-title {{
            font-size: 36px;
            color: #2c3e50;
            border-bottom: 4px solid #3498db;
            padding-bottom: 15px;
            margin-bottom: 30px;
            font-weight: bold;
        }}
        
        /* Rotating message box */
        .rotating-message {{
            background: linear-gradient(135deg, rgba(0, 229, 86), rgba(0, 120, 168));
            color: white;
            padding: 40px;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 30px;
            box-shadow: 0 8px 20px rgba(0,0,0,0.15);
            min-height: 200px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}
        
        .message {{
            display: none;
        }}
        
        .message.active {{
            display: block;
            animation: fadeIn 1s ease-in-out;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        .message-title {{
            font-size: 32px;
            margin-bottom: 10px;
            font-weight: bold;
        }}
        
        .message-scripture {{
            font-size: 18px;
            font-style: italic;
            opacity: 0.95;
            margin-bottom: 20px;
        }}
        
        .message-text {{
            font-size: 20px;
            line-height: 1.7;
        }}
        
        .welcome-text {{
            font-size: 18px;
            line-height: 1.8;
            color: #555;
        }}

        /* Date display in section title */
        .section-title {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 36px;
            color: #2c3e50;
            border-bottom: 4px solid #3498db;
            padding-bottom: 15px;
            margin-bottom: 30px;
            font-weight: bold;
        }}

        .date-badge {{
            font-size: 18px;
            color: #3498db;
            background: #e8f4fc;
            padding: 5px 15px;
            border-radius: 30px;
            font-weight: normal;
            display: inline-flex;
            align-items: center;
            gap: 5px;
        }}

    /* ============================================
   MISSIONS TAB STYLES
   ============================================ */

        .missions-container {{
            display: flex;
            flex-direction: column;
            gap: 30px;
        }}

        /* Video Section */
        .video-section {{
            background: #f8f9fa;
            border-radius: 16px;
            padding: 25px;
            border-left: 6px solid #e74c3c;
            box-shadow: 0 8px 20px rgba(0,0,0,0.05);
        }}

        .video-header {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 20px;
        }}

        .video-icon {{
            font-size: 32px;
        }}

        .video-title {{
            font-size: 20px;
            font-weight: bold;
            color: #2c3e50;
            margin: 0;
        }}

        .video-container {{
            background: #2c3e50;
            border-radius: 12px;
            padding: 40px 20px;
            text-align: center;
            color: white;
            margin-bottom: 15px;
        }}

        .video-placeholder {{
            font-size: 48px;
            margin-bottom: 15px;
        }}

        .video-link {{
            display: inline-block;
            background: #e74c3c;
            color: white;
            padding: 12px 25px;
            border-radius: 50px;
            text-decoration: none;
            font-weight: bold;
            transition: transform 0.2s, box-shadow 0.2s;
            margin-top: 15px;
        }}

        .video-link:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 15px rgba(231, 76, 60, 0.3);
        }}

        .video-meta {{
            display: flex;
            justify-content: space-between;
            color: #7f8c8d;
            font-size: 14px;
            margin-top: 10px;
        }}

        /* Local Video Player */
        .local-video-player {{
            width: 100%;
            border-radius: 12px;
            background: #2c3e50;
            margin-bottom: 15px;
        }}

        /* Featured Mission Card */
        .mission-card {{
            background: white;
            border-radius: 16px;
            padding: 25px;
            box-shadow: 0 8px 20px rgba(0,0,0,0.05);
            border-top: 6px solid #3498db;
        }}

        .mission-header {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 20px;
        }}

        .mission-icon {{
            font-size: 32px;
        }}

        .mission-title {{
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
            margin: 0;
        }}

        .mission-location {{
            font-size: 16px;
            color: #7f8c8d;
            margin-left: auto;
        }}

        .mission-message {{
            font-size: 18px;
            line-height: 1.7;
            color: #444;
            font-style: italic;
            background: #f9f9f9;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 20px;
            border-left: 4px solid #3498db;
        }}

        .mission-author {{
            font-size: 16px;
            font-weight: bold;
            color: #2c3e50;
            text-align: right;
            margin-bottom: 25px;
        }}

        /* Prayer Points */
        .prayer-section {{
            background: #e8f4fc;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 25px;
        }}

        .prayer-header {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 15px;
            font-size: 18px;
            font-weight: bold;
            color: #2c3e50;
        }}

        .prayer-list {{
            list-style: none;
            padding: 0;
            margin: 0;
        }}

        .prayer-list li {{
            padding: 10px 0 10px 35px;
            position: relative;
            font-size: 16px;
            color: #2c3e50;
            border-bottom: 1px solid rgba(52, 152, 219, 0.2);
        }}

        .prayer-list li:last-child {{
            border-bottom: none;
        }}

        .prayer-list li:before {{
            content: "🙏";
            position: absolute;
            left: 5px;
            top: 8px;
            font-size: 16px;
        }}

        /* Progress Bar */
        .progress-section {{
            background: #f9f9f9;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 15px;
        }}

        .progress-label {{
            display: flex;
            justify-content: space-between;
            font-size: 16px;
            color: #2c3e50;
            margin-bottom: 8px;
            font-weight: bold;
        }}

        .progress-container {{
            width: 100%;
            height: 24px;
            background: #e0e0e0;
            border-radius: 12px;
            overflow: hidden;
            margin: 10px 0;
        }}

        .progress-bar {{
            height: 100%;
            background: linear-gradient(90deg, #27ae60, #2ecc71);
            border-radius: 12px;
            transition: width 0.5s ease;
            display: flex;
            align-items: center;
            justify-content: flex-end;
            padding-right: 10px;
            color: white;
            font-size: 12px;
            font-weight: bold;
        }}

        .progress-percent {{
            font-size: 18px;
            font-weight: bold;
            color: #27ae60;
            text-align: right;
        }}

        /* Support Section */
        .support-section {{
            background: linear-gradient(135deg, rgb(52, 152, 219), rgb(41, 128, 185));
            color: white;
            border-radius: 16px;
            padding: 25px;
            margin-top: 10px;
        }}

        .support-header {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 20px;
            font-size: 22px;
            font-weight: bold;
        }}

        .support-list {{
            list-style: none;
            padding: 0;
            margin: 0 0 20px 0;
        }}

        .support-list li {{
            padding: 12px 0 12px 35px;
            position: relative;
            font-size: 16px;
            border-bottom: 1px solid rgba(255,255,255,0.2);
        }}

        .support-list li:last-child {{
            border-bottom: none;
        }}

        .support-list li:before {{
            content: "•";
            color: white;
            font-weight: bold;
            font-size: 20px;
            position: absolute;
            left: 8px;
            top: 10px;
        }}

        .support-email {{
            color: white;
            text-decoration: underline;
            font-weight: bold;
        }}

        /* No Mission Message */
        .no-mission {{
            background: #f9f9f9;
            border: 2px dashed #3498db;
            border-radius: 16px;
            padding: 50px 30px;
            text-align: center;
            color: #7f8c8d;
        }}

        .no-mission span {{
            font-size: 60px;
            display: block;
            margin-bottom: 20px;
            opacity: 0.5;
        }}

        .no-mission h3 {{
            font-size: 24px;
            color: #2c3e50;
            margin-bottom: 15px;
        }}

        .no-mission p {{
            font-size: 16px;
            line-height: 1.6;
            max-width: 500px;
            margin: 0 auto 20px;
        }}

        .no-mission .prayer-suggestions {{
            background: #e8f4fc;
            border-radius: 12px;
            padding: 20px;
            margin-top: 25px;
            text-align: left;
            display: inline-block;
        }}

        .no-mission .prayer-suggestions h4 {{
            color: #2c3e50;
            margin-bottom: 10px;
        }}

        .no-mission .prayer-suggestions ul {{
            list-style: none;
            padding: 0;
        }}

        .no-mission .prayer-suggestions li {{
            padding: 5px 0 5px 25px;
            position: relative;
        }}

        .no-mission .prayer-suggestions li:before {{
            content: "🙏";
            position: absolute;
            left: 0;
            top: 5px;
        }}
        
        /* Event items */
        .event-item {{
            background: #f8f9fa;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 10px;
            border-left: 5px solid #3498db;
            transition: transform 0.2s;
        }}
        
        .event-item:hover {{
            transform: translateX(5px);
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }}

        .event-item--permanent {{
            border-left-color: #e74c3c;
        }}
        
        .event-title {{
            font-size: 22px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 12px;
        }}
        
        .event-detail {{
            font-size: 16px;
            margin: 6px 0;
            color: #555;
        }}
        
        .event-description {{
            margin-top: 10px;
            font-style: italic;
            color: #666;
        }}

        /* ============================================
        INSPIRE TAB STYLES
        ============================================ */

        .inspire-container {{
            display: flex;
            flex-direction: column;
            gap: 30px;
        }}

        /* Verse of the Week Card */
        .verse-card {{
            background: white;
            padding: 30px;
            border-radius: 16px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.15);
            border-left: 8px solid rgba(0, 229, 86);
            position: relative;
            overflow: hidden;
        }}

        .verse-card::before {{
            content: "“";
            font-size: 120px;
            position: absolute;
            top: -20px;
            left: 10px;
            opacity: 0.1;
            color: white;
            font-family: Georgia, serif;
        }}

        .verse-icon {{
            font-size: 32px;
            margin-bottom: 15px;
        }}

        .verse-text {{
            font-size: 26px;
            font-style: italic;
            line-height: 1.5;
            margin-bottom: 15px;
            font-weight: 500;
            position: relative;
            z-index: 2;
        }}

        .verse-reference {{
            font-size: 18px;
            opacity: 0.9;
            margin-bottom: 20px;
            letter-spacing: 1px;
        }}

        .verse-theme {{
            display: inline-block;
            background: rgba(52, 45, 45, 0.15);
            padding: 6px 20px;
            border-radius: 40px;
            font-size: 14px;
            font-weight: bold;
            border: 1px solid rgba(255,255,255,0.3);
            margin-bottom: 15px;
        }}

        /* Pastor's Comment (Optional) */
        .pastor-comment {{
            background: rgba(255,255,255,0.1);
            padding: 18px 22px;
            border-radius: 12px;
            margin-top: 20px;
            border-left: 4px solid #f1c40f;
        }}

        .pastor-comment-text {{
            font-size: 17px;
            line-height: 1.6;
            font-style: italic;
            margin-bottom: 8px;
        }}

        .pastor-comment-author {{
            font-size: 15px;
            font-weight: bold;
            opacity: 0.9;
            display: flex;
            align-items: center;
            gap: 6px;
        }}

        .pastor-comment-author:before {{
            content: "—";
            margin-right: 4px;
        }}

        /* Testimony Section */
        .testimony-section {{
            background: white;
            border-radius: 16px;
            padding: 25px;
            box-shadow: 0 8px 20px rgba(0,0,0,0.06);
            border-top: 6px solid rgba(0, 229, 86);
        }}

        .testimony-header {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 20px;
        }}

        .testimony-icon {{
            font-size: 28px;
        }}

        .testimony-title {{
            font-size: 22px;
            font-weight: bold;
            color: #2c3e50;
            margin: 0;
        }}

        /* SCROLLBOX - Fixed height with custom scrollbar */
        .testimony-scrollbox {{
            max-height: 250px;
            overflow-y: auto;
            padding-right: 15px;
            margin-bottom: 5px;
        }}

        /* Custom scrollbar */
        .testimony-scrollbox::-webkit-scrollbar {{
            width: 6px;
        }}

        .testimony-scrollbox::-webkit-scrollbar-track {{
            background: #f0f0f0;
            border-radius: 10px;
        }}

        .testimony-scrollbox::-webkit-scrollbar-thumb {{
            background: rgba(0, 229, 86);
            border-radius: 10px;
        }}

        .testimony-scrollbox::-webkit-scrollbar-thumb:hover {{
            background: #8e44ad;
        }}

        /* Testimony Card */
        .testimony-card {{
            background: #f9f9f9;
            border-radius: 12px;
            padding: 20px;
            border-left: 5px solid rgba(0, 229, 86);
        }}

        .testimony-quote {{
            font-size: 20px;
            color: rgba(0, 229, 86);
            margin-bottom: 10px;
            opacity: 0.7;
        }}

        .testimony-text {{
            font-size: 16px;
            line-height: 1.7;
            color: #444;
            margin-bottom: 20px;
            white-space: pre-line;
        }}

        .testimony-author {{
            font-weight: bold;
            color: #2c3e50;
            font-size: 16px;
            margin-bottom: 5px;
        }}

        .testimony-date {{
            font-size: 13px;
            color: #7f8c8d;
            margin-bottom: 10px;
        }}

        .testimony-verse {{
            font-size: 14px;
            color: #9b59b6;
            font-style: italic;
            padding-top: 10px;
            border-top: 1px solid #e0e0e0;
        }}

        /* No testimony message */
        .no-testimony {{
            background: #f9f9f9;
            border: 2px dashed rgb(217, 52, 54);
            border-radius: 12px;
            padding: 40px;
            text-align: center;
            color: #7f8c8d;
        }}

        .no-testimony span {{
            font-size: 40px;
            display: block;
            margin-bottom: 10px;
        }}

        .no-testimony p {{
            font-size: 16px;
        }}

        /* Share Your Story CTA */
        .share-cta {{
            background: linear-gradient(135deg, rgb(52, 152, 219), rgb(41, 128, 185));
            color: white;
            padding: 25px;
            border-radius: 16px;
            text-align: center;
            box-shadow: 0 8px 20px rgba(52, 152, 219, 0.2);
        }}

        .share-cta h3 {{
            font-size: 22px;
            font-weight: bold;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }}

        .share-cta p {{
            font-size: 16px;
            line-height: 1.6;
            margin-bottom: 20px;
            opacity: 0.95;
        }}

        .share-email {{
            display: inline-block;
            background: white;
            color: #2c3e50;
            padding: 12px 25px;
            border-radius: 50px;
            font-weight: bold;
            font-size: 16px;
            text-decoration: none;
            transition: transform 0.2s, box-shadow 0.2s;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }}

        .share-email:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 15px rgba(0,0,0,0.15);
        }}


        /* Sermons section */
        .sermons-container {{
            display: flex;
            flex-direction: column;
            gap: 25px;
            margin-top: 10px;
        }}

        .sermon-card {{
            background: #fff;
            border-radius: 12px;
            border-left: 6px solid rgba(37, 150, 190);
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            overflow: hidden;
            transition: transform 0.2s, box-shadow 0.2s;
            margin-bottom: 15px;
        }}

        .sermon-card:hover {{
            transform: translateX(5px);
            box-shadow: 0 8px 20px rgba(155, 89, 182, 0.15);
        }}

        .sermon-header {{
            background: linear-gradient(135deg, rgba(37, 150, 190), rgb(10, 203, 84));
            color: white;
            padding: 18px 25px;
            display: flex;
            align-items: center;
            gap: 15px;
            cursor: pointer;
            transition: background 0.2s;
        }}

        .sermon-header:hover {{
            background: linear-gradient(135deg, #1e8a8c, #0e7c6f); /* Match your teal/green theme */
        }}

        .sermon-header .toggle-icon {{
            font-size: 20px;
            width: 24px;
            text-align: center;
            transition: transform 0.3s;
        }}

        .sermon-date {{
            background: rgba(255,255,255,0.2);
            padding: 8px 16px;
            border-radius: 30px;
            font-size: 16px;
            font-weight: bold;
            display: inline-flex;
            align-items: center;
            gap: 5px;
        }}

        .sermon-title {{
            font-size: 22px;
            font-weight: bold;
            margin: 0;
            flex: 1;
        }}

        .sermon-content {{
            padding: 25px;
            border-top: 1px solid #eee;
            background: white;
            transition: all 0.3s ease;
        }}

        .sermon-content.collapsed {{
            display: none;
        }}

        .sermon-scripture {{
            display: inline-block;
            background: rgb(231, 245, 230);
            color: rgba(37, 150, 190);
            padding: 8px 18px;
            border-radius: 25px;
            font-size: 16px;
            font-weight: bold;
            margin-bottom: 20px;
            border-left: 3px solid rgba(37, 150, 190);
        }}

        .sermon-summary {{
            font-size: 16px;
            line-height: 1.7;
            color: #444;
            margin-bottom: 20px;
            padding: 15px;
            background: #f9f9f9;
            border-radius: 8px;
            border-left: 3px solid #ddd;
        }}

        .key-points-title {{
            font-size: 18px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .key-points-list {{
            list-style: none;
            padding: 0;
            margin: 0;
        }}

        .key-points-list li {{
            padding: 8px 0 8px 25px;
            position: relative;
            font-size: 15px;
            color: #555;
            border-bottom: 1px solid #eee;
        }}

        .key-points-list li:last-child {{
            border-bottom: none;
        }}

        .key-points-list li:before {{
            content: "•";
            color: rgba(37, 150, 190);
            font-weight: bold;
            font-size: 20px;
            position: absolute;
            left: 5px;
            top: 5px;
        }}

        /* No sermons message */
        .no-sermons {{
            display: block !important;
            background: #f5f0f7 !important;
            padding: 40px !important;
            text-align: center !important;
            border-radius: 12px !important;
            color: rgb(127, 140, 141) !important;
            font-size: 18px !important;
            border: 2px dashed rgb(217, 52, 54) !important;
            margin: 20px 0 !important;
            opcaity: 1 !important;
            visibilty: visible !important;
        }}

        .no-sermons br {{
            margin-bottom: 10px;
        }}
        
        /* Announcements */
        .announcement-item {{
            background: #fff3cd;
            padding: 15px;
            margin-bottom: 12px;
            border-radius: 8px;
            border-left: 5px solid #ffc107;
            font-size: 16px;
            color: #856404;
        }}
        
        /* Contact section */
        .contact-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        
        .contact-item {{
            background: #e8f4f8;
            padding: 20px;
            border-radius: 10px;
        }}
        
        .contact-label {{
            font-weight: bold;
            color: #2c3e50;
            font-size: 16px;
            margin-bottom: 8px;
        }}
        
        .contact-value {{
            font-size: 16px;
            color: #555;
        }}
        
        /* About section */
        .about-section {{
            margin-bottom: 25px;
        }}
        
        .about-heading {{
            color: #3498db;
            font-size: 20px;
            margin-bottom: 10px;
            font-weight: bold;
        }}
        
        .about-text {{
            font-size: 16px;
            line-height: 1.6;
            color: #555;
        }}

        .about-text .highlight{{
            font-size: 20px;
            font-weight: bold;
            color: rgb(230, 7, 7);
        }}
        
        /* ============================================
           RIGHT CONTAINER - Church Info + Slideshow
           ============================================ */
        .right-container {{
            width: 50%;
            position: relative;
            overflow: hidden;
            color: white;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 40px;
            order: 2;  /* Show second on desktop (source has it first) */
        }}

        /* Slideshow Background */
        .slideshow-background {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 1;
        }}

        .slideshow-image {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            object-fit: cover;
            opacity: 0;
            transition: opacity 2s ease-in-out, transform 15s linear;
            transform: scale(1.1); 
        }}

        .slideshow-image.active {{
            opacity: 0.6; 
            transform: scale(1);
        }}

        .slideshow-image.exiting {{
            opacity: 0;
            transform: translateX(-100%) scale(1.05);
        }}

        /* Semi-transparent overlay */
        .slideshow-overlay {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, 
                rgba(0, 229, 86, 0.5), 
                rgba(0, 120, 168, 0.7));
            z-index: 2;
        }}

        /* Church info on top */
        .church-header {{
            text-align: center;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            width: 100%;
            z-index: 3;
            position: relative;
            margin-bottom: 0;
        }}

        .church-logo {{
            margin: 0 auto 25px;
            text-align: center;
            display: flex;
            justify-content: center;
            align-items: center;
            width: 100%;
        }}

        .church-logo img {{
            max-width: 250px;
            width: 60%;
            height: auto;
            display: block;
            margin: 0 auto;
            filter: drop-shadow(0 4px 6px rgba(0,0,0,0.3));
        }}

        .church-name {{
            font-size: 40px;
            font-weight: bold;
            margin-bottom: 12px;
            line-height: 1.3;
            text-align: center;
            width: 100%;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        }}

        .church-tagline {{
            font-size: 20px;
            opacity: 0.95;
            text-align: center;
            width: 100%;
            text-shadow: 1px 1px 3px rgba(0,0,0,0.5);
        }}

        /* Message when no images */
        .no-images-message {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            color: white;
            font-size: 18px;
            text-align: center;
            padding: 20px;
            background: rgba(0,0,0,0.5);
            border-radius: 10px;
            z-index: 3;
        }}

        /* ============================================
        WISDOM TIP CARD - HOME PAGE
        ============================================ */

        .wisdom-card {{
            background: linear-gradient(135deg, rgba(0, 229, 86), rgba(0, 120, 168));
            color: white;
            padding: 30px;
            border-radius: 16px;
            margin-top: 30px;
            margin-bottom: 20px;
            box-shadow: 0 10px 25px rgba(243, 156, 18, 0.25);
            border-left: 8px solid #fff;
            position: relative;
            overflow: hidden;
        }}

        .wisdom-card::before {{
            content: "💡";
            font-size: 80px;
            position: absolute;
            bottom: -10px;
            right: 10px;
            opacity: 0.1;
            color: white;
        }}

        .wisdom-header {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 15px;
        }}

        .wisdom-month-badge {{
            background: rgba(255,255,255,0.2);
            padding: 6px 16px;
            border-radius: 40px;
            font-size: 13px;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            border: 1px solid rgba(255,255,255,0.3);
        }}

        .wisdom-title {{
            font-size: 26px;
            font-weight: bold;
            margin-bottom: 15px;
            line-height: 1.3;
        }}

        .wisdom-tip-text {{
            font-size: 18px;
            line-height: 1.6;
            margin-bottom: 20px;
            font-style: italic;
            background: rgba(255,255,255,0.1);
            padding: 18px;
            border-radius: 12px;
            border-left: 4px solid white;
        }}

        .wisdom-steps-title {{
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .wisdom-steps {{
            list-style: none;
            padding: 0;
            margin: 0 0 25px 0;
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            padding: 15px 20px;
        }}

        .wisdom-steps li {{
            padding: 10px 0 10px 35px;
            position: relative;
            font-size: 16px;
            border-bottom: 1px solid rgba(255,255,255,0.15);
        }}

        .wisdom-steps li:last-child {{
            border-bottom: none;
        }}

        .wisdom-steps li:before {{
            content: "✓";
            position: absolute;
            left: 8px;
            top: 10px;
            color: white;
            font-weight: bold;
            font-size: 16px;
            background: rgba(255,255,255,0.2);
            width: 20px;
            height: 20px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        .wisdom-verse-box {{
            background: rgba(255,255,255,0.15);
            padding: 18px;
            border-radius: 12px;
            margin-bottom: 20px;
            border-left: 4px solid white;
        }}

        .wisdom-verse-text {{
            font-size: 17px;
            font-style: italic;
            margin-bottom: 8px;
            line-height: 1.5;
        }}

        .wisdom-verse-ref {{
            font-size: 15px;
            font-weight: bold;
            opacity: 0.95;
        }}

        .wisdom-footer {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 10px;
        }}

        .wisdom-theme {{
            background: rgba(255,255,255,0.2);
            padding: 6px 18px;
            border-radius: 30px;
            font-size: 14px;
            font-weight: bold;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }}

        .wisdom-author {{
            font-size: 14px;
            opacity: 0.9;
            display: flex;
            align-items: center;
            gap: 6px;
        }}

        .wisdom-author:before {{
            content: "—";
            margin-right: 4px;
        }}

        /* Empty state - no tip for current month */
        .no-wisdom {{
            background: #f8f9fa;
            border: 2px dashed rgb(217, 52, 54);
            border-radius: 16px;
            padding: 30px;
            text-align: center;
            margin-top: 30px;
            color: #7f8c8d;
        }}

        .no-wisdom span {{
            font-size: 40px;
            display: block;
            margin-bottom: 10px;
        }}

        .no-wisdom p {{
            font-size: 16px;
        }}

        /* Did You Know mini-card */
        .did-you-know {{
            background: rgba(0, 229, 86, 0.07);
            border-radius: 14px;
            padding: 18px 22px;
            border-left: 5px solid rgba(0, 229, 86);
            margin-top: 16px;
        }}

        .did-you-know-header {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 17px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 12px;
        }}

        .did-you-know ul {{
            list-style: none;
            padding: 0;
            margin: 0;
        }}

        .did-you-know li {{
            font-size: 15px;
            color: #444;
            padding: 8px 0 8px 24px;
            position: relative;
            border-bottom: 1px solid rgba(0, 229, 86, 0.2);
            line-height: 1.5;
        }}

        .did-you-know li:last-child {{
            border-bottom: none;
        }}

        .did-you-know li::before {{
            content: "?";
            position: absolute;
            left: 2px;
            font-weight: bold;
            color: rgba(0, 180, 70);
        }}

        /* ============================================
        RESPONSIVE DESIGN - MOBILE
        ============================================ */
        @media (max-width: 768px) {{

            /* ========== OUTER CONTAINER ========== */
            /* Let the page scroll naturally - no clipping */
            html, body {{
                height: auto !important;
                overflow: auto !important;
            }}

            .container {{
                flex-direction: column;
                height: auto !important;
                min-height: 100vh;
                overflow: visible !important;
            }}

            /* ========== TOP SECTION - LOGO ========== */
            .right-container {{
                order: 1 !important;
                width: 100%;
                height: auto !important;
                min-height: 160px;
                max-height: none !important;   /* Never clip the logo */
                flex-shrink: 0;
                padding: 20px 15px;
                display: flex;
                align-items: center;
                justify-content: center;
                background: linear-gradient(135deg, rgba(0, 229, 86), rgba(0, 120, 168));
                position: relative;
                overflow: hidden;
            }}

            /* Slideshow stays behind logo, just dimmed */
            .slideshow-image.active {{
                opacity: 0.25;
            }}

            /* Logo text - keep original sizes, just center */
            .church-header {{
                width: 100%;
                z-index: 3;
                position: relative;
                text-align: center;
            }}

            .church-logo {{
                margin: 0 auto 10px;
            }}

            /* DO NOT shrink the logo image */
            .church-logo img {{
                max-width: 250px;
                width: 60%;
                height: auto;
            }}

            .church-name {{
                font-size: 28px;
                margin-bottom: 4px;
            }}

            .church-tagline {{
                font-size: 14px;
            }}

            /* ========== BOTTOM SECTION - TABS + CONTENT ========== */
            .left-container {{
                order: 1 !important;
                width: 100%;
                height: auto !important;
                display: flex;
                flex-direction: column;
                overflow: visible !important;
                background: #ecf0f1;
            }}

            /* ========== TABS - Scrollable Row ========== */
            /* Tab bar sticks to top when user scrolls down */
            .tab-buttons {{
                width: 100%;
                height: auto !important;
                flex-shrink: 0;
                display: flex;
                flex-direction: row;
                overflow-x: auto;
                overflow-y: visible;
                padding: 10px 12px;
                gap: 8px;
                background: linear-gradient(135deg, rgba(0, 229, 86), rgba(0, 120, 168));
                align-items: stretch;
                position: sticky;
                top: 0;
                z-index: 100;
                /* Hide scrollbar but keep scrolling */
                scrollbar-width: none;
                -ms-overflow-style: none;
            }}

            .tab-buttons::-webkit-scrollbar {{
                display: none;
            }}

            /* Each tab button - tall enough to hold icon + full word */
            .tab-button {{
                flex-shrink: 0;
                padding: 8px 10px;
                min-width: 70px;
                width: auto;
                height: auto !important;
                min-height: 72px;
                background: #2c3e50;
                border-radius: 8px;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                gap: 4px;
                white-space: nowrap;
            }}

            /* Icon inside tab */
            .tab-icon {{
                font-size: 20px;
                margin-bottom: 0;
                line-height: 1;
            }}

            .tab-icon img.icon-image {{
                width: 26px;
                height: 26px;
                display: block;
            }}

            /* Tab label - horizontal letters, NOT vertical */
            .tab-text {{
                font-size: 9px;
                font-weight: bold;
                letter-spacing: 0.5px;
                line-height: 1.2;
                text-align: center;
                white-space: normal;
                word-break: break-word;
                max-width: 60px;
                display: block !important;
            }}

            /* Override the vertical letter spans - show as inline */
            .tab-text span {{
                display: inline !important;
                margin: 0 !important;
            }}

            /* ========== CONTENT AREA ========== */
            .content-area {{
                width: 100%;
                height: auto !important;
                overflow: visible !important;
                padding: 20px 16px 60px 16px;
                background: white;
            }}

            /* Content sections flow naturally */
            .content-section.active {{
                height: auto !important;
                overflow: visible !important;
                padding-bottom: 40px;
            }}

            /* ========== HOME TAB ========== */
            .welcome-text {{
                font-size: 15px;
                margin-bottom: 20px;
            }}

            .rotating-message {{
                margin-bottom: 25px;
                padding: 20px;
                min-height: 140px;
            }}

            .message-title {{
                font-size: 18px;
            }}

            .message-text {{
                font-size: 15px;
            }}

            /* ========== SECTION TITLES ========== */
            .section-title {{
                font-size: 22px;
                flex-direction: column;
                align-items: flex-start;
                gap: 8px;
                margin-bottom: 20px;
            }}

            .date-badge {{
                font-size: 12px;
                padding: 3px 10px;
            }}

            /* ========== CARD STYLES ========== */
            .event-item,
            .sermon-card,
            .verse-card,
            .testimony-section,
            .mission-card,
            .video-section {{
                margin-bottom: 15px;
            }}

            .event-item {{
                padding: 12px;
            }}

            .event-title {{
                font-size: 17px;
            }}

            .event-detail {{
                font-size: 13px;
            }}

            /* ========== SERMONS ========== */
            .sermon-header {{
                flex-direction: column;
                align-items: flex-start;
                gap: 6px;
                padding: 12px;
            }}

            .sermon-title {{
                font-size: 17px;
            }}

            .sermon-date {{
                font-size: 13px;
                padding: 4px 10px;
            }}

            .sermon-content {{
                padding: 12px;
            }}

            .sermon-scripture {{
                font-size: 13px;
                padding: 5px 12px;
            }}

            .sermon-summary {{
                font-size: 13px;
                padding: 10px;
            }}

            .key-points-title {{
                font-size: 15px;
            }}

            .key-points-list li {{
                font-size: 13px;
                padding: 5px 0 5px 20px;
            }}

            /* ========== INSPIRE ========== */
            .verse-text {{
                font-size: 20px;
            }}

            .verse-card {{
                padding: 18px;
            }}

            .testimony-scrollbox {{
                max-height: 180px;
            }}

            .testimony-card {{
                padding: 12px;
            }}

            .share-cta {{
                padding: 18px;
            }}

            .share-cta h3 {{
                font-size: 18px;
            }}

            /* ========== MISSIONS ========== */
            .mission-title {{
                font-size: 18px;
            }}

            .mission-message {{
                font-size: 15px;
                padding: 12px;
            }}

            .video-container {{
                padding: 20px 12px;
            }}

            .no-mission {{
                padding: 25px 15px;
            }}

            /* ========== CONTACT ========== */
            .contact-grid {{
                grid-template-columns: 1fr;
                gap: 12px;
            }}

            .contact-item {{
                padding: 12px;
            }}

            /* ========== ANNOUNCEMENTS ========== */
            .announcement-item {{
                padding: 10px;
                font-size: 13px;
            }}

            /* ========== BUTTONS ========== */
            .share-email,
            .video-link,
            .support-email {{
                padding: 10px 18px;
                font-size: 14px;
                min-width: 160px;
            }}

            /* ========== WISDOM ========== */
            .wisdom-card {{
                padding: 18px;
                margin-bottom: 30px;
            }}

            .wisdom-title {{
                font-size: 20px;
            }}

            .wisdom-tip-text {{
                font-size: 15px;
                padding: 12px;
            }}

            .wisdom-steps li {{
                font-size: 14px;
                padding: 6px 0 6px 30px;
            }}

            .wisdom-footer {{
                flex-direction: column;
                align-items: flex-start;
                gap: 5px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- LEFT: Content with tabs on the edge -->
        <div class="left-container">
            <div class="tab-buttons">
                <button class="tab-button active" onclick="showTab(0)">
                    <div class="tab-icon">
                        <img src="icons/Home.png" alt="Home" class="icon-image">
                    </div>
                    <div class="tab-text">{vertical_text('HOME')}</div>
                </button>
                <button class="tab-button" onclick="showTab(1)">
                    <div class="tab-icon">
                        <img src="icons/Birthday.png" alt="Birthday" class="icon-image">
                    </div>
                    <div class="tab-text">{vertical_text('BIRTHDAYS')}</div>
                </button>
                <button class="tab-button" onclick="showTab(2)">
                    <div class="tab-icon">
                        <img src="icons/Anniversary.png" alt="Anniversary" class="icon-image">
                    </div>
                    <div class="tab-text">{vertical_text('ANNIVERSARIES')}</div>
                </button>
                <button class="tab-button" onclick="showTab(3)">
                    <div class="tab-icon">
                        <img src="icons/Sermons.png" alt="Sermons" class="icon-image">
                    </div>
                    <div class="tab-text">{vertical_text('SERMONS')}</div>
                </button>
                <button class="tab-button" onclick="showTab(4)">
                    <div class="tab-icon">
                        <img src="icons/Inspire.png" alt="Inspire" class="icon-image">
                    </div>
                    <div class="tab-text">{vertical_text('INSPIRE')}</div>
                </button>
                <button class="tab-button" onclick="showTab(5)">
                    <div class="tab-icon">
                        <img src="icons/Missions.png" alt="Missions" class="icon-image">
                    </div>
                    <div class="tab-text">{vertical_text('MISSIONS')}</div>
                </button>
                <button class="tab-button" onclick="showTab(6)">
                    <div class="tab-icon">
                        <img src="icons/Events.png" alt="Events" class="icon-image">
                    </div>
                    <div class="tab-text">{vertical_text('EVENTS')}</div>
                </button>
                <button class="tab-button" onclick="showTab(7)">
                    <div class="tab-icon">
                        <img src="icons/News.png" alt="News" class="icon-image">
                    </div>
                    <div class="tab-text">{vertical_text('NEWS')}</div>
                </button>
                <button class="tab-button" onclick="showTab(8)">
                    <div class="tab-icon">
                        <img src="icons/Contact.png" alt="Contact" class="icon-image">
                    </div>
                    <div class="tab-text">{vertical_text('CONTACT')}</div>
                </button>
                <button class="tab-button" onclick="showTab(9)">
                    <div class="tab-icon">
                        <img src="icons/About-us.png" alt="About" class="icon-image">
                    </div>
                    <div class="tab-text">{vertical_text('ABOUT')}</div>
                </button>
            </div>
            
            <!-- Content area -->
            <div class="content-area">
                <!-- HOME TAB (tab 0) -->
                <div class="content-section active">
                    <div class="section-title">Welcome <span class="date-badge">📅 {current_date}</span></div>
                    <p class="welcome-text">{tabs['home']['welcome_text']}</p>
                    
                    <div class="rotating-message">
    """)
    
    # Add rotating messages
    for i, msg in enumerate(messages):
        active_class = "active" if i == 0 else ""
        scripture = f'<div class="message-scripture">{msg["scripture"]}</div>' if "scripture" in msg else ""
        html_parts.append(f"""
                        <div class="message {active_class}">
                            <div class="message-title">{msg['title']}</div>
                            {scripture}
                            <div class="message-text">{msg['text']}</div>
                        </div>
        """)
    
    html_parts.append(f"""
                    </div>  <!-- Close rotating-message -->
                    
                    <!-- WISDOM TIP - Monthly -->
    """)

    # Get wisdom tip for current month
    current_wisdom = tabs.get('wisdom_tips', {}).get(current_month, {})

    # Check if we have a real tip (not empty dict and has a title)
    if current_wisdom and isinstance(current_wisdom, dict) and current_wisdom.get('title'):
        tip = current_wisdom.get('tip', '')
        tip_html = f'<div class="wisdom-tip-text">{tip}</div>' if tip else ''
        steps_label = current_wisdom.get('steps_label', 'Quick Steps')  # override per month in JSON
        html_parts.append(f"""
                    <div class="wisdom-card">
                        <div class="wisdom-header">
                            <span class="wisdom-month-badge">💡 {current_month} Wisdom Tip</span>
                        </div>
                        <h3 class="wisdom-title">{current_wisdom.get('title', '')}</h3>
                        {tip_html}
        """)

        # Add steps if they exist
        steps = current_wisdom.get('steps', [])
        if steps:
            html_parts.append(f"""
                        <div class="wisdom-steps-title">📋 {steps_label}:</div>
                        <ul class="wisdom-steps">
            """)
            for step in steps:
                html_parts.append(f"""
                            <li>{step}</li>
            """)
            html_parts.append("""
                        </ul>
        """)

        # Add verse if it exists
        verse = current_wisdom.get('verse', '')
        verse_text = current_wisdom.get('verse_text', '')
        if verse and verse_text:
            html_parts.append(f"""
                        <div class="wisdom-verse-box">
                            <div class="wisdom-verse-text">"{verse_text}"</div>
                            <div class="wisdom-verse-ref">— {verse}</div>
                        </div>
        """)

        # Footer — only render if at least one field has content
        theme = current_wisdom.get('theme', '')
        author = current_wisdom.get('author', '')
        if theme or author:
            theme_html = f'<span class="wisdom-theme">🏷️ {theme}</span>' if theme else ''
            author_html = f'<span class="wisdom-author">{author}</span>' if author else ''
            html_parts.append(f"""
                        <div class="wisdom-footer">
                            {theme_html}
                            {author_html}
                        </div>
        """)

        html_parts.append("""
                    </div>
        """)
    else:
        # No tip for this month
        html_parts.append(f"""
                    <div class="no-wisdom">
                        <span>💭</span>
                        <p>Check back next month for a new wisdom tip!</p>
                    </div>
        """)

    # Did You Know — only renders if data exists for the month
    did_you_know = current_wisdom.get('did_you_know', []) if current_wisdom else []
    if did_you_know:
        html_parts.append("""
                    <div class="did-you-know">
                        <div class="did-you-know-header">📚 Did You Know?</div>
                        <ul>
        """)
        for fact in did_you_know:
            html_parts.append(f"""
                            <li>{fact}</li>
            """)
        html_parts.append("""
                        </ul>
                    </div>
        """)

    html_parts.append(f"""
                </div>  <!-- CLOSE HOME TAB content-section -->
                
                <!-- ========== BIRTHDAY TAB (tab 1) ========== -->
                <div class="content-section">
                    <div class="section-title">🎂 Birthdays This Month ({current_month})</div>
    """)
    
    # Birthday content
    if current_birthdays and len(current_birthdays) > 0:
        for birthday in current_birthdays:
            name = birthday.get('name')
            if not name:
                continue
            formatted_date = format_date_with_ordinal(birthday.get('date', ''))
            html_parts.append(f"""    
                    <div class="event-item">    
                        <div class="event-title">{birthday['name']}</div>
                        <div class="event-detail">🎂 Birthday: {current_month} {formatted_date}</div>        
                    </div>
            """)    
    else:
        html_parts.append("""
                    <div class="event-item">
                        <div class="event-title">No birthdays this month</div>
                        <div class="event-description">Check back next month!</div>
                    </div>
        """)
    
    html_parts.append(f"""
                </div>  <!-- CLOSE BIRTHDAY TAB -->
                
                <!-- ========== ANNIVERSARY TAB (tab 2) ========== -->
                <div class="content-section">
                    <div class="section-title">💍 Anniversaries This Month ({current_month})</div>
    """)
    
    # Anniversary content
    if current_anniversaries and len(current_anniversaries) > 0 and not (len(current_anniversaries) == 1 and current_anniversaries[0] == {}):
        for anniversary in current_anniversaries:
            if anniversary:
                formatted_date = format_date_with_ordinal(anniversary.get('date', ''))
                html_parts.append(f"""
                    <div class="event-item">
                        <div class="event-title">{anniversary.get('names', anniversary.get('couple', ''))}</div>
                        <div class="event-detail">💍 Anniversary: {current_month} {formatted_date}</div>
                """)
                if 'years' in anniversary:
                    html_parts.append(f'<div class="event-detail">🎉 {anniversary["years"]} years together</div>')
                html_parts.append("""
                    </div>
                """)
    else:
        html_parts.append("""
                    <div class="event-item">
                        <div class="event-title">No anniversaries this month</div>
                        <div class="event-description">Check back next month!</div>
                    </div>
        """)
    
    html_parts.append("""
                </div>  
""")

    html_parts.append(f"""
                
                <!-- SERMONS TAB (tab 3) -->
                <div class="content-section">
                    <div class="section-title">📖 Sermons: {sermon_month}</div>
                    <div class="sermons-container">
    """)

    # Get sermons for the month
    current_sermons = tabs.get('sermons', {}).get(current_month, [])
    
    # FILTER OUT EMPTY DICTIONARIES
    valid_sermons = []
    for sermon in current_sermons:
        if sermon and isinstance(sermon, dict) and len(sermon) > 0 and sermon.get('title'):
            valid_sermons.append(sermon)

    if valid_sermons:
        # Sort sermon by date (ascending)
        valid_sermons.sort(key=lambda x: x.get('date', 0))
        
        for i, sermon in enumerate(valid_sermons):
            # Format date
            formatted_date = format_date_with_ordinal(sermon.get('date', ''))
            
            # First sermon is open by default, others closed
            is_first = (i == 0)
            toggle_icon = "▼" if is_first else "▶"
            content_class = "" if is_first else "collapsed"
            header_active = "active" if is_first else ""
            
            # Make the sermon card
            html_parts.append(f"""
                        <div class="sermon-card">
                            <div class="sermon-header {header_active}" onclick="toggleSermon(this)">
                                <span class="toggle-icon">{toggle_icon}</span>
                                <span class="sermon-date">📅 {sermon_month} {formatted_date}</span>
                                <h3 class="sermon-title">{sermon.get('title', 'Sermon')}</h3>
                            </div>
                            <div class="sermon-content {content_class}">
            """)
            scripture = sermon.get('scripture', '')
            summary = sermon.get('summary', '')
            if scripture:
                html_parts.append(f'<div class="sermon-scripture">📖 {scripture}</div>')
            if summary:
                html_parts.append(f'<div class="sermon-summary">{summary}</div>')
            
            # Add key points
            key_points = sermon.get('key_points', [])
            if key_points:
                html_parts.append(f"""
                                <div class="key-points-title">💭 Key Points:</div>
                                <ul class="key-points-list">
                """)
                for point in key_points:
                    html_parts.append(f"""
                                    <li>{point}</li>
                    """)
                html_parts.append("""
                                </ul>
                """)
            
            html_parts.append("""
                            </div>
                        </div>
            """)
    else:
        # No valid sermons - Show message with normal styling
        html_parts.append("""
                        <div class="no-sermons">
                            📖 No sermons yet this month.<br>
                            Check back after Sunday service!
                        </div>
        """)

    html_parts.append("""
                    </div>
                </div>
                
                <!-- INSPIRE TAB (tab 4) -->
                <div class="content-section">
                    <div class="section-title">✨ Inspire Corner</div>
                    <div class="inspire-container">
    """)
    
    current_inspire = tabs.get('inspire', {}).get(current_month, {})
    
    # ========== VERSE OF THE MONTH (OPTIONAL) ==========
    verse_data = current_inspire.get('verse_of_the_month', {})
    
    if verse_data and isinstance(verse_data, dict) and verse_data.get('verse') and verse_data.get('text'):
        verse_theme = verse_data.get('theme', '')
        verse_theme_html = f'<span class="verse-theme">🎯 {verse_theme}</span>' if verse_theme else ''
        html_parts.append(f"""
                        <div class="verse-card">
                            <div class="verse-icon">📖</div>
                            <div class="verse-text">"{verse_data.get('text', '')}"</div>
                            <div class="verse-reference">— {verse_data.get('verse', '')}</div>
                            {verse_theme_html}
        """)
        
        # Optional pastor's comment
        if verse_data.get('comment') and verse_data.get('comment_author'):
            html_parts.append(f"""
                            <div class="pastor-comment">
                                <div class="pastor-comment-text">💬 {verse_data.get('comment', '')}</div>
                                <div class="pastor-comment-author">{verse_data.get('comment_author', '')}</div>
                            </div>
        """)
        
        html_parts.append("""
                        </div>
        """)
    else:
        # No verse for this week/month
        html_parts.append("""
                        <div class="no-wisdom" style="border-color: rgb(217, 52, 54); color: #7f8c8d;">
                            <span>📖</span>
                            <p>No verse this month. Check back soon!</p>
                        </div>
        """)
    
    # ========== FEATURED TESTIMONY (OPTIONAL) ==========
    testimony_data = current_inspire.get('featured_testimony', {})
    
    if testimony_data and isinstance(testimony_data, dict) and testimony_data.get('testimony') and testimony_data.get('name'):
        html_parts.append(f"""
                        <div class="testimony-section">
                            <div class="testimony-header">
                                <span class="testimony-icon">🌟</span>
                                <h3 class="testimony-title">Featured Testimony</h3>
                            </div>
                            <div class="testimony-scrollbox">
                                <div class="testimony-card">
                                    <div class="testimony-quote">❝</div>
                                    <div class="testimony-text">{testimony_data.get('testimony', '')}</div>
                                    <div class="testimony-author">— {testimony_data.get('name', '')}</div>
                                    <div class="testimony-date">{testimony_data.get('date', '')}</div>
        """)
        
        # Optional verse with testimony
        if testimony_data.get('verse'):
            html_parts.append(f"""
                                    <div class="testimony-verse">📖 {testimony_data.get('verse', '')}</div>
        """)
        
        html_parts.append("""
                                </div>
                            </div>
                        </div>
        """)
    else:
        # No testimony this month
        html_parts.append("""
                        <div class="no-testimony">
                            <span>🌟</span>
                            <p>No testimony this month.</p>
                            <p style="font-size: 14px; margin-top: 10px;">Check back next month or share your own!</p>
                        </div>
        """)
    
    # ========== SHARE YOUR STORY (ALWAYS VISIBLE) ==========
    html_parts.append(f"""
                        <div class="share-cta">
                            <h3>💌 Share Your Story</h3>
                            <p>Has God moved in your life? Your testimony could encourage someone else.</p>
                            <a href="mailto:gcbctt@gmail.com?subject=My Testimony" class="share-email">📧 gcbctt@gmail.com</a>
                        </div>
                    </div>
                </div>
                      
                                <!-- MISSIONS TAB (tab 5) -->
                <div class="content-section">
                    <div class="section-title">🌍 Missions - {current_month}</div>
                    <div class="missions-container">
    """)

    # Get missions data for current month
    current_missions = tabs.get('missions', {}).get(current_month, {})
    
    if current_missions and len(current_missions) > 0 and current_missions.get('featured'):
        
        # ========== VIDEO SECTION (OPTIONAL) ==========
        video_data = current_missions.get('video', {})
        if video_data and isinstance(video_data, dict) and video_data.get('type'):
            
            if video_data.get('type') == 'youtube' and video_data.get('url'):
                # YouTube link
                html_parts.append(f"""
                        <div class="video-section">
                            <div class="video-header">
                                <span class="video-icon">🎬</span>
                                <h3 class="video-title">{video_data.get('title', 'Mission Video')}</h3>
                            </div>
                            <div class="video-container">
                                <div class="video-placeholder">▶️</div>
                                <p>{video_data.get('title', '')}</p>
                                <p>Duration: {video_data.get('duration', '')}</p>
                                <a href="{video_data.get('url', '#')}" target="_blank" class="video-link">Watch on YouTube ↗</a>
                            </div>
                            <div class="video-meta">
                                <span>📅 {current_month} 2026</span>
                                <span>🎥 Mission Update</span>
                            </div>
                        </div>
                """)
            
            elif video_data.get('type') == 'local' and video_data.get('filename'):
                # Local video file
                video_file = video_data.get('filename', '')
                html_parts.append(f"""
                        <div class="video-section">
                            <div class="video-header">
                                <span class="video-icon">🎬</span>
                                <h3 class="video-title">{video_data.get('title', 'Mission Video')}</h3>
                            </div>
                            <video controls class="local-video-player" width="100%">
                                <source src="missions_videos/{video_file}" type="video/mp4">
                                Your browser does not support the video tag.
                            </video>
                            <div class="video-meta">
                                <span>📅 {current_month} 2026</span>
                                <span>🎥 {video_data.get('duration', '')}</span>
                            </div>
                        </div>
                """)
        
        # ========== FEATURED MISSION ==========
        html_parts.append(f"""
                        <div class="mission-card">
                            <div class="mission-header">
                                <span class="mission-icon">🌍</span>
                                <h3 class="mission-title">{current_missions.get('featured', 'Mission')}</h3>
                                <span class="mission-location">{current_month} 2026</span>
                            </div>
        """)
        
        # Mission Update
        update_data = current_missions.get('update', {})
        if update_data:
            mission_msg = update_data.get('message', '')
            mission_author = update_data.get('author', '')
            if mission_msg:
                html_parts.append(f'<div class="mission-message">"{mission_msg}"</div>')
            if mission_author:
                html_parts.append(f'<div class="mission-author">— {mission_author}</div>')
        
        # ========== PRAYER POINTS ==========
        prayer_points = current_missions.get('prayer_points', [])
        if prayer_points and len(prayer_points) > 0:
            html_parts.append(f"""
                            <div class="prayer-section">
                                <div class="prayer-header">
                                    <span>🙏</span>
                                    <span>Prayer Focus</span>
                                </div>
                                <ul class="prayer-list">
            """)
            for point in prayer_points:
                html_parts.append(f"""
                                    <li>{point}</li>
                """)
            html_parts.append(f"""
                                </ul>
                            </div>
            """)
        
        # ========== PROGRESS BAR (OPTIONAL) ==========
        progress_data = current_missions.get('progress', {})
        if progress_data and progress_data.get('percentage') is not None:
            percentage = progress_data.get('percentage', 0)
            label = progress_data.get('label', 'Progress')
            html_parts.append(f"""
                            <div class="progress-section">
                                <div class="progress-label">
                                    <span>📊 {label}</span>
                                    <span class="progress-percent">{percentage}%</span>
                                </div>
                                <div class="progress-container">
                                    <div class="progress-bar" style="width: {percentage}%;"></div>
                                </div>
                            </div>
            """)
        
        html_parts.append("""
                        </div>
        """)
        
        # ========== SUPPORT SECTION (OPTIONAL) ==========
        support_data = current_missions.get('support', {})
        
        # Check if there's ANY actual content (non-empty values)
        has_content = False
        if support_data:
            if support_data.get('give_link') and str(support_data.get('give_link')).strip():
                has_content = True
            elif support_data.get('drive') and str(support_data.get('drive')).strip():
                has_content = True
            elif support_data.get('email') and str(support_data.get('email')).strip():
                has_content = True
        
        if has_content:
            html_parts.append(f"""
                        <div class="support-section">
                            <div class="support-header">
                                <span>💰</span>
                                <span>How to Support</span>
                            </div>
                            <ul class="support-list">
            """)
            
            if support_data.get('give_link') and str(support_data.get('give_link')).strip():
                html_parts.append(f"""
                                <li>💵 Give online: {support_data.get('give_link')}</li>
            """)
            if support_data.get('drive') and str(support_data.get('drive')).strip():
                html_parts.append(f"""
                                <li>📦 Supply drive: {support_data.get('drive')}</li>
            """)
            if support_data.get('email') and str(support_data.get('email')).strip():
                html_parts.append(f"""
                                <li>✉️ Write to missionaries: <a href="mailto:{support_data.get('email')}" class="support-email">{support_data.get('email')}</a></li>
            """)
            
            html_parts.append("""
                            </ul>
                        </div>
        """)
        
    else:
        # No mission this month - Show empty state with prayer suggestions
        html_parts.append("""
                        <div class="no-mission">
                            <span>🌍</span>
                            <h3>No Missions Testimony This Month</h3>
                            <p>Check back next month for updates from our missionaries around the world!</p>
                            <div class="prayer-suggestions">
                                <h4>🙏 In the meantime, please pray for:</h4>
                                <ul>
                                    <li>All missionaries serving globally</li>
                                    <li>Upcoming mission teams</li>
                                    <li>Open hearts in every nation</li>
                                    <li>Safety and provision for our partners</li>
                                </ul>
                            </div>
                        </div>
        """)

    html_parts.append("""
                    </div>
                </div>
                
                <!-- EVENTS TAB (tab 6) -->
                <div class="content-section">
                    <div class="section-title">📅 Events</div>
    """)

    permanant_events = [e for e in tabs.get('events', {}).get('permanant', []) if e]
    monthly_events   = [e for e in tabs.get('events', {}).get(current_month, []) if e]

    def render_event(event, permanent=False):
        css_class = "event-item event-item--permanent" if permanent else "event-item"
        desc = event.get('description', '')
        desc_html = f'<div class="event-description">{desc}</div>' if desc else ''
        zoom = event.get('zoom_link', '')
        meeting_id = event.get('meeting_id', '')
        passcode = event.get('passcode', '')
        if zoom:
            zoom_html = f'<div class="event-detail"><a href="{zoom}" target="_blank">🔗 Join on Zoom</a></div>'
        elif meeting_id:
            zoom_html = f'<div class="event-detail">🔗 Join on Zoom</div>'
        else:
            zoom_html = ''
        meeting_html = f'<div class="event-detail">Meeting ID: {meeting_id}</div>' if meeting_id else ''
        passcode_html = f'<div class="event-detail">Passcode: {passcode}</div>' if passcode else ''
        return f"""
                        <div class="{css_class}">
                            <div class="event-title">{event['title']}</div>
                            <div class="event-detail">📅 {event['date']}</div>
                            <div class="event-detail">🕐 {event['time']}</div>
                            <div class="event-detail">📍 {event['location']}</div>
                            {desc_html}
                            {zoom_html}
                            {meeting_html}
                            {passcode_html}
                        </div>
        """

    if permanant_events or monthly_events:
        for event in permanant_events:
            html_parts.append(render_event(event, permanent=True))
        for event in monthly_events:
            html_parts.append(render_event(event, permanent=False))
    else:
        html_parts.append(f"""
            <div class="event-item">
                <div class="event-title">No events this month</div>
                <div class="event-description">Check back next month!</div>
            </div>
        """)   
    
    html_parts.append("""
                </div>
                
                <!-- ANNOUNCEMENTS TAB (tab 7) -->
                <div class="content-section">
                    <div class="section-title">📢 Announcements</div>
    """)
    
    # Add announcements
    announcements = tabs.get('announcements', [])
    if announcements:
        for announcement in announcements:
            html_parts.append(f"""
                    <div class="announcement-item">{announcement}</div>
            """)
    else:
        html_parts.append("""
                    <div class="announcement-item" style="color:#7f8c8d; font-style:italic;">No announcements this month.</div>
        """)
    
    html_parts.append("""
                </div>
                
                <!-- CONTACT TAB (tab 8) -->
                <div class="content-section">
                    <div class="section-title">📞 Contact Us</div>
                    <div class="contact-grid">
    """)
    
    # Add contact info
    contact = tabs['contact']
    html_parts.append(f"""
                        <div class="contact-item">
                            <div class="contact-label">Phone</div>
                            <div class="contact-value">{contact['phone']}</div>
                        </div>
                        <div class="contact-item">
                            <div class="contact-label">Mail</div>
                            <div class="contact-value">{contact['mail']}</div>
                        </div>
                        <div class="contact-item">
                            <div class="contact-label">Email</div>
                            <div class="contact-value">{contact['email']}</div>
                        </div>
                        <div class="contact-item">
                            <div class="contact-label">Address</div>
                            <a href="https://maps.app.goo.gl/Z1PNBhH6kBJWH3zk8"><div class="contact-value">{contact['address']}</div></a>
                        </div>
    """)
    
    html_parts.append("""
                    </div>
                </div>
                
                <!-- ABOUT TAB (tab 9) -->
                <div class="content-section">
                    <div class="section-title">ℹ️ About Us</div>
    """)
    
    # Add about info
    about = tabs['about']
    html_parts.append(f"""
                    <div class="about-section">
                        <div class="about-heading">Our Mission Statement</div>
                        <div class="about-text">{about['mission']}</div>
                    </div>
                    <div class="about-section">
                        <div class="about-heading">Leadership</div>
                        <div class="about-text">{about['leadership']}</div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- RIGHT: Church Info with Slideshow Background -->
        <div class="right-container">
            <!-- Slideshow Background -->
            <div class="slideshow-background">
    """)
    
    # Add slideshow if it exists
    if slideshow_images:
        for i, img in enumerate(slideshow_images):
            active_class = "active" if i == 0 else ""
            html_parts.append(f"""
                <img src="slideshow_folder/{img}" class="slideshow-image {active_class}" alt="Slideshow Image {i+1}">
            """)
    else:
        html_parts.append("""
                <div class="no-images-message">
                    Add images to 'slideshow_folder'
                </div>
        """)
    
    html_parts.append(f"""
            </div>
            
            <!-- Semi-transparent overlay -->
            <div class="slideshow-overlay"></div>
            
            <!-- Church Info (on top of slideshow) -->
            <div class="church-header">
                <div class="church-logo">
                    <img src="Images/GCBC LOGO Transparent.png" alt="Church Logo"> 
                </div>
                <div class="church-name">{church['name']}</div>
                <div class="church-tagline">{church['tagline']}</div>
            </div>
        </div>
    </div>
    
    <script>
        // Tab switching
        function showTab(tabIndex) {{
            const buttons = document.querySelectorAll('.tab-button');
            const sections = document.querySelectorAll('.content-section');
            
            buttons.forEach(btn => btn.classList.remove('active'));
            sections.forEach(section => section.classList.remove('active'));
            
            buttons[tabIndex].classList.add('active');
            sections[tabIndex].classList.add('active');
        }}
        
        // ROTATE MESSAGES
        let currentMessage = 0;
        const messages = document.querySelectorAll('.message');
        let messageInterval;

        function calculateMessageDuration(messageElement) {{
            //Get text content from title, scripture and text
            const title = messageElement.querySelector('.message-title')?.textContent || '';
            const scripture = messageElement.querySelector('.message-scripture')?.textContent || '';
            const text = messageElement.querySelector('.message-text')?.textContent || '';

            //Gets total count
            const totalLength = title.length + scripture.length + text.length;

            console.log(`Message length: ${{totalLength}} characters`);

            //Calculate Duration: base 5 seconds + 1 seconds per 50 characters
            let duration = 5000 + (totalLength * 38) //38ms per character = 1 second per 50 chars

            //Set min and max
            if (duration < 5000) duration = 5000;
            if (duration > 20000) duration = 20000

            return duration;
        }}
        
        function rotateMessages() {{
            if (messages.length === 0) return;

            //Hide current message
            messages[currentMessage].classList.remove('active');

            //Move to next one
            currentMessage = (currentMessage + 1) % messages.length;

            //Show next message
            messages[currentMessage].classList.add('active');

            //Calcualte duration for new meesage
            const nextDuration = calculateMessageDuration(messages[currentMessage]);
            console.log(`Next message will display for ${{nextDuration/1000}} seconds`);

            //Clear old interval and set the new one
            clearInterval(messageInterval);
            messageInterval = setInterval(rotateMessages, nextDuration);
        }}
        //Start the rotation with first message
        if (messages.length > 0) {{
            const initialDuration = calculateMessageDuration(messages[0]);
            messageInterval = setInterval(rotateMessages, initialDuration);
        }}
        
        // Slideshow functionality
        function initSlideshow() {{
            const slides = document.querySelectorAll('.slideshow-image');
            const slideDuration = 5000;
            let currentSlide = 0;
        
            if (slides.length === 0) {{
                console.log('No slideshow images found');
                return;
            }}
            
            slides[currentSlide].classList.add('active');
            
            if (slides.length === 1) {{
                return;
            }}
            
            function rotateSlides() {{
                slides[currentSlide].classList.add('exiting');
                slides[currentSlide].classList.remove('active');
                
                currentSlide = (currentSlide + 1) % slides.length;
                
                slides[currentSlide].classList.add('active');
                slides[currentSlide].classList.remove('exiting');
                
                setTimeout(() => {{
                    const prevSlide = (currentSlide - 1 + slides.length) % slides.length;
                    slides[prevSlide].classList.remove('exiting');
                }}, 2000);
            }}
            
            setInterval(rotateSlides, slideDuration);
        }}
        
        document.addEventListener('DOMContentLoaded', initSlideshow);

        // Sermons Accordion Functionality - Single Open Mode (Recommended)
        function toggleSermon(header) {{
            // Get all sermon headers and contents
            const allHeaders = document.querySelectorAll('.sermon-header');
            const allContents = document.querySelectorAll('.sermon-content');
            const currentContent = header.nextElementSibling;
            const currentIcon = header.querySelector('.toggle-icon');
            
            // Check if current sermon is already open
            const isOpen = !currentContent.classList.contains('collapsed');
            
            // CLOSE ALL sermons first
            allHeaders.forEach((h, index) => {{
                h.classList.remove('active');
                const icon = h.querySelector('.toggle-icon');
                if (icon) icon.textContent = '▶';
            }});
            
            allContents.forEach(content => {{
                content.classList.add('collapsed');
            }});
            
            // If it wasn't open, OPEN the clicked one
            if (!isOpen) {{
                currentContent.classList.remove('collapsed');
                header.classList.add('active');
                currentIcon.textContent = '▼';
            }} 
            else {{
                currentContent.classList.add('collapsed');
                header.classList.remove('active');
                currentIcon.textContent = '▶';                
            }}
        }}
    </script>
</body>
</html>
""")
    
    html = ''.join(html_parts)
    
    # Write to file
    with open(os.path.join(SCRIPT_DIR, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html)
    
    print("index.html generated successfully!")
    return 'index.html'

if __name__ == "__main__":
    generate_html()