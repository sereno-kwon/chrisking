"""chrisking.com 페이지를 돌며 이미지 후보를 모읍니다 (일회성, 결과는 scrape 브랜치에 저장)."""
import re, json, os, sys, hashlib, urllib.request, urllib.parse
from html.parser import HTMLParser

UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36'
START = ['https://chrisking.com/', 'https://www.chrisking.com/']
OUT = sys.argv[1]
os.makedirs(OUT + '/img', exist_ok=True)


def get(url, binary=False):
    r = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': '*/*'}), timeout=30)
    data = r.read()
    if binary:
        return data, r.geturl(), r.headers.get('Content-Type', '')
    return data.decode('utf-8', 'replace'), r.geturl()


class P(HTMLParser):
    def __init__(s, base):
        super().__init__()
        s.base, s.links, s.imgs, s.title, s._t = base, set(), [], '', False

    def add(s, u, alt=''):
        if u and not u.startswith('data:'):
            s.imgs.append((urllib.parse.urljoin(s.base, u.strip()), alt))

    def handle_starttag(s, tag, a):
        a = dict(a)
        if tag == 'title':
            s._t = True
        if tag == 'a' and a.get('href'):
            s.links.add(urllib.parse.urljoin(s.base, a['href']).split('#')[0])
        if tag == 'meta' and a.get('property') in ('og:image', 'og:image:secure_url'):
            s.add(a.get('content'), 'og:image')
        if tag in ('img', 'source'):
            alt = a.get('alt', '') or ''
            for k in ('srcset', 'data-srcset'):
                if a.get(k):
                    cands = [c.strip().split(' ') for c in a[k].split(',') if c.strip()]
                    best = max(cands, key=lambda c: int(re.sub(r'\D', '', c[1]) or 0) if len(c) > 1 else 0)
                    s.add(best[0], alt)
            for k in ('src', 'data-src', 'data-original'):
                if a.get(k):
                    s.add(a[k], alt)
        for u in re.findall(r'url\(["\']?([^"\')]+)', a.get('style', '') or ''):
            s.add(u, 'bg')

    def handle_data(s, d):
        if s._t:
            s.title += d

    def handle_endtag(s, tag):
        if tag == 'title':
            s._t = False


log, queue = [], []
for u in START:
    try:
        html, final = get(u)
        queue.append((final, html))
        break
    except Exception as e:
        log.append(f'start fail {u} {e}')
host = urllib.parse.urlparse(queue[0][0]).netloc if queue else 'chrisking.com'
SKIP = re.compile(r'/(cart|account|login|search|checkout|policies|cdn-cgi)|\.(pdf|zip)$|mailto:|tel:', re.I)

seen, found, done = set(), {}, 0
while queue and done < 60:
    url, html = queue.pop(0)
    if url in seen:
        continue
    seen.add(url)
    done += 1
    p = P(url)
    try:
        p.feed(html)
    except Exception as e:
        log.append(f'parse {url} {e}')
    for m in re.findall(r'https?:\\?/\\?/[^"\'\s<>]+?\.(?:jpe?g|png|webp)(?:\?[^"\'\s<>]*)?', html, re.I):
        p.add(m.replace('\\/', '/'), 'inline')
    log.append(f'page {url} title={p.title.strip()[:80]!r} imgs={len(p.imgs)}')
    for iu, alt in p.imgs:
        found.setdefault(iu, {'alt': alt, 'pages': []})['pages'].append(url)
    for l in sorted(p.links):
        pu = urllib.parse.urlparse(l)
        if pu.netloc != host or SKIP.search(l) or l in seen or any(l == q[0] for q in queue):
            continue
        if done + len(queue) >= 120:
            break
        try:
            h, f = get(l)
            queue.append((f, h))
        except Exception as e:
            log.append(f'fail {l} {e}')


def norm(u):
    u = u.replace('&amp;', '&')
    if 'cdn.shopify.com' in u or '/cdn/shop/' in u:
        u = re.sub(r'_(\d+x\d*|\d*x\d+)(?=\.(jpe?g|png|webp))', '', u)
        u = re.sub(r'([?&])width=\d+&?', r'\1', u).rstrip('?&')
        u += ('&' if '?' in u else '?') + 'width=2400'
    return u


index, got = [], set()
for u, meta in found.items():
    if re.search(r'\.gif(\?|$)', u, re.I):
        continue
    nu = norm(u)
    if nu in got:
        continue
    got.add(nu)
    try:
        data, final, ct = get(nu, binary=True)
    except Exception:
        try:
            data, final, ct = get(u, binary=True)
            nu = u
        except Exception as e2:
            log.append(f'imgfail {u} {e2}')
            continue
    is_logo = 'logo' in u.lower() or u.lower().split('?')[0].endswith('.svg')
    if len(data) < 12000 and not is_logo:
        continue
    ext = {'image/png': 'png', 'image/webp': 'webp', 'image/svg+xml': 'svg'}.get(ct.split(';')[0].strip(), 'jpg')
    name = f'{len(index):03d}_{hashlib.md5(nu.encode()).hexdigest()[:6]}.{ext}'
    open(f'{OUT}/img/{name}', 'wb').write(data)
    index.append({'file': name, 'url': nu, 'bytes': len(data), 'alt': meta['alt'], 'pages': meta['pages'][:5]})
    if len(index) >= 400:
        break

json.dump(index, open(f'{OUT}/index.json', 'w'), indent=1, ensure_ascii=False)
open(f'{OUT}/log.txt', 'w').write('\n'.join(log))
print(len(seen), 'pages,', len(found), 'image refs,', len(index), 'saved')
