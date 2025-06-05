import json
import boto3
import os 
import uuid
import re
from botocore.exceptions import ClientError

def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def check_email_exists(table, email):
    try:
        response = table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key('email').eq(email)
        )
        
        return len(response.get('Items', [])) > 0
    except ClientError as e:
        if 'ValidationException' in str(e):
            response = table.scan(
                FilterExpression=boto3.dynamodb.conditions.Attr('email').eq(email)
            )
            return len(response.get('Items', [])) > 0
        raise e

def handler(event, context):
    print(event)
    
    if event.get('httpMethod') != 'POST':
        return {
            'statusCode': 405,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'message': 'Method Not Allowed. Only POST method is accepted.'
            })
        }
    
    try:
        if not event.get('body'):
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'message': 'Missing request body'
                })
            }
        
        body = json.loads(event['body'])
        
        if not body.get('name'):
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'message': 'Name is required'
                })
            }
        
        if not body.get('email'):
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'message': 'Email is required'
                })
            }
        
        if not is_valid_email(body['email']):
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'message': 'Invalid email format'
                })
            }
        
        table_name = os.environ['STORAGE_USERS_NAME']
        dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')
        table = dynamodb.Table(table_name)
        
        try:
            if check_email_exists(table, body['email']):
                return {
                    'statusCode': 409,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({
                        'message': 'Email already exists'
                    })
                }
        except Exception as e:
            print(f"Error checking existing email: {str(e)}")
        
        user_id = str(uuid.uuid4())
        table.put_item(
            Item={
                'id': user_id,
                'name': body['name'],
                'email': body['email'],
            }
        )
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'message': 'User created successfully',
                'user': {
                    'id': user_id,
                    'name': body['name'],
                    'email': body['email']
                }
            })
        }
        
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'message': 'Invalid JSON in request body'
            })
        }
    except ClientError as e:
        print(f"DynamoDB error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'message': 'Database operation failed',
                'error': str(e)
            })
        }
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'message': 'Internal server error',
                'error': str(e)
            })
        }
