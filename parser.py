# -*- coding: utf-8 -*-
import re
import json
import copy
import codecs


FOLDER_PATH = 'AT'
ALL_NODE = {}
NAME_EMPTY_NODES = {}
MAX_CHILDREN = 0


def insert(tree, node):
    if len(tree['children']) == 0:
        tree['children'].append(node)
    else:
        if tree['children'][-1]['depth'] == node['depth']:
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


def create_content_object(contents):
    matched_contents = re.findall(
        '[a-zA-Z]+\s|[a-zA-Z]+=.[^=]+\s',
        contents + ' ')
    content_list = [content.strip() for content in matched_contents]

    html_tag = ""
    name = ""

    for j, content in enumerate(content_list):
        if len(content.split('=')) == 2:
            target_key = content.split('=')[0]
            target_value = content.split('=')[1].strip()
            if target_value[0] == "'":
                target_value = target_value[1:-1].strip()
            if target_key == "htmlTag":
                if len(target_value) > 0 and "<" not in target_value:
                    html_tag = target_value
            elif target_key == "name":
                if len(target_value) > 0:
                    name = target_value

    content_obj = {
        'atTag': content_list[0],
        'htmlTag': html_tag,
        'name': name,
    }
    return content_obj


def get_tree(f_name):
    path = FOLDER_PATH + '/' + f_name

    tree_data = []
    with codecs.open(path, 'r', encoding='utf8') as f_r:
        lines = f_r.read().splitlines()
        for index, line in enumerate(lines):
            level = get_level(line)
            item = create_content_object(line[level:])
            node = {
                'id': index,
                'depth': level/2,
                'name': item['name'],
                'atTag': item['atTag'],
                'htmlTag': item['htmlTag'],
                'children': [],
            }
            if len(tree_data) == 0:
                tree_data.append(node)
            else:
                insert(tree_data[0], node)
    return json.dumps(tree_data, indent=4)


def dfs_one_child_reduction(node):
    if len(node['children']) == 1:
        child_node = node['children'][0]
        p_name = node['name']
        c_name = child_node['name']

        condition_one = (p_name == '') and (c_name == '')
        condition_two = (p_name == '') and (c_name != '')
        condition_three = (p_name != '') and (c_name == '')
        condition_four = (p_name != '') and (c_name != '')
        condition_four_one = condition_four and (p_name == c_name)
        condition_four_two = condition_four and (p_name != c_name)

        if condition_one or condition_two or \
                condition_three or condition_four_one:
            new_name = p_name if len(p_name) >= len(c_name) else c_name
            node['name'] = new_name
            node['atTag'] = node['atTag'] + "-" + child_node['atTag']
            node['htmlTag'] = node['htmlTag'] + "-" + child_node['htmlTag']
            node['children'] = child_node['children']
            dfs_one_child_reduction(node)
        elif condition_four_two:
            dfs_one_child_reduction(child_node)
    else:
        for child in node['children'][:]:
            dfs_one_child_reduction(child)


def dfs_update_depth(node):
    for child in node['children'][:]:
        child['depth'] = node['depth'] + 1
        dfs_update_depth(child)


def dfs_name_reduction_remain_parent(node):
    for child in node['children'][:]:
        if len(child['name']) == 0 and len(child['children']) == 0:
            node['children'].remove(child)
        else:
            dfs_name_reduction_remain_parent(child)


def get_tree_reduction(json_data):
    tree_data = json.loads(json_data)
    prev_tree_data = []

    while tree_data != prev_tree_data:
        print "reducting"
        prev_tree_data = copy.deepcopy(tree_data)
        dfs_name_reduction_remain_parent(tree_data[0])
        dfs_one_child_reduction(tree_data[0])

    dfs_update_depth(tree_data[0])
    return json.dumps(tree_data, indent=4)


def convert_json_to_txt(f_name, json_data):
    with codecs.open('results/' + f_name, 'w', encoding='utf-8') as outfile:
        outfile.write(json_data)


def dfs_analyze(node):
    global ALL_NODE, NAME_EMPTY_NODES, MAX_CHILDREN
    html_tag = node["htmlTag"].split('-')[0]

    if html_tag in ALL_NODE:
        ALL_NODE[html_tag] += 1
    else:
        ALL_NODE[html_tag] = 1

    if len(node["name"]) == 0:
        if html_tag in NAME_EMPTY_NODES:
            NAME_EMPTY_NODES[html_tag] += 1
        else:
            NAME_EMPTY_NODES[html_tag] = 1

    if len(node['children']) >= MAX_CHILDREN:
        MAX_CHILDREN = len(node['children'])

    for child in node['children'][:]:
        dfs_analyze(child)


def analyze_tree(json_data):
    tree_data = json.loads(json_data)
    dfs_analyze(tree_data[0])

    print "Max children len : ", MAX_CHILDREN
    print "TAG\tALL\tNAME_EMPTY"
    print "---\t---\t----------"
    sum_all = 0
    sum_name_empty = 0
    for key in ALL_NODE.keys():
        values = ALL_NODE[key]
        sum_all += values
        if key in NAME_EMPTY_NODES:
            sum_name_empty += NAME_EMPTY_NODES[key]
            print key + "\t" + str(values) + "\t" + str(NAME_EMPTY_NODES[key])
        else:
            if key != "":
                print key + "\t" + str(values) + "\t0"
            else:
                print "text\t" + str(values) + "\t0"
    print "---\t---\t----------"
    print "sum\t" + str(sum_all) + "\t" + str(sum_name_empty)


if __name__ == "__main__":
    target_site_list = [
        'amazon', 'blog', 'daum', 'naver', 'news', 'search', 'wiki'
    ]
    for target_site in target_site_list:
        ALL_NODE = {}
        NAME_EMPTY_NODES = {}
        MAX_CHILDREN = 0
        PREV_PRINTED_NODE_PARENT = -1

        f_name = target_site + '.AT'
        tree = get_tree(f_name)
        tree = get_tree_reduction(tree)
        print "Target Site :", target_site
        analyze_tree(tree)
        convert_json_to_txt(target_site+'.json', tree)
