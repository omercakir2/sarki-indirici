# Bedava ve Reklamsız MP3 Şarkı İndirici

YouTube linkini yapıştır, MP3 olarak indir. Reklam yok, hesap yok, her şey kendi bilgisayarında çalışır.

- Tek video, oynatma listesi ya da şarkı adıyla arama
- 128 / 192 / 320 kbps MP3, içine kapak resmi ve sanatçı/şarkı adı gömülü
- Canlı ilerleme, indirme kuyruğu, "klasörde göster"
- İndirme motoru (yt-dlp) her açılışta kendini günceller

> Durum: geliştirme aşamasında. Docker imajı ve çift tıkla açılan masaüstü uygulaması sıradaki adım.

## Geliştirme

Gerekenler: Python 3.11+, [uv](https://docs.astral.sh/uv/), Node 20+, ffmpeg ve deno (`brew install ffmpeg deno`).

```bash
cd frontend && npm install && npm run build
```

```bash
cd backend && uv sync && uv run uvicorn app.main:app --port 8765
```

Sonra tarayıcıda http://127.0.0.1:8765 adresini aç. Arayüzde değişiklik yaparken `cd frontend && npm run dev` (http://localhost:5173, API'yi 8765'e yönlendirir).

Ayarlar ortam değişkenleriyle değişir: `SARKI_DOWNLOAD_DIR` (varsayılan `~/Downloads/Sarki-Indirici`), `SARKI_DATA_DIR`, `SARKI_MAX_PARALLEL` (varsayılan 2), `SARKI_AUTO_UPDATE=0`, `YTDLP_PATH`.

## Yapı

```
backend/   FastAPI: arama, önizleme, indirme kuyruğu (SSE ile canlı durum), yt-dlp kurulum/güncelleme
frontend/  Vite + React + Tailwind arayüz
PRODUCT.md ürün tanımı · DESIGN.md görsel sistem
```

## Not

Bu araç kişisel kullanım içindir. İndirdiğin içeriklerin telif haklarına ve YouTube kullanım koşullarına uymak senin sorumluluğundadır.
