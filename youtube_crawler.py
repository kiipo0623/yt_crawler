import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import json

# setting
DATA_SIZE_FOR_EACH = 20
CREATOR_FILE_NAME = "./youtuber/youtubers_pet.json"
RESULT_FILE_NAME = "data/youtube_pet_data.csv"

# 검색할 유튜브 채널명 리스트
channel_names = []
with open(CREATOR_FILE_NAME, "r", encoding="utf-8") as f:
    channel_names = json.load(f)

# 크롬 드라이버 설정
options = Options()
# options.add_argument("--headless")  # 브라우저 안 띄움
options.add_argument("--disable-gpu")
driver = webdriver.Chrome(options=options)
driver.maximize_window()

results = []

def collect_videos_sorted_by(sort_keyword):
    video_info = []

    # 정렬 버튼 누르기
    sort_buttons = driver.find_elements(By.XPATH, '//*[@id="chip-shape-container"]/chip-shape/button/div')
    for btn in sort_buttons:
        text = btn.text.strip()
        if sort_keyword in text:
            btn.click()
            print(f"✅ '{sort_keyword}' 정렬 버튼 클릭")
            time.sleep(2)
            break

    # 영상 목록 수집
    video_elements = driver.find_elements(By.XPATH, '//a[@id="video-title-link"]')[:DATA_SIZE_FOR_EACH]
    for element in video_elements:
        href = element.get_attribute("href")
        title = element.get_attribute("title")
        if href:
            video_info.append((href, title))

    return video_info


for channel in channel_names:
    try:
        # 1. 유튜브 검색
        driver.get(f"https://www.youtube.com/results?search_query={channel}")
        time.sleep(2)

        # 2. 첫 번째 채널 클릭 (없으면 건너뜀)
        try:
            first_channel = driver.find_element(By.XPATH, '//a[@href and @aria-label and contains(@href, "/@")]')
            first_channel.click()
            time.sleep(2)
        except:
            print(f"[SKIP] {channel} 채널을 찾을 수 없음")
            continue

        # 3. 동영상 탭으로 이동
        try:
            video_tab = driver.find_element(By.XPATH, '//*[@id="tabsContent"]/yt-tab-group-shape/div[1]/yt-tab-shape[2]/div[1]')
            video_tab.click()
            time.sleep(2)

        except:
            print(f"[SKIP] {channel} 동영상 탭 없음")
            continue

        # 4. 인기순 정렬
        latest_videos = collect_videos_sorted_by("최신")
        popular_videos = collect_videos_sorted_by("인기")
        video_data = latest_videos + popular_videos 

        for video_url, video_title in video_data:
            # 동영상 접속
            driver.get(video_url)
            time.sleep(2)

            # 페이지 소스 가져오기
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')

            # category 찾기
            if '"category":"' in html:
                start = html.find('"category":"') + len('"category":"')
                end = html.find('"', start)
                category = html[start:end].replace('\\u0026', ',')
            else:
                category = ""

            # keywords 찾기
            meta_tag = soup.find("meta", {"name": "keywords"})
            keywords = meta_tag["content"] if meta_tag else ""

            # 채널명 수집
            channel_title = driver.find_element(By.XPATH, '//ytd-channel-name//yt-formatted-string').text

            results.append({
                "channel_name": channel_title,
                "video_title": video_title,
                "category": category,
                "keywords": keywords
            })

            print(f"channel_name: {channel}")
            print(f"category: {category}")

    except Exception as e:
        print(f"[ERROR] {channel} 처리 중 오류 발생: {e}")
        continue

# 크롬 종료
driver.quit()

# CSV로 저장
df = pd.DataFrame(results)
df.to_csv(RESULT_FILE_NAME, index=False, encoding="utf-8-sig", quoting=csv.QUOTE_NONNUMERIC)
print(f"✅ 완료! {RESULT_FILE_NAME} 파일 생성됨.")

