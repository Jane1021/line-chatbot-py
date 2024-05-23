import argparse
import json
import time
import logging
import traceback
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from youtube_transcript_api import YouTubeTranscriptApi
import os

# 初始化日誌記錄器
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    # 將頻道名稱硬編碼為 "維思維WeisWay"
    channel_name = "維思維WeisWay"

    # 初始化網頁驅動程式
    driver = webdriver.Chrome()

    # 打開 "WeisWay" 頻道的影片列表頁面
    url = "https://www.youtube.com/@WeisWay/videos"
    driver.get(url)

    # 捲動頁面以加載所有影片
    ht = driver.execute_script("return document.documentElement.scrollHeight;")
    while True:
        prev_ht = driver.execute_script("return document.documentElement.scrollHeight;")
        driver.execute_script(
            "window.scrollTo(0, document.documentElement.scrollHeight);"
        )
        time.sleep(2)
        ht = driver.execute_script("return document.documentElement.scrollHeight;")
        if prev_ht == ht:
            break

    # 儲存影片資訊的列表
    videos = []
    try:
        for e in WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div#details"))
        ):
            # 取得影片標題和 URL
            title = e.find_element(By.CSS_SELECTOR, "a#video-title-link").get_attribute(
                "title"
            )
            vurl = e.find_element(By.CSS_SELECTOR, "a#video-title-link").get_attribute(
                "href"
            )

            # 將影片資訊加入列表
            videos.append(
                {
                    "video_url": vurl,
                    "title": title,
                }
            )
    except Exception as e:
        logger.error(f"An error occurred while scraping videos: {e}")
        logger.error(traceback.format_exc())

    logger.info(f"# videos from TheFreezia: {len(videos)}")

    # 儲存影片字幕
    for video_i in videos:
        video_id = video_i["video_url"].split("=")[-1]
        video_i["video_id"] = video_id
        video_i["channel_name"] = channel_name
        logger.info(f"video id: {video_id}")

        entity_fname = f"{video_id}.json"

        # 檢查檔案是否存在
        file_path = os.path.join("C:\\Users\\User\\Desktop\\專題\\字幕", entity_fname)
        if Path(file_path).exists():
            logger.info(f"file exist: {file_path}")
            continue

        try:
            transcript_i = YouTubeTranscriptApi.get_transcript(
                video_id, languages=["zh-TW"]
            )
            video_i["transcript"] = transcript_i
        except Exception as e:
            logger.error(f"An error occurred while getting transcript for video {video_id}: {e}")
            logger.error(traceback.format_exc())
            video_i["transcript"] = []
        finally:
            # 將影片資訊以 JSON 格式輸出到指定路徑
            with open(file_path, "w") as f:
                json.dump(video_i, f)
            logger.info(f"JSON file saved: {file_path}")

if __name__ == "__main__":
    main()
