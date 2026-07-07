import os
import sys
import random
from yt_dlp import YoutubeDL
from moviepy import VideoFileClip, concatenate_videoclips, TextClip, CompositeVideoClip

# =====================================================================
# 1. TEXT CONTENT CONFIGURATION (Change these for every new video)
# =====================================================================
VIDEO_TITLE = "Ranking Insane Ankle Breaking Moments"  
CLIP_DURATION = 10             

RANK_LABELS = {
    6: "Wow.",
    5: "Brah.",
    4: "Yikes.",
    3: "Dude",
    2: "Oh.",
    1: "Yo."
}

TIKTOK_URLS = [
    "https://www.tiktok.com/@overtime/video/7643091572598263053?is_from_webapp=1&sender_device=pc",
    "https://www.tiktok.com/@overtime/video/7626609471468408078?is_from_webapp=1&sender_device=pc",  # Will become Rank #3
    "https://www.tiktok.com/@hoopsnation/video/7470697942622539051?is_from_webapp=1&sender_device=pc",
    "https://www.tiktok.com/@breakanklesdaily/video/7118213436248542506?is_from_webapp=1&sender_device=pc",  # Will become Rank #2
    "https://www.tiktok.com/@hooperzgod/video/6970740966407933189?is_from_webapp=1&sender_device=pc",   # Will become Rank #1 (Best)
    "https://www.tiktok.com/@breakanklesdaily/video/6921773708533140741?is_from_webapp=1&sender_device=pc"
]

# =====================================================================
# 2. DESIGN & MASTER LAYOUT CONFIGURATION
# =====================================================================
# We force a uniform canvas size so the banner stretches edge-to-edge every time
MASTER_WIDTH = 1080           
MASTER_HEIGHT = 1920          
FONT_PATH = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

# Title Settings
TITLE_FONT_SIZE = 55          
TITLE_COLOR = "Red"       
TITLE_STROKE_COLOR = "white"
TITLE_STROKE_WIDTH = 7
TITLE_BANNER_HEIGHT = 220     # Height of the top black bar

# Left-Side Number List Settings
LIST_PADDING_LEFT = 80        # Pushed in slightly more to look better on a 1080p canvas
LIST_START_Y = 550            
LIST_SPACING_Y = 120          

INACTIVE_FONT_SIZE = 45
INACTIVE_COLOR = "white"
INACTIVE_STROKE_WIDTH = 3

ACTIVE_FONT_SIZE = 65
ACTIVE_COLOR = "yellow"
ACTIVE_STROKE_WIDTH = 7

# =====================================================================
# AUTOMATION ENGINE
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
        
        # Scale the clip to fit inside the master canvas while keeping aspect ratio
        scaled_clip = trimmed_clip.resized(width=MASTER_WIDTH)
        if scaled_clip.h > MASTER_HEIGHT:
            scaled_clip = scaled_clip.resized(height=MASTER_HEIGHT)
        
        # Center the video clip onto the master canvas background
        scaled_clip = scaled_clip.with_position(('center', 'center'))
        
        layers = [scaled_clip]

        # --- A. BUILD MAIN TITLE FULL-WIDTH BANNER ---
        # size=(MASTER_WIDTH, ...) locks the text box perfectly edge-to-edge 
        title_clip = TextClip(
            text=VIDEO_TITLE,
            font=FONT_PATH,
            font_size=TITLE_FONT_SIZE,
            color=TITLE_COLOR,
            stroke_color=TITLE_STROKE_COLOR,
            stroke_width=TITLE_STROKE_WIDTH,
            size=(MASTER_WIDTH, TITLE_BANNER_HEIGHT), 
            method="caption",
            text_align="center",
            bg_color=(10, 10, 10, 240)    # Strong black masking bar
        )
        # Anchor the banner flush to the absolute top (0) of the canvas
        title_clip = title_clip.with_position((0, 0)).with_duration(trimmed_clip.duration)
        layers.append(title_clip)

        # --- B. BUILD LEFT-SIDE RANKING LIST ---
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

        # Compile everything on top of a solid 1080x1920 canvas size
        final_clip = CompositeVideoClip(layers, size=(MASTER_WIDTH, MASTER_HEIGHT))
        processed_clips.append(final_clip)

    # Step 4: Save & Compile
    if processed_clips:
        print("\n[4/4] Stitching final video output file...")
        output_filename = "cinematic_ranking_compilation.mp4"
        
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
