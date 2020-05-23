---
layout: post
title: 用Pyhton实现的高可用IP代理池
slug: 2020-05-09-Proxy_Pool
date: 2020-5-9 20:10
status: publish
author: Kanshan
categories: 
  - Python
tags:
  - Proxy Pool
excerpt: 这是一个Python代理池的项目。
---

#### 1.代理池概述

##### 1.1什么是代理池

- 代理池就是代理Ip组成的池子，它可以提供稳定可用的代理IP

##### 1.2为什么要实现代理池

- 我们在做爬虫的时候，最常见的一种反爬手段，就是IP反爬，常见的解决方法就是用代理IP方案
- 代理IP非常不稳定，可用性10%可能都不到
- 从一堆不稳定的代理IP中抽取出可用代理IP，给爬虫使用。

##### 1.3代理池开发环境

- 平台：MAC,Windows,Linux

- 开发语言：Python3

- 开发工具：PyCharm

- 使用到的主要技术：

  - requests：发送请求，获取页面数据
  - lxml：使用XPATH从页面回去我们想要的数据
  - pymongo：把提取到的代理IP存储到MongoDB数据库中和从MongoDB数据库中读取代理IP给爬虫使用
  - Flask：用于提供WEB服务

  #### 

#### 2.代理池的设计

- 目标：理解代理池的工作流程和各个模块的作用
- 内容介绍
  - 代理池的工作流程
  - 代理池的模块及其作用
  - 代理池的项目结构

##### 2.1代理池的工作流程

![代理池的工作流程](.\images\2020-5-9-1.png)



- 代理池工作流程文字描述
  - 代理IP采集模块-->采集代理IP -->如果不可用，直接过滤掉，如果可用，制定默认分数-->存入数据库
  - 代理IP检测模块-->从数据库中获取所有代理IP-->检测代理IP-->如果代理IP不可用，就把分数-1，如果的分数为0，就从数据库中删除，否则更新数据库；如果代理IP可用，则恢复为默认分值，更新数据库。
  - 代理API模块-->数据库中高可用的代理IP给爬虫使用

##### 2.2 代理模块及其作用

- 代理池分为5大核心模块
  - 爬虫模块：采集代理IP
    - 从代理IP网站上采集代理IP
    - 进行校验（获取代理响应速度，协议类型，匿名类型）
    - 把可用的代理IP存储到数据库中
  - 代理IP的检验模块：获取指定代理的响应速度，支持的协议以及匿名程度
    - 原因：网站上所标注的响应速度，协议类型是不准确的
    - 这里使用httpbin.org进行检测
  - 数据库模块：实现对代理IP的增删改查操作
    - 这里使用MongoDB来存储代理IP
  - 检测模块：定时对代理池中代理进行检测，确保代理池中代理的可用性
    -   从数据库读取所有的代理IP
    - 对代理IP进行逐一检测，可用开启多个协程，以提高检测速度
    - 如果该代理不可用，就让这个代理分数-1，当代理的分数到0了，就删除该代理，如果检测到代理可用就恢复为满分
  - 代理IP服务接口：提供高可用代理IP给爬虫使用
    - 根据协议类型和域名获取随机的高质量代理IP
    - 根据协议类型和域名获取多个高质量代理IP
    - 根据代理IP，不可用域名，告诉代理池这个代理IP在该域名下不可用，下次获取这个域名时就不会再用这个代理IP了，从而保证代理IP的高可用
  - 其他模块
    - 数据模型：domain.py
      - 代理IP的数据模型，用于封装代理IP的相关信息，如ip,端口，响应速度，协议类型，匿名类型，分数等。
    - 程序启动入口：main.py
      - 代理池提供一个统一的启动入口
    - 工具模块
      - 日志模块：用于记录日志信息
      - http模块：用于获取随机User-Agent的请求头
    - 配置文件：setting
      - 用于默认代理的分数，配置日志格式，文件，启动的爬虫，检验的时间等



##### 2.3 代理池的项目结构

![代理池的项目结构](.\images\2020-5-9-2.png)



#### 3.实现代理池的思路

- 目标：明确代理池实现思路
- 步骤：
  - 介绍实现项目的两种思路
  - 对比两种实现思路
  - 明确代理池采用实现思路

##### 实现项目的两种思路

- 思路1：
  - 依据项目的设计流程图，一步一步进行实现
  - 遇到需要依赖于其他模块的地方，就暂停当前的模块，去实现其他模块中需要使用的功能
  - 其他模块实现后，再回来接着写当前的模块
- 思路2：
  - 先实现基础模块，这些模块不依赖于其他的模块，比如这里的：数据模型，数据库模块
  - 然后实现具体得功能模块，比如爬虫模块，检测模块，代理API模块
- 对比：
  - 思路1：按照流程一步步实现，适合一个人完成项目，流程清晰，但是不适合分工合作
  - 思路2：把项目拆分为多个相对独立的模块，每一个人实现一个模块，适合分工合作；实现项目也会更加流畅，不会有跳来跳去的现象，对最初设计要求比较高，要提前设计好后面需要用到的接口
- 代理池项目采用的实现思路
  - 这里采用 思路2来进行实现



#### 4.定义代理IP的数据模型类

- 目标：定义代理IP的数据模型类

- 步骤：
  - 定义`Proxy`类，继承object
  - 实现`__init__`方法，负责初始化，包含如下字段：
    - ip：代理的IP地址
    - port：代理IP的端口号
    - protocol：代理IP支持的协议类型，http是0，https是1，https和http都支持是2
    - nick_type：代理IP的匿名程度，高匿：0，匿名：1，透明：2
    - speed：代理IP的响应速度，单位s
    - area：代理IP所在的地区
    - score：代理IP的评分，用于衡量代理的可用性，默认分之可以通过配置文件进行配置，在进行代理可用性检查的时候，每遇到一次请求失败就减1分，减到0的时候就从池子中删除，如果检查代理可用，就恢复默认分值。
    - disable_domains：不可用域名列表，有些代理IP在某些域名下不可用，但是在其他域名下可用
  - 配置文件：`settings.py` 中定义MAX_SCORE=50，表示代理IP的默认最高分数
  - 提供`__str__`方法，返回数据字符串
  
- 代码：

  ```python
  # -*- coding:utf-8 -*-
  #domin.py
  
  from settings import MAX_SCORE
  """
  4.定义代理IP的数据模型类
  目标：定义代理IP的数据模型类
  步骤：
  
  1.定义Proxy类，继承object
  2.实现__init__方法，负责初始化，包含如下字段：
      ip：代理的IP地址
      port：代理IP的端口号
      protocol：代理IP支持的协议类型，http是0，https是1，https和http都支持是2
      nick_type：代理IP的匿名程度，高匿：0，匿名：1，透明：2
      speed：代理IP的响应速度，单位s
      area：代理IP所在的地区
      score：代理IP的评分，用于衡量代理的可用性，默认分之可以通过配置文件进行配置，在进行代理可用性检查的时候，每遇到一次请求失败就减1分，减到0的时候就从池子中删除，如果检查代理可用，就恢复默认分值。
      disable_domains：不可用域名列表，有些代理IP在某些域名下不可用，但是在其他域名下可用
      配置文件：`settings.py` 中定义MAX_SCORE=50，表示代理IP的默认最高分数
  3.提供__str__方法，返回数据字符串
  
  """
  
  class Proxy(object):
  
      def __init__(self, ip, port, protocol=-1, nick_type=-1, speed=-1, area=None, score=MAX_SCORE, disable_domain=[]):
          # ip：代理的IP地址
          self.ip = ip
          # port：代理IP的端口号
          self.port = port
        # protocol：代理IP支持的协议类型，http是0，https是1，https和http都支持是2
          self.protocol = protocol
        # nick_type：代理IP的匿名程度，高匿：0，匿名：1，透明：2
          self.nick_type = nick_type
          # speed：代理IP的响应速度，单位s
          self.speed = speed
          # area：代理IP所在的地区
          self.area = area
          # score：代理IP的评分，用于衡量代理的可用性，默认分之可以通过配置文件进行配置，在进行代理可用性检查的时候，每遇到一次请求失败就减1分，减到0的时候就从池子中删除，如果检查代理可用，就恢复默认分值。
          self.score = score
          # disable_domains：不可用域名列表，有些代理IP在某些域名下不可用，但是在其他域名下
          self.disable_domain = disable_domain
          # 配置文件：settings.py中定义MAX_SCORE = 50，表示代理IP的默认最高分数
  
      # 3.提供__str__方法，返回数据字符串
      def __str__(self):
          #返回数据字符串
          return str(self.__dict__)
  
  ```
  
  ```python
  #settings.py
  
  # 配置文件：settings.py中定义MAX_SCORE = 50，表示代理IP的默认最高分数MAX_SCORE = 50
  ```

#### 5.实现代理池工具模块

- 步骤
  - 实现日志模块
  - http模块 

##### 5.1实现日志模块

###### 5.1.1.为什么要实现日志模块

- 能够方便的对进程进行调试
- 能够方便记录程序的运行状态
- 能够记录错误信息

###### 5.1.2.日志模块的实现

- 目标：实现日志模块，用于记录日志
- 前提：日志模块在网上有很多现成的实现，我们开发的时候，通常不会自己写，而是拿来主义。
- 步骤：

- 拷贝笔记日志代码到项目中

```python
#utils/log.py
import sys
import logging

#默认的配置
DEFAULT_LOG_LEVEL = logging.INFO   # 默认等级
DEFAULT_LOG_FMT = '%(asctime)s %(filename)s [line:%(lineno)d] %(levelname)s: %(message)s'  # 默认日志格式
DEFUALT_LOG_DATEFMT = '%Y-%m-%d %H:%M:%S'  # 默认时间格式
DEFAULT_LOG_FILENAME = 'log.log'  # 默认日志文件名称

class Logger(object):

    def __init__(self):
        # 1. 获取一个logger对象
        self._logger = logging.getLogger()
        # 2. 设置format对象
        self.formatter = logging.Formatter(fmt=DEFAULT_LOG_FMT,datefmt=DEFUALT_LOG_DATEFMT)
        # 3. 设置日志输出
        # 3.1 设置文件日志模式
        self._logger.addHandler(self._get_file_handler(DEFAULT_LOG_FILENAME))
        # 3.2 设置终端日志模式self._logger.addHandler(self._get_console_handler())
        # 4. 设置日志等级
        self._logger.setLevel(DEFAULT_LOG_LEVEL)

    def _get_file_handler(self, filename):
        '''返回一个文件日志handler'''
        # 1. 获取一个文件日志handler
        filehandler = logging.FileHandler(filename=filename,encoding="utf-8")
        # 2. 设置日志格式
        filehandler.setFormatter(self.formatter)
        # 3. 返回
        return filehandler
    def _get_console_handler(self):
        '''返回一个输出到终端日志handler'''
        # 1. 获取一个输出到终端日志handler
        console_handler = logging.StreamHandler(sys.stdout)
        # 2. 设置日志格式
        console_handler.setFormatter(self.formatter)
        # 3. 返回handler
        return console_handler

    @property

    def logger(self):
        return self._logger
# 初始化并配一个logger对象，达到单例的
# 使用时，直接导入logger就可以使用
logger = Logger().logger

if __name__ == '__main__':
    logger.debug("调试信息")
    logger.info("状态信息")
    logger.warning("警告信息")
    logger.error("错误信息")
    logger.critical("严重错误信息")
```

- 把日志相关配置信息放到配置文件中

```python
#settings.py
MAX_SCORE = 50

#日志的配置信息
import logging

#默认的配置
DEFAULT_LOG_LEVEL = logging.INFO   # 默认等级
DEFAULT_LOG_FMT = '%(asctime)s %(filename)s [line:%(lineno)d] %(levelname)s: %(message)s'  # 默认日志格式
DEFUALT_LOG_DATEFMT = '%Y-%m-%d %H:%M:%S'  # 默认时间格式
DEFAULT_LOG_FILENAME = 'log.log'  # 默认日志文件名称

```

- 修改日志代码，使用配置文件中的配置信息

```python 
import sys
import logging

#导入settingss中日志配置信息
from settings import DEFAULT_LOG_FMT, DEFUALT_LOG_DATEFMT, DEFAULT_LOG_FILENAME, DEFAULT_LOG_LEVEL
```



##### 5.2. http模块

我们从代理IP网站上抓取代理IP和检验代理IP的时候，为了不容易被服务器识别为一个爬虫，我们最好提供随机的User-Agent请求头。

- 目标：获取随机User-Agent的请求头
- 步骤：
  - 准备User-Agent的列表
  - 实现一个方法，获取随机User-Agent的请求头
- 代码：

```python
#-*- coding:utf-8 -*-
import random
"""
5.2. http模块

我们从代理IP网站上抓取代理IP和检验代理IP的时候，为了不容易被服务器识别为一个爬虫，我们最好提供随机的User-Agent请求头。

目标：获取随机User-Agent的请求头
步骤：
    1.准备User-Agent的列表
    2.实现一个方法，获取随机User-Agent的请求头
"""

#1.准备User-Agent列表
USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
    "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:38.0) Gecko/20100101 Firefox/38.0",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E; .NET CLR 2.0.50727; .NET CLR 3.0.30729; .NET CLR 3.5.30729; InfoPath.3; rv:11.0) like Gecko",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)",
    "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
    "Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11",
    "Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Maxthon 2.0)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; TencentTraveler 4.0)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; The World)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Avant Browser)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)",
    "Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5",
    "Mozilla/5.0 (iPod; U; CPU iPhone OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5",
    "Mozilla/5.0 (iPad; U; CPU OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5",
    "Mozilla/5.0 (Linux; U; Android 2.3.7; en-us; Nexus One Build/FRF91) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
    "MQQBrowser/26 Mozilla/5.0 (Linux; U; Android 2.3.7; zh-cn; MB200 Build/GRJ22; CyanogenMod-7) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
    "Opera/9.80 (Android 2.3.4; Linux; Opera Mobi/build-1107180945; U; en-GB) Presto/2.8.149 Version/11.10",
    "Mozilla/5.0 (Linux; U; Android 3.0; en-us; Xoom Build/HRI39) AppleWebKit/534.13 (KHTML, like Gecko) Version/4.0 Safari/534.13",
    "Mozilla/5.0 (BlackBerry; U; BlackBerry 9800; en) AppleWebKit/534.1+ (KHTML, like Gecko) Version/6.0.0.337 Mobile Safari/534.1+",
    "Mozilla/5.0 (hp-tablet; Linux; hpwOS/3.0.0; U; en-US) AppleWebKit/534.6 (KHTML, like Gecko) wOSBrowser/233.70 Safari/534.6 TouchPad/1.0",
    "Mozilla/5.0 (SymbianOS/9.4; Series60/5.0 NokiaN97-1/20.0.019; Profile/MIDP-2.1 Configuration/CLDC-1.1) AppleWebKit/525 (KHTML, like Gecko) BrowserNG/7.1.18124",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows Phone OS 7.5; Trident/5.0; IEMobile/9.0; HTC; Titan)",
    "UCWEB7.0.2.37/28/999",
    "NOKIA5700/ UCWEB7.0.2.37/28/999",
    "Openwave/ UCWEB7.0.2.37/28/999",
    "Mozilla/4.0 (compatible; MSIE 6.0; ) Opera/UCWEB7.0.2.37/28/999",
    # iPhone 6：
    "Mozilla/6.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/8.0 Mobile/10A5376e Safari/8536.25",
]


#2.实现一个方法，获取随机User-Agent的请求头
def get_request_headers():
    headers = {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Accept-language': 'zh-CN,zh;q=0.9',
        'Accept-Encoding': 'gzip, deflate,br',
        'Connection': 'keep-alive',
    }
    return headers


if __name__ == '__main__':
    # 测试随机与否
    print(get_request_headers())
    print(get_request_headers())
```



#### 6.实现代理池的校验模块

- 目标：检验代理IP速度，匿名程度以及支持的协议类型
- 步骤：
  - 代理IP速度，就是从发送请求到获取响应的时间间隔
  - 检验代理IP速度和匿名程度：
    - 匿名程度检查：
      - 对http://httpbin.org/get  或 https://httpbin.org/get 发送请求
      - 如果响应origin中有',' 分割的两个IP就是透明代理IP
      - 如果响应的headers中包含Proxy-Connection 说明是匿名代理IP
      - 否则就是高匿名IP
  - 检查代理IP协议类型
    - 如果 http://httpbin.org/get 发送请求可以成功，说明支持http协议
    - 如果 https://httpbin.org/get 发送请求可以成功，说明支持https协议
- 代码 

```python
#httpbin_validator.py
"""
6.实现代理池的校验模块
目标：检验代理IP速度，匿名程度以及支持的协议类型
步骤：

检验代理IP速度和匿名程度：
    1.代理IP速度，就是从发送请求到获取响应的时间间隔
    2.匿名程度检查：
        1.对http://httpbin.org/get  或 https://httpbin.org/get 发送请求
        2.如果响应origin中有',' 分割的两个IP就是透明代理IP
        3.如果响应的headers中包含Proxy-Connection 说明是匿名代理IP
        4.否则就是高匿名IP
检查代理IP协议类型
    如果 http://httpbin.org/get 发送请求可以成功，说明支持http协议
    如果 https://httpbin.org/get 发送请求可以成功，说明支持https协议

"""
import json
import time
import requests

from domain import Proxy
from utils.http import get_request_headers
from settings import TEST_TIMEOUT
from utils.log import logger

def check_proxy(proxy):
    """
    用于检查指定 代理IP  响应速度  匿名程度  支持协议类型
    :param proxy:代理IP模型对象
    :return:检查后的代理IP模型对象
    """

    #准备代理IP字典
    proxies = {
        'http': "http://{}:{}".format(proxy.ip, proxy.port),
        'https': 'https://{}:{}".format(proxy.ip, proxy.port),
    }

    #测试该代理IP
    http, http_nick_type, http_speed = __check_http_proxies(proxies)
    https, https_nick_type, https_speed = __check_http_proxies(proxies, False)

    #代理IP支持的协议类型，http是0， https是1， http和https都支持是2
    if http and https:
        proxy.protocol = 2
        proxy.nick_type = http_nick_type
        proxy.speed = http_speed
    elif http:
        proxy.protocol = 0
        proxy.nick_type = http_nick_type
        proxy.speed = http_speed
    elif https:
        proxy.protocol = 1
        proxy.nick_type = https_nick_type
        proxy.speed = https_speed
    else:
        proxy.protocol = -1
        proxy.nick_type = -1
        proxy.speed = -1
    return proxy


def __check_http_proxies(proxies, is_http=True):
    #匿名类型： 高匿：0， 匿名：1， 透明：2
    nick_type = -1
    #响应速度，单位s
    speed = -1

    if is_http:
        test_url = 'http://httpbin.org/get'
    else:
        test_url = 'https://httpbin.org/get'

    try:
        #获取开始时间
        start = time.time()
        #发送请求，获取响应速度
        response = requests.get(test_url, headers=get_request_headers(), proxies=proxies, timeout=TEST_TIMEOUT)

        if response.ok:
            #计算响应速度
            speed = round(time.time() - start, 2)
            #匿名程度
            #把响应的json字符串转换成字典
            dic = json.loads(response.text)
            #获取来源IP:origin
            origin = dic['origin']
            proxy_connection = dic['headers'].get('Proxy-Connection', None)
            # 1.如果响应origin中有',' 分割的两个IP就是透明代理IP
            if ',' in origin:
                nick_type = 2
            # 2.如果响应的headers中包含Proxy-Connection 说明是匿名代理IP
            elif proxy_connection:
                nick_type = 1
            # 3.否则就是高匿名IP
            else:
                nick_type = 0
            return True, nick_type, speed
        return False, nick_type, speed
    except Exception as ex:
        #logger.exception(ex)
        return False, nick_type, speed

#测试是否可用

if __name__ == '__main__':
    proxy = Proxy('45.76.162.126', port='8080')
    print(check_proxy(proxy))
```

```pyhton
#settings.py
#测试代理IP的超时时间
TEST_TIMEOUT = 10
```



#### 7.实现代理池的数据库模块

- 作用：用于对proxies集合进行数据库的相关 操作
- 目标：实现对数据库增删改查相关操作
- 步骤：
  - 在`__init__`中，建立数据连接，获取要操作的集合，在`__del__`方法中关闭数据库连接
  
  - 提供基础的增删改查功能
    - 实现插入功能
    - 实现修改功能
    - 实现删除代理：根据代理的IP删除代理
    - 查询所有代理IP的功能
- 提供代理API模块使用的功能
  - 实现查询功能：根据条件进行查询 ，可以指定查询数量，先分数降序，速度升序，保证优质的代理IP在上面
  - 实现根据协议类型和要访问网站的域名，获取代理IP列表
  - 实现根据协议类型和要访问完整的域名，随机获取一个代理IP
  - 实现把指定域名添加到指定IP的disable_domain列表中
- 代码：

```python
# -*- coding:utf-8 -*-
#mongo_pool.py
"""
7.实现代理池的数据库模块
作用：用于对proxies集合进行数据库的相关操作
目标：实现对数据库增删改查相关操作
步骤：
   1.在init中，建立数据连接，获取要操作的集合，在del方法中关闭数据库连接
   2.提供基础的增删改查功能
        2.1实现插入功能
        2.2实现修改功能
        2.3实现删除代理：根据代理的IP删除代理
        2.4查询所有代理IP的功能
   3.提供代理API模块使用的功能
        3.1实现查询功能：根据条件进行查询 ，可以指定查询数量，先分数降序，速度升序，保证优质的代理IP在上面
        3.2实现根据协议类型和要访问网站的域名，获取代理IP列表
        3.3实现根据协议类型和要访问完整的域名，随机获取一个代理IP
        3.4实现把指定域名添加到指定IP的disable_domain列表中

"""
import random

from pymongo import MongoClient  #http://www.imooc.com/article/43478  使用方法
from settings import MONGO_URL  #https://juejin.im/post/5d525b1af265da03b31bc2d5
from utils.log import logger
from domain import Proxy
import pymongo


class MongoPool(object):

    def __init__(self):
        #1.在 int中，建立数据连接，获取要操作的集合
        self.client = MongoClient(MONGO_URL)
        #获取要操作的集合
        self.proxies = self.client['proxies_pool']['proxies']

    def __del__(self):
        #关闭数据库连接
        self.client.close()

    def insert_one(self, proxy):
        """2.1实现插入功能"""

        count = self.proxies.count_documents({'_id':proxy.ip})
        if count == 0:
            #我们使用proxy.ip作为MongoDB的主键： _id
            dic = proxy.__dict__
            dic['_id'] = proxy.ip
            self.proxies.insert_one(dic)
            logger.info("插入新的代理：{}".format(proxy))
        else:
            logger.warning("已存在的代理：{}".format(proxy))

    def update_one(self, proxy):
        """2.2实现修改功能"""
        self.proxies.update_one({'_id': proxy.ip}, {'$set': proxy.__dict__})
        logger.warning("代理更新：{}".format(proxy))

    def delete_one(self, proxy):
        """2.3实现删除代理，根据代理的IP删除代理"""
        self.proxies.delete_one({'_id':proxy.ip})
        logger.info("删除代理IP:{}".format(proxy))

    def find_all(self):
        """2.4查询所有代理IP的功能"""
        cursor = self.proxies.find()
        for item in cursor:
            #删除_id这个key
            item.pop('_id')
            proxy = Proxy(**item)
            yield proxy

    def find(self, conditions={}, count=0):
        """
        3.1实现查询功能：根据条件进行查询 ，可以指定查询数量，先分数降序，速度升序，保证优质的代理IP在上面
        :param conditions:查询条件字典
        :param count:限制最多取出多少个代理IP
        :return:返回满足要求的代理IP（Proxy）列表
        """
        cursor = self.proxies.find(conditions, limit=count).sort(
            [('score', pymongo.DESCENDING),('speed', pymongo.ASCENDING)]
        )

        #准备列表，用于存储查询处理代理IP
        proxy_list = []
        #遍历 cursor
        for item in cursor:
            item.pop('_id')
            proxy = Proxy(**item)
            proxy_list.append(proxy)
        return proxy_list

    #返回满足要求代理IP(Proxy对象）列表
    def get_proxies(self, protocol=None, domain=None, count=0, nick_type=0):
        """
        3.2 实现根据协议类型和要访问网页的域名，获取代理IP列表
        :param protocol:协议：http,https
        :param domain:域名：jd.com
        :param count:用于限制获取多少个代理IP,默认是获取所有的
        :param nick_type:匿名类型，默认，获取高匿的代理IP
        :return:满足要求的代理IP列表
        """

        #定义查询条件
        conditions = {'nick_type': nick_type}
        #根据协议，指定查询条件
        if protocol is None:
            #如果没有传入协议类型，返回支持http和https的代理IP
            conditions['protocol'] = 2
        elif protocol.lower() == 'http':
            conditions['protocol'] = {'$in': [0, 2]}
        else:
            conditions['protocol'] = {'$in': [1, 2]}

        if domain:
            conditions['disable_domain'] = {'$nin': [domain]}
        #满足要求的代理IP列表
        return self.find(conditions, count=count)

    def random_proxy(self, protocol=None, domain=None, count=0, nick_type=0):
        """
        #3.3实现根据协议类型和要访问完整的域名，随机获取一个代理IP
        :param protocol:协议：http,https
        :param domain:域名：jd.com
        :param count:用于限制获取多少个代理IP,默认是获取所有的
        :param nick_type:匿名类型，默认，获取高匿的代理IP
        :return:返回满足要求的的一个代理IP(Proxy对象）
        """
        proxy_list = self.get_proxies(protocol=protocol, domain=domain, count=count, nick_type=nick_type)
        #从Proxy_list列表中，随机选出一个代理IP返回
        return random.choice(proxy_list)

    def disable_domain(self, ip, domain):
        """
        #3.4实现把指定域名添加到指定IP的disable_domain列表中
        :param ip: IP地址
        :param domain: 域名
        :return: 如果返回True,就表示添加成功，返回False，表示添加失败
        """

        if self.proxies.count_documents({'_id':ip, 'disable_domain':domain}) == 0:
            #如果disable_domains字段中，没有这个域名才添加
            self.proxies.update_one({'_id':ip}, {'$push': {'disable_domain':domain}})
            return True
        else:
            return False

#测试是否可用
if __name__ == '__main__':
    mongo = MongoPool()

    #proxy = Proxy('202.104.113.36', port='53281')
    #mongo.inser_one(proxy)
    # mongo.update_one(proxy)
    #mongo.delete_one(proxy)
    #for proxy in mongo.find_all():
     #   print(proxy)

    #dic = {'ip': '202.104.113.46', 'port': '53281', 'protocol': 2, 'nick_type': 1, 'speed': 3, 'area': None, 'score': 40,'disable_domain': ['taobao.com']}
    #proxy = Proxy(**dic)
    #mongo.inser_one(proxy)

    #for proxy in mongo.find({'protocol':0}, count=1):
    #    print(proxy)
    #for proxy in mongo.get_proxies(domain='taobao.com', nick_type=1):
    #    print(proxy)
    #mongo.disable_domain('202.104.113.46', 'ali.com')
```



```python
#settings.py
#MongoDB数据库的URL
MONGO_URL = 'mongodb://127.0.0.1:27017'
```



#### 8.实现代理池的爬虫模块

##### 8.1爬虫模块的需求

- 需求：抓取各个代理IP网站上的免费代理IP,进行检测，如果可用，存储到数据库中
- 需要抓取代理IP的页面如下：
  - [西刺代理](https://www.xicidaili.com/nn/1)：https://www.xicidaili.com/nn/1
  - [ip3366代理](http://www.ip3366.net/free/?stype=1&page=1)： http://www.ip3366.net/free/?stype=1&page=1 
  - [快代理](https://www.kuaidaili.com/free/inha/1/)： https://www.kuaidaili.com/free/inha/1/ 
  - [proxylistplus代理](https://list.proxylistplus.com/Fresh-HTTP-Proxy-List-1)： https://list.proxylistplus.com/Fresh-HTTP-Proxy-List-1 

##### 8.2 爬虫模块的设计思路

- 通用爬虫：通过指定URL列表，分组XPATH和组内XPATH,来提取不同网站的代理IP
  - 原因：代理IP网站的结构几乎是Table，页面结构类似
- 具体爬虫：用于抓取集体代理IP网站
  - 通过继承通用爬虫实现网站的抓取吗，一般只需要指定爬虫的URL列表，分组的XPATH，组内的XPATH就可以了。
  - 如果该网站有特殊反爬手段，可以通过重写某些方法实现反爬
- 爬虫运行模块：启动爬虫，抓取代理IP，如果可用，就存储到数据库中；
  -  通过配置文件来控制启动哪些爬虫，增加扩展性；如果将来我们遇到返回json格式的代理，单独写一个爬虫配置就好了。

##### 8.3实现通用爬虫

- 目标：实现一个可以通过指定不同URL列表，分组的XPATH和详情的XPATH,从不同页面上提取代理的Ip、端口号和区域的通用爬虫；
- 步骤：
  1. 在base_spider.py 文件中，定义一个BaseSpider类，继承object
  2. 提供三个类成员变量：
     1. urls:代理IP网址的URL列表
     2. group_xpath：分组XPATH，获取包含代理IP信息标签列表的XPATH
     3. detail_xpath：组内XPATH,获取代理IP详情的信息XPATH，格式为: {'ip':'xx', 'port':'xx', 'area':'xx'}
  3. 提供初始方法，传入爬虫URL列表，分组XPATH，详情（组内）XPATRH
  4. 对外提供一个获取代理IP的方法
     1. 遍历URL列表，获取URL
     2. 根据发送请求，获取页面数据
     3. 解析页面，提取数据，封装为Proxy对象
     4. 返回Proxy对象列表

```python
#base_spider.py
"""
8.3实现通用爬虫
目标：实现一个可以通过指定不同URL列表，分组的XPATH和详情的XPATH,从不同页面上提取代理的Ip、端口号和区域的通用爬虫；
步骤：
  1. 在base_spider.py 文件中，定义一个BaseSpider类，继承object
  2. 提供三个类成员变量：
     2.1. urls:代理IP网址的URL列表
     2.2. group_xpath：分组XPATH，获取包含代理IP信息标签列表的XPATH
     2.3. detail_xpath：组内XPATH,获取代理IP详情的信息XPATH，格式为: {'ip':'xx', 'port':'xx', 'area':'xx'}
  3. 提供初始方法，传入爬虫URL列表，分组XPATH，详情（组内）XPATRH
  4. 对外提供一个获取代理IP的方法
     4.1. 遍历URL列表，获取URL
     4.2. 根据发送请求，获取页面数据
     4.3. 解析页面，提取数据，封装为Proxy对象
     4.4. 返回Proxy对象列表

"""
#1. 在base_spider.py 文件中，定义一个BaseSpider类，继承object
import requests
from utils.http import get_request_headers
from lxml import etree
from domain import Proxy


class BaseSpider(object):
    #2. 提供三个类成员变量：
    #2.1. urls:代理IP网址的URL列表
    urls = []
    #2.2. group_xpath：分组XPATH，获取包含代理IP信息标签列表的XPATH
    group_xpath = ''
    #2.3. detail_xpath：组内XPATH,获取代理IP详情的信息XPATH，格式为: {'ip':'xx', 'port':'xx', 'area':'xx'}
    detail_xpath = {}

    #3. 提供初始方法，传入爬虫URL列表，分组XPATH，详情（组内）XPATRH
    def __init__(self, urls=[], group_xpath='', detail_xpath={}):
        if urls:
            self.urls = urls
        if group_xpath:
            self.group_xpath = group_xpath
        if detail_xpath:
            self.detail_xpath = detail_xpath

    def get_page_from_url(self, url):
        """根据url发送请求，获取页面数据"""
        response = requests.get(url, headers=get_request_headers())
        return response.content

    def get_first_from_list(self, lis):
        #如果列表中有元素就返回第一个，否则返回空串
        return lis[0] if len(lis) != 0 else ''

    def get_proxies_from_page(self, page):
        """解析页面，提取数据，封装为Proxy对象"""
        element = etree.HTML(page)
        #获取包含代理IP信息的标签列表
        trs = element.xpath(self.group_xpath)
        #遍历trs，获取代理IP相关信息
        for tr in trs:
            # ip = tr.xpath(self.detail_xpath['ip'])[0]
            # port = tr.xpath(self.detail_xpath['port'])[0]
            # area = tr.xpath(self.detail_xpath['area'])[0]
            ip = self.get_first_from_list(tr.xpath(self.detail_xpath['ip']))
            port = self.get_first_from_list(tr.xpath(self.detail_xpath['port']))
            area = self.get_first_from_list(tr.xpath(self.detail_xpath['area']))
            proxy = Proxy(ip, port, area=area)
            #使用yield返回提取到的数据
            yield proxy

    def get_proxies(self):
        # 4.对外提供一个获取代理IP的方法
        # 4.1.遍历URL列表，获取URL
        for url in self.urls:
            print("获取URl{}".format(url))
            # 4.2.根据发送请求，获取页面数据
            page = self.get_page_from_url(url)
            # 4.3.解析页面，提取数据，封装为Proxy对象
            proxies = self.get_proxies_from_page(page)
            # 4.4.返回Proxy对象列表
            yield from proxies

# 测试
# if __name__ == '__main__':
#     config = {
#         'urls': ['http://www.ip3366.net/free/?stype=1&page={}'.format(i) for i in range(1,4)],
#         'group_xpath': '//*[@id="list"]/table/tbody/tr',
#         'detail_xpath':{
#             'ip': './td[1]/text()',
#             'port': './td[2]/text()',
#             'area' : './td[5]/text()'
#         }
#     }
#     spider = BaseSpider(**config)
#     for proxy in spider.get_proxies():
#         print(proxy)


```

##### 8.4 实现具体的爬虫类

- 目标：通过继承通用爬虫，实现多个具体爬虫，分别从各个免费代理IP网站上抓取代理IP

- 目标：

  1. 实现 [西刺代理](https://www.xicidaili.com/nn/1) 爬虫： https://www.xicidaili.com/nn/1
     - 定义一个类，继承通用爬虫类（BasicSpider）
     - 提供urls, group_xpath和detail_xpath
  2. 实现 [ip3366代理](http://www.ip3366.net/free/?stype=1&page=1) 爬虫：http://www.ip3366.net/free/?stype=1&page=1 
     - 定义一个类，继承通用爬虫类（BasicSpider）
     - 提供urls, group_xpath和detail_xpath
  3. 实现[快代理](https://www.kuaidaili.com/free/inha/1/) 爬虫： https://www.kuaidaili.com/free/inha/1/ 
     - 定义一个类，继承通用爬虫类（BasicSpider）
     - 提供urls, group_xpath和detail_xpath
  4. 实现[proxylistplus代理](https://list.proxylistplus.com/Fresh-HTTP-Proxy-List-1) 爬虫： https://list.proxylistplus.com/Fresh-HTTP-Proxy-List-1 
     - 定义一个类，继承通用爬虫类（BasicSpider）
     - 提供urls, group_xpath和detail_xpath
  5. 实现 [66ip](http://www/66ip.cn/1.html) 爬虫： http://www/66ip.cn/1.html
     - 定义一个类，继承通用爬虫类（BasicSpider）
     - 提供urls, group_xpath和detail_xpath
     - 由于66ip网页进行js +cookie 反爬，需要重写父类的get_page_from_url方法

  ```python
  #proxy_spider.py
  
  """
  1. 实现 [西刺代理] 爬虫： https://www.xicidaili.com/nn/1
     定义一个类，继承通用爬虫类（BasicSpider）
     提供urls, group_xpath和detail_xpath
  """
  
  from core.proxy_spider.base_spider import BaseSpider
  import time
  import random
  
  class XiciSpider(BaseSpider):
  
      #准备URL 列表
      urls = ['https://www.xicidaili.com/nn/{}'.format(i) for i in range(1, 11)]
      #分组的XPATH，用于获取包含代理IP信息的标签列表
      group_xpath = '//*[@id="ip_list"]/tr[position()>1]'
      #组内的XPATH,用于提取 ip,port,area
      detail_xpath = {
          'ip': './td[2]/text()',
          'port': './td[3]/text()',
          'area': './td[4]/a/text()'
      }
  
  """
  实现 [ip3366代理] 爬虫：http://www.ip3366.net/free/?stype=1&page=1 
  
  - 定义一个类，继承通用爬虫类（BasicSpider）
  - 提供urls, group_xpath和detail_xpath
  """
  
  class Ip3366Spider(BaseSpider):
  
      #准备URL 列表
      urls = ['http://www.ip3366.net/free/?stype={}&page={}'.format(i, j) for i in range(1, 5) for j in range(1, 8)]
      #分组的XPATH，用于获取包含代理IP信息的标签列表
      group_xpath = '//*[@id="list"]/table/tbody/tr'
      #组内的XPATH,用于提取 ip,port,area
      detail_xpath = {
          'ip': './td[1]/text()',
          'port': './td[2]/text()',
          'area': './td[5]/text()'
      }
  
  """
  3.实现[快代理] 爬虫： https://www.kuaidaili.com/free/inha/1/ 
  
  - 定义一个类，继承通用爬虫类（BasicSpider）
  - 提供urls, group_xpath和detail_xpath
  """
  
  class KuaiSpider(BaseSpider):
  
      #准备URL 列表
      urls = ['https://www.kuaidaili.com/free/inha/{}/'.format(i) for i in range(1, 6)]
      #分组的XPATH，用于获取包含代理IP信息的标签列表
      group_xpath = '//*[@id="list"]/table/tbody/tr'
      #组内的XPATH,用于提取 ip,port,area
      detail_xpath = {
          'ip': './td[1]/text()',
          'port': './td[2]/text()',
          'area': './td[5]/text()'
      }
  
      #当我们两个页面访问时间间隔太短，就会报错，这是一种反爬手段
      def get_page_from_url(self, url):
          #随机等待1-3秒
          time.sleep(random.uniform(1, 3))
          #调用父类的方法，发送请求，获取响应数据
          return super().get_page_from_url(url)
  
  """
  4.实现[proxylistplus代理] 爬虫： https://list.proxylistplus.com/Fresh-HTTP-Proxy-List-1 
  
  - 定义一个类，继承通用爬虫类（BasicSpider）
  - 提供urls, group_xpath和detail_xpath
  """
  
  class ProxylistplusSpider(BaseSpider):
      #国外网站会比较慢
      #准备URL 列表
      urls = ['https://list.proxylistplus.com/Fresh-HTTP-Proxy-List-{}'.format(i) for i in range(1, 7)]
      #分组的XPATH，用于获取包含代理IP信息的标签列表
      group_xpath = '//*[@id="page"]/table[2]/tr[position()>2]'
      #组内的XPATH,用于提取 ip,port,area
      detail_xpath = {
          'ip': './td[2]/text()',
          'port': './td[3]/text()',
          'area': './td[5]/text()'
      }
      
  #测试
  # if __name__ == '__main__':
  #     spider = XiciSpider()
  #     for proxy in spider.get_proxies():
  #         print(proxy)
  
      #print(Ip3366Spider().urls)
  ```

  

##### 8.5 实现运行爬虫模块

- 目标：根据配置文件信息，加载爬虫，抓取代理IP，进行校验，如果可用，写入到数据库中
- 思路：
  - 在`run_spider.py`中，创建`RunSpider`类
  - 提供一个运行爬虫的run方法，作为运行爬虫的入口，实现核心的处理逻辑
    - 根据配置文件信息，获取爬虫对象列表
    - 遍历爬虫对象列表，获取爬虫对象，遍历爬虫对象的get_proxies方法，获取代理Ip
    - 检测代理IP——代理IP检测模块
    - 如果可以用，写入数据库——数据库模块
    - 处理异常，防止一个爬虫内部出错了，影响其他的爬虫
  - 使用异步俩执行每一个爬虫任务，以提高抓取代理IP效率
    - 在`__ini__`方法中创建协程池对象
    - 把处理一个代理爬虫的代码抽到一个方法
    - 使用异步执行这个方法
    - 调用协程的json方法，让当前线程等待队列任务的完成
  - 使用schedule模块，实现每隔一定的时间，执行一次爬取任务
    - 定义一个start的类方法
    - 创建当前类的对象，调用run方法
    - 使用schedule模块，每隔一定的时间，执行当前对象的run方法
  - 步骤：
    - 在`run_spider.py`中，创建RunSpider类
    - 修改setting.py 增加代理IP爬虫的配置信息

```python
#run_spider.py
#如果要用协程就要打猴子补丁
from gevent import monkey
monkey.patch_all()
#导入协程池
from gevent.pool import Pool
import schedule
import time
from settings import RUN_SPIDERS_INTERVAL

from settings import PROXIES_SPIDERS
import importlib
from core.proxy_validate.httpbin_validator import check_proxy
from core.db.mongo_pool import MongoPool
from utils.log import logger

"""
8.5 实现运行爬虫模块
目标：根据配置文件信息，加载爬虫，抓取代理IP，进行校验，如果可用，写入到数据库中
思路：

1.在`run_spider.py`中，创建`RunSpider`类
2.提供一个运行爬虫的run方法，作为运行爬虫的入口，实现核心的处理逻辑
    2.1根据配置文件信息，获取爬虫对象列表
    2.2遍历爬虫对象列表，获取爬虫对象，遍历爬虫对象的get_proxies方法，获取代理Ip
    2.3检测代理IP——代理IP检测模块
    2.4如果可以用，写入数据库——数据库模块
    2.5处理异常，防止一个爬虫内部出错了，影响其他的爬虫
3.使用异步俩执行每一个爬虫任务，以提高抓取代理IP效率
    3.1在`__ini__`方法中创建协程池对象
    3.2把处理一个代理爬虫的代码抽到一个方法
    3.3使用异步执行这个方法
    3.4调用协程的json方法，让当前线程等待队列任务的完成
4.使用schedule模块，实现每隔一定的时间，执行一次爬取任务
    4.1定义一个start的类方法
    4.2创建当前类的对象，调用run方法
    4.3使用schedule模块，每隔一定的时间，执行当前对象的run方法
"""


class RunSpider(object):

    def __init__(self):
        #创建MongoPool对象
        self.mongo_pool = MongoPool()
        # 3.1在`__ini__`方法中创建协程池对象
        self.coroutine_pool = Pool()

    def get_spider_from_settings(self):
        """根据配置文件信息，获取爬虫对象列表"""
        #遍历配置文件中爬虫信息，获取每个爬虫全类名
        for full_class_name in PROXIES_SPIDERS:
            #core.proxy_spider.proxy_spiders.XiciSpider
            #获取模块名和类名
            module_name, class_name = full_class_name.rsplit('.', maxsplit=1)
            #根据模块名，导入模块
            module = importlib.import_module(module_name)
            #根据类名，从模块中获取类
            cls = getattr(module, class_name)
            #创建爬虫对象
            spiders = cls()
            #print(spider)
            yield spiders

    def run(self):
        #2.1根据配置文件信息，获取爬虫对象列表
        spiders = self.get_spider_from_settings()
        #2.2遍历爬虫对象列表，获取爬虫对象，遍历爬虫对象的get_proxies方法，获取代理Ip
        #2.5处理异常，防止一个爬虫内部出错了，影响其他的爬虫
        #self.__execute_one_spider_task(spiders)
        # 3.3使用异步执行这个方法
        for spider in spiders:
            self.coroutine_pool.apply_async(self.__execute_one_spider_task, args=(spider, ))

        # 3.4调用协程的json方法，让当前线程等待队列任务的完成
        self.coroutine_pool.join()

    def __execute_one_spider_task(self, spider):
        # 3.2把处理一个代理爬虫的代码抽到一个方法
        #此方法是用来处理一个爬虫任务的
        try:
            # 遍历爬虫对象的get_proxies()方法，获取代理IP
            for proxy in spider.get_proxies():
                print(proxy)
                # 2.3检测代理IP——代理IP检测模块
                proxy = check_proxy(proxy)
                # print(proxy)
                # 2.4如果可以用，写入数据库——数据库模块
                # 如果speed不为-1，就说明可用
                if proxy.speed != -1:
                    # 写入数据库——数据库模块
                    self.mongo_pool.insert_one(proxy)
        except Exception as ex:
            logger.exception(ex)

    @classmethod
    def start(cls):
        # 4使用schedule模块，实现每隔一定的时间，执行一次爬取任务
        # 4.1定义一个start的类方法
        # 4.2创建当前类的对象，调用run方法
        rs = RunSpider()
        rs.run()
        # 4.3使用schedule模块，每隔一定的时间，执行当前对象的run方法
        #4.3.1 修改配置文件，增加爬虫运行时间间隔的配置，单位为小时
        schedule.every(RUN_SPIDERS_INTERVAL).hours.do(rs.run)
        while True:
            schedule.run_pending()
            time.sleep(1)

#测试
if __name__ == '__main__':
    # rs = RunSpider()
    # rs.run()
    #测试schedule
    # def task():
    #     print("哈哈")
    # schedule.every(2).seconds.do(task)
    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)
    RunSpider.start()
```

```python
#settings.py
PROXIES_SPIDERS = [
    #爬虫的全类名，路径，模块.类名
    'core.proxy_spider.proxy_spiders.XiciSpider',
    'core.proxy_spider.proxy_spiders.Ip3366Spider',
    'core.proxy_spider.proxy_spiders.KuaiSpider',
    'core.proxy_spider.proxy_spiders.ProxylistplusSpider',
]

#修改配置文件，增加爬虫运行时间间隔的配置，单位为小时
RUN_SPIDERS_INTERVAL = 24
```



#### 9. 实现代理池的检测模块

- 目的：检查代理IP可用性，保证代理池中代理IP基本可用
- 思路：
  1. 在`proxy_test.py`中，创建`ProxyTester`类
  2. 提供一个 `run` 方法，用于检测代理代理IP核心逻辑
     1. 从数据库中获取所有代理IP
     2. 遍历代理IP列表
     3. 检查代理可用性
        - 如果不可用，让代理分数-1，如果代理分数等于0就从数据库中删除该代理，否则更换新代理
        - 如果代理可用，就恢复该代理的分数，更新到数据库中
  3. 为了提高检查的速度，使用异步来执行检测任务
     1. 把要检测的代理IP，放到队列中
     2. 把检查一个代理可用性的代码，抽取到一个方法中，从队列中获取代理IP,进行检查，检查完毕，调度队列的task_done方法
     3. 通过异步回调，使用死循不断执行这个方法
     4. 开启多一个异步任务，来处理代理IP的检测，可以通过配置文件制定异步数量
  4. 使用`schedule`模块，每隔一定的时间，执行一次检测任务
     1. 定义类方法`start`，用于启动检测模块
     2. 在`start`方法中：
        - 创建本类对象
        - 调用run方法
        - 每间隔一定时间，执行一下run方法

```python
#proxy_test.py
from gevent import monkey
monkey.patch_all()
from gevent.pool import Pool
from queue import Queue
from core.db.mongo_pool import MongoPool
from core.proxy_validate.httpbin_validator import check_proxy
from settings import MAX_SCORE, TEST_PROXIES_ASYNC_COUNT, TEST_PROXIES_INTERVAL
import schedule
import time

"""
9. 实现代理池的检测模块
目的：检查代理IP可用性，保证代理池中代理IP基本可用
思路：
1. 在`proxy_test.py`中，创建`ProxyTester`类
2. 提供一个 `run` 方法，用于检测代理代理IP核心逻辑
    2.1. 从数据库中获取所有代理IP
    2.2. 遍历代理IP列表
    2.3. 检查代理可用性
    2.4如果不可用，让代理分数-1，如果代理分数等于0就从数据库中删除该代理，否则更换新代理
    2.5如果代理可用，就恢复该代理的分数，更新到数据库中
3. 为了提高检查的速度，使用异步来执行检测任务
    3.1. 把要检测的代理IP，放到队列中
    3.2. 把检查一个代理可用性的代码，抽取到一个方法中，从队列中获取代理IP,进行检查，检查完毕，调度队列的task_done方法
    3.3. 通过异步回调，使用死循不断执行这个方法
    3.4. 开启多一个异步任务，来处理代理IP的检测，可以通过配置文件制定异步数量
4. 使用`schedule`模块，每隔一定的时间，执行一次检测任务
    1. 定义类方法`start`，用于启 动检测模块
    2. 在`start`方法中：
        创建本类对象
        调用run方法
        每间隔一定时间，执行一下run方法
"""

class ProxyTester(object):

    def __init__(self):
        #创建操作数据库的MongoPool对象
        self.mongo_pool = MongoPool()
        # 3.1. 在init方法，创建队列和协程池
        self.queue = Queue()
        self.coroutine_pool = Pool()

    def __check_callback(self, temp):
        self.coroutine_pool.apply_async(self.__check_one_proxy, callback=self.__check_callback)

    def run(self):
        #提供一个 run 方法，用于检测代理代理IP核心逻辑
        # 2.1.从数据库中获取所有代理IP
        proxies = self.mongo_pool.find_all()
        # 2.2.遍历代理IP列表
        for proxy in proxies:
            #self.__check_one_proxy(proxy)
            # 3.2.把要检测的代理IP，放到队列中
            self.queue.put(proxy)
        # 3.5.开启多一个异步任务，来处理代理IP的检测，可以通过配置文件制定异步数量
        for i in range(TEST_PROXIES_ASYNC_COUNT):
            # 3.4.通过异步回调，使用死循不断执行这个方法
            self.coroutine_pool.apply_async(self.__check_one_proxy, callback=self.__check_callback)

        #让当前线程，等待队列任务完成
        self.queue.join()

    def __check_one_proxy(self):
        #检测一个代理IP的可用性
        # 2.3.检查代理可用性
        # 3.3.把检查一个代理可用性的代码，抽取到一个方法中，
        # 从队列中获取代理IP, 进行检查，
        proxy = self.queue.get()
        proxy = check_proxy(proxy)
        # 2.4如果不可用，让代理分数 - 1
        if proxy.speed == -1:
            proxy.score -= 1
            # 如果代理分数等于0就从数据库中删除该代理
            if proxy.score == 0:
                self.mongo_pool.delete_one(proxy)
            # 否则更换新代理
            else:
                self.mongo_pool.update_one(proxy)
        else:
            # 2.5如果代理可用，就恢复该代理的分数，更新到数据库中
            proxy.score = MAX_SCORE
            self.mongo_pool.update_one(proxy)
        #调用队列的task_done方法
        self.queue.task_done()

    @classmethod
    def start(cls):
        # 创建本类对象
        proxy_tester = cls()
        # 调用run方法
        proxy_tester.run()
        # 每间隔一定时间，执行一下run方法
        schedule.every(TEST_PROXIES_INTERVAL).hours.do(proxy_tester.run)
        while True:
            schedule.run_pending()
            time.sleep(1)



#测试
if __name__ == '__main__':
    pt = ProxyTester()
    pt.run()

```



```python
#settings
#配置检测代理IP的异步数量
TEST_PROXIES_ASYNC_COUNT =10
#配置检测代理IP时间间隔
TEST_PROXIES_INTERVAL = 2
```



#### 10.实现代理池的API模块

- 目标：
  - 为爬虫提供高可用代理IP的服务接口
- 步骤:
  - 实现根据协议类型和域名，提供随机的获取高可用代理IP的服务
  - 实现根据协议类型和域名，提供随机多个高可用代理的服务
  - 实现给指定的IP上追加不可用域名的服务
- 实现：
  - 在`proxy_api.py`中，创建ProxyApi类
  - 实现初始方法
    - 初始一个Flask的Web服务
    - 实现根据协议类型和域名，提供随机的获取高可用代理IP的服务
      - 可用通过 protocol 和domain 参数对IP进行过滤
      - protocol：当前请求的协议类型
      - domain：当前请求域名
    - 实现根据协议类型和域名，提供获取多个高可用代理IP的服务
      - 可通过protocol 和domain 参数对IP进行过滤
    - 实现给指定的IP上追加不可用域名的服务
      - 如果获取IP的时候，有指定域名参数，将不再获取该IP，从而进一步提高代理IP的可用性
    - 实现run方法，用于启动Flask的WEB服务
    - 实现start的类方法，用于通过类名，启动服务

代码：

```python
#proxy_api.py
from flask import Flask
from flask import request
import json

from core.db.mongo_pool import MongoPool
from settings import PROXIES_MAX_COUNT
"""
10.实现代理池的API模块
目标：
为爬虫提供高可用代理IP的服务接口
步骤:
    实现根据协议类型和域名，提供随机的获取高可用代理IP的服务
    实现根据协议类型和域名，提供随机多个高可用代理的服务
    实现给指定的IP上追加不可用域名的服务
实现：

1.在`proxy_api.py`中，创建ProxyApi类
2.实现初始方法
    2.1初始一个Flask的Web服务
    2.2实现根据协议类型和域名，提供随机的获取高可用代理IP的服务
      - 可用通过 protocol 和domain 参数对IP进行过滤
      - protocol：当前请求的协议类型
      - domain：当前请求域名
    2.3实现根据协议类型和域名，提供获取多个高可用代理IP的服务
      - 可通过protocol 和domain 参数对IP进行过滤
    2.4实现给指定的IP上追加不可用域名的服务
      - 如果获取IP的时候，有指定域名参数，将不再获取该IP，从而进一步提高代理IP的可用性
3.实现run方法，用于启动Flask的WEB服务
4.实现start的类方法，用于通过类名，启动服务
"""
# 1.在`proxy_api.py`中，创建ProxyApi类
class ProxyApi(object):

    def __init__(self):
        #2.实现初始方法
        #2.1初始一个Flask的Web服务
        self.app = Flask(__name__)
        #创建MongoPool对象，用于操作数据库
        self.mongo_pool = MongoPool()

        @self.app.route('/random')
        def random():
            """
            2.2实现根据协议类型和域名，提供随机的获取高可用代理IP的服务
                可用通过 protocol 和domain 参数对IP进行过滤
                protocol：当前请求的协议类型
                domain：当前请求域名
            :return:
            """
            protocol = request.args.get('protocol')
            domain = request.args.get('domain')
            proxy = self.mongo_pool.random_proxy(protocol, domain, count=PROXIES_MAX_COUNT)

            if protocol:
                return '{}://{}:{}'.format(protocol, proxy.ip, proxy.port)
            else:
                return '{}:{}'.format(proxy.ip, proxy.port)

        @self.app.route('/proxies')
        def proxies():
            """
            2.3实现根据协议类型和域名，提供获取多个高可用代理IP的服务
                可通过protocol 和domain 参数对IP进行过滤
            :return:
            """
            #获取协议：http/https
            protocol = request.args.get('protocol')
            #域名：如jd.com
            domain = request.args.get('domain')
            proxies = self.mongo_pool.get_proxies(protocol, domain, count=PROXIES_MAX_COUNT)

            #proxies 是一个Proxy对象的列表，但是Proxy对象不能进行序列化，需要转换为字典列表
            #转换为字典列表
            proxies = [proxy.__dict__ for proxy in proxies]
            #返回json格式字符串
            return json.dumps(proxies)

        @self.app.route('/disable_domain')
        def disable_domain():
            """
            2.4实现给指定的IP上追加不可用域名的服务
            如果获取IP的时候，有指定域名参数，将不再获取该IP，从而进一步提高代理IP的可用性
            :return:
            """
            ip = request.args.get('ip')
            domain = request.args.get('domain')

            if ip is None:
                return '请提供IP参数'
            if domain is None:
                return '请提供domain参数'

            self.mongo_pool.disable_domain(ip, domain)
            return '{} 禁用域名 {} 成功'.format(ip, domain)

    def run(self):
        """3.实现run方法，用于启动Flask的WEB服务"""
        self.app.run('0.0.0.0', port=16888)

    @classmethod
    def start(cls):
        # 4.实现start的类方法，用于通过类名，启动服务
        proxy_api = cls()
        proxy_api.run()

#测试
if __name__ == '__main__':
    # proxy_api = ProxyApi()
    # proxy_api.run()
    ProxyApi.start()
```

```python
#settings
#配置获取代理的IP最大数量，这个越小可用性就越高，但是随机性越差
PROXIES_MAX_COUNT = 50
```



#### 11.实现代理池的启动入口

- 目标：把 `启动爬虫`，`启动检测代理IP`,`启动WEB服务`  统一到一起
- 思路：
  - 开启三个进程，用于启动爬虫，检测代理IP，WEB服务
- 步骤：
  - 定义一个run方法用于启动代理池
    - 定义一个列表，用于存储要启动的进程
    - 创建 `启动爬虫` 的进程，添加到列表中
    - 创建 `启动检测` 的进程，添加到列表中
    - 创建 `启动提供API服务` 的进程，添加到列表中
    - 遍历进程列表，启动所有进程
    - 遍历进程列表，让主进程等待子进程的完成
  - 在 `if __name__ == '__main__':`中调用run方法

代码：

```python
#main.py
from multiprocessing import Process
from core.proxy_spider.run_spiders import RunSpider
from core.proxy_test import ProxyTester
from core.proxy_api import ProxyApi

"""
11.实现代理池的启动入口
目标：把 `启动爬虫`，`启动检测代理IP`,`启动WEB服务`  统一到一起
思路：
开启三个进程，用于启动爬虫，检测代理IP，WEB服务
步骤：

1.定义一个run方法用于启动代理池
    1.1定义一个列表，用于存储要启动的进程
    1.2创建 `启动爬虫` 的进程，添加到列表中
    1.3创建 `启动检测` 的进程，添加到列表中
    1.4创建 `启动提供API服务` 的进程，添加到列表中
    1.5遍历进程列表，启动所有进程
    1.6遍历进程列表，让主进程等待子进程的完成
2.在 `if __name__ == '__main__':`中调用run方法
"""


# 1.定义一个run方法用于启动代理池
def run():
    # 1.1定义一个列表，用于存储要启动的进程
    process_lis = []
    # 1.2创建 `启动爬虫` 的进程，添加到列表中
    process_lis.append(Process(target=RunSpider.start))
    # 1.3创建 `启动检测` 的进程，添加到列表中
    process_lis.append(Process(target=ProxyTester.start))
    # 1.4创建 `启动提供API服务` 的进程，添加到列表中
    process_lis.append(Process(target=ProxyApi.start))
    # 1.5遍历进程列表，启动所有进程
    for process in process_lis:
        #设置守护进程
        process.daemon = True
        process.start()
    # 1.6遍历进程列表，让主进程等待子进程的完成
    for process in process_lis:
        process.join()

if __name__ == '__main__':
    run()
```



附思维导图：



![代理池项目思维导图](.\images\2020-5-9-3.png)