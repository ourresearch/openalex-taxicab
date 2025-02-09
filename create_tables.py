import boto3


def create_harvested_tables():
    dynamodb = boto3.client('dynamodb', region_name='us-east-1')

    # GSI definitions for tables
    gsi_definitions = [
        {
            'IndexName': 'by_normalized_doi',
            'KeySchema': [
                {'AttributeName': 'normalized_doi', 'KeyType': 'HASH'}
            ],
            'Projection': {
                'ProjectionType': 'ALL'
            }
        },
        {
            'IndexName': 'by_native_id',
            'KeySchema': [
                {'AttributeName': 'native_id', 'KeyType': 'HASH'},
                {'AttributeName': 'native_id_namespace', 'KeyType': 'RANGE'}
            ],
            'Projection': {
                'ProjectionType': 'ALL'
            }
        },
        {
            'IndexName': 'by_created_date',
            'KeySchema': [
                {'AttributeName': 'created_date', 'KeyType': 'HASH'}
            ],
            'Projection': {
                'ProjectionType': 'ALL'
            }
        },
        {
            'IndexName': 'by_url',
            'KeySchema': [
                {'AttributeName': 'url', 'KeyType': 'HASH'}
            ],
            'Projection': {
                'ProjectionType': 'ALL'
            }
        }
    ]

    # create HTML table
    dynamodb.create_table(
        TableName='harvested-html',
        KeySchema=[
            {'AttributeName': 'id', 'KeyType': 'HASH'}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'id', 'AttributeType': 'S'},
            {'AttributeName': 'normalized_doi', 'AttributeType': 'S'},
            {'AttributeName': 'native_id', 'AttributeType': 'S'},
            {'AttributeName': 'native_id_namespace', 'AttributeType': 'S'},
            {'AttributeName': 'created_date', 'AttributeType': 'S'},
            {'AttributeName': 'url', 'AttributeType': 'S'}
        ],
        GlobalSecondaryIndexes=gsi_definitions,
        BillingMode='PAY_PER_REQUEST'
    )

    # create grobid table with same structure
    dynamodb.create_table(
        TableName='grobid-xml',
        KeySchema=[
            {'AttributeName': 'id', 'KeyType': 'HASH'}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'id', 'AttributeType': 'S'},
            {'AttributeName': 'normalized_doi', 'AttributeType': 'S'},
            {'AttributeName': 'native_id', 'AttributeType': 'S'},
            {'AttributeName': 'native_id_namespace', 'AttributeType': 'S'},
            {'AttributeName': 'created_date', 'AttributeType': 'S'},
            {'AttributeName': 'url', 'AttributeType': 'S'}
        ],
        GlobalSecondaryIndexes=gsi_definitions,
        BillingMode='PAY_PER_REQUEST'
    )


if __name__ == '__main__':
    create_harvested_tables()
    print("Tables created")