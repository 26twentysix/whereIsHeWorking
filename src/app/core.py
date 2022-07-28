import asyncio

from src.app.util.settings import set_access_token
from src.app.group_members_collector.group_members_collector import GroupMembersCollector
from src.app.user_friends_collector.user_friends_collector import UserFriendsCollector
from src.app.users_workplace_collector.users_workplace_collector import UsersWorkplaceCollector
from src.app.output_maker.output_maker import create_output_file


def run_app(dotenv_path):
    print('Starting app...')
    set_access_token(dotenv_path)
    group_members_collector = GroupMembersCollector()
    print('Getting group members...')
    asyncio.run(group_members_collector.collect_members())
    user_friends_collector = UserFriendsCollector()
    print('Collecting group members friends...')
    asyncio.run(user_friends_collector.collect_users(group_members_collector.member_clusters))
    users_workplace_collector = UsersWorkplaceCollector()
    print('Looking where are they working...')
    asyncio.run(users_workplace_collector.collect_workplaces(user_friends_collector.user_clusters))
    print('Creating output...')
    create_output_file(users_workplace_collector.employer_names, group_members_collector.group_members_count,
                       len(user_friends_collector.users_set))
    print('Done.')
