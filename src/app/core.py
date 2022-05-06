import time

import requests

base_url = 'https://api.vk.com/method/'
access_token = '95967a0724e6cbccafdb90812fd7fdea824061b4ba144ebe4e099c91a1cec5203a833113baf6c63470c38'
api_ver = '5.131'


def request_maker(method, params):
    return base_url + method + '?' + params + '&access_token=' + access_token + '&v=' + api_ver


group = requests.get(request_maker('groups.getById', 'group_id=math_mech&fields=name,members_count'))
count = group.json()["response"][0]["members_count"]
offset = 0
my_dict = {}
while offset < count:
    time.sleep(0.3)
    group_members = requests.get(request_maker('groups.getMembers',
                                               'group_id=math_mech&count=1000&offset=' + str(offset)))
    users_with_info = requests.get(request_maker('users.get',
                                  'user_ids=' +
                                  str(group_members.json()['response']['items'])[1:-1].replace(' ', '') +
                                  '&fields=career'))
    for i in range(len(users_with_info.json()['response'])):
        current_user = users_with_info.json()["response"][i]
        if 'career' in users_with_info.json()["response"][i]:
            comp_list = users_with_info.json()["response"][i]['career']
            for comp in comp_list:
                if 'company' in comp:
                    if comp['company'] in my_dict:
                        my_dict[comp['company']] += 1
                    else:
                        my_dict[comp['company']] = 1
    offset += 100
print(my_dict)
