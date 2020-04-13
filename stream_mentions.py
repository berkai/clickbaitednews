import tweepy
import logging
import twitterCredential
import time
from newsplease import NewsPlease
from newspaper import Article
from newspaper import fulltext
import requests
from lxml import html
import requests
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
# text to image 
import numpy as np
import textwrap
import PIL
import PIL.Image as Image
import PIL.ImageDraw as ImageDraw
import PIL.ImageFont as ImageFont
import logging
from urllib3 import exceptions
import socket
from config import create_api
import logging

logging.basicConfig(
    filename='bot.log',
    level=logging.DEBUG,
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger()

mentions_hash_table = {}

filepath = './hash_table.txt'

with open(filepath, 'r') as fp:
    for line in fp:
        print(line.strip())
        mentions_hash_table[str(line.strip())] = str(line.strip())
    
    line = fp.readline().strip()
    print(line)
    while line:    
        line = fp.readline().strip()
        print(line)
        mentions_hash_table[str(line)] = str(line)

def text_to_image(text):
    '''
    If text is too long this function put text in a image.
    '''
    font_fname = 'arial.ttf'
    font_size = 18
    font = ImageFont.truetype(font_fname, font_size)
    h, w = 1080, 1920
    bg_colour = (21,32,43)
    bg_image = np.dot(np.ones((h,w,3), dtype='uint8'), np.diag(np.asarray((bg_colour), dtype='uint8')))
    image0 = Image.fromarray(bg_image)

    draw = ImageDraw.Draw(image0)
    margin = offset = 40
    for line in textwrap.wrap(text, width=160):
        draw.text((margin, offset), line, font=font, fill="#DBDBDB")
        offset += font.getsize(line)[1]
    # draw.text((30, 15), haber, font=font, fill='rgb(0, 0, 0)')
    # image0.save('hello_world.jpg')
    return image0

def get_text_hard_way(url):
    '''
    If newsplease cant get the news and returns "None" this function getting
    the url's all text.
    '''
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read()

    soup = BeautifulSoup(webpage, "lxml")

    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.decompose()    # rip it out

    # get text
    text = soup.get_text()

    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)
    return text

def check_mentions(api):
    '''
    getting mentions and reply them.
    '''
    mention_list = api.mentions_timeline() # get the mentions
    filepath = '/home/berkay/Desktop/projects/twitter/hash_table.txt'
    logger.info("Getting mentions")

    for mention in mention_list:
        time_of_mention = str(mention.created_at)
        if not (time_of_mention in mentions_hash_table): # if not previously replied
            parent_tweet_id = mention.in_reply_to_status_id_str
            if parent_tweet_id is None: # If this tweet is not a mention
                print(parent_tweet_id, "geldi")
                mentions_hash_table[time_of_mention] = time_of_mention
                with open(filepath, 'a') as fp:
                    fp.write('\n')
                    fp.write(time_of_mention)
                status = '@' + mention.user.screen_name + ' Please mention me below of the news tweet.'
                api.update_status(status, mention.id)
                continue
            try:
                status = api.get_status(parent_tweet_id, tweet_mode="extended")
                logger.info("parent tweet id: %s", parent_tweet_id)
                logger.info("tweet text: %s", status.full_text)
                logger.info("status urls in tweet: %s", status.entities['urls'][0]['url'])

                if "@clickbaitednews" in mention.text:
                    logger.info(f"Answering to {mention.user.name}")
                    mentions_hash_table[time_of_mention] = time_of_mention
                    with open(filepath, 'a') as fp:
                        fp.write('\n')
                        fp.write(time_of_mention)
                    parent_tweet_id = mention.in_reply_to_status_id_str
                    status = api.get_status(parent_tweet_id, tweet_mode="extended")

                    news_url = status.entities['urls'][0]['url']
                    article = NewsPlease.from_url(news_url)
                    news_text = article.text
                    logger.info("text of tweet: %s", news_text)

                    beginning_of_tweet = 0
                    end_of_tweet = 255-13
                    keyword = 255-13
                    try:
                        print(news_text)
                        if len(news_text) <= 1000:
                            tweet_sayisi = len(news_text) // keyword
                            LAST_TWEET = len(news_text) % keyword
                            for i in range(tweet_sayisi+1):
                                tweet_no = str(i+1) 
                                tweet_no = tweet_no + '/'
                                tweet_no = tweet_no + str(tweet_sayisi+1)
                                news_text_tweet = news_text[beginning_of_tweet:end_of_tweet]
                                beginning_of_tweet = end_of_tweet
                                end_of_tweet = end_of_tweet + keyword
                                if end_of_tweet >= len(news_text):
                                    end_of_tweet = len(news_text)
                                    beginning_of_tweet = end_of_tweet - LAST_TWEET
                                    status = '@' + mention.user.screen_name + ' ' + news_text_tweet + ' ' + tweet_no
                                    api.update_status(status, mention.id)
                                    news_text_tweet = []
                                else:
                                    status = '@' + mention.user.screen_name + ' ' + news_text_tweet + ' ' + tweet_no
                                    api.update_status(status, mention.id)
                                    news_text_tweet = []
                        else:
                            image = text_to_image(news_text)
                            image.save('news_pic.jpg')
                            status = '@' + mention.user.screen_name + ' This text is too long we are adding text to the image. ' + news_url
                            api.update_with_media('news_pic.jpg', status=status)
                    except TypeError:
                        text = get_text_hard_way(news_url)
                        if len(text) >= 600:
                            image = text_to_image(text)
                            image.save('news_pic.jpg')
                            status = '@' + mention.user.screen_name + ' This text is too long we are adding text to the image. ' + news_url
                            api.update_with_media('news_pic.jpg', status=status)
                        else:
                            tweet_sayisi = len(news_text) // keyword
                            LAST_TWEET = len(news_text) % keyword
                            for i in range(tweet_sayisi+1):
                                tweet_no = str(i+1) 
                                tweet_no = tweet_no + '/'
                                tweet_no = tweet_no + str(tweet_sayisi+1)
                                news_text_tweet = news_text[beginning_of_tweet:end_of_tweet]
                                beginning_of_tweet = end_of_tweet
                                end_of_tweet = end_of_tweet + keyword
                                if end_of_tweet >= len(news_text):
                                    end_of_tweet = len(news_text)
                                    beginning_of_tweet = end_of_tweet - LAST_TWEET
                                    status = '@' + mention.user.screen_name + ' ' + news_text_tweet + ' ' + tweet_no
                                    api.update_status(status, mention.id)
                                    news_text_tweet = []
                                else:
                                    status = '@' + mention.user.screen_name + ' ' + news_text_tweet + ' ' + tweet_no
                                    api.update_status(status, mention.id)
                                    news_text_tweet = []
            except tweepy.TweepError as e:
                logger.error("Tweepy error", exc_info=True) 
            
def main():
    api = create_api()
    # since_id = 1
    while True:
        check_mentions(api)
        logger.info("Waiting...")
        time.sleep(15)

if __name__ == "__main__":
    main()
