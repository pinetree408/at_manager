# -*- coding: utf-8 -*-
import re
import json
import copy

folder_name = 'AT'

def insert(tree, node):
    if len(tree['children']) == 0:
        node['parent'] = tree['id']
        tree['children'].append(node)
    else:
        if tree['children'][-1]['depth'] == node['depth']:
            node['parent'] = tree['id']
            tree['children'].append(node)
        elif tree['children'][-1]['depth'] < node['depth']:
            insert(tree['children'][-1], node)

def get_level(line):
    level = 0
    for i in range(len(line)):
        if line[i] == '+':
            level += 1
        else:
            break
    return level

def create_content_object(index, contents):
    matched_contents = re.findall('[a-zA-Z]+\s|[a-zA-Z]+=.[^=]+\s', contents + ' ')
    content_list = [content.strip() for content in matched_contents]

    is_focusable = False
    html_tag = ""
    name = ""

    var_object = {}
    for j, content in enumerate(content_list):
        if len(content.split('=')) == 2:
            target_key = content.split('=')[0]
            target_value = content.split('=')[1].strip()
            if target_value[0] == "'":
                target_value = target_value[1:-1].strip()
            if target_key == "htmlTag":
                if len(target_value) > 0 and not "<" in target_value:
                    html_tag = target_value
            elif target_key == "name":
                if len(target_value) > 0:
                    name = target_value
            else:
                var_object[target_key] = target_value
        else:
            if content == "focusable":
                is_focusable = True

    content_obj = {
        'id': index, 
        'atTag': content_list[0],
        'htmlTag': html_tag,
        'name': name,
    }
    return content_obj


def get_tree(f_name):
    path = folder_name + '/' + f_name

    tree_data = []
    with open(path, 'r') as f_r:
        lines = f_r.read().splitlines()
        for index, line in enumerate(lines):
            level = get_level(line)
            item = create_content_object(index, line[level:])
            node = {
                'id': index,
                'depth': level/2,
                'parent': -1,
                'name': item['name'],
                'atTag': item['atTag'],
                'htmlTag': item['htmlTag'],
                'children': [] 
            }
            if len(tree_data) == 0:
                tree_data.append(node)
            else:
                insert(tree_data[0], node)
    return json.dumps(tree_data, indent=4)

def get_content_list(f_name):
    path = folder_name + '/' + f_name

    node_list = []
    with open(path, 'r') as f_r:
        lines = f_r.read().splitlines()
        for index, line in enumerate(lines):
            level = get_level(line)
            item = create_content_object(index, line[level:])
            node_list.append(item)
    return json.dumps(node_list, indent=4)

def dfs_one_child_reduction(node):
    if len(node['children']) == 1:
        if len(node['children'][0]['children']) > 0:
            node['children'] = node['children'][0]['children']
            dfs_one_child_reduction(node)
        else:
            node.update(node['children'][0])
    else:
        for child in node['children'][:]:
            dfs_one_child_reduction(child)

def dfs_update_parent_and_depth(node):
    for child in node['children'][:]:
        child['parent'] = node['id']
        child['depth'] = node['depth'] + 1
        dfs_update_parent_and_depth(child)

def dfs_name_reduction_remain_parent(node):
    for child in node['children'][:]:
        if len(child['name']) == 0:
            if len(child['children']) == 0:
                node['children'].remove(child)
            else:
                dfs_name_reduction_remain_parent(child)
        else:
            dfs_name_reduction_remain_parent(child)

def dfs_name_reduction_remove_parent(node):
    for child in node['children'][:]:
        if len(child['name']) == 0:
            if len(child['children']) == 0:
                node['children'].remove(child)
            else:
                node['children'].extend(child['children'])
                node['children'].remove(child)
        else:
            dfs_name_reduction_remove_parent(child)

def get_tree_reduction(json_data):
    tree_data = json.loads(json_data)
    prev_tree_data = copy.deepcopy(tree_data)
    
    dfs_one_child_reduction(tree_data[0])
    dfs_update_parent_and_depth(tree_data[0])
    dfs_name_reduction_remain_parent(tree_data[0])
    dfs_update_parent_and_depth(tree_data[0])
    dfs_one_child_reduction(tree_data[0])
    dfs_update_parent_and_depth(tree_data[0])

    while tree_data != prev_tree_data:
        print "reducting"
        prev_tree_data = copy.deepcopy(tree_data)
        dfs_name_reduction_remain_parent(tree_data[0])
        dfs_update_parent_and_depth(tree_data[0])
        dfs_one_child_reduction(tree_data[0])
        dfs_update_parent_and_depth(tree_data[0])
    return json.dumps(tree_data, indent=4)

def convert_json_to_txt(f_name, json_data):
    with open(f_name, 'w') as outfile:
        outfile.write(json_data)

if __name__ == "__main__":
    f_name = 'naver.AT'
    tree = get_tree(f_name)
    tree = get_tree_reduction(tree)
    convert_json_to_txt('tree.json', tree)
