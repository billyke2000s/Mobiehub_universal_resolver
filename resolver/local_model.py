"""Only the owner's local Ollama; structured proposals, never executable commands."""
import json
import re
import urllib.request
from urllib.parse import urlsplit


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        raise ValueError('The local model cannot redirect requests.')


class LocalModel:
    def __init__(self, model='qwen3.5:9b', url='http://127.0.0.1:11434'):
        p = urlsplit(url)
        if p.scheme != 'http' or p.hostname != '127.0.0.1' or not p.port or p.path not in ('', '/') or p.username or p.query or p.fragment:
            raise ValueError('Ollama must use a literal local 127.0.0.1 HTTP endpoint.')
        if not re.fullmatch(r'[a-zA-Z0-9_.:/-]{1,100}', model):
            raise ValueError('Invalid model name.')
        self.url, self.model = url.rstrip('/'), model

    def decide(self, instruction, observation, image=None, max_tokens=700, timeout=60):
        msg = {'role': 'user', 'content': json.dumps(observation, ensure_ascii=False)}
        if image:
            msg['images'] = [image]
        payload = {'model': self.model, 'stream': False, 'think': False, 'format': 'json',
                   'messages': [{'role': 'system', 'content': instruction}, msg],
                   'options': {'num_ctx': 12288, 'num_predict': max_tokens, 'temperature': 0}}
        request = urllib.request.Request(self.url + '/api/chat', data=json.dumps(payload).encode(),
                                         headers={'Content-Type': 'application/json'})
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
        try:
            with opener.open(request, timeout=max(1, min(60, timeout))) as response:
                raw = response.read(1000001)
            if len(raw) > 1000000:
                raise ValueError('Model response too large.')
            result = json.loads(json.loads(raw)['message']['content'])
            if not isinstance(result, dict):
                raise ValueError('Expected a JSON object.')
            return result
        except Exception as exc:
            raise RuntimeError('Local Ollama did not return a valid decision. Check its model and connection.') from exc
