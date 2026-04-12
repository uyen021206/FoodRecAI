import json
import time
import re
import requests
from bs4 import BeautifulSoup

# =========================
# CONFIG
# =========================
INPUT_FILE = "merge_result_demo.json"
OUTPUT_FILE = "foody_review_demo.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "vi-VN,vi;q=0.9",
    "Referer": "https://www.foody.vn/",
    "Origin": "https://www.foody.vn",
    "X-Requested-With": "XMLHttpRequest",
    "Connection": "keep-alive",
    "Cookie": "flg=vn; __ondemand_sessionid=a14o4gr35vj0lhnawlh12f25; floc=218; gcat=food; _ga=GA1.2.1159984972.1766564630; _gid=GA1.2.967712488.1766564630; fbm_395614663835338=base_domain=.foody.vn; _fbp=fb.1.1766564988830.810075820636650041; __utmc=257500956; ID_FOODY.AUTH=FCA3061086CE38BE923DD599DBC3211B5E4E4524C12A3341241A50AC9A04B8AEDA515A5749855F7E66902DCE0FD632388ED1832D61AFAF8B1319F8C730CF98C7D65BBB4A082CF275C108EBCC4BD62EFAA36147793EB5253343B11D20B3D2916C19CFEA7382AA7EEFD6F89CD626B8B221D5FC8BDD38ECB2E453C8A39C8687C2C165C1725DF237E248DC454C579E5494C0DFB160C76F5ABDDF4E37E9B853050D108B293974ACA69DB9FD986BB9C95FCEFE91B92813D4993B78BCF676941AEA0510745A0BB8FD656838B79A2D1096C153D63170431CC9B81F8753D4C9A0C1E99608B6A5201B7FC23C3B5EF92DF5F264976EE5E70574C6B5398A0D27801611477994; FOODY.AUTH.UDID=f04ab5a4-3a5d-4ede-8be4-b4f4228fbdbc; FOODY.AUTH=8AEBA71E4CD8DAA3DDA79DCD2D04E65CF6539A94AEDFDE996F59CB75CB8ECD2203A2DBF12106667384DB8DD9D4E9A927C64A4052F60FCDCBE116013E0225AC8ABD213FBFA62D8B1F2FA9355DF26CA2095E96FD7B66D29D1DC7F918E0F14CE97C306B2265F37D0F082DB37A860995F28C729AE042BCC1BD2B57BCF04C4321942B26FA07B7D0651875D3EDC155F11BC54DCF124B4C4AA68772091DCD113EDEA3435C9B51A4183E0D013D12C3672CDFA6ACFEEC49D812B7CFFC90E9A7903427CC563C9F4A8EEEB003EA6568915810CFF86DA153CA09A57005111516D4E7AA430674795C2CA83A3A26FD1CFD56BDAA1DF76E041A16260866CB36907F5BC6C8165F6D; fd.verify.password.24690847=24/12/2025; _fbc=fb.1.1766567002765.IwY2xjawO4i6hleHRuA2FlbQIxMABicmlkETFmd1hkVTlScGhTMGZnbWtrc3J0YwZhcHBfaWQQMjIyMDM5MTc4ODIwMDg5MgABHk-T0CDJfCN6h6RD9PC7KzoQjsHOlw9YnWZ2tlhdJje0KvFKCiffVIEj1Fu6_aem_sSTRKnxtY-KHkhMq6Fr-5w; _gcl_au=1.1.1557224540.1766567615; __utmz=257500956.1766715944.5.4.utmcsr=l.facebook.com|utmccn=(referral)|utmcmd=referral|utmcct=/; fd.keys=; __utma=257500956.1159984972.1766564630.1766763699.1766826083.8; __utmt_UA-33292184-1=1; fd.res.view.218=70304,638078,67559,7975,223850,1000027698,1092352,1243056,1000027544,223001,1024448,694536,164027,1085866,6734,8855,496,854376,19146,28877; fbsr_395614663835338=aoC_bgRgk3JGRwfnHk_iloQZiyjHEt5iVHya2KpYoDs.eyJ1c2VyX2lkIjoiMzIwODM4MTQ5NzM5MjMxIiwiY29kZSI6IkFRQ3lqRzFKLTRPeDUwQWtLcUdTSjNtSWVScEVNdmVqNDVBRzZPLVhvUEp5RnNONGctZGUzd2hlQk4tWjFNc2N6RVQ2d3dvcW82aTEzOGtLUXJYT1NYUWlHRUVlZWdPU05kUWh3dnJjelloM2Q3NjkzcDBlaGpxQk1xZ1Q5M3VxQTNKcl9aS0N0WVZTei04OVRQVHdZOVVRSlRnVl93dE5VeExPNEpPV0N5UmVKSWR5M0pMNF9VN01NVXp2MDh2M1lnbjQyVDBEeUlCRFJMZ3QtY2Zic0x4WDJ0RURWQmk0Z3pUS0NGaXF5dUt3YllpbENSR0RmRy0tTVNBQTdXaWVDX1JqLWZZc0ZGdWsyY1BGSE11WXR3ZDAyUjJYekowcmF1dXA0Q1duRDdDS0EzaFJwSlFyZkt1TmZZOWJuTGNwY0VXU0dWZ2tTWGJLZURYTzRyS1pfMlVEIiwib2F1dGhfdG9rZW4iOiJFQUFGbnp6ZUJmc29CUVViVU5HblIwWkFqVTFlU0Y4ajk2ZUdtZ2RJdnFBOEJOemZPNnJUT1pCWkFmUGhaQ3d1TFk1ZXoyZ0N1QzlROUI5WkI1bmNEenN2MnFUYlRYMXRrbFNjVjhNOU95MUhCc1F6cTFZejNHM2JJdUQ2TVpCdGYxUFhQQ241eGFnVVQ1RjZFcE5oZ1B0UHhzaXNkV2VKT0hhcHZuT2pqc3E5NWNrMVVLVVBza0JhNjF0TlV6S2V5aG5rUXN3VDJRWkQiLCJhbGdvcml0aG0iOiJITUFDLVNIQTI1NiIsImlzc3VlZF9hdCI6MTc2NjgyNjM5MH0; fbsr_395614663835338=aoC_bgRgk3JGRwfnHk_iloQZiyjHEt5iVHya2KpYoDs.eyJ1c2VyX2lkIjoiMzIwODM4MTQ5NzM5MjMxIiwiY29kZSI6IkFRQ3lqRzFKLTRPeDUwQWtLcUdTSjNtSWVScEVNdmVqNDVBRzZPLVhvUEp5RnNONGctZGUzd2hlQk4tWjFNc2N6RVQ2d3dvcW82aTEzOGtLUXJYT1NYUWlHRUVlZWdPU05kUWh3dnJjelloM2Q3NjkzcDBlaGpxQk1xZ1Q5M3VxQTNKcl9aS0N0WVZTei04OVRQVHdZOVVRSlRnVl93dE5VeExPNEpPV0N5UmVKSWR5M0pMNF9VN01NVXp2MDh2M1lnbjQyVDBEeUlCRFJMZ3QtY2Zic0x4WDJ0RURWQmk0Z3pUS0NGaXF5dUt3YllpbENSR0RmRy0tTVNBQTdXaWVDX1JqLWZZc0ZGdWsyY1BGSE11WXR3ZDAyUjJYekowcmF1dXA0Q1duRDdDS0EzaFJwSlFyZkt1TmZZOWJuTGNwY0VXU0dWZ2tTWGJLZURYTzRyS1pfMlVEIiwib2F1dGhfdG9rZW4iOiJFQUFGbnp6ZUJmc29CUVViVU5HblIwWkFqVTFlU0Y4ajk2ZUdtZ2RJdnFBOEJOemZPNnJUT1pCWkFmUGhaQ3d1TFk1ZXoyZ0N1QzlROUI5WkI1bmNEenN2MnFUYlRYMXRrbFNjVjhNOU95MUhCc1F6cTFZejNHM2JJdUQ2TVpCdGYxUFhQQ241eGFnVVQ1RjZFcE5oZ1B0UHhzaXNkV2VKT0hhcHZuT2pqc3E5NWNrMVVLVVBza0JhNjF0TlV6S2V5aG5rUXN3VDJRWkQiLCJhbGdvcml0aG0iOiJITUFDLVNIQTI1NiIsImlzc3VlZF9hdCI6MTc2NjgyNjM5MH0; __utmb=257500956.8.10.1766826083; _ga_6M8E625L9H=GS2.2.s1766826082$o7$g1$t1766826472$j31$l0$h0"    
}

API_PAGE_SIZE = 10

# =========================
# SESSION
# =========================
session = requests.Session()
session.headers.update(HEADERS)

# =========================
# LOAD URL LIST
# =========================
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    urls = json.load(f)

# =========================
# FUNCTIONS
# =========================
def get_restaurant_id(html):
    soup = BeautifulSoup(html, "html.parser")

    tag = soup.find(attrs={"data-res-id": True})
    if tag:
        return tag["data-res-id"]

    match = re.search(r'"restaurantId"\s*:\s*(\d+)', html)
    if match:
        return match.group(1)

    return None


def parse_reviews_from_html(html, restaurant_id):
    soup = BeautifulSoup(html, "html.parser")
    reviews = []

    for item in soup.select(".review-item"):
        reviews.append({
            "ID": item.get("data-review-id"),
            "RestaurantID": restaurant_id,
            "UserID": item.get("data-user-id"),
            "Rating": item.select_one(".review-points").text.strip()
                      if item.select_one(".review-points") else None,
            "Content": item.select_one(".review-des").text.strip()
                       if item.select_one(".review-des") else None,
            "CreatedAt": item.select_one(".review-time").text.strip()
                         if item.select_one(".review-time") else None
        })

    return reviews


def get_reviews_api(res_id, offset=0, count=API_PAGE_SIZE):
    url = "https://www.foody.vn/__get/Review/ResLoadMore"
    payload = {
        "ResId": res_id,
        "Offset": offset,
        "Count": count
    }
    r = session.post(url, data=payload, timeout=10)
    return r.json() if r.status_code == 200 else {}


def parse_reviews_from_api(api_json, restaurant_id):
    reviews = []
    soup = BeautifulSoup(api_json.get("Data", ""), "html.parser")

    for item in soup.select(".review-item"):
        reviews.append({
            "ID": item.get("data-review-id"),
            "RestaurantID": restaurant_id,
            "UserID": item.get("data-user-id"),
            "Rating": item.select_one(".review-points").text.strip()
                      if item.select_one(".review-points") else None,
            "Content": item.select_one(".review-des").text.strip()
                       if item.select_one(".review-des") else None,
            "CreatedAt": item.select_one(".review-time").text.strip()
                         if item.select_one(".review-time") else None
        })

    return reviews


# =========================
# MAIN SCRAPER
# =========================
results = []

for idx, url in enumerate(urls, start=1):
    print("=" * 80)
    print(f"[{idx}/{len(urls)}] Crawling URL:")
    print(url)
    print("=" * 80)

    try:
        page_html = session.get(url, timeout=10).text
    except Exception as e:
        print("  ❌ Page request failed:", e)
        continue

    res_id = get_restaurant_id(page_html)
    if not res_id:
        print("  ❌ RestaurantID not found")
        continue

    print(f"  ✔ RestaurantID: {res_id}")

    restaurant_block = {
        "url": url,
        "review": [],
        "initData": {}
    }

    # -------------------------
    # 1️⃣ HTML REVIEWS
    # -------------------------
    html_reviews = parse_reviews_from_html(page_html, res_id)
    if html_reviews:
        restaurant_block["review"].extend(html_reviews)
        print(f"    ✔ {len(html_reviews)} reviews from HTML")

    # -------------------------
    # 2️⃣ API REVIEWS
    # -------------------------
    offset = len(html_reviews)

    while True:
        api_data = get_reviews_api(res_id, offset)
        api_reviews = parse_reviews_from_api(api_data, res_id)

        if not api_reviews:
            print("Het review")
            break

        restaurant_block["review"].extend(api_reviews)
        print(f"    ✔ {len(api_reviews)} reviews (offset={offset})")

        offset += API_PAGE_SIZE
        time.sleep(1)

    print(f"  🧾 Total reviews: {len(restaurant_block['review'])}")
    results.append(restaurant_block)
    time.sleep(2)

# =========================
# SAVE OUTPUT
# =========================
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("\n✅ DONE")
print(f"📦 Restaurants saved: {len(results)}")
print(f"📁 Output file: {OUTPUT_FILE}")



# How to extract cookies 

# Step-by-step

# Open Chrome

#Go to https://www.foody.vn

#Log in

#Press F12 → Application → Cookies

#Select https://www.foody.vn

# Copy these values: _foody_session and .ASPXAUTH (if present)

#Inject cookies into YOUR scraper (DEMO)
# Add this AFTER creating session
# =========================
# LOGIN COOKIES (DEMO)
# =========================
#session.cookies.set(
   # name="_foody_session",
   # value="PASTE_REAL_VALUE_HERE",
   # domain=".foody.vn",
   ## path="/"
#)

# session.cookies.set(
    # name=".ASPXAUTH",
    # value="PASTE_REAL_VALUE_HERE",
    # domain=".foody.vn",
    # path="/"
# )



