import time
import random
import os
import datetime
import json
import platform
import asyncio
from dotenv import load_dotenv
from playwright.async_api import async_playwright, Page, Browser, ElementHandle, TimeoutError

# Import from the app
from app import data_manager as dm

# Load environment variables
load_dotenv()

# Get Capsolver API key from environment variables
CAPSOLVER_API_KEY = os.environ.get('CAPSOLVER_API_KEY', 'CAP-F79C6D0E7A810348A201783E25287C6003CFB45BBDCB670F96E525E7C0132148')

# ------------------------------
# Basic user agents for stealth
# ------------------------------
USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
]

# Mac-specific user agents that work well with captcha solving
MAC_USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
]

# ------------------------------
# Helper function for screenshots
# ------------------------------
async def save_screenshot(page, prefix, group_id):
    """Save a screenshot of the current page state"""
    timestamp = int(time.time())
    screenshots_dir = os.path.join(os.getcwd(), 'screenshots')
    os.makedirs(screenshots_dir, exist_ok=True)
    filename = f"{prefix}_{timestamp}.png"
    filepath = os.path.join(screenshots_dir, filename)
    await page.screenshot(path=filepath, full_page=True)
    # Log the screenshot
    dm.add_log(f"Screenshot saved: {filename}", "info", group_id=group_id)
    return filename

# ------------------------------
# Initialize the Playwright browser
# ------------------------------
async def init_browser(headless=True):
    """Initialize a Playwright browser with stealth settings"""
    # Use platform-specific user agents for better captcha solving
    system_platform = platform.system()
    
    # For GCP, always use headless mode with Linux settings
    is_cloud = os.environ.get('CLOUD_ENV', '').lower() == 'true'
    if is_cloud:
        headless = True
        system_platform = 'Linux'
        dm.add_log(f"Running in cloud environment (GCP). Using Linux configuration.", "info")
    
    if system_platform == "Darwin":  # macOS
        # On macOS, use the Mac-specific user agents that work better with captcha
        user_agent = random.choice(MAC_USER_AGENTS)
        dm.add_log(f"Using macOS user agent: {user_agent}", "info")
    else:
        # On other platforms (Linux for GCP), use a random user agent
        user_agent = random.choice(USER_AGENTS)
        dm.add_log(f"Using {system_platform} user agent: {user_agent}", "info")

    # Path to the Capsolver extension
    capsolver_extension_path = os.path.join(os.getcwd(), 'extensions', 'capsolver')
    if not os.path.exists(capsolver_extension_path):
        dm.add_log(f"Capsolver extension not found at {capsolver_extension_path}. Captcha solving may not work.", "warning")
        capsolver_extension_path = None

    # Launch playwright
    p = await async_playwright().start()
    
    # Set browser viewport and device scale factor for better rendering
    viewport_size = {'width': 1280, 'height': 800}
    
    # Create browser launch options
    browser_args = [
        '--disable-blink-features=AutomationControlled',
        '--disable-infobars',
        '--disable-dev-shm-usage',
        '--disable-setuid-sandbox',
        '--no-sandbox',
        '--start-maximized',
    ]
    
    # Load Capsolver extension if available
    if capsolver_extension_path and os.path.isdir(capsolver_extension_path):
        dm.add_log(f"Loading Capsolver extension from {capsolver_extension_path}", "info")
    
    # Create browser context with stealth settings
    browser = await p.chromium.launch(
        headless=headless,
        args=browser_args
    )
    
    # Create a new browser context with more granular settings
    context_options = {
        "user_agent": user_agent,
        "viewport": viewport_size,
        "device_scale_factor": 1.0,
        "is_mobile": False,
        "has_touch": False,
        "locale": 'en-US',
        "permissions": ['geolocation'],
        "java_script_enabled": True,
    }
    
    # Add Capsolver extension to context options if available
    if capsolver_extension_path and os.path.isdir(capsolver_extension_path):
        # Playwright can't use extensions in the same way as Selenium
        # We'll handle captcha solving separately in our code
        dm.add_log("Note: Using built-in captcha handling instead of extension", "info")
    
    context = await browser.new_context(**context_options)
    
    # Mask the fact that this is automated
    await context.add_init_script("""
    Object.defineProperty(navigator, 'webdriver', {
        get: () => false
    });
    Object.defineProperty(navigator, 'plugins', {
        get: () => [1, 2, 3, 4, 5]
    });
    window.chrome = {
        runtime: {}
    };
    """)
    
    # Create a new page
    page = await context.new_page()
    
    # Set default navigation timeout
    page.set_default_timeout(30000)  # 30 seconds
    
    # Log browser info
    dm.add_log(f"Browser initialized: Headless={headless}, Platform={system_platform}", "info")
    
    return p, browser, context, page

# ------------------------------
# Login function with URL check
# ------------------------------
async def login(page, email, password, group_id=None):
    """Login to Airtasker with the given credentials"""
    try:
        # Navigate directly to the login page
        dm.add_log(f"Navigating to login page for {email}", "info", group_id=group_id)
        await page.goto("https://www.airtasker.com/login")
        
        # Wait longer for the page to load completely to allow Capsolver extension to initialize
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(random.uniform(7, 10))  # Wait longer as in original code
        
        # Take screenshot of login page
        await save_screenshot(page, "login_page", group_id)
        
        # Type the email - using the original ID
        dm.add_log(f"Typing email: {email}", "info", group_id=group_id)
        try:
            # Wait for email field to be present - using original ID
            await page.wait_for_selector("#username", timeout=10000)
            email_field = await page.query_selector("#username")
            
            # Clear the field and type with human-like delays
            await email_field.click()
            await email_field.fill("")  # Clear the field
            
            # Type character by character with random delays
            for c in email:
                await email_field.type(c, delay=random.uniform(50, 150))
                
        except Exception as e:
            dm.add_log(f"Error finding email field: {str(e)}", "error", group_id=group_id)
            await save_screenshot(page, "email_error", group_id)
            raise

        # Type the password - using the original ID
        dm.add_log("Typing password", "info", group_id=group_id)
        try:
            password_field = await page.query_selector("#password")
            await password_field.click()
            await password_field.fill("")  # Clear the field
            
            # Type character by character with random delays
            for c in password:
                await password_field.type(c, delay=random.uniform(40, 120))
                
        except Exception as e:
            dm.add_log(f"Error finding password field: {str(e)}", "error", group_id=group_id)
            await save_screenshot(page, "password_error", group_id)
            raise

        # Wait for the Capsolver extension to automatically solve the captcha
        # This is the key part: we don't need special handling, just wait for the extension to work
        dm.add_log("Waiting for Capsolver extension to solve captcha automatically", "info", group_id=group_id)
        await asyncio.sleep(random.uniform(10, 15))  # Long wait as in original code
        
        # Take screenshot before submitting
        await save_screenshot(page, "before_submit", group_id)
        
        # Submit the login form - using the original XPath but with proper Playwright format
        dm.add_log("Submitting login form", "info", group_id=group_id)
        submit_button_xpath = "/html/body/main/section/div/div/div/form/div[2]/button"
        
        # In Playwright, XPath selectors must be prefixed with "xpath="
        await page.click(f"xpath={submit_button_xpath}")
        
        # Wait for navigation to complete
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(random.uniform(10, 15))  # Long wait as in original code
        
        # Take screenshot after login
        await save_screenshot(page, "post_login", group_id)
        
        # Check if the login was successful by looking for avatar using original XPath
        try:
            avatar_xpath = '//*[@id="overlay-provider"]/nav/div[2]/div/div/div/div[2]/button/div/div'
            avatar_element = await page.query_selector(f"xpath={avatar_xpath}", timeout=5000)
            if avatar_element:
                dm.add_log("Login successful: Avatar element found", "info", group_id=group_id)
                return True
        except:
            # If avatar not found, check URL as fallback
            current_url = page.url
            if "airtasker.com" in current_url and ("/login" not in current_url):
                dm.add_log("Login successful: Valid URL detected", "info", group_id=group_id)
                return True
            else:
                await save_screenshot(page, "login_error", group_id)
                dm.add_log(f"Login failed: Avatar not found and invalid URL. Current URL: {current_url}", "error", group_id=group_id)
                raise Exception(f"Login failed: Avatar not found and invalid URL. Current URL: {current_url}")
        
        dm.add_log("Login successful", "info", group_id=group_id)
        return True
    
    except Exception as e:
        await save_screenshot(page, "login_error", group_id)
        dm.add_log(f"Login error: {str(e)}", "error", group_id=group_id)
        raise

# ------------------------------
# Set location filter function
# ------------------------------
async def set_location_filter(page, suburb_name, radius_km=100, group_id=None):
    """Set location filter on the Airtasker tasks page"""
    try:
        dm.add_log(f"Setting location filter to {suburb_name} with {radius_km}km radius", "info", group_id=group_id)
        
        # Click the filter button - using the original XPath
        filter_button_xpath = '//*[@id="airtasker-app"]/nav/nav/div/div/div/div[3]/button'
        try:
            # Always prefix XPath selectors with "xpath="
            await page.wait_for_selector(f"xpath={filter_button_xpath}", timeout=15000)
            await page.click(f"xpath={filter_button_xpath}")
            await asyncio.sleep(random.uniform(1, 2))
        except TimeoutError:
            dm.add_log("Filter button not found within 15s.", "warning", group_id=group_id)
            await save_screenshot(page, "filter_error", group_id)
            return False

        # Input the suburb name - using the original XPath/ID
        suburb_input_xpath = '//*[@id="label-1"]'
        suburb_input = await page.query_selector(f"xpath={suburb_input_xpath}")
        await suburb_input.click()
        await suburb_input.fill("")  # Clear it first
        
        # Type character by character with random delays
        for c in suburb_name:
            await suburb_input.type(c, delay=random.uniform(50, 150))
        
        await asyncio.sleep(random.uniform(1, 2))
        
        # Select the first suggestion - using the original XPath
        first_item_xpath = '//*[@id="airtasker-app"]/nav/nav/div/div/div/div[3]/div/div[1]/div/div[4]/div/div/ul/li[1]'
        await page.wait_for_selector(f"xpath={first_item_xpath}")
        await page.click(f"xpath={first_item_xpath}")
        await asyncio.sleep(random.uniform(1, 2))
        
        # Adjust the slider for radius - using the original XPath
        try:
            # Find the slider - using original XPath
            slider_thumb_xpath = '//*[@id="airtasker-app"]/nav/nav/div/div/div/div[3]/div/div[1]/div/div[7]/div/div/button'
            slider = await page.query_selector(f"xpath={slider_thumb_xpath}")
            
            if slider:
                # Calculate the percentage position based on radius
                percentage = min(radius_km / 100.0, 1.0)  # Max is 100km (100%)
                
                # Get slider dimensions
                slider_box = await slider.bounding_box()
                
                # Calculate the target X-coordinate
                target_x = slider_box['x'] + (slider_box['width'] * percentage)
                target_y = slider_box['y'] + (slider_box['height'] / 2)
                
                # Click at that position
                await page.mouse.click(target_x, target_y)
                await asyncio.sleep(random.uniform(0.5, 1))
            else:
                dm.add_log("Slider not found. Skipping slider adjustment.", "warning", group_id=group_id)
        except Exception as e:
            dm.add_log(f"Error adjusting radius slider: {str(e)}", "warning", group_id=group_id)
        
        # Click Apply button - using the original XPath
        apply_button_xpath = '//*[@id="airtasker-app"]/nav/nav/div/div/div/div[3]/div/div[2]/button[2]'
        await page.click(f"xpath={apply_button_xpath}")
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(random.uniform(2, 4))
        
        # Verify the filter was applied
        dm.add_log(f"Filter applied for {suburb_name}", "info", group_id=group_id)
        return True
        
    except Exception as e:
        dm.add_log(f"Error setting location filter: {str(e)}", "error", group_id=group_id)
        await save_screenshot(page, "filter_error", group_id)
        return False

# ------------------------------
# Scrape tasks with infinite scroll
# ------------------------------
async def scrape_tasks(page, max_scroll=3, group_id=None):
    """Scrape tasks from the current page with infinite scrolling"""
    results = []
    seen_ids = set()
    
    dm.add_log(f"Starting task scraping with max_scroll={max_scroll}", "info", group_id=group_id)
    
    # Selector for task containers - using the original attribute
    task_container_xpath = '//a[@data-ui-test="task-list-item" and @data-task-id]'
    title_xpath = './/p[contains(@class,"TaskCard__StyledTitle")]'
    link_xpath = '.'
    
    for scroll_count in range(max_scroll):
        dm.add_log(f"Scroll {scroll_count + 1}/{max_scroll}", "info", group_id=group_id)
        
        # Wait for task containers to be visible - always prefix XPath selectors with "xpath="
        await page.wait_for_selector(f"xpath={task_container_xpath}")
        
        # Get all task containers currently visible
        containers = await page.query_selector_all(f"xpath={task_container_xpath}")
        
        # Extract data from containers
        for container in containers:
            # Get task ID - using the original attribute
            task_id = await container.get_attribute("data-task-id")
            
            # Skip if we've already seen this ID or it's None
            if not task_id or task_id in seen_ids:
                continue
            
            seen_ids.add(task_id)
            
            # Get task title - using the original XPath
            try:
                # When using container.query_selector with XPath, still need the "xpath=" prefix
                title_element = await container.query_selector(f"xpath={title_xpath}")
                title_txt = await title_element.text_content() if title_element else "Unknown Title"
            except:
                title_txt = "Unknown Title"
            
            # Get task link - using the original element
            link_url = await container.get_attribute("href")
            if link_url and not link_url.startswith('http'):
                link_url = f"https://www.airtasker.com{link_url}"
            
            # Add to results
            results.append({
                "id": task_id,
                "title": title_txt,
                "link": link_url,
            })
        
        # If we're on the last scroll or have enough tasks, break early
        if scroll_count == max_scroll - 1:
            break
        
        # Get the current height for comparison after scrolling
        prev_height = await page.evaluate("document.body.scrollHeight")
        
        # Scroll to the bottom of the page
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(random.uniform(2, 4))
        
        # Wait for new content to load
        try:
            await page.wait_for_function(
                "document.body.scrollHeight > arguments[0]",
                args=[prev_height],
                timeout=5000
            )
        except:
            dm.add_log("No more tasks loaded after scrolling. Stopping scroll.", "info", group_id=group_id)
            break
    
    dm.add_log(f"Scraped {len(results)} tasks", "info", group_id=group_id)
    return results

# ------------------------------
# Comment Functions
# ------------------------------
def pick_random_comment():
    """
    Picks a random comment template and does placeholder replacements.
    """
    RAW_MESSAGES = [
        # Message 1
        "Hey did you know there is another jobs application called ?????Tasker (Replace ????? with Smart, all one word with less fees. you are more likely to get better quotes.",
        # Message 2
        "Hey just thought I would mention that you will likely find better quotes on the new S___Tasker application (insert the word Smart, all one word). fees are 25% less.",
        # Message 3
        "Hi for this task you might want to post on *****Tasker ( Insert the word *Smart*, all one word). The fees are less so we can give you better quotes",
        # Message 4
        "Hey probably a good idea to poston the new Smart______ application. (insert the word Tasker, all one word.) You will get more quotes. And the fees are much less!",
        # Message 5
        "By the way you might get better quotes with posting to the Smart/ / / / / / application. (Replace / / / / / with Tasker, all one word) better fees for all users and more options."
    ]
    
    template = random.choice(RAW_MESSAGES)
    final = (template
             .replace("?????", "Smart")
             .replace("___", "mart")
             .replace("*****", "Smart")
             .replace("______", "Tasker")
             .replace("/ / / / / /", "Tasker")
             )
    return final

async def post_comment_on_task(page, task_url, image_path=None, group_id=None):
    """
    Navigates to the given task URL, posts a comment, and optionally attaches an image.
    """
    dm.add_log(f"Posting comment on: {task_url}", "info", group_id=group_id)
    
    # Navigate to the task page
    await page.goto(task_url)
    await page.wait_for_load_state("networkidle")
    await asyncio.sleep(random.uniform(3, 5))
    
    # Take screenshot of task page
    await save_screenshot(page, "task_page", group_id)
    
    # Generate a random comment
    comment_text = pick_random_comment()
    dm.add_log(f"Using comment: {comment_text}", "info", group_id=group_id)
    
    # Find and fill the comment textarea - using the original XPath
    comment_box_xpath = '//*[@id="airtasker-app"]/main/div/div[1]/div[3]/div/div/div[2]/div/div[6]/div/div[2]/div/div/div/div/div[3]/textarea'
    try:
        # Always prefix XPath selectors with "xpath="
        await page.wait_for_selector(f"xpath={comment_box_xpath}", timeout=15000)
        
        # Make sure the textarea is in view and click it
        comment_box = await page.query_selector(f"xpath={comment_box_xpath}")
        await comment_box.scroll_into_view_if_needed()
        await comment_box.click()
        
        # Type the comment with human-like delays
        for c in comment_text:
            await comment_box.type(c, delay=random.uniform(40, 120))
        
        await asyncio.sleep(random.uniform(1, 2))
        
        # Attach an image if provided - using the original XPath/attribute
        if image_path:
            try:
                # Find the upload input
                upload_selector = '//*[@data-ui-test="upload-attachment-input"]'
                await page.wait_for_selector(f"xpath={upload_selector}")
                
                # Upload the file
                input_element = await page.query_selector(f"xpath={upload_selector}")
                await input_element.set_input_files(image_path)
                dm.add_log(f"Attached image: {image_path}", "info", group_id=group_id)
                await asyncio.sleep(random.uniform(2, 4))
                
            except Exception as e:
                dm.add_log(f"Error attaching image: {str(e)}", "warning", group_id=group_id)
        
        # Take screenshot before sending
        await save_screenshot(page, "before_send_comment", group_id)
        
        # Click the send button - using the original XPath
        send_button_xpath = '//*[@id="airtasker-app"]/main/div/div[1]/div[3]/div/div/div[2]/div/div[6]/div/div[2]/div/div/div/div/div[3]/div/span/button'
        await page.click(f"xpath={send_button_xpath}")
        
        # Wait for the comment to be posted
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(random.uniform(2, 4))
        
        # Take screenshot after posting
        await save_screenshot(page, "after_send_comment", group_id)
        
        dm.add_log("Comment posted successfully!", "info", group_id=group_id)
        return True
        
    except Exception as e:
        dm.add_log(f"Error posting comment: {str(e)}", "error", group_id=group_id)
        await save_screenshot(page, "comment_error", group_id)
        return False

async def comment_on_some_tasks(page, tasks, max_to_post=3, image_path=None, group_id=None):
    """
    Posts comments on multiple tasks.
    """
    dm.add_log(f"Preparing to comment on up to {max_to_post} tasks", "info", group_id=group_id)
    
    # Shuffle the tasks and take the first `max_to_post`
    random.shuffle(tasks)
    tasks_to_comment = tasks[:max_to_post]
    
    successful_comments = 0
    
    for i, task in enumerate(tasks_to_comment, start=1):
        link = task.get("link")
        if not link:
            dm.add_log(f"Task {i} missing link; skipping.", "warning", group_id=group_id)
            continue
        
        dm.add_log(f"Starting comment {i}/{len(tasks_to_comment)}: {task.get('title', 'Unknown Title')}", "info", group_id=group_id)
        
        success = await post_comment_on_task(page, link, image_path=image_path, group_id=group_id)
        if success:
            successful_comments += 1
        
        # Wait between comments to avoid rate limiting
        if i < len(tasks_to_comment):
            wait_time = random.uniform(5, 10)
            dm.add_log(f"Waiting {wait_time:.1f} seconds before next comment", "info", group_id=group_id)
            await asyncio.sleep(wait_time)
    
    dm.add_log(f"Completed commenting on {successful_comments}/{len(tasks_to_comment)} tasks", "info", group_id=group_id)
    return successful_comments

# ------------------------------
# Main automation function
# ------------------------------
async def run_airtasker_bot(email, password, city_name="Sydney", max_posts=3, message_content=None, group_id=None, headless=True):
    """
    Main function to run the Airtasker automation.
    """
    p = None
    browser = None
    
    try:
        # Initialize the session info
        session_id = int(time.time())
        if not group_id:
            group_id = session_id
        
        dm.add_log(f"Starting Airtasker automation (session: {session_id})", "info", group_id=group_id)
        
        # Initialize browser
        p, browser, context, page = await init_browser(headless=headless)
        
        # 1. LOGIN
        dm.add_log("Step 1: Login", "info", group_id=group_id)
        await login(page, email, password, group_id=group_id)
        
        # 2. Navigate to tasks page
        dm.add_log("Step 2: Navigating to tasks page", "info", group_id=group_id)
        await page.goto("https://www.airtasker.com/tasks")
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(random.uniform(3, 5))
        
        # 3. Set location filter
        dm.add_log("Step 3: Setting location filter", "info", group_id=group_id)
        await set_location_filter(page, city_name, radius_km=100, group_id=group_id)
        
        # 4. Scrape tasks
        dm.add_log("Step 4: Scraping tasks", "info", group_id=group_id)
        tasks = await scrape_tasks(page, max_scroll=5, group_id=group_id)
        
        # Log the scraped tasks
        for i, task in enumerate(tasks[:5], start=1):  # Show just first 5 for brevity
            dm.add_log(f"Task {i}: {task['title']} - {task['link']}", "info", group_id=group_id)
        
        if len(tasks) > 5:
            dm.add_log(f"... and {len(tasks) - 5} more tasks", "info", group_id=group_id)
        
        # 5. Post comments on tasks
        if tasks:
            dm.add_log("Step 5: Posting comments", "info", group_id=group_id)
            await comment_on_some_tasks(page, tasks, max_to_post=max_posts, image_path=None, group_id=group_id)
        else:
            dm.add_log("No tasks found to comment on", "warning", group_id=group_id)
        
        dm.add_log("Automation completed successfully!", "info", group_id=group_id)
        return {"status": "success", "session_id": session_id, "tasks_found": len(tasks)}
        
    except Exception as e:
        dm.add_log(f"Automation failed: {str(e)}", "error", group_id=group_id)
        if page:
            await save_screenshot(page, "error", group_id)
        return {"status": "error", "message": str(e), "session_id": group_id}
        
    finally:
        # Clean up
        if browser:
            await browser.close()
        if p:
            await p.stop()

# ------------------------------
# Entry point for synchronous calls
# ------------------------------
def run_bot(email, password, city_name="Sydney", max_posts=3, message_content=None, group_id=None, headless=True):
    """
    Synchronous wrapper for the async run_airtasker_bot function.
    """
    result = asyncio.run(run_airtasker_bot(
        email=email,
        password=password,
        city_name=city_name,
        max_posts=max_posts,
        message_content=message_content,
        group_id=group_id,
        headless=headless
    ))
    return result 