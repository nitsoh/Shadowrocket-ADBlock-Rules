# -*- coding: utf-8 -*-

#
# 下载并解析最新版本的 GFWList
# 忽略混合性质的网站
# 对于@@指定的站点，单独列出
#


import time
import requests
import re
import base64


rules_url = 'https://raw.githubusercontent.com/gfwlist/gfwlist/master/gfwlist.txt'

unhandle_rules = []
unhandle_rules_bypass = []


def get_rule(rules_url):
    success = False
    try_times = 0
    r = None
    while try_times < 5 and not success:
        r = requests.get(rules_url)
        if r.status_code != 200:
            time.sleep(1)
            try_times = try_times + 1
        else:
            success = True
            break

    if not success:
        raise Exception('error in request %s\n\treturn code: %d' % (rules_url, r.status_code) )

    rule = base64.b64decode(r.text) \
            .decode("utf-8") \
            .replace('\\n', '\n')

    return rule


def clear_format(rule):
    rules = []

    rule = rule.split('\n')
    for row in rule:
        row = row.strip()

        # 注释 直接跳过
        if row == '' or row.startswith('!') or row.startswith('@@') or row.startswith('[AutoProxy'):
            continue

        # 清除前缀
        row = re.sub(r'^\|?https?://', '', row)
        row = re.sub(r'^\|\|', '', row)
        row = row.lstrip('.*')

        # 清除后缀
        row = row.rstrip('/^*')

        rules.append(row)

    return rules

def clear_format_bypass(rule):
    rules_bypass = []

    rule = rule.split('\n')
    for row in rule:
        row = row.strip()

        if row.startswith('@@'):

            # 清除前缀
            row = row.lstrip('@')
            row = re.sub(r'^\|?https?://', '', row)
            row = re.sub(r'^\|\|', '', row)
            row = row.lstrip('.*')

            # 清除后缀 
            row = row.rstrip('/^*')

            rules_bypass.append(row)

    return rules_bypass

def filtrate_rules(rules):
    ret = []

    for rule in rules:
        rule0 = rule

        # only hostname
        # if '/' in rule:
        #     split_ret = rule.split('/')
        #     rule = split_ret[0]

        # 不考虑混合性质的站点
        if (not re.match('^[\w.-]+$', rule)) or ('/' in rule):
            unhandle_rules.append(rule0)
            continue

        ret.append(rule)

    ret = list( set(ret) )
    ret.sort()

    return ret

def filtrate_rules_bypass(rules):
    ret = []

    for rule in rules:
        rule0 = rule

        # only hostname
        # if '/' in rule:
        #     split_ret = rule.split('/')
        #     rule = split_ret[0]

        if (not re.match('^[\w.-]+$', rule)) or ('/' in rule) or ('ampproject.org' in rule):
            unhandle_rules_bypass.append(rule0)
            continue

        ret.append(rule)

    ret = list( set(ret) )
    ret.sort()

    return ret

# main

rule = get_rule(rules_url)

rules = clear_format(rule)

rules = filtrate_rules(rules)

rules_bypass = clear_format_bypass(rule)

rules_bypass = filtrate_rules_bypass(rules_bypass)

# 保存原始 gfwlist
open('resultant/gfwlist.txt', 'w', encoding='utf-8') \
    .write(rule)

open('resultant/gfw.list', 'w', encoding='utf-8') \
    .write('\n'.join(rules))

open('resultant/gfw_bypass.list', 'w', encoding='utf-8') \
    .write('\n'.join(rules_bypass))

open('resultant/gfw_unhandle.log', 'w', encoding='utf-8') \
    .write('\n'.join(unhandle_rules))

open('resultant/gfw_unhandle_bypass.log', 'w', encoding='utf-8') \
    .write('\n'.join(unhandle_rules_bypass))
