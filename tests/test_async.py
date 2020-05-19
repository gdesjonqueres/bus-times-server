import asyncio
import aiohttp  # $ pip install aiohttp


async def fetch(session, key, item, base_url='http://google.com'):
    async with session.get(base_url + item) as response:
        return key, await response.text()


async def main():
    d = {'a': '', 'b': '', 'c': ''}
    async with aiohttp.ClientSession() as session:
        # tasks = map(functools.partial(fetch, session), *zip(*d.items()))
        tasks = [fetch(session, *item) for item in d.items()]
        responses = await asyncio.gather(*tasks)
    print(dict(responses))

asyncio.get_event_loop().run_until_complete(main())
