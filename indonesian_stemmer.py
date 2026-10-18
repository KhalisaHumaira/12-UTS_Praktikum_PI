from config import STEM_MIN_FREQ, STEM_MIN_RATIO, STEM_MIN_ROOT_LEN

_VOWELS = "aiueo"

_PARTICLES = ("lah", "kah", "tah", "pun")
_POSSESSIVES = ("nya", "ku", "mu")
_DERIV_SUFFIXES = ("kan", "an", "i")

# Awalan tanpa perubahan bentuk
_SIMPLE_PREFIXES = ("memper", "diper", "keber", "keter", "di", "ke", "se",
                    "ber", "bel", "be", "ter", "per", "pel")

# Awalan me-/pe- dengan perubahan bentuk: (awalan, huruf yang luluh).
# Contoh: men + ulis -> tulis, meny + apu -> sapu, mem + ukul -> pukul.
_ME_RULES = (("menge", ""), ("meng", "k"), ("meny", "s"),
             ("men", "t"), ("mem", "p"), ("me", ""))
_PE_RULES = (("penge", ""), ("peng", "k"), ("peny", "s"),
             ("pen", "t"), ("pem", "p"), ("pe", ""))


def _melting_prefix_candidates(word, rules):
    """Kandidat setelah awalan me-/pe- dibuang, termasuk huruf awal yang luluh."""
    out = set()
    for prefix, melted in rules:
        if word.startswith(prefix):
            rest = word[len(prefix):]
            out.add(rest)
            if melted and rest and rest[0] in _VOWELS:
                out.add(melted + rest)
    return out


def _prefix_candidates(word):
    """Bangkitkan kandidat kata setelah satu awalan dibuang."""
    out = {word[len(p):] for p in _SIMPLE_PREFIXES if word.startswith(p)}
    out |= _melting_prefix_candidates(word, _ME_RULES)
    out |= _melting_prefix_candidates(word, _PE_RULES)
    out.discard(word)
    return out


def _suffix_candidates(word):
    """Bangkitkan kandidat kata setelah satu akhiran dibuang."""
    out = set()
    for s in _PARTICLES + _POSSESSIVES + _DERIV_SUFFIXES:
        if word.endswith(s):
            out.add(word[: -len(s)])
    out.discard(word)
    return out


class IndonesianStemmer:
    """Stemmer dengan validasi frekuensi korpus.

    vocab: dict kata -> frekuensi (hasil pass pertama indexing).
    """

    def __init__(self, vocab=None):
        self.vocab = vocab if vocab is not None else {}
        self._cache = {}

    def _valid(self, cand, orig_freq):
        if len(cand) < STEM_MIN_ROOT_LEN:
            return False
        f = self.vocab.get(cand, 0)
        return f >= STEM_MIN_FREQ and f >= STEM_MIN_RATIO * orig_freq

    def stem(self, word):
        cached = self._cache.get(word)
        if cached is not None:
            return cached
        result = self._stem(word)
        self._cache[word] = result
        return result

    def _stem(self, word):
        if len(word) <= STEM_MIN_ROOT_LEN:
            return word
        orig_freq = self.vocab.get(word, 0)

        # Telusuri kombinasi pembuangan imbuhan (maks. 4 langkah), simpan yang valid.
        accepted = []
        seen = {word}
        frontier = {word}
        for _ in range(4):
            nxt = set()
            for w in frontier:
                for c in _suffix_candidates(w) | _prefix_candidates(w):
                    if c in seen or len(c) < 3:
                        continue
                    seen.add(c)
                    nxt.add(c)
                    if self._valid(c, orig_freq):
                        accepted.append(c)
            frontier = nxt
            if not frontier:
                break

        if not accepted:
            return word
        # paling pendek; jika sama, yang paling sering muncul
        accepted.sort(key=lambda c: (len(c), -self.vocab.get(c, 0)))
        return accepted[0]
