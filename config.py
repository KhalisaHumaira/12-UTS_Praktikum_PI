from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Folder dataset sesuai struktur soal: datasets/<nama-dataset>/*.csv
DATASET_DIR = BASE_DIR / "datasets"
INDEX_DIR = BASE_DIR / "index_dir"

# Lima dataset wajib
DATASETS = ["etd-usk", "etd-ugm", "kompas", "tempo", "mojok"]

# Pengaturan pencarian
TOP_K = 5              # jumlah dokumen yang ditampilkan
CANDIDATES = 300       # kandidat dari Whoosh yang di-rerank dengan cosine similarity

# Pengaturan preprocessing
USE_STEMMING = True    # fitur opsional: stemming bahasa Indonesia (buatan sendiri)
MIN_TOKEN_LEN = 2

# Pengaturan stemmer (lihat indonesian_stemmer.py)
STEM_MIN_ROOT_LEN = 4      # panjang minimal kata dasar
STEM_MIN_FREQ = 2          # kata dasar harus muncul minimal sekian kali di korpus
STEM_MIN_RATIO = 0.05      # frekuensi kata dasar >= rasio * frekuensi kata asal

# Kandidat nama kolom CSV (huruf kecil). Dipakai untuk deteksi otomatis kolom.
TITLE_COLUMNS = ["title", "judul", "headline", "judul_berita", "name"]
URL_COLUMNS = ["url", "link", "href", "source_url", "uri"]
# Kolom yang salah satu kata penyusun namanya (dipisah _ atau -) ada di daftar ini
# dianggap kolom isi teks. Kata yang diawali "abstra" (abstract/abstrak) juga dikenali.
CONTENT_KEYWORDS = ["content", "isi", "text", "body", "konten", "article", "artikel",
                    "description", "deskripsi", "berita", "narasi"]

# Jika deteksi otomatis salah, isi manual di sini. Contoh:
# COLUMN_OVERRIDES = {
#     "etd-usk": {"title": "judul", "content": ["abstrak", "abstract"], "url": "link"},
# }
COLUMN_OVERRIDES = {}
