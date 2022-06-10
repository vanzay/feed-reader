from abc import ABC, abstractmethod
from datetime import datetime
from hashlib import sha256

import requests
from lxml import etree


class FeedItem:

    def __init__(self, guid, link, author, title, description, pub_date):
        self.guid = guid
        self.link = link
        self.author = author
        self.title = title
        self.description = description
        self.pub_date = pub_date


class FeedParser(ABC):

    @staticmethod
    def _get_node_item_text(node, item_name):
        # use local-name() to ignore namespaces
        item = node.xpath(f".//*[local-name() = '{item_name}']")
        return item[0].text if len(item) > 0 else None

    @abstractmethod
    def _get_posts(self, tree):
        pass

    @abstractmethod
    def _get_guid(self, post):
        pass

    @abstractmethod
    def _get_link(self, post):
        pass

    @abstractmethod
    def _get_author(self, post):
        pass

    @abstractmethod
    def _get_title(self, post):
        pass

    @abstractmethod
    def _get_description(self, post):
        pass

    @abstractmethod
    def _get_date_time(self, post):
        pass

    def parse(self, url):
        result = []

        # to avoid 403 error (some resources block bots) set User-Agent header
        response = requests.get(url, headers={"User-Agent": "Feed Browser"})
        tree = etree.fromstring(response.content)
        posts = self._get_posts(tree)
        for post in posts:
            link = self._get_link(post)
            guid = self._get_guid(post)
            if not guid:
                guid = sha256(link.encode("utf-8")).hexdigest()
            author = self._get_author(post)
            title = self._get_title(post)
            description = self._get_description(post)
            date_time = self._get_date_time(post)
            if not date_time:
                date_time = datetime.today()
            pub_date = date_time.strftime("%Y-%m-%d %H:%M:%S")
            result.append(FeedItem(guid, link, author, title, description, pub_date))

        return result


class RssParser(FeedParser):

    def _get_posts(self, tree):
        return tree.xpath("//rss/channel/item")

    def _get_guid(self, post):
        return self._get_node_item_text(post, "guid")

    def _get_link(self, post):
        return self._get_node_item_text(post, "link")

    def _get_author(self, post):
        return self._get_node_item_text(post, "author")

    def _get_title(self, post):
        return self._get_node_item_text(post, "title")

    def _get_description(self, post):
        return self._get_node_item_text(post, "description")

    def _get_date_time(self, post):
        pub_date = self._get_node_item_text(post, "pubDate")
        if pub_date:
            try:
                return datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %z")
            except Exception:
                return datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %Z")
        return None


class AtomParser(FeedParser):

    def _get_posts(self, tree):
        return tree.xpath("//*[local-name() = 'entry']")

    def _get_guid(self, post):
        return self._get_node_item_text(post, "id")

    def _get_link(self, post):
        link_items = post.xpath(f".//*[local-name() = 'link']")
        alternate_links = list(filter(lambda item: not item.get("rel") or item.get("rel") == "alternate", link_items))
        return alternate_links[0].get("href") if len(alternate_links) > 0 else None

    def _get_author(self, post):
        return None

    def _get_title(self, post):
        return self._get_node_item_text(post, "title")

    def _get_description(self, post):
        return self._get_node_item_text(post, "content")

    def _get_date_time(self, post):
        published = self._get_node_item_text(post, "published")
        return datetime.strptime(published, "%Y-%m-%dT%H:%M:%S.%f%z")


def get_parser(feed_type):
    if feed_type == "RSS":
        return RssParser()
    elif feed_type == "ATOM":
        return AtomParser()
    else:
        raise ValueError(feed_type)
