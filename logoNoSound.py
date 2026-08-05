import os
import asyncio
import edge_tts
import sys
import random
import subprocess
import numpy as np
from yt_dlp import YoutubeDL
from moviepy import VideoFileClip, concatenate_videoclips, TextClip, CompositeVideoClip, ImageClip, AudioFileClip, CompositeAudioClip
import moviepy.video.fx as vfx
from moviepy.video.fx import FadeIn
from moviepy import concatenate_audioclips

# =====================================================================
# 1. TEXT CONTENT CONFIGURATION (Change these for every new video)
# =====================================================================
VIDEO_TITLE = "Ranking Awesome Must See Trickshots"
CLIP_DURATION = 12

RANK_LABELS = {
    #8: " What. ",
    #7: " Damn. ",
    #6: " Crazy. ",
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
    #7: "red",
    #6: "orange",
    5: "blue",
    4: "white",
    3: "green",
    2: "white",
    1: "red"
}

# Configure your video links below.
TIKTOK_URLS = [
        {"url": "https://www.tiktok.com/@trickshottitan/video/7474599300962585902?is_from_webapp=1&sender_device=pc&web_id=7659949271056631310", "start": 7, "end": 12.5},
        {"url": "https://www.tiktok.com/@firstrytrickshot/video/7475527938159480107?is_from_webapp=1&sender_device=pc&web_id=7659949271056631310", "start": 24, "end": 34},
        {"url": "https://www.tiktok.com/@jmtrickshots/video/6639796630176402694?is_from_webapp=1&sender_device=pc&web_id=7659949271056631310", "start": 2, "end": 16},
        {"url": "https://www.tiktok.com/@trickshot_ceo/video/7483671888586198303?is_from_webapp=1&sender_device=pc&web_id=7659949271056631310", "start": 26, "end": 32.5},
        {"url": "https://www.tiktok.com/@backtosportz/video/7316035656285834526?is_from_webapp=1&sender_device=pc&web_id=7659949271056631310", "start": 21, "end": 36},
        #{"url": "https://www.tiktok.com/@espn/video/7366012887141256490?is_from_webapp=1&sender_device=pc&web_id=7659949271056631310"}, #"start": 18, "end": 38},
]

# =====================================================================
# 2. DESIGN & MASTER LAYOUT CONFIGURATION
# =====================================================================
MASTER_WIDTH = 1080
MASTER_HEIGHT = 1920
FONT_PATH = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

VIDEO_X_OFFSET = 75

# Title Settings
TITLE_FONT_SIZE = 85
TITLE_COLOR = "red"
TITLE_STROKE_COLOR = "white"
TITLE_STROKE_WIDTH = 4
TITLE_BANNER_HEIGHT = 220

# Left-Side Number List Settings
LIST_PADDING_LEFT = 60
LIST_START_Y = 550
LIST_SPACING_Y = 225

# Inactive Ranks
INACTIVE_FONT_SIZE = 55
INACTIVE_NUM_COLOR = "white"
INACTIVE_LABEL_COLOR = "#00FFFF"
INACTIVE_STROKE_WIDTH = 6
INACTIVE_STROKE_COLOR = "white"

# Active Rank
ACTIVE_FONT_SIZE = 90
ACTIVE_COLOR = "yellow"
ACTIVE_STROKE_WIDTH = 6
ACTIVE_STROKE_COLOR = "red"

VOICEOVER_PHRASES = {
    "top_ranks": [
        "... Certified... BANGER!",
        "! Absolute... madness!!",
        "... Unreal scenes right here.",
        "! Total... masterpiece!",
        "... Pure, raw gold."
    ],
    "mid_ranks": [
        "... Clean bounce! Love to see it.",
        "! Zero luck... all skill.",
        ". Too easy for them.",
        "... Ridiculous angle!",
        ". Completely optimal precision."
    ],
    "brand_themed": [
        "RUNNIN RANKS... Level up!",
        "RUNNIN RANKS! Lock it down.",
        "RUNNIN RANKS... Heavy weight styling.",
        "RUNNIN RANKS! Pure swagger.",
        "RUNNIN RANKS... Stealing the show."
    ],
    "funny_roasts": [
        "... Calculated luck, surely!",
        "! Flexing on them, wow.",
        "... Physics has left the building.",
        "! Show off!"
    ]
}

# =====================================================================
# AUTOMATION ENGINE (PART 1)
# =====================================================================

#helper function to generate voice files
def generate_ai_voice(text, output_mp3_path, voice_name="en-IE-ConnorNeural"):
    """
    Generates a highly expressive, punchy UK male character voiceover.
    Alternative highly expressive option to try: "en-IE-ConnorNeural"
    """

    async def _create():
        # Shifting the speech rate to +12% adds a clean, sharp tempo to the dialect
        communicate = edge_tts.Communicate(text, voice_name, rate="+12%")
        await communicate.save(output_mp3_path)

    asyncio.run(_create())

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
        'cookiesfrombrowser': ('firefox',),  
    }

    print(f"\n[1/4] Downloading {len(TIKTOK_URLS)} TikTok videos...")
    with YoutubeDL(ydl_opts) as ydl:
        for item in TIKTOK_URLS:
            url = item["url"]  
            try:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                if not filename.endswith('.mp4'):
                    filename = os.path.splitext(filename) + '.mp4'
                downloaded_files.append(filename)
                item["filename_cache"] = filename 
            except Exception as e:
                print(f"Failed to download {url}. Error: {e}")

    print("\n[2/4] Shuffling video play order...")
    random.shuffle(TIKTOK_URLS) 
    downloaded_files = [item["filename_cache"] for item in TIKTOK_URLS if "filename_cache" in item]
    print(" -> New video sequence generated successfully!")

    print("\n[3/4] Processing clips and building layout...")
    processed_clips = []
    total_clips = len(downloaded_files)

    for index, file_path in enumerate(downloaded_files):
        if not os.path.exists(file_path):
            continue

        current_rank_num = total_clips - index
        print(f" -> Position {index + 1} assigned to: {current_rank_num}.")
        
        full_clip = VideoFileClip(file_path)
        matched_config = next((item for item in TIKTOK_URLS if item.get("filename_cache") == file_path), None)
        
        if matched_config and "start" in matched_config and "end" in matched_config:
            start_time = max(0, matched_config["start"])
            end_time = min(full_clip.duration, matched_config["end"])
        else:
            start_time = 0
            end_time = min(CLIP_DURATION, full_clip.duration)
            
        trimmed_clip = full_clip.subclipped(start_time, end_time)

        # --- DYNAMIC SELECTION LOGIC WITH ULTRA PUNCHY WORDING ---
        if current_rank_num == 1:
            chosen_category = random.choice(["top_ranks", "brand_themed"])
        elif current_rank_num == 2:
            chosen_category = random.choice(["top_ranks", "mid_ranks", "funny_roasts"])
        else:
            chosen_category = random.choice(["mid_ranks", "brand_themed", "funny_roasts"])
            
        raw_template = random.choice(VOICEOVER_PHRASES[chosen_category])
        chosen_script = raw_template.format(num=current_rank_num)

        temp_voice_path = f"temp_voice_{current_rank_num}.mp3"
        print(f"   -> [{chosen_category.upper()}] Generating AI Voiceover: '{chosen_script}'")
        generate_ai_voice(chosen_script, temp_voice_path)

        # --- AUDIO HARMONIZATION LAYER MIXING ---
        stinger_audio_path = "punch_stinger.mp3"
        
        if os.path.exists(temp_voice_path) and os.path.exists(stinger_audio_path):
            stinger_audio = AudioFileClip(stinger_audio_path).with_start(0.1).with_volume_scaled(1.4)
            voice_audio = AudioFileClip(temp_voice_path).with_start(0.3).with_volume_scaled(1.9)
            
            audio_layers = [stinger_audio, voice_audio]
            if trimmed_clip.audio:
                # Crush background original volume factor to let voice pop cleanly without echoes
                ducked_original_audio = trimmed_clip.audio.with_volume_scaled(0.08)
                audio_layers.insert(0, ducked_original_audio)
                
            mixed_audio = CompositeAudioClip(audio_layers)
            trimmed_clip = trimmed_clip.with_audio(mixed_audio)
        
        scaled_clip = trimmed_clip.resized(height=MASTER_HEIGHT - (TITLE_BANNER_HEIGHT * 2))
        if scaled_clip.w > MASTER_WIDTH:
            scaled_clip = scaled_clip.resized(width=MASTER_WIDTH)

        new_w = scaled_clip.w if scaled_clip.w % 2 == 0 else scaled_clip.w - 1
        new_h = scaled_clip.h if scaled_clip.h % 2 == 0 else scaled_clip.h - 1
        scaled_clip = scaled_clip.resized((new_w, new_h))    
        
        x_position = (MASTER_WIDTH - scaled_clip.w) // 2 + VIDEO_X_OFFSET
        scaled_clip = scaled_clip.with_position((x_position, 'center'))
        
        layers = [scaled_clip]

        title_clip = TextClip(
            text=VIDEO_TITLE, font=FONT_PATH, font_size=TITLE_FONT_SIZE, color=TITLE_COLOR,
            stroke_color=TITLE_STROKE_COLOR, stroke_width=TITLE_STROKE_WIDTH,
            size=(MASTER_WIDTH, TITLE_BANNER_HEIGHT), method="caption", text_align="center", bg_color=(10, 10, 10, 240)    
        )
        title_clip = title_clip.with_position((0, 0)).with_duration(trimmed_clip.duration)
        layers.append(title_clip)

        for r in range(total_clips, 0, -1):
            is_active = (r == current_rank_num)
            text_size = ACTIVE_FONT_SIZE if is_active else INACTIVE_FONT_SIZE
            stroke_w = ACTIVE_STROKE_WIDTH if is_active else INACTIVE_STROKE_WIDTH
            
            if is_active:
                num_color = ACTIVE_COLOR
                label_color = ACTIVE_COLOR
            else:
                num_color = RANK_COLORS.get(r, "white")
                label_color = RANK_COLORS.get(r, "white") 
            
            label_text = RANK_LABELS.get(r, "")
            
            num_clip = TextClip(
                text=f"{r}. ", font=FONT_PATH, font_size=text_size, color=num_color,
                stroke_color='black', stroke_width=stroke_w, method="label"
            )
            label_clip = TextClip(
                text=label_text, font=FONT_PATH, font_size=text_size, color=label_color,
                stroke_color='black', stroke_width=stroke_w, method="label"
            )
            
            y_pos = LIST_START_Y + ((total_clips - r) * LIST_SPACING_Y)
            num_clip = num_clip.with_position((LIST_PADDING_LEFT, y_pos)).with_duration(trimmed_clip.duration)
            label_clip = label_clip.with_position((LIST_PADDING_LEFT + 70, y_pos)).with_duration(trimmed_clip.duration)
            
            layers.append(num_clip)
            layers.append(label_clip)

        final_clip = CompositeVideoClip(layers, size=(MASTER_WIDTH, MASTER_HEIGHT))
        if len(processed_clips) > 0:
            final_clip = final_clip.with_effects([FadeIn(0.5)])
            
        processed_clips.append(final_clip)

    # Step 4: Save & Apply Clear Outro Audio
    if processed_clips:
        print("\n[4/4] Stitching final video output file with transitions...")
        temp_filename = "temp_unbranded_compilation.mp4"
        output_filename = "ultimate_ranking_compilation.mp4"
        
        final_compilation = concatenate_videoclips(processed_clips, method="compose", padding=-0.5)
        final_compilation.write_videofile(temp_filename, fps=30, codec="libx264", audio_codec="aac")
        
        final_compilation.close()
        for clip in processed_clips:
            clip.close()

        print("\n⚡ Integrating the Runnin Ranks Logo Outro + Sound Effects...")
        scratch_audio_path = "record_scratch.mp3"
        bruh_audio_path = "deep_bruh.mp3"
        logo_path = "channel_logo.png"
        
        if not os.path.exists(scratch_audio_path) or not os.path.exists(bruh_audio_path) or not os.path.exists(logo_path):
            print("❌ Error: Missing record_scratch.mp3, deep_bruh.mp3, or channel_logo.png!")
            sys.exit(1)

        master_video = VideoFileClip(temp_filename)
        total_duration = master_video.duration
        
        scratch_duration = 0.5
        bruh_duration = 1.0
        total_outro_duration = scratch_duration + bruh_duration  
        
        freeze_start_time = total_duration - total_outro_duration
        scratch_start_time = freeze_start_time
        bruh_start_time = freeze_start_time + scratch_duration

        # 1. Visual Slice Configuration
        normal_video_part = master_video.subclipped(0, freeze_start_time).without_audio()
        
        # 2. Freeze frame conversion to B&W
        freeze_frame = master_video.get_frame(freeze_start_time)
        bw_image = np.dstack([np.mean(freeze_frame, axis=2)] * 3).astype('uint8')
        bw_frozen_clip = ImageClip(bw_image).with_duration(total_outro_duration).with_start(freeze_start_time).without_audio()

        # 3. Logo Layer Configuration
        logo_clip = (ImageClip(logo_path)
                     .with_duration(bruh_duration)
                     .with_start(bruh_start_time)
                     .resized(width=550)  
                     .with_effects([vfx.Rotate(-10, expand=True)])
                     .without_audio()
                     .with_position(("center", "center")))

        final_video_layers = [normal_video_part, bw_frozen_clip, logo_clip]
        final_branded_video = CompositeVideoClip(final_video_layers, size=(MASTER_WIDTH, MASTER_HEIGHT))
        
        # --- THE CLEAN AUDIO PIPELINE ---
        clean_base_audio = master_video.audio.copy()
        
        scratch_audio = AudioFileClip(scratch_audio_path).with_start(scratch_start_time)
        bruh_audio = AudioFileClip(bruh_audio_path).with_start(bruh_start_time).with_volume_scaled(1.5)
        sfx_overlay = CompositeAudioClip([scratch_audio, bruh_audio])
        
        final_audio = CompositeAudioClip([clean_base_audio, sfx_overlay])
        final_branded_video = final_branded_video.with_audio(final_audio)

        final_branded_video.write_videofile(
            output_filename, fps=30, codec="libx264", audio_codec="aac",
            temp_audiofile="temp-audio.m4a", remove_temp=True
        )
        
        master_video.close()
        final_branded_video.close()
        
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
        for i in range(1, total_clips + 1):
            t_v = f"temp_voice_{i}.mp3"
            if os.path.exists(t_v):
                os.remove(t_v)
        for file in downloaded_files:
            if os.path.exists(file):
                os.remove(file)
                
        print(f"\n✅ Success! Open your folder to find: {output_filename}")
    else:
        print("\nProcess failed: No clips were successfully compiled.")

if __name__ == "__main__":
    main()