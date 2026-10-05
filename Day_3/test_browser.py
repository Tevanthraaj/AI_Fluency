from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)

    page = browser.new_page()

    page.goto(
        "https://leetcode.com/u/lB7Xv2VMcu/",
        wait_until="domcontentloaded"
    )

    # Give JavaScript time to execute
    page.wait_for_timeout(5000)

    print("TITLE:", page.title())
    print("\nPAGE TEXT:\n")
    print(page.locator("body").inner_text())

    input("\nPress Enter to close...")

    browser.close()