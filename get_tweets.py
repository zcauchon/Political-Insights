import boto3, requests, os, json
from botocore.exceptions import ClientError
from datetime import datetime, timedelta

def request_recent_crime_data(event, context):
    '''
    Will call API endpoint to get tweets
    '''
    userID = event['userID']
    date = datetime.now() - timedelta(days=7)
    strDate = datetime.strftime(date, '%Y-%m-%d')
    expansions = 'author_id,geo.place_id'
    tweet_fields = 'id,created_at,text,author_id,geo,public_metrics'
    user_fields = 'name,username'
    media_fields = 'url&place.fields=full_name,country'
    auth_token = os.environ['stoken']
    next_token = event.get('next_token', None)
    url = f'https://api.twitter.com/2/users/{userID}/tweets?max_results=100&start_time={strDate}T00:00:00.000Z'
    if next_token:
        url = f'{url}&pagination_token={next_token}'
    endpoint = f'{url}&expansions={expansions}&tweet.fields={tweet_fields}&user.fields={user_fields}&media.fields={media_fields}'
    response = requests.get(endpoint, headers={f'Authorization': f'Bearer {auth_token}'})
    if response.ok:
        data = response.json()
        tweets = data.get('data', None)
        meta = data.get('meta', None)
        meta['userID'] = userID
        if tweets:
        #data has been returned, save into s3
            print(meta)
            s3_client = boto3.client('s3')
            try:
                s3response = s3_client.put_object(
                    Body=json.dumps(tweets),
                    Bucket='zcauchon-political-insights',
                    Key=f'input/recent_source_data_{userID}_{strDate}.json',
                )
            except ClientError as e:
                print(e)
        return meta
    return None