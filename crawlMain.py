# -*-  coding=utf8  -*-

import requests
from bs4 import BeautifulSoup
from collections import deque
import time
import re


headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:46.0) Gecko/20100101 Firefox/46.0',
}
totalUrls = dict()
totalImageUrls = dict()


def getHtmlResponse(url):
    try:
        r = requests.get(url, headers=headers, timeout=30)
    except requests.exceptions.ConnectionError:
        print('request get url {0} happen exceptions. '.  format(url))
        return None
    except Exception:
        print('get url {0} happen exceptions. '.  format(url))
        return None
    return r


def writeContentToFile(filename, data, mode='w'):
    m_mode = mode
    with open(filename, m_mode) as f:
        f.write(data)
    return True


def downImageFromUrls(urls, path):
        while urls:
            url = urls.pop()
            filename = re.split("/|//", url)
            m_len = len(filename)
            m = re.match(".*\.jpg|.*\.gif|.*\.png", filename[m_len-1])
            if m is not None:
                time.sleep(0.1)
                osfile = path + filename[m_len-1]
                try:
                    rel = requests.get(url, stream=True, verify=False)
                    if rel.status_code == 200:
                        print("down image is {0}. ". format(url))
                        with open(osfile, 'wb') as f:
                            for chunk in rel.iter_content(1024):
                                f.write(chunk)
                except requests.exceptions as e:
                    print('requests is exceptions when downImage.', url)
                    continue
                except Exception as e:
                    print('ordinary exception', url)
                    continue
                # print 'the current url\'s status is ',url,rel.status_code
            else:
                # print 'The url is filtered. ', url
                return True
        return True

def makeUrlFromHref(valueurl, currenturl, defaulturl=""):
    """

    # <a href="../../../">, <a href="thread0806.php?fid=7">,
    """
    m = re.match("http://.+|https://.+", valueurl)
    if m is not None:
        return valueurl
    else:
        new_url = defaulturl + valueurl
    return new_url


def getHrefFromHtml(urls, currenturl, urlcontent):
    soup_html = BeautifulSoup(urlcontent, 'lxml')
    global totalUrls
    for url_link in soup_html.find_all('a'):
        value = url_link.get('href')
        if value is not None:
            new_url = makeUrlFromHref(value, currenturl)
            m = re.match("http://.+\.\..*|https://.+\.\..*", new_url)
            if m is not None:
                continue
            else:
                m_count = totalUrls.get(new_url)
                if m_count:
                    m_count = m_count + 1
                    totalUrls[new_url] = m_count
                else:
                    urls.append(new_url)
                    totalUrls[new_url] = 1
    return True


def getImageSrcFromHtml(urls, text):
    global totalImageUrls
    soup_html = BeautifulSoup(text, 'lxml')
    for img_src in soup_html.find_all('img'):
        value = img_src.get('src')
        if value is not None:
            m = re.match("http://.+|https://.+", value)
            if m is not None:
                if not totalImageUrls.get(value):
                    print('get Image url,{}'.format(value))
                    urls.append(value)
                    totalImageUrls[value] = 1
    return True

if __name__ == '__main__':
    print("hello webCrawl.")
    # reload(sys)
    # sys.setdefaultencoding('utf-8')
    url = 'http://v.comicbus.com/online/comic-103.html?ch=1'
    img_path = '/home/beyondkoma/work/gitProject/webCrawl/images/'

    # createImageFromUrl('http://i4.tietuku.com/408da328c806fa52.jpg',img_path)
    init_urls = deque()
    img_urls = []
    init_urls.append(url)
    url_num = 1

    while len(init_urls) > 0:
        r = getHtmlResponse(url)
        r.encoding = 'big5'
        if r is not None:
            url = init_urls.popleft()
            writeContentToFile(img_path + "study.html", r.text)
            print('current url is {0},the count is {1}. '.format(url, url_num))
            url_num += 1
            # getHrefFromHtml(init_urls, url, r.text)
            img_urls = []
            getImageSrcFromHtml(img_urls, r.text)
            downImageFromUrls(img_urls, img_path)
        else:
            url = init_urls.popleft()
            time.sleep(2)
            continue
