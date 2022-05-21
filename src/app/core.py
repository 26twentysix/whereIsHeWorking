import asyncio
import time

import aiohttp
import requests
import os
from collections import defaultdict
from dotenv import load_dotenv

base_url = 'https://api.vk.com/method/'
api_ver = '5.131'


def set_env_vars(dotenv_path):
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)
        global access_token
        access_token = os.environ.get('ACCESS_TOKEN')


def request_maker(method, params):
    return base_url + method + '?' + params + '&access_token=' + access_token + '&v=' + api_ver


def set_group_members_count():
    global group_members_count
    group_members_count = \
        requests.get(request_maker('groups.getById', 'group_id=' + group_id + '&fields=name,members_count')).json()[
            "response"][0]["members_count"]


async def get_company_name(user_company_group_id, session):
    async with session.get(request_maker('groups.getById', 'group_id=' + str(user_company_group_id))) as response:
        resp_json = await response.json()
        user_company_name = resp_json['response'][0]['name']
        return user_company_name


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
                    for current_user_company in current_user['career']:
                        if 'company' in current_user_company:
                            if current_user_company['company'] in employers:
                                employers[current_user_company['company']] += 1
                            else:
                                employers[current_user_company['company']] = 1
                        elif 'group_id' in current_user_company:
                            company = current_user_company['group_id']
                            if company in employers:
                                employers_id[company] += 1
                            else:
                                employers_id[company] = 1


# async def get_user_friend


def convert_emp_ids_to_name():
    global employers
    group_ids = str(employers_id.keys())[11:-2].replace(' ', '')
    response = requests.get(request_maker('groups.getById', 'group_ids=' + group_ids))
    group_names = list()
    keys = list()
    vals = employers_id.values()
    for i in range(len(response.json()['response'])):
        keys.append(response.json()['response'][i]['name'])
    new_dict = dict(zip(keys, vals))
    print(new_dict)
    employers.update(new_dict)


async def get_group_members(session, offset):
    # global offset
    if offset < group_members_count:
        async with session.get(request_maker('groups.getMembers',
                                             'group_id=' + group_id + '&count=1000&offset=' + str(
                                                 offset))) as group_members:
            data = await group_members.json()
            await users_stack.put(data['response']['items'])
        offset += 1000
        await get_group_members(session, offset)
        await get_user_info(session)


def check_valid_group_link(group_link: str):
    if not group_link.startswith('https://vk.com/') or ' ' in group_link:
        return 1
    resp = requests.get(request_maker('groups.getById', 'group_id=' + group_link[15:]))
    if 'error' in resp.json():
        return 2
    return 0


def set_group_id():
    print('Enter group link in format "https://vk.com/GROUP_ID" without any spaces:')
    group_link = input()
    while not check_valid_group_link(group_link) == 0:
        ret_code = check_valid_group_link(group_link)
        if ret_code == 1:
            print('Wrong format!\nEnter group link in format "https://vk.com/GROUP_ID" without any spaces:')
        elif ret_code == 2:
            print('Something went wrong, group doesn\'t exist\n'
                  'Enter group link in format "https://vk.com/GROUP_ID" without any spaces:')
        group_link = input()
    global group_id
    group_id = group_link[15:]


def init():
    set_group_id()
    set_group_members_count()
    global employers, users_stack, employers_id
    employers_id = dict()
    employers = dict()
    users_stack = asyncio.Queue()
    print('Starting group parse...')


def run_app():
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    print('To start app enter start or enter help to get available commands')
    command = input().replace(' ', '')
    while True:
        if command == 'start':
            init()
            t0 = time.time()
            asyncio.run(main())
            print(time.time() - t0)
            create_output_file()
            print('Done.\nEnter next command:')
            command = input().replace(' ', '')
        elif command == 'stop':
            print('Exiting app...')
            exit(0)
        elif command == 'help':
            print('Available commands:\ninfo - output information about app\nhelp - output available commands\n'
                  'start - start app\nstop - stop app\nEnter next command:')
            command = input().replace(' ', '')
        elif command == 'info':
            print('This app is parsing info about group members and output their employers in'
                  ' output/GROUP_ID.txt\nEnter next command:')
            command = input().replace(' ', '')
        else:
            print('Wrong command\nEnter next command:')
            command = input().replace(' ', '')


def sort_dict(dict1: dict):
    sorted_dict = dict(sorted(dict1.items(), key=lambda item: item[1], reverse=True))
    return sorted_dict


def create_output_file():
    filepath = 'output/' + group_id + '.txt'
    convert_emp_ids_to_name()
    with open(filepath, 'w', encoding='utf-8') as file:
        sorted_dict = sort_dict(employers)
        for key in sorted_dict:
            line = str(key) + ' : ' + str(employers[key]) + '\n'
            file.write(line)


async def main():
    async with aiohttp.ClientSession() as session:
        task1 = get_group_members(session, 0)
        task2 = get_user_info(session)
        await asyncio.gather(task1, task2)
