import json
import pickle
import shutil
import time
from collections import Counter

from whoosh import index
from whoosh.analysis import RegexTokenizer
from whoosh.fields import ID, STORED, TEXT, Schema

import config
from data_loader import iter_documents, snippet_of
from indonesian_stemmer import IndonesianStemmer
from text_preprocessing import case_folding, clean_text, remove_stopwords, tokenize

# Teks yang disimpan di index sudah berupa token dipisah spasi -> tokenizer cukup \S+
_WS = RegexTokenizer(expression=r"\S+")

SCHEMA = Schema(
    doc_id=ID(stored=True, unique=True),
    source=ID(stored=True),
    title=STORED,
    url=STORED,
    snippet=STORED,
    clean=STORED,   # teks hasil preprocessing (judul + isi), dipakai untuk cosine similarity
    title_idx=TEXT(analyzer=_WS, field_boost=2.0, phrase=False),
    body=TEXT(analyzer=_WS, phrase=False),
)


def _base_tokens(text):
    """Preprocessing tanpa stemming (untuk pass 1)."""
    if not isinstance(text, str) or not text:
        return []
    return remove_stopwords(tokenize(case_folding(clean_text(text))))


def index_exists():
    return config.INDEX_DIR.exists() and index.exists_in(str(config.INDEX_DIR))


def count_vocabulary(max_docs, log=print):
    """Pass 1: baca semua dataset. Mengembalikan (jumlah dokumen per dataset, kosakata)."""
    stats, vocab = {}, Counter()
    for name in config.DATASETS:
        log(f"- {name}")
        n = 0
        for doc in iter_documents(name, max_docs):
            vocab.update(_base_tokens(doc["title"]))
            vocab.update(_base_tokens(doc["content"]))
            n += 1
            if n % 5000 == 0:
                log(f"    {n} dokumen dibaca")
        stats[name] = n
        log(f"  selesai: {n} dokumen")
    return stats, vocab


def write_index(vocab, total, max_docs, use_stemming, log=print):
    """Pass 2: preprocessing + stemming, lalu tulis setiap dokumen ke index Whoosh."""
    stemmer = IndonesianStemmer(vocab) if use_stemming else None

    def prep(text):
        tokens = _base_tokens(text)
        if stemmer is not None:
            tokens = [stemmer.stem(t) for t in tokens]
        return tokens

    if config.INDEX_DIR.exists():
        shutil.rmtree(config.INDEX_DIR)
    config.INDEX_DIR.mkdir(parents=True)
    ix = index.create_in(str(config.INDEX_DIR), SCHEMA)
    writer = ix.writer(limitmb=256)

    done = 0
    for name in config.DATASETS:
        for doc in iter_documents(name, max_docs, verbose=False):
            title_toks = prep(doc["title"])
            body_toks = prep(doc["content"])
            writer.add_document(
                doc_id=doc["doc_id"],
                source=doc["source"],
                title=doc["title"] or "(tanpa judul)",
                url=doc["url"],
                snippet=snippet_of(doc["content"] or doc["title"]),
                clean=" ".join(title_toks + body_toks),
                title_idx=" ".join(title_toks),
                body=" ".join(body_toks),
            )
            done += 1
            if done % 5000 == 0:
                log(f"    {done}/{total} dokumen di-index")
    log("Menyimpan (commit) index...")
    writer.commit()


def save_metadata(vocab, stats, use_stemming):
    """Simpan kosakata (untuk stemmer saat pencarian) dan ringkasan index."""
    with open(config.INDEX_DIR / "vocab.pkl", "wb") as f:
        pickle.dump(dict(vocab), f)
    meta = {"use_stemming": bool(use_stemming), "docs": stats,
            "total_docs": sum(stats.values()), "vocab_size": len(vocab)}
    with open(config.INDEX_DIR / "meta.json", "w") as f:
        json.dump(meta, f, indent=2)
    return meta


def build_index(max_docs_per_dataset=None, use_stemming=None, log=print):
    """Bangun index dari 5 dataset. Mengembalikan dict statistik."""
    if use_stemming is None:
        use_stemming = config.USE_STEMMING
    t0 = time.time()

    log("\n[Pass 1/2] Membaca dataset dan menghitung kosakata...")
    stats, vocab = count_vocabulary(max_docs_per_dataset, log)
    total = sum(stats.values())
    if total == 0:
        raise RuntimeError(
            f"Tidak ada dokumen yang dibaca. Letakkan CSV di {config.DATASET_DIR}/<nama-dataset>/")
    log(f"\nKosakata: {len(vocab)} kata unik dari {total} dokumen "
        f"({time.time() - t0:.1f} detik)")

    log("\n[Pass 2/2] Preprocessing, stemming, dan indexing dengan Whoosh...")
    write_index(vocab, total, max_docs_per_dataset, use_stemming, log)

    meta = save_metadata(vocab, stats, use_stemming)
    meta["seconds"] = round(time.time() - t0, 1)
    return meta
