# coding=utf-8

from multiprocessing import Process
import logging
import os
import re
import asyncio
import queue

import aiohttp


class CrawlWork(Process):
    def __init__(self, task_queue):
            super(CrawlWork, self).__init__()
            self.init_log()
            self.log.info("start log system")
            self.task_queue = task_queue
            self.dst_path = "/home/beyondkoma/work/gitProject/webCrawl/images/"

    def init_log(self):
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                            datefmt='%a, %d %b %Y %H:%M:%S',
                            filename='crawl.log',
                            filemode='a')
        self.log = logging.getLogger("crawl")
        return

    def run(self):
            self.log.info("start run log system")
            loop = asyncio.get_event_loop()
            task = asyncio.ensure_future(self.process_crawl_tasks())
            loop.run_until_complete(task)
            self.log.info("CrawlWork ret:{}".format(task.result()))

    async def process_crawl_tasks(self):
        while True:
            try:
                (base_url, page, img_url) = self.task_queue.get_nowait()
                self.log.info("the cur crawl info is {}, {}, {}".format(base_url, page, img_url))
                await self.down_img_by_url(img_url, self.dst_path)
            except queue.Empty:
                await asyncio.sleep(3)
        return True

    async def down_img_by_url(self, img_url, dst_path):
        if not os.path.exists(dst_path):
            os.mkdir(dst_path)
        filename = re.split("/|//", img_url)
        osfile = dst_path + filename[len(filename)-1]
        chunk_size = 1024
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(img_url) as resp:
                    with open(osfile, 'wb') as fd:
                        while True:
                            chunk = await resp.content.read(chunk_size)
                            if not chunk:
                                break
                            fd.write(chunk)
        except Exception:
            print('download img happens exception', img_url)
            return False
        return True
