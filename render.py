# coding=utf-8


from selenium.common.exceptions import TimeoutException
from selenium import webdriver
from bs4 import BeautifulSoup

import threading


class RenderWork(threading.Thread):
    def __init__(self, thread_id, url, page, work_queue):
        super(RenderWork, self).__init__()
        self.thread_id = thread_id
        self.url = url
        self.page = page
        self.work_queue = work_queue
        self.driver = None

    def init_web_engine(self):
        self.driver = webdriver.PhantomJS()
        return

    def run(self):
        self.init_web_engine()
        self.gen_url_task()

    def gen_url_task(self):
        for num in range(1, self.page+1):
            new_url = self.url + '-' + str(num)
            img_url = self.get_imgsrc_by_render(new_url)
            if img_url:
                self.work_queue.put((self.url, self.page, img_url))
        return

    def get_imgsrc_by_render(self, url):
        self.driver.set_page_load_timeout(60)
        try:
            self.driver.get(url)
        except TimeoutException:
            print("timeout")
            self.driver.execute_script('window.stop()')
        finally:
            soup_html = BeautifulSoup(self.driver.page_source, 'lxml')
            # print(webdriver.page_source)
            for img_src in soup_html.find_all('img'):
                if 'name' in img_src.attrs and img_src['name'] == 'TheImg':
                    if 'src' in img_src.attrs:
                        print(img_src['src'])
                        return img_src['src']
                    else:
                        return None
                        # with open(file_path, "w") as f:
                        #     f.write(webdriver.page_source)
