import os
import sys
import random
from yt_dlp import YoutubeDL
from moviepy import VideoFileClip, concatenate_videoclips, TextClip, CompositeVideoClip
import moviepy.video.fx as vfx
from moviepy.video.fx import FadeIn

# =====================================================================
# 1. TEXT CONTENT CONFIGURATION (Change these for every new video)
# =====================================================================
VIDEO_TITLE = "Ranking Awesome Must See Trickshots"
CLIP_DURATION = 12             

RANK_LABELS = {
    
    #8: " What. ",
    #7: " Damn. ",
    6: " Crazy. ",
    5: " Huh.",
    4: " Ah.",
    3: " Huh.",
    2: " Wow.",
    1: " Brah."
}
# =====================================================================
# CUSTOM ROW COLORS: Assign a unique color to each specific line!
# Accepts standard names like 'red', 'cyan', or custom Hex codes.
# =====================================================================
RANK_COLORS = {

    #8: "orange",
    #7: "red",  # Line 6 text will be 
    6: "orange",  # Line 6 text will be
    5: "blue",  # Line 5 text will be 
    4: "white",  # Line 4 text will be 
    3: "green",   # Line 3 text will be 
    2: "white",  # Line 2 text will be 
    1: "red"   # Line 1 text will be 
}


# Configure your video links below. 
# You can optionally add 'start' and 'end' seconds to manually trim a specific clip!
TIKTOK_URLS = [
    {"url": "https://www.tiktok.com/@espn/video/7640878738661461279?is_from_webapp=1&sender_device=pc&web_id=7659949271056631310", "start": 0, "end": 15},
    {"url": "https://www.tiktok.com/@hulett_brothers/video/7145946399455317294?is_from_webapp=1&sender_device=pc&web_id=7659949271056631310", "start": 40, "end": 46.5},
    {"url": "https://www.tiktok.com/@trickshotbros.93/video/7666225847296167182?is_from_webapp=1&sender_device=pc&web_id=7659949271056631310", "start": 23.5, "end": 30}, 
    {"url": "https://www.tiktok.com/@thatll.work/video/6974071715513044230?is_from_webapp=1&sender_device=pc&web_id=7659949271056631310", "start": 41.5, "end": 45.5},
    {"url": "https://www.tiktok.com/@adambobrowofficial/video/7485996460039834910?is_from_webapp=1&sender_device=pc&web_id=7659949271056631310"}, #"start": 22, "end": 26.5},
    {"url": "https://www.tiktok.com/@espn/video/7366012887141256490?is_from_webapp=1&sender_device=pc&web_id=7659949271056631310"}, #"start": 18, "end": 38},
    #{"url": "https://www.tiktok.com/@lavander1237/video/7560347294961339704?is_from_webapp=1&sender_device=pc&web_id=7659949271056631310"}, #"start": 20, "end": 23}
    #{"url": "https://www.tiktok.com/@nate.shockey/video/7579753301583875359?is_from_webapp=1&sender_device=pc&web_id=7659949271056631310"}
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
VIDEO_X_OFFSET = 75 #was 180          

# Title Settings
TITLE_FONT_SIZE = 85          
TITLE_COLOR = "red"       
TITLE_STROKE_COLOR = "white"
TITLE_STROKE_WIDTH = 4
TITLE_BANNER_HEIGHT = 220     

# Left-Side Number List Settings
LIST_PADDING_LEFT = 60        
LIST_START_Y = 550           
LIST_SPACING_Y = 225 #was 130, then 160, 255 latest

# --- NEW COLOR CONTROLS FOR THE LIST ---
# Inactive Ranks (Default view for list items not currently playing)
INACTIVE_FONT_SIZE = 55
INACTIVE_NUM_COLOR = "white"      # The color of the number (e.g., "5.")
INACTIVE_LABEL_COLOR = "#00FFFF"  # The color of the text words (e.g., "Wildest Play") - Accepts hex or color names!
INACTIVE_STROKE_WIDTH = 6
INACTIVE_STROKE_COLOR = "white"

# Active Rank (The clip currently playing on screen)
ACTIVE_FONT_SIZE = 90
ACTIVE_COLOR = "yellow"           # Active line turns entirely Yellow to pop out
ACTIVE_STROKE_WIDTH = 6
ACTIVE_STROKE_COLOR = "red"

#INACTIVE_FONT_SIZE = 45
#INACTIVE_COLOR = "white"
#INACTIVE_STROKE_WIDTH = 3
#
#ACTIVE_FONT_SIZE = 55
#ACTIVE_COLOR = "yellow"
#ACTIVE_STROKE_WIDTH = 5

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
        for item in TIKTOK_URLS:
            url = item["url"]  # Extracts the actual link string cleanly
            try:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                if not filename.endswith('.mp4'):
                    filename = os.path.splitext(filename) + '.mp4'
                downloaded_files.append(filename)
                item["filename_cache"] = filename # Remembers which downloaded file belongs to this link
            except Exception as e:
                print(f"Failed to download {url}. Error: {e}")

    # Step 2: Shuffle
    #print("\n[2/4] Shuffling video play order...")
    #random.shuffle(downloaded_files)
    #print(" -> New video sequence generated successfully!")

    print("\n[2/4] Shuffling video play order...")
    random.shuffle(TIKTOK_URLS) # Shuffles the master config dictionary list
    
    # Rebuild downloaded_files list based on the new randomized dictionary order
    downloaded_files = [item["filename_cache"] for item in TIKTOK_URLS if "filename_cache" in item]
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
        #end_time = min(CLIP_DURATION, full_clip.duration)
        #trimmed_clip = full_clip.subclipped(0, end_time)

        # --- NEW: DYNAMIC OVERRIDE TRIMMING LOGIC ---
        # Find the original link dictionary configuration that matches this downloaded file
        # (We search our list to check if you gave it custom start/end timestamps)
        matched_config = next((item for item in TIKTOK_URLS if item.get("filename_cache") == file_path), None)
        
        if matched_config and "start" in matched_config and "end" in matched_config:
            # Safely clamp timestamps to the video's actual physical boundary limitations
            start_time = max(0, matched_config["start"])
            end_time = min(full_clip.duration, matched_config["end"])
            print(f"   -> Applying custom manual trim: Playing from {start_time}s to {end_time}s")
        else:
            # Default fallback rule if no custom values were provided at the top
            start_time = 0
            end_time = min(CLIP_DURATION, full_clip.duration)
            print(f"   -> Using default timing parameters: Playing from 0s to {end_time}s")
            
        trimmed_clip = full_clip.subclipped(start_time, end_time)
        
        # Scale the clip to fit the master layout height comfortably
        scaled_clip = trimmed_clip.resized(height=MASTER_HEIGHT - (TITLE_BANNER_HEIGHT * 2))
        if scaled_clip.w > MASTER_WIDTH:
            scaled_clip = scaled_clip.resized(width=MASTER_WIDTH)

        # --- FIX: FORCE EVEN DIMENSIONS FOR THE VIDEO MASK ---
        new_w = scaled_clip.w if scaled_clip.w % 2 == 0 else scaled_clip.w - 1
        new_h = scaled_clip.h if scaled_clip.h % 2 == 0 else scaled_clip.h - 1
        scaled_clip = scaled_clip.resized((new_w, new_h))    
        
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

        # --- B. BUILD LEFT-SIDE RANKING LIST WITH INDEPENDENT WORD COLORS ---
        for r in range(total_clips, 0, -1):
            is_active = (r == current_rank_num)
            
            # Master State Styling
            text_size = ACTIVE_FONT_SIZE if is_active else INACTIVE_FONT_SIZE
            stroke_w = ACTIVE_STROKE_WIDTH if is_active else INACTIVE_STROKE_WIDTH
            
            # --- COLOR SHIFT RULE ---
            # Active items turn completely yellow. Inactive lines split colors: White numbers + Cyan descriptions!
            #num_color = "yellow" if is_active else "white"
            #label_color = "yellow" if is_active else "#00FFFF"
            # If the rank is currently playing, keep it highlighted in your main ACTIVE_COLOR.
            # If it's inactive, pull its custom unique color from the RANK_COLORS dictionary!
            if is_active:
                num_color = ACTIVE_COLOR
                label_color = ACTIVE_COLOR
            else:
                # .get(r, "white") acts as a backup color if you forget to add a rank to the dictionary
                num_color = RANK_COLORS.get(r, "white")
                label_color = RANK_COLORS.get(r, "white") 
            
            label_text = RANK_LABELS.get(r, "")
            
            # 1. Create the Number Dot Prefix Clip
            num_clip = TextClip(
                text=f"{r}. ",
                font=FONT_PATH,
                font_size=text_size,
                color=num_color,
                stroke_color='black',
                stroke_width=stroke_w,
                method="label" # Keep it as standard v2 label mode
            )
            
            # 2. Create the Description Label Clip
            label_clip = TextClip(
                text=label_text,
                font=FONT_PATH,
                font_size=text_size,
                color=label_color, # Applies your custom color string independently
                stroke_color='black',
                stroke_width=stroke_w,
                method="label"
            )
            
            y_pos = LIST_START_Y + ((total_clips - r) * LIST_SPACING_Y)
            
            # Position the Number on the far left edge
            num_clip = num_clip.with_position((LIST_PADDING_LEFT, y_pos)).with_duration(trimmed_clip.duration)
            
            # Shift the Description Label text further right (e.g. +70px) so it sits directly after the dot!
            label_clip = label_clip.with_position((LIST_PADDING_LEFT + 70, y_pos)).with_duration(trimmed_clip.duration)
            
            layers.append(num_clip)
            layers.append(label_clip)

        # Compile layers onto master canvas
        final_clip = CompositeVideoClip(layers, size=(MASTER_WIDTH, MASTER_HEIGHT))
        
        # --- NEW: APPLY CROSSFADE TRANSITION ENTRY ---
        # We blend each multi-layered segment seamlessly as it transitions onto screen
        if len(processed_clips) > 0:
            #final_clip = CrossFadeIn(final_clip, 0.5)
            #final_clip = final_clip.with_effects([vfx.CrossFadeIn(0.5)])
            #from moviepy.video.fx import fadein
            final_clip = final_clip.with_effects([FadeIn(0.5)])
            
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
