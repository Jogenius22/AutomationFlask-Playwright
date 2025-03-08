import threading
import datetime
import logging
import traceback
import os
import uuid
from flask import current_app

from app.automations.main import run_airtasker_bot
from app import data_manager as dm

def start_bot_task(account_id, city_id, message_id, max_posts=3, image=None, headless=True):
    """
    Start the Airtasker bot as a background thread.
    
    Args:
        account_id: The ID of the account to use
        city_id: The ID of the city to use for location
        message_id: The ID of the message to use
        max_posts: Maximum number of posts to comment on
        image: Optional image path to attach
        headless: Whether to run browser in headless mode (default: False)
    """
    from app import create_app
    
    account = dm.get_account_by_id(account_id)
    city = dm.get_city_by_id(city_id)
    message = dm.get_message_by_id(message_id)
    
    # Generate a unique group ID for log filtering
    group_id = str(uuid.uuid4())
    
    dm.add_log(f"Starting bot for {account['email']} in {city['name']}", "info", group_id=group_id)
    
    if not account or not city or not message:
        error_msg = "Missing required data:"
        if not account: error_msg += " account"
        if not city: error_msg += " city"
        if not message: error_msg += " message"
        dm.add_log(error_msg, "error", group_id=group_id)
        return {"status": "error", "message": error_msg}
    
    def run_bot_with_logging():
        with create_app().app_context():
            try:
                dm.add_log(f"Using message content: {message['content']}", "info", group_id=group_id)
                # Update the last used timestamp
                dm.update_account_last_used(account_id)
                
                # Run the bot
                run_airtasker_bot(
                    email=account['email'],
                    password=account['password'],
                    city_name=city['name'],
                    max_posts=max_posts,
                    message_content=message['content'],
                    group_id=group_id,
                    headless=headless
                )
                
                dm.add_log("Bot task completed successfully", "success", group_id=group_id)
            except Exception as e:
                tb = traceback.format_exc()
                dm.add_log(f"Bot error: {str(e)}\n{tb}", "error", group_id=group_id)
    
    # Start the bot in a separate thread
    thread = threading.Thread(target=run_bot_with_logging)
    thread.daemon = True
    thread.start()
    
    return {"status": "success", "message": "Bot started", "group_id": group_id} 