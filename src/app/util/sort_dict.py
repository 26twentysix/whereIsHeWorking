def sort_dict(to_sort: dict):
    sorted_dict = dict(sorted(to_sort.items(), key=lambda item: item[1], reverse=True))
    return sorted_dict
