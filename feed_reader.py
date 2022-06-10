import traceback

import psycopg2
from psycopg2.extras import DictCursor

from conf import DB_HOST, DB_USER, DB_PASS, DB_NAME, BUZZ_WORDS
from feed_parser import get_parser

db = psycopg2.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASS,
    dbname=DB_NAME
)


def check_exists(guid):
    with db.cursor(cursor_factory=DictCursor) as cursor:
        cursor.execute("""
            SELECT count(*) AS row_count
            FROM feed_item
            WHERE guid = %s
            """, (guid,))
        row = cursor.fetchone()
        return row["row_count"] != 0


def check_buzz_words(text):
    s = text.lower()
    return any(word in s for word in BUZZ_WORDS)


def update_feed(feed):
    parser = get_parser(feed["feed_type"])
    feed_data = parser.parse(feed["url"])
    if len(feed_data) == 0:
        return

    with db.cursor(cursor_factory=DictCursor) as cursor:
        for item in feed_data:
            if check_exists(item.guid):
                continue
            if check_buzz_words(item.title):
                continue
            cursor.execute("""
                INSERT INTO feed_item (feed_id, guid, link, title, description, pub_date)
                VALUES (%s, %s, %s, %s, %s, %s)
                """, (feed["feed_id"], item.guid, item.link, item.title, item.description, item.pub_date))
        db.commit()


def update_all_feeds():
    with db.cursor(cursor_factory=DictCursor) as cursor:
        cursor.execute("""
            SELECT f.feed_id, f.url, t.code AS feed_type
            FROM feed f
            INNER JOIN feed_type t ON t.feed_type_id = f.feed_type_id
            """)
        feeds = cursor.fetchall()

        for feed in feeds:
            try:
                print(feed)
                update_feed(feed)
            except Exception:
                traceback.print_exc()


update_all_feeds()

db.close()
