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
    page=browser.new_page(); errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto(base+'wave.html?audience=mathematics')
    term=page.locator('[data-edition=mathematics] .dictionary-term:visible').first
    term.wait_for(); term.focus()
    popup=page.locator('#dictionary-popup')
    assert popup.is_visible() and 'Mathematics:' in popup.inner_text()
    title=popup.locator('strong > a').first
    assert 'audience=mathematics' in title.get_attribute('href')
    destination=title.get_attribute('href')
    title.click()
    page.wait_for_url('**/'+destination)
    assert page.locator('.dictionary-entry').count()==1
    assert page.locator('input[name=audience]:checked').count()==1
    page.go_back();term.wait_for();term.focus()
    page.keyboard.press('Escape');assert not popup.is_visible()
    term.hover();assert popup.is_visible()
    popup.hover();page.wait_for_timeout(450);assert popup.is_visible()
    popup.get_by_role('link',name='Compare all four definitions').click()
    assert page.locator('input[name=audience]:checked').count()==4
    assert page.locator('.dictionary-entry .dictionary-term').count()==0
    page.goto(base+'dictionary.html?audience=general,physics,mathematics,specialist#aca')
    page.wait_for_url('**/term-aca.html?*')
    assert page.locator('.dictionary-entry').count()==1
    assert page.locator('#aca [data-edition=general] h3').count()>=3
    page.goto(base+'term-modulus.html?audience=general,mathematics')
    page.screenshot(path='/tmp/dictionary-expanded-desktop.png')
    page.goto(base+'atlas.html?audience=general,physics')
    page.wait_for_function("document.querySelector('#dictionary-popup') !== null")
    page.evaluate("""() => {
      const p=document.createElement('p');p.id='dictionary-probe';
      p.innerHTML='RCA₀ and convergence rate; Xmodulus <code>ACA₀</code> <a href="#">RCA₀</a>';
      document.body.append(p);
    }""")
    probe=page.locator('#dictionary-probe');page.wait_for_function("document.querySelectorAll('#dictionary-probe .dictionary-term').length === 2")
    assert probe.locator('code .dictionary-term,a .dictionary-term').count()==0
    probe.locator('.dictionary-term').first.click()
    assert 'General:' in popup.inner_text() and 'Physics:' in popup.inner_text()
    popup.get_by_text('More for General',exact=True).click()
    assert 'What a rulebook does' in popup.inner_text()
    popup.get_by_text('More for General',exact=True).click()
    page.set_viewport_size({'width':390,'height':844})
    probe.locator('.dictionary-term').first.click()
    box=popup.bounding_box();assert box['x']>=0 and box['x']+box['width']<=390
    page.screenshot(path='/tmp/dictionary-mobile.png')
    page.goto(base+'term-observable.html?audience=general,mathematics')
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
    assert page.locator('#observable [data-edition]:visible').count()==2
    page.screenshot(path='/tmp/dictionary-expanded-mobile.png')
    plain=browser.new_context(java_script_enabled=False).new_page()
    plain.goto(base+'dictionary.html')
    assert plain.locator('.dictionary-entry:visible').count()==0
    assert plain.locator('#dictionary-word-list li').count()==143
    plain.goto(base+'term-wave-equation.html')
    assert plain.locator('.dictionary-entry:visible').count()==1
    assert plain.locator('#wave-equation [data-edition=general]').is_visible()
    assert not plain.locator('#wave-equation [data-edition=physics]').is_visible()
    assert not errors,errors
    browser.close()
 print('PASS: perspective definitions, comparison, hover/focus/tap, Escape, dynamic atlas annotation, word boundaries, excluded elements and mobile bounds')
finally:
 server.shutdown();server.server_close()
