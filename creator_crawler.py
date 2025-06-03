from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import json
import time

options = Options()
# options.add_argument("--headless")
driver = webdriver.Chrome(options=options)
driver.get("https://youtube-rank.com/board/bbs/board.php?bo_table=youtube&sca=게임")

time.sleep(2)  # 로딩 대기

# ✅ 스크롤을 강제로 한 번 내림 → 전체 row 렌더링 유도
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
time.sleep(2)

# ✅ tr 행 수집
rows = driver.find_elements(By.XPATH, '//*[@id="list-skin"]/form/table/tbody/tr')

youtuber_names = []

for row in rows:
    try:
        name_tag = row.find_element(By.XPATH, './td[3]/h1/a')
        name = name_tag.text.strip()
        if name:
            youtuber_names.append(name)
    except:
        continue

print(f"총 수집된 유튜버 수: {len(youtuber_names)}")

# 최대 20개까지만 저장
youtuber_names = youtuber_names[:50]

with open("youtubers_gaming.json", "w", encoding="utf-8") as f:
    json.dump(youtuber_names, f, ensure_ascii=False, indent=2)

print("✅ 유튜버 수집 완료!")
driver.quit()
