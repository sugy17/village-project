"""
    This module extracts data and opens end point.Also updates
    the data periodically every 24 hrs.
"""

import asyncio
import multiprocessing
import re
import base64
from flask_cors import CORS
from flask import Flask, json, request
import aiohttp
from bs4 import BeautifulSoup

import html2markdown
from markdownify import markdownify as md


class SCHEME:
    """This class contains all scheme data related behaviours and objects"""

    def __init__(self, schemeid, link, title, img):
        # self.index_details={}   #futre optimisation
        self.link = link
        self.schemeid = schemeid
        self.title = title
        self.img = img
        self.content = {}
        # self.nested_content = {}
        self.html_data = ""

    img_regx = re.compile(r'(?:!\[(.*?)\]\((.*?)\)).*', re.DOTALL)
    comments = re.compile(r'<!--.*-->')
    stop_flag = False
    LIST = []

    def parse_contentPage(self) -> None:
        """Parses html content into required json"""
        soup = SCHEME.clean_content(self.html_data)
        element_count = -1
        section_count = 0
        section = 'section-' + str(0)
        js = {
            section: {}
        }
        for child in soup.recursiveChildGenerator():
            name = getattr(child, 'name', None)
            parents = [getattr(p, 'name', None) for p in child.find_parents()]
            # if 'br/'==name or 'br'==name or 'br /'==name:
            #     print(parents, '------------', 'linebreak-n', '::', "linebreak")
            #     continue
            if name is not None:
                if name == 'p' and 'li' not in parents:
                    part = md(str(child))
                    res = SCHEME.img_regx.search(part)
                    part = SCHEME.img_regx.sub(' ', part)
                    element_count += 1
                    js[section]['normal-' + str(element_count)] = part
                    if res is not None:
                        element_count = SCHEME.image_handle(js, section, element_count, res.group(0))
                    # print(parents, '------------', child.name, '::', md(str(child)))
                elif name[0] == 'h' and len(name) == 2:
                    section = 'section-' + str(section_count)
                    section_count += 1
                    element_count = -1
                    js[section] = {}
                elif name == 'table':
                    element_count += 1
                    SCHEME.table_handle(child, js, section, element_count)
                elif name == 'li':
                    part = md(str(child))
                    res = SCHEME.img_regx.search(part)
                    part = SCHEME.img_regx.sub(' ', part)
                    element_count += 1
                    js[section]['listElement-' + str(element_count)] = part
                    if res is not None:
                        element_count = SCHEME.image_handle(js, section, element_count, res.group(0))
                    # print(parents, '------------', 'li', '::', md(str(child)))
                elif name == 'img' and 'p' not in parents and 'li' not in parents:
                    element_count = SCHEME.image_handle(js, section, element_count, md(str(child)))
            elif not child.isspace() and len(child) > 0:  # leaf node, don't print spaces
                if 'table' in parents or 'li' in parents or 'a' in parents or 'article' in child.parent.name or 'p' in parents:
                    continue
                element_count += 1
                if len(child.parent.name) == 2 and child.parent.name[0] == 'h':
                    js[section]['title-' + str(element_count)] = html2markdown.convert(
                        str(child.parent).replace('\n', ' '))
                else:
                    js[section][child.parent.name + '-' + str(element_count)] = html2markdown.convert(
                        str(child.parent).replace('\n', ' '))
        # print(self.schemeid, js)
        self.content = js
        # self.nested_content = js

    @staticmethod
    def image_handle(js: dict, section: str, element_count: int, img_md: str) -> int:
        """Check if markdown data contains image and add it to json"""
        img_link = re.search(r'\(.*\)', img_md, re.DOTALL)
        img_desc = re.sub(r'.*\)', '', img_md, re.DOTALL)
        element_count += 1
        js[section]['image-' + str(element_count)] = {'link': img_link.group(0)[1:][:-1],
                                                      'textUnderImage': img_desc}
        return element_count

    @staticmethod
    def table_handle(child, js, section, element_count) -> None:
        """add table into the json (dict)"""
        table = []
        for i in child.findAll('tr'):
            row = []
            for j in i.children:
                if not str(j).isspace():
                    row.append(md(j))
            table.append(row)
        js[section]['table-' + str(element_count)] = {'row': len(table),
                                                      'column': len(table[0]),
                                                      'data': table}

    # js[section]['table-' + str(element_count)] = tables[table_ctr]
    # print('table::',tables[table_ctr])

    @staticmethod
    def clean_content(page: str) -> BeautifulSoup:
        """Extracts neccesary html content and removes ads and other unnecessary components"""
        soup = BeautifulSoup(page, "html.parser")
        soup = BeautifulSoup(SCHEME.comments.sub("", str(soup.findAll("article")[0])), "html.parser")
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
        tag = soup.find("a", {"class": "saveaspdf"})
        if tag is not None:
            tag.replaceWith("")
        for tag in soup.findAll("img"):
            temp = tag["src"]
            tag.attrs = {}
            tag["src"] = temp
        for tag in soup.findAll():
            if "src" in tag.attrs:
                temp = tag["src"]
                tag.attrs = {}
                tag["src"] = temp
            elif "href" in tag.attrs:
                temp = tag["href"]
                tag.attrs = {}
                if not str(temp).startswith("#"):
                    tag["href"] = temp
            else:
                tag.attrs = {}
        for tag in soup.findAll('small'):
            tag.name = 'p'
        for tag in soup.findAll('div'):
            tag.unwrap()
        soup.findAll("p")[-1].replaceWith("")
        return soup

    @staticmethod
    async def async_prepare_content(loop) -> None:
        """Prepare the deatiled description for all schemems"""
        # scheme_link=[scheme_link[0]]
        for scheme in SCHEME.LIST:
            page = await loop.create_task(SCHEME.get_page(scheme.link))
            scheme.html_data = page
            scheme.parse_contentPage()

    @staticmethod
    def parse_IndexPage(page: str) -> tuple:
        """Parses the page containing the list of schemes"""
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
                divs = isoup.findAll("div")
                imgs.append(divs[0].find("img")["src"])
                try:
                    desc.append(divs[2].find("p").text)
                except:
                    desc.append(divs[1].find("p").text)
            return links, imgs, desc
        except:
            return None, None, None

    @staticmethod
    async def async_prepare_index(loop) -> None:
        """Create short details about schemes in SCHEME.LIST """
        tasks = []
        i = 1
        # print('\n' + "https://sarkariyojana.com/karnataka/")
        while not SCHEME.stop_flag and i < 5:
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
            img_tasks = []
            j = 0
            for link in links:
                img_tasks.append((loop.create_task(SCHEME.get_page(imgs[j], True)), j))
                j += 1
            for img_task, j in img_tasks:
                img = await img_task
                if img is None:
                    img = await loop.create_task(SCHEME.get_page(imgs[j], True))
                link = links[j]
                img = base64.b64encode(img).decode("utf-8")
                title = desc[j]
                SCHEME.LIST.append(SCHEME(len(SCHEME.LIST), link, title, img))
                j += 1

    @staticmethod
    async def get_page(url: str, get_blob=False):
        """gets a page"""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url) as resp:
                    resp.raise_for_status()
                    return await resp.read() if get_blob else await resp.text()
            except:
                SCHEME.stop_flag = True
                return None


# end of SCHEME def


# setting up end point
app = Flask(__name__)
CORS(app)


@app.route("/content", methods=['POST'])
def send_content() -> json:
    """recive json containing schemeid and send scheme content"""
    try:
        req_data = request.get_json()  # schemeid = i  #
        schemeid = int(req_data['schemeId'])
        data = app.config['shared_data'][int(schemeid)].content
        return json.jsonify(data)  # c.OrderedDict(scheme_content[int(i)])#scheme_content[int(i)]
    except IndexError:
        return json.jsonify(
            message="please wait...updating"
        )
    except Exception as e:
        return json.jsonify(
            message=repr(e)
        )


@app.route("/list")
def send_list() -> json:
    """send a list of schemes and relevent data"""
    try:
        li = []
        for scheme in app.config['shared_data']:
            li.append(
                {
                    'title': scheme.title,
                    'image': scheme.img,
                    'schemeid': scheme.schemeid}
            )
        return json.jsonify(li)
    except Exception as e:
        return json.jsonify(
            message=str(
                repr(e)
            )
        )


def execute_flask(shared_list):
    """function to execute flask"""
    app.config['shared_data'] = shared_list
    app.run()


async def main():
    """
        main function - starts flask on a new process and updates
                        data every 24 hrs.
    """
    multiprocessing.set_start_method('spawn')
    shared_list = multiprocessing.Manager().list()
    multiprocessing.Process(target=execute_flask, args=(shared_list,), name='FlaskProcess').start()
    my_loop = asyncio.get_event_loop()
    while True:
        # gathering data
        SCHEME.stop_flag = False
        SCHEME.LIST.clear()
        await SCHEME.async_prepare_index(my_loop)
        await SCHEME.async_prepare_content(my_loop)
        shared_list[:] = []
        shared_list.extend(SCHEME.LIST)
        await asyncio.sleep(86400)


if __name__ == "__main__":
    asyncio.run(main())
