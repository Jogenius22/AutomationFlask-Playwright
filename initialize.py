#!/usr/bin/env python

"""
Initialization script for Playwright in GCP App Engine.
This script runs before the main application to install browsers and dependencies.
"""

import os
import subprocess
import sys
import logging
import time
from dotenv import load_dotenv

def setup_logging():
    """Set up logging for initialization"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    return logging.getLogger("initializer")

def check_env_variables():
    """Check if required environment variables are set"""
    logger.info("Checking environment variables...")
    
    # Load environment variables from .env file if it exists
    load_dotenv()
    
    # Check for Capsolver API key
    capsolver_api_key = os.environ.get('CAPSOLVER_API_KEY')
    if not capsolver_api_key:
        logger.warning("CAPSOLVER_API_KEY environment variable not set. Using default key.")
        os.environ['CAPSOLVER_API_KEY'] = 'CAP-F79C6D0E7A810348A201783E25287C6003CFB45BBDCB670F96E525E7C0132148'
    else:
        logger.info("CAPSOLVER_API_KEY environment variable found.")
        
    # Set cloud environment variable if not set
    if not os.environ.get('CLOUD_ENV'):
        logger.info("CLOUD_ENV not set. Setting to 'true' for server environments.")
        os.environ['CLOUD_ENV'] = 'true'
    
    logger.info("Environment variables checked.")

def install_system_dependencies():
    """Install required system dependencies"""
    logger.info("Installing system dependencies...")
    
    try:
        # Install Xvfb for headless browser support
        subprocess.run(
            ["apt-get", "update", "-y"],
            check=True, capture_output=True
        )
        subprocess.run(
            ["apt-get", "install", "-y", "xvfb"],
            check=True, capture_output=True
        )
        logger.info("System dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install system dependencies: {e.stderr.decode() if hasattr(e, 'stderr') else str(e)}")
        # Continue anyway - they might already be installed in the Docker image

def install_playwright_browsers():
    """Install Playwright and browser binaries"""
    logger.info("Installing Playwright browsers...")
    
    try:
        # Install Playwright browser binaries (Chromium)
        subprocess.run(
            ["playwright", "install", "chromium"],
            check=True, capture_output=True
        )
        
        # Install browser dependencies
        subprocess.run(
            ["playwright", "install-deps", "chromium"],
            check=True, capture_output=True
        )
        
        logger.info("Playwright browsers installed successfully")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install Playwright browsers: {e.stderr.decode() if hasattr(e, 'stderr') else str(e)}")
        # This is a critical error, but we'll continue and hope for the best
        
def setup_display():
    """Set up a virtual display for headless browser operation"""
    logger.info("Setting up virtual display...")
    
    # Start Xvfb (virtual framebuffer) on display :99
    try:
        subprocess.Popen(["Xvfb", ":99", "-screen", "0", "1280x720x16"], 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL)
        os.environ["DISPLAY"] = ":99"
        logger.info("Virtual display started on :99")
    except Exception as e:
        logger.error(f"Failed to start virtual display: {str(e)}")
        # Continue anyway, as Playwright might not need it in some cases

def create_directories():
    """Create necessary directories"""
    logger.info("Creating application directories...")
    
    # Make sure screenshots directory exists
    os.makedirs('screenshots', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    
    logger.info("Directories created")

def main():
    """Main initialization function"""
    logger.info("Starting initialization...")
    
    # Check environment variables
    check_env_variables()
    
    # Cloud environment setup
    if os.environ.get('CLOUD_ENV', '').lower() == 'true':
        logger.info("Running in cloud environment")
        install_system_dependencies()
        setup_display()
    
    # Always run these steps
    install_playwright_browsers()
    create_directories()
    
    logger.info("Initialization complete!")

if __name__ == "__main__":
    logger = setup_logging()
    
    try:
        main()
    except Exception as e:
        logger.error(f"Initialization failed: {str(e)}")
        # Continue anyway to allow the app to start
    
    logger.info("Proceeding to start application...")
    # Exit with success so the application can start
    sys.exit(0) 