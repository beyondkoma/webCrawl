# coding=utf-8

from multiprocessing import Queue
import queue

from render import RenderWork
from crawl import CrawlWork



file_path = "/home/beyondkoma/work/gitProject/webCrawl/images/test.html"
base_url = "http://v.comicbus.com/online/comic-103.html?ch=1"
dst_path = "/home/beyondkoma/work/gitProject/webCrawl/images/"


# r = requests.post("http://v.comicbus.com/online/comic-103.html?ch=1", data={'id': 'next'})
# r.encoding = 'big5'
# with open(file_path, "w") as f:
#         f.write(r.text)
# img_url_tasks = Queue()

# 线程队列
workQueue = queue.Queue()


def analyse_url():
    while not workQueue.empty():
        task_url = workQueue.get()
        print("the img is {}".format(task_url[2]))
        crawl_tasks.put(task_url)


if __name__ == '__main__':
    thread_num = 1
    page = 20
    for num in range(thread_num):
        thread = RenderWork(num, base_url, page, workQueue)
        thread.start()

    # 进程队列
    crawl_tasks = Queue()
    analyse_url()
    # start crawl process
    crawl_process = CrawlWork(workQueue)
    crawl_process.start()
    crawl_process.join()
