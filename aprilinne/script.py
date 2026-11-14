"""Reading a script: acts (hồi), spoken words, and finding quoted evidence in it."""
import re
import unicodedata

HEADING = re.compile(r'^\s*#{1,6}\s*(.*?)\s*$')
IMAGE = re.compile(r'\[\s*HÌNH\s*:[^\]]*\]', re.I)
WORD = re.compile(r'\w+', re.U)


def norm(text):
    """Lowercase, NFC, letters/digits only, single spaces: quotes match despite punctuation or line breaks."""
    t = unicodedata.normalize('NFC', str(text or '')).casefold()
    return ' '.join(WORD.findall(t))


def words(text):
    return norm(text).split()


def split_acts(text, default_acts=6):
    """[(title, body)] — split on '## ' headings; a script without headings is cut into equal-length acts at paragraph breaks."""
    acts, title, buf = [], None, []
    for line in str(text).splitlines():
        m = HEADING.match(line)
        if m and line.lstrip().startswith('#'):
            if title is not None or ''.join(buf).strip():
                acts.append((title or '', '\n'.join(buf).strip()))
            title, buf = m.group(1), []
        else:
            buf.append(line)
    if title is not None or ''.join(buf).strip():
        acts.append((title or '', '\n'.join(buf).strip()))
    acts = [(t, b) for t, b in acts if b.strip()]
    if len(acts) > 1:
        return acts
    body = acts[0][1] if acts else ''
    paras = [p for p in re.split(r'\n\s*\n', body) if p.strip()]
    total = sum(len(words(p)) for p in paras) or 1
    out, cur, n = [], [], 0
    for p in paras:
        cur.append(p)
        n += len(words(p))
        if n >= total * (len(out) + 1) / default_acts and len(out) < default_acts - 1:
            out.append(('', '\n\n'.join(cur)))
            cur = []
    if cur:
        out.append(('', '\n\n'.join(cur)))
    return out


def spoken(text):
    """What is read aloud: no image cues."""
    return IMAGE.sub(' ', str(text))


def numbered(acts):
    """The script as the grader sees it: every act headed 'Hồi N'."""
    out = []
    for i, (t, b) in enumerate(acts):
        t = re.sub(r'(?i)^hồi\s*\d+\s*[—–:.\-]*\s*', '', t or '').strip()
        out.append('## Hồi %d%s\n\n%s' % (i + 1, ' — ' + t if t else '', b.strip()))
    return '\n\n'.join(out)


class Script:
    """Spoken word stream of a script with act boundaries, for locating quotes by word position."""

    def __init__(self, text, default_acts=6):
        self.text = str(text)
        self.acts = split_acts(self.text, default_acts)
        self.tokens, self.act_start = [], []
        for _, body in self.acts:
            self.act_start.append(len(self.tokens))
            self.tokens.extend(words(spoken(body)))
        self.joined = ' '.join(self.tokens)
        # char offset in self.joined -> token index
        self._char_tok = []
        pos = 0
        for i, t in enumerate(self.tokens):
            self._char_tok.append(pos)
            pos += len(t) + 1

    @property
    def n(self):
        return len(self.tokens)

    def act_of(self, tok):
        a = 0
        for i, s in enumerate(self.act_start):
            if tok >= s:
                a = i
        return a + 1

    def act_words(self, act):
        start = self.act_start[act - 1]
        end = self.act_start[act] if act < len(self.act_start) else self.n
        return start, end

    def find(self, quote, start_tok=0):
        """Token index where `quote` begins (at or after start_tok), else None. Needs at least 3 words to count."""
        q = norm(quote)
        if len(q.split()) < 3:
            return None
        start_char = self._char_tok[start_tok] if 0 <= start_tok < len(self._char_tok) else 0
        while True:
            i = self.joined.find(q, start_char)
            if i < 0:
                return None
            # must start on a word boundary
            if i == 0 or self.joined[i - 1] == ' ':
                end = i + len(q)
                if end == len(self.joined) or self.joined[end] == ' ':
                    return self._tok_at(i)
            start_char = i + 1

    def _tok_at(self, char):
        lo, hi = 0, len(self._char_tok) - 1
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if self._char_tok[mid] <= char:
                lo = mid
            else:
                hi = mid - 1
        return lo

    def contains(self, quote):
        return self.find(quote) is not None
