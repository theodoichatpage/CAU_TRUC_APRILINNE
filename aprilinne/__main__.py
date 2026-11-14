"""python -m aprilinne <lệnh> — xem README.md."""
import argparse
import json
import sys
from pathlib import Path

from . import llm
from .pipeline import Run, RUNS


def main(argv=None):
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding='utf-8')
        except Exception:
            pass
    ap = argparse.ArgumentParser(prog='aprilinne')
    sub = ap.add_subparsers(dest='lenh', required=True)
    m = sub.add_parser('moi', help='tạo lần chạy mới từ link YouTube hoặc file transcript')
    m.add_argument('ten')
    g = m.add_mutually_exclusive_group(required=True)
    g.add_argument('--url')
    g.add_argument('--transcript', help='file transcript có sẵn')
    m.add_argument('--kenh', default='', help='tên kênh nói trong lời chào')
    m.add_argument('--phut', type=float, default=0, help='độ dài mong muốn (phút); mặc định bằng video gốc')
    c = sub.add_parser('cham', help='chỉ chấm một kịch bản có sẵn (kiểm định người chấm)')
    c.add_argument('ten')
    c.add_argument('kich_ban')
    for p in (m, c):
        p.add_argument('--may', choices=['file', 'cli'], default='file', help='ai trả lời: file (mặc định) hoặc cli (claude -p)')
        p.add_argument('--model')
    r = sub.add_parser('chay', help='chạy tiếp một lần chạy')
    r.add_argument('ten')
    r.add_argument('--may', choices=['file', 'cli'], default='file')
    r.add_argument('--model')
    t = sub.add_parser('xem', help='xem trạng thái')
    t.add_argument('ten', nargs='?')
    a = ap.parse_args(argv)

    if a.lenh == 'xem':
        names = [a.ten] if a.ten else sorted(p.parent.name for p in RUNS.glob('*/state.json'))
        for n in names:
            s = json.loads((RUNS / n / 'state.json').read_text(encoding='utf-8'))
            print('%-30s bước=%-14s vòng=%s tốt nhất=%s' % (n, s['buoc'], s.get('vong'), s.get('tot_nhat')))
        return 0
    if a.lenh == 'moi':
        tr = Path(a.transcript).read_text(encoding='utf-8') if a.transcript else None
        Run.create(a.ten, url=a.url, transcript=tr, kenh=a.kenh, so_chu=int(a.phut * 160))
    elif a.lenh == 'cham':
        Run.create(a.ten, script=Path(a.kich_ban).read_text(encoding='utf-8'))
    run = Run(a.ten, llm.make(a.may, RUNS / a.ten, a.model))
    try:
        s = run.go()
    except llm.Pending as p:
        print('CHỜ TRẢ LỜI bước "%s"' % p.step)
        print('  đề bài : %s' % p.prompt_path)
        print('  ghi vào: %s' % p.out_path)
        print('rồi chạy lại: python -m aprilinne chay %s' % a.ten)
        return 3
    print('XONG: %s' % (RUNS / a.ten / 'KET_QUA.md'))
    print((RUNS / a.ten / 'KET_QUA.md').read_text(encoding='utf-8'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
