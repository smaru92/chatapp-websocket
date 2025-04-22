#utils/return_result.py

def success():
    return {
        'statusCode': 200
    }

def bad_request():
    {
        'statusCode': 400,
        'body': 'Invalid route key'
    }