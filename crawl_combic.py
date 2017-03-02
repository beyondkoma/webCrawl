# coding=utf-8
import requests
from selenium.common.exceptions import TimeoutException
from selenium import webdriver
from bs4 import BeautifulSoup

import time
import os
import re
from multiprocessing import Process, Queue

file_path = "/home/beyondkoma/work/gitProject/webCrawl/images/test.html"
base_url = "http://v.comicbus.com/online/comic-103.html?ch=1"
dst_path = "/home/beyondkoma/work/gitProject/webCrawl/images/"
page = 103

# r = requests.post("http://v.comicbus.com/online/comic-103.html?ch=1", data={'id': 'next'})
# r.encoding = 'big5'
# with open(file_path, "w") as f:
#         f.write(r.text)
img_url_tasks = Queue()


def init_web_engine():
    driver = webdriver.PhantomJS()
    return driver


def gen_img_url_task(webdriver):
    for num in range(1, page+1):
        if num != 1:
            new_url = base_url + '-' + str(num)
        else:
            new_url = base_url
        img_url = get_imgsrc_by_render(new_url, webdriver)
        if img_url:
            img_url_tasks.put(img_url)
            print("get img url {}, current process is {}, the parent process is {}".format(img_url, os.getpid(), os.getppid()))
    return


def get_imgsrc_by_render(url,  webdriver):
    webdriver.set_page_load_timeout(60)
    try:
        webdriver.get(url)
    except TimeoutException:
        print("timeout")
        webdriver.execute_script('window.stop()')
    finally:
        soup_html = BeautifulSoup(webdriver.page_source, 'lxml')
        # print(webdriver.page_source)
        for img_src in soup_html.find_all('img'):
            if 'name' in img_src.attrs and img_src['name'] == 'TheImg':
                if 'src' in img_src.attrs:
                    print(img_src['src'])
                    return img_src['src']
                else:
                    return None
                with open(file_path, "w") as f:
                    f.write(webdriver.page_source)


def down_img_by_url(url, dst_path):
    if not os.path.exists(dst_path):
        os.mkdir(dst_path)
    filename = re.split("/|//", url)
    m_len = len(filename)
    osfile = dst_path + filename[m_len-1]
    try:
        rel = requests.get(url, stream=True, verify=False, timeout=30)
        if rel.status_code == 200:
                with open(osfile, 'wb') as f:
                    for chunk in rel.iter_content(1024):
                        f.write(chunk)
                print("down image:{0} is finished, the path is{1}. ". format(url, dst_path))
        else:
                print("down image:{0} has failured. ". format(url))
                return False
    except requests.RequestException:
        print('requests is exceptions when downImage.', url)
        return False
    except Exception:
        print('ordinary exception', url)
        return False
    return True


def down_worker(img_url_tasks):
    print("current process is {}, the parent process is {}".format(os.getpid(), os.getppid()))
    img_count = 0
    while True:
        print("current total img urls is {}".format(img_url_tasks.qsize()))
        img_url = img_url_tasks.get()
        down_img_by_url(img_url, dst_path)
        img_count += 1
        if img_count == page:
            print("down_worker has finished the download tasks")
            break
        if img_url_tasks.empty():
            time.sleep(5)


if __name__ == '__main__':
    driver = init_web_engine()
    worker = Process(target=down_worker, args=(img_url_tasks,))
    worker.start()
    gen_img_url_task(driver)
    driver.quit()
    worker.join()
