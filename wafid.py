#!/usr/bin/env python
# -*- coding:utf-8 -*-
# waf identify prog
# Author Cryin'@cSecGroup.com
'''
 __      __  _____  ___________.__    .___
/  \    /  \/  _  \ \_   _____/|__| __| _/
\   \/\/   /  /_\  \ |    __)  |  |/ __ | 
 \        /    |    \|     \   |  / /_/ | 
  \__/\  /\____|__  /\___  /   |__\____ | 
       \/         \/     \/            \/

WAFid - Web Application Firewall identify Tool
By Code Security Group
https://github.com/cSecGroup
'''


from copy import deepcopy
from urlparse import urljoin
from lxml.html import etree
import re
import os
import requests
import optparse
import sys

wafdetectlist = [
    '360',
    'Safedog',
    'NetContinuum',
    'Anquanbao',
    'Baidu Yunjiasu',
    'Knownsec KS-WAF',
    'BIG-IP',
    'Barracuda',
    'BinarySEC',
    'BlockDos',
    'Cisco ACE',
    'CloudFlare',
    'NetScaler',
    'FortiWeb',
    'jiasule',
    'Newdefend',
    'Palo Alto',
    'Safe3WAF',
    'Profense',
    'West263CDN',
    'WebKnight',
    'Wallarm',
    'USP Secure Entry Server',
    'Sucuri WAF',
    'Radware AppWall',
    'PowerCDN',
    'Naxsi',
    'Mission Control Application Shield',
    'IBM WebSphere DataPower',
    'Edgecast',
    'Applicure dotDefender',
    'Comodo WAF',
    'ChinaCache-CDN',
    'NSFocus'
]

WAF_ATTACK_VECTORS = (
                        "",  # NULL
                        "search=<script>alert(/csecgroup/)</script>",
                        "file=../../../../../../etc/passwd",
                        "id=1 AND 1=1 UNION ALL SELECT 1,2,3,table_name FROM information_schema.tables WHERE 2>1--"
                     )
WAF_KEYWORD_VECTORS = ( 
                        "<a href=\"http://bbs.jiasule.com/thread-124-1-1.html",
                        "This error was generated by Mod_Security",
                        "has been blocked in accordance with company policy"
                      )
WAF_PRODUCT_NAME = (
                     "Knownsec jiasule Web Application Firewall",
                     "ModSecurity: Open Source Web Application Firewall",
                     "Palo Alto Firewall"
                   )

banner = r'''
 __      __  _____  ___________.__    .___
/  \    /  \/  _  \ \_   _____/|__| __| _/
\   \/\/   /  /_\  \ |    __)  |  |/ __ | 
 \        /    |    \|     \   |  / /_/ | 
  \__/\  /\____|__  /\___  /   |__\____ | 
       \/         \/     \/            \/

WAFid - Web Application Firewall identify Tool
By Code Security Group

'''

class wafid(object):
    def __init__(self,url):

        self._finger = ''
        self._nowaf = ''
        self._url = url
    def _run(self):
        try:
            self.scan_site()
        except:
            print "[+]【Wafid】please check site url : " +self._url
            raise

    def report_waf(self):
        print "[+]【Wafid】identify website waf type is : "+self._finger +"\r\n"

    def scan_site(self):
        if "http" not in self._url:
            print "[+]【Wafid】please check site url : " +self._url
            return False
        for vector in range(0,len(WAF_ATTACK_VECTORS)):
            turl= ''
            turl = deepcopy(self._url)

            add_url = WAF_ATTACK_VECTORS[vector]
            turl = urljoin(turl, add_url)
            resp = requests.get(turl)
            if self.check_waf(resp):
                self.report_waf()
                return True
            else:
                self._nowaf="This website has no waf or identify false!!!"
                print "[+]【Wafid】identify waf finger false : "+self._nowaf+"\r\n"
                return False
        
        return True

    def regexp_header(self,rule_dom,waf_dom,head_type,resp):
        if head_type in resp.headers:

            regmatch_dom = rule_dom[0].xpath("regmatch")
            regexp_doms = regmatch_dom[0].xpath("regexp") if regmatch_dom != None else []
        
            for regexp_dom in regexp_doms:
                exp_pattern = re.compile(regexp_dom.text)
                if exp_pattern.search(resp.headers[head_type]):
                   self._finger=waf_dom.get("name")
                  # print "identify website waf type is : "+self._finger
                   return True
                else:
                    continue
                   #print "regmatch head_type regexp false!"
      
            if not self._finger:
                return False 
            else:
                return False
        return False
    
    def check_resp(self,resp):
        content=''
        if len(resp.content) != 0:
            content = resp.content.strip()
        for waf_keyword in range(0,len(WAF_KEYWORD_VECTORS)):
            if WAF_KEYWORD_VECTORS[waf_keyword] in content:
                self._finger=WAF_PRODUCT_NAME[waf_keyword]
               # print "identify website waf type with respcontent is : "+self._finger
                return True
            else:
                self._nowaf="This website has no waf or identify false!!!"
                #print "get waf finger false:"+self._nowaf
                #return False
        return False

    def check_waf(self, resp):
        if not resp.content:
            return
        self._xmlstr_dom = etree.parse('finger.xml')
        waf_doms = self._xmlstr_dom.xpath("waf")
        for waf_dom in waf_doms:
            finger_dom = waf_dom.xpath("finger")
            rule_dom = finger_dom[0].xpath("rule")
            head_type =rule_dom[0].get("header").lower()
            if head_type in resp.headers:
                if self.regexp_header(rule_dom,waf_dom,head_type,resp):
                    return True
                else:
                    self._nowaf="This website has no waf or identify false!!!"
                    #print "[+]【Wafid】get waf finger false: "+self._nowaf
            else:
                continue
                #print "head type search ..."
        
        if self.check_resp(resp):
           return True
        return False

if __name__ == '__main__':
    print(banner)
    parser = optparse.OptionParser('usage: python %prog [options](eg: python %prog http://www.csecgroup.com/)')
    parser.add_option('-u', '--url', dest = 'url', type = 'string', help = 'target url')
    parser.add_option('-l', '--list', dest = 'list', default=False, action="store_true", help='List all WAFs that we are able to detect')

    (options, args) = parser.parse_args()
    if options.list== True:
        print "[+]【Wafid】WAFid can identify these WAFs:"
        for waf in wafdetectlist:
            print "  "+waf
        sys.exit()
    if options.url == None or options.url == "":
        parser.print_help()
        sys.exit()
    url =options.url
    wafidentify = wafid(url)
    wafidentify._run()

