from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import time

def crawl_stock_data(stock_code):
    # Khởi tạo trình duyệt Selenium với context manager
    with webdriver.Chrome() as driver:
        url = f"https://timkiem.vnexpress.net/?q={stock_code}"
        driver.get(url)
        data = []

        while True:
            try:
                # Đợi cho phần tử chứa kết quả tìm kiếm xuất hiện trên trang
                WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "result_search")))
            except:
                break  # Nếu không tìm thấy phần tử, thoát khỏi vòng lặp

            soup = BeautifulSoup(driver.page_source, "html.parser")
            news_container = soup.find("div", {"id": "result_search"})

            news_articles = news_container.find_all("article")

            for article in news_articles:
                img = article.find("img")
                img_url = None
                if img and "data-srcset" in img.attrs:
                    img_url = img["data-srcset"].split(",")[-1].split()[0]

                timestamp_str = article.get("data-publishtime")
                if timestamp_str:
                    timestamp = datetime.datetime.fromtimestamp(int(timestamp_str)).strftime("%Y-%m-%d")
                else:
                    timestamp = None
                    continue

                first_paragraph = article.find("h3", {"class": "title-news"}).find_next_sibling("p").text.strip()

                title = article.find("h3", {"class": "title-news"}).text.strip()
                article_link = article.find("a", href=True)["href"]

                data.append({
                    'Thời gian đăng bài': timestamp,
                    'Link bài viết': article_link,
                    'Tiêu đề bài viết': title,
                    'First paragraph': first_paragraph
                })

            try:
                # Tìm nút next-page
                next_page_button = driver.find_element(By.CSS_SELECTOR, '.button-page .next-page')
                # Sử dụng JavaScript để nhấp vào nút next-page
                driver.execute_script("arguments[0].click();", next_page_button)
            except:
                break


            time.sleep(5)

    df = pd.DataFrame(data)
    df.to_excel(f'Data_{stock_code}.xlsx')
    driver.quit()

# Example usage:
stock_code = input("Nhập từ khóa tìm kiếm: ")
crawl_stock_data(stock_code)



