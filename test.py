import os
import asyncio
import edge_tts
import sys
import random
import subprocess
import numpy as np
import requests
import time
import re
from yt_dlp import YoutubeDL
from urllib.parse import urlparse, urlunparse
import moviepy.audio.fx as afx
from moviepy import VideoFileClip, concatenate_videoclips, TextClip, CompositeVideoClip, ImageClip, AudioFileClip, CompositeAudioClip
import moviepy.video.fx as vfx
from moviepy.video.fx import FadeIn
from moviepy import concatenate_audioclips

# =====================================================================
# 1. TEXT CONTENT CONFIGURATION (Change these for every new video)
# =====================================================================
VIDEO_TITLE = "Ranking Ultra Elite Trickshots"
CLIP_DURATION = 12

RANK_LABELS = {
    #8: " What. ",
    #7: " Damn. ",
    #6: " Crazy. ",
    5: "Crazy ",
    4: "Wow ",
    3: "Insane ",
    2: "Amazing ",
    1: "Brah. "
}

# =====================================================================
# CUSTOM ROW COLORS: Assign a unique color to each specific line!
# Accepts standard names like 'red', 'cyan', or custom Hex codes.
# =====================================================================
RANK_COLORS = {
    #8: "orange",
    #7: "red",
    #6: "orange",
    5: "orange",
    4: "blue",
    3: "white",
    2: "green",
    1: "red"
}

# =====================================================================
# VIDEO SOURCES CONFIGURATION - MIX TIKTOK AND LOCAL FILES!
# =====================================================================
# For TikTok videos: {"url": "https://www.tiktok.com/..."}
# For local videos: {"local": "path/to/video.mp4"}
# Both support optional "start" and "end" parameters for trimming!
VIDEO_SOURCES = [
    # TikTok videos
    {"url": "https://www.tiktok.com/@flickgodtt/video/7637161501748366614?is_from_webapp=1&sender_device=pc&web_id=7673309675748886029", "start": 8.5, "end": 14.5},
    {"url": "https://www.tiktok.com/@poolstrikertrickshots/video/7506575559737019670?is_from_webapp=1&sender_device=pc&web_id=7673309675748886029"}, #"start": 13, "end": 16.5},
    {"url": "https://www.tiktok.com/@bond442sports/video/7416500608158485802?is_from_webapp=1&sender_device=pc&web_id=7673309675748886029"}, #"start": 0, "end": 5},
    {"url": "https://www.tiktok.com/@nba/video/7375536984409836843?is_from_webapp=1&sender_device=pc&web_id=7673309675748886029", "start": 0, "end": 14},
    {"url": "https://www.tiktok.com/@henrywild96/video/7508931522699742495?is_from_webapp=1&sender_device=pc&web_id=7673309675748886029"}, #"start": 0, "end": 7.5},
    #{"url": "https://www.tiktok.com/@whistle/video/7350125514054438174?is_from_webapp=1&sender_device=pc&web_id=7673309675748886029", "start": 5, "end": 11},

    # Local videos (uncomment and add your own files)
    #{"local": "/home/ogbobby/Documents/git/RedditVideoScraper/library_nextfuckinglevel/nextfuckinglevel/RonaldoInsaneHeader.mp4", "start": 2, "end": 17},
    # {"local": "C:/Users/YourName/Videos/clip2.mp4", "start": 5, "end": 20},
    # {"local": "/home/user/Videos/my_video.mp4"},
]

# =====================================================================
# 2. DESIGN & MASTER LAYOUT CONFIGURATION
# =====================================================================
MASTER_WIDTH = 1080
MASTER_HEIGHT = 1875#was 1920
FONT_PATH = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

VIDEO_X_OFFSET = 75

# Title Settings
TITLE_FONT_SIZE = 85
TITLE_COLOR = "red"
TITLE_STROKE_COLOR = "white"
TITLE_STROKE_WIDTH = 4
TITLE_BANNER_HEIGHT = 220

# Left-Side Number List Settings
LIST_PADDING_LEFT = 60 #was 60
LIST_START_Y = 550 #was 550
LIST_SPACING_Y = 200 # was 225

# Inactive Ranks
INACTIVE_FONT_SIZE = 30 #was 55
INACTIVE_NUM_COLOR = "white"
INACTIVE_LABEL_COLOR = "#00FFFF"
INACTIVE_STROKE_WIDTH = 6
INACTIVE_STROKE_COLOR = "white"

# Active Rank
ACTIVE_FONT_SIZE = 90
ACTIVE_COLOR = "yellow"
ACTIVE_STROKE_WIDTH = 6
ACTIVE_STROKE_COLOR = "red"

# =====================================================================
# HELPER FUNCTIONS
# =====================================================================

def download_tiktok_video(url):
    """Download a TikTok video by passing native extractor arguments to curl-cffi."""
    # Introduce an automation-breaking delay before hitting the backend firewall
    print("   -> Resting connection profile for 5 seconds...")
    time.sleep(5)
    
    ydl_opts = {
        'outtmpl': 'temp_clip_%(id)s.%(ext)s',
        'format': 'bv*[height<=960][ext=mp4]+ba[ext=m4a]/b[ext=mp4]', 
        'merge_output_format': 'mp4',
        'quiet': True,
        'cookiesfrombrowser': ('firefox',),  
        
        # Bypasses the broken 'impersonate' dictionary key check
        'compat_opts': {'no-impersonate-check'},
        
        # FIX: Force the extraction architecture to run purely inside curl-cffi 
        # while explicitly declaring the impersonation layer inside your extractor
        'http_backend': 'curl_cffi',
        'extractor_args': {
            'youtube': {'player_client': 'web'},
            'tiktok': {'impersonate': 'chrome'}
        },
        'ignoreerrors': True
    }
    
    with YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=True)
            if not info:
                # If extraction returns empty, the server dropped a captcha or session expired
                print("   ⚠️ TikTok returned an empty payload. Refreshing browser handshakes required.")
                return None
            filename = ydl.prepare_filename(info)
            
            if not filename.endswith('.mp4'):
                base_path, _ = os.path.splitext(filename)
                filename = base_path + '.mp4'
                
            return filename
        except Exception as e:
            print(f"Failed to download {url}. Error: {e}")
            return None

def process_single_video(source, index, total_clips, processed_clips):
    """Process a single video source (either local or TikTok URL)."""
    current_rank_num = total_clips - index
    
    if "local" in source:
        file_path = source["local"]
        print(f" -> Position {index + 1} assigned to: {current_rank_num}. (Local file: {os.path.basename(file_path)})")
        if not os.path.exists(file_path):
            print(f"   ⚠️ Warning: Local file not found: {file_path}")
            return None
    elif "url" in source:
        print(f" -> Position {index + 1} assigned to: {current_rank_num}. (Downloading TikTok...)")
        file_path = download_tiktok_video(source["url"])
        if not file_path:
            return None
        source["filename_cache"] = file_path
    else:
        print(f"   ⚠️ Warning: Invalid source format at position {index + 1}")
        return None
    
    try:
        full_clip = VideoFileClip(file_path)
        
        if "start" in source and "end" in source:
            start_time = max(0, source["start"])
            end_time = min(full_clip.duration, source["end"])
            print(f"   -> Applying custom manual trim: Playing from {start_time}s to {end_time}s")
        else:
            start_time = 0
            end_time = min(CLIP_DURATION, full_clip.duration)
            print(f"   -> Using default timing parameters: Playing from 0s to {end_time}s")
        
        trimmed_clip = full_clip.subclipped(start_time, end_time).without_audio()
        
        scaled_clip = trimmed_clip.resized(height=MASTER_HEIGHT - (TITLE_BANNER_HEIGHT * 2))
        if scaled_clip.w > MASTER_WIDTH:
            scaled_clip = scaled_clip.resized(width=MASTER_WIDTH)

        new_w = scaled_clip.w if scaled_clip.w % 2 == 0 else scaled_clip.w - 1
        new_h = scaled_clip.h if scaled_clip.h % 2 == 0 else scaled_clip.h - 1
        scaled_clip = scaled_clip.resized((new_w, new_h))    
        
        x_position = (MASTER_WIDTH - scaled_clip.w) // 2 + VIDEO_X_OFFSET
        y_position = (MASTER_HEIGHT - scaled_clip.h) // 2
        scaled_clip = scaled_clip.with_position((x_position, y_position))
        
        layers = [scaled_clip]

        title_clip = TextClip(
            text=VIDEO_TITLE, font=FONT_PATH, font_size=TITLE_FONT_SIZE, color=TITLE_COLOR,
            stroke_color=TITLE_STROKE_COLOR, stroke_width=TITLE_STROKE_WIDTH,
            size=(MASTER_WIDTH, TITLE_BANNER_HEIGHT), method="caption", text_align="center", bg_color=(10, 10, 10, 240)    
        )
        title_clip = title_clip.with_position((0, 0)).with_duration(trimmed_clip.duration)
        layers.append(title_clip)

        # Ranking list
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
            
            num_box_size = (120, text_size + 40)
            label_box_size = (500, text_size + 40) #was 500

            num_clip = TextClip(
                text=f"{r}. ", font=FONT_PATH, font_size=text_size, color=num_color,
                stroke_color='black', stroke_width=stroke_w, method="caption",
                size=num_box_size, text_align="left"
            )
            
            label_clip = TextClip(
                text=label_text, font=FONT_PATH, font_size=text_size, color=label_color,
                stroke_color='black', stroke_width=stroke_w, method="caption",
                size=label_box_size, text_align="left"
            )
            
            y_pos = LIST_START_Y + ((total_clips - r) * LIST_SPACING_Y)
            
            # This tighter offset pulls the text closer to the numbers
            label_offset = 60 if is_active else 35 #was 75 and 35
            
            num_clip = num_clip.with_position((LIST_PADDING_LEFT, y_pos)).with_duration(trimmed_clip.duration)
            label_clip = label_clip.with_position((LIST_PADDING_LEFT + label_offset, y_pos)).with_duration(trimmed_clip.duration)
            
            layers.append(num_clip)
            layers.append(label_clip)
            
        final_clip = CompositeVideoClip(layers, size=(MASTER_WIDTH, MASTER_HEIGHT))
        return final_clip
    except Exception as e:
        print(f"   ❌ Error processing video: {e}")
        return None

# =====================================================================
# MAIN FUNCTION
# =====================================================================

def main():
    if not VIDEO_SOURCES:
        print("Error: Please add video sources to VIDEO_SOURCES.")
        sys.exit(1)

    print(f"\n[1/4] Preparing to process {len(VIDEO_SOURCES)} video sources...")
    
    # Randomize the order
    print("\n[2/4] Shuffling video play order...")
    random.shuffle(VIDEO_SOURCES)
    print(" -> New video sequence generated successfully!")

    # Process all videos
    print("\n[3/4] Processing clips and building layout...")
    processed_clips = []
    total_clips = len(VIDEO_SOURCES)

    for index, source in enumerate(VIDEO_SOURCES):
        clip = process_single_video(source, index, total_clips, processed_clips)
        if clip:
            processed_clips.append(clip)

    # Step 4: Save, Dynamic Low-Volume Music Mix, and Appended Outro
    if processed_clips:
        print("\n[4/4] Stitching final video output file with transitions...")
        temp_filename = "temp_unbranded_compilation.mp4"
        output_filename = "901.mp4"
        
        # Audio assets and configuration paths
        music_audio_path = "Antique_Prism.mp3"
        scratch_audio_path = "record_scratch.mp3"
        bruh_audio_path = "deep_bruh.mp3"
        logo_path = "channel_logo.png"
        
        # Immediate asset sanity check to prevent pipeline crashes before long render cycles
        if not os.path.exists(music_audio_path) or not os.path.exists(scratch_audio_path) or not os.path.exists(bruh_audio_path) or not os.path.exists(logo_path):
            print(f"❌ Error: Outro assets missing! Make sure '{music_audio_path}', '{scratch_audio_path}', '{bruh_audio_path}', and '{logo_path}' are in this directory.")
            sys.exit(1)
        
        # Render the raw compilation layer structure
        final_compilation = concatenate_videoclips(processed_clips, method="compose", padding=-0.5)
        final_compilation.write_videofile(temp_filename, fps=30, codec="libx264", audio_codec="aac", logger=None)
        
        final_compilation.close()
        for clip in processed_clips:
            clip.close()

        print("\n⚡ Integrating the Runnin Ranks Logo Outro + Balanced Music Mix...")
        master_video = VideoFileClip(temp_filename)
        total_duration = master_video.duration
        
        scratch_duration = 0.5
        bruh_duration = 1.0
        total_outro_duration = scratch_duration + bruh_duration  
        
        freeze_start_time = total_duration - total_outro_duration
        scratch_start_time = freeze_start_time
        bruh_start_time = freeze_start_time + scratch_duration

        # 1. Visual Track Separation: Strip hidden layer variables to completely destroy echoes
        normal_video_part = master_video.subclipped(0, freeze_start_time).without_audio()
        
        # 2. Freeze final frame position and apply Black & White transformation matrix
        freeze_frame = master_video.get_frame(freeze_start_time)
        bw_image = np.dstack([np.mean(freeze_frame, axis=2)] * 3).astype('uint8')
        bw_frozen_clip = ImageClip(bw_image).with_duration(total_outro_duration).with_start(freeze_start_time).without_audio()

        # 3. Scale, orient, and tilt your channel logo overlay matching your banner styling rules
        logo_clip = (ImageClip(logo_path)
                     .with_duration(bruh_duration)
                     .with_start(bruh_start_time)
                     .resized(width=550)  
                     .with_effects([vfx.Rotate(-10, expand=True)])
                     .without_audio()
                     .with_position(("center", "center")))

        # Assemble purely visual components on a 100% silent slate
        final_video_layers = [normal_video_part, bw_frozen_clip, logo_clip]
        final_branded_video = CompositeVideoClip(final_video_layers, size=(MASTER_WIDTH, MASTER_HEIGHT))
        
        # --- THE CLEAN MULTI-TRACK AUDIO PIPELINE ---
        ## A. Pull baseline clean audio directly from the master compilation track
        ##clean_base_audio = master_video.audio.copy()
        # A. Handle the silent clip layout baseline safely to prevent NoneType crashes
        clean_base_audio = master_video.audio.copy() if master_video.audio is not None else None
        # B. Load the background music, program a loop factor matching short lengths, and scale down to 15% volume
        # Change '0.15' to turn your background track up or down.
        # (e.g., 0.10 is 10% volume, 0.25 is 25% volume, 1.0 is full volume)
        bg_music = AudioFileClip(music_audio_path).with_effects([afx.AudioLoop(duration=total_duration)]).with_volume_scaled(0.15)
        
        # C. Sequence out your custom stinger overlay audio tracking points explicitly
        scratch_audio = AudioFileClip(scratch_audio_path).with_start(scratch_start_time)
        bruh_audio = AudioFileClip(bruh_audio_path).with_start(bruh_start_time).with_volume_scaled(1.5)
        sfx_overlay = CompositeAudioClip([scratch_audio, bruh_audio])
        
        ## Flatten all tracks together smoothly on a clean global linear mixer channel
        ##final_audio = CompositeAudioClip([clean_base_audio, bg_music, sfx_overlay])
        # Build the final mix list starting with your background music track and the outro sound effects
        audio_mix_list = [bg_music, sfx_overlay]
        
        # Only inject the base video audio track if it actually exists in system memory
        if clean_base_audio is not None:
            audio_mix_list.insert(0, clean_base_audio)
            
        final_audio = CompositeAudioClip(audio_mix_list)

        final_branded_video = final_branded_video.with_audio(final_audio)

        # Final Render
        final_branded_video.write_videofile(
            output_filename, fps=30, codec="libx264", audio_codec="aac",
            temp_audiofile="temp-audio.m4a", remove_temp=True, logger=None
        )
        
        master_video.close()
        final_branded_video.close()
        
        # --- THE COMPLETE REPAIRED WORKSPACE CLEANUP ENGINE ---
        if os.path.exists(temp_filename):
            try:
                os.remove(temp_filename)
            except Exception as e:
                print(f"   ⚠️ Could not remove temporary layout file: {e}")

        # Cycle through and purge any cached video downloads automatically to save hard drive space
        print("\nCleaning up local storage download cache files...")
        for source in VIDEO_SOURCES:
            if "filename_cache" in source and os.path.exists(source["filename_cache"]):
                try:
                    os.remove(source["filename_cache"])
                except Exception as e:
                    pass
                
        print(f"\n✅ Success! Open your folder to find your finished deadline video: {output_filename}")
    else:
        print("\nProcess failed: No clips were successfully compiled.")

if __name__ == "__main__":
    main()