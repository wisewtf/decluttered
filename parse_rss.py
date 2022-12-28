import feedparser
import datetime
from telethon import TelegramClient
from telethon import events
import mysql.connector
from bs4 import BeautifulSoup
import re
import time
import os

DB_HOST = os.environ['DB_HOST']
DB_USER = os.environ['DB_USER']
DB_PASS = os.environ['DB_PASS']
DB_NAME = os.environ['DB_NAME']

# Parse the RSS feed
feed = feedparser.parse('link')

articles = []

def rss_grab_and_run():
    # Loop through each item in the feed
    for article in feed.entries:
        # Extract content
        title = article.title
        description = article.content
        link = article.link
        updated_time = article.updated

        for content in description:
            article_content = content.value
            converted_content = BeautifulSoup(article_content, features="html.parser")
            fixed_content = re.sub("\n{1,}", "\n", converted_content.get_text())

        articles_dict = {
            'title': title,
            'description': fixed_content,
            'link': link,
            'updated_time': updated_time,
            }
        articles.append(articles_dict)

    last_feed_item = articles[0]
    last_feed_item_date = last_feed_item['updated_time']

    with open('last_date.txt', 'r') as rd:
        old_date = rd.read()
        if not old_date:
            old_date = datetime.datetime.min.replace(tzinfo=datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S %Z')

    new_articles = [x for x in articles if x['updated_time'] > old_date]

    with open('last_date.txt', 'w') as d:
        d.write(str(last_feed_item_date))

    database_connection = mysql.connector.connect(user={DB_USER}, password={DB_PASS}, host={DB_HOST}, database={DB_NAME})

    database_cursor = database_connection.cursor()

    database_query = "INSERT INTO articles (article_title,article_description,article_link,article_date) values (%s, %s, %s, %s)"

    for new_article in new_articles:
        query_values = (new_article['title'], new_article['description'], new_article['link'], new_article['updated_time'])
        database_cursor.execute(database_query,query_values)
        database_connection.commit()

    database_cursor.close()
    database_connection.close()

while True:
    rss_grab_and_run()
    time.sleep(900)
