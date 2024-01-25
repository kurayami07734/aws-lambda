import json
import boto3
import os
import datetime
import random
import string
from botocore.exceptions import ClientError

from typing import Any, Dict, Optional

URL_TABLE_NAME = os.getenv('URL_TABLE_NAME')
BASE_URL = os.getenv('BASE_URL')

dynamodb = boto3.resource('dynamodb')
url_table = dynamodb.Table(URL_TABLE_NAME)

def get_item(short_id: str) -> Optional[Dict]:
    try:
        response = url_table.get_item(
                Key={
                    'PK': short_id,
                    'SK': short_id,
                }
        )
    except ClientError as e:
        print(f'Error: {e.response}')
        return {
                "statusCode": 500,
                "body": e.response['Error']['Message']
        }
    item = response.get('Item', {})
    return item

def get_unique_short_id(size=7, max_iter=10) -> str:
    short_id = ''
    curr_iter = 0
    while (short_id == '' or get_item(short_id) and curr_iter < max_iter):
        short_id = ''.join(random.choices(string.ascii_lowercase, k=size))
        curr_iter += 1

    return short_id

def create_short_url(event: Dict[str, Any], context) -> Dict[str, Any]:
    request_body = json.loads(event['body'])
    long_url = request_body['longURL']
    short_id = get_unique_short_id()
    short_url = f'{BASE_URL}/short/{short_id}'

