import json

folder_name = 'AT'

def insert(tree, item):
    if len(tree['children']) == 0:
        item['parent'] = tree['pk']
        tree['children'].append(item['pk'])
        tree['visibleChildren'].append(item)
    else:
        if tree['visibleChildren'][-1]['level'] == item['level']:
            item['parent'] = tree['pk']
            tree['children'].append(item['pk'])
            tree['visibleChildren'].append(item)
        elif tree['visibleChildren'][-1]['level'] < item['level']:
            insert(tree['visibleChildren'][-1], item)

def create_content_object(index, line):
    level = 0
    for i in range(len(line)):
        if line[i] == '+':
            level += 1
        else:
            break
    contents = line[level:]
    content_list = contents.split(' ')

    is_focusable = False
    focusable_count = 0

    var_object = {}
    for j, content in enumerate(content_list):
        content = content.strip()
        if len(content) == 0 or content[-1] == ')':
            continue

        target = content
        if content[-1] == ',':
            target = target + content_list[j + 1]

        if len(target.split('=')) == 2:
            target_key = target.split('=')[0]
            target_value = target.split('=')[1]
            var_object[target_key] = target_value
        else:
            if target == "focusable":
                is_focusable = True
                focusable_count = 1

    content_obj = {
        'pk': index, 
        'level': level/2,
        'atTag': content_list[0],
        'isFocusable': is_focusable,
        'focusableSum': focusable_count,
        'var': var_object,
        'parent': 'null',
        'children': [],
        'visibleChildren': [],
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
            if child['focusable'] == True:
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
            if not (child['focusable'] and child['focusableSum'] == 1):
                dfs_with_child(child)
        else:
            node['visibleChildren'].remove(child)


def dfs_without_child(node):
    for child in node['children'][:]:
        if child['focusableSum'] > 0:
            dfs_without_child(child)
        else:
            node['visibleChildren'].remove(child)


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

    f_name = 'naver.AT'
    focusable_list = get_focusable_list(f_name)
    with open(out_name, 'w') as f_w:
        json.dump(focusable_list, f_w)

if __name__ == "__main__":
    print json.loads(get_tree('naver.AT'))[0]['visibleChildren'][0]['children']
