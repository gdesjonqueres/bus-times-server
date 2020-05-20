import asyncio
import aiohttp

from tools.http_request import HTTPRequest


class AsyncHTTPRequests:
    """Helper class for handling multiple async requests

    """

    def __init__(self, timeout=10):
        self.timeout = aiohttp.ClientTimeout(total=timeout)

    async def _fetch(self, session, key, request: HTTPRequest):
        async with session.get(
                request.url,
                headers=request.headers,
                params=request.parameters) as response:
            return (key,
                    await response.json() if request.is_accept_json()
                    else await response.text())

    async def _batch(self, requests_iterator):
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            tasks = [self._fetch(session, *item)
                     for item in requests_iterator]
            responses = await asyncio.gather(*tasks)
            return responses

    async def fetch(self, requests):
        """Returns a handle on the pool of async requests

        """
        if isinstance(requests, dict):
            iterator = requests.items()
        elif isinstance(requests, list):
            iterator = enumerate(requests)
        else:
            raise ValueError(
                '"requests" argument should be either list or dict')
        return await self._batch(iterator)

    def run(self, requests):
        """Performs provided requests asynchronously

        """
        return asyncio.run(self.fetch(requests))
