import argparse
import json
import time

import config
from indexer import build_index, index_exists
from searcher import SearchEngine

MENU = """
=== INFORMATION RETRIEVAL SYSTEM ===
[1] Load & Index Dataset
[2] Search Query
[3] Index Statistics
[4] Exit
===================================="""

NO_INDEX_MESSAGE = "\nIndex belum ada. Jalankan menu [1] terlebih dahulu."


def print_results(results, q_tokens, elapsed):
    """Cetak hasil pencarian: token query, lalu tiap dokumen beserta skornya."""
    print(f"\nQuery setelah preprocessing: {q_tokens}")
    if not results:
        print("Tidak ada dokumen yang cocok.")
        return
    print(f"Top {len(results)} dokumen (cosine similarity), waktu {elapsed * 1000:.0f} ms\n")
    for r in results:
        print(f"[{r['rank']}] skor={r['score']:.4f} | {r['source']}")
        print(f"    Judul  : {r['title']}")
        if r["url"]:
            print(f"    URL    : {r['url']}")
        print(f"    Cuplikan: {r['snippet']}\n")


class IRApp:
    """Menu interaktif. SearchEngine disimpan agar index tidak dibuka ulang tiap pencarian."""

    def __init__(self):
        self.engine = None

    def _close_engine(self):
        if self.engine is not None:
            self.engine.close()
            self.engine = None

    def load_and_index(self):
        """Menu [1]: bangun index dari kelima dataset."""
        self._close_engine()
        ans = input("Batas dokumen per dataset (Enter = semua dokumen): ").strip()
        max_docs = int(ans) if ans.isdigit() and int(ans) > 0 else None
        try:
            meta = build_index(max_docs_per_dataset=max_docs)
        except RuntimeError as e:
            print(f"\n[ERROR] {e}")
            return
        print("\nIndexing selesai.")
        for name, n in meta["docs"].items():
            print(f"  {name:<10}: {n} dokumen")
        print(f"  Total     : {meta['total_docs']} dokumen, {meta['vocab_size']} kata unik, "
              f"{meta['seconds']} detik")

    def search(self):
        """Menu [2]: cari query berulang kali sampai pengguna mengosongkan input."""
        if self.engine is None:
            if not index_exists():
                print(NO_INDEX_MESSAGE)
                return
            self.engine = SearchEngine()
        print("Ketik query (kosongkan lalu Enter untuk kembali ke menu).")
        while True:
            query = input("\nQuery > ").strip()
            if not query:
                return
            t0 = time.time()
            results, q_tokens = self.engine.search(query)
            print_results(results, q_tokens, time.time() - t0)

    def statistics(self):
        """Menu [3] (tambahan): tampilkan ringkasan index yang sudah dibuat."""
        if not index_exists():
            print(NO_INDEX_MESSAGE)
            return
        with open(config.INDEX_DIR / "meta.json") as f:
            meta = json.load(f)
        index_files = (p for p in config.INDEX_DIR.rglob("*") if p.is_file())
        size_mb = sum(p.stat().st_size for p in index_files) / 1e6

        print("\n--- Statistik Index ---")
        for name, n in meta["docs"].items():
            print(f"  {name:<10}: {n} dokumen")
        print(f"  Total dokumen : {meta['total_docs']}")
        print(f"  Kata unik     : {meta['vocab_size']}")
        print(f"  Stemming      : {'aktif' if meta['use_stemming'] else 'nonaktif'}")
        print(f"  Ukuran index  : {size_mb:.1f} MB ({config.INDEX_DIR.name}/)")

    def run(self):
        """Loop menu utama; menu [4] mengakhiri program."""
        actions = {"1": self.load_and_index, "2": self.search, "3": self.statistics}
        while True:
            print(MENU)
            choice = input("Pilih menu: ").strip()
            if choice == "4":
                print("Terima kasih.")
                self._close_engine()
                return
            action = actions.get(choice)
            if action is None:
                print("Pilihan tidak valid.")
            else:
                action()


def main():
    parser = argparse.ArgumentParser(description="Multi-Dataset IR System (CLI)")
    parser.add_argument("--index", action="store_true", help="bangun index lalu keluar")
    parser.add_argument("--max-docs", type=int, default=None,
                        help="batas dokumen per dataset saat --index")
    parser.add_argument("--search", metavar="QUERY", help="cari satu query lalu keluar")
    args = parser.parse_args()

    if args.index:
        print(build_index(max_docs_per_dataset=args.max_docs))
    elif args.search:
        if not index_exists():
            raise SystemExit("Index belum ada. Jalankan: python main.py --index")
        engine = SearchEngine()
        t0 = time.time()
        results, q_tokens = engine.search(args.search)
        print_results(results, q_tokens, time.time() - t0)
        engine.close()
    else:
        IRApp().run()


if __name__ == "__main__":
    main()
