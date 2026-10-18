# UTS Praktikum Penelusuran Informasi - Kelompok 12

Anggota:
- Cut Wynona Andromeda (2408107010097)
- Nayla Khansa Livya (2408107010098)
- Khalisa Humaira (2408107010099)

## Tentang Program

Program ini adalah sistem Information Retrieval berbasis CLI. Program bisa mencari
dokumen dari 5 dataset (etd-usk, etd-ugm, kompas, tempo, mojok) lalu menampilkan 5
dokumen yang paling mirip dengan query.

Cara kerjanya secara singkat:

1. Teks dibersihkan: huruf dikecilkan, dipecah jadi kata, stopword dibuang, lalu
   kata diubah ke bentuk dasarnya (stemming).
2. Dokumen disimpan ke index Whoosh.
3. Saat query dimasukkan, Whoosh mengambil 300 dokumen kandidat.
4. Kandidat dan query diubah ke Bag of Words (CountVectorizer), lalu diurutkan
   berdasarkan cosine similarity. Lima teratas ditampilkan.

Library yang dipakai: scikit-learn, Whoosh, dan pandas, ditambah library standar Python.

## Isi Folder
12_UTS_Praktikum_PI

- main.py                 program utama (menu CLI)
- config.py               pengaturan
- text_preprocessing.py   preprocessing dan tokenisasi
- indonesian_stemmer.py   stemmer bahasa Indonesia
- data_loader.py          membaca file CSV
-  indexer.py              membuat index Whoosh
-  searcher.py             pencarian dan ranking
-  run_queries.py          menjalankan banyak query sekaligus
-  requirements.txt

- datasets
    - etd-usk
    - etd-ugm
    -  kompas
    -  tempo
    -  mojok


## Cara Menjalankan

1. Masukkan file CSV ke folder `datasets` 

   - etd_usk.csv ke datasets/etd-usk/
   - etd_ugm.csv ke datasets/etd-ugm/
   - kompas.csv ke datasets/kompas/
   - tempo.csv ke datasets/tempo/
   - mojok.csv ke datasets/mojok/

2. Jalankan program:

   python3 main.py

3. Menu yang muncul:

   === INFORMATION RETRIEVAL SYSTEM ===
   [1] Load & Index Dataset
   [2] Search Query
   [3] Exit
   ====================================
 
   - Pilih 1 untuk membuat index. Program akan bertanya batas dokumen per
     dataset. Isi 2000 kalau mau coba cepat, atau tekan Enter untuk memakai semua
     dokumen (butuh beberapa menit).
   - Pilih 2 untuk mencari. Ketik query lalu Enter. Tekan Enter tanpa mengetik
     apa-apa untuk kembali ke menu.
   - Pilih 3 untuk keluar.

   Menu 1 harus dijalankan dulu sebelum menu 2.

## Catatan

- Kolom CSV yang dipakai adalah `judul` dan `konten`. Kalau nama kolomnya
  berbeda, ubah `COLUMN_OVERRIDES` di `config.py`.
- Stemmer dibuat sendiri karena library stemmer seperti Sastrawi tidak termasuk
  yang diizinkan. Hasilnya belum sempurna, misalnya "pembelajaran" menjadi
  "ajaran". Stemming bisa dimatikan dengan mengubah `USE_STEMMING` menjadi
  `False` di `config.py`, lalu index ulang.
- Untuk menguji banyak query sekaligus (dipakai untuk laporan):

  python run_queries.py "query 1" "query 2" "query 3"

  Hasilnya disimpan di file `hasil_pengujian.md`.
