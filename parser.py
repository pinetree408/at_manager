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
                'children': []
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

def dfs(node):
    for i, child in enumerate(node['children']):
        if child['focusable_sum'] != 0:
            dfs(child)
        else:
            del node['children'][i]

def get_focusable_tree(json_data):
    tree_data = focusable_count(json_data)
    dfs(tree_data[0])
    return json.dumps(tree_data)

if __name__ == "__main__":
    get_focusable_tree(get_tree())
