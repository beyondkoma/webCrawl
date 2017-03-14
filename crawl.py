# coding=utf-8

from multiprocessing import Process, Queue
import logging
import os
import re
import json
import asyncio
import queue

import aiohttp


class CrawlWork(Process):
    def __init__(self, task_queue):
            super(CrawlWork, self).__init__()
            self.task_queue = task_queue
            self.dst_path = os.path.join(os.getcwd(), "images")

    def init_log(self):
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                            datefmt='%a, %d %b %Y %H:%M:%S',
                            filename='crawl.log',
                            filemode='a')
        self.log = logging.getLogger("crawl")
        return

    def run(self):
            self.init_log()
            self.log.info("start run log system")
            loop = asyncio.get_event_loop()
            task = asyncio.ensure_future(self.process_crawl_tasks())
            loop.run_until_complete(task)
            self.log.info("CrawlWork ret:{}".format(task.result()))

    async def process_crawl_tasks(self):
        while True:
            try:
                json_str = self.task_queue.get_nowait()
                img_task = json.loads(json_str)
                self.log.info("the crawl task content is {}".format(img_task))
                if img_task['base_url'] == "undef":
                    self.log.info("the crawl tasks has finished")
                    break
                else:
                    cur_path = os.path.join(self.dst_path, img_task['path'])
                    await self.down_img_by_url(img_task['base_url'], img_task['img_url'], cur_path)
            except queue.Empty:
                await asyncio.sleep(3)
        return True

    async def down_img_by_url(self, base_url, img_url, dst_path):
        dirname = re.split("/|//", base_url)
        # target_path = os.path.join(self.dst_path, dirname[-1])
        # target_path = self.dst_path + dirname[-1]
        if not os.path.exists(dst_path):
            os.makedirs(dst_path)
        filename = re.split("/|//", img_url)
        osfile = os.path.join(dst_path, filename[-1])
        # headers = {
        #     'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:46.0) Gecko/20100101 Firefox/46.0',        }
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
            self.log.info("download img {} ,happens exception".format(img_url))
            return False
        return True
