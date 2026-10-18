import re
from config import MIN_TOKEN_LEN

# Stopword bahasa Indonesia (+ sedikit bahasa Inggris, karena abstrak ETD sering bilingual)
_STOPWORDS_ID = """
ada adalah adanya adapun agak agaknya agar akan akankah akhir akhirnya aku akulah amat amatlah
anda andalah antar antara antaranya apa apaan apabila apakah apalagi apatah artinya asal asalkan
atas atau ataukah ataupun awal awalnya bagai bagaikan bagaimana bagaimanakah bagaimanapun bagi
bagian bahkan bahwa bahwasanya baik bakal bakalan balik banyak bapak baru bawah beberapa begini
beginian beginikah beginilah begitu begitukah begitulah begitupun bekerja belakang belakangan
belum belumlah benar benarkah benarlah berada berakhir berakhirlah berakhirnya berapa berapakah
berapalah berapapun berarti berawal berbagai berdatangan beri berikan berikut berikutnya berjumlah
berkali berkata berkehendak berkeinginan berkenaan berlainan berlalu berlangsung berlebihan
bermacam bermaksud bermula bersama bersiap bertanya berturut bolehkah bolehlah buat bukan bukankah
bukanlah bukannya bulan bung cara caranya cukup cukupkah cukuplah cuma dahulu dalam dan dapat dari
daripada datang dekat demi demikian demikianlah dengan depan di dia diakhiri diakhirinya dialah
diantara diantaranya diberi diberikan diberikannya dibuat dibuatnya didapat didatangkan digunakan
diibaratkan diibaratkannya diingat diingatkan diinginkan dijawab dijelaskan dijelaskannya dikarenakan
dikatakan dikatakannya dikerjakan diketahui diketahuinya dikira dilakukan dilalui dilihat dimaksud
dimaksudkan dimaksudkannya dimaksudnya diminta dimintai dimisalkan dimulai dimulailah dimulainya
dimungkinkan dini dipastikan diperbuat diperbuatnya dipergunakan diperkirakan diperlihatkan
diperlukan diperlukannya dipersoalkan dipertanyakan dipunyai diri dirinya disampaikan disebut
disebutkan disebutkannya disini disinilah ditambahkan ditandaskan ditanya ditanyai ditanyakan
ditegaskan ditujukan ditunjuk ditunjuki ditunjukkan ditunjukkannya ditunjuknya dituturkan
dituturkannya diucapkan diucapkannya diungkapkan dong dua dulu empat enggak enggaknya entah entahlah
guna gunakan hal hampir hanya hanyalah hari harus haruslah harusnya hendak hendaklah hendaknya
hingga ia ialah ibarat ibaratkan ibaratnya ibu ikut ingat ingat-ingat ingin inginkah inginkan ini
inikah inilah itu itukah itulah jadi jadilah jadinya jangan jangankan janganlah jauh jawab jawaban
jawabnya jelas jelaskan jelaslah jelasnya jika jikalau juga jumlah jumlahnya justru kala kalau
kalaulah kalaupun kalian kami kamilah kamu kamulah kan kapan kapankah kapanpun karena karenanya
kasus kata katakan katakanlah katanya ke keadaan kebetulan kecil kedua keduanya keinginan kelamaan
kelihatan kelihatannya kelima keluar kembali kemudian kemungkinan kemungkinannya kenapa kepada
kepadanya kesampaian keseluruhan keseluruhannya keterlaluan ketika khususnya kini kinilah kira
kira-kira kiranya kita kitalah kok kurang lagi lagian lah lain lainnya lalu lama lamanya lanjut
lanjutnya lebih lewat lima luar macam maka makanya makin malah malahan mampu mampukah mana manakala
manalagi masa masalah masalahnya masih masihkah masing masing-masing mau maupun melainkan melakukan
melalui melihat melihatnya memang memastikan memberi memberikan membuat memerlukan memihak meminta
memintakan memisalkan memperbuat mempergunakan memperkirakan memperlihatkan mempersiapkan
mempersoalkan mempertanyakan mempunyai memulai memungkinkan menaiki menambahkan menandaskan
menanti menantikan menanya menanyai menanyakan mendapat mendapatkan mendatang mendatangi
mendatangkan menegaskan mengakhiri mengapa mengatakan mengatakannya mengenai mengerjakan mengetahui
menggunakan menghendaki mengibaratkan mengibaratkannya mengingat mengingatkan menginginkan
mengira mengucapkan mengucapkannya mengungkapkan menjadi menjawab menjelaskan menuju menunjuk
menunjuki menunjukkan menunjuknya menurut menuturkan menyampaikan menyangkut menyatakan menyebutkan
menyeluruh menyiapkan merasa mereka merekalah merupakan meski meskipun meyakini meyakinkan minta
mirip misal misalkan misalnya mula mulai mulailah mulanya mungkin mungkinkah nah naik namun nanti
nantinya nyaris nyatanya oleh olehnya pada padahal padanya pak paling panjang pantas para pasti
pastilah penting pentingnya per percuma perlu perlukah perlunya pernah persoalan pertama pertama-tama
pertanyaan pertanyakan pihak pihaknya pukul pula pun punya rasa rasanya rata rupanya saat saatnya
saja sajalah saling sama sama-sama sambil sampai sampai-sampai sampaikan sana sangat sangatlah
satu saya sayalah se sebab sebabnya sebagai sebagaimana sebagainya sebagian sebaik sebaik-baiknya
sebaiknya sebaliknya sebanyak sebegini sebegitu sebelum sebelumnya sebenarnya seberapa sebesar
sebetulnya sebisanya sebuah sebut sebutlah sebutnya secara secukupnya sedang sedangkan sedemikian
sedikit sedikitnya seenaknya segala segalanya segera seharusnya sehingga seingat sejak sejauh
sejenak sejumlah sekadar sekadarnya sekali sekali-kali sekalian sekaligus sekalipun sekarang
sekarang sekecil seketika sekiranya sekitar sekitarnya sekurang-kurangnya sekurangnya sela selain
selaku selalu selama selama-lamanya selamanya selanjutnya seluruh seluruhnya semacam semakin semampu
semampunya semasa semasih semata semata-mata semaunya sementara semisal semisalnya sempat semua
semuanya semula sendiri sendirian sendirinya seolah seolah-olah seorang sepanjang sepantasnya
sepantasnyalah seperlunya seperti sepertinya sepihak sering seringnya serta serupa sesaat sesama
sesampai sesegera sesekali seseorang sesuatu sesuatunya sesudah sesudahnya setelah setempat
setengah seterusnya setiap setiba setibanya setidak-tidaknya setidaknya setinggi seusai sewaktu
siap siapa siapakah siapapun sini sinilah soal soalnya suatu sudah sudahkah sudahlah supaya tadi
tadinya tahu tahun tak tambah tambahnya tampak tampaknya tandas tandasnya tanpa tanya tanyakan
tanyanya tapi tegas tegasnya telah tempat tengah tentang tentu tentulah tentunya tepat terakhir
terasa terbanyak terdahulu terdapat terdiri terhadap terhadapnya teringat teringat-ingat terjadi
terjadilah terjadinya terkira terlalu terlebih terlihat termasuk ternyata tersampaikan tersebut
tersebutlah tertentu tertuju terus terutama tetap tetapi tiap tiba tiba-tiba tidak tidakkah
tidaklah tiga tinggi toh tunjuk turut tutur tuturnya ucap ucapnya ujar ujarnya umum umumnya ungkap
ungkapnya untuk usah usai waduh wah wahai waktu waktunya walau walaupun wong yaitu yakin yakni yang
""".split()

_STOPWORDS_EN = """
the of and in to is for with on by that this are as from at an be or it was were which has have
had not but can will also their its these those such been between into than other using used use
""".split()

# Kata bertanda hubung (mis. "kira-kira") dibuang dari daftar: tokenisasi sudah memecahnya,
# jadi tidak akan pernah cocok.
STOPWORDS = frozenset(w for w in _STOPWORDS_ID if w.isalpha()) | frozenset(_STOPWORDS_EN)

_URL_RE = re.compile(r"https?://\S+|www\.\S+")
_TAG_RE = re.compile(r"<[^>]+>")
_ENTITY_RE = re.compile(r"&[a-z]{2,8};|&#\d+;")
_TOKEN_RE = re.compile(r"[a-z]+")


def case_folding(text):
    """Ubah teks menjadi huruf kecil."""
    return text.lower()


def clean_text(text):
    """Buang URL, tag HTML, dan entitas HTML dari teks."""
    text = _URL_RE.sub(" ", text)
    text = _TAG_RE.sub(" ", text)
    text = _ENTITY_RE.sub(" ", text)
    return text


def tokenize(text):
    """Tokenisasi: ambil rangkaian huruf a-z (angka dan tanda baca dibuang)."""
    return _TOKEN_RE.findall(text)


def remove_stopwords(tokens):
    """Buang stopword dan token yang terlalu pendek."""
    return [t for t in tokens if len(t) >= MIN_TOKEN_LEN and t not in STOPWORDS]


def preprocess(text, stemmer=None):
    """Pipeline lengkap: cleaning -> case folding -> tokenisasi -> stopword -> (stemming).

    Mengembalikan list token.
    """
    if not isinstance(text, str) or not text:
        return []
    tokens = remove_stopwords(tokenize(case_folding(clean_text(text))))
    if stemmer is not None:
        tokens = [stemmer.stem(t) for t in tokens]
    return tokens
