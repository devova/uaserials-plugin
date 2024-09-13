import json
from fastapi import FastAPI
from importlib.metadata import version

from urllib.parse import unquote

from uaseries.mappings import TOP_NAV_TO_CATALOG
from uaseries.scrape import fetch, parse_top_nav, pase_catalog_items


app = FastAPI()


@app.get("/manifest.json")
def manifest():
    main = fetch("")
    top_nav = parse_top_nav(main)
    return {
        "id": "org.stremio.uaserialsPro",
        "version": version("uaseries"),
        "name": "uaseries.pro адаптер",
        "description": "Піратимо піратський контент, має працювати",
        "types": ["movie", "series"],
        "catalogs": [
            {
                "id": item.ref,
                "type": TOP_NAV_TO_CATALOG[item.title],
                "name": f"uaserials: {item.title}",
            }
            for item in top_nav
            if item.title in TOP_NAV_TO_CATALOG
        ],
        "resources": [
            "catalog",
            # The meta call will be invoked only for series with ID starting with hpy
            {"name": "meta", "types": ["movie", "series"], "idPrefixes": ["uaseries"]},
            {
                "name": "stream",
                "types": ["movie", "series"],
                "idPrefixes": ["uaseries"],
            },
        ],
    }


@app.get("/catalog/{stream_type}/{ref}.json")
def list_collection(stream_type: str, ref: str):
    ref = unquote(ref)
    catalog = fetch(ref)
    items = pase_catalog_items(catalog)
    streams = [
        {
            "id": f"uaseries:{item.id}",
            "type": stream_type,
            "name": item.title,
            "poster": item.poster,
            "genres": item.labels,
            "available": True,
        }
        for item in items
    ]
    print(json.dumps(streams, indent=2))
    return {"metas": streams}


@app.get("/meta/{stream_type}/{ref}.json")
def get_item(stream_type: str, ref: str):
    ref = unquote(ref)
    catalog = fetch(ref)
    items = pase_catalog_items(catalog)
    streams = [
        {
            "id": f"uaseries:{item.id}",
            "type": stream_type,
            "name": item.title,
            "poster": item.poster,
            "genres": item.labels,
            "available": True,
        }
        for item in items
    ]
    print(json.dumps(streams, indent=2))
    return {"metas": streams}
