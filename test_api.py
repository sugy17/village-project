"""
    This module extracts data and opens end point.Also updates
    the data periodically every 24 hrs.
"""

import asyncio
import multiprocessing
import os
import sys

from flask_cors import CORS
from flask import Flask, json, request, abort


import pickle


from whoosh import index
from whoosh.qparser import QueryParser
import os
from whoosh.index import create_in
from whoosh.fields import *

def handle_exception(e, risk='notify'):
    if risk == 'notify':
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(fname, exc_tb.tb_lineno, exc_type, e)
    pass


REGIONS = ['karnataka', 'andhra-pradesh', 'arunachal-pradesh', 'assam', 'bihar',
           'chhattisgarh', 'delhi', 'goa', 'gujarat', 'haryana', 'himachal-pradesh', 'jammu-kashmir',
           'jharkhand', 'kerala', 'madhya-pradesh', 'maharashtra', 'manipur', 'meghalaya', 'mizoram',
           'odisha', 'punjab', 'rajasthan', 'tamilnadu', 'telangana', 'tripura', 'uttar-pradesh',
           'uttarakhand', 'west-bengal', 'central-government']

# Setting up endpoints
app = Flask(__name__)
CORS(app)


@app.route("/<region>/content")
def send_content(region) -> json:
    """recive json containing schemeid and send scheme content"""
    try:
        schemeid = request.args.get('schemeId')  # schemeid = i  #
        data = json.load(open(os.path.join('DATA', region, schemeid, 'content')))
        return json.jsonify(data)  # c.OrderedDict(scheme_content[int(i)])#scheme_content[int(i)]
    except IndexError as e:
        handle_exception(e)
        abort(503)
    except Exception as e:
        handle_exception(e)
        abort(401)


@app.route("/<region>/list")
def send_list(region) -> json:
    """send a list of schemes and relevent data"""
    try:
        offset = -1
        try:
            req_range = int(request.args.get('range'))
            try:
                fromSchemeid = request.args.get('fromSchemeid')
                offset = app.config['shared_keys'][region].index(fromSchemeid)
            except Exception as e:
                handle_exception(e)
                pass
        except Exception as e:
            handle_exception(e)
            req_range = len(app.config['shared_keys'][region])
        li = []
        try:
            for i in range(1, req_range + 1):
                li.append(json.load(
                    open(os.path.join('DATA', region, app.config['shared_keys'][region][i + offset], 'index'))))
        except Exception as e:
            handle_exception(e)
            pass
        if len(li) == 0:
            abort(503)
        return json.jsonify(li)
    except Exception as e:
        handle_exception(e)
        abort(401)


@app.route("/<region>/search")
def search(region) -> json:
    """recive get req containing search key word and send scheme list"""
    try:
        phrase = request.args.get('phrase')
        data = []
        ix = index.open_dir(os.path.join("indexdir", region))
        with ix.searcher() as searcher:
            query = QueryParser("content", ix.schema).parse(phrase)
            results = searcher.search(query)
            for hit in results:
                #print(hit['schemeId'])
                data.append(json.load(open(os.path.join('DATA', region,hit['schemeId'],'index'))))
        return json.jsonify(data)
    except IndexError as e:
        handle_exception(e)
        abort(503)
    except Exception as e:
        handle_exception(e)
        abort(401)


@app.route("/regions")
def send_regions():
    return json.jsonify(REGIONS)


def execute_flask(key_list):
    """function to execute flask"""
    app.config['shared_keys'] = key_list
    app.run(host="0.0.0.0")


async def main():
    """
        main function - starts flask on a new process and updates
                        data every 50000 seconds.
    """
    multiprocessing.set_start_method('spawn')
    shared_key_list = multiprocessing.Manager().dict({region: [] for region in REGIONS})
    multiprocessing.Process(target=execute_flask, args=(shared_key_list,), name='FlaskProcess').start()
    # load key data
    keys = {region: [] for region in REGIONS}
    try:
        keys = pickle.load(open("KEYS.data", "rb"))
    except Exception as e:
        handle_exception(e)
    while True:
        for region in REGIONS:
            new_data = []
            keys[region] = new_data + keys[region]
            shared_key_list[region] = keys[region].copy()
        await asyncio.sleep(50000)


if __name__ == "__main__":
    my_loop = asyncio.get_event_loop()
    my_loop.run_until_complete(main())
