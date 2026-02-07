import json
import boto3
import hashlib
import hmac
import base64
import time
import os
from decimal import Decimal

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
teams_table = dynamodb.Table('aais-hackathon-teams')
panelists_table = dynamodb.Table('aais-hackathon-panelists')
scores_table = dynamodb.Table('aais-hackathon-scores')
use_cases_table = dynamodb.Table('aais-hackathon-use-cases')
judging_criteria_table = dynamodb.Table('aais-hackathon-judging-criteria')

# JWT Secret (in production, use AWS Secrets Manager)
JWT_SECRET = os.environ.get('JWT_SECRET', 'aais-hackathon-2026-secret-key')

def decimal_to_num(obj):
    """Convert Decimal to int/float for JSON serialization"""
    if isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    elif isinstance(obj, dict):
        return {k: decimal_to_num(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [decimal_to_num(i) for i in obj]
    return obj

def create_jwt(payload):
    """Create a simple JWT token"""
    header = base64.urlsafe_b64encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode()).decode().rstrip('=')
    payload['exp'] = int(time.time()) + 86400  # 24 hour expiry
    payload_encoded = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip('=')
    signature = hmac.new(JWT_SECRET.encode(), f"{header}.{payload_encoded}".encode(), hashlib.sha256).digest()
    signature_encoded = base64.urlsafe_b64encode(signature).decode().rstrip('=')
    return f"{header}.{payload_encoded}.{signature_encoded}"

def verify_jwt(token):
    """Verify and decode JWT token"""
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return None
        header, payload_encoded, signature = parts
        
        # Verify signature
        expected_sig = hmac.new(JWT_SECRET.encode(), f"{header}.{payload_encoded}".encode(), hashlib.sha256).digest()
        expected_sig_encoded = base64.urlsafe_b64encode(expected_sig).decode().rstrip('=')
        
        if not hmac.compare_digest(signature, expected_sig_encoded):
            return None
        
        # Decode payload
        padding = 4 - len(payload_encoded) % 4
        if padding != 4:
            payload_encoded += '=' * padding
        payload = json.loads(base64.urlsafe_b64decode(payload_encoded))
        
        # Check expiry
        if payload.get('exp', 0) < time.time():
            return None
            
        return payload
    except Exception as e:
        print(f"JWT verification error: {e}")
        return None

def get_auth_context(event):
    """Extract and verify auth from request headers"""
    headers = event.get('headers', {}) or {}
    auth_header = headers.get('Authorization') or headers.get('authorization', '')
    
    if not auth_header.startswith('Bearer '):
        return None
    
    token = auth_header[7:]
    return verify_jwt(token)

def response(status_code, body):
    """Create API Gateway response with CORS headers"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
        },
        'body': json.dumps(decimal_to_num(body))
    }

def lambda_handler(event, context):
    """Main Lambda handler"""
    print(f"Event: {json.dumps(event)}")
    
    http_method = event.get('httpMethod', '')
    path = event.get('path', '')
    
    # Handle CORS preflight
    if http_method == 'OPTIONS':
        return response(200, {'message': 'OK'})
    
    # Parse body
    body = {}
    if event.get('body'):
        try:
            body = json.loads(event['body'])
        except:
            pass
    
    # Route handling
    try:
        # Auth routes (no auth required)
        if path == '/auth/team-login' and http_method == 'POST':
            return team_login(body)
        
        if path == '/auth/panelist-login' and http_method == 'POST':
            return panelist_login(body)
        
        if path == '/auth/team-register' and http_method == 'POST':
            return team_register(body)
        
        # Public use case routes (no auth required)
        if path == '/use-cases' and http_method == 'GET':
            return get_all_use_cases()
        
        if path.startswith('/use-cases/') and http_method == 'GET':
            use_case_id = path.split('/')[-1]
            return get_use_case(use_case_id)
        
        # Public judging criteria route (no auth required)
        if path == '/judging-criteria' and http_method == 'GET':
            return get_judging_criteria()
        
        # Public team card route (no auth required, limited data for sharing)
        if path.startswith('/team-card/') and http_method == 'GET':
            team_id = path.split('/')[-1]
            return get_public_team_card(team_id)
        
        # Protected routes - require auth
        auth = get_auth_context(event)
        if not auth:
            return response(401, {'error': 'Unauthorized - Invalid or missing token'})
        
        # Team routes
        if path == '/team/me' and http_method == 'GET':
            if auth.get('type') != 'team':
                return response(403, {'error': 'Forbidden - Team access only'})
            return get_team(auth['team_id'])
        
        if path == '/team/me' and http_method == 'PUT':
            if auth.get('type') != 'team':
                return response(403, {'error': 'Forbidden - Team access only'})
            return update_team(auth['team_id'], body)
        
        # Panelist routes
        if path == '/teams' and http_method == 'GET':
            if auth.get('type') != 'panelist':
                return response(403, {'error': 'Forbidden - Panelist access only'})
            return get_all_teams()
        
        if path.startswith('/teams/') and http_method == 'GET':
            if auth.get('type') != 'panelist':
                return response(403, {'error': 'Forbidden - Panelist access only'})
            team_id = path.split('/')[-1]
            return get_team(team_id)
        
        if path == '/scores' and http_method == 'POST':
            if auth.get('type') != 'panelist':
                return response(403, {'error': 'Forbidden - Panelist access only'})
            return submit_score(auth['panelist_id'], body)
        
        if path == '/scores' and http_method == 'GET':
            return get_all_scores()
        
        if path.startswith('/scores/') and http_method == 'GET':
            team_id = path.split('/')[-1]
            return get_team_scores(team_id)
        
        # Admin-only use case management routes
        if path == '/use-cases' and http_method == 'POST':
            if auth.get('type') != 'panelist' or not auth.get('is_admin'):
                return response(403, {'error': 'Forbidden - Admin access only'})
            return create_use_case(body)
        
        if path.startswith('/use-cases/') and http_method == 'PUT':
            if auth.get('type') != 'panelist' or not auth.get('is_admin'):
                return response(403, {'error': 'Forbidden - Admin access only'})
            use_case_id = path.split('/')[-1]
            return update_use_case(use_case_id, body)
        
        if path.startswith('/use-cases/') and http_method == 'DELETE':
            if auth.get('type') != 'panelist' or not auth.get('is_admin'):
                return response(403, {'error': 'Forbidden - Admin access only'})
            use_case_id = path.split('/')[-1]
            return delete_use_case(use_case_id)
        
        # Admin-only judging criteria management
        if path == '/judging-criteria' and http_method == 'PUT':
            if auth.get('type') != 'panelist' or not auth.get('is_admin'):
                return response(403, {'error': 'Forbidden - Admin access only'})
            return update_judging_criteria(body)
        
        # Admin-only team management
        if path.startswith('/teams/') and path.endswith('/reset-password') and http_method == 'PUT':
            if auth.get('type') != 'panelist' or not auth.get('is_admin'):
                return response(403, {'error': 'Forbidden - Admin access only'})
            team_id = path.split('/')[2]
            return admin_reset_team_password(team_id, body)
        
        if path.startswith('/teams/') and http_method == 'DELETE':
            if auth.get('type') != 'panelist' or not auth.get('is_admin'):
                return response(403, {'error': 'Forbidden - Admin access only'})
            team_id = path.split('/')[-1]
            return admin_delete_team(team_id)
        
        # Admin-only panelist management
        if path == '/panelists' and http_method == 'GET':
            if auth.get('type') != 'panelist' or not auth.get('is_admin'):
                return response(403, {'error': 'Forbidden - Admin access only'})
            return get_all_panelists()
        
        if path == '/panelists' and http_method == 'POST':
            if auth.get('type') != 'panelist' or not auth.get('is_admin'):
                return response(403, {'error': 'Forbidden - Admin access only'})
            return create_panelist(body)
        
        if path.startswith('/panelists/') and path.endswith('/reset-password') and http_method == 'PUT':
            if auth.get('type') != 'panelist' or not auth.get('is_admin'):
                return response(403, {'error': 'Forbidden - Admin access only'})
            panelist_id = path.split('/')[2]
            return admin_reset_panelist_password(panelist_id, body)
        
        if path.startswith('/panelists/') and path.endswith('/toggle-admin') and http_method == 'PUT':
            if auth.get('type') != 'panelist' or not auth.get('is_admin'):
                return response(403, {'error': 'Forbidden - Admin access only'})
            panelist_id = path.split('/')[2]
            return toggle_panelist_admin(panelist_id, auth['panelist_id'])
        
        return response(404, {'error': 'Not found'})
        
    except Exception as e:
        print(f"Error: {e}")
        return response(500, {'error': str(e)})

# Auth handlers
def team_login(body):
    """Authenticate a team"""
    team_id = body.get('team_id', '').lower().strip()
    password = body.get('password', '')
    
    if not team_id or not password:
        return response(400, {'error': 'team_id and password required'})
    
    try:
        result = teams_table.get_item(Key={'team_id': team_id})
        team = result.get('Item')
        
        if not team or team.get('password') != password:
            return response(401, {'error': 'Invalid credentials'})
        
        token = create_jwt({
            'type': 'team',
            'team_id': team_id,
            'team_name': team.get('team_name', team_id)
        })
        
        return response(200, {
            'token': token,
            'team_id': team_id,
            'team_name': team.get('team_name', team_id)
        })
    except Exception as e:
        return response(500, {'error': str(e)})

def team_register(body):
    """Register a new team"""
    team_id = body.get('team_id', '').lower().strip().replace(' ', '-')
    team_name = body.get('team_name', '')
    password = body.get('password', '')
    
    if not team_id or not password or not team_name:
        return response(400, {'error': 'team_id, team_name, and password required'})
    
    if len(password) < 6:
        return response(400, {'error': 'Password must be at least 6 characters'})
    
    try:
        # Check if team exists
        result = teams_table.get_item(Key={'team_id': team_id})
        if result.get('Item'):
            return response(409, {'error': 'Team ID already exists'})
        
        # Create team
        teams_table.put_item(Item={
            'team_id': team_id,
            'team_name': team_name,
            'password': password,
            'use_case': 0,
            'use_case_name': '',
            'solution_description': '',
            'services_used': [],
            'members': [],
            'created_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            'updated_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        })
        
        token = create_jwt({
            'type': 'team',
            'team_id': team_id,
            'team_name': team_name
        })
        
        return response(201, {
            'message': 'Team registered successfully',
            'token': token,
            'team_id': team_id,
            'team_name': team_name
        })
    except Exception as e:
        return response(500, {'error': str(e)})

def panelist_login(body):
    """Authenticate a panelist"""
    panelist_id = body.get('panelist_id', '').lower().strip().replace(' ', '-')
    password = body.get('password', '')
    
    if not panelist_id or not password:
        return response(400, {'error': 'panelist_id and password required'})
    
    try:
        result = panelists_table.get_item(Key={'panelist_id': panelist_id})
        panelist = result.get('Item')
        
        if not panelist or panelist.get('password') != password:
            return response(401, {'error': 'Invalid credentials'})
        
        is_admin = panelist.get('is_admin', False)
        
        token = create_jwt({
            'type': 'panelist',
            'panelist_id': panelist_id,
            'name': panelist.get('name', panelist_id),
            'is_admin': is_admin
        })
        
        return response(200, {
            'token': token,
            'panelist_id': panelist_id,
            'name': panelist.get('name', panelist_id),
            'is_admin': is_admin
        })
    except Exception as e:
        return response(500, {'error': str(e)})

# Public team card handler (no auth required)
def get_public_team_card(team_id):
    """Get limited team info for public sharing (no auth required)"""
    try:
        result = teams_table.get_item(Key={'team_id': team_id})
        team = result.get('Item')
        
        if not team:
            return response(404, {'error': 'Team not found'})
        
        # Return only public-safe fields for sharing
        public_data = {
            'team_id': team.get('team_id'),
            'team_name': team.get('team_name'),
            'use_case': team.get('use_case'),
            'use_case_name': team.get('use_case_name'),
            'members': [
                {'name': m.get('name'), 'role': m.get('role')}
                for m in (team.get('members') or [])
            ]  # Exclude email for privacy
        }
        
        return response(200, public_data)
    except Exception as e:
        return response(500, {'error': str(e)})

# Team handlers
def get_team(team_id):
    """Get team details"""
    try:
        result = teams_table.get_item(Key={'team_id': team_id})
        team = result.get('Item')
        
        if not team:
            return response(404, {'error': 'Team not found'})
        
        # Remove password from response
        team.pop('password', None)
        return response(200, team)
    except Exception as e:
        return response(500, {'error': str(e)})

def update_team(team_id, body):
    """Update team details"""
    try:
        update_expr = []
        expr_values = {}
        expr_names = {}
        
        # Allowed fields to update
        if 'team_name' in body:
            update_expr.append('#tn = :tn')
            expr_values[':tn'] = body['team_name']
            expr_names['#tn'] = 'team_name'
        
        if 'use_case' in body:
            use_case = int(body['use_case'])
            # Get use case name from database
            uc_result = use_cases_table.get_item(Key={'use_case_id': use_case})
            uc_item = uc_result.get('Item')
            if not uc_item or not uc_item.get('active', True):
                return response(400, {'error': 'Invalid use_case'})
            update_expr.append('use_case = :uc')
            update_expr.append('use_case_name = :ucn')
            expr_values[':uc'] = use_case
            expr_values[':ucn'] = uc_item.get('name', '')
        
        if 'solution_description' in body:
            update_expr.append('solution_description = :sd')
            expr_values[':sd'] = body['solution_description']
        
        if 'services_used' in body:
            update_expr.append('services_used = :su')
            expr_values[':su'] = body['services_used']
        
        if 'members' in body:
            update_expr.append('members = :m')
            expr_values[':m'] = body['members']
        
        if not update_expr:
            return response(400, {'error': 'No valid fields to update'})
        
        update_expr.append('updated_at = :ua')
        expr_values[':ua'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        
        update_params = {
            'Key': {'team_id': team_id},
            'UpdateExpression': 'SET ' + ', '.join(update_expr),
            'ExpressionAttributeValues': expr_values,
            'ReturnValues': 'ALL_NEW'
        }
        
        if expr_names:
            update_params['ExpressionAttributeNames'] = expr_names
        
        result = teams_table.update_item(**update_params)
        team = result.get('Attributes', {})
        team.pop('password', None)
        
        return response(200, team)
    except Exception as e:
        return response(500, {'error': str(e)})

def get_all_teams():
    """Get all teams (for panelists)"""
    try:
        result = teams_table.scan()
        teams = result.get('Items', [])
        
        # Remove passwords
        for team in teams:
            team.pop('password', None)
        
        return response(200, {'teams': teams})
    except Exception as e:
        return response(500, {'error': str(e)})

# Score handlers
def submit_score(panelist_id, body):
    """Submit or update a score"""
    team_id = body.get('team_id', '')
    
    if not team_id:
        return response(400, {'error': 'team_id required'})
    
    # Validate scores
    required_fields = ['presentation', 'innovation', 'functionality', 'aws_well_architected']
    for field in required_fields:
        if field not in body:
            return response(400, {'error': f'{field} score required'})
        score = body[field]
        if not isinstance(score, (int, float)) or score < 1 or score > 5:
            return response(400, {'error': f'{field} must be between 1 and 5'})
    
    try:
        # Verify team exists
        team_result = teams_table.get_item(Key={'team_id': team_id})
        if not team_result.get('Item'):
            return response(404, {'error': 'Team not found'})
        
        total = sum(body[f] for f in required_fields)
        
        scores_table.put_item(Item={
            'team_id': team_id,
            'panelist_id': panelist_id,
            'presentation': Decimal(str(body['presentation'])),
            'innovation': Decimal(str(body['innovation'])),
            'functionality': Decimal(str(body['functionality'])),
            'aws_well_architected': Decimal(str(body['aws_well_architected'])),
            'total': Decimal(str(total)),
            'comments': body.get('comments', ''),
            'submitted_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        })
        
        return response(200, {
            'message': 'Score submitted successfully',
            'team_id': team_id,
            'panelist_id': panelist_id,
            'total': total
        })
    except Exception as e:
        return response(500, {'error': str(e)})

def get_all_scores():
    """Get all scores with aggregations"""
    try:
        result = scores_table.scan()
        scores = result.get('Items', [])
        
        # Aggregate by team
        team_scores = {}
        for score in scores:
            team_id = score['team_id']
            if team_id not in team_scores:
                team_scores[team_id] = {
                    'team_id': team_id,
                    'scores': [],
                    'avg_presentation': 0,
                    'avg_innovation': 0,
                    'avg_functionality': 0,
                    'avg_aws_well_architected': 0,
                    'avg_total': 0,
                    'num_scores': 0
                }
            team_scores[team_id]['scores'].append(score)
            team_scores[team_id]['num_scores'] += 1
        
        # Calculate averages
        for team_id, data in team_scores.items():
            n = data['num_scores']
            if n > 0:
                data['avg_presentation'] = sum(s['presentation'] for s in data['scores']) / n
                data['avg_innovation'] = sum(s['innovation'] for s in data['scores']) / n
                data['avg_functionality'] = sum(s['functionality'] for s in data['scores']) / n
                data['avg_aws_well_architected'] = sum(s['aws_well_architected'] for s in data['scores']) / n
                data['avg_total'] = sum(s['total'] for s in data['scores']) / n
        
        # Sort by average total
        leaderboard = sorted(team_scores.values(), key=lambda x: x['avg_total'], reverse=True)
        
        return response(200, {'leaderboard': leaderboard, 'all_scores': scores})
    except Exception as e:
        return response(500, {'error': str(e)})

def get_team_scores(team_id):
    """Get scores for a specific team"""
    try:
        result = scores_table.query(
            KeyConditionExpression='team_id = :tid',
            ExpressionAttributeValues={':tid': team_id}
        )
        scores = result.get('Items', [])
        
        return response(200, {'team_id': team_id, 'scores': scores})
    except Exception as e:
        return response(500, {'error': str(e)})

# Use Case handlers
def get_all_use_cases():
    """Get all active use cases (public)"""
    try:
        result = use_cases_table.scan()
        use_cases = result.get('Items', [])
        
        # Filter to active only and sort by sort_order
        active_use_cases = [uc for uc in use_cases if uc.get('active', True)]
        active_use_cases.sort(key=lambda x: x.get('sort_order', 999))
        
        return response(200, {'use_cases': active_use_cases})
    except Exception as e:
        return response(500, {'error': str(e)})

def get_use_case(use_case_id):
    """Get a single use case by ID (public)"""
    try:
        result = use_cases_table.get_item(Key={'use_case_id': int(use_case_id)})
        use_case = result.get('Item')
        
        if not use_case:
            return response(404, {'error': 'Use case not found'})
        
        return response(200, use_case)
    except ValueError:
        return response(400, {'error': 'Invalid use_case_id'})
    except Exception as e:
        return response(500, {'error': str(e)})

def create_use_case(body):
    """Create a new use case (admin only)"""
    required_fields = ['name', 'archetype', 'quote', 'background', 'reality', 'persona', 'tension', 'focus', 'challenges', 'values']
    
    for field in required_fields:
        if field not in body:
            return response(400, {'error': f'{field} is required'})
    
    try:
        # Get next use_case_id
        result = use_cases_table.scan(ProjectionExpression='use_case_id')
        existing_ids = [item['use_case_id'] for item in result.get('Items', [])]
        next_id = max(existing_ids) + 1 if existing_ids else 1
        
        use_case = {
            'use_case_id': next_id,
            'name': body['name'],
            'archetype': body['archetype'],
            'quote': body['quote'],
            'background': body['background'],
            'reality': body['reality'],
            'persona': body['persona'],
            'tension': body['tension'],
            'focus': body['focus'],
            'challenges': body['challenges'],
            'values': body['values'],
            'closing': body.get('closing', ''),
            'ascii_logo': body.get('ascii_logo', ''),
            'loading_message': body.get('loading_message', ''),
            'sort_order': body.get('sort_order', next_id),
            'active': body.get('active', True),
            'created_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            'updated_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        }
        
        use_cases_table.put_item(Item=use_case)
        
        return response(201, {'message': 'Use case created', 'use_case': use_case})
    except Exception as e:
        return response(500, {'error': str(e)})

def update_use_case(use_case_id, body):
    """Update an existing use case (admin only)"""
    try:
        use_case_id = int(use_case_id)
        
        # Check if exists
        result = use_cases_table.get_item(Key={'use_case_id': use_case_id})
        if not result.get('Item'):
            return response(404, {'error': 'Use case not found'})
        
        update_expr = []
        expr_values = {}
        expr_names = {}
        
        # Map fields to safe attribute names (many are DynamoDB reserved words)
        field_mappings = {
            'name': '#fname',
            'archetype': '#farchetype',
            'quote': '#fquote',
            'background': '#fbackground',
            'reality': '#freality',
            'persona': '#fpersona',
            'tension': '#ftension',
            'focus': '#ffocus',
            'challenges': '#fchallenges',
            'values': '#fvalues',
            'closing': '#fclosing',
            'ascii_logo': '#fascii_logo',
            'loading_message': '#floading_message',
            'sort_order': '#fsort_order',
            'active': '#factive'
        }
        
        for field, attr_name in field_mappings.items():
            if field in body:
                value_key = f':v{field}'
                update_expr.append(f'{attr_name} = {value_key}')
                expr_values[value_key] = body[field]
                expr_names[attr_name] = field
        
        if not update_expr:
            return response(400, {'error': 'No valid fields to update'})
        
        update_expr.append('#fupdated_at = :vupdated_at')
        expr_values[':vupdated_at'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        expr_names['#fupdated_at'] = 'updated_at'
        
        update_params = {
            'Key': {'use_case_id': use_case_id},
            'UpdateExpression': 'SET ' + ', '.join(update_expr),
            'ExpressionAttributeValues': expr_values,
            'ExpressionAttributeNames': expr_names,
            'ReturnValues': 'ALL_NEW'
        }
        
        result = use_cases_table.update_item(**update_params)
        use_case = result.get('Attributes', {})
        
        return response(200, use_case)
    except ValueError:
        return response(400, {'error': 'Invalid use_case_id'})
    except Exception as e:
        return response(500, {'error': str(e)})

def delete_use_case(use_case_id):
    """Delete (deactivate) a use case (admin only)"""
    try:
        use_case_id = int(use_case_id)
        
        # Check if exists
        result = use_cases_table.get_item(Key={'use_case_id': use_case_id})
        if not result.get('Item'):
            return response(404, {'error': 'Use case not found'})
        
        # Soft delete - just set active to false
        use_cases_table.update_item(
            Key={'use_case_id': use_case_id},
            UpdateExpression='SET active = :a, updated_at = :ua',
            ExpressionAttributeValues={
                ':a': False,
                ':ua': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
            }
        )
        
        return response(200, {'message': 'Use case deactivated'})
    except ValueError:
        return response(400, {'error': 'Invalid use_case_id'})
    except Exception as e:
        return response(500, {'error': str(e)})

# Judging Criteria handlers
def get_judging_criteria():
    """Get the judging criteria (public)"""
    try:
        result = judging_criteria_table.get_item(Key={'criteria_id': 'main'})
        criteria = result.get('Item')
        
        if not criteria:
            return response(404, {'error': 'Judging criteria not found'})
        
        return response(200, criteria)
    except Exception as e:
        return response(500, {'error': str(e)})

def update_judging_criteria(body):
    """Update judging criteria (admin only)"""
    try:
        update_expr = []
        expr_values = {}
        
        allowed_fields = ['intro', 'categories', 'required_tool', 'expected_services', 'closing']
        
        for field in allowed_fields:
            if field in body:
                update_expr.append(f'{field} = :{field[:3]}')
                expr_values[f':{field[:3]}'] = body[field]
        
        if not update_expr:
            return response(400, {'error': 'No valid fields to update'})
        
        update_expr.append('updated_at = :ua')
        expr_values[':ua'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        
        result = judging_criteria_table.update_item(
            Key={'criteria_id': 'main'},
            UpdateExpression='SET ' + ', '.join(update_expr),
            ExpressionAttributeValues=expr_values,
            ReturnValues='ALL_NEW'
        )
        
        return response(200, result.get('Attributes', {}))
    except Exception as e:
        return response(500, {'error': str(e)})

# Admin team management handlers
def admin_reset_team_password(team_id, body):
    """Reset a team's password (admin only)"""
    new_password = body.get('new_password', '')
    
    if not new_password or len(new_password) < 6:
        return response(400, {'error': 'new_password required (minimum 6 characters)'})
    
    try:
        # Check if team exists
        result = teams_table.get_item(Key={'team_id': team_id})
        if not result.get('Item'):
            return response(404, {'error': 'Team not found'})
        
        # Update password
        teams_table.update_item(
            Key={'team_id': team_id},
            UpdateExpression='SET password = :pw, updated_at = :ua',
            ExpressionAttributeValues={
                ':pw': new_password,
                ':ua': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
            }
        )
        
        return response(200, {'message': f'Password reset successfully for team {team_id}'})
    except Exception as e:
        return response(500, {'error': str(e)})

def admin_delete_team(team_id):
    """Delete a team and their scores (admin only)"""
    try:
        # Check if team exists
        result = teams_table.get_item(Key={'team_id': team_id})
        if not result.get('Item'):
            return response(404, {'error': 'Team not found'})
        
        team_name = result['Item'].get('team_name', team_id)
        
        # Delete all scores for this team
        scores_result = scores_table.query(
            KeyConditionExpression='team_id = :tid',
            ExpressionAttributeValues={':tid': team_id}
        )
        
        for score in scores_result.get('Items', []):
            scores_table.delete_item(
                Key={
                    'team_id': team_id,
                    'panelist_id': score['panelist_id']
                }
            )
        
        # Delete the team
        teams_table.delete_item(Key={'team_id': team_id})
        
        return response(200, {
            'message': f'Team "{team_name}" and all associated scores deleted successfully'
        })
    except Exception as e:
        return response(500, {'error': str(e)})

def admin_reset_panelist_password(panelist_id, body):
    """Reset a panelist's password (admin only)"""
    new_password = body.get('new_password', '')
    
    if not new_password or len(new_password) < 6:
        return response(400, {'error': 'new_password required (minimum 6 characters)'})
    
    try:
        # Check if panelist exists
        result = panelists_table.get_item(Key={'panelist_id': panelist_id})
        if not result.get('Item'):
            return response(404, {'error': 'Panelist not found'})
        
        # Update password
        panelists_table.update_item(
            Key={'panelist_id': panelist_id},
            UpdateExpression='SET password = :pw, updated_at = :ua',
            ExpressionAttributeValues={
                ':pw': new_password,
                ':ua': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
            }
        )
        
        return response(200, {'message': f'Password reset successfully for panelist {panelist_id}'})
    except Exception as e:
        return response(500, {'error': str(e)})

def get_all_panelists():
    """Get all panelists (admin only)"""
    try:
        result = panelists_table.scan()
        panelists = result.get('Items', [])
        
        # Remove passwords from response
        for panelist in panelists:
            panelist.pop('password', None)
        
        return response(200, {'panelists': panelists})
    except Exception as e:
        return response(500, {'error': str(e)})

def create_panelist(body):
    """Create a new panelist (admin only)"""
    panelist_id = body.get('panelist_id', '').lower().strip().replace(' ', '-')
    name = body.get('name', '')
    password = body.get('password', '')
    is_admin = body.get('is_admin', False)
    
    if not panelist_id or not password or not name:
        return response(400, {'error': 'panelist_id, name, and password required'})
    
    if len(password) < 6:
        return response(400, {'error': 'Password must be at least 6 characters'})
    
    try:
        # Check if panelist exists
        result = panelists_table.get_item(Key={'panelist_id': panelist_id})
        if result.get('Item'):
            return response(409, {'error': 'Panelist ID already exists'})
        
        # Create panelist
        panelists_table.put_item(Item={
            'panelist_id': panelist_id,
            'name': name,
            'password': password,
            'is_admin': is_admin,
            'created_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            'updated_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        })
        
        return response(201, {
            'message': 'Panelist created successfully',
            'panelist_id': panelist_id,
            'name': name,
            'is_admin': is_admin
        })
    except Exception as e:
        return response(500, {'error': str(e)})

def toggle_panelist_admin(panelist_id, current_admin_id):
    """Toggle admin status for a panelist (admin only)"""
    # Prevent admin from demoting themselves
    if panelist_id == current_admin_id:
        return response(400, {'error': 'Cannot modify your own admin status'})
    
    try:
        # Check if panelist exists
        result = panelists_table.get_item(Key={'panelist_id': panelist_id})
        if not result.get('Item'):
            return response(404, {'error': 'Panelist not found'})
        
        current_status = result['Item'].get('is_admin', False)
        new_status = not current_status
        
        # Update admin status
        panelists_table.update_item(
            Key={'panelist_id': panelist_id},
            UpdateExpression='SET is_admin = :ia, updated_at = :ua',
            ExpressionAttributeValues={
                ':ia': new_status,
                ':ua': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
            }
        )
        
        status_text = 'promoted to admin' if new_status else 'demoted from admin'
        return response(200, {
            'message': f'Panelist {panelist_id} {status_text}',
            'panelist_id': panelist_id,
            'is_admin': new_status
        })
    except Exception as e:
        return response(500, {'error': str(e)})
