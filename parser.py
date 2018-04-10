import json

folder_name = 'AT'
f_name = 'mobile_verge.AT'

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

def get_tree():
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
            item = {
                'level': level/2,
                'name': content.split(' ')[0],
                'focusable': is_focusable,
                'var': content,
                'parent': 'null',
                'children': []
            }
            if len(tree_data) == 0:
                tree_data.append(item)
            else:
                insert(tree_data[0], item)
    return json.dumps(tree_data)

def focusable_search(children):
    for child in children:
        if len(child['children']) != 0:
            focusable_search(child['children'])
        else:
            if child['focusable'] == False:
                for i in range(len(children)):
                    if children[i]['var'] == child['var']:
                        del children[i]
                        break

def get_focusable_tree(json_data):
    tree_data = json.loads(json_data)
    focusable_search(tree_data[0]['children'])
    return json.dumps(tree_data)


if __name__ == "__main__":
    get_focusable_tree(get_tree())
