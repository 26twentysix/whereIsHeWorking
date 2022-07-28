import asyncio

import aiohttp

from src.app.util.request_maker import request_maker as rm


class UsersWorkplaceCollector:
    user_clusters = asyncio.Queue()
    employer_names = dict()
    employer_ids = dict()

    def set_user_clusters(self, uc):
        self.user_clusters = uc

    async def get_users_workplace(self, session):
        while not self.user_clusters.empty():
            cluster = await self.user_clusters.get()
            async with session.get(rm('users.get', 'user_ids=' + str(cluster)[1:-1].replace(' ', '') +
                                                   '&fields=career')) as response:
                data = await response.json()
                try:
                    for user in data['response']:
                        if 'career' in user:
                            for company in user['career']:
                                if 'company' in company:
                                    if company['company'] in self.employer_names:
                                        self.employer_names[company['company']] += 1
                                    else:
                                        self.employer_names[company['company']] = 1
                                elif 'group_id' in company:
                                    if company['group_id'] in self.employer_ids:
                                        self.employer_ids[company['group_id']] += 1
                                    else:
                                        self.employer_ids[company['group_id']] = 1
                except KeyError:
                    await self.user_clusters.put(cluster)

    async def convert_employer_ids(self, session):
        group_ids = list(self.employer_ids.keys())
        offset = 0
        while offset < len(group_ids):
            if len(group_ids) - offset > 0:
                ids_cluster = group_ids[offset:offset + 500]
            else:
                ids_cluster = group_ids[offset:]
            async with session.get(rm('groups.getById',
                                      'group_ids=' + str(ids_cluster)[1:-1].replace(' ', ''))) as response:
                data = await response.json()
                try:
                    for group in data['response']:
                        if group['name'] in self.employer_names:
                            self.employer_names[group['name']] += self.employer_ids[group['id']]
                        else:
                            self.employer_names[group['name']] = self.employer_ids[group['id']]
                    offset += 500
                    ids_cluster.clear()
                except KeyError:
                    pass

    async def collect_workplaces(self, uc):
        self.set_user_clusters(uc)
        async with aiohttp.ClientSession() as session:
            await asyncio.gather(self.get_users_workplace(session))
            await asyncio.gather(self.convert_employer_ids(session))
