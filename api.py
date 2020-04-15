from flask_cors import CORS
from flask import Flask, json, jsonify, request

import aiohttp
from bs4 import BeautifulSoup
import asyncio
import re
import base64
import html2markdown
from markdownify import markdownify as md

# import collections as c

img_regx=re.compile('(?:!\[(.*?)\]\((.*?)\)).*',re.DOTALL) #('(?:\\(|:\\s+)(?!http)([^\\s]+\\.(?:jpe?g|gif|png|svg|pdf))')#
comments = re.compile(r"<!--.*-->")

# regx_stripHtmlTags=re.compile(r'<.*?>|::after')
# regx2=re.compile(r'<li>[^<][^(<.*?>)]*<[^(/)]')

class SCHEME:
    def __init__(self, schemeid, link, title, img):
        # self.index_details={}   #futre optimisation
        self.link = link
        self.schemeid = schemeid
        self.title = title
        self.img = img
        self.content = {}
        #self.nested_content = {}
        self.html_data = ""

    LIST = []

    def parse_contentPage(self):
        soup=SCHEME.clean_content(self.html_data)
        tables,table,row=[],[],[]
        table_ctr=-1
        element_count=-1
        section_count=0
        section = 'section-' + str(0)
        js={}
        js[section]={}
        for k in soup.findAll('table'):
            table = []
            for i in k.findAll('tr'):
                row=[]
                for j in i.children:
                    if not str(j).isspace():
                        row.append(md(j))
                table.append(row)
            tables.append(table)
        #print(table)
        for child in soup.recursiveChildGenerator():
            name = getattr(child,'name',None)
            parents = [getattr(p, 'name', None) for p in child.find_parents()]
            # if 'br/'==name or 'br'==name or 'br /'==name:
            #     print(parents, '------------', 'linebreak-n', '::', "linebreak")
            #     continue
            if 'p'==name and 'li' not in parents:
                part = md(str(child))
                res = img_regx.search(part)
                part = img_regx.sub(' ', part)
                element_count += 1
                js[section]['normal-'+str(element_count)]=part
                try:
                    img_md = res.group(0)
                    img_link = re.search('\\(.*\\)', img_md, re.DOTALL)
                    img_desc = re.sub('.*\\)', '', img_md, re.DOTALL)
                    element_count += 1
                    js[section]['image-' + str(element_count)] = {}
                    js[section]['image-' + str(element_count)]['link'] = img_link.group(0)[1:][:-1]
                    try:
                        js[section]['image-' + str(element_count)]['textUnderImage'] = img_desc
                    except:
                        js[section]['image-' + str(element_count)]['textUnderImage'] = ""
                except:pass
                #js[section]['normal-'+str(element_count)]=html2markdown.convert(str(child))
                #print(parents, '------------', child.name, '::', md(str(child)))
                continue
            if name is not None :
                if name[0] == 'h' and len(name) == 2:
                    section = 'section-' + str(section_count)
                    section_count+=1
                    element_count=-1
                    js[section] = {}
                    continue
                elif 'table' == name:
                    table_ctr += 1
                    element_count += 1
                    js[section]['table-' + str(element_count)]={}
                    js[section]['table-' + str(element_count)]['row'] = len(tables[table_ctr])
                    js[section]['table-' + str(element_count)]['column'] = len(tables[table_ctr][0])
                    js[section]['table-' + str(element_count)]['data'] = tables[table_ctr]
                    #js[section]['table-' + str(element_count)] = tables[table_ctr]
                    element_count += 1
                    #print('table::',tables[table_ctr])
                    continue
                elif 'table' in parents:
                    continue
                elif 'li' == name:
                    part=md(str(child))
                    res=img_regx.search(part)
                    part = img_regx.sub(' ', part)
                    element_count += 1
                    js[section]['listElement-' + str(element_count)] = part
                    try:
                        img_md=res.group(0)
                        img_link=re.search('\\(.*\\)',img_md,re.DOTALL)
                        img_desc=re.sub('.*\\)','',img_md,re.DOTALL)
                        element_count += 1
                        js[section]['image-'+ str(element_count)]={}
                        js[section]['image-' + str(element_count)]['link'] = img_link.group(0)[1:][:-1]
                        try:
                            js[section]['image-' + str(element_count)]['textUnderImage']=img_desc
                        except: js[section]['image-' + str(element_count)]['textUnderImage']=""
                    except: pass
                    #js[section]['listElement-' + str(element_count)] = html2markdown.convert(str(child))
                    #print(parents, '------------', 'li', '::', md(str(child)))
                    continue
                elif 'img' == name and 'p' not in parents and 'li' not in parents:
                    try:
                        img_md = md(str(child))
                        img_link = re.search('\\(.*\\)', img_md, re.DOTALL)
                        img_desc = re.sub('.*\\)', '', img_md, re.DOTALL)
                        element_count += 1
                        js[section]['image-' + str(element_count)] = {}
                        js[section]['image-' + str(element_count)]['link'] = img_link.group(0)[1:][:-1]
                        try:
                            js[section]['image-' + str(element_count)]['textUnderImage'] = img_desc
                        except:
                            js[section]['image-' + str(element_count)]['textUnderImage'] = ""
                    except: pass
                    continue
            elif not child.isspace() and len(child) > 0 :  # leaf node, don't print spaces
                if 'table' in parents or 'li' in parents  or 'a' in parents or 'article' in child.parent.name or 'p' in [getattr(p, 'name', None) for p in child.find_parents()]:
                    continue
                #js[section][child.parent.name+'-'+str(element_count)]=md(str(child.parent))
                element_count += 1
                if len(child.parent.name)==2 and child.parent.name[0]=='h':
                    js[section]['title-'+str(element_count)]=html2markdown.convert(str(child.parent).replace('\n',' '))
                    continue
                js[section][child.parent.name+'-'+str(element_count)]=html2markdown.convert(str(child.parent).replace('\n',' '))
        print(js)
        self.content=js
        #self.nested_content = js

    @staticmethod
    def clean_content(page):
        soup = BeautifulSoup(page, "html.parser")
        soup = BeautifulSoup(comments.sub("", str(soup.findAll("article")[0])), "html.parser")
        for tag in soup.findAll("div", {"class": "googleads"}):
            tag.replaceWith("")
        for tag in soup.findAll("div", {"class": "mobaddiv250 abc"}):
            tag.replaceWith("")
        for tag in soup.findAll("div", {"class": "stats"}):
            tag.replaceWith("")
        for tag in soup.findAll("span"):
            tag.replaceWith("")
        for tag in soup.findAll("noscript"):
            tag.replaceWith("")
        for tag in soup.findAll("nav"):
            # tag.unwrap()
            tag.name = "div"
        for tag in soup.findAll("img"):
            temp = tag["src"]
            tag.attrs = {}
            tag["src"] = temp
        try:
            soup.find("a", {"class": "saveaspdf"}).replaceWith("")
        except:
            pass
        for tag in soup.findAll("img"):
            temp = tag["src"]
            tag.attrs = {}
            tag["src"] = temp
        for tag in soup.findAll():
            try:
                temp = tag["src"]
                tag.attrs = {}
                tag["src"] = temp
            except:
                try:
                    temp = tag["href"]
                    tag.attrs = {}
                    if not str(temp).startswith("#"):
                        tag["href"] = temp
                except:
                    tag.attrs = {}
        for tag in soup.findAll('small'):
            tag.name = 'p'
        for tag in soup.findAll('div'):
            tag.unwrap()
        soup.findAll("p")[-1].replaceWith("")
        return soup

    @staticmethod
    async def async_prepare_content(loop):
        # scheme_link=[scheme_link[0]]
        for scheme in SCHEME.LIST[2:3]:
            page = await loop.create_task(SCHEME.get_page(scheme.link))
            scheme.html_data = page
            scheme.parse_contentPage()

    @staticmethod
    def parse_IndexPage(page):
        try:
            soup = BeautifulSoup(page, "html.parser")
            # print(soup.find_all('div',{'class':'divTableCell'}))
            try:
                data = (
                    soup.findAll("div", {"class": "tabcontent"})[0].find("ul").findAll("li")
                )
            except:
                data = soup.findAll("div", {"class": "tabccontainer"})[0].findAll("li")
            links, imgs, desc = [], [], []
            for i in data:
                isoup = BeautifulSoup(str(i), "html.parser")
                links.append(isoup.find("a")["href"])
                imgs.append(isoup.findAll("div")[0].find("img")["src"])
                try:
                    desc.append(isoup.findAll("div")[2].find("p").text)
                except:
                    desc.append(isoup.findAll("div")[1].find("p").text)
            return links, imgs, desc
        except Exception as e:
            return None, None, None

    @staticmethod
    async def async_prepare_index(loop):
        global stop_flag
        tasks = []
        i = 1
        # print('\n' + "https://sarkariyojana.com/karnataka/")
        while not stop_flag and i < 2:
            tasks.append(
                (
                    loop.create_task(
                        SCHEME.get_page("https://sarkariyojana.com/karnataka/page/" + str(i))
                    ),
                    i,
                )
            )
            i += 1
        for task, i in tasks:
            page = await task
            links, imgs, desc = SCHEME.parse_IndexPage(page)
            if links is None or imgs is None:
                continue
            tasks = []
            j = 0
            for link in links:
                tasks.append((loop.create_task(SCHEME.get_page(imgs[j], True)), j))
                j += 1
            for task, j in tasks:
                img = await task
                link = links[j]
                img = base64.b64encode(img).decode("utf-8")
                title = desc[j]
                SCHEME.LIST.append(SCHEME(len(SCHEME.LIST), link, title, img))
                j += 1


    @staticmethod
    async def get_page(url, get_blob=False):
        global stop_flag
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url) as resp:
                    resp.raise_for_status()
                    return await resp.read() if get_blob else await resp.text()
            except:
                stop_flag = True
                return None


SCHEME.LIST.clear()
stop_flag = False
loop = asyncio.get_event_loop()
loop.run_until_complete(SCHEME.async_prepare_index(loop))
loop.run_until_complete(SCHEME.async_prepare_content(loop))
# store data in files
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
CORS(app)


@app.route("/api/content")
def send_content():
    try:
        req_data=request.get_json()
        schemeid = int(req_data['schemeId'])
        return json.jsonify(
            SCHEME.LIST[int(schemeid)].content)  # c.OrderedDict(scheme_content[int(i)])#scheme_content[int(i)]
    except Exception as e:
        return json.jsonify(message=str(repr(e)))


@app.route("/api/list")
def send_list():
    try:
        li = []
        for scheme in SCHEME.LIST:
            li.append({'title': scheme.title, 'image': scheme.img, 'schemeid': scheme.schemeid})
        return json.jsonify(li)
    except Exception as e:
        return json.jsonify(message=str(repr(e)))


if __name__ == "__main__":
    app.run()
