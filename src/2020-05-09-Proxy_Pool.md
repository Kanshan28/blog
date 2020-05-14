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


1.代理池概述

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
        'http':'http://{}:{}.format(proxy.ip, proxy.port)',
        'https': 'https://{}:{}.format(proxy.ip, proxy.port)',
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
    
  - 代码

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

    def inser_one(self, proxy):
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
            conditions['disable_domains'] = {'$nin': [domain]}
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

        if self.proxies.count_documents({'_id':ip, 'disable_domains':domain}) == 0:
            #如果disable_domains字段中，没有这个域名才添加
            self.proxies.update_one({'_id':ip}, {'$push': {'disable_domains':domain}})
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





- 提供代理API模块使用的功能
  - 实现查询功能：根据条件进行查询 ，可以指定查询数量，先分数降序，速度升序，保证优质的代理IP在上面
  - 实现根据协议类型和要访问网站的域名，获取代理IP列表
  - 实现根据协议类型和要访问完整的域名，随机获取一个代理IP
  - 实现把指定域名添加到指定IP的disable_domain列表中