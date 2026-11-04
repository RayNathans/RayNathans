# Profil GitHub Cyberpunk · Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Repo `RayNathans/RayNathans` berisi README profil bergaya cyberpunk (Mockup B rev 2) dengan semua aset SVG animasi dihasilkan dari data JSON oleh satu generator Python.

**Architecture:** `tools/build.py` membaca `data/*.json`, merender template SVG di `tools/templates/` lewat `tools/svgkit.py` (embed font subset + avatar sebagai data URI, gaya bersama), menulis `assets/*.svg` dan `README.md` dari `tools/templates/README.md.tpl`. Semua teks yang bergantung status kerja berasal dari satu flag `current_job` sehingga lima tempat terdampak berubah bersamaan. Hasil build di-commit; GitHub Action hanya untuk snake.

**Tech Stack:** Python 3.11 (stdlib + `fonttools[woff]`/`brotli` untuk subset font, Pillow untuk avatar), `unittest`, GitHub Actions (Platane/snk), layanan pihak ketiga: readme-typing-svg, github-readme-stats, streak-stats, shields.io, komarev.

**Spec:** `docs/superpowers/specs/2026-11-04-github-profile-cyberpunk-design.md`

## Global Constraints

- Palet persis: bg `#03040d`, panel `#0a0f24`, line `#15214a`, ink `#dbe7ff`, muted `#7f93c4`, c1 `#00e5ff`, c2 `#2f6bff`, c3 `#ff2bd6`, c4 `#7c3aed`, ok `#22c55e`.
- SVG tidak boleh memuat sumber eksternal: tidak ada `http://`/`https://` di dalam `assets/*.svg`; font dan gambar di-embed `data:`.
- Tiap `assets/*.svg` < 400 KB.
- Tidak ada `<script>` di SVG; animasi hanya CSS `@keyframes`/SMIL; sertakan `@media (prefers-reduced-motion: reduce)` yang mematikan animasi.
- Font: Orbitron (judul), Share Tech Mono (HUD/terminal), fallback `sans-serif`/`monospace`. Lisensi OFL disertakan di `fonts/`.
- Teks isi Bahasa Indonesia; judul seksi campur: `01 // IDENTITY`, `02 // SKILL MATRIX`, `03 // MISSION LOGS`, `04 // TELEMETRY`, `05 // TIMELINE.LOG`, `06 // ESTABLISH CONNECTION`.
- Hero hanya menampilkan `SYS.ONLINE`, tanpa LOC/UPTIME. Tidak ada tautan `#` di README; tidak ada angka stats hard-coded.
- Commit tanpa penanda atribusi apa pun (tanpa Co-Authored-By, tanpa nama model). `.superpowers/` di `.gitignore`.
- Semua perintah dijalankan dari root repo `C:\Users\NATHAN-NB\source\RayNathans-profile`.

## Review Focus

1. Glyph di luar subset font (mis. `✔`, `→`, `·`, `▸`) di dalam SVG jatuh ke font fallback dan terlihat beda; test Task 1 memastikan subset memuat semua karakter yang dipakai template.
2. Teks nama panjang `NIKOLAUS RAY NATHAN` meluap keluar hero bila lebar font berbeda; Task 2 memverifikasi lebar via screenshot `<img>` dan `textLength` tidak dipakai (agar tidak gepeng).
3. `current_job=false` harus mengubah kelima tempat; test Task 6 memeriksa semuanya sekaligus.
4. Karakter `&`, `<`, `"` dari JSON (mis. "PWA & arsitektur") merusak XML; `svgkit.esc` dipakai di semua interpolasi dan test Task 1 memparse hasil.
5. Snake belum tersedia sebelum Action pertama jalan; Task 7 menjalankan workflow via `workflow_dispatch` dan serah-terima menjelaskan jeda.

---

### Task 1: Data, font subset, dan `svgkit`

**Files:**
- Create: `data/profile.json`, `data/skills.json`, `data/projects.json`, `data/certs.json`
- Create: `fonts/Orbitron-subset.woff2`, `fonts/ShareTechMono-subset.woff2`, `fonts/OFL-Orbitron.txt`, `fonts/OFL-ShareTechMono.txt`
- Create: `tools/svgkit.py`, `tools/fetch_fonts.py`, `tools/__init__.py`
- Create: `assets/avatar.jpg` (240×240, hasil resize)
- Test: `tests/test_svgkit.py`

**Interfaces:**
- Produces `svgkit.PALETTE: dict[str,str]` dengan kunci `bg,panel,line,ink,muted,c1,c2,c3,c4,ok`.
- Produces `svgkit.esc(s: str) -> str` (escape `& < > "`).
- Produces `svgkit.font_face_css() -> str` (dua `@font-face` data URI woff2, family `Orbitron` dan `Share Tech Mono`).
- Produces `svgkit.avatar_data_uri() -> str` (`data:image/jpeg;base64,...` dari `assets/avatar.jpg`).
- Produces `svgkit.base_style() -> str`: `font_face_css()` + variabel warna sebagai kelas (`.c1{fill:#00e5ff}` dst.) + `@media (prefers-reduced-motion: reduce){*{animation:none!important}}`.
- Produces `svgkit.render(template_name: str, **vars) -> str`: baca `tools/templates/<name>`, ganti `{{key}}` dengan nilai (sudah di-escape oleh pemanggil), error bila ada `{{` tersisa.
- Produces `svgkit.load_data() -> dict` dengan kunci `profile, skills, projects, certs`.
- Produces `svgkit.ROOT: Path` (root repo).

Isi data (nilai dari spec):
- `profile.json`: `name "Nikolaus Ray Nathan"`, `handle "RayNathans"`, `role "Full Stack Developer"`, `current_job true`, `job {"title":"Backend Developer","company":"Performa Optima Group","city":"SURABAYA","start":"2025-08","end":"2026-02"}`, `stack ["Laravel","Next.js","TypeScript","PostgreSQL"]`, `learning "PWA & arsitektur backend yang rapi"`, `motto "Kode bersih hari ini, tidur nyenyak besok"`, `city "Surabaya, Indonesia"`, `links {"linkedin":"https://www.linkedin.com/in/nikolaus-ray-nathan/","portfolio":"https://nathporto.netlify.app/","email":"nikolausraynathan@gmail.com"}`, `bio` (teks bagian 7 spec).
- `skills.json`: 12 pasangan `{"name","pct","badge":{"logo","color"}}` dengan angka mockup (Laravel 87, Next.js 90, TypeScript 85, React 95, PHP 98, PostgreSQL 85, MySQL 90, Tailwind 95, Python 70, Node.js 85, Git 92, Supabase 75); `logo` = slug simple-icons (`laravel, nextdotjs, typescript, react, php, postgresql, mysql, tailwindcss, python, nodedotjs, git, supabase`).
- `projects.json`: tiga entri `{"id","title","status","desc","stack":[...],"live","art"}` dengan `id` `fruch|story|pos`, `art` nama template parsial `proj-art-<id>.svg`, nilai dari tabel spec 6.5.
- `certs.json`: sembilan entri `{"id","title","date"}` dari tabel spec 6.7, urut tanggal.

- [ ] **Step 1: Pasang dependensi dan ambil font**

Run: `python -m pip install "fonttools[woff]" brotli`
Buat `tools/fetch_fonts.py` yang mengunduh dari repo resmi Google Fonts (raw.githubusercontent.com/google/fonts/main/ofl/orbitron/Orbitron[wght].ttf, .../ofl/sharetechmono/ShareTechMono-Regular.ttf, dan OFL.txt masing-masing) ke `scratch/fonts/` (di-gitignore), lalu `pyftsubset` ke `fonts/*-subset.woff2` dengan `--unicodes="U+0020-007E,U+00B7,U+2192,U+2714,U+25B8,U+25CF,U+2022"` dan `--flavor=woff2 --layout-features='*'`; untuk Orbitron tambahkan `--instance` tidak dipakai (biarkan variable, sumbu wght dipakai lewat `font-weight`).
Run: `python tools/fetch_fonts.py`
Expected: dua file woff2 di `fonts/`, masing-masing < 40 KB.

- [ ] **Step 2: Siapkan avatar**

Salin `C:\Users\NATHAN-NB\AppData\Local\Temp\claude\3525012098466cd2\407953e4-643e-4a01-978f-a0ea4c96e2d7\scratchpad\avatar.png` (unduhan avatar GitHub sebelumnya; bila hilang, unduh ulang dari `https://avatars.githubusercontent.com/u/160562538?v=4`), resize 240×240 dengan Pillow, simpan JPEG kualitas 82 ke `assets/avatar.jpg`.
Expected: file < 25 KB.

- [ ] **Step 3: Tulis test**

```python
# tests/test_svgkit.py
class SvgkitTests(unittest.TestCase):
    def test_palette_values(self): assert svgkit.PALETTE["c1"] == "#00e5ff" and svgkit.PALETTE["bg"] == "#03040d"
    def test_esc(self): assert svgkit.esc('PWA & <b> "x"') == 'PWA &amp; &lt;b&gt; &quot;x&quot;'
    def test_font_face_has_two_data_uris(self): css = svgkit.font_face_css(); assert css.count("data:font/woff2;base64,") == 2 and "Orbitron" in css and "Share Tech Mono" in css
    def test_avatar_uri(self): assert svgkit.avatar_data_uri().startswith("data:image/jpeg;base64,")
    def test_render_rejects_missing_var(self): with self.assertRaises(KeyError): svgkit.render("_probe.svg", a="1")  # template berisi {{a}} dan {{b}}
    def test_subset_covers_template_glyphs(self): semua karakter non-ASCII yang muncul di tools/templates/*.svg ada di cmap fonts/ShareTechMono-subset.woff2 (fontTools TTFont)
    def test_load_data_keys(self): d = svgkit.load_data(); assert set(d) == {"profile","skills","projects","certs"} and len(d["skills"]) == 12 and len(d["certs"]) == 9 and len(d["projects"]) == 3
```

- [ ] **Step 4: Jalankan test, pastikan gagal**

Run: `python -m unittest tests.test_svgkit -v`
Expected: FAIL/ERROR (`svgkit` belum ada).

- [ ] **Step 5: Implementasi `tools/svgkit.py` dan empat file data**

`render` memakai `str.replace` per kunci lalu `re.search(r"\{\{\w+\}\}")` → `KeyError`. `base_style()` menyusun CSS: font-face, kelas warna, `.mono{font-family:'Share Tech Mono',monospace}`, `.orb{font-family:Orbitron,sans-serif;font-weight:900}`, dan blok reduced-motion.

- [ ] **Step 6: Jalankan test, pastikan lulus**

Run: `python -m unittest tests.test_svgkit -v`
Expected: 7 PASS.

- [ ] **Step 7: Commit**

```bash
git add data fonts tools tests assets/avatar.jpg .gitignore
git commit -m "Tambah data profil, font subset, dan svgkit"
```

---

### Task 2: Hero SVG

**Files:**
- Create: `tools/templates/hero.svg`, `tools/build.py` (kerangka: `build_hero()`, `main()`)
- Create: `assets/hero.svg` (hasil build)
- Test: `tests/test_build.py` (kelas `HeroTests`)

**Interfaces:**
- Consumes `svgkit.*` dari Task 1.
- Produces `build.build_hero(data: dict) -> str` dan `build.write(name: str, svg: str)` yang menulis `assets/<name>`; `build.main()` memanggil semua `build_*` dan `build_readme` (ditambah di task berikutnya).
- Produces `build.job_strings(profile: dict) -> dict` dengan kunci `timeline_when, strip_label, strip_value, term_status, about_now, fact01`:
  - `current_job=true`: `"2025-08 → NOW · SURABAYA"`, `"COMPANY"`, `"PERFORMA OPTIMA GROUP"`, `"status: building PWA for field technicians [RUNNING]"`, `"Backend Dev @ Performa Optima Group"`, `"Backend Developer di Performa Optima Group (Ags 2025 – sekarang)"`.
  - `current_job=false`: `"2025-08 → 2026-02 · SURABAYA"`, `"STATUS"`, `"OPEN TO WORK"`, `"status: open for new missions [READY]"`, `"Open to work · Full Stack"`, `"Backend Developer di Performa Optima Group (Ags 2025 – Feb 2026)"`.

Isi `hero.svg` (viewBox `0 0 1200 400`, `width="100%"`): latar `bg`; skyline jauh (17 rect dari mockup baris 304–307) dan gedung dekat bergradasi; ≥ 30 jendela `class="win"` kedip (`@keyframes blink` 2.6 s, `animation-delay` negatif bervariasi); papan neon `LARAVEL` (c3) dan `NEXT.JS` (c1) dengan `@keyframes flicker`; label `SBY-07 // SECTOR 2026`; lantai grid: `<pattern>` garis c2 opacity .35 pada area y 300–400 dengan `animateTransform translate` 0→40 px loop 1.6 s dan garis horizon memudar; hujan: 40 `<line>` c1 opacity .25–.5 panjang 14–30 px, `@keyframes rain` jatuh 400 px 0.9–1.6 s dengan delay berbeda; kiri: `● SYS.ONLINE` (titik ok berdenyut), judul Orbitron 54 px dua baris `NIKOLAUS` / `RAY NATHAN` (kata kedua c1) dengan glitch: dua salinan teks warna c1/c3 digeser ±3 px dan `clip-path` rect yang berubah lewat `@keyframes glitch` 3.2 s (aktif hanya 12% durasi); subjudul `FULL STACK DEVELOPER` Share Tech Mono 16 px letter-spacing 6; kotak terminal 420×78 panel dengan border line: baris `nathan@github:~$ whoami` + kursor `_` kedip, lalu dua baris output: `▸ loading stack: laravel, next.js, typescript, postgresql [OK]` dan `▸ {{term_status}}` (muncul via `@keyframes fadein` berurutan); kanan: hologram pada pusat (960,185): tiga cincin (r 110/92/74, stroke c1/c3/c2, dasharray, `animateTransform rotate` 14 s/10 s/18 s arah selang-seling), `<clipPath>` heksagon r 70 berisi `<image href="{{avatar}}">` 160×160 dengan `<rect>` overlay c1 opacity .18, garis scan `<rect>` tinggi 4 c1 opacity .6 naik-turun 2.4 s, label `ID: RAY_NATHANS · LVL 24` Share Tech Mono 11 px di y 300; drone 54×40 di (1090,40) `@keyframes hover` ±6 px.

- [ ] **Step 1: Tulis test**

```python
class HeroTests(unittest.TestCase):
    def setUp(self): self.svg = build.build_hero(svgkit.load_data())
    def test_is_xml_and_no_external(self): ET.fromstring(self.svg); assert "http" not in self.svg.replace("http://www.w3.org","")
    def test_texts(self): for s in ["SYS.ONLINE","NIKOLAUS","RAY NATHAN","FULL STACK DEVELOPER","LARAVEL","NEXT.JS","SBY-07 // SECTOR 2026","ID: RAY_NATHANS","[OK]","building PWA for field technicians [RUNNING]"]: assert s in self.svg
    def test_no_loc_uptime(self): assert "LOC:" not in self.svg and "UPTIME" not in self.svg
    def test_embeds(self): assert self.svg.count("data:font/woff2;base64,") == 2 and "data:image/jpeg;base64," in self.svg and "<script" not in self.svg
    def test_size(self): assert len(self.svg.encode()) < 400_000
    def test_job_strings_toggle(self): p = dict(load_data()["profile"], current_job=False); js = build.job_strings(p); assert js["strip_value"] == "OPEN TO WORK" and js["timeline_when"] == "2025-08 → 2026-02 · SURABAYA" and "[READY]" in js["term_status"]
```

- [ ] **Step 2: Jalankan test, pastikan gagal**

Run: `python -m unittest tests.test_build.HeroTests -v`
Expected: ERROR (`build` belum ada).

- [ ] **Step 3: Implementasi `tools/templates/hero.svg`, `build.job_strings`, `build.build_hero`, `build.write`, `build.main`**

Variabel template: `{{style}}`, `{{avatar}}`, `{{term_status}}`, `{{rain}}` (40 `<line>` dihasilkan Python dengan `random.Random(7)` agar deterministik), `{{windows}}` (rect jendela dihasilkan dari daftar koordinat mockup).

- [ ] **Step 4: Jalankan test, pastikan lulus, lalu build**

Run: `python -m unittest tests.test_build.HeroTests -v && python tools/build.py`
Expected: PASS; `assets/hero.svg` tertulis.

- [ ] **Step 5: Verifikasi visual sebagai `<img>`**

Buat `scratch/preview.html` (di-gitignore) yang memuat `<img src="../assets/hero.svg" width="900">` di latar `#0d1117` dan `#ffffff`; buka di Chrome, screenshot. Periksa: nama tidak terpotong, hologram terlihat, hujan/grid/kedip bergerak (dua screenshot berselang 1 s berbeda), font Orbitron aktif (bukan fallback).
Expected: sesuai; bila nama terpotong, kecilkan `font-size` sampai pas (minimum 44).

- [ ] **Step 6: Commit**

```bash
git add tools/templates/hero.svg tools/build.py tests/test_build.py assets/hero.svg
git commit -m "Bangun hero SVG kota neon dengan hologram avatar"
```

---

### Task 3: Judul seksi dan footer

**Files:**
- Create: `tools/templates/header.svg`, `tools/templates/footer.svg`
- Create: `assets/h-01.svg` … `assets/h-06.svg`, `assets/footer.svg`
- Modify: `tools/build.py` (tambah `build_headers`, `build_footer`)
- Test: `tests/test_build.py` (kelas `HeaderFooterTests`)

**Interfaces:**
- Produces `build.SECTIONS: list[tuple[str,str]]` = `[("01","IDENTITY"),("02","SKILL MATRIX"),("03","MISSION LOGS"),("04","TELEMETRY"),("05","TIMELINE.LOG"),("06","ESTABLISH CONNECTION")]`.
- Produces `build.build_header(idx: str, title: str) -> str` (viewBox `0 0 1200 64`): teks `{{idx}} //` c3 Share Tech Mono 20 px + judul Orbitron 26 px ink, garis HUD c2 di bawah dengan segmen terang c1 yang **menyapu** kiri→kanan (`@keyframes sweep` 4 s), sudut siku kecil c1 di kiri.
- Produces `build.build_footer() -> str` (viewBox `0 0 1200 180`): grid bergerak seperti hero, teks glitch `END OF TRANSMISSION` Orbitron 34 px, baris `// thanks for visiting · stay curious · ship clean code` Share Tech Mono 13 px muted.

- [ ] **Step 1: Tulis test**

```python
class HeaderFooterTests(unittest.TestCase):
    def test_header_content(self): s = build.build_header("02","SKILL MATRIX"); ET.fromstring(s); assert "02 //" in s and "SKILL MATRIX" in s and "sweep" in s
    def test_six_sections(self): assert [t for _,t in build.SECTIONS] == ["IDENTITY","SKILL MATRIX","MISSION LOGS","TELEMETRY","TIMELINE.LOG","ESTABLISH CONNECTION"]
    def test_footer(self): s = build.build_footer(); ET.fromstring(s); assert "END OF TRANSMISSION" in s and "ship clean code" in s and "http" not in s.replace("http://www.w3.org","")
```

- [ ] **Step 2: Jalankan test, pastikan gagal** · Run: `python -m unittest tests.test_build.HeaderFooterTests -v` · Expected: ERROR/FAIL.

- [ ] **Step 3: Implementasi template dan fungsi; daftarkan di `main()`** (menulis `h-<idx>.svg` untuk tiap SECTIONS dan `footer.svg`).

- [ ] **Step 4: Jalankan test, pastikan lulus, build, cek visual** · Run: `python -m unittest tests.test_build.HeaderFooterTests -v && python tools/build.py` · Tambahkan `h-01.svg` dan `footer.svg` ke `scratch/preview.html`, screenshot; sapuan garis terlihat bergerak.

- [ ] **Step 5: Commit**

```bash
git add tools assets/h-0*.svg assets/footer.svg tests
git commit -m "Tambah judul seksi HUD dan footer"
```

---

### Task 4: Skill matrix SVG

**Files:**
- Create: `tools/templates/skills.svg`
- Create: `assets/skills.svg`
- Modify: `tools/build.py` (tambah `build_skills`)
- Test: `tests/test_build.py` (kelas `SkillsTests`)

**Interfaces:**
- Produces `build.build_skills(skills: list[dict]) -> str` (viewBox `0 0 1200 {{height}}`, dua kolom × 6 baris, tinggi baris 52): tiap baris: nama Share Tech Mono 15 px ink (x kolom), 20 segmen `<rect>` 18×12 jarak 4 px, segmen aktif `round(pct/5)` kelas `on` (fill c1, segmen ke-17+ fill c3) dengan `@keyframes light` 0.35 s `animation-delay = (baris*60 + seg*40) ms` lalu `@keyframes pulse` tak hingga; segmen mati fill panel stroke line; persentase `{{pct}}%` c1 di kanan. Judul kecil `SELF-ASSESSMENT · EDIT data/skills.json` muted 11 px di pojok kanan atas.

- [ ] **Step 1: Tulis test**

```python
class SkillsTests(unittest.TestCase):
    def test_rows_and_segments(self): s = build.build_skills(load_data()["skills"]); ET.fromstring(s); assert s.count('class="seg on"') == sum(round(x["pct"]/5) for x in load_data()["skills"]); assert "PHP" in s and "98%" in s and "Supabase" in s
```

- [ ] **Step 2: Gagal dulu** · Run: `python -m unittest tests.test_build.SkillsTests -v` · Expected: ERROR.
- [ ] **Step 3: Implementasi template + `build_skills`; daftarkan di `main()`.**
- [ ] **Step 4: Lulus, build, cek visual di preview** · segmen menyala berurutan saat reload.
- [ ] **Step 5: Commit** · `git add tools assets/skills.svg tests && git commit -m "Tambah skill matrix bersegmen"`

---

### Task 5: Kartu proyek SVG

**Files:**
- Create: `tools/templates/project.svg`, `tools/templates/proj-art-fruch.svg`, `tools/templates/proj-art-story.svg`, `tools/templates/proj-art-pos.svg`
- Create: `assets/proj-fruch.svg`, `assets/proj-story.svg`, `assets/proj-pos.svg`
- Modify: `tools/build.py` (tambah `build_project`, `wrap_text`)
- Test: `tests/test_build.py` (kelas `ProjectTests`)

**Interfaces:**
- Produces `build.wrap_text(s: str, max_chars: int) -> list[str]` (pemenggalan kata sederhana).
- Produces `build.build_project(p: dict) -> str` (viewBox `0 0 400 300`): bingkai HUD panel + border line, sudut c1; area ilustrasi y 0–150 berisi parsial `proj-art-<id>.svg` (ilustrasi dari mockup baris 437–457, dengan `pulse-line` dan titik berkedip); label status `{{status}}` kanan atas (ok bila `DEPLOYED`, c3 bila `IN PRODUCTION`) berkedip pelan; judul Orbitron 15 px ink; deskripsi Share Tech Mono 12 px muted, maksimal 3 baris via `wrap_text(desc, 46)`; chip stack: kotak kecil border c2 teks 10 px; baris bawah `> LIVE DEMO` c1.

- [ ] **Step 1: Tulis test**

```python
class ProjectTests(unittest.TestCase):
    def test_three_cards(self):
        for p in load_data()["projects"]:
            s = build.build_project(p); ET.fromstring(s)
            assert p["title"] in s and p["status"] in s and all(t in s for t in p["stack"]) and "http" not in s.replace("http://www.w3.org","")
    def test_wrap(self): assert build.wrap_text("Deteksi kematangan & manfaat buah berbasis AI. Antarmuka minimalis dan aksesibel.", 46) == ["Deteksi kematangan & manfaat buah berbasis AI.", "Antarmuka minimalis dan aksesibel."]
```

- [ ] **Step 2: Gagal dulu** · Run: `python -m unittest tests.test_build.ProjectTests -v`
- [ ] **Step 3: Implementasi template, tiga parsial seni, `wrap_text`, `build_project`; `main()` menulis `proj-<id>.svg`.**
- [ ] **Step 4: Lulus, build, cek visual tiga kartu berdampingan lebar 290 px masing-masing di preview.**
- [ ] **Step 5: Commit** · `git add tools assets/proj-*.svg tests && git commit -m "Tambah kartu mission logs"`

---

### Task 6: README generator

**Files:**
- Create: `tools/templates/README.md.tpl`
- Create: `README.md`
- Modify: `tools/build.py` (tambah `build_readme`, `badge`, `stats_urls`)
- Test: `tests/test_build.py` (kelas `ReadmeTests`)

**Interfaces:**
- Produces `build.badge(label: str, value: str, color: str, logo: str|None=None, logo_color: str="white") -> str` → URL `https://img.shields.io/badge/<label>-<value>-<color>?style=for-the-badge&labelColor=0a0f24[&logo=..&logoColor=..]` dengan escape shields (`-`→`--`, `_`→`__`, spasi→`%20`).
- Produces `build.build_readme(data: dict) -> str`.

Isi README (urut, semua gambar lewat path relatif `assets/...` kecuali layanan):
1. `<p align="center"><img src="assets/hero.svg" width="100%" alt="Nikolaus Ray Nathan · Full Stack Developer"></p>`
2. Typing: `https://readme-typing-svg.demolab.com?font=Share+Tech+Mono&size=18&duration=2600&pause=800&color=00E5FF&background=00000000&center=true&vCenter=true&width=700&height=40&lines=nathan%40github%3A~%24+whoami;nathan%40github%3A~%24+cat+about.json;nathan%40github%3A~%24+.%2Fdeploy+--prod;nathan%40github%3A~%24+git+push+origin+main`
3. Status strip: `<p align="center">` empat badge: `badge("ROLE","BACKEND_DEV","00e5ff")`, `badge(strip_label, strip_value, "2f6bff")`, `badge("CERTS","09 · DICODING","ff2bd6")`, dan komarev `https://komarev.com/ghpvc/?username=RayNathans&style=for-the-badge&color=00e5ff&label=PROFILE+VIEWS`.
4. `h-01.svg`; tabel 2 kolom (`<td width="60%" valign="top">` blok kode ```jsonc about.json persis spec 6.3 dengan `sekarang = about_now`; `<td width="40%">` lima fakta `[01]`…`[05]`, fakta `[01] = fact01`, `[04] = "9 sertifikat Dicoding: Front-End, Back-End, Web Intermediate"`). Blok kode di dalam `<td>` diawali/diakhiri baris kosong.
5. `h-02.svg`; `<img src="assets/skills.svg" width="100%">`; baris badge logo 12 skill (`badge("", name, "0a0f24", logo, color)` → shields menerima label kosong dengan format `badge/<value>-<color>`).
6. `h-03.svg`; tabel 3 kolom, tiap sel `<a href="{{live}}"><img src="assets/proj-<id>.svg" width="100%"></a>` lalu baris `<p align="center"><a href="{{live}}">▸ LIVE DEMO</a></p>`.
7. `h-04.svg`; tabel 2 kolom: stats `https://github-readme-stats.vercel.app/api?username=RayNathans&show_icons=true&hide_border=false&bg_color=03040d&border_color=15214a&title_color=00e5ff&text_color=dbe7ff&icon_color=ff2bd6&ring_color=2f6bff&rank_icon=percentile&include_all_commits=true` dan streak `https://streak-stats.demolab.com?user=RayNathans&background=03040d&border=15214a&stroke=15214a&ring=2f6bff&fire=ff2bd6&currStreakNum=00e5ff&sideNums=dbe7ff&currStreakLabel=00e5ff&sideLabels=7f93c4&dates=7f93c4`; di bawahnya top-langs `.../api/top-langs/?username=RayNathans&layout=compact&langs_count=6&bg_color=03040d&border_color=15214a&title_color=00e5ff&text_color=dbe7ff`; baris mono `> DATA STREAM // contribution snake` lalu `<img src="https://raw.githubusercontent.com/RayNathans/RayNathans/output/github-snake.svg" width="100%">`.
8. `h-05.svg`; tiga entri timeline sebagai daftar: `**\`{{timeline_when}}\`** Backend Developer · Performa Optima Group` + deskripsi; entri Litera `2025-02 → 2025-08 · YOGYAKARTA`; entri Dicoding `2025-02 → 2025-05`; lalu `<details><summary><b>ACCESS CERTIFICATES [09]</b></summary>` daftar 9 tautan `- [{{title}}](https://www.dicoding.com/certificates/{{id}}) · {{date}}` `</details>`.
9. `h-06.svg`; kalimat spec 6.8; badge `LINKEDIN` (`0a66c2`, logo linkedin) → links.linkedin, `PORTFOLIO` (`00e5ff`, logo netlify) → links.portfolio, `EMAIL` (`ff2bd6`, logo gmail) → `mailto:`.
10. `<img src="assets/footer.svg" width="100%">`.
Semua gambar punya `alt`.

- [ ] **Step 1: Tulis test**

```python
class ReadmeTests(unittest.TestCase):
    def setUp(self): self.d = load_data(); self.md = build.build_readme(self.d)
    def test_badge_escape(self): assert build.badge("ROLE","BACKEND_DEV","00e5ff") == "https://img.shields.io/badge/ROLE-BACKEND__DEV-00e5ff?style=for-the-badge&labelColor=0a0f24"
    def test_sections_and_assets(self): for a in ["assets/hero.svg","assets/h-01.svg","assets/h-06.svg","assets/skills.svg","assets/proj-fruch.svg","assets/proj-story.svg","assets/proj-pos.svg","assets/footer.svg","readme-typing-svg.demolab.com","github-readme-stats.vercel.app/api?username=RayNathans","streak-stats.demolab.com?user=RayNathans","output/github-snake.svg","komarev.com/ghpvc/?username=RayNathans"]: assert a in self.md
    def test_links(self): assert 'href="#"' not in self.md and "](#)" not in self.md; for u in ["https://dicoding-milestone-fruch.vercel.app/","https://nathdicodingstory.netlify.app/","https://sipolubogo.cartera.my.id/","https://www.linkedin.com/in/nikolaus-ray-nathan/","https://nathporto.netlify.app/","mailto:nikolausraynathan@gmail.com"]: assert u in self.md
    def test_certs(self): assert self.md.count("https://www.dicoding.com/certificates/") == 9 and "Belajar Pengembangan Web Intermediate" in self.md and "React" not in self.md.split("ACCESS CERTIFICATES")[1].split("</details>")[0]
    def test_no_loc_uptime_no_coffee(self): assert "UPTIME" not in self.md and "COFFEE" not in self.md.upper()
    def test_current_job_toggle_changes_five_places(self):
        d = dict(self.d, profile=dict(self.d["profile"], current_job=False)); md = build.build_readme(d)
        assert "STATUS-OPEN%20TO%20WORK" in md and "2025-08 → 2026-02 · SURABAYA" in md and '"Open to work · Full Stack"' in md and "(Ags 2025 – Feb 2026)" in md and "PERFORMA%20OPTIMA%20GROUP" not in md
        hero = build.build_hero(d); assert "[READY]" in hero and "[RUNNING]" not in hero
```

- [ ] **Step 2: Gagal dulu** · Run: `python -m unittest tests.test_build.ReadmeTests -v`
- [ ] **Step 3: Implementasi `README.md.tpl`, `badge`, `build_readme`; `main()` menulis `README.md`.**
- [ ] **Step 4: Lulus; jalankan seluruh test dan build** · Run: `python -m unittest -v && python tools/build.py` · Expected: semua PASS, `README.md` tertulis.
- [ ] **Step 5: Pratinjau README** · Render `README.md` ke HTML dengan `python -m pip install markdown` + `markdown.markdown(md, extensions=["fenced_code","tables"])` ke `scratch/readme-preview.html` dengan CSS latar `#0d1117` lebar 900 px; buka di Chrome; screenshot tiap seksi. Periksa: tabel 60/40 dan 3 kolom tersusun, blok kode terhighlight (minimal terlihat sebagai kode), details terbuka-tutup, tidak ada gambar rusak lokal (gambar layanan boleh gagal offline).
- [ ] **Step 6: Commit** · `git add tools README.md tests && git commit -m "Hasilkan README profil dari data"`

---

### Task 7: Snake workflow, serah-terima, dan publikasi

**Files:**
- Create: `.github/workflows/snake.yml`, `.github/workflows/build.yml`
- Create: `docs/SERAH-TERIMA.md`
- Modify: `.gitignore` (tambah `scratch/`, `__pycache__/`)
- Test: `tests/test_repo.py`

**Interfaces:** tidak ada kode baru.

`snake.yml`: trigger `schedule: "0 */12 * * *"`, `workflow_dispatch`, `push: branches: [main]`; job `permissions: contents: write`; steps `actions/checkout@v4`, `Platane/snk@v3` dengan `github_user_name: RayNathans` dan `outputs: dist/github-snake.svg?palette=github-dark&color_dots=0a0f24,1b2a6b,2f6bff,00b8d4,00e5ff&color_snake=ff2bd6`, lalu `crazy-max/ghaction-github-pages@v4` `target_branch: output`, `build_dir: dist`, env `GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}`.
`build.yml`: pada `push` ke `main` yang mengubah `data/**` atau `tools/**`: setup Python 3.11, `pip install "fonttools[woff]" brotli pillow`, `python -m unittest`, `python tools/build.py`, commit otomatis bila `assets/`/`README.md` berubah (pesan `Build ulang aset`, tanpa penanda lain).
`SERAH-TERIMA.md`: langkah Nathan: (1) buat repo publik `RayNathans` lalu perintah push; (2) isi Settings → Public profile dengan teks bagian 7 spec (siap salin); (3) tunggu/menjalankan workflow `snake` sekali lewat tab Actions; (4) cara mengubah data (`data/*.json` → `python tools/build.py` → commit) termasuk `current_job`; (5) catatan email publik dan cara menghapusnya; (6) sumber font dan lisensi OFL.

- [ ] **Step 1: Tulis test**

```python
class RepoTests(unittest.TestCase):
    def test_assets_match_build(self): jalankan build ke direktori sementara (build.main(out=tmp)) dan bandingkan byte tiap file dengan assets/ dan README.md → identik (hasil build sudah di-commit)
    def test_svgs_small_and_offline(self): untuk tiap assets/*.svg: ukuran < 400_000, tidak ada "https://" / "http://" selain namespace w3.org, mengandung "prefers-reduced-motion"
    def test_workflows_valid_yaml(self): yaml stdlib tidak ada → pakai pemeriksaan `python -c "import json"`? Tidak: pasang `pyyaml` hanya di test, `yaml.safe_load` kedua workflow; snake memiliki `workflow_dispatch` dan `RayNathans`
    def test_no_attribution_markers_in_history(self): `git log --format=%B` tidak memuat "Co-Authored-By" maupun "Generated with"
```

- [ ] **Step 2: Gagal dulu** · Run: `python -m unittest tests.test_repo -v`
- [ ] **Step 3: Tambah `out` opsional ke `build.main(out: Path = svgkit.ROOT)`, tulis dua workflow, `SERAH-TERIMA.md`, perbarui `.gitignore`.**
- [ ] **Step 4: Semua test lulus** · Run: `python -m unittest -v` · Expected: PASS semua.
- [ ] **Step 5: Verifikasi akhir di Chrome** · buka `scratch/readme-preview.html` ulang, screenshot penuh atas-bawah; pastikan tidak ada teks meluap; cek `README.md` di tema terang (latar `#ffffff`): hero/footer/kartu tetap gelap utuh, badge terbaca.
- [ ] **Step 6: Commit** · `git add -A && git commit -m "Tambah workflow snake, build otomatis, dan dokumen serah-terima"`
- [ ] **Step 7: Coba publikasi**

Run: `git remote add origin https://github.com/RayNathans/RayNathans.git && git push -u origin main`
Expected: bila repo sudah ada dan kredensial tersedia → sukses, lalu buka `https://github.com/RayNathans` di Chrome dan screenshot; bila `repository not found` → laporkan ke Nathan langkah 1 di `SERAH-TERIMA.md` tanpa mencoba membuat repo lewat cara lain.
