from aiohttp import ClientSession, web
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from aiohttp_proxy import ProxyConnector
from json5 import loads
from re import findall

import asyncio


def _create_session(proxy: str = None):
    connector = None if not proxy else ProxyConnector.from_url(proxy)

    return ClientSession(
        connector=connector,
        headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/109.0"
        },
    )


async def find_all_queries(session: ClientSession, path: str):
    response = await session.get(path)
    html = await response.text()

    queries = findall(r"e\.exports=({queryId:.*?)},", html)

    return list(map(loads, queries))


async def parse_scripts(session: ClientSession):
    response = await session.get("https://twitter.com/")
    html = await response.text()

    main_script = findall(r"client\-web(-legacy)?\/main\.(.*?)\.js", html)[0]

    scripts = findall(
        r"<script.*?>window\.__SCRIPTS_LOADED__ = {};.*\"\.\"\+({.*?})", html
    )[0]

    scripts = loads(scripts)

    scripts["main"] = main_script[1]
    scripts["legacy"] = bool(main_script[0])

    return scripts


async def parse_query_ids(proxy: str = None) -> dict:
    async with _create_session(proxy) as session:
        scripts = await parse_scripts(session)

        api = scripts.get("api") + "a.js"
        main = scripts.get("main")
        legacy = scripts.get("legacy")

        main = f"https://abs.twimg.com/responsive-web/{('client-web/' if not legacy else 'client-web-legacy/') + 'main.' + main}.js"
        api = f"https://abs.twimg.com/responsive-web/client-web/api.{api}"

        queries = await find_all_queries(session, main) + await find_all_queries(
            session, api
        )

        return queries
