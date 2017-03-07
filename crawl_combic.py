# coding=utf-8

from multiprocessing import Queue
import queue
import time
import ConfigParser

from render import RenderWork
from crawl import CrawlWork



file_path = "/home/beyondkoma/work/gitProject/webCrawl/images/test.html"
base_url = "http://v.comicbus.com/online/comic-103.html?ch=1"
dst_path = "/home/beyondkoma/work/gitProject/webCrawl/images/"
# page = 103

# r = requests.post("http://v.comicbus.com/online/comic-103.html?ch=1", data={'id': 'next'})
# r.encoding = 'big5'
# with open(file_path, "w") as f:
#         f.write(r.text)
# img_url_tasks = Queue()

# 进程队列
crawl_tasks = Queue()


def analyse_url(thread_queue):
    while True:
        while not thread_queue.empty():
            task_url = thread_queue.get()
            print("the img is {}".format(task_url[2]))
            crawl_tasks.put(task_url)
        time.sleep(1)


if __name__ == '__main__':
    print("start crawl combic")
    cf = ConfigParser.ConfigParser()
    cf.read("config.ini")
    for k, v in cf.items("urls"):
        l = v.split(',')
        print(l[0], int(l[1])+10)

    # 线程队列
    thread_queue = queue.Queue()
    thread_num = 1
    page = 20
    for num in range(thread_num):
        thread = RenderWork(num, base_url, page, thread_queue)
        thread.start()

    # start crawl process
    print("start crawl process")
    crawl_process = CrawlWork(crawl_tasks)
    crawl_process.start()
    analyse_url(thread_queue)
    crawl_process.join()
