from playwright.sync_api import sync_playwright
import json, time

TEST_URL = "https://www.foody.vn/ha-noi/pizza-hut-xuan-thuy"

def scroll(page, max_scroll=10):
    for _ in range(max_scroll):
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(1.5)

def load_all_reviews(page, max_click=15):
    for i in range(max_click):
        try:
            btn = page.wait_for_selector(
                "a.fd-btn-more",
                timeout=5000
            )

            # Scroll nút vào viewport
            page.evaluate(
                "(el) => el.scrollIntoView({behavior: 'smooth', block: 'center'})",
                btn
            )
            time.sleep(1)

            # Force click (bỏ qua visible check)
            btn.click(force=True)
            time.sleep(2)

        except Exception as e:
            print(f"❌ Stop at click {i}: {e}")
            break

        
def extract_reviews(page):
    res_id = page.get_attribute("[data-res-id]", "data-res-id")
    reviews = []

    for item in page.query_selector_all(".review-item"):
        def safe(sel):
            el = item.query_selector(sel)
            return el.inner_text().strip() if el else None

        reviews.append({
            "ID": item.get_attribute("data-review-id"),
            "RestaurantID": res_id,
            "UserID": item.get_attribute("data-user-id"),
            "Rating": safe(".review-points"),
            "Content": safe(".review-des"),
            "CreatedAt": safe(".review-time")
        })
    return reviews

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    page.goto("https://www.foody.vn")
    input("👉 Login Foody rồi nhấn ENTER...")

    page.goto(TEST_URL)
    time.sleep(3)

    page = load_all_reviews(page)
    input("👉 Tải hết cmt rồi nhấn ENTER...")
    reviews = extract_reviews(page)

    with open("F:/HUST/Năm ba/DS/prj/data/test_review_result.json", "w", encoding="utf-8") as f:
        json.dump({
            "url": TEST_URL,
            "review": reviews,
            "initData": {}
        }, f, ensure_ascii=False, indent=2)

    print("✅ Test OK:", len(reviews), "reviews")
    browser.close()
