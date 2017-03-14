# coding=utf-8

from multiprocessing import Queue
import queue
import time
from datetime import datetime
import configparser
import json


from render import RenderWork
from crawl import CrawlWork



# 进程队列
crawl_tasks = Queue()
# 线程队列
thread_queue = queue.Queue()

sub_threads = []


def is_sub_thread_alive():
    # except main thread
    for th in sub_threads:
        if th.is_alive():
            return True
    return False


def put_task_to_process(thread_queue):
    while not thread_queue.empty():
        task_data = thread_queue.get()
        crawl_tasks.put(task_data)
    return True


# 每３秒检测子线程是否完成提取下载url任务
def manage_queue_task(thread_queue):
    start_time = datetime.now()
    while True:
        end_time = datetime.now()
        if (end_time - start_time).total_seconds() > 3:
            if not is_sub_thread_alive():
                put_task_to_process(thread_queue)
                end_task = dict(base_url="undef", page=None, img_url=None, path=None)
                crawl_tasks.put(json.dumps(end_task))
                break
            else:
                start_time = end_time
                continue
        put_task_to_process(thread_queue)
        time.sleep(0.1)


def start_sub_render_thread(url_tasks):
    for num, cur_url_task in enumerate(url_tasks):
        m_thread = RenderWork(num, cur_url_task[0], int(cur_url_task[1]), cur_url_task[2], thread_queue)
        m_thread.start()
        sub_threads.append(m_thread)
        print("start crawl thread {}, handle the combic url {}".format(num, cur_url_task[0]))


if __name__ == '__main__':
    print("start crawl combic")
    url_tasks = []
    cf = configparser.ConfigParser()
    cf.read("config.ini")
    for k, v in cf.items("urls"):
        l = v.split(',')
        l.append(k)
        url_tasks.append(l)

    start_sub_render_thread(url_tasks)
    # start crawl process
    print("start crawl process")
    crawl_process = CrawlWork(crawl_tasks)
    crawl_process.start()
    manage_queue_task(thread_queue)
    print("wait crawl task finished")
    crawl_process.join()
