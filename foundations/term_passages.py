"""Readable indexed-prose views; source spans remain separate provenance."""
from html import escape
from html.parser import HTMLParser
import markdown

class SafeProse(HTMLParser):
    allowed={'p','strong','em','code','blockquote','ul','ol','li','h1','h2','h3','h4','h5','h6','hr','br','table','thead','tbody','tr','th','td','mark'}
    def __init__(self):super().__init__(convert_charrefs=True);self.parts=[]
    def handle_starttag(self,tag,attrs):
        if tag in self.allowed:self.parts.append('<'+tag+'>')
    def handle_endtag(self,tag):
        if tag in self.allowed and tag not in {'hr','br'}:self.parts.append('</'+tag+'>')
    def handle_data(self,data):self.parts.append(escape(data))

def render(text,start=None,end=None):
    if start is None:source=escape(text)
    else:source=escape(text[:start])+'<mark>'+escape(text[start:end])+'</mark>'+escape(text[end:])
    parser=SafeProse();parser.feed(markdown.markdown(source,extensions=['tables']));return ''.join(parser.parts)
