# Profil Cyberpunk Tahap 2: Semua Seksi Jadi SVG · Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Mendekatkan tampilan README di GitHub ke Mockup B rev 2 dengan mengubah lima bagian yang masih teks/badge/layanan luar menjadi SVG neon dari generator yang sama, dan mengganti kartu stats pihak ketiga dengan data yang diambil sendiri dari API publik GitHub.

**Architecture:** Lima builder baru di `tools/build.py` (strip, identity, telemetry, timeline, connect + tombol) memakai template di `tools/templates/`. `tools/fetch_stats.py` (stdlib) mengambil data dari REST API publik + halaman kontribusi dan menulis `data/stats.json`; workflow `stats.yml` menjalankannya tiap 12 jam lalu build + commit. README hanya menyusun gambar, tautan, `<details>` sertifikat, dan baris typing.

**Tech Stack:** sama dengan tahap 1. Tanpa token untuk fetch lokal; di Actions `GITHUB_TOKEN` hanya menaikkan rate limit.

**Spec:** `docs/superpowers/specs/2026-11-04-github-profile-cyberpunk-design.md` + keputusan tahap 2 di bawah (disetujui Nathan 2026-11-04: "kerjakan kelima poin itu sampai kelar").

## Keputusan tahap 2

- Latar semua SVG baru `#0d1117` (warna latar GitHub gelap) agar sambungan antar gambar tidak terlihat; panel di dalamnya tetap `#0a0f24` dengan garis `#15214a`.
- Status strip: sel `ROLE`, `COMPANY|STATUS`, `CERTS`, `FOLLOWERS` (dari stats). Komarev dilepas karena hitungannya tidak bisa diambil ke dalam SVG.
- Telemetry: satu `telemetry.svg` tiga panel (GITHUB STATS: commits publik, kontribusi 12 bulan, repo, stars, PR, followers · STREAK: total/current/longest 12 bulan dari kalender kontribusi · TOP LANGUAGES: byte per bahasa dari repo milik sendiri). Angka berasal dari `data/stats.json`; tidak ada angka hard-coded.
- Timeline: `data/timeline.json` untuk entri selain pekerjaan sekarang; entri pertama dari `profile.job` + `job_strings`. Tanda panah `→` diganti `–` di semua `timeline_when` (font subset tidak punya `→`).
- Connect: `connect.svg` (kalimat ajakan) + tiga tombol SVG terpisah yang dibungkus `<a>` agar tetap bisa diklik.
- Skill badges shields.io dan baris typing tetap (keduanya sudah mirip mockup). Sertifikat tetap `<details>`.

## Global Constraints

Sama dengan tahap 1 (palet, tanpa sumber eksternal di SVG, < 400 KB, reduced-motion, tanpa penanda atribusi), ditambah: `fetch_stats.py` tidak boleh menggagalkan build bila API gagal (pakai `data/stats.json` lama).

---

### Task 1: fetch_stats + data stats/timeline
**Files:** Create `tools/fetch_stats.py`, `data/stats.json`, `data/timeline.json`; Test `tests/test_fetch_stats.py`.
**Produces:** `parse_contributions(html) -> list[dict]` (date, count), `compute_streaks(days, today) -> dict` (total, current, longest, current_range, longest_range), `aggregate_languages(per_repo, top=6) -> list[dict]` (name, pct, bytes, color), `fetch_all(user, token=None) -> dict`, `main()` menulis `data/stats.json`.
- [ ] Test parse (HTML cuplikan 3 hari), streaks (deret sintetis), languages (persen bulat total 100, urut turun) → RED → implement → GREEN → fetch nyata → commit.

### Task 2: Builder strip, identity, telemetry, timeline, connect
**Files:** Create template `strip.svg`, `identity.svg`, `telemetry.svg`, `timeline.svg`, `connect.svg`, `button.svg`; Modify `tools/build.py`, `tests/test_build.py`, `tests/fixtures.py`.
**Produces:** `build_strip(data)`, `build_identity(data)`, `build_telemetry(data)`, `build_timeline(data)`, `build_connect(data) -> dict[str,str]` (`connect.svg`, `btn-linkedin.svg`, `btn-portfolio.svg`, `btn-email.svg`); `job_strings` memakai `–`.
- [ ] Test per builder (teks kunci, toggle current_job, XML valid, glyph) → RED → implement → GREEN → build → verifikasi visual Chrome → commit.

### Task 3: README, workflow stats, serah-terima
**Files:** Modify `tools/templates/README.md.tpl`, `tests/test_build.py` (ReadmeTests), `tests/test_repo.py`, `docs/SERAH-TERIMA.md`; Create `.github/workflows/stats.yml`.
- [ ] Test README (aset baru ada; tidak ada shields status/komarev/github-readme-stats/streak-stats; tombol dibungkus `<a href>` benar) + stats.yml valid → RED → implement → GREEN → build → pratinjau → commit → push → cek github.com/RayNathans.
