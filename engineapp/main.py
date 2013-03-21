#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

# See the License for the specific language governing permissions and
# limitations under the License.

import webapp2
import cgi
from google.appengine.api import users
from BeautifulSoup import BeautifulSoup
import cStringIO
import gzip
import re
from time import gmtime, strftime
from datetime import *
import urllib2


form = """<form method ="post" action = "/testform">
<table border="0" cellpadding="5" cellspacing="0" style="border:5px double aliceblue;font-family:century gothic;">
<tr><td><b><i>Enter Travel details</i></b></td></tr>
<tr><td>Depart from (Enter airport code):</td><td> <input type="text" name="departure"></td></tr>
<tr><td>Arrive at (Enter airport code):</td><td> <input type="text" name="arrival"></td></tr>
<tr><td>Departure date (YYYY-MM-DD):</td><td> <input type="text" name="depdate"></td></tr>
<tr><td>Return date (YYYY-MM-DD):</td><td> <input type="text" name="retdate"></td></tr>
<tr><td><input type="submit" value="Scrape"></td></tr>
</table>
</form>
"""

class MainHandler(webapp2.RequestHandler):
    def get(self):
        ##self.response.headers['Content-Type']='text/plain'
        self.response.write(form)

class TestHandler(webapp2.RequestHandler):
        
    def post(self):
        ## req from the browser
        departure = self.request.get("departure")
        arrival = self.request.get("arrival")
        dep_date = self.request.get("depdate")
        ret_date = self.request.get("retdate")
        
        newScrape = Scraper(dep_date,ret_date, departure, arrival)
        resp = newScrape.generateRequest()
        if type(resp)==str:
            self.response.write(resp)
        else:
            result_outbound, result_inbound = newScrape.parseResponse(resp)
            
            if result_outbound:
                self.response.write('<html><body><b><i><u><font size="4" face="Century gothic">Cheapest Outbound Price</font></u></i></b><pre>')
                self.response.write('<font size="4" face="Century gothic"><b>'+departure+' '+ 'TO'+' '+arrival+'</b></font>')
                self.response.out.write('<br><font size="3" face="Century gothic">')
                for e in result_outbound:
                    self.response.write(''.join(e))
                    self.response.out.write('<br>')
                self.response.out.write('</font><hr></pre></body></html>')
               
            if result_inbound:
                self.response.write('<html><body><b><i><u><font size="4" face="Century gothic">Cheapest Inbound Price</font></u></i></b><pre>')
                self.response.write('<font size="4" face="Century gothic"><b>'+arrival+' '+ 'TO'+' '+departure+'</b></font>')
                self.response.out.write('<br><font size="2" face="Century gothic">')
                for e in result_inbound:
                    self.response.write('<font size="3" face="Century gothic">')
                    self.response.write(''.join(e)+'</font>')
                    self.response.out.write('<br>')
                self.response.out.write('</font></pre></body></html>')
            if not (result_outbound or(result_outbound and result_inbound)):
                self.response.write('<html><body><b><i><font size="4" face="Century gothic">No results for selected data</font></i></b><pre></font></pre></body></html>')
                


class Scraper:
    req={}
    def __init__(self, to, fro, fromair, toair):
        self.to = to
        self.fro = fro
        self.fromair = fromair
        self.toair = toair
        self.is_one_way = False
        
    def generateRequest(self):
        currtime=strftime("%Y-%m-%d %H:%M:%S", gmtime())
        if self.fro=='':
            self.is_one_way = True

        h = {'Host':'www.easyjet.com',
         'Connection': 'keep-alive',
         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
         'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.40 Safari/537.17',
         'Referer': 'http://www.easyjet.com/en/searchpod.mvc/showborderless?aclwidth=279&flightsearch='+self.fromair+'|*LO|%to|%fro|1|0|0|false||',
         'Accept-Encoding': 'gzip,deflate,sdch',
         'Accept-Language': 'en-US,en;q=0.8',
         'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
         'Cookie': 'idb*=%7B%22departure%22%3Anull%2C%22when%22%3Anull%2C%22flag%22%3Anull%2C%22price%22%3Anull%2C%22fromDate%22%3Anull%2C%22toDate%22%3Anull%2C%22customDate%22%3Anull%2C%22mapLocation%22%3Anull%2C%22destination%22%3Anull%2C%22moveMap%22%3Anull%2C%22region%22%3A%22en-gb%22%7D; VisitorRecognition=gid=00f49016-3778-4e7d-8d9d-464f05fcbef8&mid=0&usl=; ejCC_3=v=4961037125396553316&i=-8588384021820206177; __qca=P0-1591738809-1363204702135; cae_browser=desktop; vuvuzela=ver%3A1%3Bvar%3A0; CMSPOD=POD1; odb*='+self.fromair+'; lang2012=en-gb; mm_homepage_en_ref=1; website#lang=en; serverID=2; bkng=11UmFuZG9tSVYkc2RlIyh9YTSWZm0K41CGzIdmyBDZiXKPygoG8aEcniPfI%2BxSytje274uWFam2KmR2kgO8GXKXJjCEb5IZws2oZzGTkLSdHxz8b3BQrutAqpOTMzC%2BD2IGrAk%2B14H50J4gKqvZTZ6oinS9x%2FB%2Bjqh3zqF9Yr%2BnIMiMinhNyV0XQfbcB1Dz3clla2vBvg8iMewaz0WTYs8DCtMOvjl6Vxcuwq3ifXFCdsF3gsfNAVPok5gV3uWerLeXehmhv6AqAKf0CS8%2FdL347ZcQTW45J%2BO9UreZjnjo6nlBy%2FqAESC2z2Imbo1mxQOJIEDh5cwT5YIa%2BOd29QHilojIu3yNneWnFmwhkvvK%2Fxm5o41GFZFuW4d%2BLEGE%2BkmBs%2BvlAU5IwA5W2DMKjWB0q5GaTXuk3hKSHlJy9RTb%2FU%3D; ASP.NET_SessionId=caahhbfpyhf40j2nytmg0r55; ej20SearchCookie=ej20Search_4='+self.fromair+'|*LO|'+self.to+'T00:00:00|'+self.fro+'T00:00:00|1|0|0|False||4|'+currtime+'Z; mmcore.tst=0.203; mmcore.mmact=; mmid=-765864009%7CMgAAAApFd/x+1wgAAA%3D%3D; mmcore.srv=ldnvwcgeu08; mmcore.pd=1350278633%7CMgAAAAoBQkV3/H7XCHbf7d4JAFxe1MNx8M9IAAsAAAADWoRAPO7PSAAAAAD/////ANcICQAAAAAAAQEAAgAABxkAAAcZAAAHGQAAAQD/CwAA632qbtcI/////wDXCNkI//8PAAAAAAABMTMAANZEAAAAAAAAAUU%3D; mmcore.uat=Flex_Date%3Dno%3BPAX_Type%3DSingle; __utma=257744927.946436784.1363204701.1363385108.1363447246.9; __utmb=257744927.29.9.1363447546937; __utmc=257744927; __utmz=257744927.1363204701.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)'}

        error_message = 'One or both given dates are invalid, please enter valid dates(YYYY-MM-DD) after '+ str(date.today())
        new_to=''
        new_from=''
        try:
            curr_date = date.today()
            dep_date = datetime.strptime(self.to,"%Y-%m-%d")
            if not self.is_one_way:
                ret_date = datetime.strptime(self.fro,"%Y-%m-%d")
                if(dep_date.date() > curr_date and ret_date.date() > curr_date):
                    new_to = dep_date.strftime("%d/%m/%Y")
                    new_from = ret_date.strftime("%d/%m/%Y")
            else:
                if (dep_date.date() > curr_date):
                    new_to = dep_date.strftime("%d/%m/%Y")
        except ValueError:
            return error_message
        
        w = (self.fromair, self.toair, new_to, new_from)
        conn=urllib2.Request("http://www.easyjet.com/links.mvc?dep=%s&dest=%s&dd=%s&rd=%s&apax=1&pid=www.easyjet.com&cpax=0&ipax=0&lang=EN&isOneWay=off" %w, headers=h)
        response = urllib2.urlopen(conn)
        return response

    def returnResults(self, code):
        result_list=[]
        for tag in code.findAll('span',{'class':'priceSmaller targetPrice'}):
            
            if (tag.findPreviousSiblings('span',{'class':'title'})):
                dates=str(tag.findParents('a')[0].findParents('li')[0].findParents('ul')[0].findPreviousSiblings('span')[0])
                result_list.append(dates)
                match = re.findall(r'\£\d+', str(tag))
                if match:
                    result_list.append(match)
                match2 = re.findall(r'([\w]{3}\s\d+\:\d+)', str(tag.findNextSiblings('span')))
                for time in match2:
                    result_list.append(time)
        return result_list

        
    def parseResponse(self, response):
        outbound =[]
        inbound =[]
        if response.info().get('Content-Encoding') == 'gzip':
            buf = cStringIO.StringIO(response.read())
            f = gzip.GzipFile(fileobj = buf)
            data = f.read()
            pool = BeautifulSoup(data)
            first_div = pool.find('div',{'id':'OutboundFlightDetails'})
            if first_div:
                outbound+=self.returnResults(first_div)
            if not self.is_one_way:
                second_div = pool.find('div',{'id':'ReturnFlightDetails'})
                if second_div:
                    inbound+=self.returnResults(second_div)
                    
        return outbound, inbound


app = webapp2.WSGIApplication([('/', MainHandler ),
                              ('/testform', TestHandler)],
                              debug=True)
            

