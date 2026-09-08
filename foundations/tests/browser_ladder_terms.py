"""Shared menu, introduction parity and contextual dictionary navigation."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]/'site'
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args): pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)))
threading.Thread(target=server.serve_forever,daemon=True).start()
base=f'http://127.0.0.1:{server.server_port}/'
try:
 with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1440,'height':1000});errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto(base+'atlas.html?audience=general#view=ladder')
    panel=page.locator('.ladder-terminology');panel.locator('summary').click()
    import json
    index=json.loads((ROOT/'ladder-terms.json').read_text())
    assert panel.locator('li').count()==index['term_count']
    for term in index['terms']:
        for match in term['matches']:
            text=page.locator('#ladder-'+match['level']).inner_text()
            assert match['text'] in text,match
    entry=panel.locator('li').filter(has_text='Coefficient-to-distribution comparison')
    assert 'Definition pending' in entry.inner_text()
    entry.get_by_role('link',name='L3',exact=True).click()
    assert 'termStage=L3_' in page.url and 'audience=general' in page.url
    assert page.locator('#ladder-L3_COEFFICIENT_WEAK_SOLUTION').evaluate('(node)=>node===document.activeElement')
    page.reload()
    page.wait_for_function("document.activeElement?.id === 'ladder-L3_COEFFICIENT_WEAK_SOLUTION'")
    assert page.locator('#ladder-L3_COEFFICIENT_WEAK_SOLUTION').evaluate('(node)=>node===document.activeElement')
    panel.locator('summary').click()
    panel.locator('li').filter(has_text='RCA₀').get_by_role('link',name='Related definition').click()
    assert 'dictionary.html?audience=general#rca' in page.url
    page.goto(base+'atlas.html?audience=general#view=ladder');panel.locator('summary').click()
    page.screenshot(path='/tmp/ladder-terminology-desktop.png')
    page.set_viewport_size({'width':390,'height':844})
    box=panel.bounding_box();assert box['width']<=390
    page.screenshot(path='/tmp/ladder-terminology-mobile.png')
    assert not errors,errors
    browser.close()
 print('PASS: every indexed source text is rendered, stage jumps and reload focus, dictionary links preserve perspective, and mobile index bounds')
finally:
 server.shutdown();server.server_close()
