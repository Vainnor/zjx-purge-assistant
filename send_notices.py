# This will handle sending emails
from zjx_utils import get_inactive_controllers
from send_email import send_inactivity_notice

def send_all_inactivity_notices():
    """
    Fetches inactive controllers and sends notices to all of them
    """
    try:
        inactive_controllers, obs_controllers, total_processed = get_inactive_controllers()
        
        print("\nSending inactivity notices...")
        for controller in inactive_controllers:
            if send_inactivity_notice(controller):
                print(f"✓ Sent notice to {controller['first_name']} {controller['last_name']}")
            else:
                print(f"✗ Failed to send notice to {controller['first_name']} {controller['last_name']}")
        
        print(f"\nSummary:")
        print(f"Total controllers processed: {total_processed}")
        print(f"Notices sent: {len(inactive_controllers)}")
        print(f"OBS controllers excluded: {len(obs_controllers)}")
        
    except Exception as e:
        print(f"Error: {e}")