import os
from dotenv import load_dotenv

base_url = 'https://api.vk.com/method/'  # vk.com api url
api_ver = '5.131'  # used api ver
group_id = 'math_mech'  # group_id to parse (from vk.com/GROUP_ID)
access_token: str
allowed_faculties = {2231180: 'Математико-механический факультет, УрГУ',
                     2139051: 'Институт математики и компьютерных наук, '
                              'УрФУ им. первого Президента России Б. Н. Ельцина'}


# ids of allowed faculties for friends of group members
# (can be obtained from vk.com api from database.getUniversities and database.getFaculties methods),
# value used only for better output


def set_access_token(dotenv_path):
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)
        global access_token
        access_token = os.environ.get('ACCESS_TOKEN')
