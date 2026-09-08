"""Locate non-prose source spans before TeX normalization (not a TeX engine)."""
import re
import unicodedata
from foundations.build_term_inventory import normalize

MATH_ENVS={'equation','align','alignat','aligned','alignedat','gather','gathered','multline','flalign','eqnarray','displaymath','math','array','matrix','pmatrix','bmatrix','Bmatrix','vmatrix','Vmatrix','smallmatrix','split','cases'}
CODE_ENVS={'verbatim','Verbatim','lstlisting','minted','tikzpicture','pgfpicture','picture','filecontents'}
SKIP_COMMANDS={'label','ref','eqref','pageref','autoref','cref','Cref','vref','url','path','includegraphics','input','include','bibliography','bibliographystyle','author','affiliation','address','email','date','documentclass','usepackage','newcommand','renewcommand','providecommand','DeclareMathOperator','newtheorem','setlength','addtolength','definecolor','texttt','nolinkurl','end','cert'}
TOKEN=re.compile(r'\\begin\s*\{([^{}]+)\}|\\[([]|(?<!\\)\$\$?|\\([A-Za-z@]+)\*?')
AUTHOR=re.compile(r'\b(?:[A-Z]\.\s*)+[A-Z][\w’\'-]+(?:\s+et\s+al\.)?|\b[A-Z][\w’\'-]+\s+et\s+al\.',re.UNICODE)

def escaped(text,pos):
    count=0;pos-=1
    while pos>=0 and text[pos]=='\\':count+=1;pos-=1
    return count%2==1

def group_end(text,start,opening='{',closing='}'):
    depth=0
    for i in range(start,len(text)):
        if escaped(text,i):continue
        if text[i]==opening:depth+=1
        elif text[i]==closing:
            depth-=1
            if depth==0:return i+1
    return len(text)

def command_end(text,start):
    pos=start
    while True:
        next_pos=pos
        while next_pos<len(text) and text[next_pos].isspace():next_pos+=1
        if next_pos>=len(text) or text[next_pos] not in '[{':return pos
        opening=text[next_pos];pos=group_end(text,next_pos,opening,']' if opening=='[' else '}')

def canonical(text):
    return re.sub(r'[^a-z0-9]','',unicodedata.normalize('NFKC',normalize(text)).casefold())

def prose_text(text):
    # Any surviving marked math is an exact registered dictionary alias.
    text=re.sub(r'\\([_&#])',r'\1',text)
    return normalize(text.replace(r'\(',' ').replace(r'\)',' ').replace('$',' ')).replace(r'\%','%')

def source_spans(raw,aliases=(),markdown=False,citations=()):
    """Return disjoint prose ranges and auditable excluded spans in raw offsets.

    Unclosed recognized math/code regions are excluded to EOF, never guessed
    to be prose. Named concepts aren't removed merely for containing a surname.
    """
    excluded=[];kept=[];chars=list(raw)
    def mask(start,end,reason):
        if end<=start:return
        excluded.append({'start':start,'end':end,'reason':reason})
        for i in range(start,end):
            if chars[i]!='\n':chars[i]=' '
    for citation in sorted(set(citations),key=lambda s:(-len(s),s)):
        if citation:
            for m in re.finditer(re.escape(citation),raw):mask(m.start(),m.end(),'BIBLIOGRAPHIC_RECORD')
    if markdown:
        for m in re.finditer(r'^\s*(`{3,}|~{3,}).*$',raw,re.M):
            if not ''.join(chars[m.start():m.end()]).strip():continue
            close=re.search(r'^\s*'+re.escape(m[1][0])+r'{'+str(len(m[1]))+r',}\s*$',raw[m.end():],re.M)
            mask(m.start(),m.end()+close.end() if close else len(raw),'CODE')
        for m in re.finditer(r'^(#{1,6})\s+(?:References|Bibliography|Literature cited)\s*$',raw,re.M|re.I):
            end=re.search(r'^#{1,'+str(len(m[1]))+r'}\s',raw[m.end():],re.M)
            mask(m.start(),m.end()+end.start() if end else len(raw),'BIBLIOGRAPHY')
        for m in re.finditer(r'`[^`\n]+`|\[(?:@|\^)[^\]]+\]|\]\([^\n)]+\)',raw):mask(m.start(),m.end(),'CODE_OR_REFERENCE')
    # Remove comments without changing source positions; delimiters inside them
    # must not close a subsequent math environment.
    for m in re.finditer(r'(?<!\\)%[^\n]*',raw):
        if not markdown:mask(m.start(),m.end(),'COMMENT')
    text=''.join(chars);known={canonical(a) for a in aliases if canonical(a)}
    pos=0
    while True:
        m=TOKEN.search(text,pos)
        if not m:break
        start=m.start();pos=m.end()
        if escaped(text,start):continue
        if m[1]:
            env=m[1];base=env.rstrip('*')
            reason='MATH' if base in MATH_ENVS else 'CODE' if base in CODE_ENVS else 'BIBLIOGRAPHY' if base=='thebibliography' else None
            if not reason:
                end=command_end(text,pos) if base in {'tabular','tabularx','tabulary','longtable','minipage','multicols'} else pos
                mask(start,end,'STRUCTURAL_MARKUP');pos=end;continue
            pattern=re.compile(r'\\(begin|end)\s*\{'+re.escape(env)+r'\}')
            depth=1;end=len(text)
            for e in pattern.finditer(text,pos):
                depth+=1 if e[1]=='begin' else -1
                if depth==0:end=e.end();break
            mask(start,end,reason);excluded[-1]['unclosed']=depth!=0;pos=end
        elif m[0] in [r'\(',r'\[','$','$$']:
            close={r'\(':r'\)',r'\[':r'\]','$':'$','$$':'$$'}[m[0]]
            end=pos
            while True:
                end=text.find(close,end)
                if end<0:end=len(text);closed=False;break
                if not escaped(text,end):end+=len(close);closed=True;break
                end+=len(close)
            if closed and m[0] in [r'\(','$'] and canonical(text[pos:end-len(close)]) in known:
                kept.append({'start':start,'end':end,'reason':'REGISTERED_DICTIONARY_ALIAS'})
            else:
                mask(start,end,'MATH');excluded[-1]['unclosed']=not closed
            pos=end
        elif m[2] in {'hypertarget','href'}:
            while pos<len(text) and text[pos].isspace():pos+=1
            end=group_end(text,pos) if pos<len(text) and text[pos]=='{' else pos
            mask(start,end,'REFERENCE_OR_METADATA');pos=end
        elif m[2] in {'verb','lstinline'}:
            if pos<len(text) and text[pos]=='[':pos=group_end(text,pos,'[',']')
            if pos<len(text):
                delimiter=text[pos];end=text.find(delimiter,pos+1)
                end=end+1 if end>=0 else len(text)
                mask(start,end,'CODE');pos=end
        elif m[2] in {'def','gdef','edef','xdef'}:
            opening=text.find('{',pos);end=group_end(text,opening) if opening>=0 else len(text)
            mask(start,end,'MACRO_DEFINITION');pos=end
        elif m[2] and (m[2] in SKIP_COMMANDS or 'cite' in m[2].lower() or m[2]=='bibitem'):
            end=command_end(text,pos)
            reason='CITATION' if 'cite' in m[2].lower() or m[2]=='bibitem' else 'AUTHOR' if m[2] in {'author','affiliation','address','email'} else 'REFERENCE_OR_METADATA'
            mask(start,end,reason);pos=end
    # Attribution patterns are contextual, not a blacklist of scientific names.
    text=''.join(chars).replace('~',' ')
    for m in AUTHOR.finditer(text):mask(m.start(),m.end(),'AUTHOR_ATTRIBUTION')
    text=''.join(chars)
    for m in re.finditer(r'https?://[^\s<>}]+',text):mask(m.start(),m.end(),'URL')
    union=[]
    for span in sorted(excluded,key=lambda s:(s['start'],s['end'])):
        start,end=span['start'],span['end']
        if union and start<=union[-1][1]:union[-1]=(union[-1][0],max(end,union[-1][1]))
        else:union.append((start,end))
    prose=[];start=0
    for left,right in union:
        if start<left:prose.append((start,left))
        start=right
    if start<len(raw):prose.append((start,len(raw)))
    return prose,excluded,kept
