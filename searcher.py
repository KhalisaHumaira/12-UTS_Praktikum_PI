import json
import pickle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from whoosh import index
from whoosh.query import Or, Term
import config
from indonesian_stemmer import IndonesianStemmer
from text_preprocessing import preprocess


class SearchEngine:
    def __init__(self):
        self.ix = index.open_dir(str(config.INDEX_DIR))
        self.searcher = self.ix.searcher()
        with open(config.INDEX_DIR / "meta.json") as f:
            self.meta = json.load(f)
        self.stemmer = None
        if self.meta.get("use_stemming"):
            with open(config.INDEX_DIR / "vocab.pkl", "rb") as f:
                self.stemmer = IndonesianStemmer(pickle.load(f))

    def close(self):
        self.searcher.close()

    def _candidates(self, q_tokens, limit):
        """Tahap 1: Whoosh (BM25F) mengambil dokumen yang memuat term query."""
        terms = sorted(set(q_tokens))
        query = Or([Term(f, t) for f in ("title_idx", "body") for t in terms])
        return self.searcher.search(query, limit=limit)

    @staticmethod
    def _cosine_scores(query_text, docs):
        """Tahap 2: Bag of Words (CountVectorizer), lalu cosine similarity query-dokumen.

        Token sudah bersih dan dipisah spasi, jadi pola token cukup \\S+.
        """
        vectorizer = CountVectorizer(token_pattern=r"\S+", lowercase=False)
        matrix = vectorizer.fit_transform(docs + [query_text])   # baris terakhir = query
        return cosine_similarity(matrix[-1], matrix[:-1]).ravel()

    def search(self, query, top_k=None, candidates=None):
        """Kembalikan (hasil, token query). Hasil: rank, score, source, title, url, snippet."""
        top_k = top_k or config.TOP_K
        candidates = candidates or config.CANDIDATES

        q_tokens = preprocess(query, self.stemmer)
        if not q_tokens:
            return [], q_tokens

        hits = self._candidates(q_tokens, candidates)
        if len(hits) == 0:
            return [], q_tokens

        scores = self._cosine_scores(" ".join(q_tokens), [h["clean"] for h in hits])
        order = scores.argsort()[::-1][:top_k]

        results = []
        for rank, i in enumerate(order, start=1):
            hit = hits[int(i)]
            results.append({
                "rank": rank,
                "score": float(scores[i]),
                "source": hit["source"],
                "title": hit["title"],
                "url": hit["url"],
                "snippet": hit["snippet"],
            })
        return results, q_tokens
