#!/usr/bin/python2
# 2014-12-24T15:10:24+0000
import random

def RR(x,y):
    return random.randint(x,y)

def RC(x):
    return random.choice(x)

def genJunkstr(len):
    str = ""
    for i in range(len):
        str += chr(RR(39,128))
    return str

def genAttr():
    attrs = ["hidden", "high", "href", "hreflang", "http-equiv",
                    "icon", "id", "ismap", "itemprop", "keytype", "kind",
                    "label", "lang", "language", "list", "loop", "low",
                    "manifest", "max", "maxlength", "media", "method", "min",
                    "multiple", "name", "novalidate", "open", "optimum",
                    "pattern", "ping", "placeholder", "poster", "preload",
                    "pubdate", "radiogroup", "readonly", "rel", "required",
                    "reversed", "rows", "rowspan", "sandbox", "spellcheck",
                    "scope", "scoped", "seamless", "selected", "shape", "size",
                    "sizes", "span", "src", "srcdoc", "srclang", "srcset",
                    "start", "step", "style", "summary", "tabindex", "target",
                    "title", "type", "usemap", "value", "width", "wrap",
                    "border", "buffered", "challenge", "charset", "checked",
                    "cite", "class", "code", "codebase", "color", "cols",
                    "colspan", "content", "contenteditable", "contextmenu",
                    "controls", "coords", "data", "data-*", "datetime",
                    "default", "defer", "dir", "dirname", "disabled",
                    "download", "draggable", "dropzone", "enctype", "for",
                    "form", "formaction", "headers", "height", "accept",
                    "accept-charset", "accesskey", "action", "align", "alt",
                    "async", "autocomplete", "autofocus", "autoplay",
                    "autosave", "bgcolor"]
    rval = " "
    for x in range(0, RR(0, len(attrs))):
        j = RR(0,9)
        if 0 <= j <= 7:
            rval += RC(attrs)
        if j == 8:
            rval += genJunkstr(RR(0, 10));
        if j == 9:
            rval += genBadval()

        j = RR(0,3)
        if j == 0:
            rval += "='" + genBadval() + "' "
        if j == 1:
            rval += "='' "
        if j == 2:
            rval += "='" + genJunkstr(RR(0, 200)) + "' "
        if j == 3:
            rval += " "

    return rval

def genTag():
    tags = ["!--", "--", "!DOCTYPE", "a", "abbr", "acronym",
                    "address", "applet", "area", "article", "aside", "audio",
                    "b", "base", "basefont", "bdi", "bdo", "big", "blockquote",
                    "body", "br", "button", "canvas", "caption", "center",
                    "cite", "code", "col", "colgroup", "datalist", "dd", "del",
                    "details", "dfn", "dialog", "dir", "div", "dl", "dt", "em",
                    "embed", "fieldset", "figcaption", "figure", "font",
                    "footer", "form", "frame", "frameset", "h1", "h2", "h3",
                    "h4", "h5", "h6", "head", "header", "hgroup", "hr", "html",
                    "i", "iframe", "img", "input", "ins", "kbd", "keygen",
                    "label", "legend", "li", "link", "main", "map", "mark",
                    "menu", "menuitem", "meta", "meter", "nav", "noframes",
                    "noscript", "object", "ol", "optgroup", "option", "output",
                    "p", "param", "pre", "progress", "q", "rp", "rt", "ruby",
                    "s", "samp", "script", "section", "select", "small",
                    "source", "span", "strike", "strong", "style", "sub",
                    "summary", "sup", "table", "tbody", "td", "textarea",
                    "tfoot", "th", "thead", "time", "title", "tr", "track",
                    "tt", "u", "ul", "var", "video", "wbr"]
    rval = ""

    j = RR(0,2)
    if j == 0:
        rval += "<" + RC(tags)
    if j == 1:
        rval += "<" + RC(tags) + genJunkstr(RR(0,10))
    if j == 2:
        rval += "</" + RC(tags)

    rval += genAttr() + ">"
    return rval

def genBadval():
    rval = ""

    j = RR(0,5)
    if j == 0:
        rval += "http://"
    if j == 1:
        rval += "javascript:"
    if j == 2:
        rval += "file://"
    if j == 3:
        rval += "news://"
    if j == 4:
        rval += genJunkstr(RR(0,50)) + "://"
    if j == 5:
        rval += ""

    return rval
#------------------------------------------------------------------------------#
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from time import time, sleep
from sys import argv, stdout
from subprocess import Popen

previous = ""
current = ""
RUNNING = True
ONESHOT = True
req = False
timeout = 0
count = 0

boiler1 = """
<script>window.addEventListener('load',function(){try {
t = document.getElementById("targ"); f = t.firstChild; f.focus(); 
f.hasChildNodes(); f.classList; f.hasAttribute("ABCDEFG");
t.replaceChild(f,test.lastChild); } catch (e) {} document.location.reload();
});</script><div id="targ">
"""
boiler2 = "</div>"

# SPEEDHACK TIME? LETS DO SOME PROFILING


ctime = time()
class myHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global count, current, previous, req
	previous = current
        current = genTag()
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        self.wfile.write(boiler1 + genTag() + boiler2)
        req = True
        count += 1
        return
    def log_message(self, format, *args):
	return

def crash():
    global server, oneshot
    curtime = time()
    fprev = "POSS_PREV_CRASH_%d.html" % curtime
    fcur = "POSS_CUR_CRASH_%d.html" % curtime
    print "Timeout detected!\nFuzz data written to files:\n\tcurrent iter:  %s\
\n\tprevious iter: %s" % (fprev, fcur)
    x = open(fcur, "w")
    x.write(current)
    x.close()
    x = open(fprev, "w")
    x.write(previous)
    x.close()
    if(ONESHOT):
        server.shutdown()
    else:
        init()

def timeoutCheck():
    global RUNNING, req, timeout, ctime, count
    while RUNNING and timeout < 5:
        if req == False:
            sleep(1)
            timeout += 1
        if req == True:
            req = False
            timeout = 0
	    if (count % 1000) == 0:
	        print "\033[100D%d attempts in %d seconds" % (count, time()-ctime),
	        ctime = time()
	        stdout.flush()
            sleep(1)
    if(timeout == 5):
        crash()

def init():
    global timeout
    print "Killing all chromium processes"
    Popen(["/usr/bin/killall", "chromium"])
    sleep(10)
    print "Starting chromium"
    Popen(["/usr/bin/chromium", "http://localhost:8080"])
    print "Restarting timeoutCheck thread"
    timeout = 0
    tc = Thread(target=timeoutCheck)
    tc.start()

if len(argv) > 1:
    if argv[1] == "forever":
        ONESHOT = False

server = HTTPServer(('', 8080), myHandler)
tc = Thread(target=timeoutCheck)
tc.start()

try:
    print "Fuzzing on port 8080, press ^C to exit"
    server.serve_forever()
except KeyboardInterrupt:
    global running
    running = False
    server.shutdown()
    RUNNING = False
