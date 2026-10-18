import argparse
from searcher import SearchEngine
def main():
    p = argparse.ArgumentParser()
    p.add_argument("queries", nargs="*")
    p.add_argument("--file")
    p.add_argument("--out", default="hasil_pengujian.md")
    args = p.parse_args()

    queries = list(args.queries)
    if args.file:
        with open(args.file, encoding="utf-8") as f:
            queries += [ln.strip() for ln in f if ln.strip()]
    if not queries:
        raise SystemExit("Berikan minimal satu query.")

    engine = SearchEngine()
    lines = ["# Hasil Pengujian Query\n"]
    for q in queries:
        results, tokens = engine.search(q)
        lines.append(f"## Query: {q}\n")
        lines.append(f"Token setelah preprocessing: `{tokens}`\n")
        if not results:
            lines.append("Tidak ada hasil.\n")
            continue
        lines.append("| Rank | Skor | Dataset | Judul |")
        lines.append("|---|---|---|---|")
        for r in results:
            title = r["title"].replace("|", "/")[:90]
            lines.append(f"| {r['rank']} | {r['score']:.4f} | {r['source']} | {title} |")
        lines.append("")
    engine.close()

    with open(args.out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Hasil disimpan ke {args.out}")


if __name__ == "__main__":
    main()
