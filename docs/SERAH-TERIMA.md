# Serah-terima: profil GitHub @RayNathans

Repo ini adalah isi repo profil `RayNathans/RayNathans`. README-nya dibangun dari
`data/*.json` oleh `tools/build.py`. Semua aset SVG sudah di-commit, jadi GitHub
langsung menampilkannya tanpa langkah build.

## 1. Publikasi (sekali)

1. Buka https://github.com/new, buat repo **publik** bernama persis `RayNathans`
   (nama sama dengan username). Jangan centang "Add a README".
2. Dari folder ini jalankan:

   ```bash
   git remote add origin https://github.com/RayNathans/RayNathans.git
   git push -u origin main
   ```

   Bila `origin` sudah ada, cukup `git push -u origin main`.
3. Buka https://github.com/RayNathans. Hero, skill matrix, kartu proyek, dan
   footer tampil seketika. Kartu stats/streak diambil dari layanan pihak ketiga
   dan bisa butuh beberapa detik.

## 2. Isi metadata profil (Settings → Public profile)

Buka https://github.com/settings/profile lalu salin:

| Kolom | Isi |
|---|---|
| Name | Nikolaus Ray Nathan |
| Bio | Full Stack Developer · Laravel · Next.js · PostgreSQL. Membangun sistem yang cepat, rapi, dan tahan banting. |
| Location | Surabaya, Indonesia |
| Website | https://nathporto.netlify.app/ |
| Social accounts | https://www.linkedin.com/in/nikolaus-ray-nathan/ |

Avatar tetap foto yang sekarang (dipakai juga di hologram hero).

## 3. Ular kontribusi (snake)

Gambar `github-snake.svg` dibuat oleh workflow `snake` dan disimpan di cabang
`output`. Sebelum workflow jalan pertama kali, kotak snake di README kosong.

1. Buka tab **Actions** di repo. Bila diminta, klik "I understand my workflows,
   go ahead and enable them".
2. Pilih workflow **snake** → **Run workflow**. Setelah ±1 menit cabang `output`
   terbentuk dan gambar muncul (cache GitHub bisa menunda beberapa menit).
3. Selanjutnya otomatis tiap 12 jam dan tiap push ke `main`.

## 3b. Statistik Telemetry (stats sendiri, tanpa layanan luar)

Panel GITHUB STATS, CONTRIBUTION STREAK, dan TOP LANGUAGES digambar dari
`data/stats.json`. File itu diisi `tools/fetch_stats.py` dari API publik GitHub
(followers, repo, stars, commit publik, PR, issue, byte per bahasa di repo milik
sendiri) dan halaman kontribusi publik (kalender 12 bulan untuk streak).

- Workflow **stats** menjalankannya tiap 12 jam dan meng-commit `data/stats.json`
  beserta aset yang berubah. Bisa juga dipicu manual dari tab Actions.
- Angka yang tampil adalah yang terlihat publik. Kontribusi di repo privat
  organisasi tidak dihitung kecuali Anda mengaktifkan "Include private
  contributions on my profile" di Settings → Public profile.
- Memperbarui lokal: `.venv/Scripts/python.exe tools/fetch_stats.py` lalu build.

## 4. Mengubah isi

| Ingin mengubah | Edit | Lalu |
|---|---|---|
| Angka skill, urutan, logo | `data/skills.json` | `python tools/build.py` |
| Proyek (judul, deskripsi, stack, link) | `data/projects.json` (ilustrasi di `tools/templates/proj-art-<id>.svg`) | build |
| Sertifikat (jumlahnya ikut berubah di strip, fakta, timeline, dropdown) | `data/certs.json` | build |
| Nama, motto, link, email | `data/profile.json` | build |
| Entri timeline selain pekerjaan sekarang | `data/timeline.json` | build |
| Kalimat ajakan di seksi 06 | `_CONNECT_TEXT` di `tools/build.py` | build |
| **Sudah tidak di Performa Optima Group** | `data/profile.json` → `"current_job": false` | build; yang berubah sekaligus: timeline, sel COMPANY → STATUS: OPEN TO WORK, sel ROLE → FULL_STACK_DEV, baris terminal hero, `sekarang` di about.json, fakta `[01]` dan `[02]` |

Cara build lokal (sekali siapkan lingkungan):

```bash
uv venv --python 3.11 .venv
uv pip install --python .venv/Scripts/python.exe "fonttools[woff]" brotli pillow pyyaml markdown
.venv/Scripts/python.exe -m unittest
.venv/Scripts/python.exe tools/build.py
git add -A && git commit -m "Perbarui data profil" && git push
```

Alternatif tanpa build lokal: edit `data/*.json` langsung di GitHub dan commit ke
`main`; workflow **build** akan menjalankan test, membangun ulang aset, dan
meng-commit hasilnya.

## 5. Catatan privasi

Tombol EMAIL memakai `nikolausraynathan@gmail.com` (alamat yang sudah dipakai di
konfigurasi git Anda). Untuk menyembunyikannya, kosongkan `links.email` di
`data/profile.json` lalu hapus blok `<a href="mailto:...">` di
`tools/templates/README.md.tpl`, atau ganti dengan alamat lain.

## 6. Layanan pihak ketiga yang dipakai

| Layanan | Untuk | Catatan |
|---|---|---|
| readme-typing-svg.demolab.com | baris terminal mengetik | tanpa akun |
| img.shields.io | badge logo teknologi di bawah skill matrix | tanpa akun |
| api.github.com + github.com/users/RayNathans/contributions | data Telemetry (lihat 3b) | tanpa akun; di Actions memakai token bawaan |
| Platane/snk (GitHub Action) | snake | token bawaan Actions |

Yang sengaja tidak dipakai lagi sejak tahap 2: github-readme-stats dan streak-stats
(instance publiknya sering 503 dan tampilannya tidak bisa disamakan dengan mockup)
serta penghitung profile views komarev (nilainya tidak bisa dibawa ke dalam SVG).

## 7. Font dan lisensi

Orbitron dan Share Tech Mono diunduh dari repo resmi Google Fonts, disubset ke
ASCII + beberapa simbol, dan di-embed ke SVG sebagai base64. Keduanya berlisensi
SIL Open Font License; salinan lisensi ada di `fonts/OFL-*.txt`. Untuk
memperbarui font: `python tools/fetch_fonts.py`.

## 8. Dokumen terkait

- Desain: `docs/superpowers/specs/2026-11-04-github-profile-cyberpunk-design.md`
- Rencana implementasi: `docs/superpowers/plans/2026-11-04-github-profile-cyberpunk.md`
- Mockup yang disetujui: `.superpowers/brainstorm/3686-1793773675/content/concept-cyberpunk-v2.html` (lokal, tidak di-commit)
