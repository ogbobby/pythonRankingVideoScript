import os
import sys
import random
from yt_dlp import YoutubeDL
from moviepy import VideoFileClip, concatenate_videoclips, TextClip, CompositeVideoClip
import moviepy.video.fx as vfx
#Next is skydiving fails, and nature fails
# =====================================================================
# 1. TEXT CONTENT CONFIGURATION (Change these for every new video)
# =====================================================================
VIDEO_TITLE = "Insane Parkour Fails"  
CLIP_DURATION = 10             

RANK_LABELS = {
    5: "Yo.",
    4: "What.",
    3: "Brah.",
    2: "Lol.",
    1: "Oh."
}

TIKTOK_URLS = [
    "https://www.tiktok.com/@olivernordin1/video/7436829959026494742?is_from_webapp=1&sender_device=pc",
    "https://www.tiktok.com/@fantasthenics/video/7057539990460435718?is_from_webapp=1&sender_device=pc",  # Will become Rank #3
    "https://www.tiktok.com/@thebrycetanner/video/6826077314942651653?is_from_webapp=1&sender_device=pc",   # Will become Rank #1 (Best)
    "https://www.tiktok.com/@dominick_hughes/video/6818623419936984326?is_from_webapp=1&sender_device=pc",
    "https://www.tiktok.com/@espn/video/7642010602336046366?is_from_webapp=1&sender_device=pc",  # Will become Rank #2
]

# =====================================================================
# 2. DESIGN & MASTER LAYOUT CONFIGURATION
# =====================================================================
MASTER_WIDTH = 1080           
MASTER_HEIGHT = 1920          
FONT_PATH = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

# --- NEW: AUTO-ADJUST BACKDROP POSITION ---
# Shifts the background video clip to the right (in pixels) to avoid text overlap.
# Set to 0 if you want the clip perfectly centered.
VIDEO_X_OFFSET = 180          

# Title Settings
TITLE_FONT_SIZE = 65          
TITLE_COLOR = "red"       
TITLE_STROKE_COLOR = "white"
TITLE_STROKE_WIDTH = 6
TITLE_BANNER_HEIGHT = 220     

# Left-Side Number List Settings
LIST_PADDING_LEFT = 60        
LIST_START_Y = 550            
LIST_SPACING_Y = 130          

INACTIVE_FONT_SIZE = 45
INACTIVE_COLOR = "white"
INACTIVE_STROKE_WIDTH = 3

ACTIVE_FONT_SIZE = 55
ACTIVE_COLOR = "yellow"
ACTIVE_STROKE_WIDTH = 5

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
        'quiet': True,
        # --- NEW: BYPASS AGE GATES & SENSITIVE POSTS ---
        # Tells the script to borrow your browser's active login token to prove you are an adult
        'cookiesfrombrowser': ('firefox',),  # Options: 'chrome', 'firefox
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
        
        # Scale the clip to fit the master layout height comfortably
        scaled_clip = trimmed_clip.resized(height=MASTER_HEIGHT - (TITLE_BANNER_HEIGHT * 2))
        if scaled_clip.w > MASTER_WIDTH:
            scaled_clip = scaled_clip.resized(width=MASTER_WIDTH)
        
        # --- SHIFT VIDEO POSITION RIGHT ---
        # Calculates horizontal center, then injects our offset to slide the video right
        x_position = (MASTER_WIDTH - scaled_clip.w) // 2 + VIDEO_X_OFFSET
        scaled_clip = scaled_clip.with_position((x_position, 'center'))
        
        layers = [scaled_clip]

        # --- A. BUILD MAIN TITLE FULL-WIDTH BANNER ---
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
            bg_color=(10, 10, 10, 240)    
        )
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

        # Compile layers onto master canvas
        final_clip = CompositeVideoClip(layers, size=(MASTER_WIDTH, MASTER_HEIGHT))
        
        # --- NEW: APPLY CROSSFADE TRANSITION ENTRY ---
        # We blend each multi-layered segment seamlessly as it transitions onto screen
        if len(processed_clips) > 0:
            #final_clip = CrossFadeIn(final_clip, 0.5)
            final_clip = final_clip.with_effects([vfx.CrossFadeIn(0.5)])
            
        processed_clips.append(final_clip)

    # Step 4: Save & Compile
    if processed_clips:
        print("\n[4/4] Stitching final video output file with transitions...")
        output_filename = "ultimate_ranking_compilation.mp4"
        
        # padding=-0.5 overlaps the clips slightly so the crossfade has frames to blend together
        final_compilation = concatenate_videoclips(processed_clips, method="compose", padding=-0.5)
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
