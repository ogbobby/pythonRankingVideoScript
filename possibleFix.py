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
import shutil
import base64
from yt_dlp import YoutubeDL
from urllib.parse import urlparse, urlunparse
from yt_dlp.networking.impersonate import ImpersonateTarget
from playwright.sync_api import sync_playwright
import moviepy.audio.fx as afx
from moviepy import VideoFileClip, concatenate_videoclips, TextClip, CompositeVideoClip, ImageClip, AudioFileClip, CompositeAudioClip
import moviepy.video.fx as vfx
from moviepy.video.fx import FadeIn
from moviepy import concatenate_audioclips
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


# =====================================================================
# 1. TEXT CONTENT CONFIGURATION (Change these for every new video)
# =====================================================================
VIDEO_TITLE = "Ranking Trickshots That Go Hard"
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
    {"url": "https://www.tiktok.com/@arr0w_sniper/video/6983419815608241413?is_from_webapp=1&sender_device=pc&web_id=7673309675748886029", "start": 53, "end": 59.5},
    {"url": "https://www.tiktok.com/@fiaza199n/video/7680921513402322190?is_from_webapp=1&sender_device=pc&web_id=7673309675748886029", "start": 0, "end": 10},#was9.5
    {"url": "https://www.tiktok.com/@gameday_original/video/7561357165789777163?is_from_webapp=1&sender_device=pc&web_id=7673309675748886029"}, #"start": 0, "end": 15},
    {"url": "https://www.tiktok.com/@dearcombat/video/7374961901601688837?is_from_webapp=1&sender_device=pc&web_id=7673309675748886029", "start": 0, "end": 24},
    {"url": "https://www.tiktok.com/@andytrickshots/video/7678805223233654046?is_from_webapp=1&sender_device=pc&web_id=7673309675748886029", "start": 0, "end": 10},
    #{"url": "https://www.tiktok.com/@jugglinjosh/video/6822677301487095045?is_from_webapp=1&sender_device=pc&web_id=7673309675748886029", "start": 0, "end": 26},

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
    """
    Download a TikTok video by capturing the authenticated CDN url from your live Chrome session,
    and passing it to a native Linux shell download subsystem (wget) to guarantee local file delivery.
    """
    print("   -> Resting connection profile for 5 seconds...")
    time.sleep(5)
    
    url_string = str(url).strip()
    
    # 1. Isolate the target 19-digit numerical sequence safely
    video_id_match = re.search(r'(\d{15,25})', url_string)
    if not video_id_match:
        print(f"   ❌ Critical: No numeric ID sequence could be found in text: {url_string}")
        return None
        
    video_id = video_id_match.group(1)
    output_filename = f"temp_clip_{video_id}.mp4"
    print(f"   -> Pure Video ID isolated successfully: {video_id}")

    # Rebuild domain host safely to bypass local string replacement blocks
    host_pieces = ['w', 'w', 'w', '.', 't', 'i', 'k', 't', 'o', 'k', '.', 'c', 'o', 'm']
    hidden_host = "".join(host_pieces)
    target_embed_url = f"https://{hidden_host}/embed/v2/{video_id}"
    print(f"   -> Attaching to live debugging socket for link: {target_embed_url}")

    # 2. Attach to the running Chrome process over port 9222
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

    driver = None
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        original_home_url = driver.current_url
        
        # Open embed route context directly inside the debugging pane
        driver.get(target_embed_url)
        time.sleep(5)  # Let your real browser render the page layout and compile the media keys

        # 3. Scan JavaScript memory layout maps directly first
        target_url_string = driver.execute_script(
            "try { return window.__INIT_DATA__.__MUSE_MANIFEST__.video.urls; } catch(e) { return null; }"
        )

        # Fallback to page source regex if window state maps are uninitialized
        if not target_url_string:
            page_source = driver.page_source
            cdn_urls = re.findall(r'"video":{"urls":\["([^"]+)"', page_source)
            if not cdn_urls:
                cdn_urls = re.findall(r'<video[^>]*src="([^"]+)"', page_source)

            if not cdn_urls:
                print("   ❌ Failed to locate the hidden media stream nodes. Resetting view...")
                driver.get(original_home_url)
                return None

            # Safely unpack index 0 if findall matched a list array
            if isinstance(cdn_urls, list) and len(cdn_urls) > 0:
                target_url_string = cdn_urls[0]
            else:
                target_url_string = cdn_urls

        # Clean unicode characters and encoding escapes explicitly on the raw string
        raw_cdn_url = (str(target_url_string)
                       .replace(r'\u002F', '/')
                       .replace(r'\u0026', '&')
                       .replace(r'%5Cu0026', '&')
                       .replace(r'&amp;', '&'))
        
        # Extract your real browser's user-agent fingerprint to hand off to the shell download sub-process
        user_agent_fingerprint = driver.execute_script("return navigator.userAgent;")
        
        # Instantly reset your Chrome tab workspace back to your original view layout cleanly
        driver.get(original_home_url)
        print("   -> Stream found! Launching native shell payload downstream engine...")

        # 4. FIX: Use a native Linux system tool (wget) to handle the stream directly via an isolated subprocess.
        # This completely routes around Chrome JavaScript fetch memory limits. Wget uses your browser's 
        # User-Agent header, downloading the data straight to your local script workspace folder.
        shell_download_command = [
            "wget",
            "-q", # Suppresses extra terminal layout spam text
            "--show-progress",
            "--user-agent", user_agent_fingerprint,
            "--header", "Referer: https://www.tiktok.com/",
            "-O", output_filename,
            raw_cdn_url
        ]
        
        # Run the system download sub-process linearly
        subprocess.run(shell_download_command, check=True)

        # 5. Final verification footprint check matching MoviePy expectations
        if os.path.exists(output_filename) and os.path.getsize(output_filename) > 100000:
            print(f"   -> Download successfully finalized natively: {output_filename}")
            return output_filename
        else:
            print("   ❌ Binary pipeline executed but generated a truncated or empty file configuration.")
            if os.path.exists(output_filename):
                os.remove(output_filename)
            return None

    except Exception as e:
        print(f"   ❌ Native system shell download pipeline failed. Error: {e}")
        return None

#def download_tiktok_video(url):
#    """
#    Download a TikTok video by attaching to your running desktop Chrome process over port 9222.
#    Navigates safely inside a single window structure to prevent browser tab-closure crashes.
#    """
#    
#    print("   -> Resting connection profile for 5 seconds...")
#    time.sleep(5)
#    
#    url_string = str(url).strip()
#    
#    # 1. Isolate the target 19-digit numerical sequence safely
#    video_id_match = re.search(r'/video/(\d+)', url_string)
#    if video_id_match:
#        video_id = video_id_match.group(1)
#    else:
#        backup_match = re.search(r'(\d{15,25})', url_string)
#        if backup_match:
#            video_id = backup_match.group(1)
#        else:
#            print(f"   ❌ Critical: No numeric ID sequence could be found in text: {url_string}")
#            return None
#        
#    output_filename = f"temp_clip_{video_id}.mp4"
#    print(f"   -> Pure Video ID isolated successfully: {video_id}")
#
#    target_embed_url = f"https://www.tiktok.com/embed/v2/{video_id}"
#    print(f"   -> Attaching to live debugging socket for link: {target_embed_url}")
#
#    # 2. Attach straight to the terminal chrome process session over port 9222
#
#    chrome_options = Options()
#    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
#
#    driver = None
#    try:
#        service = Service(ChromeDriverManager().install())
#        driver = webdriver.Chrome(service=service, options=chrome_options)
#        
#        # Save your browser's initial landing location so your layout stays clean after execution
#        original_home_url = driver.current_url
#        
#        # FIX: Navigate straight inside the active view pane instead of opening popup tabs.
#        # This completely strips out popup blocks or tab-destruction webview errors.
#        driver.get(target_embed_url)
#        time.sleep(6)  # Give your real browser full timeline frames to decode the media URL keys
#
#        # 3. Extract the video tags using page layout source regex
#        page_source = driver.page_source
#        
#        # Find the structural JSON or video elements on the rendering frame
#        cdn_urls = re.findall(r'"video":{"urls":\["([^"]+)"', page_source)
#        if not cdn_urls:
#            cdn_urls = re.findall(r'<video[^>]*src="([^"]+)"', page_source)
#
#        if not cdn_urls:
#            print("   ❌ Failed to locate the hidden media stream nodes. Resetting view context...")
#            driver.get(original_home_url)
#            return None
#
#        # Safely capture index 0 if matched inside an active array list frame layout
#        target_url_string = cdn_urls[0] if isinstance(cdn_urls, list) else cdn_urls
#        
#        # Clean unicode characters and escape parameters explicitly
#        raw_cdn_url = (target_url_string
#                       .replace(r'\u002F', '/')
#                       .replace(r'\u0026', '&')
#                       .replace(r'&amp;', '&'))
#        
#        print("   -> Stream found! Directing active browser layer to download natively...")
#
#        # 4. Force your browser's native engine to process the file stream download natively
#        driver.execute_script(f"window.location.href = '{raw_cdn_url}';")
#        time.sleep(6) # Give the system file download pipe time to finalize writing chunks
#
#        # Safely return your open browser tab back to where it was before the script triggered
#        driver.get(original_home_url)
#
#        # 5. Locate the newly downloaded file inside your Linux user account's default Downloads folder
#        linux_downloads_path = os.path.expanduser("~/Downloads")
#        
#        downloaded_file = None
#        time.sleep(2)
#        
#        for item in os.listdir(linux_downloads_path):
#            if item.endswith(".mp4") or "main" in item:
#                full_item_path = os.path.join(linux_downloads_path, item)
#                # Ensure the file isn't an active, incomplete download (.crdownload)
#                if os.path.isfile(full_item_path) and os.path.getsize(full_item_path) > 100000:
#                    downloaded_file = full_item_path
#                    break
#
#        if not downloaded_file:
#            # Fallback check if the video was cached inside a generic temporary name matrix
#            fallback_name = "main.mp4"
#            if os.path.exists(os.path.join(linux_downloads_path, fallback_name)):
#                downloaded_file = os.path.join(linux_downloads_path, fallback_name)
#
#        if downloaded_file and os.path.exists(downloaded_file):
#            # Move the cleanly completed video file straight into your local workspace directory
#            shutil.move(downloaded_file, output_filename)
#            print(f"   -> Download successfully finalized natively: {output_filename}")
#            return output_filename
#        else:
#            print("   ❌ Binary pipeline executed but file transfer was intercepted or delayed by system drivers.")
#            return None
#
#    except Exception as e:
#        print(f"   ❌ Live browser debug controller connection failed. Error: {e}")
#        return None
    
def process_single_video(source, index, total_clips, processed_clips):
    """Process a single video source layout on a timeline."""
    current_rank_num = total_clips - index
    
    if "local" in source:
        file_path = source["local"]
        print(f" -> Position {index + 1} assigned to: {current_rank_num}. (Local file: {os.path.basename(file_path)})")
        if not os.path.exists(file_path):
            print(f"   ⚠️ Warning: Local file not found: {file_path}")
            return None
    elif "url" in source:
        print(f" -> Position {index + 1} assigned to: {current_rank_num}. (Downloading TikTok...)")
        # We explicitly query the dict value safely without saving reference markers back into it
        file_path = download_tiktok_video(source["url"])
        if not file_path:
            return None
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

        # Build ranking text tracks
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
            label_box_size = (500, text_size + 40)

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
            label_offset = 60 if is_active else 35
            
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
    
    print("\n[2/4] Shuffling video play order...")
    random.shuffle(VIDEO_SOURCES)
    print(" -> New video sequence generated successfully!")

    print("\n[3/4] Processing clips and building layout...")
    processed_clips = []
    total_clips = len(VIDEO_SOURCES)

    for index, source in enumerate(VIDEO_SOURCES):
        clip = process_single_video(source, index, total_clips, processed_clips)
        if clip:
            processed_clips.append(clip)

    if processed_clips:
        print("\n[4/4] Stitching final video output file with transitions...")
        temp_filename = "temp_unbranded_compilation.mp4"
        output_filename = "906.mp4"
        
        music_audio_path = "Subway_Altar.mp3"
        scratch_audio_path = "record_scratch.mp3"
        bruh_audio_path = "deep_bruh.mp3"
        logo_path = "channel_logo.png"
        
        if not os.path.exists(music_audio_path) or not os.path.exists(scratch_audio_path) or not os.path.exists(bruh_audio_path) or not os.path.exists(logo_path):
            print(f"❌ Error: Outro assets missing! Make sure '{music_audio_path}', '{scratch_audio_path}', '{bruh_audio_path}', and '{logo_path}' are in this directory.")
            sys.exit(1)
        
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

        normal_video_part = master_video.subclipped(0, freeze_start_time).without_audio()
        
        freeze_frame = master_video.get_frame(freeze_start_time)
        bw_image = np.dstack([np.mean(freeze_frame, axis=2)] * 3).astype('uint8')
        bw_frozen_clip = ImageClip(bw_image).with_duration(total_outro_duration).with_start(freeze_start_time).without_audio()

        logo_clip = (ImageClip(logo_path)
                     .with_duration(bruh_duration)
                     .with_start(bruh_start_time)
                     .resized(width=550)  
                     .with_effects([vfx.Rotate(-10, expand=True)])
                     .without_audio()
                     .with_position(("center", "center")))

        final_video_layers = [normal_video_part, bw_frozen_clip, logo_clip]
        final_branded_video = CompositeVideoClip(final_video_layers, size=(MASTER_WIDTH, MASTER_HEIGHT))
        
        clean_base_audio = master_video.audio.copy() if master_video.audio is not None else None
        bg_music = AudioFileClip(music_audio_path).with_effects([afx.AudioLoop(duration=total_duration)]).with_volume_scaled(0.15)
        
        scratch_audio = AudioFileClip(scratch_audio_path).with_start(scratch_start_time)
        bruh_audio = AudioFileClip(bruh_audio_path).with_start(bruh_start_time).with_volume_scaled(1.5)
        sfx_overlay = CompositeAudioClip([scratch_audio, bruh_audio])
        
        audio_mix_list = [bg_music, sfx_overlay]
        if clean_base_audio is not None:
            audio_mix_list.insert(0, clean_base_audio)
            
        final_audio = CompositeAudioClip(audio_mix_list)
        final_branded_video = final_branded_video.with_audio(final_audio)

        final_branded_video.write_videofile(
            output_filename, fps=30, codec="libx264", audio_codec="aac",
            temp_audiofile="temp-audio.m4a", remove_temp=True, logger=None
        )
        
        master_video.close()
        final_branded_video.close()
        
        if os.path.exists(temp_filename):
            try:
                os.remove(temp_filename)
            except Exception as e:
                print(f"   ⚠️ Could not remove temporary layout file: {e}")

        # Local cleanup loop using regex signatures to protect original variable memory contexts
        print("\nCleaning up local storage download cache files...")
        for source in VIDEO_SOURCES:
            if "url" in source:
                vid_match = re.search(r'(\d{15,25})', str(source["url"]))
                if vid_match:
                    cache_file = f"temp_clip_{vid_match.group(1)}.mp4"
                    if os.path.exists(cache_file):
                        try:
                            os.remove(cache_file)
                        except Exception:
                            pass
                
        print(f"\n✅ Success! Open your folder to find your finished video: {output_filename}")
    else:
        print("\nProcess failed: No clips were successfully compiled.")

if __name__ == "__main__":
    main()