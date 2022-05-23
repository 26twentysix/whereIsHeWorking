import asyncio
import time
import aiohttp
import requests
import os
from dotenv import load_dotenv


def sort_dict(output: dict):
    sorted_dict = dict(sorted(output.items(), key=lambda item: item[1], reverse=True))
    return sorted_dict


class App:
    group_id = 'ural.federal.university'
    base_url = 'https://api.vk.com/method/'
    api_ver = '5.131'
    access_token = ''
    employers = dict()
    members_k_stack = asyncio.Queue()
    users_k_stack = asyncio.Queue()
    employers_id = dict()
    group_members_done_flag = False
    all_users_set = set()
    allowed_faculties = [2231180, 2139051]

    def set_access_token(self, dotenv_path):
        if os.path.exists(dotenv_path):
            load_dotenv(dotenv_path)
            self.access_token = os.environ.get('ACCESS_TOKEN')

    def request_maker(self, method, params):
        return self.base_url + method + '?' + params + '&access_token=' + self.access_token + '&v=' + self.api_ver

    def set_group_members_count(self):
        self.group_members_count = \
            requests.get(self.request_maker('groups.getById',
                                            'group_id=' + self.group_id + '&fields=name,members_count')).json()[
                "response"][0]["members_count"]

    def init(self):
        self.set_group_members_count()
        print('Starting group parse...')

    def create_output_file(self):
        filepath = 'output/' + self.group_id + '.txt'
        with open(filepath, 'w', encoding='utf-8') as file:
            sorted_dict = sort_dict(self.employers)
            for key in sorted_dict:
                line = str(key) + ' : ' + str(self.employers[key]) + '\n'
                file.write(line)

    async def get_group_members(self, session, offset):
        while offset < self.group_members_count:
            async with session.get(
                    self.request_maker('groups.getMembers', 'group_id=' + self.group_id + '&count=1000&offset=' + str(
                        offset))) as response:
                data = await response.json()
                offset += 1000
                await self.members_k_stack.put(data['response']['items'])
                await self.get_members_friends(session)

    async def get_members_friends(self, session):
        while not self.members_k_stack.empty():
            k_members = await self.members_k_stack.get()
            for member in k_members:
                pass
                await self.get_member_friends(session, member)
        await self.convert_user_set()
        await self.get_users_workplace(session)

    async def convert_user_set(self):
        all_users_list = list(self.all_users_set)
        start_pos = 0
        while start_pos < len(all_users_list):
            if len(all_users_list) - start_pos > 0:
                k_users = all_users_list[start_pos:start_pos + 1000]
            else:
                k_users = all_users_list[start_pos:]
            start_pos += 1000
            await self.users_k_stack.put(list(k_users))
            k_users.clear()

    async def get_users_workplace(self, session):
        while not self.users_k_stack.empty():
            k_users = await self.users_k_stack.get()
            async with session.get(self.request_maker('users.get', 'user_ids=' + str(k_users)[1:-1].replace(' ', '') +
                                                                   '&fields=career')) as response:
                data = await response.json()
                for user in data['response']:
                    if 'career' in user:
                        for company in user['career']:
                            if 'company' in company:
                                if company['company'] in self.employers:
                                    self.employers[company['company']] += 1
                                else:
                                    self.employers[company['company']] = 1
                            elif 'group_id' in company:
                                if company['group_id'] in self.employers_id:
                                    self.employers_id[company['group_id']] += 1
                                else:
                                    self.employers_id[company['group_id']] = 1
        await self.convert_group_ids(session)

    async def convert_group_ids(self, session):
        group_ids = list(self.employers_id.keys())
        start_pos = 0
        while start_pos < len(group_ids):
            if len(group_ids) - start_pos > 0:
                k_ids = group_ids[start_pos:start_pos + 500]
            else:
                k_ids = group_ids[start_pos:]
            async with session.get(self.request_maker('groups.getById',
                                                      'group_ids=' + str(k_ids)[1:-1].replace(' ', ''))) as response:
                data = await response.json()
                for group in data['response']:
                    if group['name'] in self.employers:
                        self.employers[group['name']] += self.employers_id[group['id']]
                    else:
                        self.employers[group['name']] = self.employers_id[group['id']]
            start_pos += 500
            k_ids.clear()

    async def get_member_friends(self, session, member):
        self.all_users_set.add(member)
        async with session.get(
                self.request_maker('friends.get', 'user_id=' + str(member) + '&fields=education')) as response:
            data = await response.json()
            if 'response' in data:
                users = data['response']['items']
                for user in users:
                    if 'faculty' in user:
                        if user['faculty'] in self.allowed_faculties:
                            self.all_users_set.add(user['id'])

    async def main(self):
        async with aiohttp.ClientSession() as session:
            task = self.get_group_members(session, 0)
            await asyncio.gather(task)

    def run_app(self):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        self.init()
        t0 = time.time()
        asyncio.run(self.main())
        self.create_output_file()
        print(time.time() - t0)
        print('Done.')
