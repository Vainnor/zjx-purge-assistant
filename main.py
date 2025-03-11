import argparse
from zjx_utils import get_inactive_controllers
from send_notices import send_all_inactivity_notices
from roster_actions import process_roster_removals

def display_inactive_controllers(inactive, obs, total):
    """Pretty print the results"""
    print("\nInactive Controllers (less than 3 hours in last 3 months):")
    print("=" * 80)
    print(f"{'Name':<24} {'CID':<10} {'Hours':<8} {'Rating':<8} {'Positions'}")
    print("-" * 80)
    for controller in inactive:
        name = f"{controller['first_name']} {controller['last_name']}"
        positions_str = ', '.join(controller['positions']) if controller['positions'] else 'No ZJX positions'
        print(f"{name:<24} {controller['cid']:<10} {controller['hours']:<8} {controller['rating']:<8} {positions_str}")
    
    print("\nExcluded OBS-Rated Controllers:")
    print("=" * 40)
    print(f"{'Name':<24} {'CID':<10}")
    print("-" * 40)
    for controller in obs:
        name = f"{controller['first_name']} {controller['last_name']}"
        print(f"{name:<24} {controller['cid']:<10}")
    
    print(f"\nTotal controllers processed: {total}")
    print(f"Total inactive controllers: {len(inactive)}")
    print(f"Total OBS controllers excluded: {len(obs)}")

def process_full_removal(inactive, obs, total):
    """Process both notifications and roster removals"""
    print("\n=== STARTING EMAIL NOTIFICATIONS ===")
    if not send_all_inactivity_notices(inactive, obs, total):
        print("Failed to send all notifications. Aborting roster removal.")
        return False
    
    print("\n=== STARTING ROSTER REMOVALS ===")
    return process_roster_removals(inactive)

def main():
    parser = argparse.ArgumentParser(description='ZJX Controller Activity Management')
    parser.add_argument('action', choices=['check', 'send-notices', 'remove'],
                      help='Action to perform (check: just display inactive controllers, '
                           'send-notices: send email notices, '
                           'remove: send notices AND remove from roster)')
    
    args = parser.parse_args()
    
    try:
        # Get the data once
        inactive, obs, total = get_inactive_controllers()
        
        if args.action == 'check':
            # Just display the results
            display_inactive_controllers(inactive, obs, total)
            
        elif args.action == 'send-notices':
            # Display results and send notices
            display_inactive_controllers(inactive, obs, total)
            send_all_inactivity_notices(inactive, obs, total)
            
        elif args.action == 'remove':
            # Display results, send notices, and remove from roster
            display_inactive_controllers(inactive, obs, total)
            process_full_removal(inactive, obs, total)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()