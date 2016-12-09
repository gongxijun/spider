#!/usr/bin/env python
# coding=utf-8
import urllib
import urllib2
import urlparse
import re
import os
import recognition as recog
from PIL import Image
import Queue as deque
import requests
import sys

reload(sys)  # Python2.5 初始化后会删除 sys.setdefaultencoding 这个方法，我们需要重新载入
sys.setdefaultencoding('utf-8')


class DataTeamSpider:
    def __init__(self, url, dest_dir, _list=[line for line in open('html_list.txt', 'r')]):
        self.url = url
        self.dest_dir = dest_dir
        self.list = _list
        self.html_list = deque.Queue(maxsize=5000)
        pass

    def getHtml(self, url=None):

        _html = None
        try:

            # page = urllib2.urlopen(self.url if url is None else url, timeout=5)
            # _html = page.read()
            page = requests.get(self.url if url is None else url, timeout=5)
            _html = page.text
        except Exception, e:
            pass
        return _html

    def parseHtml(self, html, reg):
        if html is None:
            return []
        _re = re.compile(reg)
        _list = re.findall(_re, html)
        return _list

    def parseURL(self, url, type):
        ind_s = url.rfind('="')
        if ind_s < 0:
            ind_s += len(url)
        ind_e = url.rfind(type)
        print url[ind_s + 2:ind_e + len(type)]
        return url[ind_s + 2:ind_e + len(type)] if ind_s < ind_e else url

    def getImg(self, html):
        if html is None:
            return
        default_reg = r'="(.+?\.(jpeg|jpg|png))"'
        x = 0
        for imgurl in self.parseHtml(html, default_reg):
            tmp_imgurl = (self.parseURL(imgurl[0], imgurl[1]), imgurl[1])
            del imgurl
            imgurl = tmp_imgurl

            if imgurl[0].find("http") == -1 and imgurl[0].find("com") == -1 and imgurl[0].find("cn") == -1:
                domain = self.getdomain()
                tmp_imgurl = (('/' if domain is None else domain) + imgurl[0], imgurl[1])
                del imgurl
                imgurl = tmp_imgurl
            self.create_file_path(imgurl, str(x))
            x += 1

    def getdomain(self):
        for url in reversed(self.list):
            proto, rest = urllib.splittype(url)
            domain, rest = urllib.splithost(rest)
            if domain is not None:
                return domain
        return None

    def getPage(self, html):
        if html is None:
            return
        self.getImg(html)
        # 防止死循环
        default_html = r'="(.+?\.(html|jsp|cn|com))"'
        fp = open("html_list.txt", 'a+')
        self.list = [line for line in open('html_list.txt', 'r')]
        for imgurl in self.parseHtml(html, default_html):
            tmp_imgurl = (self.parseURL(imgurl[0], imgurl[1]), imgurl[1])
            del imgurl
            imgurl = tmp_imgurl

            imgurl_find = imgurl[0] + '\n'
            if imgurl_find in self.list:
                print "已存在"
                continue
            new_imgurl = imgurl[0]
            new_imgurl = new_imgurl.lstrip('/')
            if imgurl[0].find("http") == -1 and imgurl[0].find("com") == -1 and imgurl[0].find("cn") == -1:
                domain = self.getdomain()
                new_imgurl = (('/' if domain is None else domain) + imgurl[0]).lstrip('/')
            print new_imgurl
            self.list.append(new_imgurl)
            fp.writelines(new_imgurl + '\n')
            _html = self.getHtml(new_imgurl)
            if self.html_list.full():
                break
            self.html_list.put(_html)
        fp.close()

    def create_file_path(self, img_url, item_id):

        """
        purpose:创建本地保存文件路径
        input:img_url
        output:文件路径
        """
        file_name = ''
        rest_img_url = ''
        try:
            rest_img_url = unicode(img_url[0])
            segs = urlparse.urlparse(img_url[0])
            if rest_img_url.find("http") == -1:
                rest_img_url = 'https://' + rest_img_url.lstrip('/')
            file_name = "./tmp." + img_url[1]
            urllib.urlretrieve(rest_img_url, file_name)
            img = Image.open(file_name)
            width, height = img.size
            if width * height < 260000:
                return
            img.thumbnail((512, 512), Image.ANTIALIAS)
            # 文件全路径
            img_name = recog.baidu_stu_lookup(img)

            print "图片名称：", img_name
            file_path = os.path.join(self.dest_dir, img_name + '.' + img_url[1])
            # 目录是否存在，不存在重新建立
            path = '/'.join(file_path.split('/')[:-1])
            isExists = os.path.exists(path)
            if not isExists:
                os.makedirs(path)
            urllib.urlretrieve(rest_img_url, file_path)
        except Exception, e:
            print '执行异常', file_name, rest_img_url, e
            # os.remove(file_name)
            pass


if __name__ == '__main__':
    #http://travel.qunar.com/youji/6500530
    #http://you.ctrip.com/photos/sight/hangzhou14/r2040-63443468.html
    #http://lvyou.elong.com/5278780/tour/a9d9hc90.html
    _spilder = DataTeamSpider("http://lvyou.elong.com/5278780/tour/a9d9hc90.html",
                              "/media/gongxijun/fun/label_img")
    _html = _spilder.getHtml()
    _spilder.html_list.put(_html)
    while not _spilder.html_list.empty():
        _html = _spilder.html_list.get(block=False)
        _spilder.getPage(_html)
