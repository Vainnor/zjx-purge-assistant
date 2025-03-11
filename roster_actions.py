import requests
import json
from typing import List, Dict
import os
import dotenv
from time import sleep

def get_api_key() -> str:
    """Get VATUSA API key from environment variables"""
    dotenv.load_dotenv()
    api_key = os.getenv("VATUSA_API_KEY")
    if not api_key:
        raise ValueError("VATUSA_API_KEY not found in environment variables")
    return api_key

def get_admin_cid() -> str:
    """Get admin CID from environment variables"""
    dotenv.load_dotenv()
    admin_cid = os.getenv("ADMIN_CID")
    if not admin_cid:
        raise ValueError("ADMIN_CID not found in environment variables")
    return admin_cid

def remove_home_controller(facility: str, cid: int, reason: str, api_key: str) -> bool:
    """Remove a home controller from the facility roster"""
    url = f"https://api.vatusa.net/v2/facility/{facility}/roster/{cid}"
    
    try:
        admin_cid = get_admin_cid()
    except ValueError as e:
        print(f"Error: {e}")
        return False   
    
    data = {
        'reason': reason,
        'apikey': api_key,
        'by': admin_cid 
    }
    
    response = requests.delete(url, data=data)
    return response.status_code == 200

def remove_visiting_controller(facility: str, cid: int, reason: str, api_key: str) -> bool:
    """Remove a visiting controller from the facility roster"""
    url = f"https://api.vatusa.net/v2/facility/{facility}/roster/manageVisitor/{cid}"
    
    data = {
        'reason': reason,
        'apikey': api_key
    }
    
    response = requests.delete(url, data=data)
    return response.status_code == 200

def process_roster_removals(inactive_controllers: List[Dict], facility: str = 'ZJX'):
    """Process roster removals with verification steps"""
    
    # First verification step
    print("\n=== ROSTER REMOVAL VERIFICATION ===")
    print(f"You are about to remove {len(inactive_controllers)} controllers from {facility}")
    print("\nThis action will:")
    print("1. Remove home controllers from the facility roster")
    print("2. Remove visiting controllers from the facility roster")
    print("3. This action CANNOT be undone")
    
    confirm = input("\nDo you want to continue? (yes/no): ").lower()
    if confirm != 'yes':
        print("Roster removal cancelled.")
        return
    
    # Second verification step
    verification_code = f"{facility}-REMOVE-{len(inactive_controllers)}"
    print(f"\nPlease type the following verification code to continue: {verification_code}")
    user_input = input("Verification code: ")
    
    if user_input != verification_code:
        print("Incorrect verification code. Roster removal cancelled.")
        return
    
    # Final warning
    print("\n⚠️ FINAL WARNING ⚠️")
    print("This is your last chance to cancel this operation.")
    final_confirm = input("Type 'CONFIRM' to proceed with roster removal: ").upper()
    
    if final_confirm != 'CONFIRM':
        print("Roster removal cancelled.")
        return
    
    # Get API key
    try:
        api_key = get_api_key()
    except ValueError as e:
        print(f"Error: {e}")
        return
    
    # Process removals
    print("\nProcessing roster removals...")
    success_count = 0
    failure_count = 0
    
    for controller in inactive_controllers:
        name = f"{controller['first_name']} {controller['last_name']}"
        cid = controller['cid']
        reason = f"Controller was removed in good standing due to inactivity. ({controller['hours']} hours in last 90 days)"
        membership = controller['membership']
        
        print(f"\nProcessing removal for {name} (CID: {cid})...")
        
        try:
            if membership == 'home':
                if remove_home_controller(facility, cid, reason, api_key):
                    print(f"✓ Successfully removed home controller {name}")
                    success_count += 1
                else:
                    print(f"✗ Failed to remove home controller {name}")
                    failure_count += 1
            elif membership == 'visitor':
                if remove_visiting_controller(facility, cid, reason, api_key):
                    print(f"✓ Successfully removed visiting controller {name}")
                    success_count += 1
                else:
                    print(f"✗ Failed to remove visiting controller {name}")
                    failure_count += 1
            else:
                print(f"✗ Unknown membership type for {name}: {membership}")
                failure_count += 1
        except Exception as e:
            print(f"✗ Error removing controller {name}: {str(e)}")
            failure_count += 1
        
        # Add a small delay between requests
        sleep(1)
    
    # Print summary
    print("\n=== REMOVAL SUMMARY ===")
    print(f"Total controllers processed: {len(inactive_controllers)}")
    print(f"Successful removals: {success_count}")
    print(f"Failed removals: {failure_count}")
    
    return success_count > 0 and failure_count == 0 