from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import time


def crawl_stock_data(stock_code):
    # Khởi tạo trình duyệt Selenium với context manager
    with webdriver.Chrome() as driver:
        url = f"https://thoibaonganhang.vn/search_enginer.html?BRSR=1&p=tim-kiem&q={stock_code}"
        driver.get(url)
        data = []
        crawled_links = set()  # Danh sách để lưu trữ các liên kết đã thu thập
        while True:
            try:
                WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "article")))
            except:
                break

            soup = BeautifulSoup(driver.page_source, "html.parser")
            news_container = soup.find_all("div", class_="article")

            for article in news_container:
                img = article.find("img")
                img_url = None
                img_timestamp = None

                if img and "src" in img.attrs:
                    img_url = img["src"]
                    img_timestamp = img_url.split("rt=")[1][:8] if "?rt=" in img_url else None

                timestamp = datetime.datetime.strptime(img_timestamp, "%Y%m%d").strftime(
                    "%Y-%m-%d") if img_timestamp else None

                title = article.find("h3", class_="article-title").text.strip()
                article_link = 'https://thoibaonganhang.vn/'+ article.find("a", href=True)["href"]

                article_desc = article.find("div", class_="article-desc")
                first_paragraph = article_desc.text.strip() if article_desc else None

                # Kiểm tra xem liên kết đã được thu thập trước đó chưa
                if article_link not in crawled_links:
                    data.append({
                        'Thời gian đăng bài': timestamp,
                        'Link bài viết': article_link,
                        'Tiêu đề bài viết': title,
                        'First paragraph': first_paragraph,
                        'Ảnh bài viết': img_url
                    })
                    crawled_links.add(article_link)  # Thêm liên kết vào danh sách đã thu thập

            try:
                next_page_button = driver.find_element(By.XPATH,
                                                       "//div[@class='btn-viewmore']/a[contains(text(),'Trang tiếp')]")
                next_page_button.click()
                time.sleep(5)
            except:
                break


    df = pd.DataFrame(data)
    df.to_excel(f'Data_{stock_code}.xlsx')

# Example usage:
stock_code = input("Nhập từ khóa tìm kiếm: ")
crawl_stock_data(stock_code)
