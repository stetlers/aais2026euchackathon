import json
import boto3
import os

sns = boto3.client('sns', region_name='us-east-1')
SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN', 'arn:aws:sns:us-east-1:031421429609:aais-hackathon-notifications')

USE_CASES = {
    1: "Vault-Tec Corporation [Secrecy-Driven]",
    2: "RobCo Industries [Speed-Driven]",
    3: "General Atomics International [Assurance-Driven]",
    4: "West Tek Research [Preservation-Driven]",
    5: "Poseidon Energy [Resilience-Driven]",
    6: "Nuka-Cola Corporation [Flexibility-Driven]"
}

def lambda_handler(event, context):
    """Process DynamoDB Stream events and send SNS notifications"""
    
    for record in event.get('Records', []):
        event_name = record.get('eventName')
        
        if event_name == 'INSERT':
            handle_new_team(record)
        elif event_name == 'MODIFY':
            handle_team_update(record)
    
    return {'statusCode': 200}

def handle_new_team(record):
    """Handle new team registration"""
    new_image = record.get('dynamodb', {}).get('NewImage', {})
    
    team_id = new_image.get('team_id', {}).get('S', 'Unknown')
    team_name = new_image.get('team_name', {}).get('S', team_id)
    created_at = new_image.get('created_at', {}).get('S', '')
    
    subject = f"🎮 New Team Registered: {team_name}"
    message = f"""
═══════════════════════════════════════════════════
    AAIS 2026 EUC HACKATHON - NEW TEAM REGISTRATION
═══════════════════════════════════════════════════

A new team has joined the hackathon!

Team Name: {team_name}
Team ID: {team_id}
Registered: {created_at}

The team has not yet selected a use case.

───────────────────────────────────────────────────
View all teams at: https://aais2026euchackathon.com/login.html
═══════════════════════════════════════════════════
"""
    
    send_notification(subject, message)

def handle_team_update(record):
    """Handle team updates"""
    old_image = record.get('dynamodb', {}).get('OldImage', {})
    new_image = record.get('dynamodb', {}).get('NewImage', {})
    
    team_id = new_image.get('team_id', {}).get('S', 'Unknown')
    team_name = new_image.get('team_name', {}).get('S', team_id)
    
    changes = []
    
    # Check use case change
    old_use_case = int(old_image.get('use_case', {}).get('N', 0))
    new_use_case = int(new_image.get('use_case', {}).get('N', 0))
    if old_use_case != new_use_case and new_use_case > 0:
        use_case_name = USE_CASES.get(new_use_case, f"Use Case {new_use_case}")
        changes.append(f"• Selected Use Case: {use_case_name}")
    
    # Check members change
    old_members = old_image.get('members', {}).get('L', [])
    new_members = new_image.get('members', {}).get('L', [])
    if len(new_members) != len(old_members):
        member_names = [m.get('M', {}).get('name', {}).get('S', '') for m in new_members if m.get('M', {}).get('name', {}).get('S')]
        if member_names:
            changes.append(f"• Team Members ({len(member_names)}): {', '.join(member_names)}")
    
    # Check solution description change
    old_solution = old_image.get('solution_description', {}).get('S', '')
    new_solution = new_image.get('solution_description', {}).get('S', '')
    if new_solution and new_solution != old_solution:
        preview = new_solution[:150] + '...' if len(new_solution) > 150 else new_solution
        changes.append(f"• Solution Description Updated:\n    \"{preview}\"")
    
    # Check services change
    old_services = old_image.get('services_used', {}).get('L', [])
    new_services = new_image.get('services_used', {}).get('L', [])
    if len(new_services) != len(old_services):
        service_names = [s.get('S', '') for s in new_services if s.get('S')]
        if service_names:
            changes.append(f"• AWS Services ({len(service_names)}): {', '.join(service_names)}")
    
    if not changes:
        return  # No significant changes to report
    
    subject = f"📝 Team Update: {team_name}"
    message = f"""
═══════════════════════════════════════════════════
    AAIS 2026 EUC HACKATHON - TEAM UPDATE
═══════════════════════════════════════════════════

Team "{team_name}" has updated their submission:

{chr(10).join(changes)}

───────────────────────────────────────────────────
View all teams at: https://aais2026euchackathon.com/login.html
═══════════════════════════════════════════════════
"""
    
    send_notification(subject, message)

def send_notification(subject, message):
    """Send SNS notification"""
    try:
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject=subject[:100],  # SNS subject limit
            Message=message
        )
        print(f"Notification sent: {subject}")
    except Exception as e:
        print(f"Error sending notification: {e}")
