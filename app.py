import json, os, time, urllib.error, urllib.request
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
ROOT = Path(__file__).resolve().parent
STATIC = ROOT / 'static'
ENV = ROOT / '.env'
API_URL = 'https://api.football-data.org/v4/competitions/BSA/standings?season=2026'
CACHE_SECONDS = 24 * 60 * 60
cache = {'at': 0, 'data': None}

def load_env():
    if not ENV.exists(): return
    for raw in ENV.read_text(encoding='utf-8').splitlines():
        line = raw.strip()
        if not line or line.startswith('#') or '=' not in line: continue
        key, value = line.split('=', 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))

def json_reply(handler, status, payload):
    body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    handler.send_response(status); handler.send_header('Content-Type', 'application/json; charset=utf-8')
    handler.send_header('Content-Length', str(len(body))); handler.send_header('Cache-Control', 'no-store')
    handler.end_headers(); handler.wfile.write(body)

def get_standings():
    token = os.environ.get('FOOTBALL_DATA_TOKEN', '').strip()
    if not token: raise RuntimeError('Chave não configurada. Preencha FOOTBALL_DATA_TOKEN no arquivo .env.')
    req = urllib.request.Request(API_URL, headers={'X-Auth-Token': token, 'User-Agent': 'BrasileiraoDashboard/1.0'})
    try:
        with urllib.request.urlopen(req, timeout=20) as response: data = json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as exc:
        if exc.code in (401, 403): raise RuntimeError(f'A API recusou a chave ou o plano não permite esta consulta (HTTP {exc.code}). Confira chave e permissões.') from None
        if exc.code == 429: raise RuntimeError('Limite de consultas atingido. Tente novamente mais tarde.') from None
        raise RuntimeError(f'A API respondeu com erro HTTP {exc.code}.') from None
    except urllib.error.URLError: raise RuntimeError('Não foi possível conectar à API. Confira sua internet.') from None
    except json.JSONDecodeError: raise RuntimeError('A API respondeu em formato inesperado.') from None
    standings = data.get('standings') or []
    total = next((s for s in standings if s.get('type') == 'TOTAL'), None)
    if not total or not total.get('table'): raise RuntimeError('A API não retornou a classificação geral do Brasileirão 2026.')
    return {'competition': data.get('competition', {}).get('name', 'Campeonato Brasileiro Série A'), 'season': str(data.get('season', {}).get('startDate', '2026'))[:4], 'currentMatchday': data.get('season', {}).get('currentMatchday'), 'table': total['table']}

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs): super().__init__(*args, directory=str(STATIC), **kwargs)
    def do_GET(self):
        path = urlparse(self.path).path
        if path == '/api/standings':
            now = time.time()
            if cache['data'] is not None and now - cache['at'] < CACHE_SECONDS:
                return json_reply(self, 200, {'source':'cache', 'updatedAt':time.strftime('%Y-%m-%dT%H:%M:%S%z', time.localtime(cache['at'])), 'data':cache['data']})
            try:
                data = get_standings(); cache.update(at=now, data=data)
                return json_reply(self, 200, {'source':'api', 'updatedAt':time.strftime('%Y-%m-%dT%H:%M:%S%z', time.localtime(now)), 'data':data})
            except RuntimeError as exc: return json_reply(self, 502, {'error':str(exc)})
        if path == '/': self.path = '/index.html'
        return super().do_GET()
    def log_message(self, fmt, *args): print('%s - %s' % (self.address_string(), fmt % args))

if __name__ == '__main__':
    load_env()
    server = ThreadingHTTPServer(('127.0.0.1', 8000), Handler)
    print('Painel iniciado: http://127.0.0.1:8000')
    print('Para encerrar, pressione Ctrl+C neste terminal.')
    server.serve_forever()
