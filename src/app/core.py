import time
import asyncio
import requests

from collections import deque


def check_valid_group_link(group_link: str):
    return group_link[:15] == 'https://vk.com/' and group_link
print(check_valid_group_link('htttps://vk.com/GROUP_ID'))