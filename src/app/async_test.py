import asyncio
import aiohttp
import time
from collections import deque

# q = deque()
# d = dict()
#
#
# async def foo():
#     print('foo')
#     curr_unit = q.pop()
#     d[curr_unit] = curr_unit
#     # await bar()
#
#
# async def bar():
#     print('bar')
#     time.sleep(1)
#     for i in range(1000):
#         q.append(i)
#     await foo()
#
#
# async def main():
#     task1 = asyncio.create_task(bar())
#     task2 = asyncio.create_task(foo())
#     await asyncio.gather(task1, task2)
#
#
# if __name__ == '__main__':
#     asyncio.run(main())
#     print(d)
import requests

base_url = 'https://api.vk.com/method/'
access_token = 'b6e53625b6e53625b6e53625d1b6994f0bbb6e5b6e53625d49779210bced5b7ea7f455f'
api_ver = '5.131'
my_dict = dict()
users_stack = deque()
group_members_count = -1
offset = 0


def request_maker(method, params):
    return base_url + method + '?' + params + '&access_token=' + access_token + '&v=' + api_ver

def get_user_career(users):
    for i in range(len(users.json()['response'])):
        current_user = users.json()["response"][i]
        if 'career' in users.json()["response"][i]:
            comp_list = current_user['career']
            for comp in comp_list:
                if 'company' in comp:
                    if comp['company'] in my_dict:
                        my_dict[comp['company']] += 1
                    else:
                        my_dict[comp['company']] = 1



async def get_user_career_coroutine(group_members, session):
    async with session.get(request_maker('users.get',
                                         'user_ids=' +
                                         str(group_members.json()['response']['items'])[1:-1].replace(' ', '') +
                                         '&fields=career')) as users:
        get_user_career(users)
    await get_group_members('math_mech', offset, session)


def get_group_members_count(group_id):
    if group_members_count == -1:
        return \
        requests.get(request_maker('groups.getById', 'group_id=' + group_id + '&fields=name,members_count')).json()[
            "response"][0]["members_count"]
    else:
        return group_members_count


async def get_group_members(group_id, offset, session):
    group_members_count = get_group_members_count(group_id)
    if offset < group_members_count:
        async with session.get(request_maker('groups.getMembers',
                                             'group_id=math_mech&count=1000&offset=' + str(offset))) as group_members:
            offset += 1000
            await get_user_career_coroutine(group_members, session)


async def main():
    async with aiohttp.ClientSession() as session:
        task = get_group_members('math_mech', offset, session)
        await asyncio.gather(task)


if __name__ == '__main__':
    asyncio.run(main())
