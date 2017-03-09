# coding=utf-8

from multiprocessing import Queue
import queue
import time
import configparser


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
# 线程队列
thread_queue = queue.Queue()


def analyse_url(thread_queue):
    while True:
        while not thread_queue.empty():
            task_url = thread_queue.get()
            print("the img is {}".format(task_url[2]))
            crawl_tasks.put(task_url)
        time.sleep(1)


def assign_thread_tasks(url_tasks):
    for num, cur_url_task in enumerate(url_tasks):
        thread = RenderWork(num, cur_url_task[0], int(cur_url_task[1]), thread_queue)
        thread.start()
        print("start crawl thread {}, handle the combic url {}".format(num, cur_url_task[0]))


if __name__ == '__main__':
    print("start crawl combic")
    url_tasks = []
    cf = configparser.ConfigParser()
    cf.read("config.ini")
    for k, v in cf.items("urls"):
        l = v.split(',')
        url_tasks.append(l)

    assign_thread_tasks(url_tasks)
    # start crawl process
    print("start crawl process")
    crawl_process = CrawlWork(crawl_tasks)
    crawl_process.start()
    analyse_url(thread_queue)
    crawl_process.join()
