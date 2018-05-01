import json

folder_name = 'AT'

def insert(tree, item):
    if len(tree['children']) == 0:
        item['parent'] = tree['name']
        tree['children'].append(item)
    else:
        if tree['children'][-1]['level'] == item['level']:
            item['parent'] = tree['name']
            tree['children'].append(item)
        elif tree['children'][-1]['level'] < item['level']:
            insert(tree['children'][-1],item)

def get_tree(f_name):
    path = folder_name + '/' + f_name

    tree_data = []
    with open(path, 'r') as f_r:
        lines = f_r.read().splitlines()
        for line in lines:
            level = 0
            for i in range(len(line)):
                if line[i] == '+':
                    level += 1
                else:
                    break
            content = line[level:]
            is_focusable = content.split(' ')[1] == "focusable"
            focusable_count = 1 if is_focusable == True else 0
            item = {
                'level': level/2,
                'name': content.split(' ')[0],
                'focusable': is_focusable,
                'focusable_sum': focusable_count,
                'var': content,
                'parent': 'null',
                'children': [],
                'children_hide': []
            }
            if len(tree_data) == 0:
                tree_data.append(item)
            else:
                insert(tree_data[0], item)
    return json.dumps(tree_data)

def focusable_search(node):
    focusable_sum = node['focusable_sum']
    for child in node['children']:
        if len(child['children']) != 0:
            focusable_sum += focusable_search(child)
        else:
            if child['focusable'] == True:
                focusable_sum += 1
    node['focusable_sum'] = focusable_sum
    return node['focusable_sum']

def focusable_count(json_data):
    tree_data = json.loads(json_data)
    focusable_search(tree_data[0])
    return tree_data

def dfs_with_child(node):
    for child in node['children'][:]:
        if child['focusable_sum'] > 0:
            if not (child['focusable'] and child['focusable_sum'] == 1):
                dfs_with_child(child)
        else:
            node['children_hide'].append(child)
            node['children'].remove(child)


def dfs_without_child(node):
    for child in node['children'][:]:
        if child['focusable_sum'] > 0:
            dfs_without_child(child)
        else:
            node['children_hide'].append(child)
            node['children'].remove(child)


def get_focusable_tree_with_child(json_data):
    tree_data = focusable_count(json_data)
    dfs_with_child(tree_data[0])
    return json.dumps(tree_data)

def get_focusable_tree_without_child(json_data):
    tree_data = focusable_count(json_data)
    dfs_without_child(tree_data[0])
    return json.dumps(tree_data)

def get_focusable_list(f_name):
    path = folder_name + '/' + f_name

    focusable_list = []
    with open(path, 'r') as f_r:
        lines = f_r.read().splitlines()
        for line in lines:
            level = 0
            for i in range(len(line)):
                if line[i] == '+':
                    level += 1
                else:
                    break
            contents = line[level:]
            content_list = contents.split(' ')
            is_focusable = content_list[1] == "focusable"
            size = ""
            for i, content in enumerate(content_list):
                if content[:4] == 'size':
                    size = content + content_list[i+1]
                    break

            if is_focusable:
                item = {
                    "tag" : content_list[0],
                    "size" : size,
                    "level" : level/2,
                    "index" : len(focusable_list)
                }
                focusable_list.append(item)

    return focusable_list

def generate_txt_file_with_focusalbe_list(out_name):

    f_name = 'mobile_naver.AT'
    focusable_list = get_focusable_list(f_name)
    with open(out_name, 'w') as f_w:
        json.dump(focusable_list, f_w)

if __name__ == "__main__":
    generate_txt_file_with_focusalbe_list('json.txt')
