
import urllib2
from BeautifulSoup import BeautifulSoup
import cStringIO
import gzip
import re
from time import gmtime, strftime
from datetime import datetime 

def scrape(to,fro,fromair,toair,passengers):
    
    print to ,fro
    currtime=strftime("%Y-%m-%d %H:%M:%S", gmtime())
    isOneWay = False
    if fro=='':
        isOneWay = True
    
    h = {'Host':'www.easyjet.com',
         'Connection': 'keep-alive',
         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
         'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.40 Safari/537.17',
         'Referer': 'http://www.easyjet.com/en/searchpod.mvc/showborderless?aclwidth=279&flightsearch='+fromair+'|*LO|%to|%fro|1|0|0|false||',
         'Accept-Encoding': 'gzip,deflate,sdch',
         'Accept-Language': 'en-US,en;q=0.8',
         'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
         'Cookie': 'idb*=%7B%22departure%22%3Anull%2C%22when%22%3Anull%2C%22flag%22%3Anull%2C%22price%22%3Anull%2C%22fromDate%22%3Anull%2C%22toDate%22%3Anull%2C%22customDate%22%3Anull%2C%22mapLocation%22%3Anull%2C%22destination%22%3Anull%2C%22moveMap%22%3Anull%2C%22region%22%3A%22en-gb%22%7D; VisitorRecognition=gid=00f49016-3778-4e7d-8d9d-464f05fcbef8&mid=0&usl=; ejCC_3=v=4961037125396553316&i=-8588384021820206177; __qca=P0-1591738809-1363204702135; cae_browser=desktop; vuvuzela=ver%3A1%3Bvar%3A0; CMSPOD=POD1; odb*='+fromair+'; lang2012=en-gb; mm_homepage_en_ref=1; website#lang=en; serverID=2; bkng=11UmFuZG9tSVYkc2RlIyh9YTSWZm0K41CGzIdmyBDZiXKPygoG8aEcniPfI%2BxSytje274uWFam2KmR2kgO8GXKXJjCEb5IZws2oZzGTkLSdHxz8b3BQrutAqpOTMzC%2BD2IGrAk%2B14H50J4gKqvZTZ6oinS9x%2FB%2Bjqh3zqF9Yr%2BnIMiMinhNyV0XQfbcB1Dz3clla2vBvg8iMewaz0WTYs8DCtMOvjl6Vxcuwq3ifXFCdsF3gsfNAVPok5gV3uWerLeXehmhv6AqAKf0CS8%2FdL347ZcQTW45J%2BO9UreZjnjo6nlBy%2FqAESC2z2Imbo1mxQOJIEDh5cwT5YIa%2BOd29QHilojIu3yNneWnFmwhkvvK%2Fxm5o41GFZFuW4d%2BLEGE%2BkmBs%2BvlAU5IwA5W2DMKjWB0q5GaTXuk3hKSHlJy9RTb%2FU%3D; ASP.NET_SessionId=caahhbfpyhf40j2nytmg0r55; ej20SearchCookie=ej20Search_4='+fromair+'|*LO|'+to+'T00:00:00|'+fro+'T00:00:00|1|0|0|False||4|'+currtime+'Z; mmcore.tst=0.203; mmcore.mmact=; mmid=-765864009%7CMgAAAApFd/x+1wgAAA%3D%3D; mmcore.srv=ldnvwcgeu08; mmcore.pd=1350278633%7CMgAAAAoBQkV3/H7XCHbf7d4JAFxe1MNx8M9IAAsAAAADWoRAPO7PSAAAAAD/////ANcICQAAAAAAAQEAAgAABxkAAAcZAAAHGQAAAQD/CwAA632qbtcI/////wDXCNkI//8PAAAAAAABMTMAANZEAAAAAAAAAUU%3D; mmcore.uat=Flex_Date%3Dno%3BPAX_Type%3DSingle; __utma=257744927.946436784.1363204701.1363385108.1363447246.9; __utmb=257744927.29.9.1363447546937; __utmc=257744927; __utmz=257744927.1363204701.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)'}

    new_to = datetime.strptime(to, "%Y-%m-%d").strftime("%d/%m/%Y")
    if not isOneWay:
        new_from = datetime.strptime(fro, "%Y-%m-%d").strftime("%d/%m/%Y")
    else: new_from =''
    w = (fromair, toair, new_to, new_from)
    conn=urllib2.Request("http://www.easyjet.com/links.mvc?dep=%s&dest=%s&dd=%s&rd=%s&apax=1&pid=www.easyjet.com&cpax=0&ipax=0&lang=EN&isOneWay=off" %w, headers=h)

    response = urllib2.urlopen(conn)
    if response.info().get('Content-Encoding') == 'gzip':
        buf = cStringIO.StringIO(response.read())
        f = gzip.GzipFile(fileobj = buf)
        data = f.read()
        pool = BeautifulSoup(data)
        
        print 'Cheapest Outbound Price:'
        first_div = pool.find('div',{'id':'OutboundFlightDetails'})
        for e in first_div.findAll('span',{'class':'priceSmaller targetPrice'}):
            
            if (e.findPreviousSiblings('span',{'class':'title'})):
                    parenta=e.findParents('a')
                    parentli=parenta[0].findParents('li')
                    
                    parentul=parentli[0].findParents('ul')
                    siblingspan=parentul[0].findPreviousSiblings('span')
                    print siblingspan
                    match = re.findall(r'\£\d+', str(e))
                    if match:
                        print ''.join(match)
                    match2 = re.findall(r'([\w]{3}\s\d+\:\d+)', str(e.findNextSiblings('span')))
                    for a in match2:
                        print ''.join(a)
        if not isOneWay:    
            print 'Cheapest Inbound price:'
                    
scrape('2013-04-24','2013-04-27','EDI','LTN',2)




##divide the program into functions with a main
##fix the format thingy
##fix the if loop thingy
##maybe a basic error handling
##
##d = {'ome':1,
## 'TWo':2}
##t=(1,2)
##def hello(*t):
##    pass
