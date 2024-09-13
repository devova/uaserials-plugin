from httpx import Client
from rocksdict import Rdict
from bs4 import BeautifulSoup
from urllib.parse import quote

from .models import CatalogItem, MetaItemPreview

BASE_URL = "https://uaserials.pro/"

cache = Rdict("cache/web")
client = Client(base_url=BASE_URL, follow_redirects=True)


def fetch(url: str) -> BeautifulSoup:
    if url not in cache:
        response = client.get(url)
        cache[url] = response.content
    return BeautifulSoup(cache[url], "html.parser")


def parse_top_nav(soup: BeautifulSoup) -> list[CatalogItem]:
    nav_menu = soup.find("ul", class_="menunav_top")
    top_nav_links = nav_menu.find_all("li")

    items = []
    for link in top_nav_links:
        href = link.a.get("href").strip("/")
        title = link.a.text.strip()
        items.append(CatalogItem(title=title, ref=quote(href)))
    return items


def pase_catalog_items(soup: BeautifulSoup) -> list[MetaItemPreview]:
    content_root = soup.find(id="dle-content")
    catalog_items = content_root.find_all(class_="short-item")
    items = []
    for item in catalog_items:
        a = item.a
        href = a.get("href").replace(BASE_URL, "")
        title = a.img.get("alt")
        labels = [
            div.span.text.strip() for div in a.find_all("div", class_="short-label")
        ]
        oname = item.find("div", class_="th-title-oname").text
        img = a.img.get("data-src")
        items.append(
            MetaItemPreview(
                title=title,
                title_original=oname,
                poster=img,
                ref=quote(href),
                labels=labels,
            )
        )
    return items
