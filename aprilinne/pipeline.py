"""One run = one folder runs/<ten>/: transcript -> outline -> write -> edit -> grade -> (repair -> grade) x rounds.
All state lives in runs/<ten>/state.json; every step's prompt and answer in buoc/; each round's script and scorecard
in vong<N>/. Re-running continues where it stopped."""
import json
import math
import re
import urllib.request
from pathlib import Path

from . import grade as G
from . import prompts as P
from .script import Script, numbered, split_acts, words

ROOT = Path(__file__).resolve().parent.parent
RUNS = ROOT / 'runs'
TRANSCRIPT_ENGINE = 'http://127.0.0.1:8000/transcript'
ROUNDS = 3
TRIES = 3


def fetch_transcript(url, language='vi'):
    """Same call as AI MANAGER's story_pipeline.fetch_transcript, to the local Transcript Engine (read only)."""
    body = json.dumps({'url': url, 'languages': [language, 'en']}).encode()
    req = urllib.request.Request(TRANSCRIPT_ENGINE, body, {'content-type': 'application/json'}, method='POST')
    with urllib.request.urlopen(req, timeout=180) as r:
        d = json.loads(r.read())
    text = str(d.get('text') or '').strip() or ' '.join(str(s.get('text') or '').strip() for s in d.get('segments') or [] if str(s.get('text') or '').strip())
    if not text:
        raise RuntimeError('Transcript Engine trả transcript trống')
    return text


class OutlineError(ValueError):
    pass


def check_outline(plan):
    """Machine check of the outline against T1–T3 before any writing."""
    errs = []
    hoi = plan.get('hoi') or []
    if not 4 <= len(hoi) <= 10:
        errs.append('Cần 4–10 hồi, có %d' % len(hoi))
    for k in ('tuyen_A', 'tuyen_B', 'doi_luc', 'hua_hen_mo_dau', 'he_lo_lon', 'hoi_tu'):
        if not str(plan.get(k) or '').strip():
            errs.append('Thiếu ' + k)
    for h in hoi:
        if not str(h.get('buoc_A') or '').strip() or not str(h.get('buoc_B') or '').strip():
            errs.append('Hồi %s thiếu bước tuyến A hoặc B' % h.get('so'))
    nt = sum(1 for h in hoi if str(h.get('ngoai_truyen') or '').strip())
    if hoi and nt < math.ceil(len(hoi) / 2):
        errs.append('Ngoại truyện chỉ có ở %d/%d hồi' % (nt, len(hoi)))
    dt = plan.get('dau_tu') or {}
    if not str(dt.get('con_so') or '').strip():
        errs.append('Thiếu con số công sức')
    if len([b for b in dt.get('bo_su') or [] if str(b).strip()]) < 2:
        errs.append('Cần ≥ 2 bộ sử')
    if not str(dt.get('phat_hien') or '').strip():
        errs.append('Thiếu phát hiện (tuyến B)')
    for h in hoi:
        if re.search(r'giai thoại|phần thưởng|ngoại truyện', str(h.get('ten') or ''), re.I) and not str(h.get('buoc_A') or '').strip():
            errs.append('Hồi %s là hồi riêng cho giai thoại' % h.get('so'))
    return errs


def outline_md(plan):
    out = ['# Dàn ý — %s' % plan.get('tieu_de', ''), '',
           '- **Tuyến A:** ' + str(plan.get('tuyen_A', '')), '- **Tuyến B:** ' + str(plan.get('tuyen_B', '')),
           '- **Đối lực:** ' + str(plan.get('doi_luc', '')), '- **Hứa hẹn mở đầu:** ' + str(plan.get('hua_hen_mo_dau', ''))]
    dt = plan.get('dau_tu') or {}
    out += ['- **Tâm sự công sức:** %s; %s; phát hiện: %s' % (dt.get('con_so', ''), ', '.join(dt.get('bo_su') or []), dt.get('phat_hien', '')), '']
    for h in plan.get('hoi') or []:
        out += ['## Hồi %s — %s' % (h.get('so'), h.get('ten', '')), '',
                '- Tuyến A: ' + str(h.get('buoc_A', '')), '- Tuyến B: ' + str(h.get('buoc_B', '')),
                '- Ngoại truyện: ' + str(h.get('ngoai_truyen', '') or '—'), '- Mốc tiến độ: ' + str(h.get('moc_tien_do', '')),
                '- Nhịp chuyển: ' + str(h.get('nhip_chuyen', '')), '']
    out += ['**Hé lộ lớn:** ' + str(plan.get('he_lo_lon', '')), '', '**Hội tụ:** ' + str(plan.get('hoi_tu', ''))]
    return '\n'.join(out)


def clean_script(text):
    """Drop a ``` fence or a preamble line the writer may add around the script."""
    t = str(text).strip()
    m = re.search(r'```(?:markdown|md|text)?\s*\n(.*?)\n```', t, re.S)
    if m and len(m.group(1)) > 0.5 * len(t):
        t = m.group(1)
    i = t.find('## ')
    if 0 < i < 400:
        t = t[i:]
    return t.strip() + '\n'


class Run:
    def __init__(self, name, backend):
        self.dir = RUNS / name
        self.name = name
        self.ai = backend
        self.state_path = self.dir / 'state.json'
        self.s = json.loads(self.state_path.read_text(encoding='utf-8'))

    @staticmethod
    def create(name, url=None, transcript=None, script=None, kenh='', so_chu=0):
        d = RUNS / name
        if (d / 'state.json').exists():
            raise FileExistsError('Đã có lần chạy ' + name)
        d.mkdir(parents=True, exist_ok=True)
        s = {'ten': name, 'buoc': 'lay_transcript', 'url': url, 'kenh': kenh, 'so_chu_muc_tieu': so_chu, 'vong': 0, 'thu': {}}
        if transcript is not None:
            (d / 'nguon.txt').write_text(transcript, encoding='utf-8')
            s['buoc'] = 'dan_y'
        if script is not None:   # grade an existing script only (checking the grader)
            (d / 'vong1').mkdir(exist_ok=True)
            (d / 'vong1' / 'kich_ban.md').write_text(script, encoding='utf-8')
            s.update(buoc='cham', vong=1, chi_cham=True)
        (d / 'state.json').write_text(json.dumps(s, ensure_ascii=False, indent=1), encoding='utf-8')
        return d

    def save(self):
        self.state_path.write_text(json.dumps(self.s, ensure_ascii=False, indent=1), encoding='utf-8')

    def read(self, rel):
        return (self.dir / rel).read_text(encoding='utf-8')

    def write(self, rel, text):
        p = self.dir / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding='utf-8')

    def step_id(self, base):
        n = self.s['thu'].get(base, 0)
        return base + ('_lai%d' % n if n else '')

    def retry(self, base, err):
        n = self.s['thu'].get(base, 0) + 1
        self.s['thu'][base] = n
        self.s['loi_cuoi'] = '%s: %s' % (base, err)
        self.save()
        if n >= TRIES:
            raise RuntimeError('Bước %s không cho kết quả dùng được sau %d lần: %s' % (base, TRIES, err))

    @property
    def cfg(self):
        return {'kenh': self.s.get('kenh', ''), 'so_chu_muc_tieu': self.s.get('so_chu_muc_tieu', 0)}

    def go(self):
        """Advance until done; raises llm.Pending when a step waits for an answer file."""
        while self.s['buoc'] != 'xong':
            getattr(self, 'do_' + self.s['buoc'])()
            self.save()
        return self.s

    # --- steps --------------------------------------------------------------------------------------
    def do_lay_transcript(self):
        t = fetch_transcript(self.s['url'])
        self.write('nguon.txt', t)
        self.s['buoc'] = 'dan_y'

    def do_dan_y(self):
        if not self.s.get('so_chu_muc_tieu'):
            self.s['so_chu_muc_tieu'] = len(words(self.read('nguon.txt')))
        base = 'dan_y'
        out = self.ai.ask(self.step_id(base), P.outline(self.cfg, self.read('nguon.txt')))
        try:
            plan = G.parse_json(out)
            errs = check_outline(plan)
            if errs:
                raise OutlineError('; '.join(errs))
        except (G.GradeError, OutlineError) as e:
            self.retry(base, e)
            return
        self.write('dan_y.json', json.dumps(plan, ensure_ascii=False, indent=1))
        self.write('dan_y.md', outline_md(plan))
        self.s['buoc'] = 'viet'

    def plan(self):
        return json.loads(self.read('dan_y.json'))

    def do_viet(self):
        out = self.ai.ask('viet', P.write(self.cfg, self.read('nguon.txt'), self.plan()))
        self.write('vong1/ban_nhap.md', clean_script(out))
        self.s.update(buoc='bien_tap', vong=1)

    def do_bien_tap(self):
        v = self.s['vong']
        out = self.ai.ask('bien_tap_%d' % v, P.edit(self.cfg, self.read('vong%d/ban_nhap.md' % v)))
        self.write('vong%d/kich_ban.md' % v, clean_script(out))
        self.s['buoc'] = 'cham'

    def do_cham(self):
        v = self.s['vong']
        script = self.read('vong%d/kich_ban.md' % v)
        text = numbered(split_acts(script))
        self.write('vong%d/kich_ban_danh_so.md' % v, text)
        base = 'cham_%d' % v
        out = self.ai.ask(self.step_id(base), P.grade(text))
        try:
            card = G.evaluate(text, out)
        except G.GradeError as e:
            self.retry(base, e)
            return
        self.write('vong%d/cham.json' % v, json.dumps(card, ensure_ascii=False, indent=1))
        self.write('vong%d/bang_diem.md' % v, G.render(card, '%s, vòng %d' % (self.name, v)))
        hist = self.s.setdefault('lich_su', [])
        hist.append({'vong': v, 'duyet': card['duyet'], 'diem': {k: card['tieu_chi'][k]['diem'] for k in G.ALL}})
        best = self.s.get('tot_nhat')
        if best is None or G.rank(card) > tuple(self.s['hang_tot_nhat']):
            self.s['tot_nhat'], self.s['hang_tot_nhat'] = v, list(G.rank(card))
        if card['duyet'] or self.s.get('chi_cham') or v >= ROUNDS:
            self.finish()
        else:
            self.s['buoc'] = 'sua'

    def do_sua(self):
        v = self.s['vong']
        b = self.s['tot_nhat']   # repair from the best version so far
        out = self.ai.ask('sua_%d' % (v + 1), P.repair(self.cfg, self.read('nguon.txt'), self.plan(),
                                                      self.read('vong%d/kich_ban.md' % b), self.read('vong%d/bang_diem.md' % b)))
        self.write('vong%d/kich_ban.md' % (v + 1), clean_script(out))
        self.s.update(vong=v + 1, buoc='cham')

    def finish(self):
        b = self.s['tot_nhat']
        card = json.loads(self.read('vong%d/cham.json' % b))
        lines = ['# Kết quả — %s' % self.name, '',
                 '**%s** — bản tốt nhất: vòng %d' % ('DUYỆT' if card['duyet'] else 'CHƯA ĐẠT', b), '',
                 '| Vòng | Duyệt | ' + ' | '.join(G.ALL) + ' |', '|---|---|' + '---|' * len(G.ALL)]
        for h in self.s.get('lich_su', []):
            lines.append('| %d | %s | %s |' % (h['vong'], 'có' if h['duyet'] else 'không', ' | '.join('%g' % h['diem'][k] for k in G.ALL)))
        lines += ['', 'Kịch bản: `vong%d/kich_ban.md` — Bảng điểm: `vong%d/bang_diem.md`' % (b, b)]
        self.write('KET_QUA.md', '\n'.join(lines) + '\n')
        self.s['buoc'] = 'xong'
