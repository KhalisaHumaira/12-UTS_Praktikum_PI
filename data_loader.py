import re
import pandas as pd
import config

_CHUNK_ROWS = 5000

def find_csv_files(name):

    root = config.DATASET_DIR
    alt = name.replace("-", "_")
    files = []
    for d in (root / name, root / alt):
        if d.is_dir():
            files.extend(sorted(d.glob("*.csv")))
    for f in (root / f"{name}.csv", root / f"{alt}.csv"):
        if f.is_file():
            files.append(f)
    # buang duplikat (mis. name == alt untuk kompas/tempo/mojok) dengan urutan tetap
    return list(dict.fromkeys(files))


def _pick_column(lowered, candidates):
    """Kolom pertama dari `candidates` yang ada di dataset (None jika tidak ada)."""
    for cand in candidates:
        if cand in lowered:
            return lowered[cand]
    return None


def _is_content_column(low_name):
    """Kolom isi: nama kolom memuat kata dari CONTENT_KEYWORDS atau diawali 'abstra'."""
    words = [w for w in re.split(r"[^a-z]+", low_name) if w]
    return any(w in config.CONTENT_KEYWORDS or w.startswith("abstra") for w in words)


def detect_columns(columns, name):
    """Tentukan kolom judul, isi, dan url dari daftar nama kolom."""
    lowered = {c.lower().strip(): c for c in columns}
    override = config.COLUMN_OVERRIDES.get(name, {})

    title = override.get("title") or _pick_column(lowered, config.TITLE_COLUMNS)
    url = override.get("url") or _pick_column(lowered, config.URL_COLUMNS)

    if override.get("content"):
        content = override["content"]
        content = [content] if isinstance(content, str) else list(content)
    else:
        content = [orig for low, orig in lowered.items()
                   if orig not in (title, url) and _is_content_column(low)]
    return title, content, url


def _fallback_content_column(df, exclude):
    """Jika tidak ada kolom isi yang dikenali: pakai kolom teks dengan rata-rata terpanjang."""
    best, best_len = None, 0
    for col in df.columns:
        if col in exclude:
            continue
        avg = df[col].dropna().astype(str).str.len().mean()
        if avg and avg > best_len:
            best, best_len = col, avg
    return [best] if best else []


def _resolve_columns(chunk, name):
    """Deteksi kolom dari chunk pertama; pakai kolom teks terpanjang jika isi tidak ketemu."""
    title_col, content_cols, url_col = detect_columns(chunk.columns, name)
    if not content_cols:
        content_cols = _fallback_content_column(chunk, exclude={title_col, url_col})
    return title_col, content_cols, url_col


def _cell(row, column):
    """Isi sel sebagai string (kosong jika kolom tidak ada atau nilainya NaN)."""
    value = row[column] if column else ""
    return value if isinstance(value, str) else ""


def _build_document(row, columns, name, number):
    """Ubah satu baris CSV menjadi dokumen; None jika judul dan isinya kosong."""
    title_col, content_cols, url_col = columns
    title = _cell(row, title_col)
    parts = [v for v in (_cell(row, c) for c in content_cols) if v.strip()]
    content = "\n".join(parts)
    if not title and not content:
        return None
    return {
        "source": name,
        "doc_id": f"{name}-{number}",
        "title": title.strip(),
        "content": content,
        "url": _cell(row, url_col),
    }


def iter_documents(name, max_docs=None, verbose=True):
    """Hasilkan dokumen (dict) dari dataset `name`.

    Setiap dokumen: source, doc_id, title, content, url.
    File dibaca bertahap (chunk) agar CSV besar tidak dimuat sekaligus.
    """
    files = find_csv_files(name)
    if not files:
        if verbose:
            print(f"  [!] Dataset '{name}' tidak ditemukan di {config.DATASET_DIR}")
        return

    count = 0
    for path in files:
        reader = pd.read_csv(path, dtype=str, chunksize=_CHUNK_ROWS, on_bad_lines="skip",
                             encoding="utf-8", encoding_errors="replace")
        columns = None
        for chunk in reader:
            if columns is None:
                columns = _resolve_columns(chunk, name)
                if verbose:
                    print(f"  {path.name}: judul={columns[0]!r}, isi={columns[1]}, "
                          f"url={columns[2]!r}")
            for _, row in chunk.iterrows():
                doc = _build_document(row, columns, name, count)
                if doc is None:
                    continue
                yield doc
                count += 1
                if max_docs and count >= max_docs:
                    return


def snippet_of(text, length=220):
    """Potongan teks bersih untuk ditampilkan pada hasil pencarian."""
    text = re.sub(r"<[^>]+>", " ", text or "")
    text = re.sub(r"\s+", " ", text).strip()
    return text[:length] + ("..." if len(text) > length else "")
