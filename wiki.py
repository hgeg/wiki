#!/usr/bin/env python
#-*- coding: utf-8 -*-
from flask import Flask, request, render_template, redirect
from flup.server.fcgi import WSGIServer
from misaka import Markdown, HtmlRenderer
from titlecase import titlecase
import misaka as m
import os, random

def fetch(key):
    try:
        return open('./pages/%s.md'%key.encode('utf-8')).read().decode('utf-8')
    except IOError: return ""

app = Flask(__name__)
app.debug = True

@app.route('/',methods=['GET'])
def index():
    pages = map(lambda fn: fn.split('.')[0], os.listdir('./pages'))
    recents = sorted(pages, key=lambda fn: os.stat('./pages/%s.md'%fn).st_ctime, reverse=True)[:5]
    try:
        randoms = random.sample(pages, 5)
    except: 
        randoms = []
    return render_template('main.html', recents=recents, randoms=randoms)

@app.route('/<string:key>/', methods=['GET'])
def page(key):
    md = fetch(key)
    if not md:
        return redirect('/create:'+key)
    content = Markdown(HtmlRenderer(flags=m.HTML_SKIP_HTML | m.HTML_HARD_WRAP), m.EXT_FOOTNOTES|m.EXT_STRIKETHROUGH)(md)
    data = {'content':content, 'key':key}
    return render_template('page.html',**data)

@app.route('/search',methods=['POST'])
def search():
    key = request.form['search'].lower().replace(' ','-')
    return page(key)

@app.route('/edit:<string:key>/',methods=['POST','GET'])
def edit(key):
    if request.method == 'POST':
        content = request.form['content']
        open('./pages/%s.md'%key.encode('utf-8'),'w').write(content.encode('utf-8'))
        return key
    else:
        data = {'content':fetch(key), 'key':key}
        return render_template('edit.html',**data)

@app.route('/create:<string:key>/',methods=['GET'])
def create(key):
    try:
        title = "%s (%s)"%tuple(titlecase(key.replace('-',' ')).split('_'))
    except:
        title = titlecase(key.replace('-',' '))
    data = {'content':"%s\n==========\n..."%title, 'key':key}
    return render_template('edit.html',**data)

if __name__ == '__main__':
    #app.run(host='0.0.0.0',port=9991,debug=True)
    WSGIServer(app).run()
