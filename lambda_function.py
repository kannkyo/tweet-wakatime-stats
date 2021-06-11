# see https://qiita.com/katafuchix/items/7fa1323265b6a448cdbc

import json
import os
import boto3
import base64
import logging
import traceback
from requests_oauthlib import OAuth1Session
import urllib.request

secret_name = "Twitter/tweet-wakatime-stats"
region_name = "ap-northeast-1"

level = os.environ.get('LOG_LEVEL', 'DEBUG')

def logger_level():
    if level == 'CRITICAL':
        return 50
    elif level == 'ERROR':
        return 40
    elif level == 'WARNING':
        return 30
    elif level == 'INFO':
        return 20
    elif level == 'DEBUG':
        return 10
    else:
        return 0

logger = logging.getLogger()
logger.setLevel(logger_level())

def get_secret():

    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        raise e
    else:
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
        else:
            secret = base64.b64decode(
                get_secret_value_response['SecretBinary'])

    return secret


def tweet_image(twitter, img_url):
    url_media = "https://upload.twitter.com/1.1/media/upload.json"

    response = urllib.request.urlopen(img_url)
    data = response.read()
    files = {"media": data}
    res_media = twitter.post(url_media, files=files)
    logger.info(res_media)
    
    return res_media


def tweet_text(twitter, message, media_ids):
    url_text = "https://api.twitter.com/1.1/statuses/update.json"

    params = {'status': message, "media_ids": media_ids}
    res_text = twitter.post(url_text, params=params)
    logger.info(res_text)
    
    return res_text


def lambda_handler(event, context):
    logger.debug(event)

    try:
        secret = json.loads(get_secret())
        logger.info(secret)

        twitter = OAuth1Session(
            secret['api_key'],
            secret['api_secret_key'],
            secret['access_token'],
            secret['access_token_secret']
        )

        img_url = "https://wakatime.com/share/@kannkyo/75b1a5a9-8b0d-47cf-a77b-2bddebd017f3.png"
        res_media = tweet_image(twitter, img_url)
        if res_media.status_code != 200:
            exit()
        media_id = json.loads(res_media.text)['media_id']

        img_url = "https://wakatime.com/share/@kannkyo/5884f410-5034-40c5-a463-b8c1b7a04289.png"
        res_media = tweet_image(twitter, img_url)
        if res_media.status_code != 200:
            exit()
        media_id2 = json.loads(res_media.text)['media_id']

        message = "今週の開発時間 measured by #wakatime tweeted by #aws_lambda"
        res_text = tweet_text(twitter, message, f'{media_id},{media_id2}')

        return {
            'statusCode': res_text.status_code
        }

    except Exception as e:
        logger.error(traceback.format_exc())
        raise e
