import ast
import copy
import json
import subprocess
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from resolver.browser import public_url, safe_url
from resolver.local_model import LocalModel
from resolver.source_repair import SourceRepair
from resolver.service import ResolverService, ServiceServer


class Model:
    def decide(self, *a, **kw):
        return {'reason': 'Search selector changed on observed page.', 'edits': [{'old': "SELECTOR = '.old'", 'new': "SELECTOR = '.new'"}]}


class Browser:
    def resolve(self, request, cancel, progress, recipe=None):
        progress({'stage': 'observed'})
        return {'status': 'resolved_unverified', 'native_playback_verified': False,
                'recipe': {'version': 1, 'site': request['url'], 'kind': request['kind'], 'steps': []}}


class LocalExtensionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.root = Path(self.tmp.name)
        self.repo = self.root / 'moviehub'; self.repo.mkdir()
        subprocess.run(['git', 'init', str(self.repo)], capture_output=True, check=True)
        subprocess.run(['git', '-C', str(self.repo), 'remote', 'add', 'origin', 'https://github.com/billyke2000s/moviehub.git'], check=True)
        self.rel = 'android-tv-launcher/app/src/main/python/moviehub_scrubs/providers/example.py'
        self.path = self.repo / self.rel; self.path.parent.mkdir(parents=True); self.path.write_text("SELECTOR = '.old'\n")
        self.source = SourceRepair(self.repo)
        self.service = ResolverService(self.root / 'data', Model(), Browser(), self.source)
    def tearDown(self): self.tmp.cleanup()
    def wait(self, job):
        for _ in range(200):
            out = self.service.dispatch('/v1/job', {'job_id': job}, False)
            if out['status'] != 'running': return out
            time.sleep(.005)
        self.fail('Job did not finish')
    def repair(self):
        r = self.service.dispatch('/v1/start', {'operation': 'repair', 'kind': 'movie', 'source_file': self.rel, 'diagnosis': 'Old selector does not exist on live page.'}, True)
        return r['job_id'], self.wait(r['job_id'])
    def test_source_proposal_apply_restart_and_rollback(self):
        key, job = self.repair()
        self.assertEqual(job['status'], 'patch_proposed'); self.assertNotIn('_before', json.dumps(job))
        self.assertEqual(self.path.read_text(), "SELECTOR = '.old'\n")
        args = {'job_id': key, 'action': 'source', 'proposal_digest': job['result']['proposal_digest']}
        with self.assertRaises(ValueError): self.service.dispatch('/v1/apply', args, False)
        self.assertEqual(self.service.dispatch('/v1/apply', args, True)['status'], 'patch_applied_unverified')
        self.assertEqual(self.path.read_text(), "SELECTOR = '.new'\n")
        self.service = ResolverService(self.root / 'data', Model(), Browser(), self.source)
        args['action'] = 'rollback'
        self.assertEqual(self.service.dispatch('/v1/apply', args, True)['status'], 'rolled_back')
        self.assertEqual(self.path.read_text(), "SELECTOR = '.old'\n")
    def test_stale_source_and_bad_digest_refused(self):
        key, job = self.repair()
        args = {'job_id': key, 'action': 'source', 'proposal_digest': 'wrong'}
        with self.assertRaises(ValueError): self.service.apply(args)
        args['proposal_digest'] = job['result']['proposal_digest']; self.path.write_text('# newer work\n')
        with self.assertRaises(ValueError): self.service.apply(args)
        self.assertEqual(self.path.read_text(), '# newer work\n')
    def test_scope_paths_and_wrong_repo(self):
        for relative in ['../secret.py', 'app/runtime.py', 'android-tv-launcher/app/src/main/python/moviehub_scrubs/providers/../../../../../../secret.py']:
            with self.assertRaises(ValueError): self.source.source(relative)
        subprocess.run(['git', '-C', str(self.repo), 'remote', 'set-url', 'origin', 'https://github.com/someone/other.git'], check=True)
        with self.assertRaises(ValueError): SourceRepair(self.repo)
    def test_no_import_or_execution_of_patch(self):
        class Evil:
            def decide(self, *a, **kw): return {'edits': [{'old': "SELECTOR = '.old'", 'new': 'invalid syntax ???'}]}
        with self.assertRaises(SyntaxError): self.source.propose(self.rel, 'test', Evil())
        self.assertEqual(self.path.read_text(), "SELECTOR = '.old'\n")
    def test_browser_recipe_persistence_and_noncertification(self):
        with patch('resolver.service.public_url', side_effect=lambda u: u):
            r = self.service.start({'operation': 'resolve', 'url': 'https://example.org', 'title': 'Example', 'kind': 'movie'})
        job = self.wait(r['job_id']); self.assertEqual(job['status'], 'resolved_unverified')
        self.assertIs(job['result']['native_playback_verified'], False)
        args = {'job_id': r['job_id'], 'action': 'recipe', 'proposal_digest': job['result']['proposal_digest']}
        self.service.dispatch('/v1/apply', args, True)
        self.assertTrue(self.service.recipes_path.exists())
    def test_oversized_patch_is_refused_before_review(self):
        class Large:
            def decide(self, *a, **kw):
                return {'edits': [{'old': "SELECTOR = '.old'", 'new': 'SELECTOR = ' + repr('x' * 8000)}]}
        with self.assertRaises(ValueError): self.source.propose(self.rel, 'test', Large())
        self.assertEqual(self.path.read_text(), "SELECTOR = '.old'\n")
    def test_busy_and_cancel(self):
        class Waiting:
            def resolve(self, request, cancel, progress, recipe):
                cancel.wait(2); return {'status': 'cancelled'}
        self.service.browser = Waiting()
        with patch('resolver.service.public_url', side_effect=lambda u: u):
            args = {'operation': 'resolve', 'url': 'https://example.org', 'title': 'Example', 'kind': 'movie'}
            first = self.service.start(args)
            with self.assertRaises(ValueError): self.service.start(args)
        self.service.dispatch('/v1/cancel', {'job_id': first['job_id']}, False)
        self.assertEqual(self.wait(first['job_id'])['status'], 'cancelled')
    def test_service_auth_origin_size_approval_and_host(self):
        server = ServiceServer(('127.0.0.1', 0), self.service, 'secret-token')
        threading.Thread(target=server.serve_forever, daemon=True).start()
        url = 'http://127.0.0.1:' + str(server.server_port)
        def call(path='/v1/job', headers=None, body=None):
            req = Request(url + path, data=json.dumps(body or {'arguments': {}}).encode(), headers={'Content-Type': 'application/json', **(headers or {})})
            try:
                with urlopen(req) as response: return response.status, json.load(response)
            except HTTPError as e: return e.code, json.load(e)
        try:
            self.assertEqual(call()[0], 403)
            auth = {'Authorization': 'Bearer secret-token'}
            self.assertEqual(call(headers=auth)[0], 200)
            self.assertEqual(call(headers={**auth, 'Origin': url})[0], 403)
            self.assertEqual(call(headers={**auth, 'Host': 'evil.example'})[0], 403)
            self.assertEqual(call('/v1/start', auth)[0], 400)
            self.assertEqual(call(headers=auth, body={'arguments': {'x': 'a' * 20000}})[0], 400)
        finally: server.shutdown(); server.server_close()
    def test_network_and_model_only_local(self):
        for url in ['file:///tmp/a', 'http://127.0.0.1', 'http://192.168.1.2', 'http://169.254.169.254']:
            with self.assertRaises(ValueError): public_url(url)
        for url in ['https://remote.example', 'http://localhost:11434', 'http://127.0.0.1:11434/path']:
            with self.assertRaises(ValueError): LocalModel(url=url)
        self.assertEqual(safe_url('https://example.org/a?token=secret#fragment'), 'https://example.org/a')
