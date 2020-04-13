import tweepy
import logging
import os

logger = logging.getLogger()

def create_api():
    '''
    Creating api object via tokens
    '''
    ACCESS_TOKEN = ""
    ACCESS_TOKEN_SECRET = ""
    CONSUMER_KEY = ""
    CONSUMER_SECRET = ""

    # Authenticate to Twitter
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

    # Create API object
    api = tweepy.API(auth, wait_on_rate_limit=True,
    wait_on_rate_limit_notify=True)    
    try:
        api.verify_credentials()
    except Exception as e:
        logger.error("Error creating API", exc_info=True)
        raise e
    logger.info("API created")
    return api