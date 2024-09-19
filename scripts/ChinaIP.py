'''
Author: Vincent Young
Date: 2022-11-17 02:14:24
LastEditors: Vincent Young
LastEditTime: 2022-11-17 03:19:20
FilePath: /ASN-China/syncIP.py
Telegram: https://t.me/missuo

Copyright © 2022 by Vincent, All Rights Reserved. 
'''

import requests
import threading

def download_file(url, filename):
    r = requests.get(url)
    with open(filename, "wb") as file:
        file.write(r.content)

# 定义URL和文件名
download_tasks = [
    ("https://raw.githubusercontent.com/cbuijs/ipasn/master/country-asia-china.list", "IP.China.list"),
    ("https://raw.githubusercontent.com/cbuijs/ipasn/master/country-asia-china4.list", "IPv4.China.list"),
    ("https://raw.githubusercontent.com/cbuijs/ipasn/master/country-asia-china6.list", "IPv6.China.list")
]

# 创建线程
threads = []
for url, filename in download_tasks:
    thread = threading.Thread(target=download_file, args=(url, filename))
    threads.append(thread)

# 启动线程
for thread in threads:
    thread.start()

# 等待所有线程结束
for thread in threads:
    thread.join()

