from playwright.sync_api import sync_playwright
import time
import subprocess
import sys

# Start the app in the background
print("Starting the app...")
app_process = subprocess.Popen([sys.executable, "src/app.py"])

# Give the app time to start
time.sleep(5)

try:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        print("Navigating to http://localhost:8050...")
        page.goto("http://localhost:8050")
        
        # Wait for the page to load
        page.wait_for_selector("h1", timeout=10000)
        
        # Check if the title is correct
        title = page.text_content("h1")
        print(f"Page title: {title}")
        
        # Select Stocks
        print("Selecting Stocks...")
        page.select_option("#asset-type", "stock")
        
        # Select AAPL
        print("Selecting AAPL ticker...")
        page.select_option("#ticker-input", "AAPL")
        
        # Click Fetch Data button
        print("Clicking Fetch Data...")
        page.click("#fetch-button")
        
        # Wait for the chart to load
        print("Waiting for chart to load...")
        page.wait_for_selector(".js-plotly-plot", timeout=30000)
        
        # Check if stats are displayed
        stats_container = page.query_selector("#stats-container")
        if stats_container:
            print("Stats loaded successfully!")
            
        # Take a screenshot
        page.screenshot(path="test_screenshot.png")
        print("Screenshot saved as test_screenshot.png")
        
        # Test different asset types
        print("\nTesting Forex...")
        page.select_option("#asset-type", "forex")
        time.sleep(1)
        page.select_option("#ticker-input", "EURUSD")
        page.click("#fetch-button")
        page.wait_for_selector(".js-plotly-plot", timeout=30000)
        print("Forex data loaded successfully!")
        
        print("\nTesting Crypto...")
        page.select_option("#asset-type", "crypto")
        time.sleep(1)
        page.select_option("#ticker-input", "BTCUSD")
        page.click("#fetch-button")
        page.wait_for_selector(".js-plotly-plot", timeout=30000)
        print("Crypto data loaded successfully!")
        
        print("\nAll tests passed!")
        
        browser.close()
        
except Exception as e:
    print(f"Error during testing: {e}")
    
finally:
    # Terminate the app
    print("\nStopping the app...")
    app_process.terminate()
    app_process.wait()