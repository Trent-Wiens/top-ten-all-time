import os
import time
import subprocess
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

def search_apple_music_album(album, artist):
    query = quote_plus(f"{album} {artist}")
    search_url = f"https://music.apple.com/us/search?term={query}"

    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    driver.get(search_url)
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    # Find album link
    album_links = soup.find_all("a", href=True)
    album_url = None
    for link in album_links:
        href = link['href']
        if '/album/' in href:
            album_url = href if href.startswith("https") else f"https://music.apple.com{href}"
            break

    if not album_url:
        driver.quit()
        return None

    # Navigate to album page
    driver.get(album_url)
    time.sleep(3)
    page_soup = BeautifulSoup(driver.page_source, "html.parser")

    # Get ambient video URL if available
    video_tag = page_soup.find("amp-ambient-video")
    m3u8_url = video_tag.get("src") if video_tag else None

    # Try getting album art image as fallback
    img_tag = page_soup.find("meta", {"property": "og:image"})
    album_art_url = img_tag["content"] if img_tag else None

    driver.quit()

    return {
        "m3u8_url": m3u8_url,
        "album_art_url": album_art_url,
        "safe_name": f"{artist}_{album}".replace(" ", "_").replace("/", "-")
    }

def download_with_vlc(m3u8_url, output_path):
    vlc_command = [
        "/Applications/VLC.app/Contents/MacOS/VLC",  # Full path on Mac
        m3u8_url,
        "--sout=#file{dst=" + output_path + "}",
        "--intf", "dummy", "--no-video-title-show",
        "--play-and-exit"
    ]
    subprocess.run(vlc_command, check=True)

def create_static_video_from_image(image_url, output_path):
    image_path = "temp.jpg"
    response = requests.get(image_url)
    with open(image_path, "wb") as f:
        f.write(response.content)

    ffmpeg_command = [
        "ffmpeg",
        "-loop", "1",
        "-i", image_path,
        "-c:v", "libx264",
        "-t", "10",  # 10 seconds
        "-pix_fmt", "yuv420p",
        "-vf", "scale=1280:720",
        output_path
    ]
    subprocess.run(ffmpeg_command, check=True)
    os.remove(image_path)

def process_album(album, artist):
    try:
        print(f"\nProcessing: {album} – {artist}")
        result = search_apple_music_album(album, artist)
        if not result:
            print("  ❌ Album page not found.")
            return

        output_path = f"mp4s/{result['safe_name']}.mp4"
        os.makedirs("mp4s", exist_ok=True)

        if result["m3u8_url"]:
            print("  ✅ Found ambient video.")
            download_with_vlc(result["m3u8_url"], output_path)
        elif result["album_art_url"]:
            print("  ⚠️ No video. Falling back to album art.")
            create_static_video_from_image(result["album_art_url"], output_path)
        else:
            print("  ❌ No video or image found.")
            return

        print(f"  🎵 Saved: {output_path}")

    except Exception as e:
        print(f"  💥 Error: {e}")

if __name__ == "__main__":
    # 👇 Add your albums here (album name, artist)
    albums_to_process = [
        ("CALL ME IF YOU GET LOST", "Tyler, The Creator"),
        ("LOUIE", "Kenny Beats"),
        ("The College Dropout", "Kanye West"),
        ("24K Magic", "Bruno Mars"),
    ]

    for album, artist in albums_to_process:
        process_album(album, artist)