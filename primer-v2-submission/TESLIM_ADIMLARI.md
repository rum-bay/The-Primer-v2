# Teslimden önce tamamlanacaklar

Bu klasör yerel prototipi ve ödev belgelerini içerir. Ödev sentetik veriyle çalışmaya izin verir; veri kaleminin yarısı alınır. HF/GitHub yayını, canlı URL ve video ekip tarafından tamamlanmalıdır.

## 1. Veri yolunu seç

**Tam veri puanı için:** uygulamayı `npm run serve` ile açıp en az 15 gönüllü gerçek oturum oynatın. Her oturumun sonunda CSV'yi indirin; isim/e-posta gibi bilgi eklemeyin. `?source=sentetik` ile açılan oturumları gerçek sayısına dahil etmeyin.

**Gönüllü bulamazsanız:** repodaki 48 sentetik oturum ve 240 karar satırını kullanın. Bu, ödevin izin verdiği seçenektir ve veri kaleminin yarısını verir. Bu oturumları `gercek` diye değiştirmeyin; üretici kuralı ve tohumu README'de belgeli.

## 2. Eğit ve pariteyi doğrula

Gerçek oturum topladıysanız CSV dosyalarını birleştirin:

```powershell
.venv\Scripts\python scripts/merge_sessions.py .\katilimci-1.csv .\katilimci-2.csv
```

Her iki veri yolunda eğitim ve referans vakalarını çalıştırın:

```powershell
.venv\Scripts\python train.py
.venv\Scripts\python tests/write_parite.py
.venv\Scripts\python tests/parite.py
```

15 gerçek oturum varsa `model/config.json` içinde `release_ready: true` beklenir. Yalnız sentetik veride `release_ready: false`, `synthetic_demo_ready: true` beklenir; model kartı sentetik kökeni açıklar.

## 3. Tarayıcı regresyonunu çalıştır

```powershell
npm install
```

Bir terminalde `npm run serve`, ikinci terminalde:

```powershell
npm run e2e
```

Beş ONNX vaka paritesinin ve 21 kararlı hikâye akışının Cypress'te geçtiğini doğrulayın.

## 4. Yayın ve teslim bağlantıları

1. Hugging Face hesabında `hf auth login` ile oturum açın. 15 gerçek oturum varsa `python publish_hf.py <kullanici/the-primer-v2>` çalıştırın. Yalnız sentetik kullanıyorsanız ödevin bu seçeneğini açıkça seçmek için `python publish_hf.py <kullanici/the-primer-v2> --synthetic-demo` çalıştırın. Sentetik veri kaynağı public model kartında belirtilir; gerçek katılımcı gibi gösterilmez. Her iki yol da model URL'sini commit hash'ine sabitler.
2. Projeyi kendi GitHub hesabınızda yayınlayın; **Settings → Pages → Source: GitHub Actions** seçin. Gizli pencerede canlı uygulamayı ve commit sabitli HF modelini açıp kontrol edin.
3. Aynı sahnedeki iki farklı davranışı gösteren 60–90 saniyelik ekran kaydı alın. Gerçek iki katılımcı yoksa oyunları simüle edin ve videoda simülasyon olduğunu açıkça belirtin.
4. [Teslim formuna](https://forms.gle/pr9QVEfLJuaFiXw39) GitHub repo, commit sabitli HF model, canlı uygulama ve demo videosu bağlantılarını girin.

Tam durum tablosu: `DELIVERY_CHECKLIST.md`. Son tarih: 6 Kasım 2026, 23:59.
