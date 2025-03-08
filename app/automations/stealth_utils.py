"""
Stealth utilities for Selenium WebDriver
This module provides functions and utilities to enhance bot stealth capabilities
and reduce the likelihood of detection when automating browser tasks.
"""

import random
import time
import platform
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# More realistic and diverse user agents
DESKTOP_USER_AGENTS = [
    # Windows Chrome
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    # Windows Firefox
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    # Windows Edge
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    # macOS Safari
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15",
    # macOS Chrome
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    # macOS Firefox
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
    # Linux
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
]

MOBILE_USER_AGENTS = [
    # iOS Safari
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_7_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.7 Mobile/15E148 Safari/604.1",
    # Android Chrome
    "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.144 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.163 Mobile Safari/537.36",
    # Android Firefox
    "Mozilla/5.0 (Android 13; Mobile; rv:121.0) Gecko/121.0 Firefox/121.0",
]

# Common screen resolutions
SCREEN_RESOLUTIONS = {
    'desktop': [
        (1920, 1080), (1366, 768), (1440, 900), (1536, 864),
        (2560, 1440), (1680, 1050), (1280, 720), (1600, 900)
    ],
    'mobile': [
        (375, 812),  # iPhone X/XS/11 Pro
        (414, 896),  # iPhone XR/11
        (360, 800),  # Samsung Galaxy S10e
        (412, 915),  # Pixel 5
        (390, 844),  # iPhone 12/13
    ]
}

# Common languages and locales
LANGUAGES = [
    "en-US", "en-GB", "en-AU", "en-CA", 
    "es-ES", "fr-FR", "de-DE", "it-IT",
    "pt-BR", "nl-NL", "sv-SE", "no-NO",
    "fi-FI", "da-DK", "pl-PL", "ru-RU"
]

# Common timezone offsets
TIMEZONE_OFFSETS = [
    # US, Canada
    -480, -420, -360, -300, -240,
    # Europe
    60, 120, 180,
    # Asia, Australia
    330, 480, 540, 600,
    # Uncommon offsets for randomization
    -570, -270, 90, 345
]

def get_random_user_agent(device_type='desktop'):
    """Get a random user agent for the specified device type"""
    if device_type.lower() == 'mobile':
        return random.choice(MOBILE_USER_AGENTS)
    return random.choice(DESKTOP_USER_AGENTS)

def get_random_resolution(device_type='desktop'):
    """Get a random screen resolution for the specified device type"""
    return random.choice(SCREEN_RESOLUTIONS[device_type.lower()])

def get_random_language():
    """Get a random language/locale"""
    return random.choice(LANGUAGES)

def get_random_timezone_offset():
    """Get a random timezone offset in minutes"""
    return random.choice(TIMEZONE_OFFSETS)

def add_stealth_js_snippets(driver):
    """Execute JavaScript snippets to mask WebDriver presence"""
    scripts = [
        # Remove webdriver property
        """
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
        """,
        
        # Modify navigator properties
        """
        const newProto = navigator.__proto__;
        delete newProto.webdriver;
        navigator.__proto__ = newProto;
        """,
        
        # Add missing chrome properties
        """
        if (window.chrome === undefined) {
            window.chrome = {
                runtime: {}, 
                loadTimes: function() {}, 
                csi: function() {}, 
                app: {
                    isInstalled: false
                }
            };
        }
        """,
        
        # Add language plugin
        """
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en', 'es'],
        });
        """,
        
        # Add fake plugins (Flash, Chrome PDF Viewer, etc.)
        """
        Object.defineProperty(navigator, 'plugins', {
            get: () => {
                const plugins = [
                    { name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer', description: 'Portable Document Format' },
                    { name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai', description: 'Portable Document Format' },
                    { name: 'Native Client', filename: 'internal-nacl-plugin', description: '' }
                ];
                
                // Create a PluginArray-like object
                const pluginArray = {};
                for (let i = 0; i < plugins.length; i++) {
                    pluginArray[i] = plugins[i];
                }
                pluginArray.length = plugins.length;
                
                return pluginArray;
            }
        });
        """,
        
        # Add permission state
        """
        if (navigator.permissions) {
            navigator.permissions.query = function(parameters) {
                return Promise.resolve({ state: 'prompt', onchange: null });
            };
        }
        """
    ]
    
    for script in scripts:
        try:
            driver.execute_script(script)
        except Exception:
            pass  # Silently fail on unsupported scripts

def configure_stealth_options(options=None, device_type='desktop', use_proxy=False, proxy=None):
    """Configure Chrome options for maximum stealth"""
    if options is None:
        options = Options()
    
    # Get random configurations
    user_agent = get_random_user_agent(device_type)
    width, height = get_random_resolution(device_type)
    language = get_random_language()
    tz_offset = get_random_timezone_offset()
    
    # Set user agent
    options.add_argument(f'--user-agent={user_agent}')
    
    # Set window size
    options.add_argument(f'--window-size={width},{height}')
    
    # Set accepted languages
    options.add_argument(f'--lang={language}')
    
    # Timezone
    options.add_argument(f'--timezone={tz_offset}')
    
    # Mask automated software
    options.add_argument('--disable-blink-features=AutomationControlled')
    
    # Disable automation flag
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Disable certain features that can reveal it's a bot
    options.add_argument('--disable-infobars')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    # Randomize fingerprint
    options.add_argument('--disable-canvas-aa')
    options.add_argument('--disable-2d-canvas-clip-aa')
    options.add_argument('--disable-web-security')
    
    # Add additional randomized args
    if random.random() > 0.5:
        options.add_argument('--disable-features=IsolateOrigins,site-per-process')
    
    # Add proxy if enabled
    if use_proxy and proxy:
        options.add_argument(f'--proxy-server={proxy}')
    
    return options

def add_humanlike_delays():
    """Add a random human-like delay during actions"""
    delay_type = random.choice(['short', 'medium', 'long', 'variable'])
    
    if delay_type == 'short':
        time.sleep(random.uniform(0.1, 0.5))
    elif delay_type == 'medium':
        time.sleep(random.uniform(0.5, 1.5))
    elif delay_type == 'long':
        time.sleep(random.uniform(1.5, 3.0))
    else:  # variable
        # Occasional longer pauses to simulate human behavior
        if random.random() < 0.1:  # 10% chance
            time.sleep(random.uniform(3.0, 8.0))
        else:
            time.sleep(random.uniform(0.2, 1.0))

def human_like_typing(element, text, min_delay=0.03, max_delay=0.2):
    """Type text like a human with variable speed and occasional mistakes"""
    for char in text:
        # Sometimes people make typos and correct them
        if random.random() < 0.02:  # 2% chance of typo
            typo_char = random.choice('abcdefghijklmnopqrstuvwxyz')
            element.send_keys(typo_char)
            time.sleep(random.uniform(0.1, 0.3))
            element.send_keys('\b')  # Backspace to delete the typo
            time.sleep(random.uniform(0.1, 0.2))
        
        # Type the correct character with variable speed
        element.send_keys(char)
        
        # Variable delay between keystrokes
        if char in ['.', ',', '!', '?', ';', ':']:
            # Longer pauses after punctuation
            time.sleep(random.uniform(max_delay * 1.5, max_delay * 2.5))
        elif char == ' ':
            # Slight pause after spaces
            time.sleep(random.uniform(min_delay * 1.2, max_delay * 1.2))
        elif random.random() < 0.03:  # 3% chance of a thinking pause
            # Occasionally pause like a human thinking
            time.sleep(random.uniform(0.5, 1.5))
        else:
            # Normal typing speed with slight variations
            time.sleep(random.uniform(min_delay, max_delay))
            
        # Sometimes add a brief pause in the middle of typing longer texts
        if len(text) > 20 and random.random() < 0.01:  # 1% chance in longer texts
            time.sleep(random.uniform(0.8, 2.0))

def human_like_mouse_movement(driver, element, direct_movement=False):
    """Move mouse to an element with human-like movement patterns"""
    try:
        from selenium.webdriver.common.action_chains import ActionChains
        
        if direct_movement:
            # Simple direct movement
            ActionChains(driver).move_to_element(element).perform()
            return
        
        # Get element location for target
        elem_rect = element.rect
        target_x = elem_rect['x'] + elem_rect['width'] // 2
        target_y = elem_rect['y'] + elem_rect['height'] // 2
        
        # Get current mouse position or use a reasonable starting point
        try:
            # This might not be supported in all browser drivers
            current_x, current_y = driver.execute_script(
                "return [window.mouseX || 0, window.mouseY || 0];"
            )
        except:
            # Use a reasonable starting position if we can't get the current mouse
            viewport_width, viewport_height = driver.execute_script(
                "return [window.innerWidth, window.innerHeight];"
            )
            current_x = random.randint(0, viewport_width)
            current_y = random.randint(0, viewport_height)
        
        # Calculate distance
        distance = ((target_x - current_x) ** 2 + (target_y - current_y) ** 2) ** 0.5
        
        # If almost at the target, just move directly
        if distance < 50:
            ActionChains(driver).move_to_element(element).perform()
            return
        
        # Create a curve with random control points for natural movement
        steps = int(min(max(distance / 50, 5), 15))  # 5-15 steps based on distance
        
        # Create a curve with random control points for natural movement
        control_x1 = current_x + (target_x - current_x) / 3 + random.randint(-100, 100)
        control_y1 = current_y + (target_y - current_y) / 3 + random.randint(-100, 100)
        control_x2 = current_x + 2 * (target_x - current_x) / 3 + random.randint(-100, 100)
        control_y2 = current_y + 2 * (target_y - current_y) / 3 + random.randint(-100, 100)
        
        for i in range(1, steps + 1):
            t = i / steps
            # Bezier curve formula for cubic curve
            x = (1-t)**3 * current_x + 3*(1-t)**2*t * control_x1 + 3*(1-t)*t**2 * control_x2 + t**3 * target_x
            y = (1-t)**3 * current_y + 3*(1-t)**2*t * control_y1 + 3*(1-t)*t**2 * control_y2 + t**3 * target_y
            
            # Move to the calculated point
            try:
                driver.execute_script(f"arguments[0].scrollIntoView({{block: 'center', inline: 'center'}});", element)
                ActionChains(driver).move_by_offset(int(x - current_x), int(y - current_y)).perform()
                current_x, current_y = x, y
            except:
                # If the movement fails, fallback to direct movement
                ActionChains(driver).move_to_element(element).perform()
                break
                
            # Add a short delay between movements
            time.sleep(random.uniform(0.01, 0.03))
        
        # Finally, ensure we're precisely on the element
        ActionChains(driver).move_to_element(element).perform()
    
    except Exception as e:
        # Fall back to direct movement if any errors
        print(f"Error in human-like mouse movement: {str(e)}")
        try:
            ActionChains(driver).move_to_element(element).perform()
        except:
            pass  # Ignore if even this fails

def human_like_scroll(driver, direction='down', distance=None, speed='medium'):
    """Scroll the page in a human-like way"""
    # Define scroll speeds
    scroll_speeds = {
        'slow': {'chunk_size': (50, 100), 'delay': (0.1, 0.3)},
        'medium': {'chunk_size': (100, 300), 'delay': (0.05, 0.15)},
        'fast': {'chunk_size': (200, 500), 'delay': (0.02, 0.08)}
    }
    
    # Get the current scroll parameters
    params = scroll_speeds.get(speed, scroll_speeds['medium'])
    
    # Determine scroll direction multiplier
    direction_multiplier = 1 if direction.lower() == 'down' else -1
    
    # Get page height
    total_height = driver.execute_script("return document.body.scrollHeight")
    viewport_height = driver.execute_script("return window.innerHeight")
    current_position = driver.execute_script("return window.pageYOffset")
    
    # Calculate how far to scroll
    if distance is None:
        # Default to approximately 1 viewport height with some randomness
        distance = int(viewport_height * random.uniform(0.7, 1.3))
    
    # Limit scrolling to not go beyond page bounds
    if direction_multiplier > 0:  # scrolling down
        max_scroll = total_height - viewport_height - current_position
        distance = min(distance, max_scroll)
    else:  # scrolling up
        max_scroll = current_position
        distance = min(distance, max_scroll)
    
    # If there's nowhere to scroll, just return
    if distance <= 0:
        return
    
    # Scroll in chunks with random delays for natural behavior
    scrolled = 0
    while scrolled < distance:
        # Determine next chunk size
        chunk = min(random.randint(*params['chunk_size']), distance - scrolled)
        scrolled += chunk
        
        # Execute scroll
        driver.execute_script(f"window.scrollBy(0, {chunk * direction_multiplier});")
        
        # Random delay between scrolls
        time.sleep(random.uniform(*params['delay']))
        
        # Occasionally pause for a moment (like a human reading/thinking)
        if random.random() < 0.1:  # 10% chance
            time.sleep(random.uniform(0.5, 2.0))

def randomize_viewport(driver):
    """Randomly resize the browser viewport for less predictable fingerprinting"""
    try:
        # Get the screen dimensions
        screen_width, screen_height = driver.execute_script(
            "return [window.screen.availWidth, window.screen.availHeight];"
        )
        
        # Calculate a random size that's reasonably large but smaller than screen
        width = random.randint(int(screen_width * 0.5), int(screen_width * 0.95))
        height = random.randint(int(screen_height * 0.5), int(screen_height * 0.95))
        
        # Set the new window size
        driver.set_window_size(width, height)
        
        # Optionally add a small chance to maximize the window
        if random.random() < 0.2:  # 20% chance
            driver.maximize_window()
            
        # Add a small pause after resizing
        time.sleep(random.uniform(0.3, 0.8))
        
        return True
    except Exception as e:
        print(f"Error randomizing viewport: {str(e)}")
        return False 