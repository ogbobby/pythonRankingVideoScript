import os
import sys
import random
from yt_dlp import YoutubeDL
from moviepy import VideoFileClip, concatenate_videoclips, TextClip, CompositeVideoClip

# =====================================================================
# 1. TEXT CONTENT CONFIGURATION (Change these for every new video)
# =====================================================================
# This title will now wrap cleanly over multiple lines if it gets too long!
VIDEO_TITLE = "THE MOST UNBELIEVABLE AND INSANE MOMENTS OF THE YEAR"  
CLIP_DURATION = 7             # How long each clip plays in seconds
TITLE_BG_COLOR = (0, 0, 0, 180)  # Pure Black with roughly 70% opacity/transparency layer

# Customize the text descriptions next to each rank number
RANK_LABELS = {
    5: "Wildest Play",
    4: "Insane Save",
    3: "Close Call",
    2: "Runner Up",
    1: "The Winner"
}

# Paste your raw TikTok or Shorts source links here
TIKTOK_URLS = [
    "https://www.tiktok.com/@overtime/video/7626609471468408078?is_from_webapp=1&sender_device=pc",  # Will become Rank #3
    "https://www.tiktok.com/@breakanklesdaily/video/7118213436248542506?is_from_webapp=1&sender_device=pc",  # Will become Rank #2
    "https://www.tiktok.com/@hooperzgod/video/6970740966407933189?is_from_webapp=1&sender_device=pc"   # Will become Rank #1 (Best)
]

# =====================================================================
# 2. DESIGN & STYLE CONFIGURATION (Customize your look here)
# =====================================================================
FONT_PATH = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

# Title Styling & Automatic Wrapping Constraints
TITLE_FONT_SIZE = 50         # Slightly smaller default to accommodate long wrapping lines safely
TITLE_MAX_WIDTH = 600         # Maximum width in pixels. Text wraps if it crosses this limit!
TITLE_COLOR = "#FF3366"       # Bright neon pink/red
TITLE_STROKE_COLOR = "black"
TITLE_STROKE_WIDTH = 5

# Left-Side Number List Styling
LIST_PADDING_LEFT = 40        # Pixels away from the left edge of the screen
LIST_START_Y = 280            # Pixels away from the top edge of the screen
LIST_SPACING_Y = 85           # Vertical gap size between each list item

# Inactive Ranks (Default view)
INACTIVE_FONT_SIZE = 40
INACTIVE_COLOR = "white"
INACTIVE_STROKE_WIDTH = 2

# Active Rank (The one currently playing on screen)
ACTIVE_FONT_SIZE = 50
ACTIVE_COLOR = "yellow"
ACTIVE_STROKE_WIDTH = 4

# =====================================================================
# AUTOMATION ENGINE (Do not modify code below this line)
# =====================================================================

def main():
    if not TIKTOK_URLS or "username" in TIKTOK_URLS:
        print("Error: Please open the script and update TIKTOK_URLS with real links.")
        sys.exit(1)

    downloaded_files = []
    
    ydl_opts = {
        'outtmpl': 'temp_clip_%(id)s.%(ext)s',
        'format': 'bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]', 
        'merge_output_format': 'mp4',
        'quiet': True
    }

    # Step 1: Download
    print(f"\n[1/4] Downloading {len(TIKTOK_URLS)} TikTok videos...")
    with YoutubeDL(ydl_opts) as ydl:
        for url in TIKTOK_URLS:
            try:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                if not filename.endswith('.mp4'):
                    filename = os.path.splitext(filename) + '.mp4'
                downloaded_files.append(filename)
            except Exception as e:
                print(f"Failed to download {url}. Error: {e}")

    # Step 2: Shuffle
    print("\n[2/4] Shuffling video play order...")
    random.shuffle(downloaded_files)
    print(" -> New video sequence generated successfully!")

    # Step 3: Layout Composition
    print("\n[3/4] Processing clips and building layout...")
    processed_clips = []
    total_clips = len(downloaded_files)

    for index, file_path in enumerate(downloaded_files):
        if not os.path.exists(file_path):
            continue
            
        current_rank_num = total_clips - index
        print(f" -> Position {index + 1} assigned to: {current_rank_num}.")
        
        # Load and trim video source
        full_clip = VideoFileClip(file_path)
        end_time = min(CLIP_DURATION, full_clip.duration)
        trimmed_clip = full_clip.subclipped(0, end_time)
        
        layers = [trimmed_clip]

        # --- A. BUILD MAIN TITLE WITH TEXT WRAPPING ---
        #title_clip = TextClip(
        #    text=VIDEO_TITLE,
        #    font=FONT_PATH,
        #    font_size=TITLE_FONT_SIZE,
        #    color=TITLE_COLOR,
        #    stroke_color=TITLE_STROKE_COLOR,
        #    stroke_width=TITLE_STROKE_WIDTH,
        #    size=(TITLE_MAX_WIDTH, 200),   # <-- Must give it a fixed bounding box height (e.g. 200px)
        #    method="caption",              # <-- CRITICAL: Forces MoviePy to wrap text inside the box
        #    text_align="center",            # Keeps wrapped rows centered
        #    bg_color=TITLE_BG_COLOR  # <-- This acts as a masking shield over the TikTok's native text!
        #)
        #title_clip = title_clip.with_position(('center', 40)).with_duration(trimmed_clip.duration)
        #layers.append(title_clip)

                # --- A. BUILD MAIN TITLE WITH A FIXED BOUNDING BOX SHIELD ---
        # Instead of reading the whole video canvas, we clamp the width to 450px 
        # so it forces clean word wrapping and stacks neatly in a tight block.
        title_clip = TextClip(
            text=VIDEO_TITLE,
            font=FONT_PATH,
            font_size=32,                 # Smaller, compact font ensures no word-breaking
            color=TITLE_COLOR,
            stroke_color=TITLE_STROKE_COLOR,
            stroke_width=3,
            size=(450, 160),              # Hard limit width restricts text inside the visual field
            method="caption",
            text_align="center",
            bg_color=(10, 10, 10, 230)    # Darker, more solid background entirely masks native video text
        )
        # Position the block safely down a tiny bit so it frames perfectly over the video center
        title_clip = title_clip.with_position(('center', 20)).with_duration(trimmed_clip.duration)
        layers.append(title_clip)


        # --- B. BUILD LEFT-SIDE RANKING LIST WITH LABELS ---
        for r in range(total_clips, 0, -1):
            is_active = (r == current_rank_num)
            
            text_color = ACTIVE_COLOR if is_active else INACTIVE_COLOR
            text_size = ACTIVE_FONT_SIZE if is_active else INACTIVE_FONT_SIZE
            stroke_w = ACTIVE_STROKE_WIDTH if is_active else INACTIVE_STROKE_WIDTH
            
            label_text = RANK_LABELS.get(r, "")
            display_string = f"{r}. {label_text}"
            
            list_item_clip = TextClip(
                text=display_string,
                font=FONT_PATH,
                font_size=text_size,
                color=text_color,
                stroke_color='black',
                stroke_width=stroke_w
            )
            
            y_pos = LIST_START_Y + ((total_clips - r) * LIST_SPACING_Y)
            list_item_clip = list_item_clip.with_position((LIST_PADDING_LEFT, y_pos)).with_duration(trimmed_clip.duration)
            layers.append(list_item_clip)

        final_clip = CompositeVideoClip(layers)
        processed_clips.append(final_clip)

    # Step 4: Save & Compile
    if processed_clips:
        print("\n[4/4] Stitching final video output file...")
        output_filename = "wrapped_title_compilation.mp4"
        
        final_compilation = concatenate_videoclips(processed_clips, method="compose")
        final_compilation.write_videofile(
            output_filename, 
            fps=30, 
            codec="libx264", 
            audio_codec="aac"
        )
        
        print("\nCleaning up temporary storage files...")
        for clip in processed_clips:
            clip.close()
        for file in downloaded_files:
            if os.path.exists(file):
                os.remove(file)
                
        print(f"\nSuccess! Open your folder to find: {output_filename}")
    else:
        print("\nProcess failed: No clips were successfully compiled.")

if __name__ == "__main__":
    main()
