import argparse
from zjx_utils import get_inactive_controllers
from send_notices import send_all_inactivity_notices

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

def main():
    parser = argparse.ArgumentParser(description='ZJX Controller Activity Management')
    parser.add_argument('action', choices=['check', 'send-notices'],
                      help='Action to perform (check: just display inactive controllers, send-notices: send email notices)')
    
    args = parser.parse_args()
    
    try:
        if args.action == 'check':
            # Just check and display inactive controllers
            inactive, obs, total = get_inactive_controllers()
            display_inactive_controllers(inactive, obs, total)
            
        elif args.action == 'send-notices':
            # Send notices to inactive controllers
            send_all_inactivity_notices()
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()