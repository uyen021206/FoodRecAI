from selenium import webdriver
import json

driver = webdriver.Chrome()
driver.get("https://www.foody.vn")

print("🔵 Đăng nhập bằng Facebook trong cửa sổ Chrome hiện ra nhé!")
input("✅ Sau khi đăng nhập Foody xong, nhấn ENTER tại đây để lấy cookies Foody...")

# Lấy cookies của Foody (domain foody.vn)
cookies = driver.get_cookies()
driver.quit()

# Lưu cookies ra file
with open("foody_cookies.json", "w", encoding="utf-8") as f:
    json.dump(cookies, f, indent=2, ensure_ascii=False)

print("🔥 Cookies Foody (đã login qua Facebook) đã được lưu!")
