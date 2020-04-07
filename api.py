import subprocess

from flask import Flask
from flask import request


import os
import sys


app = Flask(__name__)

@app.route("/")
def hello():
    item_no=request.args.get('scheme')
    md = request.args.get('markdown')
    print(item_no)
    p = subprocess.Popen("C:\\Users\\Sugyan\\village-project\\venv\\Scripts\\python.exe scrap.py "+str(int(item_no))+" "+str(md), stdout=subprocess.PIPE)
    result = p.communicate()
    text = result[0].decode()
    return text
if __name__ == "__main__":
    app.run()