import os
import sys
import random
from yt_dlp import YoutubeDL
from moviepy import VideoFileClip, concatenate_videoclips, TextClip, CompositeVideoClip

# =====================================================================
# CONFIGURATION: Paste all your TikTok or Shorts source links below.
# =====================================================================
TIKTOK_URLS = [
    "https://www.tiktok.com/@overtime/video/7626609471468408078?is_from_webapp=1&sender_device=pc",  # Will become Rank #3
    "https://www.tiktok.com/@breakanklesdaily/video/7118213436248542506?is_from_webapp=1&sender_device=pc",  # Will become Rank #2
    "https://www.tiktok.com/@hooperzgod/video/6970740966407933189?is_from_webapp=1&sender_device=pc"   # Will become Rank #1 (Best)
]

VIDEO_TITLE = "Insane Man"  # Change this to your main title text
CLIP_DURATION = 7             # Duration of each clip in seconds
FONT_PATH = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

# =====================================================================
# CUSTOM LIST LABELS: Customize the text that appears next to each number.
# Make sure you provide text for every rank number you have in your list!
# =====================================================================
RANK_LABELS = {
    5: "Wildest Play",
    4: "Insane Save",
    3: "Close Call",
    2: "Runner Up",
    1: "The Winner"
}

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

        # --- A. BUILD MAIN TITLE AT TOP WITH STROKE/OUTLINE ---
        title_clip = TextClip(
            text=VIDEO_TITLE,
            font=FONT_PATH,
            font_size=75,
            color='white',
            stroke_color='black',  # The border color
            stroke_width=5        # The thickness of the border text effect
        )
        title_clip = title_clip.with_position(('center', 40)).with_duration(trimmed_clip.duration)
        layers.append(title_clip)

        # --- B. BUILD LEFT-SIDE RANKING LIST WITH LABELS ---
        start_y_position = 250  
        spacing_y = 110         
        
        for r in range(total_clips, 0, -1):
            is_active = (r == current_rank_num)
            text_color = 'yellow' if is_active else 'white'
            text_size = 75 if is_active else 60
            stroke_w = 4 if is_active else 2
            
            # Get the custom label text or fallback to blank if missing
            label_text = RANK_LABELS.get(r, "")
            # Combine the new "X." number layout with your custom text line
            display_string = f"{r}. {label_text}"
            
            list_item_clip = TextClip(
                text=display_string,
                font=FONT_PATH,
                font_size=text_size,
                color=text_color,
                stroke_color='black',
                stroke_width=stroke_w
            )
            
            y_pos = start_y_position + ((total_clips - r) * spacing_y)
            # Position the entire line neatly padded on the left side
            list_item_clip = list_item_clip.with_position((50, y_pos)).with_duration(trimmed_clip.duration)
            layers.append(list_item_clip)

        final_clip = CompositeVideoClip(layers)
        processed_clips.append(final_clip)

    # Step 4: Save & Compile
    if processed_clips:
        print("\n[4/4] Stitching final video output file...")
        output_filename = "styled_ranking_compilation.mp4"
        
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
