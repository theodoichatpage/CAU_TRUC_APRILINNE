import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from aprilinne import grade as G
from aprilinne import llm, pipeline
from aprilinne.script import Script, norm, numbered, split_acts

EFFORT = ('Các bác ạ, em đã dành 1000 giờ tra cứu Đại Việt sử ký toàn thư, Việt sử thông giám cương mục và An Nam chí lược, '
          'và nhận ra một câu chuyện mà sách giáo khoa chắc chắn không ai kể cho các bác.')


def good_script(acts=4, filler=20):
    pad = ' '.join(['chuyện kể tiếp diễn'] * filler)
    out = []
    for i in range(1, acts + 1):
        a = 'Tuyến chính hồi %d Trần Thủ Độ tiến thêm một bước. %s' % (i, pad)
        b = 'Phía triều đình hồi %d lại phản đòn ông. Giai thoại hồi %d kể rằng người lính dám ngăn kiệu. %s' % (i, i, pad)
        body = EFFORT + '\n\n' + b + '\n\n' + a if i == 1 else a + '\n\n' + b   # act 1: line B right after the effort talk
        out.append('## Hồi %d — Phần %d\n\n%s' % (i, i, body))
    return '\n\n'.join(out)


def good_reply(acts=4):
    doan = []
    for i in range(1, acts + 1):
        if i == 1:
            doan.append({'hoi': 1, 'tuyen': 'chung', 'mo_dau': 'Các bác ạ, em đã dành 1000 giờ tra cứu'})
        pair = [{'hoi': i, 'tuyen': 'A', 'mo_dau': 'Tuyến chính hồi %d Trần Thủ Độ tiến thêm' % i},
                {'hoi': i, 'tuyen': 'B', 'mo_dau': 'Phía triều đình hồi %d lại phản đòn ông' % i}]
        doan += pair[::-1] if i == 1 else pair
    ev = [{'hoi': 1, 'trich': 'Tuyến chính hồi 1 Trần Thủ Độ tiến thêm một bước'}]
    return {
        'tuyen_A': 'Trần Thủ Độ đưa họ Trần lên ngôi', 'tuyen_B': 'Triều đình phản đòn', 'doi_luc': 'B kéo ngược A',
        'doan': doan,
        'ngoai_truyen': [{'hoi': i, 'trich': 'Giai thoại hồi %d kể rằng người lính dám ngăn kiệu' % i} for i in range(1, acts + 1)],
        'phan_rieng_giai_thoai': [],
        'dau_tu': {'trich': EFFORT, 'con_so': '1000 giờ', 'bo_su': ['Đại Việt sử ký toàn thư', 'An Nam chí lược'],
                   'phat_hien': 'triều đình phản đòn', 'trung_tuyen_B': True, 'nhac_lai': ''},
        'tieu_chi': {k: {'diem': 9, 'bang_chung': ev, 'ly_do': 'ok', 'cach_sua': ''} for k in G.ALL},
        'su_that': [],
    }


class ScriptTest(unittest.TestCase):
    def test_norm_ignores_punctuation_and_case(self):
        self.assertEqual(norm('Ông  là, "NGƯỜI"\nquyết đoán!'), 'ông là người quyết đoán')

    def test_split_by_headings_and_numbered(self):
        acts = split_acts('## Mở\n\nmột hai ba\n\n## Hồi 2 — Giữa\n\nbốn năm sáu')
        self.assertEqual([t for t, _ in acts], ['Mở', 'Hồi 2 — Giữa'])
        self.assertIn('## Hồi 2 — Giữa', numbered(acts))
        self.assertNotIn('Hồi 2 — Hồi 2', numbered(acts))

    def test_split_without_headings_into_equal_acts(self):
        text = '\n\n'.join('đoạn số %d có vài chữ ở đây' % i for i in range(30))
        acts = split_acts(text, 6)
        self.assertEqual(len(acts), 6)

    def test_find_quote_positions_and_acts(self):
        s = Script('## A\n\nmột hai ba bốn\n\n[HÌNH: ảnh lớn]\n\n## B\n\nnăm sáu bảy tám')
        self.assertEqual(s.n, 8)   # image cue not counted
        self.assertEqual(s.find('năm, sáu bảy'), 4)
        self.assertEqual(s.act_of(4), 2)
        self.assertIsNone(s.find('hai ba'))   # too short to count as evidence
        self.assertIsNone(s.find('ai ba bốn'))   # not on a word boundary


class GradeTest(unittest.TestCase):
    def test_good_script_passes(self):
        card = G.evaluate(good_script(), good_reply())
        self.assertTrue(card['duyet'], G.render(card))
        self.assertEqual(card['khong_tim_thay'], [])
        self.assertEqual(card['do_dac']['hoi_co_ngoai_truyen'], [1, 2, 3, 4])

    def test_act_without_line_b_caps_t1_t2(self):
        r = good_reply()
        r['doan'] = [d for d in r['doan'] if not (d['tuyen'] == 'B' and d['hoi'] == 3)]
        card = G.evaluate(good_script(), r)
        self.assertEqual(card['tieu_chi']['T1']['diem'], 4)
        self.assertLessEqual(card['tieu_chi']['T2']['diem'], 5)
        self.assertFalse(card['duyet'])

    def test_no_line_b_at_all(self):
        r = good_reply()
        r['tuyen_B'] = ''
        for d in r['doan']:
            d['tuyen'] = 'A'
        card = G.evaluate(good_script(), r)
        self.assertEqual(card['tieu_chi']['T1']['diem'], 3)

    def test_anecdote_list_caps_t2(self):
        r = good_reply()
        r['phan_rieng_giai_thoai'] = [{'hoi': 1, 'trich': 'Giai thoại hồi 1 kể rằng người lính dám ngăn kiệu'}]
        self.assertEqual(G.evaluate(good_script(), r)['tieu_chi']['T2']['diem'], 3)

    def test_effort_missing_or_weak(self):
        r = good_reply()
        r['dau_tu'] = {'trich': '', 'trung_tuyen_B': False}
        self.assertEqual(G.evaluate(good_script(), r)['tieu_chi']['T3']['diem'], 2)
        r = good_reply()
        r['dau_tu']['trung_tuyen_B'] = False
        self.assertEqual(G.evaluate(good_script(), r)['tieu_chi']['T3']['diem'], 4)
        r = good_reply()
        r['dau_tu']['bo_su'] = ['Đại Việt sử ký toàn thư', 'Sách không có trong câu']
        self.assertEqual(G.evaluate(good_script(), r)['tieu_chi']['T3']['diem'], 5)

    def test_effort_without_figure(self):
        s = good_script().replace('1000 giờ', 'nhiều công')
        r = good_reply()
        r['dau_tu']['trich'] = EFFORT.replace('1000 giờ', 'nhiều công')
        r['doan'][0]['mo_dau'] = 'Các bác ạ, em đã dành nhiều công tra cứu'
        self.assertEqual(G.evaluate(s, r)['tieu_chi']['T3']['diem'], 5)

    def test_invented_quote_is_dropped(self):
        r = good_reply()
        r['tieu_chi']['H5']['bang_chung'] = [{'hoi': 1, 'trich': 'câu này không hề có trong kịch bản'}]
        card = G.evaluate(good_script(), r)
        self.assertEqual(card['tieu_chi']['H5']['diem'], 3)
        self.assertEqual(card['khong_tim_thay'][0]['muc'], 'H5')

    def test_long_single_line_run_and_late_b(self):
        s = good_script(filler=400)
        card = G.evaluate(s, good_reply())
        self.assertEqual(card['tieu_chi']['T1']['diem'], 6)

    def test_editor_note_blocks_and_double_greeting(self):
        s = good_script().replace('Phần 2\n\n', 'Phần 2\n\nChào mừng các bác. [CẦN KIỂM TRA] Chào mừng lần nữa nhé.\n\n')
        card = G.evaluate(s, good_reply())
        self.assertTrue(card['loi_chan'])
        self.assertEqual(card['tieu_chi']['H2']['diem'], 4)
        self.assertFalse(card['duyet'])

    def test_source_mentions_read_aloud_block(self):
        for note in ('Bản transcript còn kể rằng', 'Theo tư liệu đang kể, ông', 'cần đối chiếu lại cách ghi'):
            s = good_script().replace('Phần 2\n\n', 'Phần 2\n\n%s.\n\n' % note)
            self.assertTrue(G.evaluate(s, good_reply())['loi_chan'], note)

    def test_segments_not_found_is_grader_error(self):
        r = good_reply()
        for d in r['doan']:
            d['mo_dau'] = 'không có câu này trong kịch bản đâu'
        with self.assertRaises(G.GradeError):
            G.evaluate(good_script(), r)

    def test_parse_json_fenced(self):
        self.assertEqual(G.parse_json('Đây:\n```json\n{"a": 1}\n```'), {'a': 1})
        with self.assertRaises(G.GradeError):
            G.parse_json('không có json')


def good_plan():
    return {'tieu_de': 'T', 'tuyen_A': 'a', 'tuyen_B': 'b', 'doi_luc': 'd', 'hua_hen_mo_dau': 'h', 'he_lo_lon': 'x', 'hoi_tu': 'y',
            'dau_tu': {'con_so': '1000 giờ', 'bo_su': ['A', 'B'], 'phat_hien': 'p'},
            'hoi': [{'so': i, 'ten': 'h%d' % i, 'buoc_A': 'a', 'buoc_B': 'b', 'ngoai_truyen': 'n', 'moc_tien_do': 'm', 'nhip_chuyen': 'A-B'}
                    for i in range(1, 5)]}


class OutlineTest(unittest.TestCase):
    def test_outline_checks(self):
        self.assertEqual(pipeline.check_outline(good_plan()), [])
        p = good_plan()
        p['hoi'][2]['buoc_B'] = ''
        p['dau_tu']['bo_su'] = ['A']
        errs = pipeline.check_outline(p)
        self.assertTrue(any('Hồi 3' in e for e in errs))
        self.assertTrue(any('bộ sử' in e for e in errs))


class FakeAI(llm.Backend):
    """Answers like a writer and a grader would; the grader is asked twice in round 1 (first answer unusable)."""

    def __init__(self, run_dir):
        super().__init__(run_dir)
        self.asked = []

    def answer(self, step, p, o, prompt):
        self.asked.append(step)
        if step == 'dan_y':
            text = '```json\n%s\n```' % json.dumps(good_plan(), ensure_ascii=False)
        elif step == 'cham_1':
            text = 'không phải json'
        elif step.startswith('cham'):
            assert 'DÀN Ý' not in prompt and 'tuyen_A": "a"' not in prompt   # grader never sees the outline
            text = json.dumps(good_reply(), ensure_ascii=False)
        else:
            text = good_script()
        o.write_text(text, encoding='utf-8')
        return text


class PipelineTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.p = mock.patch.object(pipeline, 'RUNS', self.tmp)
        self.p.start()

    def tearDown(self):
        self.p.stop()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_full_run_with_fake_ai(self):
        pipeline.Run.create('thu', transcript='transcript gốc ' * 50)
        run = pipeline.Run('thu', FakeAI(self.tmp / 'thu'))
        s = run.go()
        self.assertEqual(s['buoc'], 'xong')
        self.assertEqual(run.ai.asked, ['dan_y', 'viet', 'bien_tap_1', 'cham_1', 'cham_1_lai1'])
        for f in ('dan_y.md', 'vong1/kich_ban.md', 'vong1/bang_diem.md', 'KET_QUA.md'):
            self.assertTrue((self.tmp / 'thu' / f).exists(), f)
        self.assertIn('DUYỆT', (self.tmp / 'thu' / 'KET_QUA.md').read_text(encoding='utf-8'))

    def test_file_backend_waits_then_resumes(self):
        pipeline.Run.create('cham', script=good_script())
        with self.assertRaises(llm.Pending) as w:
            pipeline.Run('cham', llm.FileBackend(self.tmp / 'cham')).go()
        self.assertTrue(w.exception.prompt_path.exists())
        prompt = w.exception.prompt_path.read_text(encoding='utf-8')
        self.assertIn('## Hồi 4', prompt)
        self.assertIn('T1. Tương phản', prompt)   # the standards travel with the grader
        w.exception.out_path.write_text(json.dumps(good_reply(), ensure_ascii=False), encoding='utf-8')
        s = pipeline.Run('cham', llm.FileBackend(self.tmp / 'cham')).go()
        self.assertEqual(s['buoc'], 'xong')

    def test_failed_round_goes_to_repair_from_best(self):
        pipeline.Run.create('sua', script=good_script())
        st = json.loads((self.tmp / 'sua' / 'state.json').read_text(encoding='utf-8'))
        st.pop('chi_cham')
        (self.tmp / 'sua' / 'state.json').write_text(json.dumps(st), encoding='utf-8')
        (self.tmp / 'sua' / 'nguon.txt').write_text('gốc', encoding='utf-8')
        (self.tmp / 'sua' / 'dan_y.json').write_text(json.dumps(good_plan()), encoding='utf-8')
        bad = good_reply()
        bad['dau_tu']['trich'] = ''
        ai = FakeAI(self.tmp / 'sua')
        (ai.dir / 'cham_1.out.md').write_text(json.dumps(bad, ensure_ascii=False), encoding='utf-8')
        s = pipeline.Run('sua', ai).go()
        self.assertEqual(ai.asked, ['sua_2', 'cham_2'])
        self.assertEqual(s['tot_nhat'], 2)


if __name__ == '__main__':
    unittest.main()
