

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from bs4 import BeautifulSoup
import time
import pandas as pd
import random
import os
import pickle
import fake_useragent
ua = fake_useragent.UserAgent()


# -----------------------------
# CONFIG
START_URL = "https://www.idealista.it/agenzie-immobiliari-affitto/#municipality-search"
BASE_URL = 'https://www.idealista.it'
# USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115 Safari/537.36"
USER_AGENT = ua.random
PROXY = "http://user:pass@proxy_ip:proxy_port"  

# -----------------------------
def launch_browser():
    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument(f"user-agent={USER_AGENT}")
    # options.add_argument(f"--proxy-server={PROXY}") 

    driver = uc.Chrome(options=options)
    wait = WebDriverWait(driver, 20)

    # Anti-detection JavaScript injection
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.execute_script("window.navigator.chrome = { runtime: {} }")
    driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['it-IT', 'it']})")
    driver.execute_script("Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] })")

    return driver, wait

# -----------------------------
def simulate_scroll(driver):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.3);")
    time.sleep(random.uniform(1, 3))
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.7);")
    time.sleep(random.uniform(1, 3))
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.9);")

# -----------------------------
def human_like_mouse_move(driver, element):
    actions = ActionChains(driver)
    location = element.location_once_scrolled_into_view
    size = element.size
    target_x = location['x'] + size['width'] // 2
    target_y = location['y'] + size['height'] // 2
    current_x = random.randint(0, 100)
    current_y = random.randint(0, 100)
    steps = random.randint(15, 30)
    for i in range(steps):
        move_x = int(current_x + (target_x - current_x) * (i + 1) / steps + random.uniform(-2, 2))
        move_y = int(current_y + (target_y - current_y) * (i + 1) / steps + random.uniform(-2, 2))
        actions.move_by_offset(move_x, move_y).perform()
        time.sleep(random.uniform(0.01, 0.05))
        actions.reset_actions()
    actions.move_to_element(element).perform()

# -----------------------------
# Main Script

driver, wait = launch_browser()
driver.get(START_URL)
simulate_scroll(driver)

cookies_path = "./idealista_scraper/cookies.pkl"
os.makedirs("./idealista_scraper", exist_ok=True)

if os.path.exists(cookies_path):
    with open(cookies_path, "rb") as f:
        cookies = pickle.load(f)
        for cookie in cookies:
            driver.add_cookie(cookie)
    driver.refresh()
    time.sleep(10)
else:
    print("\n🧩 Please solve the CAPTCHA manually in the browser.")
    input("Press ENTER after solving CAPTCHA...")
    with open(cookies_path, "wb") as f:
        pickle.dump(driver.get_cookies(), f)

soup = BeautifulSoup(driver.page_source, 'lxml')
print(f"\n🔍 Found {len(soup.find_all('ul', class_='locations-list__links'))} location blocks")


csv_path = "./idealista_scraper/idealista_agencies.xlsx"
if os.path.exists(csv_path):
    existing_df = pd.read_excel(csv_path, engine="openpyxl")
    data_rows = existing_df.to_dict(orient='records')
    print(f"📄 Loaded {len(data_rows)} previously saved rows.")
else:
    data_rows = []

csv1_path = "./idealista_scraper/missed_idealista_agencies.csv"
if os.path.exists(csv1_path):
    existing_df = pd.read_csv(csv1_path)
    missed_data = existing_df.to_dict(orient='records')
    print(f"📄 Loaded {len(missed_data)} previously saved rows.")
else:
    missed_data = []


visited_file = "./idealista_scraper/visited_agencies.txt"
visited_urls = set()
if os.path.exists(visited_file):
    with open(visited_file, "r") as f:
        visited_urls = set(line.strip() for line in f)

visited_region = "./idealista_scraper/visited_regions.txt"
visited_name = set()
if os.path.exists(visited_region):
    with open(visited_region, "r") as f:
        visited_name = set(line.strip() for line in f)

for ul in soup.find_all('ul', class_='locations-list__links'):
    region_title = ul.find(class_='region-title').text.strip() if ul.find(class_='region-title') else "Unknown Region"
    for li in ul.find_all('li'):
        a_tag = li.find('a')
        if not a_tag:
            continue

        sub_url = BASE_URL + a_tag.get('href')
        sub_region = a_tag.text.strip()
        print(f"\n🌍 Visiting subregion: {sub_region}")
        if sub_region in visited_name:
            print(f"🔗 Already visited: {sub_region}")
            continue

        driver.get(sub_url)
        simulate_scroll(driver)
        time.sleep(2)

        agency_links = []
        while True:
            try:
                wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'zone-experts-agency-card')))
                cards = driver.find_elements(By.CLASS_NAME, 'zone-experts-agency-card')
                for card in cards:
                    agency_url = card.get_attribute('data-microsite-url')
                    if agency_url:
                        print(f"🔗 Found agency URL: {agency_url}")
                        agency_links.append(agency_url)
                next_button = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, 'icon-arrow-right-after'))
                )
                simulate_scroll(driver)
                next_button.click()
                time.sleep(random.uniform(1, 3))
            except:
                break

        for agency_url in agency_links:
            if agency_url in visited_urls:
                continue
            try:
                driver.get(agency_url + 'affitto-case/con-affitto-lungo-termine/')
                simulate_scroll(driver)
                try:
                    agency_name = driver.find_element(By.ID, "commercial-name").text.strip()
                except:
                    agency_name = "N/A"
                try:
                    online_office_title = driver.find_element(By.CLASS_NAME, 'online-office-title').text.strip()
                    office_title_split = online_office_title.replace(agency_name, '')
                    listing_count = ''.join(x for x in office_title_split if x.isdigit())
                except:
                    listing_count = "0"
                try:
                    if int(listing_count) > 0:
                        phone_btn = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.CLASS_NAME, "see-phones-btn"))
                        )
                        human_like_mouse_move(driver, phone_btn)
                        phone_btn.click()
                        agency_number = wait.until(
                            EC.presence_of_element_located((By.CLASS_NAME, '_mobilePhone'))
                        ).text.strip()
                    else:
                        agency_number = ''
                except:
                    agency_number = "N/A"
                try:
                    agency_description = driver.find_element(By.CLASS_NAME, 'office-description').text.strip()
                except:
                    agency_description = "N/A"

                if int(listing_count) > 0:
                    data_rows.append({
                        "Regione": region_title,
                        "provincia": sub_region,
                        "nome": agency_name,
                        "link agenzia": agency_url + 'affitto-case/con-affitto-lungo-termine/',
                        "Annunci a lungo termine in affitto": listing_count,
                        "Numeri di telefono": agency_number,
                        "Descrizione": agency_description,
                    })

                    with open(visited_file, "a") as f:
                        f.write(agency_url + "\n")

                    df = pd.DataFrame(data_rows)
                    df.to_excel(csv_path, index=False)
                    df.to_csv("./idealista_scraper/idealista_agencies.csv", index=False)
                    print(f"\n📁 Data saved for {agency_name}\nLenght:{agency_links.index(agency_url)}/{len(agency_links)}")
                else:
                    with open(visited_file, "a") as f:
                        f.write(agency_url + "\n")
                    print(f'\n📁 No Option\nLenght:{agency_links.index(agency_url)}/{len(agency_links)}')
                    time.sleep(random.uniform(1, 3))

            except Exception as e:
                print("❌ Error while processing agency:", e)

        with open(visited_region, "a") as f:
            f.write(sub_region + "\n")

# Done
driver.quit()
