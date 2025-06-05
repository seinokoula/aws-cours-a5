import json
import boto3
import os
import decimal
from datetime import datetime, timezone
import uuid

dynamodb = boto3.resource('dynamodb', region_name="eu-west-1")
s3 = boto3.client('s3', region_name="eu-west-1")

table_name = os.environ.get('STORAGE_CRYPTOPRICEALEX_NAME', 'cryptoPriceAlex-alex')
EXPORT_BUCKET_NAME = "awscoursa56611b4ddc1304dddaecf86e82a8a91468fdac-alex"

bucket_name = EXPORT_BUCKET_NAME

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

def handler(event, context):
    try:
        table = dynamodb.Table(table_name)

        response = table.scan()
        items = response.get("Items", [])

        items.sort(key=lambda x: x.get("email", "").lower()) 

        now = datetime.now(timezone.utc)
        timestamp = now.strftime("%Y-%m-%dT%H-%M-%S")
        filename = f"exports/crypto_{timestamp}.json"

        json_data = json.dumps(items, cls=DecimalEncoder, indent=2)
    
        s3.put_object(
            Bucket=bucket_name,
            Key=filename,
            Body=json_data,
            ContentType="application/json"
        )

        presigned_url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': filename},
            ExpiresIn=3600
        )

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Export effectué avec succès.",
                "download_url": presigned_url
            })
        }

    except Exception as e:
        print("Erreur :", str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Erreur lors de l'export des données."})
        }