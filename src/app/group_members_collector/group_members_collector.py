import asyncio
import aiohttp
import requests as requests
from app.util.request_maker import request_maker as rm
import app.util.settings as settings


class GroupMembersCollector:
    group_members_count: int
    group_id = settings.group_id
    member_clusters = asyncio.Queue()

    def set_group_members_count(self):
        self.group_members_count = \
            requests.get(rm('groups.getById',
                            'group_id=' + self.group_id + '&fields=name,members_count')).json()[
                "response"][0]["members_count"]

    async def get_group_members(self, session, offset):
        while offset < self.group_members_count:
            async with session.get(rm('groups.getMembers', 'group_id=' + self.group_id + '&count=1000&offset='
                                                           + str(offset))) as response:
                data = await response.json()
                try:
                    await self.member_clusters.put(data['response']['items'])
                    offset += 1000
                except KeyError:
                    await asyncio.sleep(0.1)

    async def collect_members(self):
        self.set_group_members_count()
        async with aiohttp.ClientSession() as session:
            await asyncio.gather(self.get_group_members(session, 0))

