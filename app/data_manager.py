import json
import os
import uuid
from datetime import datetime
from config import ACCOUNTS_FILE, CITIES_FILE, MESSAGES_FILE, SCHEDULES_FILE, LOGS_FILE, SETTINGS_FILE
import math

def generate_id():
    """Generate a unique ID for new records"""
    return str(uuid.uuid4())

def datetime_converter(obj):
    """Convert datetime objects to ISO format for JSON serialization"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

def get_accounts():
    """Get all accounts from JSON file"""
    if os.path.exists(ACCOUNTS_FILE):
        with open(ACCOUNTS_FILE, 'r') as f:
            return json.load(f)
    return []

def add_account(email, password, active=True):
    """Add a new account to JSON file"""
    accounts = get_accounts()
    new_account = {
        'id': generate_id(),
        'email': email,
        'password': password,
        'active': active,
        'last_used': None,
        'created_at': datetime.utcnow().isoformat()
    }
    accounts.append(new_account)
    with open(ACCOUNTS_FILE, 'w') as f:
        json.dump(accounts, f, indent=4)
    return new_account

def get_cities():
    """Get all cities from JSON file"""
    if os.path.exists(CITIES_FILE):
        with open(CITIES_FILE, 'r') as f:
            return json.load(f)
    return []

def add_city(name, radius):
    """Add a new city to JSON file"""
    cities = get_cities()
    new_city = {
        'id': generate_id(),
        'name': name,
        'radius': int(radius),
        'created_at': datetime.utcnow().isoformat()
    }
    cities.append(new_city)
    with open(CITIES_FILE, 'w') as f:
        json.dump(cities, f, indent=4)
    return new_city

def get_messages():
    """Get all messages from JSON file"""
    if os.path.exists(MESSAGES_FILE):
        with open(MESSAGES_FILE, 'r') as f:
            return json.load(f)
    return []

def add_message(content, image=None):
    """Add a new message to JSON file"""
    messages = get_messages()
    new_message = {
        'id': generate_id(),
        'content': content,
        'image': image,
        'created_at': datetime.utcnow().isoformat(),
        'last_used': None
    }
    messages.append(new_message)
    with open(MESSAGES_FILE, 'w') as f:
        json.dump(messages, f, indent=4)
    return new_message

def get_schedules():
    """Get all schedules from JSON file"""
    if os.path.exists(SCHEDULES_FILE):
        with open(SCHEDULES_FILE, 'r') as f:
            return json.load(f)
    return []

def add_schedule(start_time, end_time, active=True):
    """Add a new schedule to JSON file"""
    schedules = get_schedules()
    new_schedule = {
        'id': generate_id(),
        'start_time': start_time,
        'end_time': end_time,
        'active': active,
        'created_at': datetime.utcnow().isoformat()
    }
    schedules.append(new_schedule)
    with open(SCHEDULES_FILE, 'w') as f:
        json.dump(schedules, f, indent=4)
    return new_schedule

def get_logs(page=1, per_page=10, group_id=None):
    """
    Get logs from the log file with pagination
    
    Args:
        page (int): Page number (1-indexed)
        per_page (int): Number of logs per page
        group_id (str, optional): Filter logs by group_id
        
    Returns:
        dict: Dictionary with logs and pagination information
    """
    try:
        # Ensure parameters are valid
        page = max(1, int(page))
        per_page = max(1, int(per_page))
        
        if os.path.exists(LOGS_FILE):
            try:
                with open(LOGS_FILE, 'r') as f:
                    logs = json.load(f)
                print(f"Successfully loaded {len(logs)} logs from {LOGS_FILE}")
            except json.JSONDecodeError as e:
                print(f"JSON decode error when loading logs: {e}")
                logs = []
        else:
            print(f"Logs file not found at {LOGS_FILE}")
            logs = []
        
        # Make sure logs is a list
        if not isinstance(logs, list):
            print(f"Logs is not a list, it's a {type(logs)}")
            logs = []
            
        # Filter by group_id if provided
        if group_id:
            filtered_logs = [log for log in logs if log.get('group_id') == group_id]
            print(f"Filtered logs by group_id {group_id}: {len(filtered_logs)} of {len(logs)} logs match")
            logs = filtered_logs
            
        # Sort logs by timestamp (newest first)
        logs = sorted(logs, key=lambda x: x.get('timestamp', ''), reverse=True)
        
        # Calculate pagination
        total_logs = len(logs)
        total_pages = math.ceil(total_logs / per_page) if total_logs > 0 else 1
        page = min(max(1, page), total_pages)
        
        # Get logs for the requested page
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        page_logs = logs[start_idx:end_idx] if logs else []
        
        result = {
            'items': page_logs,
            'total': total_logs,
            'page': page,
            'per_page': per_page,
            'pages': total_pages
        }
        print(f"Returning {len(page_logs)} logs for page {page} of {total_pages}")
        return result
    except Exception as e:
        print(f"Error getting logs: {str(e)}")
        # Return a valid structure even on error
        return {
            'items': [],
            'total': 0,
            'page': 1,
            'per_page': per_page,
            'pages': 0
        }

def add_log(message, level='info', group_id=None):
    """
    Add a log entry to the log file
    
    Args:
        message (str): Log message
        level (str): Log level (info, warning, error)
        group_id (str, optional): Group ID to associate related logs together
        
    Returns:
        dict: The log entry that was added
    """
    try:
        # Load existing logs or create empty list
        logs = []
        if os.path.exists(LOGS_FILE):
            try:
                with open(LOGS_FILE, 'r') as f:
                    logs = json.load(f)
                print(f"Successfully loaded {len(logs)} existing logs from {LOGS_FILE}")
            except json.JSONDecodeError:
                print(f"JSON decode error when loading logs file. Creating new logs array.")
                logs = []  # Reset logs if file is corrupted
        else:
            print(f"Logs file not found at {LOGS_FILE}. Creating new file.")
        
        # Sanitize message for JSON compatibility
        if message is not None:
            # Limit message length
            message = str(message)[:2000]
            # Replace control characters that would break JSON
            message = ''.join(c if ord(c) >= 32 or c in '\n\r\t' else ' ' for c in message)
        
        # Create new log entry
        log_entry = {
            'id': str(uuid.uuid4()),
            'message': message,
            'level': level,
            'timestamp': datetime.now().isoformat()
        }
        
        # Add group_id if provided
        if group_id:
            log_entry['group_id'] = group_id
            print(f"Adding log with group_id {group_id}: {message[:50]}...")
        else:
            print(f"Adding log without group_id: {message[:50]}...")
        
        # Append new log
        logs.append(log_entry)
        
        # Sort logs by timestamp (newest first)
        logs = sorted(logs, key=lambda x: x.get('timestamp', ''), reverse=True)
        
        # Keep only the last 1000 logs to prevent file growth
        logs = logs[:1000]
        
        # Write logs back to file
        with open(LOGS_FILE, 'w') as f:
            json.dump(logs, f, indent=4)
        
        print(f"Successfully saved {len(logs)} logs to {LOGS_FILE}")
        return log_entry
    except Exception as e:
        print(f"Error adding log: {str(e)}")
        return {
            'id': str(uuid.uuid4()),
            'message': f"Error adding log: {str(e)}",
            'level': 'error',
            'timestamp': datetime.now().isoformat()
        }

def get_settings():
    """Get application settings"""
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    return {
        "run_interval": 30,
        "max_posts_per_day": 10,
        "timeout_between_actions": 5,
        "enable_random_delays": True
    }

def update_settings(settings_data):
    """Update application settings"""
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings_data, f, indent=4)
    return settings_data

def get_account_by_id(account_id):
    """Get an account by its ID"""
    accounts = get_accounts()
    for account in accounts:
        if account['id'] == account_id:
            return account
    return None

def get_city_by_id(city_id):
    """Get city by ID"""
    cities = get_cities()
    for city in cities:
        if city['id'] == city_id:
            return city
    return None

def get_message_by_id(message_id):
    """Get message by ID"""
    messages = get_messages()
    for message in messages:
        if message['id'] == message_id:
            return message
    return None

def update_account_last_used(account_id):
    """Update last_used timestamp for account"""
    accounts = get_accounts()
    for account in accounts:
        if account['id'] == account_id:
            account['last_used'] = datetime.utcnow().isoformat()
            break
    
    with open(ACCOUNTS_FILE, 'w') as f:
        json.dump(accounts, f, indent=4)

def delete_account(account_id):
    """Delete an account by ID"""
    accounts = get_accounts()
    accounts = [account for account in accounts if account['id'] != account_id]
    with open(ACCOUNTS_FILE, 'w') as f:
        json.dump(accounts, f, indent=4)
    return True

def delete_city(city_id):
    """Delete a city by ID"""
    cities = get_cities()
    cities = [city for city in cities if city['id'] != city_id]
    with open(CITIES_FILE, 'w') as f:
        json.dump(cities, f, indent=4)
    return True

def delete_message(message_id):
    """Delete a message by ID"""
    messages = get_messages()
    # Find the message to delete and get its image filename if it exists
    image_to_delete = None
    for message in messages:
        if message['id'] == message_id and message.get('image'):
            image_to_delete = message['image']
            break
    
    # Filter out the message to be deleted
    messages = [message for message in messages if message['id'] != message_id]
    
    with open(MESSAGES_FILE, 'w') as f:
        json.dump(messages, f, indent=4)
    
    # Return the image filename if it exists, so it can be deleted from the filesystem
    return image_to_delete

def delete_schedule(schedule_id):
    """Delete a schedule by ID"""
    schedules = get_schedules()
    schedules = [schedule for schedule in schedules if schedule['id'] != schedule_id]
    with open(SCHEDULES_FILE, 'w') as f:
        json.dump(schedules, f, indent=4)
    return True

def update_last_used(account_id):
    """Update the last_used timestamp for an account"""
    accounts = get_accounts()
    for account in accounts:
        if account['id'] == account_id:
            account['last_used'] = datetime.utcnow().isoformat()
            with open(ACCOUNTS_FILE, 'w') as f:
                json.dump(accounts, f, indent=4)
            return True
    return False 