# Desain: Profil GitHub @RayNathans · Konsep Cyberpunk (Mockup B rev 2)

Tanggal: 2026-11-04
Status: disetujui lewat mockup interaktif (`.superpowers/brainstorm/3686-1793773675/content/concept-cyberpunk-v2.html`)
Target: repo `RayNathans/RayNathans` (profile README) + metadata profil GitHub

## 1. Maksud dan alasan

Nathan (Nikolaus Ray Nathan, Full Stack Developer, Surabaya) ingin halaman
github.com/RayNathans menjadi "super duper menarik": tampilan futuristik
cyberpunk, dominan biru neon dengan aksen magenta, penuh animasi, dan terasa
interaktif meski GitHub tidak mengizinkan JavaScript. Profil saat ini kosong:
tanpa nama, bio, lokasi, maupun README.

Tujuan praktisnya: pengunjung (rekruter, rekan developer) langsung menangkap
siapa Nathan, stack-nya, pengalaman kerjanya, proyek nyatanya, dan cara
menghubunginya, dengan kesan "developer yang peduli detail".

Sumber data profil: portofolio https://nathporto.netlify.app/ dan LinkedIn
https://www.linkedin.com/in/nikolaus-ray-nathan/.

## 2. Keputusan pengguna (tercatat dari klik di mockup)

| Hal | Keputusan |
|---|---|
| Konsep | **B · Cyberpunk** murni (bukan kartun, bukan gabungan) |
| Palet | **Biru neon + sentuhan magenta** (bukan magenta kuat, bukan kuning) |
| Figur hero | **Hologram foto** avatar GitHub di dalam bingkai heksagon bercincin |
| Intensitas efek | **Penuh**: glitch, hujan, neon berkedip |
| Bahasa | Teks isi **Bahasa Indonesia**; judul seksi **campur** (istilah HUD Inggris seperti `SKILL MATRIX`, `MISSION LOGS`, `TELEMETRY`, dipadukan teks Indonesia) |
| Panjang | Halaman lengkap, enam seksi + hero + footer |
| Hero | **Tanpa** label `LOC: SURABAYA // ID` dan `UPTIME: 1+ YRS`; hanya `SYS.ONLINE` |
| Bagian favorit | Hero kota neon + glitch, terminal about.json, skill matrix, mission logs, telemetry + snake |

## 3. Goals, non-goals, anti-goals

**Goals**

- README profil yang di GitHub asli terlihat sedekat mungkin dengan mockup B rev 2.
- Semua animasi berjalan tanpa JavaScript: SVG animasi (CSS keyframes/SMIL), readme-typing-svg, kartu stats, snake dari GitHub Actions.
- Interaktif sebatas yang GitHub izinkan: tautan/kartu yang bisa diklik, `<details>` untuk sertifikat, badge yang mengarah ke tautan.
- Data nyata dari akun: stats, streak, top languages, snake, visitor counter.
- Metadata profil GitHub terisi: nama, bio, lokasi, website, LinkedIn.
- Semua aset dan sumber generatornya tersimpan di repo agar Nathan bisa mengubah sendiri (ganti angka skill, tambah proyek).

**Non-goals**

- Tidak membuat situs GitHub Pages atau mengubah portofolio Netlify.
- Tidak menyentuh repo lain milik Nathan (testdemo, litera, present).
- Tidak meniru efek yang mustahil di README: hover, scanline layar penuh, kursor mengikuti mouse.

**Anti-goals** (gagal walau "jalan")

- Teks hero/nama tidak terbaca karena glitch terlalu agresif atau kontras rendah.
- Aset berat: satu SVG > 400 KB atau halaman terasa lambat memuat.
- Tampilan pecah di layar sempit (GitHub mobile) atau pada tema terang GitHub.
- Angka palsu yang terlihat seperti data nyata (mis. profile views atau stats hard-coded).

## 4. Batasan teknis (fakta tentang GitHub README)

- Markdown GitHub membersihkan HTML: tidak ada `<script>`, `<style>`, `<iframe>`, atribut `style`, atau event. Tata letak hanya lewat `<table>`, `<p align>`, `<img width>`, `<details>`, `<picture>`.
- SVG ditampilkan lewat `<img>` dan proxy camo: SVG **tidak boleh memuat sumber eksternal** (font Google, gambar avatar, CSS luar). Semua font dan gambar harus **di-embed sebagai data URI** di dalam SVG.
- CSS `@keyframes` dan SMIL di dalam `<style>` SVG tetap jalan di `<img>`. Media query `prefers-reduced-motion` di dalam SVG boleh dipakai sebagai bonus.
- Cache camo: perubahan aset muncul setelah beberapa menit; URL raw harus memakai path cabang `main`.
- Tidak ada `gh` CLI di mesin ini; ada `git 2.53`, Python 3.11 (Pillow tersedia, fontTools belum), Node 24.

## 5. Palet dan tipografi

```
--bg      #03040d   latar utama
--panel   #0a0f24   panel/kartu
--line    #15214a   garis HUD
--ink     #dbe7ff   teks
--muted   #7f93c4   teks redup
--c1      #00e5ff   cyan neon (utama)
--c2      #2f6bff   electric blue
--c3      #ff2bd6   magenta (aksen, dipakai hemat)
--c4      #7c3aed   violet (pelengkap)
ok        #22c55e   status hijau
```

Font: **Orbitron** (judul besar, nama), **Share Tech Mono** (label HUD, terminal),
**Rajdhani** (teks di dalam SVG bila perlu). Di SVG, font di-embed sebagai subset
woff2 base64; fallback `monospace`/`sans-serif`. Teks markdown biasa memakai font
GitHub (tidak bisa diubah).

## 6. Struktur halaman (urut dari atas)

Setiap blok di bawah menyebut bagaimana ia diwujudkan di GitHub.

### 6.1 Hero `assets/hero.svg` (SVG animasi, lebar penuh, rasio ±3:1)

- Kota neon: skyline jauh gelap, gedung dekat bergradasi biru, jendela cyan/magenta
  **berkedip** acak, lampu antena merah, papan neon `LARAVEL` (magenta) dan
  `NEXT.JS` (cyan) yang **flicker**, label kecil `SBY-07 // SECTOR 2026`.
- Lantai grid perspektif yang **bergerak** ke arah penonton; **hujan** garis tipis
  cyan jatuh terus-menerus.
- Kiri: baris status `● SYS.ONLINE` (titik hijau berdenyut), judul
  `NIKOLAUS RAY NATHAN` Orbitron dengan efek **glitch** (dua salinan cyan/magenta
  bergeser + potongan clip berkala), subjudul `FULL STACK DEVELOPER`, lalu kotak
  terminal kecil berisi `nathan@github:~$` dan dua baris output
  (`loading stack: laravel, next.js, typescript, postgresql [OK]`,
  `status: building PWA for field technicians [RUNNING]`).
- Kanan: **hologram foto**: avatar GitHub (di-embed base64, dipotong heksagon,
  tint cyan) dengan tiga cincin berputar, garis scan vertikal naik-turun, label
  `ID: RAY_NATHANS · LVL 24`. Drone kecil melayang di pojok kanan atas.
- Satu drone, satu label hologram, tidak ada teks lokasi/uptime.

Di bawah hero, baris **typing** memakai readme-typing-svg (font Share Tech Mono,
warna cyan, latar transparan) yang bergantian mengetik:
`whoami`, `cat about.json`, `./deploy --prod`, `git push origin main`.

### 6.2 Status strip

Empat sel dalam `<table>` satu baris: `ROLE → BACKEND_DEV`,
`COMPANY → PERFORMA OPTIMA GROUP`, `CERTS → 09 · DICODING`,
`PROFILE VIEWS → ` counter komarev (warna cyan). Tiap sel adalah badge
shields.io `for-the-badge` warna panel dengan label cyan, agar konsisten di tema
terang/gelap.

### 6.3 `01 // IDENTITY`

- Judul seksi: SVG kecil `assets/h-01.svg` (dan seterusnya untuk 02–06) agar
  memakai Orbitron + garis HUD neon; semuanya dihasilkan satu template.
- Kiri (sel tabel 60%): blok kode ```jsonc berisi about.json persis seperti mockup
  (`nama`, `peran`, `sekarang`, `basis`, `stack`, `sedang_belajar`, `motto`,
  `kopi: true // selalu`). Syntax highlight bawaan GitHub.
- Kanan (sel 40%): lima fakta bernomor `[01]`…`[05]` sesuai mockup.

### 6.4 `02 // SKILL MATRIX` `assets/skills.svg`

Dua kolom, 12 skill, tiap baris: nama (Share Tech Mono), 20 segmen bar yang
**menyala berurutan** saat dimuat lalu berdenyut pelan, persentase di kanan.
Data awal (self-assessment, dapat diedit Nathan di `data/skills.json`):
Laravel 87, Next.js 90, TypeScript 85, React 95, PHP 98, PostgreSQL 85, MySQL 90,
Tailwind 95, Python 70, Node.js 85, Git 92, Supabase 75. Di bawahnya baris
badge logo teknologi (shields.io, gaya `for-the-badge`, warna panel + logo
berwarna) sebagai "ikon" yang bisa diklik ke situs resminya.

### 6.5 `03 // MISSION LOGS`

Tabel tiga kolom, satu kartu per proyek. Tiap kartu = `<a>` ke demo yang
membungkus SVG ilustrasi animasi `assets/proj-*.svg` (bingkai HUD, label status
berkedip), lalu judul, deskripsi Indonesia, chip teknologi (badge kecil), dan
tautan `> LIVE DEMO · > SOURCE`.

| Kartu | Status | Ilustrasi | Stack | Live |
|---|---|---|---|---|
| FRUIT CHECK // FRUCH | DEPLOYED | lingkaran buah + panel `SCAN: RIPE ✔ 97%` | Next.js, React, TypeScript, Tailwind | https://dicoding-milestone-fruch.vercel.app/ |
| DICODING STORY | DEPLOYED | grid peta + titik geo berdenyut, `GEO-TAG: -7.25, 112.75` | JavaScript, REST API, Tailwind | https://nathdicodingstory.netlify.app/ |
| SIPOLUBOGO POS | IN PRODUCTION | struk `ORDER #128 … Rp 85.000 ✔` + lingkaran `POS` | Laravel, PHP, MySQL, Tailwind | https://sipolubogo.cartera.my.id/ |

Tautan SOURCE hanya dipasang bila repo publiknya diketahui; kalau tidak, kartu
hanya menampilkan LIVE DEMO (jangan tautan `#`).

### 6.6 `04 // TELEMETRY`

- Dua kartu bersisian: github-readme-stats (`show_icons`, ring rank) dan
  streak-stats; di bawahnya top-langs layout compact. Semua memakai tema kustom
  via parameter warna: bg `03040d` (atau transparan), border `15214a`, title
  `00e5ff`, text `dbe7ff`, icon `ff2bd6`, ring `2f6bff`. Pasang `<picture>`
  hanya bila versi tema terang diperlukan; default: satu versi gelap.
- Baris `> DATA STREAM // contribution snake` lalu snake dari GitHub Action
  Platane/snk (workflow di repo ini, jalan tiap 12 jam + manual, hasil ke cabang
  `output`), warna kustom: titik kosong `0a0f24`, level `2f6bff→00e5ff`, kepala
  ular `ff2bd6`.
- Tidak ada angka hard-coded; semua kartu menarik data nyata.

### 6.7 `05 // TIMELINE.LOG`

Daftar vertikal bergaya log (markdown + badge kecil tanggal):

- `2025-08 → 2026-02 · SURABAYA` Backend Developer · Performa Optima Group:
  aplikasi PWA otomasi laporan teknisi; Next.js, Python, PostgreSQL, TypeScript.
  (Periode mengikuti portofolio; status "sekarang" dikonfirmasi di bagian 9.)
- `2025-02 → 2025-08 · YOGYAKARTA` Frontend Developer (Volunteer) · Litera
  Sumbu Pakarti: sistem manajemen buku yayasan (peminjaman, donasi, inventaris);
  memimpin tim 3 developer; Laravel/PHP.
- `2025-02 → 2025-05` Dicoding Indonesia: 9 kelas selesai (dasar pemrograman
  sampai Back-End dan Web Intermediate).
- `<details><summary>ACCESS CERTIFICATES [09]</summary>` berisi 9 tautan
  `https://www.dicoding.com/certificates/<ID>`, urut tanggal terbit
  (sudah diverifikasi dari halaman sertifikat, semua atas nama Nikolaus Ray
  Nathan, berlaku 3 tahun):

  | ID | Kelas | Terbit |
  |---|---|---|
  | 72ZD5MK9VZYW | Memulai Dasar Pemrograman untuk Menjadi Pengembang Software | 2025-02-15 |
  | ERZRE720MXYV | Pengenalan ke Logika Pemrograman (Programming Logic 101) | 2025-02-15 |
  | 0LZ0RJ51KP65 | Belajar Dasar Git dengan GitHub | 2025-02-16 |
  | NVP75WJ1RXR0 | Belajar Dasar Pemrograman Web | 2025-02-24 |
  | ERZRE3KLQXYV | Belajar Dasar Pemrograman JavaScript | 2025-03-08 |
  | MEPJQ3G24X3V | Belajar Membuat Front-End Web untuk Pemula | 2025-03-21 |
  | ERZREJR62XYV | Belajar Fundamental Front-End Web Development | 2025-04-17 |
  | JLX19M1MNP72 | Belajar Back-End Pemula dengan JavaScript | 2025-05-16 |
  | 2VX3KQ6VJXYQ | Belajar Pengembangan Web Intermediate | 2025-05-19 |

  Catatan: daftar di mockup menyebut "React" dan "Dasar AI"; itu keliru dan
  diganti dengan daftar nyata di atas. Fakta `[04]` di seksi Identity ikut
  disesuaikan: "9 sertifikat Dicoding: Front-End, Back-End, Web Intermediate".

### 6.8 `06 // ESTABLISH CONNECTION`

Kalimat ajakan kolaborasi (Indonesia) lalu badge besar `for-the-badge`:
LINKEDIN (isi cyan), PORTFOLIO (outline), EMAIL (outline), dan opsional
BUY ME A COFFEE (magenta) hanya bila Nathan punya tautannya.

### 6.9 Footer `assets/footer.svg`

Lantai grid bergerak + teks glitch `END OF TRANSMISSION` dan baris kecil
`// thanks for visiting · stay curious · ship clean code`.

## 7. Metadata profil GitHub (di luar README)

Diisi lewat Settings → Public profile (atau API bila kredensial tersedia):

- Name: Nikolaus Ray Nathan
- Bio: `Full Stack Developer · Laravel · Next.js · PostgreSQL. Membangun sistem yang cepat, rapi, dan tahan banting.`
- Location: Surabaya, Indonesia
- Website: https://nathporto.netlify.app/
- Social: https://www.linkedin.com/in/nikolaus-ray-nathan/
- Avatar: tetap foto yang sekarang.

## 8. Struktur repo dan cara kerja

```
RayNathans/            (repo RayNathans/RayNathans, cabang main)
├─ README.md
├─ assets/             SVG hasil build (hero, h-01..h-06, skills, proj-*, footer)
├─ data/               skills.json, projects.json, certs.json, profile.json
├─ tools/              generator Python: build.py (template → assets/*.svg),
│                      embed font subset + avatar base64, tanpa dependensi npm
├─ fonts/              subset woff2 Orbitron, Share Tech Mono, Rajdhani (lisensi OFL)
├─ .github/workflows/snake.yml
└─ docs/superpowers/specs/  (dokumen ini)
```

- Generator dijalankan lokal (`python tools/build.py`), hasil SVG di-commit.
  Opsional: workflow yang menjalankan build saat `data/*` berubah.
- Commit dan PR **tanpa penanda atribusi apa pun** (aturan pribadi Nathan).
- `.superpowers/` masuk `.gitignore`.

## 9. Pertanyaan terbuka dan keputusan yang diambil

Nathan meminta semuanya dikerjakan sampai selesai tanpa putaran tanya jawab
lagi (2026-11-04). Keputusan di bawah adalah **asumsi pembangun**; semuanya
mudah diubah lewat `data/profile.json` dan dicatat di checklist serah-terima.

1. **Email publik**: badge EMAIL memakai `nikolausraynathan@gmail.com`
   (alamat yang sudah dipakai Nathan di konfigurasi git dan karenanya sudah
   tampil di commit publiknya). Ditandai di serah-terima agar bisa dihapus.
2. **Buy Me a Coffee / Saweria**: tidak ada tautan yang diketahui → badge
   **dihilangkan**.
3. **Repo sumber** proyek: tidak ada repo publik yang cocok di akun
   (hanya `testdemo`, `litera`, `present`) → kartu hanya menampilkan LIVE DEMO.
4. **Status pekerjaan**: ditulis **masih berjalan** (`2025-08 → NOW`), sesuai
   mockup yang disetujui dan alamat email kerja Performa Optima Group yang masih
   dipakai Nathan. Bila ternyata sudah selesai, ubah `profile.json`
   (`current_job: false`) lalu jalankan build; generator otomatis mengganti lima
   tempat terdampak (timeline, sel COMPANY → `STATUS: OPEN TO WORK`, baris
   terminal hero → `status: open for new missions [READY]`, `sekarang` di
   about.json, fakta `[01]`).
5. **Cara publikasi**: tidak ada `gh` dan tidak ada token. Semua dibangun dan
   di-commit lokal. Push dicoba ke `https://github.com/RayNathans/RayNathans.git`;
   bila repo belum ada, serah-terima berisi satu langkah untuk Nathan: buat repo
   publik kosong bernama `RayNathans`, lalu push diulang.
6. **Angka skill matrix**: memakai angka mockup.

Keputusan pembangun lain:

- **Metadata profil (bagian 7)** diisi Nathan sendiri lewat Settings; tidak ada
  token API yang diminta atau dipakai. Rencana diakhiri checklist serah-terima
  dan verifikasi dilakukan setelah ia mengisinya.
- **Layar sempit**: "pecah" berarti elemen tumpang-tindih, terpotong, atau teks
  tak terbaca pada lebar ≥ 768 px. Di bawah itu, tabel GitHub boleh scroll
  horizontal. Agar kartu proyek tetap utuh saat mengecil, seluruh kartu (ilustrasi,
  judul, deskripsi, chip) digambar di dalam satu `proj-*.svg`; markdown hanya
  menambah baris tautan LIVE/SOURCE di bawahnya. Seksi Identity dan Telemetry
  tetap dua kolom.

## 10. Yang diserahkan ke pembangun

- Cara mensubset dan meng-embed font (fontTools, atau subset manual) dan
  menjaga ukuran tiap SVG wajar.
- Detail keyframes (durasi glitch, kecepatan hujan, delay kedip jendela), selama
  nama tetap terbaca dan kesan "penuh" terjaga.
- Struktur template/generator dan format `data/*.json`.
- Pemilihan parameter persis github-readme-stats/streak/komarev dan fallback bila
  layanan pihak ketiga lambat (mis. `cache_seconds`).
- Urutan verifikasi: render tiap SVG di Chrome sebagai `<img>` (bukan inline)
  sebelum commit; cek README di GitHub pada tema gelap dan terang serta lebar
  mobile.
