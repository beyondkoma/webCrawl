# coding=utf-8

from multiprocessing import Process
import os
import re
import asyncio

import aiohttp


class CrawlWork(Process):
    def __init__(self, task_queue):
            super(CrawlWork, self).__init__()
            self.task_queue = task_queue
            self.dst_path = "/home/beyondkoma/work/gitProject/webCrawl/images/"

    def run(self):
            loop = asyncio.get_event_loop()
            task = asyncio.ensure_future(self.process_crawl_tasks())
            loop.run_until_complete(task)
            print('CrawlWork ret:', task.result())

    async def process_crawl_tasks(self):
        while True:
            if not self.task_queue.empty():
                (base_url, page, img_url) = self.task_queue.get()
                await self.down_img_by_url(img_url, self.dst_path)
            else:
                await asyncio.sleep(3)
        return True

    async def down_img_by_url(self, img_url, dst_path):
        if not os.path.exists(dst_path):
            os.mkdir(dst_path)
        filename = re.split("/|//", img_url)
        osfile = dst_path + filename[len(filename)-1]
        max_bytes = 1024
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(img_url) as resp:
                    with open(osfile, 'wb') as f:
                        async for chunk in resp.content.iter_content(max_bytes):
                            f.write(resp)
        except Exception:
            print('download img happens exception', img_url)
            return False
        return True
