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
    expected=['Introduction','Questions','Theory journeys','Research atlas','Papers','Dictionary']
    for route in ['index.html','wave.html','questions.html','papers.html','dictionary.html','atlas.html','cutoff-positivity.html']:
        page.goto(base+route+'?audience=general')
        assert page.locator('nav[aria-label="Main navigation"]').count()==1
        assert page.locator('.site-header nav a').all_text_contents()==expected
        menu=page.locator('#perspective-menu');assert not menu.get_attribute('open')==''
        menu.locator('summary').first.click()
        page.locator('input[name=audience][value=physics]').check()
        assert page.locator('#perspective-current').inner_text()=='General + Physics'
        page.keyboard.press('Escape');assert menu.get_attribute('open') is None
        assert page.locator('main').count()==1
    page.goto(base+'index.html?audience=general')
    assert page.locator('.intro-provenance a').count()==2
    for edition in ['general','physics','mathematics','specialist']:
        assert page.locator('.reading-section > [data-edition='+edition+']').count()==8
    page.locator('#perspective-menu > summary').focus();page.keyboard.press('Enter')
    assert page.locator('#perspective-menu').get_attribute('open')==''
    page.locator('h1').click();assert page.locator('#perspective-menu').get_attribute('open') is None
    page.screenshot(path='/tmp/unified-introduction-desktop.png')
    page.locator('#perspective-menu > summary').click();page.screenshot(path='/tmp/unified-menu-desktop.png')
    page.goto(base+'dictionary.html?audience=general')
    assert 'Arithmetical Comprehension Axiom' in page.locator('#aca [data-edition=general]').inner_text()
    assert 'Recursive Comprehension Axiom' in page.locator('#rca [data-edition=general]').inner_text()
    page.locator('#aca [data-edition=general] a.dictionary-crosslink').first.click()
    assert page.url.endswith('#rca') and 'audience=general' in page.url
    assert page.locator('#rca [data-edition=general]').is_visible()
    page.set_viewport_size({'width':390,'height':844})
    for route in ['index.html','wave.html','questions.html','papers.html','dictionary.html','cutoff-positivity.html']:
        page.goto(base+route)
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'),route
        page.locator('#perspective-menu > summary').click()
        box=page.locator('.perspective-panel').bounding_box()
        assert box['x']>=0 and box['x']+box['width']<=390,route
    page.goto(base+'index.html');page.screenshot(path='/tmp/unified-introduction-mobile.png')
    page.locator('#perspective-menu > summary').click();page.screenshot(path='/tmp/unified-menu-mobile.png')
    assert not errors,errors
    browser.close()
 print('PASS: shared navigation, compact keyboard menu, persistent selection, eight-section introduction parity, abbreviation expansions, dictionary crosslinks and mobile layout')
finally:
 server.shutdown();server.server_close()
