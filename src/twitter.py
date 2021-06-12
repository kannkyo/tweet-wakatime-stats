import urllib.request
from requests_oauthlib import OAuth1Session
import logging

logger = logging.getLogger()


def tweet_image(twitter: OAuth1Session, img_url: str):
    url_media = "https://upload.twitter.com/1.1/media/upload.json"

    response = urllib.request.urlopen(img_url)
    data = response.read()
    files = {"media": data}
    res_media = twitter.post(url_media, files=files)
    logger.info(res_media)

    return res_media


def tweet_text(twitter: OAuth1Session, message: str, media_ids: str):
    url_text = "https://api.twitter.com/1.1/statuses/update.json"

    params = {'status': message, "media_ids": media_ids}
    res_text = twitter.post(url_text, params=params)
    logger.info(res_text)

    return res_text
