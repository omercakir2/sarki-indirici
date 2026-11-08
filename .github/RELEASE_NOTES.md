## Hangi dosyayı indirmeliyim?

| Bilgisayarın | İndir |
|---|---|
| Windows 10 / 11 | **Sarki-Indirici-Windows.exe** |
| Mac (M1, M2, M3, M4…) | **Sarki-Indirici-macOS-AppleSilicon.zip** |
| Eski Intel Mac | **Sarki-Indirici-macOS-Intel.zip** |

Kurulum yok, dosyayı çift tıklaman yeterli. Şarkılar **İndirilenler › Sarki-Indirici** klasörüne iner.

### İlk açılışta çıkan uyarı

Uygulama ücretli bir geliştirici sertifikasıyla imzalanmadığı için bilgisayarın bir kez uyarı verir:

- **Windows:** "Windows bilgisayarınızı korudu" çıkarsa **Ek bilgi** › **Yine de çalıştır**.
- **Mac:** zip'i aç, uygulamayı **Uygulamalar** klasörüne sürükle ve çift tıkla. "Açılamıyor" derse **Sistem Ayarları › Gizlilik ve Güvenlik** sayfasının en altında **Yine de Aç**'a bas.

İlk açılış yarım dakika kadar sürebilir, çünkü indirme motoru o sırada kuruluyor. Sonraki açılışlar hızlı.

### Docker

```bash
docker run -d -p 127.0.0.1:8080:8080 -v "$PWD/indirilenler:/downloads" ghcr.io/omercakir2/sarki-indirici:latest
```

Sonra http://localhost:8080 adresini aç. Ya da repodaki `docker-compose.yml` ile `docker compose up -d`.
