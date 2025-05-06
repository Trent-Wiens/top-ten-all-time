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
        raise Exception("Album page not found.")

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
        "safe_name": f"{artist}_{album}".replace(" ", "_")
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
        "-t", "10",  # 10 second static video
        "-pix_fmt", "yuv420p",
        "-vf", "scale=1280:720",
        output_path
    ]
    subprocess.run(ffmpeg_command, check=True)
    os.remove(image_path)

if __name__ == "__main__":
    album = input("Enter album name: ").strip()
    artist = input("Enter artist name: ").strip()

    try:
        result = search_apple_music_album(album, artist)
        os.makedirs("mp4s", exist_ok=True)
        output_path = f"mp4s/{result['safe_name']}.mp4"

        if result["m3u8_url"]:
            print(f"Found ambient video: {result['m3u8_url']}")
            download_with_vlc(result["m3u8_url"], output_path)
        elif result["album_art_url"]:
            print("No video found. Falling back to album art...")
            print(f"Using image: {result['album_art_url']}")
            create_static_video_from_image(result["album_art_url"], output_path)
        else:
            raise Exception("No ambient video or album art found.")

        print(f"Saved to {output_path}")

    except Exception as e:
        print("Error:", e)