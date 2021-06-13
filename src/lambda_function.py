# see https://qiita.com/katafuchix/items/7fa1323265b6a448cdbc

import json
import os
import logging
import traceback
from requests_oauthlib import OAuth1Session
from secret import get_secret
from twitter import tweet_image, tweet_text

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


def tweet_wakatime(twitter: OAuth1Session, img_url: str):
    res_media = tweet_image(twitter, img_url)
    if res_media.status_code != 200:
        exit()
    media_id = json.loads(res_media.text)['media_id']
    return media_id


def lambda_handler(event, context):
    logger.debug(event)

    try:
        secret = get_secret(
            secret_name="Twitter/tweet-wakatime-stats",
            region_name="ap-northeast-1")

        logger.info(secret)

        twitter = OAuth1Session(
            secret['api_key'],
            secret['api_secret_key'],
            secret['access_token'],
            secret['access_token_secret']
        )

        media_id = tweet_wakatime(
            twitter=twitter,
            img_url=os.environ.get('LANGUAGES_URL'))

        media_id2 = tweet_wakatime(
            twitter=twitter,
            img_url=os.environ.get('CODING_ACTIVITY_URL'))

        message = "今週の開発時間 measured by #wakatime tweeted by #aws_lambda"
        res_text = tweet_text(
            twitter=twitter,
            message=message,
            media_ids=f'{media_id},{media_id2}')

        return {
            'statusCode': res_text.status_code
        }

    except Exception as e:
        logger.error(traceback.format_exc())
        raise e
