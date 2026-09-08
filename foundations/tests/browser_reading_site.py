"""Audience navigation and legacy-link regression in real Chromium."""
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
import threading
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]/'site'
class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(QuietHandler,directory=str(ROOT)))
thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
base=f'http://127.0.0.1:{server.server_port}/'
try:
 with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox'])
    context=browser.new_context(viewport={'width':1440,'height':1000})
    page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto(base+'index.html')
    assert page.locator('h1').inner_text()=='What does it take to turn an equation into a prediction?'
    assert page.locator('#audience').input_value()=='general'
    assert page.locator('#matrixView').count()==0
    page.screenshot(path='/tmp/reading-introduction-desktop.png',full_page=True)
    page.goto(base+'wave.html?audience=mathematics#inputs')
    shared=page.locator('.shared-status').inner_text()
    for audience in ['general','physics','mathematics','specialist']:
        page.locator('#audience').select_option(audience)
        assert 'audience='+audience in page.url and page.url.endswith('#inputs')
        assert page.locator('#inputs [data-edition="'+audience+'"]').is_visible()
        assert page.locator('#inputs [data-edition]:visible').count()==1
        assert page.locator('.shared-status').inner_text()==shared
    page.get_by_role('link',name='Introduction',exact=True).click()
    assert page.locator('#audience').input_value()=='specialist'
    page.reload();assert page.locator('#audience').input_value()=='specialist'
    page.goto(base+'wave.html?audience=general#inputs');page.go_back()
    assert page.locator('#audience').input_value()=='specialist'
    page.goto(base+'wave.html?audience=unrecognized');assert page.locator('#audience').input_value()=='general'
    page.set_viewport_size({'width':390,'height':844})
    for route in ['index.html','wave.html?audience=mathematics','questions.html','papers.html']:
        page.goto(base+route);assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'),route
    page.goto(base+'wave.html?audience=mathematics');page.screenshot(path='/tmp/reading-wave-mobile.png',full_page=True)
    for fragment in ['view=ladder','view=passports','view=matrix&q=wave','f=WEAK_ARITHMETIC']:
        page.goto(base+'index.html#'+fragment);page.wait_for_url('**/atlas.html*')
        if 'ladder' in fragment:assert page.locator('#ladderView').is_visible()
        if 'passports' in fragment:assert page.locator('#passportsView').is_visible()
        if 'q=wave' in fragment:assert page.locator('#search').input_value()=='wave'
    page.goto(base+'atlas.html');page.screenshot(path='/tmp/reading-atlas-desktop.png')
    assert page.locator('.export-audit').is_visible()
    nojs=browser.new_context(java_script_enabled=False)
    static=nojs.new_page();static.goto(base+'index.html');assert static.locator('#question [data-edition="general"]').is_visible()
    assert not static.locator('#question [data-edition="specialist"]').is_visible()
    nojs.close()
    blocked=browser.new_context();blocked.add_init_script("Object.defineProperty(window, 'localStorage', {get(){throw new Error('blocked storage')}})")
    bp=blocked.new_page();bp.goto(base+'wave.html?audience=physics');assert bp.locator('#audience').input_value()=='physics'
    bp.locator('#audience').select_option('mathematics');assert 'audience=mathematics' in bp.url
    blocked.close();assert not errors,errors
    browser.close()
 print('PASS: default introduction, four editions, section preservation, shared status, persistence, history, mobile layout, legacy atlas links, no-JS reading and blocked-storage fallback')
finally:
 server.shutdown();server.server_close()
