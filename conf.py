# -*- coding: utf-8 -*-
"""博客构建配置文件
"""

# For Maverick
#site_prefix = "/Blog-With-GitHub-Boilerplate/"
site_prefix = "/"
source_dir = "../src/"
build_dir = "../dist/"
index_page_size = 10
archives_page_size = 20
template = {
    "name": "Galileo",
    "type": "local",
    "path": "../Galileo"
}
enable_jsdelivr = {
    "enabled": TRUE,
    "repo": "Kanshan28/Blog@gh-pages"
}

# 站点设置
site_name = "刘看山的博客"
site_logo = "${static_prefix}logo.png"
#site_build_date = "2019-12-18T16:51+08:00"
site_build_date = "2020-04-29T17:40+08:00"
author = "刘看山"
email = "kansha_liu@foxmail.com"
author_homepage = "https://www.liukanhsan.club"
description = "TALK IS CHEAP , SHOW ME CODE !"
key_words = ['Maverick', '刘看山', 'Galileo', 'blog']
language = 'zh-CN'
external_links = [
    {
        "name": "Github",
        "url": "https://github.com/Kanshan28",
        "brief": "🏄‍ Go My Own Way."
    },
    {
        "name": "刘看山",
        "url": "https://www.liukanshan.club",
        "brief": "刘看山的主页。"
    }
]
nav = [
    {
        "name": "首页",
        "url": "${site_prefix}",
        "target": "_self"
    },
    {
        "name": "归档",
        "url": "${site_prefix}archives/",
        "target": "_self"
    },
    {
        "name": "关于",
        "url": "${site_prefix}about/",
        "target": "_self"
    }
]

social_links = [
    {
        "name": "GitHub",
        "url": "https://github.com/Kanshan28",
        "icon": "gi gi-github"
    },
    {
        "name": "Weibo",
        "url": "https://weibo.com/5366743913/",
        "icon": "gi gi-weibo"
    }
]

head_addon = r'''
<meta http-equiv="x-dns-prefetch-control" content="on">
<link rel="dns-prefetch" href="//cdn.jsdelivr.net" />
'''

footer_addon = ''

body_addon = ''
