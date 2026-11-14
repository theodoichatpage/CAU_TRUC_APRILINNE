"""Who answers a step. Every step is a prompt file and an answer file in runs/<ten>/buoc/, whoever answers it:

- 'file' (default): the tool writes buoc/<buoc>.prompt.md and stops; someone (a Claude Code session, or a fresh
  sub-agent for the grader) writes buoc/<buoc>.out.md, then the run is resumed.
- 'cli': Claude Code headless (`claude -p`), one fresh process per step, so writer and grader never share context.
  Needs Claude Code logged in on this machine (run `claude` once and /login)."""
import glob
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path


class Pending(Exception):
    def __init__(self, step, prompt_path, out_path):
        super().__init__(step)
        self.step, self.prompt_path, self.out_path = step, prompt_path, out_path


def find_claude():
    exe = os.environ.get('APRILINNE_CLAUDE') or shutil.which('claude')
    if exe:
        return exe
    base = Path(os.environ.get('LOCALAPPDATA', '')) / 'Claude-Data'
    found = sorted(glob.glob(str(base / '*' / 'claude-code' / '*' / '*' / 'claude.exe')),
                   key=lambda p: [int(x) if x.isdigit() else 0 for x in Path(p).parent.parent.name.split('.')])
    return found[-1] if found else None


class Backend:
    def __init__(self, run_dir):
        self.dir = Path(run_dir) / 'buoc'
        self.dir.mkdir(parents=True, exist_ok=True)

    def paths(self, step):
        return self.dir / (step + '.prompt.md'), self.dir / (step + '.out.md')

    def ask(self, step, prompt):
        p, o = self.paths(step)
        if o.exists() and o.read_text(encoding='utf-8').strip():
            return o.read_text(encoding='utf-8')
        p.write_text(prompt, encoding='utf-8')
        return self.answer(step, p, o, prompt)

    def answer(self, step, p, o, prompt):
        raise Pending(step, p, o)


class FileBackend(Backend):
    pass


class CliBackend(Backend):
    def __init__(self, run_dir, exe=None, model=None, timeout=3600):
        super().__init__(run_dir)
        self.exe = exe or find_claude()
        self.model, self.timeout = model, timeout
        if not self.exe:
            raise RuntimeError('Không tìm thấy Claude Code (claude). Dùng --may file, hoặc đặt APRILINNE_CLAUDE.')

    def answer(self, step, p, o, prompt):
        cmd = [self.exe, '-p', '--output-format', 'json']
        if self.model:
            cmd += ['--model', self.model]
        with tempfile.TemporaryDirectory() as cwd:   # empty folder: the call sees nothing but the prompt
            r = subprocess.run(cmd, input=prompt, capture_output=True, text=True, encoding='utf-8', cwd=cwd, timeout=self.timeout)
        try:
            d = json.loads(r.stdout)
        except json.JSONDecodeError:
            raise RuntimeError('Claude Code trả lời không đọc được: ' + (r.stdout or r.stderr)[:300])
        if d.get('is_error'):
            raise RuntimeError('Claude Code báo lỗi: ' + str(d.get('result'))[:300])
        text = str(d.get('result') or '')
        o.write_text(text, encoding='utf-8')
        return text


def make(kind, run_dir, model=None):
    return CliBackend(run_dir, model=model) if kind == 'cli' else FileBackend(run_dir)
