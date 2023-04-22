from . import parse_query_ids
from asyncio import run
from json import dumps
from sys import argv


async def main():
    proxy = argv[-1]
    queries = await parse_query_ids(proxy)
    queries = dumps(queries)

    open("queries.json", "w+").write(queries)


if __name__ == "__main__":
    run(main())
