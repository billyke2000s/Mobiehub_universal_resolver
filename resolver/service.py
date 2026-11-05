"""Authenticated loopback service and bounded asynchronous local jobs."""
import argparse
import copy
import hashlib
import json
import os
import secrets
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
from .browser import BrowserResolver, public_url, safe_url
from .local_model import LocalModel
from .source_repair import SourceRepair, digest


def private_write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(value, indent=2), encoding='utf-8')
    if os.name != 'nt':
        temp.chmod(0o600)
    temp.replace(path)


def public_result(value):
    if isinstance(value, dict):
        return {k: public_result(v) for k, v in value.items() if not k.startswith('_')}
    if isinstance(value, list):
        return [public_result(v) for v in value]
    return value


class ResolverService:
    def __init__(self, folder, model, browser, source):
        self.folder, self.model, self.browser, self.source = Path(folder), model, browser, source
        self.folder.mkdir(parents=True, exist_ok=True)
        self.jobs, self.lock = {}, threading.RLock()
        self.worker = threading.BoundedSemaphore(1)
        self.recipes_path = self.folder / 'recipes.json'
        self.recipes = json.loads(self.recipes_path.read_text()) if self.recipes_path.exists() else {}
        self.restore_proposals()

    def restore_proposals(self):
        for path in sorted(self.folder.glob('proposal-*.json'))[-20:]:
            try:
                entry = json.loads(path.read_text())
                self.jobs[entry['id']] = {**entry, 'cancel': threading.Event()}
            except (ValueError, KeyError):
                pass

    def dispatch(self, path, args, approved):
        if not isinstance(args, dict):
            raise ValueError('Arguments must be an object.')
        if path in ('/v1/start', '/v1/apply') and approved is not True:
            raise ValueError('This action needs explicit local approval.')
        if path == '/v1/start':
            return self.start(args)
        if path == '/v1/job':
            with self.lock:
                if args.get('action') == 'inventory':
                    inv = self.source.inventory()
                    # Keep responses within the extension host limit; full file list can be read locally too.
                    return inv
                if args.get('job_id'):
                    job = self.job(args['job_id'])
                    return public_result({k: v for k, v in job.items() if k not in ('cancel', 'request')})
                return {'jobs': [{'id': j['id'], 'status': j['status'], 'progress': j.get('progress')} for j in list(self.jobs.values())[-20:]]}
        if path == '/v1/cancel':
            with self.lock:
                self.job(args.get('job_id'))['cancel'].set()
            return {'status': 'cancellation_requested'}
        if path == '/v1/apply':
            return self.apply(args)
        raise ValueError('Unknown service endpoint.')

    def job(self, key):
        if not isinstance(key, str) or key not in self.jobs:
            raise ValueError('Unknown job ID.')
        return self.jobs[key]

    def start(self, args):
        if args.get('operation') not in ('resolve', 'repair') or args.get('kind') not in ('movie', 'series'):
            raise ValueError('Choose resolve/repair and movie/series.')
        args = copy.deepcopy(args)
        if args.get('operation') == 'resolve' or args.get('url'):
            public_url(args.get('url', ''))
            if not isinstance(args.get('title'), str) or not 1 <= len(args['title']) <= 200:
                raise ValueError('Supply the title; for series include season and episode in the title.')
        if args['operation'] == 'repair':
            self.source.source(args.get('source_file'))
            if not isinstance(args.get('diagnosis'), str) or not 1 <= len(args['diagnosis']) <= 2000:
                raise ValueError('Describe the observed source failure.')
        with self.lock:
            if not self.worker.acquire(blocking=False):
                raise ValueError('A local job is already running. Cancel it or wait for it to finish.')
            if len(self.jobs) >= 40:
                key = next((k for k, j in self.jobs.items() if j['status'] != 'running'), None)
                if key:
                    del self.jobs[key]
            key = secrets.token_hex(8)
            job = {'id': key, 'status': 'running', 'created': time.time(), 'request': args,
                   'cancel': threading.Event(), 'progress': {'stage': 'starting'}}
            self.jobs[key] = job
            threading.Thread(target=self.run, args=(job,), daemon=True).start()
        return {'job_id': key, 'status': 'running', 'note': 'Poll job for progress; this response does not claim a fix.'}

    def run(self, job):
        try:
            args = job['request']
            result = None
            def progress(value):
                with self.lock:
                    job['progress'] = value
            if args.get('url'):
                recipe_key = urlsplit(args['url']).hostname + ':' + args['kind']
                result = self.browser.resolve(args, job['cancel'], progress, self.recipes.get(recipe_key))
            if job['cancel'].is_set():
                result = {'status': 'cancelled'}
            elif args['operation'] == 'repair':
                # Two proposals maximum; only retry malformed edits. No repeated whole-site audit.
                for attempt in range(2):
                    progress({'stage': 'source_proposal', 'attempt': attempt + 1})
                    try:
                        result = self.source.propose(args['source_file'], args['diagnosis'], self.model,
                                                     public_result(result) if result else None)
                        break
                    except (ValueError, SyntaxError):
                        if attempt == 1:
                            raise ValueError('The local model could not produce a valid scoped patch in two attempts.')
                if job['cancel'].is_set():
                    result = {'status': 'cancelled'}
            if result and result.get('recipe'):
                result['proposal_digest'] = digest(json.dumps(result['recipe'], sort_keys=True))
            with self.lock:
                job['result'], job['status'] = result, result['status']
                # Media tokens stay in memory. Only source proposals and their backups survive restart.
                if result.get('status') == 'patch_proposed':
                    self.checkpoint(job)
        except Exception as exc:
            with self.lock:
                job['status'] = 'failed'
                job['result'] = {'error': str(exc)[:400] if isinstance(exc, (ValueError, RuntimeError)) else
                                 'The browser or model could not finish. Check installation and the selected website.'}
        finally:
            self.worker.release()

    def checkpoint(self, job):
        private_write(self.folder / ('proposal-' + job['id'] + '.json'),
                      {k: v for k, v in job.items() if k not in ('cancel', 'request')})

    def apply(self, args):
        with self.lock:
            job = self.job(args.get('job_id'))
            result = job.get('result', {})
            expected = args.get('proposal_digest')
            if expected != result.get('proposal_digest') or not isinstance(expected, str):
                raise ValueError('Review the job result and supply its exact proposal_digest.')
            action = args.get('action')
            if action == 'recipe' and result.get('recipe'):
                recipe = result['recipe']
                key = urlsplit(recipe['site']).hostname + ':' + recipe['kind']
                if self.recipes_path.exists():
                    private_write(self.folder / 'recipes.previous.json', self.recipes)
                self.recipes[key] = recipe
                private_write(self.recipes_path, self.recipes)
                return {'status': 'recipe_saved', 'note': 'Used on future browser jobs; no Android source was changed.'}
            if action == 'source' and job['status'] == 'patch_proposed':
                applied = self.source.apply(result, expected)
                job['status'] = applied['status']
                self.checkpoint(job)
                return applied
            if action == 'rollback' and job['status'] == 'patch_applied_unverified':
                rolled = self.source.rollback(result)
                job['status'] = 'rolled_back'
                self.checkpoint(job)
                return rolled
            raise ValueError('This job has no change available for that action.')


class ServiceServer(ThreadingHTTPServer):
    daemon_threads = True
    def __init__(self, address, service, token):
        if address[0] != '127.0.0.1':
            raise ValueError('Bind only to 127.0.0.1.')
        self.service, self.token = service, token
        super().__init__(address, ServiceHandler)


class ServiceHandler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def respond(self, value, status=200):
        raw = json.dumps(value).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(raw)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(raw)

    def do_POST(self):
        expected_host = '127.0.0.1:' + str(self.server.server_port)
        if self.headers.get('Host') != expected_host or self.headers.get('Origin') or not secrets.compare_digest(
                self.headers.get('Authorization', ''), 'Bearer ' + self.server.token):
            return self.respond({'error': 'Unauthorized.'}, 403)
        if self.headers.get_content_type() != 'application/json':
            return self.respond({'error': 'JSON required.'}, 415)
        try:
            size = int(self.headers.get('Content-Length', '0'))
            if not 0 < size <= 16000:
                raise ValueError('Request too large or empty.')
            body = json.loads(self.rfile.read(size))
            value = self.server.service.dispatch(self.path, body.get('arguments'), body.get('approved'))
            self.respond(value)
        except (ValueError, TypeError, AttributeError) as exc:
            self.respond({'error': str(exc)[:400] if isinstance(exc, ValueError) else 'Invalid request.'}, 400)
        except Exception:
            self.respond({'error': 'The local resolver could not finish.'}, 503)


def main():
    parser = argparse.ArgumentParser(description='Local AI MovieHub extension service')
    parser.add_argument('--moviehub', help='Path to your actual billyke2000s/moviehub checkout')
    parser.add_argument('--model', default='qwen3.5:9b')
    parser.add_argument('--ollama', default='http://127.0.0.1:11434')
    parser.add_argument('--port', default=47831, type=int)
    parser.add_argument('--data', default=str(Path(os.environ.get('LOCALAPPDATA', Path.home())) / 'MovieHubResolver'))
    parser.add_argument('--headless', action='store_true')
    parser.add_argument('--vision', action='store_true', help='Send browser screenshots only to the local model')
    parser.add_argument('--browser', help='Optional installed Chromium executable')
    options = parser.parse_args()
    folder = Path(options.data)
    model = LocalModel(options.model, options.ollama)
    service = ResolverService(folder, model, BrowserResolver(model, options.headless, options.browser, options.vision), SourceRepair(options.moviehub))
    token_path = folder / 'service-token.json'
    token = json.loads(token_path.read_text())['token'] if token_path.exists() else secrets.token_urlsafe(32)
    private_write(token_path, {'token': token})
    server = ServiceServer(('127.0.0.1', options.port), service, token)
    manifest = json.loads((Path(__file__).resolve().parent.parent / 'extensions/cortana/manifest.json').read_text())
    manifest['connection'] = {'url': 'http://127.0.0.1:' + str(server.server_port), 'token': token}
    package = folder / 'moviehub-extension.json'
    private_write(package, manifest)
    print('Resolver ready. In Cortana: Systems > Extensions > Import extension, then enable it.', flush=True)
    print('Import file: ' + str(package), flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        with service.lock:
            for job in service.jobs.values():
                job['cancel'].set()
        server.server_close()


if __name__ == '__main__':
    main()
