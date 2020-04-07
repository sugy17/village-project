import aiohttp
from bs4 import BeautifulSoup as bs
import asyncio
import html2markdown
#from markdownify import markdownify as md
import re
import sys
#import markdown2 as mm

stop_flag = False
regx_stripHtmlTags=re.compile(r'<.*?>|::after')
regx2=re.compile(r'<li>[^<][^(<.*?>)]*<[^(/)]')

# storing scheme data as [original_link,img_link,one_line_desc,required_content(in html form from orginal_link)]
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

def add_strong(tag,soup):
    try:
        tag.attrs = {}
        tag.unwrap()
        new = soup.new_tag('strong')
        new.string = soup.new_string(tag.text)
        # tag.wrap(soup.new_tag('strong'))
        tag.clear()
        tag.insert(0, new)
    except Exception as e:
        print(repr(e))
        return

def html_table_convert(table):
    new_str = ""
    itr_flag = False
    table_soup = bs(table, 'html.parser')
    for row in table_soup.findAll('tr'):
        if len(row.findAll('th')) != 0:
            itr_flag = True
            for col in row.findAll('th'):
                new_str += '\n|' + str(html2markdown.convert(str(col.text)))
            new_str += '|\n'
            for dummy in row.findAll('th'):
                new_str += '|---'
            new_str += '|\n'
        for col in row.findAll('td'):
            new_str += '|' + str(html2markdown.convert(str(col.text)))
        new_str += '|\n'
        if not itr_flag:
            itr_flag = True
            for dummy in row.findAll('td'):
                new_str += '|---'
            new_str += '|\n'
    return new_str

def parse_scheme_desc(page):
    soup = bs(page, 'html.parser')
    html_data = soup.find("article")
    soup = bs(str(html_data), 'html.parser')
    for tag in soup.findAll('div', {"class": "googleads"}):
        tag.replaceWith('')
    for tag in soup.findAll('div', {"class": "mobaddiv250 abc"}):
        tag.replaceWith('')
    for tag in soup.findAll('div', {"class": "stats"}):
        tag.replaceWith('')
    for tag in soup.findAll('span'):
        tag.replaceWith('')
    for tag in soup.findAll('noscript'):
        tag.replaceWith('')
    for tag in soup.findAll('nav'):
        tag.unwrap()
    for tag in soup.findAll('img'):
        temp = tag['src']
        tag.attrs = {}
        tag['src'] = temp
    try:
        soup.find('a', {"class": "saveaspdf"}).replaceWith('')
    except:
        xyz = 0
    for tag in soup.findAll('b'):
        try:
            tag.attrs = {}
            tag.unwrap()
            new = soup.new_tag('strong')
            new.string = soup.new_string(tag.text)
            # tag.wrap(soup.new_tag('strong'))
            tag.clear()
            tag.insert(0, new)
        except Exception as e:
            print(repr(e))
            continue
    for tag in soup.findAll('a'):
        try:
            temp = tag['href']
            tag.attrs = {}
            if not str(temp).startswith('#'):
                tag['href'] = temp
            else:
                tag.unwrap()
            new = soup.new_tag('strong')
            new.string = soup.new_string(tag.text)
            # tag.wrap(soup.new_tag('strong'))
            tag.clear()
            tag.insert(0, new)
        except Exception as e:
            print(repr(e))
            continue
    for tag in soup.findAll('center'):
        add_strong(tag,soup)
    for tag in soup.findAll('p'):
        try:
            tag.attrs = {}
        except Exception as e:
            print(repr(e))
            continue
    soup.article.unwrap()
    for tag in soup.findAll('div'):
        tag.unwrap()
    for tag in soup.findAll('ul'):
        tag.attrs = {}
    # for tag in soup.findAll('li'):
    #     add_strong(tag, soup)
    for tag in soup.findAll():
        try:
            tag.attrs.pop('class')
        except:
            continue
    for tag in soup.findAll('small'):
        tag.name = 'p'
    for tag in soup.findAll('table'):
        tag.attrs = {}
    #return str(soup)
    html_text=str(soup)
    # while regx2.search(html_text):
    #     text = regx2.findall(html_text)[0]
    #     print(text)
    #     text=text[:4]+'<strong>'+text[4:]
    #     text=text[-len(text):-2]+'</strong>'+text[-2:]
    #     html_text=regx2.sub(text, html_text)
    html_data = html2markdown.convert(re.sub(r".*<br/>.*", '<br>',html_text ))
    tables=re.findall(r'<table>.*</table>',html_data,re.DOTALL)
    for table in tables:
        new_str=html_table_convert(table)
        #print(new_str)
        re.sub(r'<table>.*</table>',new_str, html_data, re.DOTALL)
        #temp=md(str(table),convert='table')
        html_data=regx_stripHtmlTags.sub('',re.sub(r'<table>.*</table>',new_str,html_data,1,re.DOTALL))
        #print(temp)
    return "\n".join(html_data.split("\n")[:-4]),"\n".join(html_text.split("\n")[:-5])


async def async_run(loop):
    global stop_flag
    global schemes
    schemes = []
    i = 1
    # print('\n' + "https://sarkariyojana.com/karnataka/")
    while not stop_flag and i < 2:
        task = loop.create_task(get_page('https://sarkariyojana.com/karnataka/page/' + str(i)))
        page = await task
        data, links, imgs, desc = parse_page(page)
        if data == None:
            continue
        #links=[links[2]] #########################
        task=loop.create_task(get_page(links[int(sys.argv[1])]))
        page = await task
        md_data,html_data = parse_scheme_desc(page)
        if(sys.argv[2]=='0'):
            print(html_data)
        else:
            print(md_data)
        i += 1


def main():
    global schemes
    try:
        #start = time.time()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(async_run(loop))
        #stop = time.time()
        #ime_taken = round((stop - start) * 100, 4)  # Gives in milliseconds upto four decimal places
        #print("Time=" + str(time_taken))
        #print(schemes[int(sys.argv[1])][3])
    except Exception as e:
        print(repr(e) + '\n')


if __name__ == '__main__':
    main()
