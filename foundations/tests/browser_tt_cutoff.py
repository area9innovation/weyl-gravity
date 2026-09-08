"""Optional Chromium check; requires Playwright and installed google-chrome."""
from pathlib import Path
import json,time
from playwright.sync_api import sync_playwright
start=time.monotonic()
root=Path(__file__).resolve().parents[1] / 'site'
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox'])
 page=browser.new_page(viewport={'width':1100,'height':850})
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto((root/'cutoff-positivity.html').as_uri())
 assert 'Full export currently rejected.' in page.locator('body').inner_text()
 assert '12-coefficient candidate' in page.locator('body').inner_text()
 for k in (4,8,128):
  page.locator('#cutoff').fill(str(k));page.locator('#cutoff').dispatch_event('input')
  assert page.locator('#next').inner_text()==str(k+1)
  assert page.locator('#negative').inner_text()=='−1/'+str(8*(k+1)*k)
  from fractions import Fraction
  cost=Fraction((k-1)**3,8*k)
  assert page.locator('#cost').inner_text()==str(cost.numerator)+'/'+str(cost.denominator)
 for href in page.locator('a').evaluate_all('(links)=>links.map(a=>a.getAttribute("href"))'):
  assert (root/href).exists(),href
 page.screenshot(path='/tmp/tt-cutoff-desktop.png',full_page=True)
 page.set_viewport_size({'width':390,'height':844})
 assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
 page.screenshot(path='/tmp/tt-cutoff-mobile.png',full_page=True)
 page.goto((root/'index.html').as_uri())
 assert page.locator('.hero-note').filter(has_text='Full export currently rejected:').count()==1
 assert not errors,errors
 browser.close()
result={'command':'PYTHONPATH=/tmp/tt-browser-deps python3 foundations/tests/browser_tt_cutoff.py', 'elapsed_seconds':round(time.monotonic()-start,6),'status':'PASS','checks':['Chromium page load without JS errors','slider K=4,8,128 exact expectations and rational lower bound','all case-study links exist','390px mobile viewport has no horizontal overflow','current rejection and partial repair displayed on case study and index']}
Path('/tmp/tt-browser-receipt.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
