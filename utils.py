import pathlib
import json
from collections import namedtuple
import feedparser
from opengraph_py3 import OpenGraph
from collections import namedtuple
from datetime import datetime
from time import mktime
from cachetools import cached, TTLCache
import pyaml
from slugify import slugify
from random import sample
import urllib


class FirefoxOpenGraph(OpenGraph):
    def fetch(self, url):
        """
        Overwrite the fetch method to set a user agent.
        """
        req = urllib.request.Request(
            url,
            data=None,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:129.0) Gecko/20100101 Firefox/129.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
            },
        )
        raw = urllib.request.urlopen(req)
        html = raw.read()
        return self.parser(html)


class Article(
    namedtuple("Article", "date,title,url,summary,feedfrom,entry,feedinfo,categories")
):
    # TODO: extract categories and/or tags from the entry
    # "og:site_name"
    # meta name="author"
    og = None

    def get_og(self):
        if not self.og:
            self.og = FirefoxOpenGraph(url=self.url, scrape=True)
        return self.og

    @property
    def image(self):
        try:
            og = self.get_og()
            return og["image"]
        except Exception as e:
            print(f"Could not retrieve opengraph for {self.url}: {e}")
            return None

    @property
    def slug(self):
        return slugify(self.title)

    def to_yaml(self):
        d = self._asdict()
        d["date"] = self.date.isoformat()
        d["link_url"] = d["url"]
        d["author"] = self.entry.author
        d["image"] = self.image
        if type([]) == type(self.image):
            d["image"] = self.image[0]
        unwanted = ["feedinfo", "entry", "url"]
        for u in unwanted:
            del d[u]
        return pyaml.dump(d).strip()


Feed = namedtuple("Feed", "url, weight, categories, fragments", defaults=[None])


def remove_continue(elem):
    description = elem.description
    description = description.split("</p>")[0]
    description = description.replace("<p>", "")
    REMOVE_CONTINUE = f'<a href="{elem.link}">Continue reading...</a>'
    return description.replace(REMOVE_CONTINUE, "")


@cached(cache=TTLCache(maxsize=1024, ttl=3600))
def get_feed_content(feeds, do_sampling=True, size=100):
    articles = []
    for f in feeds:
        print(f"fetching from {f.url}")
        factor = f.weight
        if do_sampling:
            # If we want to sample, get more from the feed to have variation
            factor = 10 * factor
        try:
            feed = feedparser.parse(f.url)
            tmp_articles = []
            for e in feed.entries[:factor]:
                categories = []
                categories += f.categories
                if f.fragments:
                    path = urllib.parse.urlparse(e.link).path.split("/")
                    for p in f.fragments:
                        categories.append(path[p])
                tmp_articles.append(
                    Article(
                        datetime.fromtimestamp(mktime(e.published_parsed)),
                        e.title,
                        e.link,
                        remove_continue(e),
                        feed.feed.title,
                        e,
                        f,
                        categories,
                    )
                )
                if len(tmp_articles) > f.weight:
                    articles += sample(tmp_articles, f.weight)
                else:
                    articles += tmp_articles
        except Exception as e:
            print(f"Could not retrieve {{f.url}}: {e}")
    return articles


def load_feeds(source="feeds.json"):
    file = pathlib.Path(source)
    for d in json.load(file.open()):
        yield Feed(*d)
