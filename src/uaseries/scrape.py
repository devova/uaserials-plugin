from typing import Optional
from httpx import Client, codes
from rocksdict import Rdict
from bs4 import BeautifulSoup
from urllib.parse import quote

from .models import CatalogItem, MetaItem, MetaItemPreview

BASE_URL = "https://uaserials.pro/"

cache = Rdict("cache/web")
client = Client(base_url=BASE_URL, follow_redirects=True)


def fetch(url: str) -> Optional[BeautifulSoup]:
    if url not in cache:
        response = client.get(url)
        if codes.is_success(response.status_code):
            cache[url] = response.content
        else:
            return None
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


def pase_item(soup: BeautifulSoup) -> MetaItem:
    article = soup.find(id="dle-content").find("article")
    title = article.find("h1").find("span", class_="oname_ua").text
    poster = article.find("img").get("src")
    imdb_rating = article.find("a", attrs={"data-text": "imdb"}).text
    infos = [
        el.text.split(":", 1)
        for el in article.find("ul", class_="short-list").find_all("li")
    ]
    infos = {el[0]: el[1] for el in infos if len(el) == 2}

    genres = infos.get("Жанр", "").strip().split(", ")
    directors = infos.get("Режисер", "").strip().split(", ")
    cast = infos.get("Актори", "").strip().split(", ")

    description = article.find("div", class_="full-text").text
    return MetaItem(
        title=title,
        title_original="",
        description=description,
        poster=poster,
        imdb_rating=imdb_rating,
        genres=genres,
        directors=directors,
        cast=cast,
        ref="",
        labels=[],
    )
