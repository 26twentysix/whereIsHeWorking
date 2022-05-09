import asyncio
import aiohttp
import requests
import time

base_url = 'https://api.vk.com/method/'
access_token = 'b6e53625b6e53625b6e53625d1b6994f0bbb6e5b6e53625d49779210bced5b7ea7f455f'
api_ver = '5.131'
my_dict = dict()
users_stack = asyncio.Queue()
group_members_count = 0
group_id = ''
offset = 0


def request_maker(method, params):
    return base_url + method + '?' + params + '&access_token=' + access_token + '&v=' + api_ver


def set_group_members_count():
    global group_members_count
    group_members_count = \
        requests.get(request_maker('groups.getById', 'group_id=' + group_id + '&fields=name,members_count')).json()[
            "response"][0]["members_count"]


async def get_user_info(session):
    while not users_stack.empty():
        current_users_ids = await users_stack.get()
        str(current_users_ids)[1:-1].replace(' ', '')
        async with session.get(request_maker('users.get',
                                             'user_ids=' +
                                             str(current_users_ids)[1:-1].replace(' ', '') +
                                             '&fields=career')) as users_info:
            data = await users_info.json()
            for i in range(len(data['response'])):
                current_user = data['response'][i]
                if 'career' in current_user:
                    for comp in current_user['career']:
                        if 'company' in comp:
                            if comp['company'] in my_dict:
                                my_dict[comp['company']] += 1
                            else:
                                my_dict[comp['company']] = 1


async def get_group_members(session):
    global offset
    if offset < group_members_count:
        async with session.get(request_maker('groups.getMembers',
                                             'group_id=' + group_id + '&count=1000&offset=' + str(offset))) as group_members:
            data = await group_members.json()
            await users_stack.put(data['response']['items'])
        offset += 1000
        await get_group_members(session)
    else:
        await get_user_info(session)


def check_valid_group_link(group_link: str):
    return group_link[:15] == 'https://vk.com/' and ' ' not in group_link


def set_group_id():
    print('Enter group link in format "https://vk.com/GROUP_ID" without any spaces:')
    group_link = input()
    while not check_valid_group_link(group_link):
        print('Wrong format!\nEnter group link in format "https://vk.com/GROUP_ID" without any spaces:')
        group_link = input()
    global group_id
    group_id = group_link[15:]

def init_script():
    set_group_id()
    set_group_members_count()


async def main():
    t0 = time.time()
    async with aiohttp.ClientSession() as session:
        task1 = get_group_members(session)
        task2 = get_user_info(session)
        await asyncio.gather(task1, task2)
        print(time.time() - t0)
        print(my_dict)


if __name__ == '__main__':
    init_script()
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())