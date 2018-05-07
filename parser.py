import re
import json

folder_name = 'AT'

def insert(tree, item):
    if len(tree['children']) == 0:
        item['parent'] = tree['id']
        tree['children'].append(item)
    else:
        if tree['children'][-1]['level'] == item['level']:
            item['parent'] = tree['id']
            tree['children'].append(item)
        elif tree['children'][-1]['level'] < item['level']:
            insert(tree['children'][-1], item)

def get_level(line):
    level = 0
    for i in range(len(line)):
        if line[i] == '+':
            level += 1
        else:
            break
    return level

def create_content_object(index, line):
    level = get_level(line)
    contents = line[level:]
    m = re.findall('[a-zA-Z]+\s|[a-zA-Z]+=.[^=]+\s', contents + ' ')
    content_list = [temp.strip() for temp in m]

    is_focusable = False
    focusable_count = 0

    var_object = {}
    for j, content in enumerate(content_list):
        if len(content.split('=')) == 2:
            target_key = content.split('=')[0]
            target_value = content.split('=')[1]
            var_object[target_key] = target_value
        else:
            if content == "focusable":
                is_focusable = True
                focusable_count = 1

    content_obj = {
        'id': index, 
        'level': level/2,
        'atTag': content_list[0],
        'isFocusable': is_focusable,
        'focusableSum': focusable_count,
        'var': var_object,
        'parent': 'null',
        'children': [],
    }
    return content_obj


def get_tree(f_name):
    path = folder_name + '/' + f_name

    tree_data = []
    with open(path, 'r') as f_r:
        lines = f_r.read().splitlines()
        for index, line in enumerate(lines):
            item = create_content_object(index, line)
            if len(tree_data) == 0:
                tree_data.append(item)
            else:
                insert(tree_data[0], item)
    return json.dumps(tree_data)


def focusable_search(node):
    focusable_sum = node['focusableSum']
    for child in node['children']:
        if len(child['children']) != 0:
            focusable_sum += focusable_search(child)
        else:
            if child['isFocusable'] == True:
                focusable_sum += 1
    node['focusableSum'] = focusable_sum
    return node['focusableSum']


def focusable_count(json_data):
    tree_data = json.loads(json_data)
    focusable_search(tree_data[0])
    return tree_data

def dfs_with_child(node):
    for child in node['children'][:]:
        if child['focusableSum'] > 0:
            if not (child['isFocusable'] and child['focusableSum'] == 1):
                dfs_with_child(child)
        else:
            node['children'].remove(child)


def dfs_without_child(node):
    for child in node['children'][:]:
        if child['focusableSum'] > 0:
            dfs_without_child(child)
        else:
            node['children'].remove(child)


def get_focusable_tree_with_child(json_data):
    tree_data = focusable_count(json_data)
    dfs_with_child(tree_data[0])
    return json.dumps(tree_data)

def get_focusable_tree_without_child(json_data):
    tree_data = focusable_count(json_data)
    dfs_without_child(tree_data[0])
    return json.dumps(tree_data)

if __name__ == "__main__":
    print json.loads(get_tree('naver.AT'))
