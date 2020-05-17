import asyncio
import aiohttp  # pip install aiohttp aiodns


async def get(
    session: aiohttp.ClientSession,
    post_id: str,
    **kwargs
) -> dict:
    url = f"https://jsonplaceholder.typicode.com/posts/{post_id}/"
    print(f"Requesting {url}")
    resp = await session.request('GET', url=url, **kwargs)
    # Note that this may raise an exception for non-2xx responses
    # You can either handle that here, or pass the exception through
    data = await resp.json()
    print(f"Received data for {url}")
    return post_id, data['title']


async def batch(post_ids):
    # Asynchronous context manager.  Prefer this rather
    # than using a different session for each GET request
    async with aiohttp.ClientSession() as session:
        tasks = []
        for pid in post_ids:
            tasks.append(get(session=session, post_id=pid))
        # asyncio.gather() will wait on the entire task set to be
        # completed.  If you want to process results greedily as they come in,
        # loop over asyncio.as_completed()
        htmls = await asyncio.gather(*tasks, return_exceptions=True)
        return htmls


async def process():
    results = await batch([1, 2, 3, 4, 5])
    return sorted(results, key=lambda r: r[0])


if __name__ == '__main__':
    # Either take colors from stdin or make some default here
    asyncio.run(process())  # Python 3.7+


# async def main(colors, **kwargs):
#     # Asynchronous context manager.  Prefer this rather
#     # than using a different session for each GET request
#     async with aiohttp.ClientSession() as session:
#         tasks = []
#         for c in colors:
#             tasks.append(get(session=session, color=c, **kwargs))
#         # asyncio.gather() will wait on the entire task set to be
#         # completed.  If you want to process results greedily as they come in,
#         # loop over asyncio.as_completed()
#         htmls = await asyncio.gather(*tasks, return_exceptions=True)
#         return htmls


# if __name__ == '__main__':
#     colors = ['red', 'blue', 'green']  # ...
#     # Either take colors from stdin or make some default here
#     asyncio.run(main(colors))  # Python 3.7+
