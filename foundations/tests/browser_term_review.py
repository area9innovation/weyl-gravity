"""Exercise contextual selection, exported briefs, navigation and fetch failure."""
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
import json,threading
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]/'site'
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)))
threading.Thread(target=server.serve_forever,daemon=True).start()
base=f'http://127.0.0.1:{server.server_port}/'
try:
 with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1440,'height':1000});errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto(base+'dictionary.html?audience=mathematics')
    assert page.locator('#dictionary-word-list li').count()==143
    assert page.locator('.dictionary-entry:visible').count()==0
    boxes=page.locator('#dictionary-word-list li').evaluate_all('(nodes)=>nodes.map(n=>{const r=n.getBoundingClientRect();return {x:r.x,y:r.y}})')
    assert boxes[1]['x']==boxes[0]['x'] and boxes[1]['y']>boxes[0]['y']
    assert any(b['x']>a['x'] and b['y']<a['y'] for a,b in zip(boxes,boxes[1:]))
    term=page.locator('#dictionary-word-list a').first
    term.focus()
    popup=page.locator('#dictionary-popup');popup.wait_for(state='visible')
    assert 'Mathematics:' in popup.inner_text()
    page.keyboard.press('Escape');assert not popup.is_visible()
    term.click();assert popup.is_visible() and '#' not in page.url
    with page.expect_navigation(wait_until='load'):
        popup.get_by_role('link',name='Compare all four definitions').click()
    assert page.locator('.dictionary-entry:visible').count()==1
    assert '/term-aca.html?' in page.url
    assert page.locator('#dictionary-word-list').count()==0
    page.locator('.dictionary-entry:visible .dictionary-back').click()
    assert page.locator('.dictionary-entry:visible').count()==0
    page.screenshot(path='/tmp/dictionary-compact-desktop.png')
    page.set_viewport_size({'width':390,'height':844})
    xs=page.locator('#dictionary-word-list li').evaluate_all('(ns)=>ns.map(n=>n.getBoundingClientRect().x)')
    assert len(set(xs))==1
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
    page.locator('#dictionary-word-list a').first.click()
    assert page.locator('#dictionary-popup').is_visible()
    page.screenshot(path='/tmp/dictionary-compact-mobile.png')
    page.keyboard.press('Escape')
    page.set_viewport_size({'width':1440,'height':1000})
    assert not page.locator('#editorial-inventory').evaluate('node=>node.open')
    assert page.locator('.term-candidate').count()==0
    assert not page.evaluate("performance.getEntriesByType('resource').some(r=>r.name.includes('term-candidates-'))")
    page.locator('#dictionary-search').fill('ACA_0')
    assert page.locator('#dictionary-word-list li:visible').all_text_contents()==['ACA₀']
    page.locator('#dictionary-search').fill('absemt')
    assert page.locator('#dictionary-word-list li:visible').count()==0
    page.locator('#dictionary-search').fill('')
    page.locator('#editorial-inventory > summary').click()
    page.wait_for_selector('.term-candidate')
    assert page.locator('#term-scope').input_value()=='all'
    assert not page.locator('#download-brief').is_visible()
    assert page.locator('.term-definition-status').first.is_visible()
    assert page.locator('.term-candidate .term-label').evaluate_all("nodes=>nodes.every(n=>/^\\p{L}/u.test(n.textContent))")
    assert page.evaluate("(() => {const terms=[...document.querySelectorAll('.term-candidate .term-label')].map(n=>n.textContent);const c=new Intl.Collator('en',{sensitivity:'base',numeric:true,ignorePunctuation:true});return terms.every((t,i)=>!i||c.compare(terms[i-1],t)<=0);})()")
    page.locator('#term-search').fill('ACA_0')
    assert page.locator('.term-candidate .term-label').all_text_contents()==['ACA₀']
    page.locator('.term-candidate').first.locator('summary').click()
    assert 'Also indexed as:' in page.locator('.term-candidate').first.inner_text()
    for word in ['absence','absent','absolute']:
        page.locator('#term-search').fill(word)
        assert word not in page.locator('.term-candidate .term-label').all_text_contents()
    page.locator('#term-search').fill('Abbott')
    assert page.locator('.term-candidate').count()==0
    page.locator('#term-search').fill('pointwise polynomial identity')
    assert page.locator('.term-candidate').count()==0
    page.goto(base+'term-review.html?audience=mathematics&scope=ladder')
    page.wait_for_url('**/dictionary.html?audience=mathematics&scope=ladder#terminology-index')
    page.locator('#editorial-inventory > summary').click()
    page.wait_for_selector('.term-candidate')
    page.locator('#term-search').fill('causal support')
    card=page.locator('.term-candidate').filter(has=page.get_by_text('causal support',exact=True)).first
    card.locator('summary').click()
    assert not card.locator('input').is_visible()
    page.locator('#editing-tools').check();card.locator('input').check()
    assert card.locator('mark').first.inner_text().casefold()=='causal support'
    with page.expect_download() as pending:page.locator('#download-brief').click()
    brief=json.loads(Path(pending.value.path()).read_text())
    assert set(brief['requirements'])=={'general','physics','mathematics','specialist'}
    c=brief['candidates'][0];assert c['selected_scope']=='ladder' and c['review_state']=='UNREVIEWED'
    for ctx in c['contexts']:assert ctx['text'][ctx['start']:ctx['end']].casefold()=='causal support'
    page.locator('#term-search').fill('');page.locator('#term-coverage').select_option('DICTIONARY_MATCH_REVIEW_SENSE')
    page.locator('.term-candidate summary').first.click()
    page.get_by_role('link',name='Read dictionary entry:').first.click()
    assert 'audience=mathematics' in page.url and 'term-' in page.url
    page.goto(base+'term-review.html?scope=ladder');page.locator('#editorial-inventory > summary').click();page.wait_for_selector('.term-candidate')
    page.locator('#term-scope').select_option('matrix');page.wait_for_function("document.querySelector('#review-status').textContent.includes('indexed here')")
    assert 'scope=matrix' in page.url
    page.screenshot(path='/tmp/term-review-desktop.png')
    page.set_viewport_size({'width':390,'height':844})
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
    page.screenshot(path='/tmp/term-review-mobile.png')
    page.locator('#term-scope').select_option('papers')
    page.wait_for_function("document.querySelector('#review-status').textContent.includes('indexed here')")
    assert page.locator('.term-candidate').count()>0
    page.route('**/term-candidates-papers.json.gz',lambda route:route.fulfill(status=503,body='Unavailable'))
    page.reload()
    page.locator('#editorial-inventory > summary').click()
    page.wait_for_function("document.querySelector('#review-status').textContent.includes('Could not load')")
    assert not errors,errors
    browser.close()
 print('PASS: global alphabetical dictionary, hidden editing tools, legacy redirect, term contexts, four-perspective brief, dictionary navigation, scope loading, mobile bounds and fetch failure')
finally:server.shutdown();server.server_close()
