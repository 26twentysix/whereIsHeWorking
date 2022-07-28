from src.app.util.settings import group_id
from src.app.util.settings import allowed_faculties
from src.app.util.sort_dict import sort_dict


def create_output_file(employers, group_members_count, users_count):
    filepath = 'output/' + group_id + '.txt'
    with open(filepath, 'w', encoding='utf-8') as file:
        line = 'Results from parsing group vk.com/' + group_id + '\n'
        file.write(line)
        line = 'Allowed faculties:\n'
        for val in allowed_faculties.values():
            line += val + '\n'
        file.write(line)
        line = 'Group members count: ' + \
               str(group_members_count) + \
               '\nGroup members + their friends from allowed faculties count: ' + \
               str(users_count) + '\n\n'
        file.write(line)
        sorted_dict = sort_dict(employers)
        for key in sorted_dict:
            line = str(key) + ' : ' + str(employers[key]) + '\n'
            file.write(line)
