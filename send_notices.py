# This will handle sending emails
from zjx_utils import get_inactive_controllers
from send_email import send_inactivity_notice

def send_all_inactivity_notices(inactive_controllers, obs_controllers, total_processed):
    """
    Sends notices to all inactive controllers
    Returns: bool indicating if all notices were sent successfully
    """
    try:
        print("\nSending inactivity notices...")
        success_count = 0
        failure_count = 0
        
        for controller in inactive_controllers:
            if send_inactivity_notice(controller):
                print(f"✓ Sent notice to {controller['first_name']} {controller['last_name']}")
                success_count += 1
            else:
                print(f"✗ Failed to send notice to {controller['first_name']} {controller['last_name']}")
                failure_count += 1
        
        print(f"\nEmail Summary:")
        print(f"Total controllers processed: {total_processed}")
        print(f"Successful notices: {success_count}")
        print(f"Failed notices: {failure_count}")
        print(f"OBS controllers excluded: {len(obs_controllers)}")
        
        # Return True only if all emails were sent successfully
        return failure_count == 0
        
    except Exception as e:
        print(f"Error sending notices: {e}")
        return False