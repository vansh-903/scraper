import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import csv

def create_driver():
    options = Options()
    options.add_argument("--disable-gpu")  # Disable GPU acceleration
    options.add_argument("--headless")  # Run without opening browser
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-software-rasterizer")
    return webdriver.Chrome(options=options)

def scrape_social_media(url):
    driver = create_driver()
    driver.get(url)
    time.sleep(5)
    
    if "instagram.com" in url:
        return scrape_instagram(driver, url)
    elif "youtube.com" in url:
        return scrape_youtube_video(url)
    elif "tiktok.com" in url:
        return scrape_tiktok(driver, url)
    elif "facebook.com" in url:
        return scrape_facebook(driver, url)
    else:
        return {"Error": "Unsupported URL"}

def scrape_instagram(driver, url):
    if "/p/" in url:
        commenters = driver.find_elements(By.CSS_SELECTOR, "._a9zj")
        data = [comment.text for comment in commenters]
    else:
        followers_element = driver.find_element(By.XPATH, "//a[contains(@href, 'followers')]/span")
        following_element = driver.find_element(By.XPATH, "//a[contains(@href, 'following')]/span")
        bio_element = driver.find_element(By.CSS_SELECTOR, "div._aa_c")
        data = {
            "Followers": followers_element.text,
            "Following": following_element.text,
            "Bio": bio_element.text
        }
    driver.quit()
    return data

def scrape_youtube_video(url):
    video_id = url.split("v=")[-1].split("&")[0]
    api_key = "AIzaSyA4zi6NECEsF2kEhsVxHYTwI"
    api_url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics&id={video_id}&key={api_key}"
    response = requests.get(api_url).json()
    
    if "items" in response:
        data = response['items'][0]
        return {
            "Video Title": data['snippet']['title'],
            "Views": data['statistics']['viewCount'],
            "Likes": data['statistics'].get('likeCount', 'N/A'),
            "Comments": data['statistics'].get('commentCount', 'N/A')
        }
    return {"Error": response.get('error', {}).get('message', 'Invalid Video ID or API Key')}

def scrape_tiktok(driver, url):
    if "/video/" in url:
        likers = driver.find_elements(By.CSS_SELECTOR, "strong[data-e2e='like-count']")
        data = [liker.text for liker in likers]
    else:
        followers_element = driver.find_element(By.CSS_SELECTOR, "strong[data-e2e='followers-count']")
        following_element = driver.find_element(By.CSS_SELECTOR, "strong[data-e2e='following-count']")
        data = {
            "Followers": followers_element.text,
            "Following": following_element.text
        }
    driver.quit()
    return data

def scrape_facebook(driver, url):
    if "/posts/" in url:
        comments = driver.find_elements(By.CSS_SELECTOR, "div[data-testid='UFI2Comment/body']")
        data = [comment.text for comment in comments]
    else:
        likes_element = driver.find_element(By.CSS_SELECTOR, "div[data-testid='page_insights']")
        data = {"Likes": likes_element.text}
    driver.quit()
    return data

def save_to_csv(data, filename):
    keys = data[0].keys() if isinstance(data, list) else data.keys()
    with open(filename, 'w', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows([data] if isinstance(data, dict) else data)

if __name__ == "__main__":
    url = input("Enter social media URL: ")
    scraped_data = scrape_social_media(url)
    print("Scraped Data:", scraped_data)
    save_to_csv(scraped_data, "social_media_data.csv")
