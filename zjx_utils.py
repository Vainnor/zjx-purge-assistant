# Core Functionallity
import requests
import json
from datetime import datetime, timedelta, UTC
from time import sleep
from random import uniform

def get_with_retry(url, max_retries=10, base_delay=5):
    """
    Make a GET request with exponential backoff for rate limiting
    """
    for attempt in range(max_retries):
        try:
            response = requests.get(url)
            
            # If successful, return response
            if response.status_code == 200:
                return response
                
            # If rate limited (429) or server error (5xx), wait and retry
            if response.status_code in [429, 500, 502, 503, 504]:
                delay = (base_delay * (2 ** attempt)) + uniform(0, 1)
                print(f"Rate limited. Waiting {delay:.1f} seconds before retry...")
                sleep(delay)
                continue
                
            # If other error, return response
            return response
            
        except Exception as e:
            print(f"Request error: {e}")
            if attempt == max_retries - 1:
                raise
            
            delay = (base_delay * (2 ** attempt)) + uniform(0, 1)
            sleep(delay)
    
    return None

def get_inactive_controllers(batch_size=10):
    """
    Collects and returns inactive controller data without taking any action
    Returns: tuple (inactive_controllers, obs_controllers, total_processed)
    """
    watched_positions = ['JAX_','MCO_','PNS_','CAE_','CHS_','DAB_','FLO_','MYR_','PAM_','SAV_',
                        'TLH_','VLD_','VPS_','NBC_','OZR_','SSC_','ABY_','COF_','CRE_','CRG_',
                        'DHN_','DTS_','ECP_','EGI_','EVB_','EZM_','FIN_','GNV_','HRT_','HXD_',
                        'ISM_','JKA_','LCQ_','LEE_','LHW_','MLB_','MMT_','NDZ_','NEN_','NFJ_',
                        'NIP_','_NPA','NRB_','NSE_','OCF_','ORL_','SFB_','SGJ_','SVN_','TIX_',
                        'TOI_','TTS_','VAD_','VQQ_','XMR_']
    
    roster_url = "https://api.vatusa.net/v2/facility/ZJX/roster/both"
    
    # Get the roster
    roster_response = get_with_retry(roster_url)
    if not roster_response or roster_response.status_code != 200:
        raise Exception("Failed to fetch roster data")
        
    roster_data = json.loads(roster_response.text)
    return process_batch(roster_data['data'], watched_positions, batch_size)

def process_batch(controllers, watched_positions, batch_size=10):
    """Process controllers in smaller batches"""
    inactive_controllers = []
    obs_controllers = []
    processed_count = 0
    total_controllers = len(controllers)
    stats_url = "https://api.vatsim.net/v2/members/{}/atc"
    
    # Filter out OBS controllers first
    active_controllers = []
    for controller in controllers:
        if controller['rating_short'] == "OBS":
            obs_controllers.append({
                'first_name': controller['fname'],
                'last_name': controller['lname'],
                'cid': controller['cid']
            })
        else:
            active_controllers.append(controller)
    
    # Update total_controllers to exclude OBS
    total_controllers = len(active_controllers)
    number_of_batches = total_controllers / batch_size
    print(f"\nExcluded {len(obs_controllers)} OBS-rated controllers")
    print(f"Processing {total_controllers} rated controllers in {number_of_batches} batches...")
    
    for i in range(0, len(active_controllers), batch_size):
        batch = active_controllers[i:i + batch_size]
        print(f"\nProcessing batch {(i//batch_size)+1}...")
        
        for controller in batch:
            try:
                cid = controller['cid']
                first_name = controller['fname']
                last_name = controller['lname']
                
                stats_response = get_with_retry(stats_url.format(cid))
                
                if stats_response and stats_response.status_code == 200:
                    current_time = datetime.now(UTC)
                    three_months_ago = current_time - timedelta(days=90)
                    
                    total_hours = 0
                    positions_worked = set()
                    stats_data = json.loads(stats_response.text)
                    
                    # Calculate total hours
                    for session in stats_data['items']:
                        start_time = datetime.strptime(session['connection_id']['start'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=UTC)
                        
                        if start_time >= three_months_ago:
                            callsign = session['connection_id']['callsign']
                            is_zjx_position = any(callsign.startswith(prefix) for prefix in watched_positions)
                            
                            if is_zjx_position:
                                end_time = datetime.strptime(session['connection_id']['end'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=UTC)
                                duration = end_time - start_time
                                duration_hours = duration.total_seconds() / 3600
                                total_hours += duration_hours
                                positions_worked.add(callsign)
                    
                    # Check if controller is inactive
                    if total_hours < 3:
                        inactive_controllers.append({
                            'first_name': first_name,
                            'last_name': last_name,
                            'cid': cid,
                            'email': controller['email'],
                            'hours': round(total_hours, 2),
                            'rating': controller['rating_short'],
                            'positions': sorted(list(positions_worked))
                        })
                    
                    processed_count += 1
                    print(f"Processed {processed_count}/{total_controllers}: {first_name} {last_name} (CID: {cid}) - {round(total_hours, 2)} ZJX hours")
                
                else:
                    print(f"Error fetching data for {first_name} {last_name} (CID: {cid}) - Status code: {stats_response.status_code if stats_response else 'No response'}")
                    
            except Exception as e:
                print(f"Error processing controller {first_name} {last_name} (CID: {cid}): {str(e)}")
                continue
        
        # Add a longer pause between batches
        if i + batch_size < len(active_controllers):
            pause = 30  # 30 second pause between batches
            print(f"\nPausing for {pause} seconds before next batch...")
            sleep(pause)
    
    return inactive_controllers, obs_controllers, processed_count
