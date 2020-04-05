import aiohttp
from bs4 import BeautifulSoup as bs
import os
import time
import sys
import asyncio

stop_flag=False

async def get_page(url):
    global stop_flag
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as resp:
                # print(resp.status)
                resp.raise_for_status()
                return await resp.text()
        except:
            stop_flag = True
            return None

def parse_page(page):
    try:
        soup = bs(page, 'html.parser')
        # print(soup.find_all('div',{'class':'divTableCell'}))
        try:
            data = soup.findAll("div", {"class": "tabcontent"})[0].find("ul").findAll("li")
        except:
            data = soup.findAll("div", {"class": "tabccontainer"})[0].findAll("li")
        links,imgs,desc=[],[],[]
        for i in data:
            isoup=bs(str(i), 'html.parser')
            links.append(isoup.find('a')['href'])
            imgs.append(isoup.findAll("div")[0].find('img')['src'])
            try:
                desc.append(isoup.findAll("div")[2].find("p").text)
            except:
                desc.append(isoup.findAll("div")[1].find("p").text)
        return data,links,imgs,desc
    except Exception as e:
        return None,None,None,None


async def async_run(loop):
    tasks=[]
    i=1
    print('\n'+"https://sarkariyojana.com/karnataka/")
    while not stop_flag and i<10:
        tasks.append((loop.create_task(get_page('https://sarkariyojana.com/karnataka/page/'+str(i))),i))
        i+=1
    for task,i in tasks:
        page = await task
        data,links,imgs,desc= parse_page(page)
        if data==None:
            return
        #print(data)
        print('page',i,':')
        print('\t',links)
        print('\t',imgs)
        print('\t',desc,'\n')

def main():
    try:
        start = time.time()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(async_run(loop))
        stop = time.time()
        time_taken = round((stop - start) * 100, 4)  # Gives in milliseconds upto four decimal places
        print("Time=" + str(time_taken))
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(repr(e)+'\n')


if __name__ == '__main__':
    main()
