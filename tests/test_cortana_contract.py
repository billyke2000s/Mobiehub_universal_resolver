"""Both repos' actual transport and local Ollama client, with a scripted model response."""
import importlib.util
import json
import os
import subprocess
import tempfile
import threading
import time
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from resolver.local_model import LocalModel
from resolver.source_repair import SourceRepair
from resolver.service import ResolverService, ServiceServer

CORTANA = Path(os.environ.get('CORTANA_CHECKOUT', str(Path(__file__).resolve().parents[2] / 'Cortana-ai')))

class Ollama(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_POST(self):
        payload = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        assert self.path == '/api/chat' and payload['format'] == 'json' and payload['stream'] is False
        result = {'reason': 'Observed selector changed.', 'edits': [{'old': "SELECTOR = '.old'", 'new': "SELECTOR = '.new'"}]}
        raw = json.dumps({'message': {'content': json.dumps(result)}}).encode()
        self.send_response(200); self.send_header('Content-Length', str(len(raw))); self.end_headers(); self.wfile.write(raw)

@unittest.skipUnless((CORTANA / 'app/extensions.py').exists(), 'Set CORTANA_CHECKOUT to the matching extension-host checkout.')
class CrossRepoContract(unittest.TestCase):
    def test_manifest_local_model_proposal_approval_apply_and_rollback(self):
        spec = importlib.util.spec_from_file_location('cortana_extension_contract', CORTANA / 'app/extensions.py')
        host = importlib.util.module_from_spec(spec); spec.loader.exec_module(host)
        class Store:
            def __init__(self): self.data = {}
            def get(self, key, default=None): return self.data.get(key, default)
            def set(self, key, value): self.data[key] = value
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); repo = root / 'moviehub'
            subprocess.run(['git', 'init', str(repo)], capture_output=True, check=True)
            subprocess.run(['git', '-C', str(repo), 'remote', 'add', 'origin', 'https://github.com/billyke2000s/moviehub.git'], check=True)
            relative = 'android-tv-launcher/app/src/main/python/moviehub_scrubs/providers/example.py'
            path = repo / relative; path.parent.mkdir(parents=True); path.write_text("SELECTOR = '.old'\n")
            model_server = ThreadingHTTPServer(('127.0.0.1', 0), Ollama)
            threading.Thread(target=model_server.serve_forever, daemon=True).start()
            model = LocalModel(url='http://127.0.0.1:' + str(model_server.server_port))
            service = ResolverService(root / 'data', model, None, SourceRepair(repo))
            server = ServiceServer(('127.0.0.1', 0), service, 'T' * 40)
            threading.Thread(target=server.serve_forever, daemon=True).start()
            try:
                manifest = json.loads((Path(__file__).resolve().parents[1] / 'extensions/cortana/manifest.json').read_text())
                manifest['connection'] = {'url': 'http://127.0.0.1:' + str(server.server_port), 'token': 'T' * 40}
                manager = host.ExtensionManager(Store()); manager.manage({'action': 'install', 'manifest': manifest})
                manager.manage({'action': 'enable', 'id': manifest['id']})
                names = {t['name']: host.tool_name(manifest, t) for t in manifest['tools']}
                args = {'operation': 'repair', 'kind': 'movie', 'source_file': relative, 'diagnosis': 'Observed selector changed.'}
                with self.assertRaises(ValueError): manager.call(names['start'], args, local=True)
                started = manager.call(names['start'], args, local=True, approved=True)
                self.assertIn('job_id', started)
                for _ in range(100):
                    result = manager.call(names['job'], {'job_id': started['job_id']}, local=True)
                    if result['status'] != 'running': break
                    time.sleep(.01)
                self.assertEqual(result['status'], 'patch_proposed')
                self.assertEqual(path.read_text(), "SELECTOR = '.old'\n")
                apply = {'job_id': started['job_id'], 'action': 'source', 'proposal_digest': result['result']['proposal_digest']}
                self.assertEqual(manager.call(names['apply'], apply, local=True, approved=True)['status'], 'patch_applied_unverified')
                self.assertEqual(path.read_text(), "SELECTOR = '.new'\n")
                apply['action'] = 'rollback'
                self.assertEqual(manager.call(names['apply'], apply, local=True, approved=True)['status'], 'rolled_back')
                self.assertNotIn('T' * 40, json.dumps(manager.listing()))
            finally:
                server.shutdown();server.server_close();model_server.shutdown();model_server.server_close()
