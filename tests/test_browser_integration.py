"""Real Chromium against a controlled changing-site fixture. Not live-provider certification."""
import json
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest.mock import patch
from resolver.browser import BrowserResolver

HTML = '''<html><title>Fixture catalogue</title><body>
<form onsubmit="event.preventDefault();document.getElementById('results').innerHTML='<button id=newResult onclick=showPlayer()>Example Film 2020</button>'">
<input type=search id=changedSearch placeholder="Search catalogue"><button>Search</button></form>
<div id=results></div><script>
function showPlayer(){const f=document.createElement('iframe');f.srcdoc="<button id='changedPlay' onclick=fetch('/film.m3u8')>Play Example Film</button>";document.getElementById('results').replaceChildren(f)}
</script></body></html>'''

class Website(BaseHTTPRequestHandler):
    challenge = False
    def log_message(self, *a): pass
    def do_GET(self):
        if self.path == '/film.m3u8':
            raw = b'#EXTM3U\n#EXT-X-TARGETDURATION:10\n'; mime = 'application/vnd.apple.mpegurl'
        else:
            raw = (('<input type=password>' if self.challenge else HTML)).encode(); mime = 'text/html'
        self.send_response(200);self.send_header('Content-Type', mime);self.send_header('Content-Length', str(len(raw)));self.end_headers();self.wfile.write(raw)

class Decisions:
    def __init__(self): self.calls = 0
    def decide(self, instruction, obs, image=None, **kw):
        self.calls += 1
        if obs['candidates']: return {'action': 'media', 'candidate': obs['candidates'][0]['id']}
        elements = [e for f in obs['frames'] for e in f['elements']]
        for label in ('Play Example Film', 'Example Film 2020'):
            target = next((e for e in elements if e['text'] == label), None)
            if target: return {'action': 'click', 'element': target['id']}
        target = next(e for e in elements if e['tag'] == 'input')
        # Fill and Enter use only the observed field; no assumed site selectors.
        action = 'enter' if obs['previous_actions'] and obs['previous_actions'][-1]['action'] == 'fill' else 'fill'
        return {'action': action, 'element': target['id']}

class RealBrowserTests(unittest.TestCase):
    def setUp(self):
        Website.challenge = False
        self.server = ThreadingHTTPServer(('127.0.0.1', 0), Website)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.url = 'http://127.0.0.1:' + str(self.server.server_port)
        self.request = {'url': self.url, 'title': 'Example Film', 'year': 2020, 'kind': 'movie'}
    def tearDown(self): self.server.shutdown();self.server.server_close()
    def test_search_iframe_media_and_replay(self):
        model = Decisions(); engine = BrowserResolver(model, headless=True)
        # This test alone permits its loopback fixture. Production public_url still refuses it.
        def fixture_only(url):
            if not url.startswith(self.url): raise ValueError('Fixture only')
            return url
        with patch('resolver.browser.public_url', side_effect=fixture_only):
            result = engine.resolve(self.request, threading.Event(), lambda p: None)
            self.assertEqual(result['status'], 'resolved_unverified')
            self.assertFalse(result['native_playback_verified'])
            self.assertTrue(result['stream']['url'].endswith('/film.m3u8'))
            self.assertEqual([s['action'] for s in result['recipe']['steps']], ['fill', 'enter', 'click', 'click'])
            first_calls = model.calls; model.calls = 0
            replayed = engine.resolve(self.request, threading.Event(), lambda p: None, result['recipe'])
            self.assertEqual(replayed['status'], 'resolved_unverified')
            self.assertLess(model.calls, first_calls)
    def test_access_challenge_stops_before_model(self):
        Website.challenge = True; model = Decisions()
        with patch('resolver.browser.public_url', side_effect=lambda u: u):
            result = BrowserResolver(model, headless=True).resolve(self.request, threading.Event(), lambda p: None)
        self.assertEqual(result['status'], 'blocked'); self.assertEqual(model.calls, 0)
