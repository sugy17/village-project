import asyncio
import html
import multiprocessing
import re
import base64
from flask_cors import CORS
from flask import Flask, json, request, abort
import aiohttp
from bs4 import BeautifulSoup

import html2markdown
from markdownify import markdownify as md

from fuzzywuzzy import process
import pickle

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
        self.search_data=""

    img_regx = re.compile(r'(?:!\[(.*?)\]\((.*?)\)).*', re.DOTALL)
    comments = re.compile(r'<!--.*-->')
    stop_flag = False
    LIST = []

    async def parse_contentPage(self) -> None:
        """Parses html content into required json"""
        soup = SCHEME.clean_content(self.html_data)
        self.search_data=soup.text
        element_count = -1
        section_count = 0
        section = str(0).zfill(3) + '-section'
        js = {
            section: {}
        }
        for child in soup.recursiveChildGenerator():
            name = getattr(child, 'name', None)
            parents = [getattr(p, 'name', None) for p in child.find_parents()]
            if name is not None:
                if name == 'p' and 'li' not in parents :
                    part = md(str(child))
                    res = SCHEME.img_regx.search(part)
                    part = SCHEME.img_regx.sub(' ', part)
                    element_count += 1
                    js[section][str(element_count).zfill(3) + '-normal'] = html.unescape(part.rstrip())
                    if res is not None:
                        element_count = await SCHEME.image_handle(js, section, element_count, res.group(0))
                    # print(parents, '------------', child.name, '::', md(str(child)))
                elif name[0] == 'h' and len(name) == 2:
                    section = str(section_count).zfill(3) + '-section'
                    section_count += 1
                    element_count = -1
                    js[section] = {}
                elif name == 'table':
                    element_count += 1
                    SCHEME.table_handle(child, js, section, element_count)
                elif name == 'li':
                    part = md(str(child)).split('\n\t*')[0]
                    res = SCHEME.img_regx.search(part)
                    part = SCHEME.img_regx.sub(' ', part)
                    element_count += 1
                    js[section][str(element_count).zfill(3) + '-listElement'] = html.unescape(part.rstrip())
                    if res is not None:
                        element_count = await SCHEME.image_handle(js, section, element_count, res.group(0))
                    # print(parents, '------------', 'li', '::', md(str(child)))
                elif name == 'img' and 'p' not in parents and 'li' not in parents:
                    element_count = await SCHEME.image_handle(js, section, element_count, md(str(child)))
            elif not child.isspace() and len(child) > 0:  # leaf node, don't print spaces
                if 'table' in parents or 'li' in parents or 'a' in parents or 'article' in child.parent.name or 'p' in parents :
                    continue
                element_count += 1
                if len(child.parent.name) == 2 and child.parent.name[0] == 'h':
                    js[section][str(element_count).zfill(3) + '-title'] = html.unescape(html2markdown.convert(
                        str(child.parent).replace('\n', ' ')).rstrip().replace('\\[','[').replace('\\]',']'))
                elif child.parent.name =='[document]':
                    pass
                else:
                    js[section][str(element_count).zfill(3) + '-' + child.parent.name] = html.unescape(html2markdown.convert(
                        str(child.parent).replace('\n', ' ')).rstrip())
        if len(js)==1 and len(js['000-section'])==1:      ##incase necessary data is removed while cleaning
            soup = BeautifulSoup(self.html_data, "html.parser")
            soup = BeautifulSoup(SCHEME.comments.sub("", str(soup.findAll("article")[0])), "html.parser")
            self.search_data = soup.text
            section = '000-section'
            element_count = 0
            for child in soup.recursiveChildGenerator():
                name = getattr(child, 'name', None)
                parents = [getattr(p, 'name', None) for p in child.find_parents()]
                if name == 'p' and 'li' not in parents :
                    part = md(str(child))
                    res = SCHEME.img_regx.search(part)
                    part = SCHEME.img_regx.sub(' ', part)
                    element_count += 1
                    js[section][str(element_count).zfill(3) + '-normal'] = html.unescape(part.rstrip())
                    if res is not None:
                        element_count = await SCHEME.image_handle(js, section, element_count, res.group(0))
                    # print(parents, '------------', child.name, '::', md(str(child)))
                elif name == 'table':
                    element_count += 1
                    SCHEME.table_handle(child, js, section, element_count)
                elif name == 'li':
                    part = md(str(child)).split('\n\t*')[0]
                    res = SCHEME.img_regx.search(part)
                    part = SCHEME.img_regx.sub(' ', part)
                    element_count += 1
                    js[section][str(element_count).zfill(3) + '-listElement'] = html.unescape(part.rstrip())
                    if res is not None:
                        element_count = await SCHEME.image_handle(js, section, element_count, res.group(0))
                elif name == 'img' and 'p' not in parents and 'li' not in parents:
                    element_count = await SCHEME.image_handle(js, section, element_count, md(str(child)))
        #js = json.jsonify(js)
        self.content = js
        print(js)
        self.title = js['000-section']['000-title']

    @staticmethod
    async def image_handle(js: dict, section: str, element_count: int, img_md: str) -> int:
        """Check if markdown data contains image and add it to json (dict)"""
        img_link = re.search(r'\(.*\)', img_md)
        img_desc = re.sub(r'.*\)', '', img_md, re.DOTALL).rstrip()
        element_count += 1
        img_url=img_link.group(0)[1:][:-1]
        img = await SCHEME.get_img(img_url, True)
        try:
            img = base64.b64encode(img).decode('utf-8')
        except:
            print('error'+'\n\n'+img_url,'\n',js['000-section']['000-title'])
        if len(img_desc) > 0:
            js[section][str(element_count).zfill(3) + '-image'] = {'encoded_image': img,
                                                                   'textUnderImage': html.unescape(img_desc.rstrip())}
        else:
            js[section][str(element_count).zfill(3) + '-image'] = {'encoded_image': img}
        return element_count

    @staticmethod
    def table_handle(child, js, section, element_count) -> None:
        """add table into the json (dict)"""
        table = []
        for i in child.findAll('tr'):
            row = []
            for j in i.children:
                if not str(j).isspace():
                    row.append(html.unescape(md(j).rstrip()))
            table.append(row)
        js[section][str(element_count).zfill(3) + '-table'] = {'row': len(table),
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
    async def async_prepare_content() -> None:
        """Prepare the deatiled description for all schemems"""
        # scheme_link=[scheme_link[0]]
        for scheme in SCHEME.LIST:
            page = await asyncio.ensure_future(SCHEME.get_page(scheme.link))
            scheme.html_data = page
            await scheme.parse_contentPage()

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
    async def async_prepare_index() -> None:
        """Create short details about schemes in SCHEME.LIST """
        tasks = []
        i = 1
        # print('\n' + "https://sarkariyojana.com/karnataka/")
        while not SCHEME.stop_flag and i < 5:
            tasks.append(
                (
                    asyncio.ensure_future(
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
                img_tasks.append((asyncio.ensure_future(SCHEME.get_page(imgs[j], True)), j))
                j += 1
            for img_task, j in img_tasks:
                img = await img_task
                if img is None:
                    img = await asyncio.ensure_future(SCHEME.get_page(imgs[j], True))
                link = links[j]
                try:
                    img = base64.b64encode(img).decode("utf-8")
                except:
                    img = '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'
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

    @staticmethod
    async def get_img(url: str, get_blob=False):
        """get img from url"""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url) as resp:
                    resp.raise_for_status()
                    return await resp.read()
            except:
                return b'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'


# end of SCHEME def

# Setting up endpoints
app = Flask(__name__)
CORS(app)

@app.route("/content", methods=['POST'])
def send_content() -> json:
    """recive json containing schemeid and send scheme content"""
    try:
        req_data = request.get_json()  # schemeid = i  #
        schemeid = int(req_data['schemeId'])
        print(schemeid)
        data = app.config['shared_data'][int(schemeid)].content
        return json.jsonify(data)  # c.OrderedDict(scheme_content[int(i)])#scheme_content[int(i)]
    except IndexError:
        abort(503)
    except:
        abort(401)


@app.route("/list")
def send_list() -> json:
    """send a list of schemes and relevent data"""
    try:
        try:
            req_range = [int(i) for i in request.args.get('range').split('-')]
            req_range.sort()
        except:
            req_range = [0, len(app.config['shared_data'])]
        li = []
        for i in range(req_range[0],req_range[1]):
            try:
                scheme = app.config['shared_data'][i]
                li.append(
                    {
                        'title': scheme.title,
                        'encoded_image': scheme.img,
                        'schemeid': scheme.schemeid
                    }
                )
            except:
                pass
        # process = psutil.Process(os.getpid())
        # print(process.memory_info().rss)
        if len(li) == 0:
            abort(503)
        return json.jsonify(li)
    except:
        abort(401)


@app.route("/search")
def search() -> json:
    """recive json containing search key word and send scheme list"""
    try:
        phrase=request.args.get('phrase')
        #print(phrase)
        Ratios = process.extract(phrase, [str(i.schemeid).zfill(3)+i.search_data for i in app.config['shared_data']],limit=9)
        data=[]
        for i,ratio in Ratios:
            if ratio > 50 :
                data.append(
                    {
                        'title': app.config['shared_data'][int(i[:3])].title,
                        'encoded_image': app.config['shared_data'][int(i[:3])].img,
                        'schemeid': int(i[:3])
                    }
                )
        #print(*Ratios, sep='\n', end='\n')
        return json.jsonify(data)
    except IndexError:
        abort(503)
    except:
        abort(401)



def execute_flask(shared_list):
    """function to execute flask"""
    app.config['shared_data'] = shared_list
    # process = psutil.Process(os.getpid())
    # print(process.memory_info().rss)
    app.run()

async def main():
    """
        main function - starts flask on a new process and updates
                        data every 5 seconds.
    """
    multiprocessing.set_start_method('spawn')
    shared_list = multiprocessing.Manager().list()
    multiprocessing.Process(target=execute_flask, args=(shared_list,), name='FlaskProcess').start()
    while True:
        # gathering data
        SCHEME.stop_flag = False
        SCHEME.LIST.clear()
        #await SCHEME.async_prepare_index()
        #await SCHEME.async_prepare_content()
        await asyncio.sleep(2)
        SCHEME.LIST = pickle.load(open("SCHEMES.data", "rb"))
        #print('loaded pkl file')
        shared_list[:] = []
        shared_list.extend(SCHEME.LIST)
        await asyncio.sleep(70000)
        # process = psutil.Process(os.getpid())
        # print(process.memory_info().rss)



if __name__ == "__main__":
    my_loop = asyncio.get_event_loop()
    my_loop.run_until_complete(main())
