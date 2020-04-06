import aiohttp
from bs4 import BeautifulSoup as bs, Tag
import os
import time
import sys
import asyncio

stop_flag = False

#storing scheme data as [original_link,img_link,one_line_desc,required_content(in html form from orginal_link)]
schemes = []


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
        links, imgs, desc = [], [], []
        for i in data:
            isoup = bs(str(i), 'html.parser')
            links.append(isoup.find('a')['href'])
            imgs.append(isoup.findAll("div")[0].find('img')['src'])
            try:
                desc.append(isoup.findAll("div")[2].find("p").text)
            except:
                desc.append(isoup.findAll("div")[1].find("p").text)
        return data, links, imgs, desc
    except Exception as e:
        return None, None, None, None


def parse_scheme_desc(page):
    soup = bs(page, 'html.parser')
    for tag in soup.findAll('div', {"class": "googleads"}):
        tag.replaceWith('')
    for tag in soup.findAll('div', {"class": "mobaddiv250 abc"}):
        tag.replaceWith('')
    for tag in soup.findAll('div', {"class": "stats"}):
        tag.replaceWith('')
    for tag in soup.findAll('noscript'):
        tag.unwrap()
    soup.find('a', {"class": "saveaspdf"}).replaceWith('')
    html_data = soup.find("article")
    return html_data


async def async_run(loop):
    global stop_flag
    global schemes
    schemes = []
    i = 1
    print('\n' + "https://sarkariyojana.com/karnataka/")
    while not stop_flag and i < 10:
        task = loop.create_task(get_page('https://sarkariyojana.com/karnataka/page/' + str(i)))
        page = await task
        data, links, imgs, desc = parse_page(page)
        if data == None:
            continue
        # print(data)
        print('page', i, ':')
        print('\t', links)
        print('\t', imgs)
        print('\t', desc, '\n')
        tasks, j = [], 0
        for link in links:
            tasks.append((loop.create_task(get_page(links[j])), j))
            j += 1
        for task, j in tasks:
            page = await task
            html_data = parse_scheme_desc(page)
            schemes.append((links[j], imgs[j], desc[j], html_data))
        i += 1


def main():
    global schemes
    try:
        start = time.time()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(async_run(loop))
        stop = time.time()
        time_taken = round((stop - start) * 100, 4)  # Gives in milliseconds upto four decimal places
        print("Time=" + str(time_taken))
        for i in schemes:
            print(i[2])
    except Exception as e:
        print(repr(e) + '\n')


if __name__ == '__main__':
    main()
