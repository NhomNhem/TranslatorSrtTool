# config.py

APP_NAME = "SRT Translator"
APP_VERSION = "2.1"  # Use a consistent version number
COPYRIGHT_NOTICE = "Copyright (c) 2024 NhemNhem. All rights reserved."

# Default settings
DEFAULT_FORMAT = ".srt"
DEFAULT_COLOR = "#FFFFFF"

# Preview text (placeholders for different formats)
PREVIEW_TEXT_SRT = "Đây là text mẫu.\nĐây là dòng thứ hai."
PREVIEW_TEXT_ASS = "Đây là text mẫu.\\NĐây là dòng thứ hai."

# --- UI Constants ---
TEXT = "#000"
BG_COLOR = "#2C2F33"         # Main background
FRAME_COLOR = "#36393F"      # Darker gray for the file list frame
BUTTON_COLOR = "#000000"     # Black  <-- CHANGED
BUTTON_TEXT_COLOR = "#FFFFFF"  # White <-- FIXED: Changed to White
BUTTON_ACTIVE_COLOR = "#777777"  # Gray
LABEL_COLOR = "#FFFFFF"        # White for most labels
SETTINGS_LABEL_COLOR = "#000000"  # Black for settings labels (like "Định dạng:")
PROGRESS_BAR_COLOR = "#7FFF00"  # Example: Chartreuse
STATUS_COLOR = "#00008B" # Not used
FONT = ("Arial", 12)
FILE_NAME_MAX_LENGTH = 20  # Maximum characters for filenames before truncation