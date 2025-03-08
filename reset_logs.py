#!/usr/bin/env python3
import os
import json

def reset_logs():
    # Define the path to the logs file
    logs_file = os.path.join('data', 'logs.json')
    
    # Create empty logs array
    empty_logs = []
    
    # Ensure the data directory exists
    os.makedirs('data', exist_ok=True)
    
    # Write the empty logs array to the file
    with open(logs_file, 'w') as f:
        json.dump(empty_logs, f, indent=4)
    
    print(f"Logs file '{logs_file}' has been reset to an empty array.")

if __name__ == "__main__":
    print("This script will reset the logs file to an empty array.")
    confirm = input("Do you want to continue? (y/n): ")
    
    if confirm.lower() == 'y':
        reset_logs()
        print("Logs have been reset successfully.")
    else:
        print("Operation cancelled.") 