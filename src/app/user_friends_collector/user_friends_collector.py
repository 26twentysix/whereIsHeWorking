import asyncio

import aiohttp

from src.app.util.request_maker import request_maker as rm
from src.app.util.settings import allowed_faculties as allowed_faculties


class UserFriendsCollector:
    group_member_clusters = asyncio.Queue()
    users_set = set()
    user_clusters = asyncio.Queue()

    def set_group_member_clusters(self, gmc):
        self.group_member_clusters = gmc

    async def get_cluster_friends(self, session):
        while not self.group_member_clusters.empty():
            members_cluster = await self.group_member_clusters.get()
            for member in members_cluster:
                await self.get_user_friends(session, member)

    async def get_user_friends(self, session, user_id: int):
        self.users_set.add(user_id)
        async with session.get(rm('friends.get', 'user_id=' + str(user_id) + '&fields=education')) as response:
            data = await response.json()
            if 'response' in data:
                friends = data['response']['items']
                for friend in friends:
                    if 'faculty' in friend:
                        if friend['faculty'] in allowed_faculties:
                            self.users_set.add(friend['id'])

    async def convert_set_to_clusters(self):
        users_list = list(self.users_set)
        offset = 0
        while len(users_list) - offset > 1000:
            temp_cluster = users_list[offset:offset + 1000]
            offset += 1000
            await self.user_clusters.put(list(temp_cluster))
            temp_cluster.clear()
        temp_cluster = users_list[offset:]
        await self.user_clusters.put(list(temp_cluster))
        temp_cluster.clear()

    async def collect_users(self, gmc):
        self.set_group_member_clusters(gmc)
        async with aiohttp.ClientSession() as session:
            await asyncio.gather(self.get_cluster_friends(session))
            await self.convert_set_to_clusters()

