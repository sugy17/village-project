import html
from flask import Flask, json
import aiohttp
from bs4 import BeautifulSoup
import asyncio
import re
import base64
#import collections as c

table_ctr = -1
td_correction = re.compile('td_[^0-9]')
tr_correction = re.compile('tr_[^0-9]')
th_correction = re.compile('th_[^0-9]')
comments = re.compile(r'<!--.*-->')
# regx_stripHtmlTags=re.compile(r'<.*?>|::after')
# regx2=re.compile(r'<li>[^<][^(<.*?>)]*<[^(/)]')


def flatten_json(nested_json):
    out = {}
    tag_ctrs = {}

    def flatten(x, name='', key_name=''):
        global table_ctr
        #key_name=key_name.replace(str(1), 'one').replace(str(2), 'two').replace(str(3), 'three')
        if key_name == 'table':
            table_ctr += 1
        if type(x) is dict:
            for a in x:
                key_name = a
                flatten(x[a], name + a + '_', key_name)
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + '_', key_name)
                i += 1
        else:
            if x != "":
                try:
                    if name.endswith('text_'):
                        key_name = name.split('_')[-3]
                        # key_name = key_name.replace(str(1), 'one').replace(str(2), 'two').replace(str(3), 'three')
                        if key_name.isdigit():
                            key_name = 'text'
                except:
                    key_name = 'text'
                try:
                    tag_ctrs[key_name] += 1
                except:
                    tag_ctrs[key_name] = 0
                if 'table_' in name:
                    # try:
                    #     tag_ctrs[name.split('_table_')[-1]] += 1
                    # except:
                    #     tag_ctrs[name.split('_table_')[-1]] = 0
                    table_key = 'table_' + str(table_ctr) + '_' + name.split('_table_')[-1]
                    try:
                        m = td_correction.search(table_key)
                        table_key = table_key[:m.span()[0]] + 'td_0_' + table_key[m.span()[1] - 1:]
                        # table_key = tr_correction.sub('tr_0_', table_key)
                    except:
                        xyz = 0
                    try:
                        m = tr_correction.search(table_key)
                        table_key = table_key[:m.span()[0]] + 'td_0_' + table_key[m.span()[1] - 1:]
                        # table_key = tr_correction.sub('tr_0_', table_key)
                    except:
                        xyz = 0
                    try:
                        m = th_correction.search(table_key)
                        table_key = table_key[:m.span()[0]] + 'th_0_' + table_key[m.span()[1] - 1:]
                        # table_key = tr_correction.sub('tr_0_', table_key)
                    except:
                        xyz = 0
                    out[table_key] = x  # + str(tag_ctrs[key_name])] = x
                    return
                out[key_name + str(tag_ctrs[key_name])] = x

    flatten(nested_json)
    try:
        out.pop('href0')
        out.pop('a0')
    except:
        xyz = 0
    return out


class HTMLtoJSONParser(html.parser.HTMLParser):
    def __init__(self, raise_exception=True):
        html.parser.HTMLParser.__init__(self)
        self.doc = {}
        self.path = []
        self.cur = self.doc
        self.line = 0
        self.raise_exception = raise_exception

    @property
    def json(self):
        return self.doc

    @staticmethod
    def to_json(content, raise_exception=True):
        parser = HTMLtoJSONParser(raise_exception=raise_exception)
        parser.feed(content)
        return parser.json

    def handle_starttag(self, tag, attrs):
        self.path.append(tag)
        attrs = {k: v for k, v in attrs}
        if tag in self.cur:
            if isinstance(self.cur[tag], list):
                self.cur[tag].append({"__parent__": self.cur})
                self.cur = self.cur[tag][-1]
            else:
                self.cur[tag] = [self.cur[tag]]
                self.cur[tag].append({"__parent__": self.cur})
                self.cur = self.cur[tag][-1]
        else:
            self.cur[tag] = {"__parent__": self.cur}
            self.cur = self.cur[tag]

        for a, v in attrs.items():
            self.cur["" + a] = v
        self.cur["text"] = ""

    def handle_endtag(self, tag):
        if tag != self.path[-1] and self.raise_exception:
            raise Exception(
                "html is malformed around line: {0} (it might be because of a tag <br>, <hr>, <img .. > not closed)".format(
                    self.line))
        del self.path[-1]
        memo = self.cur
        self.cur = self.cur["__parent__"]
        self.clean(memo)

    def handle_data(self, data):
        self.line += data.count("\n")
        if "text" in self.cur:
            self.cur["text"] += data

    def clean(self, values):
        keys = list(values.keys())
        for k in keys:
            v = values[k]
            if isinstance(v, str):
                # print ("clean", k,[v])
                c = v.strip(" \n\r\t")
                if c != v:
                    if len(c) > 0:
                        values[k] = c
                    else:
                        del values[k]
        del values["__parent__"]


scheme_apis = []
keypos = ""
def parse_content(page):
    html_data=page
    soup = BeautifulSoup(page, 'html.parser')
    soup = BeautifulSoup(comments.sub('', str(soup.find('article'))), 'html.parser')
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
        # tag.unwrap()
        tag.name = 'p'
    for tag in soup.findAll('img'):
        temp = tag['src']
        tag.attrs = {}
        tag['src'] = temp
    try:
        soup.find('a', {"class": "saveaspdf"}).replaceWith('')
    except:
        xyz = 0
    for tag in soup.findAll('img'):
        temp = tag['src']
        tag.attrs = {}
        tag['src'] = temp
    for tag in soup.findAll():
        try:
            temp = tag['src']
            tag.attrs = {}
            tag['src'] = temp
        except:
            try:
                temp = tag['href']
                tag.attrs = {}
                if not str(temp).startswith('#'):
                    tag['href'] = temp
            except:
                tag.attrs = {}
    # for tag in soup.findAll('h1'):
    #     tag.name='###head'
    # for tag in soup.findAll('h2'):
    #     tag.name='##head'
    # for tag in soup.findAll('h3'):
    #     tag.name='#head'
    for tag in soup.findAll('b'):
        # tag.name='#bold'
        tag.unwrap()
    for tag in soup.findAll('a'):
        # tag.name='#bold'
        tag.unwrap()
    # for tag in soup.findAll('div'):
    #     tag.name='p'

    soup.findAll('p')[-1].replaceWith('')
    # print(soup.find_all()[0])
    content = str(soup)
    js = HTMLtoJSONParser.to_json(content, )
    #print(js)
    nested=js
    def parse(data):
        global scheme_apis, keypos
        for key, value in data.items():
            # print (str(key)+'/'+str(value))
            keypos += '/' + key
            if type(value) == type(str()):
                scheme_apis.append(str(keypos) + '==' + str(value))
            if type(value) == type(dict()):
                parse(value)
            elif type(value) == type(list()):
                for val in value:
                    if type(val) == type(str()):
                        scheme_apis.append(str(keypos) + '==' + str(value))
                        keypos = keypos.split('/')[:-1].join('/')
                        pass
                    elif type(val) == type(list()):
                        keypos = keypos.split('/')[:-1].join('/')
                        pass
                    else:
                        parse(val)

    js['article']['div'] = js['article'].pop('div')
    #parse(js)
    # print(js['article'])
    flat=flatten_json(js)
    print(flat)
    return flat,nested,html_data

stop_flag = False

scheme_link,scheme_img,scheme_desc,scheme_content,nested_scheme_content,html_scheme_data=[],[],[],[],[],[]
loop = asyncio.get_event_loop()


async def get_page(url,get_blob=False):
    global stop_flag
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as resp:
                resp.raise_for_status()
                return await resp.read() if get_blob else await resp.text()
        except:
            stop_flag = True
            return None

def parse_page(page):
    try:
        soup = BeautifulSoup(page, 'html.parser')
        # print(soup.find_all('div',{'class':'divTableCell'}))
        try:
            data = soup.findAll("div", {"class": "tabcontent"})[0].find("ul").findAll("li")
        except:
            data = soup.findAll("div", {"class": "tabccontainer"})[0].findAll("li")
        links, imgs, desc = [], [], []
        for i in data:
            isoup = BeautifulSoup(str(i), 'html.parser')
            links.append(isoup.find('a')['href'])
            imgs.append(isoup.findAll("div")[0].find('img')['src'])
            try:
                desc.append(isoup.findAll("div")[2].find("p").text)
            except:
                desc.append(isoup.findAll("div")[1].find("p").text)
        return links, imgs, desc
    except Exception as e:
        return  None, None, None

async def async_prepare_index(loop):
    global stop_flag
    global  scheme_link,scheme_img,scheme_desc
    tasks=[]
    i = 1
    # print('\n' + "https://sarkariyojana.com/karnataka/")
    while not stop_flag and i < 5:
        tasks.append((loop.create_task(get_page('https://sarkariyojana.com/karnataka/page/' + str(i))),i))
        i += 1
    for task,i in tasks:
        page = await task
        links, imgs, desc = parse_page(page)
        if links == None:
            continue
        tasks=[]
        j=0
        for link in links:
            tasks.append((loop.create_task(get_page(imgs[j], True)), j))
            j+=1
        for task,j in tasks:
            img = await task
            scheme_link.append(links[j])
            scheme_img.append(base64.b64encode(img).decode('utf-8'))
            scheme_desc.append(desc[j])
            j+=1

async def async_prepare_content(loop=loop):
    global scheme_content,scheme_link,nested_scheme_content,html_scheme_data
    #scheme_link=[scheme_link[0]]
    for link in scheme_link:
        page=await loop.create_task(get_page(link))
        json,nested,html_dat=parse_content(page)
        scheme_content.append(json)
        nested_scheme_content.append(nested)
        html_scheme_data.append(html_dat)

scheme_link,scheme_img,scheme_desc,scheme_content,nested_scheme_content,html_scheme_data=[],[],[],[],[],[]
stop_flag=False
loop = asyncio.get_event_loop()
loop.run_until_complete(async_prepare_index(loop))
loop.run_until_complete(async_prepare_content(loop))
#store data in files
# file_ctr=0
# for content in scheme_content:
#     json_object = json.dumps(c.OrderedDict(content), indent=4)
#     # Writing to sample.json
#     with open("scheme_data/"+str(file_ctr)+".json", "w") as outfile:
#         outfile.write(json_object)
#         outfile.close()
#     file_ctr += 1
# file_ctr=0
# for content in nested_scheme_content:
#     json_object = json.dumps(content, indent=4)
#     # Writing to sample.json
#     with open("nested_scheme_data/" + str(file_ctr) + ".json", "w") as outfile:
#         outfile.write(json_object)
#         outfile.close()
#     file_ctr+=1
# import io
# file_ctr=0
# for content in html_scheme_data:
#     #json_object = json.dumps(content, indent=4)
#     # Writing to sample.json
#     with io.open("html_scheme_data/"+str(file_ctr)+".txt", "w", encoding="utf-8") as f:
#         f.write(content)
#         f.close()
#     file_ctr += 1

app = Flask(__name__)

@app.route('/api/scheme<i>/content')
def  one_desc(i):
    global scheme_content
    try :

        return str(scheme_content[int(i)]) #c.OrderedDict(scheme_content[int(i)])#scheme_content[int(i)]
    except Exception as e: return str(repr(e))


@app.route('/api/list')
def  return_content():
    global scheme_desc,scheme_img
    try :   return json.jsonify({'desc':scheme_desc,'image':scheme_img})
    except Exception as e: return str(repr(e))

if __name__ == "__main__":
    app.run()
