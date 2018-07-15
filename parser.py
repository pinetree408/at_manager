# -*- coding: utf-8 -*-
import re
import json
import copy
import codecs
import glob
import os
import math


FOLDER_PATH = 'AT'


def insert_node(tree, node):
    if len(tree['children']) == 0:
        tree['children'].append(node)
    else:
        if tree['children'][-1]['depth'] == node['depth']:
            tree['children'].append(node)
        elif tree['children'][-1]['depth'] < node['depth']:
            insert_node(tree['children'][-1], node)


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


def get_tree(path):

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
                insert_node(tree_data[0], node)
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
        prev_tree_data = copy.deepcopy(tree_data)
        dfs_name_reduction_remain_parent(tree_data[0])
        dfs_one_child_reduction(tree_data[0])

    dfs_update_depth(tree_data[0])
    return json.dumps(tree_data, indent=4)


def word_analyze_dfs(json_data):
    tree_data = json.loads(json_data)
    word_set = {}

    will_visit = []
    visited = []

    will_visit.append(tree_data[0])

    while(will_visit):
        node = will_visit.pop()
        visited.append(node)

        word_list = list(set([w.strip() for w in node['name'].split(' ')]))
        for word in word_list:
            if not word:
                continue

            if word in word_set:
                word_set[word] = word_set[word] + 1
            else:
                word_set[word] = 1

        for child in node['children']:
            if child not in visited:
                will_visit.append(child)

    return word_set


def node_analyze_dfs(json_data):
    tree_data = json.loads(json_data)
    node_num = 0

    will_visit = []
    visited = []

    will_visit.append(tree_data[0])

    while(will_visit):
        node = will_visit.pop()
        visited.append(node)

        node_num = node_num + 1

        for child in node['children']:
            if child not in visited:
                will_visit.append(child)

    return node_num


def convert_json_to_txt(json_data, f_name, target_site_dir):
    if not os.path.exists('results/' + target_site_dir):
        os.makedirs('results/' + target_site_dir)
    with codecs.open(
            'results/' + target_site_dir + '/' + f_name,
            'w', encoding='utf-8') as outfile:
        outfile.write(json_data)


if __name__ == "__main__":
    target_site_dir_list = [
        'google_news',
    ]
    for target_site_dir in target_site_dir_list:
        target_site_path_list = glob.glob(
            FOLDER_PATH + "/" + target_site_dir + "/*.AT"
        )
        all_word_set = {}
        all_node_num = 0
        for target_site_path in target_site_path_list:
            tree = get_tree(target_site_path)
            tree = get_tree_reduction(tree)

            node_num = node_analyze_dfs(tree)
            all_node_num = all_node_num + node_num
            word_set = word_analyze_dfs(tree)
            for key in word_set.keys():
                if key in all_word_set:
                    all_word_set[key] = all_word_set[key] + word_set[key]
                else:
                    all_word_set[key] = word_set[key]

            target_site = target_site_path.split('/')[2].split('.')[0]
            convert_json_to_txt(tree, target_site+'.json', target_site_dir)

        idf_set = {}
        for word in all_word_set.keys():
            idf = math.log10((all_node_num * 1.0) / (all_word_set[word] + 1))
            idf_set[word] = idf

        convert_json_to_txt(
            json.dumps(idf_set, indent=4),
            'idf.json', target_site_dir)
