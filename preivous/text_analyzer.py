import os
import json
import pytesseract
import csv
from PIL import Image
from datetime import datetime
from pathlib import Path

# === CONFIG ===
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

screenshot_folder = "screen_logs"
keyboard_log_file = "full_key_log.txt"
output_folder = "extracted_texts"
cropped_folder = os.path.join(output_folder, "cropped")
mouse_data_file = "mouse_coords.json"

FOCUS_SIZE = 300
LOGO_REGION = (0, 0, 200, 80)

os.makedirs(output_folder, exist_ok=True)
os.makedirs(cropped_folder, exist_ok=True)

def load_mouse_positions():
    with open(mouse_data_file, 'r') as f:
        return json.load(f)

def load_keyboard_log():
    logs = []
    with open(keyboard_log_file, 'r') as f:
        for line in f:
            try:
                time_str, key = line.strip().split(' | ')
                logs.append((datetime.fromisoformat(time_str), key))
            except:
                continue
    return logs

def extract_region(image, box, save_path=None):
    region = image.crop(box)
    if save_path:
        region.save(save_path)
    return region

def get_text_lines(image):
    raw_text = pytesseract.image_to_string(image)
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    joined = " ".join(lines)
    return {"lines": lines, "joined": joined}

def extract_focused_region(image, x, y):
    width, height = image.size
    left = max(x - FOCUS_SIZE // 2, 0)
    top = max(y - FOCUS_SIZE // 2, 0)
    right = min(x + FOCUS_SIZE // 2, width)
    bottom = min(y + FOCUS_SIZE // 2, height)
    return image.crop((left, top, right, bottom)), (left, top, right, bottom)

def find_closest_keys(timestamp, keyboard_logs, tolerance_secs=5):
    closest = []
    for t, key in keyboard_logs:
        if abs((timestamp - t).total_seconds()) <= tolerance_secs:
            closest.append((t.isoformat(), key))
    return closest

def save_csv_row(csv_file, data):
    file_exists = os.path.isfile(csv_file)
    with open(csv_file, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=data.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)

def process_screenshots():
    mouse_positions = load_mouse_positions()
    keyboard_logs = load_keyboard_log()
    csv_log_path = os.path.join(output_folder, "summary.csv")

    for filename, mouse_data in mouse_positions.items():
        if not filename.endswith(('.jpg', '.png')):
            continue

        try:
            timestamp = datetime.fromisoformat(mouse_data["timestamp"])
        except Exception as e:
            print(f"Skipping {filename}: Invalid timestamp - {e}")
            continue

        image_path = os.path.join(screenshot_folder, filename)
        if not os.path.exists(image_path):
            print(f"Image file not found: {filename}")
            continue

        image = Image.open(image_path)
        base_name = Path(filename).stem

        # Extract regions
        logo_img = extract_region(image, LOGO_REGION, os.path.join(cropped_folder, f"{base_name}_logo.png"))
        logo_text = get_text_lines(logo_img)

        focused_img, focus_box = extract_focused_region(image, mouse_data['x'], mouse_data['y'])
        focused_img.save(os.path.join(cropped_folder, f"{base_name}_focused.png"))
        focused_text = get_text_lines(focused_img)

        full_text = get_text_lines(image)

        keys = find_closest_keys(timestamp, keyboard_logs)

        data = {
            "timestamp": timestamp.isoformat(),
            "image_file": filename,
            "mouse_click": {"x": mouse_data['x'], "y": mouse_data['y']},
            "window_title": logo_text['lines'][0] if logo_text['lines'] else "Unknown",
            "ocr_text": {
                "full_screen": full_text,
                "focused_area": focused_text,
                "logo": logo_text
            },
            "focused_region_box": focus_box,
            "cropped_images": {
                "logo": f"{base_name}_logo.png",
                "focused": f"{base_name}_focused.png"
            },
            "keys_pressed": [
                {"time": t, "key": key} for t, key in keys
            ]
        }

        # Save JSON
        output_json_path = os.path.join(output_folder, base_name + ".json")
        with open(output_json_path, 'w') as out:
            json.dump(data, out, indent=4)

        # Save to CSV
        save_csv_row(csv_log_path, {
            "timestamp": data["timestamp"],
            "window_title": data["window_title"],
            "keys": " ".join([k['key'] for k in data['keys_pressed']]),
            "ocr_snippet": data['ocr_text']['focused_area']['joined'][:100],
            "logo_text": data['ocr_text']['logo']['joined'][:100],
            "focused_crop": data['cropped_images']['focused']
        })

        print(f"[+] Processed {filename}")

process_screenshots()
