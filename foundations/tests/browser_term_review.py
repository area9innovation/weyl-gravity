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
    page.goto(base+'term-review.html?audience=mathematics&scope=ladder')
    page.wait_for_selector('.term-candidate')
    page.locator('#term-search').fill('causal support')
    card=page.locator('.term-candidate').filter(has=page.get_by_text('causal support',exact=True)).first
    card.locator('summary').click();card.locator('input').check()
    assert card.locator('mark').first.inner_text().casefold()=='causal support'
    with page.expect_download() as pending:page.locator('#download-brief').click()
    brief=json.loads(Path(pending.value.path()).read_text())
    assert set(brief['requirements'])=={'general','physics','mathematics','specialist'}
    c=brief['candidates'][0];assert c['selected_scope']=='ladder' and c['review_state']=='UNREVIEWED'
    for ctx in c['contexts']:assert ctx['text'][ctx['start']:ctx['end']].casefold()=='causal support'
    page.locator('#term-search').fill('');page.locator('#term-coverage').select_option('DICTIONARY_MATCH_REVIEW_SENSE')
    page.locator('.term-candidate summary').first.click()
    page.get_by_role('link',name='Read dictionary entry:').first.click()
    assert 'audience=mathematics' in page.url and 'dictionary.html' in page.url
    page.goto(base+'term-review.html?scope=ladder');page.wait_for_selector('.term-candidate')
    page.locator('#term-scope').select_option('matrix');page.wait_for_function("document.querySelector('#review-status').textContent.includes('extracted here')")
    assert 'scope=matrix' in page.url
    page.screenshot(path='/tmp/term-review-desktop.png')
    page.set_viewport_size({'width':390,'height':844})
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
    page.screenshot(path='/tmp/term-review-mobile.png')
    page.locator('#term-scope').select_option('papers')
    page.wait_for_function("document.querySelector('#review-status').textContent.includes('extracted here')")
    assert page.locator('.term-candidate').count()>0
    page.route('**/term-candidates-papers.json.gz',lambda route:route.fulfill(status=503,body='Unavailable'))
    page.reload()
    page.wait_for_function("document.querySelector('#review-status').textContent.includes('Could not load')")
    assert not errors,errors
    browser.close()
 print('PASS: term contexts, four-perspective brief, dictionary navigation, scope loading, mobile bounds and fetch failure')
finally:server.shutdown();server.server_close()
