import requests
import threading
import os

def download_file(url, filename):
    try:
        r = requests.get(url)
        r.raise_for_status()
        with open(os.path.join(os.getcwd(), filename), "wb") as file:
            file.write(r.content)
        print(f"Successfully downloaded {filename}")
    except requests.RequestException as e:
        print(f"Error downloading {url}: {e}")

# 定义URL和文件名
download_tasks = [
    ("https://raw.githubusercontent.com/cbuijs/ipasn/master/country-asia-china.list", "IP.China.list"),
    ("https://raw.githubusercontent.com/kankankankankankan/china-ip-list/master/chnroute.txt", "IPv4.China.list"),
    ("https://raw.githubusercontent.com/kankankankankankan/china-ip-list/master/chnroute_v6.txt", "IPv6.China.list")
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

# 打印当前目录内容
print("Current directory contents:")
print(os.listdir(os.getcwd()))
