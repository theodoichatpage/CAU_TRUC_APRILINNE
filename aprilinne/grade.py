"""Turn the grader's reply into a checked scorecard: every quote looked up in the script, the measurable caps of
STANDARDS.md applied by the machine, and the verdict. The grader's own scores are never trusted above these caps."""
import json
import math
import re

from .script import Script, norm

CORE = ['T1', 'T2', 'T3']
SUPPORT = ['H1', 'H2', 'H3', 'H4', 'H5', 'H6']
ALL = CORE + SUPPORT
NAMES = {
    'T1': 'Tương phản — hai tuyến đối lực đan xen',
    'T2': 'Phần thưởng — ngoại truyện trong tuyến song song',
    'T3': 'Mức đầu tư — tâm sự công sức dẫn vào tuyến ngoại truyện',
    'H1': 'Mở đầu 20 giây',
    'H2': 'Vào chuyện sớm, liền mạch',
    'H3': 'Nhịp độ',
    'H4': 'Hé lộ lớn và kết ở cao trào',
    'H5': 'Giọng kênh',
    'H6': 'Kêu gọi tương tác',
}
PASS_CORE, PASS_SUPPORT = 8, 7
OPENING_WORDS = 350          # ≈ 2 phút
LATE_B_SHARE = 0.15
MIN_B_SHARE = 0.15
MAX_RUN = 900                # ≈ 5,5 phút liền một tuyến
EDITOR_NOTES = re.compile(r'cần kiểm tra|cần đối chiếu|tư liệu được cung cấp|tư liệu đầu vào|theo tư liệu bạn|tư liệu đang kể|'
                          r'bản tư liệu|transcript|video gốc|ghi chú biên tập', re.I)
GREETING = re.compile(r'chào mừng', re.I)
# a call to like / follow / comment (checked on normalized text)
CTA = re.compile(r'(?:^| )(?:like|subscribe|đăng ký kênh|lượt đăng ký|lượt theo dõi|theo dõi kênh|bấm theo dõi|nhấn theo dõi|'
                 r'để lại bình luận|phần bình luận|bình luận bên dưới|bình luận cho em)(?: |$)')
# an effort figure: a number followed by a unit of time or reading ("1000 giờ", "ba tháng", "hàng trăm trang")
NUMBER = re.compile(r'(?:^| )(?:\d+|một|hai|ba|bốn|năm|sáu|bảy|tám|chín|mười|mươi|trăm|nghìn|ngàn|vạn|triệu|chục)'
                    r' (?:giờ|tiếng|ngày|đêm|tuần|tháng|năm|trang|cuốn|quyển|tập)(?: |$)')


class GradeError(ValueError):
    """The grader's reply cannot be used (bad JSON, segments not found in the script): ask the grader again."""


def parse_json(text):
    t = str(text or '')
    m = re.search(r'```(?:json)?\s*(\{.*\})\s*```', t, re.S)
    if m:
        t = m.group(1)
    else:
        a, b = t.find('{'), t.rfind('}')
        if a < 0 or b <= a:
            raise GradeError('Không thấy JSON trong câu trả lời')
        t = t[a:b + 1]
    try:
        return json.loads(t)
    except json.JSONDecodeError as e:
        raise GradeError('JSON hỏng: %s' % e)


def _num(v):
    try:
        x = float(v)
    except (TypeError, ValueError):
        return None
    return max(0.0, min(10.0, x))


def evaluate(script_text, reply):
    """reply: grader JSON (dict or text). Returns the scorecard dict (see STANDARDS.md, 'Phần máy kiểm tra')."""
    g = reply if isinstance(reply, dict) else parse_json(reply)
    s = Script(script_text)
    n_acts = len(s.acts)
    unverified = []
    caps = {k: [] for k in ALL}   # (max, reason)
    blocking = []

    def cap(k, mx, why):
        caps[k].append((mx, why))

    # --- line segments, located in order -------------------------------------------------------------
    segs, pos = [], 0
    raw = g.get('doan') or []
    for d in raw:
        q = d.get('mo_dau') or ''
        line = str(d.get('tuyen') or '').strip().upper()
        line = line if line in ('A', 'B') else 'C'
        at = s.find(q, pos)
        if at is None:
            at = s.find(q)   # out of order still counts, but does not move the cursor back
            if at is None or at < pos:
                unverified.append(('đoạn tuyến', q))
                continue
        segs.append({'tuyen': line, 'start': at, 'mo_dau': q})
        pos = at + 1
    if raw and len(segs) < max(2, len(raw) / 2):
        raise GradeError('Chỉ dò được %d/%d câu mở đầu đoạn tuyến trong kịch bản' % (len(segs), len(raw)))
    segs.sort(key=lambda x: x['start'])
    if segs and segs[0]['start'] > 0:
        segs.insert(0, {'tuyen': 'C', 'start': 0, 'mo_dau': '(đầu kịch bản)'})
    for i, x in enumerate(segs):
        x['end'] = segs[i + 1]['start'] if i + 1 < len(segs) else s.n
        x['len'] = x['end'] - x['start']

    def words_in(line, a, b):
        return sum(max(0, min(x['end'], b) - max(x['start'], a)) for x in segs if x['tuyen'] == line)

    acts = []
    for i in range(1, n_acts + 1):
        a, b = s.act_words(i)
        acts.append({'hoi': i, 'ten': s.acts[i - 1][0], 'chu': b - a,
                     'A': words_in('A', a, b), 'B': words_in('B', a, b), 'ngoai_truyen': 0})
    b_total = sum(x['len'] for x in segs if x['tuyen'] == 'B')
    b_share = b_total / s.n if s.n else 0
    first_b = next((x['start'] for x in segs if x['tuyen'] == 'B'), None)
    runs, cur = [], None
    for x in segs:
        if cur and x['tuyen'] == cur['tuyen']:
            cur['len'] += x['len']
        else:
            cur = {'tuyen': x['tuyen'], 'start': x['start'], 'len': x['len']}
            runs.append(cur)
    longest = max([r for r in runs if r['tuyen'] in 'AB'], key=lambda r: r['len'], default=None)
    switches = sum(1 for r1, r2 in zip([r for r in runs if r['tuyen'] in 'AB'], [r for r in runs if r['tuyen'] in 'AB'][1:])
                   if r1['tuyen'] != r2['tuyen'])

    def in_b(tok):
        return any(x['tuyen'] == 'B' and x['start'] <= tok < x['end'] for x in segs)

    # --- T1 ---------------------------------------------------------------------------------------------
    no_b = [x['hoi'] for x in acts if x['B'] == 0]
    if not str(g.get('tuyen_B') or '').strip() or b_total == 0:
        cap('T1', 3, 'Không có tuyến B có diễn biến riêng')
        cap('T2', 3, 'Không có tuyến B để chứa ngoại truyện')
    if no_b:
        cap('T1', 4, 'Hồi không có tuyến B: %s' % ', '.join(map(str, no_b)))
        cap('T2', 5, 'Hồi không có tuyến B: %s' % ', '.join(map(str, no_b)))
    if b_total and b_share < MIN_B_SHARE:
        cap('T1', 4, 'Tuyến B chỉ chiếm %.0f%% lời đọc (cần ≥ 15%%)' % (b_share * 100))
    if first_b is not None and first_b > LATE_B_SHARE * s.n:
        cap('T1', 6, 'Đoạn B đầu tiên bắt đầu ở chữ %d (%.0f%% kịch bản, cần trong 15%% đầu)' % (first_b, 100 * first_b / s.n))
    if longest and longest['len'] > MAX_RUN:
        cap('T1', 6, 'Có đoạn kể liền tuyến %s dài %d chữ (≈ %.1f phút, tối đa 900 chữ)' % (longest['tuyen'], longest['len'], longest['len'] / 160))

    # --- T2 ---------------------------------------------------------------------------------------------
    nt_acts = set()
    for it in g.get('ngoai_truyen') or []:
        at = s.find(it.get('trich'))
        if at is None:
            unverified.append(('ngoại truyện', it.get('trich')))
        elif in_b(at):
            nt_acts.add(s.act_of(at))
    for x in acts:
        x['ngoai_truyen'] = 1 if x['hoi'] in nt_acts else 0
    if len(nt_acts) < math.ceil(n_acts / 2):
        cap('T2', 5, 'Ngoại truyện nằm trong tuyến B chỉ trích được ở %d/%d hồi (cần ≥ một nửa)' % (len(nt_acts), n_acts))
    separate = []
    for it in g.get('phan_rieng_giai_thoai') or []:
        if s.find(it.get('trich')) is not None:
            separate.append(it.get('trich'))
        else:
            unverified.append(('phần riêng giai thoại', it.get('trich')))
    if separate:
        cap('T2', 3, 'Giai thoại gom thành phần/danh sách riêng: "%s"' % separate[0][:120])

    # --- T3 ---------------------------------------------------------------------------------------------
    dt = g.get('dau_tu') or {}
    q = str(dt.get('trich') or '').strip()
    at = s.find(q) if q else None
    if at is None:
        if q:
            unverified.append(('tâm sự công sức', q))
        cap('T3', 2, 'Không trích được lời tâm sự công sức')
    else:
        if at > OPENING_WORDS:
            cap('T3', 6, 'Lời tâm sự bắt đầu ở chữ %d (cần trong 350 chữ đầu)' % at)
        if not NUMBER.search(norm(q)):
            cap('T3', 5, 'Lời tâm sự không có con số công sức')
        books = [b for b in (dt.get('bo_su') or []) if str(b).strip() and norm(b) in norm(q)]
        if len(books) < 2:
            cap('T3', 5, 'Lời tâm sự gọi tên %d bộ sử (cần ≥ 2)' % len(books))
        if dt.get('trung_tuyen_B') is not True:
            cap('T3', 4, 'Phát hiện trong lời tâm sự không trùng tuyến B')

    # --- whole script -------------------------------------------------------------------------------------
    body = s.joined
    notes = sorted(set(m.group(0) for m in EDITOR_NOTES.finditer(script_text)))
    if notes:
        blocking.append('Ghi chú biên tập lọt vào lời đọc: %s' % ', '.join(notes))
        cap('H2', 4, 'Ghi chú biên tập lọt vào lời đọc')
    greet = len(GREETING.findall(body))
    if greet > 1:
        cap('H2', 4, 'Lời chào kênh xuất hiện %d lần' % greet)
    cta_acts = sorted({s.act_of(s._tok_at(m.start() + (m.group(0)[0] == ' '))) for m in CTA.finditer(body)})
    if not cta_acts:
        cap('H6', 3, 'Không có lời kêu gọi like / theo dõi / bình luận')
    elif len(cta_acts) < 2:
        cap('H6', 5, 'Lời kêu gọi chỉ ở hồi %d' % cta_acts[0])

    # --- criteria from the grader, evidence checked -------------------------------------------------
    crit = g.get('tieu_chi') or {}
    rows = {}
    for k in ALL:
        c = crit.get(k) or {}
        score = _num(c.get('diem'))
        if score is None:
            raise GradeError('Thiếu điểm tiêu chí ' + k)
        ev_ok = []
        for e in c.get('bang_chung') or []:
            quote = e.get('trich') if isinstance(e, dict) else e
            at = s.find(quote)
            if at is None:
                unverified.append((k, quote))
            else:
                ev_ok.append({'hoi': s.act_of(at), 'trich': quote})
        if not ev_ok and score > 3:
            cap(k, 3, 'Không còn bằng chứng trích đúng nguyên văn')
        mx = min([m for m, _ in caps[k]], default=10)
        final = min(score, mx)
        need = PASS_CORE if k in CORE else PASS_SUPPORT
        rows[k] = {'ma': k, 'ten': NAMES[k], 'diem_cham': score, 'gioi_han': mx if caps[k] else None,
                   'vi_sao_gioi_han': [w for m, w in sorted(caps[k])], 'diem': final, 'dat': final >= need,
                   'can': need, 'bang_chung': ev_ok, 'ly_do': c.get('ly_do', ''), 'cach_sua': c.get('cach_sua', '')}

    approved = all(rows[k]['dat'] for k in ALL) and not blocking
    return {
        'duyet': approved,
        'loi_chan': blocking,
        'tieu_chi': rows,
        'tuyen': {'A': g.get('tuyen_A', ''), 'B': g.get('tuyen_B', ''), 'doi_luc': g.get('doi_luc', '')},
        'do_dac': {'so_chu': s.n, 'so_hoi': n_acts, 'ty_le_B': round(b_share, 3),
                   'B_bat_dau_o_chu': first_b, 'doan_lien_dai_nhat': longest and {'tuyen': longest['tuyen'], 'chu': longest['len']},
                   'so_lan_chuyen_tuyen': switches, 'hoi_co_ngoai_truyen': sorted(nt_acts), 'so_loi_chao': greet, 'hoi_co_keu_goi': cta_acts},
        'hoi': acts,
        'doan': [{k: x[k] for k in ('tuyen', 'start', 'len', 'mo_dau')} for x in segs],
        'dau_tu': dt,
        'khong_tim_thay': [{'muc': a, 'trich': b} for a, b in unverified],
        'su_that': g.get('su_that') or [],
        'diem_tong': round(sum(rows[k]['diem'] for k in ALL), 1),
    }


def rank(card):
    """Best version first: approved, then core criteria passed, then the core sum, then the total."""
    t = card['tieu_chi']
    return (card['duyet'], sum(t[k]['dat'] for k in CORE), sum(t[k]['dat'] for k in ALL),
            sum(t[k]['diem'] for k in CORE), card['diem_tong'])


def render(card, title=''):
    t = card['tieu_chi']
    out = ['# Bảng điểm%s' % (' — ' + title if title else ''), '',
           '**Kết luận: %s**' % ('DUYỆT' if card['duyet'] else 'CHƯA ĐẠT'), '']
    fail = [k for k in ALL if not t[k]['dat']]
    if fail:
        out.append('Trượt: ' + ', '.join('%s (%s)' % (k, ('%g' % t[k]['diem'])) for k in fail))
    for b in card['loi_chan']:
        out.append('Lỗi chặn: ' + b)
    out += ['', '| Mã | Tiêu chí | Người chấm | Máy giới hạn | Điểm cuối | Cần | Đạt |', '|---|---|---|---|---|---|---|']
    for k in ALL:
        r = t[k]
        out.append('| %s | %s | %g | %s | **%g** | %d | %s |' % (k, r['ten'], r['diem_cham'], '%g' % r['gioi_han'] if r['gioi_han'] is not None else '—',
                                                         r['diem'], r['can'], 'đạt' if r['dat'] else 'TRƯỢT'))
    tu = card['tuyen']
    m = card['do_dac']
    out += ['', '## Hai tuyến (người chấm nhận ra)', '', '- Tuyến A: ' + (tu['A'] or '—'), '- Tuyến B: ' + (tu['B'] or '—'),
            '- Đối lực: ' + (tu['doi_luc'] or '—'), '',
            '## Máy đo', '',
            '- Số chữ: %d (≈ %.0f phút đọc), %d hồi' % (m['so_chu'], m['so_chu'] / 160, m['so_hoi']),
            '- Tuyến B chiếm: %.0f%%' % (m['ty_le_B'] * 100),
            '- Đoạn B đầu tiên ở chữ: %s' % (m['B_bat_dau_o_chu'] if m['B_bat_dau_o_chu'] is not None else 'không có'),
            '- Đoạn kể liền một tuyến dài nhất: %s' % ('%s, %d chữ' % (m['doan_lien_dai_nhat']['tuyen'], m['doan_lien_dai_nhat']['chu']) if m['doan_lien_dai_nhat'] else '—'),
            '- Số lần chuyển tuyến A↔B: %d' % m['so_lan_chuyen_tuyen'],
            '- Lời chào kênh: %d lần' % m['so_loi_chao'],
            '- Lời kêu gọi tương tác ở hồi: %s' % (', '.join(map(str, m['hoi_co_keu_goi'])) or 'không có'), '',
            '| Hồi | Tên | Chữ | Chữ tuyến A | Chữ tuyến B | Ngoại truyện trong B |', '|---|---|---|---|---|---|']
    for h in card['hoi']:
        out.append('| %d | %s | %d | %d | %d | %s |' % (h['hoi'], h['ten'] or '', h['chu'], h['A'], h['B'], 'có' if h['ngoai_truyen'] else '—'))
    out += ['', '## Chi tiết từng tiêu chí', '']
    for k in ALL:
        r = t[k]
        out += ['### %s. %s — %g/10 %s' % (k, r['ten'], r['diem'], '(đạt)' if r['dat'] else '(TRƯỢT)'), '']
        for w in r['vi_sao_gioi_han']:
            out.append('- Máy giới hạn: ' + w)
        for e in r['bang_chung']:
            out.append('- Hồi %d: "%s"' % (e['hoi'], e['trich']))
        if r['ly_do']:
            out.append('- Lý do: ' + r['ly_do'])
        if r['cach_sua']:
            out.append('- Cách sửa: ' + r['cach_sua'])
        out.append('')
    if card['khong_tim_thay']:
        out += ['## Câu trích không có trong kịch bản (đã loại)', '']
        out += ['- [%s] "%s"' % (x['muc'], str(x['trich'])[:200]) for x in card['khong_tim_thay']]
        out.append('')
    if card['su_that']:
        out += ['## Ghi chú sự thật (không chặn duyệt)', '']
        out += ['- "%s" — %s' % (x.get('trich', ''), x.get('ghi_chu', '')) for x in card['su_that']]
        out.append('')
    return '\n'.join(out)
