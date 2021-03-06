import requests
from lxml import etree
import os
import os.path
import time


class IP:
    def __init__(self, ip, port, type, speed, check_time, live_time, addr):
        self.ip = ip
        self.port = port
        self.type = type
        self.speed = speed

        self.check_time = check_time  # 最后校验时间
        self.live_time = live_time  # 存活时间
        self.addr = addr  # 位置

    def __str__(self):
        return str({
            'ip': self.ip,
            'port': self.port,
            'type': self.type,
            'speed': self.speed,
            'check_time': self.check_time,
            'live_time': self.live_time,
            'addr': self.addr
        })


class Kuaidaili_com:
    free_inha_count = 0
    free_inha_timeout = 5
    def free_inha(self, page=1):
        url = 'https://www.kuaidaili.com/free/inha/%d/' % page
        try:
            r = requests.get(url, headers={
                'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Accept-Encoding':'gzip, deflate, br',
                'Accept-Language':'zh-CN,zh;q=0.9',
                'Cache-Control':'max-age=0',
                'Host': 'www.kuaidaili.com',
                'Upgrade-Insecure-Requests':'1',
                'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
            }, timeout=self.free_inha_timeout)
        except requests.exceptions.ReadTimeout as e:
            self.free_inha_timeout += 5
            self.free_inha(page)
        except requests.exceptions.ConnectionError as e:
            raise Exception('快代理访问国内高匿代理分页时，服务器丢弃了这个请求')
        else:
            r.raise_for_status()
            r.encoding = 'utf-8'
            ips = []
            try:
                page = etree.HTML(r.text)
                trs = page.xpath('//table[@class="table table-bordered table-striped"]/tbody/tr')
                for tr in trs:
                    tds = tr.xpath('./td')

                    ip = tds[0].xpath('./text()')[0].strip()
                    port = tds[1].xpath('./text()')[0].strip()
                    type = tds[3].xpath('./text()')[0].strip().lower()
                    addr = tds[4].xpath('./text()')[0].strip().lower()
                    speed = tds[5].xpath('./text()')[0].strip()[:-1]
                    check_time = tds[6].xpath('./text()')[0].strip()

                    live_time = None

                    ips.append(IP(ip, port, type, speed, check_time, live_time, addr))
            except Exception as e:
                print(e)
                if not os.path.exists('kuaidaili_com'):
                    os.mkdir('kuaidaili_com')
                else:
                    with open('kuaidaili_com' + os.path.sep + url + '.err') as f:
                        f.write(r.text)
            return ips


class Ip_seofangfa_com:
    index_count = 0
    index_timeout = 30
    def index(self):
        self.index_count += 1
        if self.index_count > 3:
            raise Exception('主页重试次数超过3次')
        url = 'https://ip.seofangfa.com/'
        headers = {
            'Host': 'ip.seofangfa.com',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 7.0; SM-G935P Build/NRD90M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.111 Mobile Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }
        try:
            r = requests.get(url, headers=headers)
        except requests.exceptions.ReadTimeout as e:
            self.index_timeout += 5
            self.index()
        else:
            r.raise_for_status()
            r.encoding = 'utf-8'
            page = etree.HTML(r.text)
            trs = page.xpath('//table[@class="table"]/tbody/tr')
            ips = []
            for tr in trs:
                tds = tr.xpath('./td')
                ip = tds[0].xpath('./text()')[0].strip()
                port = tds[1].xpath('./text()')[0].strip()
                speed = tds[2].xpath('./text()')[0].strip()
                addr = tds[3].xpath('./text()')[0].strip()
                check_time = tds[4].xpath('./text()')[0].strip()
                type = 'http'
                live_time = None
                ips.append(IP(ip, port, type, speed, check_time, live_time, addr))
            return ips


def get_ips():
    kc = Kuaidaili_com()
    isc = Ip_seofangfa_com()
    ips = []

    for i in range(1, 4):
        ips += kc.free_inha(i)
        time.sleep(15)

    ips += isc.index()

    return ips