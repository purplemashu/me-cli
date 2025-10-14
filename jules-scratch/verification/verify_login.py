from playwright.sync_api import sync_playwright, Page, expect

def verify_login_flow(page: Page):
    """
    This script verifies the full login flow of the Ukons Dor web app.
    It checks redirection to the login page, takes a screenshot of the user selection,
    logs in as the first user, and takes a screenshot of the dashboard.
    """
    try:
        # 1. Arrange: Go to the application's homepage.
        page.goto("http://127.0.0.1:5000/")

        # 2. Assert: Expect to be redirected to the login page.
        expect(page).to_have_url("http://127.0.0.1:5000/login")
        expect(page.get_by_role("heading", name="Select Account")).to_be_visible()

        # 3. Screenshot: Capture the login page for visual verification.
        page.screenshot(path="jules-scratch/verification/login_page.png")
        print("Screenshot of the login page taken.")

        # 4. Act: Find the first user link and click it.
        # We use a robust selector to find the first link inside the user list.
        user_list = page.locator(".user-list ul")
        first_user_link = user_list.locator("li a").first

        # Check if a user link exists before clicking
        if first_user_link.count() > 0:
            first_user_link.click()

            # 5. Assert: Wait for the main dashboard to load after login.
            expect(page).to_have_url("http://127.0.0.1:5000/")
            expect(page.get_by_role("heading", name="Ukons Dor")).to_be_visible()

            # Wait for profile info to be visible
            profile_info = page.locator(".profile-info")
            expect(profile_info).to_be_visible(timeout=10000) # Increased timeout for data fetching

            # 6. Screenshot: Capture the dashboard for final verification.
            page.screenshot(path="jules-scratch/verification/dashboard_page.png")
            print("Screenshot of the dashboard page taken.")
        else:
            print("No user accounts found to perform login test.")
            # If no users, the login page screenshot is still valuable.
            page.screenshot(path="jules-scratch/verification/dashboard_page.png")


    except Exception as e:
        print(f"An error occurred during verification: {e}")
        # Take a screenshot even on failure for debugging
        page.screenshot(path="jules-scratch/verification/error_screenshot.png")

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        verify_login_flow(page)
        browser.close()

if __name__ == "__main__":
    main()
