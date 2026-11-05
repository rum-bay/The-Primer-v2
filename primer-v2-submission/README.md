# The Primer v2 — davranışa göre uyarlanan yazılım mühendisliği hikâyesi

**Teslim paketi:** küçük bir sklearn modeli, ONNX, tarayıcıda çalışan hikâye/tutor, veri toplama dışa aktarımı, test kahini, Cypress 21-adım regresyonu ve release/vize belgeleri.

> **Hazırlık durumu:** yerel prototip ve 48 sentetik eğitim oturumu. Ödev sentetik veriye izin verir; veri kaleminin yarısı alınır. Sentetik oturumları gerçek gönüllüler gibi sunmayın. 70 saniyelik sentetik A/B simülasyon animasyonu `demo-simule.mp4` içinde; gerçek uygulama ekran kaydı değildir. HF/GitHub yayını ve canlı URL henüz yok.

Teslimden önce zorunlu kalan kısa adımlar: [`TESLIM_ADIMLARI.md`](TESLIM_ADIMLARI.md).

## Sentetik demo

[70 saniyelik simülasyon animasyonunu aç](demo-simule.mp4). Aynı karar sahnesinde sentetik A için model olasılığı yaklaşık 10,5%, sentetik B için 84,9% çıkar; video sentetik/simülasyon uyarısını görünür tutar. Bu MP4 gerçek kullanıcı veya gerçek ekran kaydı değildir. Canlı uygulamanın ekran kaydı isteniyorsa uygulamayı yerelde açıp ayrıca kaydedin.

## 3 komutta kurulum ve model üretimi

Python 3.12 ile proje kökünde:

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python train.py
```

`train.py` CSV'yi oturum bazında ayırır, spec'teki eşikleri uygular ve yalnızca kapı geçerse `model/` artefaktlarını yazar. ONNX dışa aktarımı sklearn olasılıklarıyla `1e-4` toleransta karşılaştırılır. `skl2onnx` kullanılabildiğinde standart exporter tercih edilir; Windows Uygulama Denetimi ONNX'in yerel yardımcı uzantısını engellerse aynı `StandardScaler + LogisticRegression` işlemleri ONNX protobuf graph'ına yazılır ve yine ONNX Runtime ile doğrulanır.

## Uygulamayı yerelde aç

Proje kökünde bir terminal:

```powershell
npm run serve
```

Tarayıcıda `http://localhost:4173/web/` aç. Uygulamayı Python kurmadan statik sunar. İlk model/ONNX Runtime yüklemesi için internet gerekir. Sonraki çıkarım tarayıcıda yapılır; karar girdileri sunucuya post edilmez.

## Veri toplama ve yeniden eğitim

1. Oyuncuya katılım bilgisini ve gönüllülük onayını okuyup sor; kişi adını veya iletişim bilgisini dosyaya ekleme. Uygulamada onay kutusu seçilir.
2. Katılımcı karar verir ve isterse oturumu istediği noktada bitirir. **Her tarayıcı belleğinde biriken tüm tamamlanmış oturumlar** `CSV'yi indir` ile dışa aktarılır. Yeni kişiye geçmeden önce indirme alın; ardından `Yeni kişi için sıfırla` ile belleği temizle.
3. Gerçek kullanıcı verisi toplayabiliyorsanız en az 15 oturum tamamlayınca indirilen CSV dosyalarını birleştirin:

```powershell
.venv\Scripts\python scripts/merge_sessions.py .\katilimci-1.csv .\katilimci-2.csv
.venv\Scripts\python train.py
.venv\Scripts\python tests/write_parite.py
```

`train.py` `release_ready` alanını yalnızca en az 15 farklı gerçek oturum için `true` yapar. Gerçek oturum yoksa bu ödevde izin verilen sentetik rotayı kullanın: `synthetic_demo_ready` eval ve ONNX parite kapıları geçince `true` olur, ancak veri puanının yarısı alınır. `publish_hf.py` sentetik modelin yanlışlıkla normal sürüm diye yayınlanmasını engeller; açıkça işaretlemek için aşağıdaki `--synthetic-demo` seçeneği zorunludur. Model kartı ve yayın manifesti kaynak türünü belirtir. Sentetik metrikler gerçek öğrenenlerde başarı kanıtı değildir.

Oturumlarda hem `ipucu_istendi=0` hem `ipucu_istendi=1` örnekleri bulunmalı; her iki sınıf yoksa eğitim başlamaz. Katılımcı dosyalarını proje köküne geçici olarak kopyalayın ya da komuta tam yollarını verin.

Bu proje klasöründeki `data/oturumlar.csv` başlangıçta yalnızca `sentetik` satırlar içerir. `generate_synthetic_data.py` aynı 48 sentetik oturumu ve 240 kararı `SEED=20261105` ile `data/sentetik.csv` dosyasına üretir ve gerçek/sentetik karma eğitim CSV'sinin üzerine yazmaz. Üreteçte özelliklerden destek isteği olasılığı hesaplanıp `random.Random` ile örneklenir; bu, gerçek kullanıcı davranışına dair kanıt değildir. Sentetik veriyle çalıştırılan metrikleri gerçek kullanıcı başarısı gibi yorumlamayın.

## Testler

- Python ONNX Oracle/parite: `.venv\Scripts\python tests/parite.py` — beş sabit girdi ve `<1e-4` olasılık toleransı.
- Browser regression: `npm install`, ayrı terminalde `npm run serve`, sonra `npm run e2e`. Cypress 21 karar akışını ve her karardaki ONNX olasılık çıktısını kontrol eder.

## Mühendislik gerekçesi: 3V ve V&V

- **Velocity:** Tek `train.py` komutu grup bazlı eval, ONNX dışa aktarımı ve sözleşme üretimini çalıştırır.
- **Validation:** Yazılı eşik kapısı kullanıcı tercih tahminini held-out oturumlarda ölçer; Python kahini, tarayıcı paritesi ve Cypress regresyonu dağıtım kusurlarını kontrol eder.
- **Versioning:** config içine veri ve model SHA-256 özetleri ile bağımlılık/split bilgisi yazılır; uygulama HF modelini commit hash'ine sabitler. `RELEASE.md` geri alma yolunu kaydeder.
- **Verification / validation:** ONNX↔sklearn paritesi, uygulamanın teknik sözleşmeye uygunluğunu doğrular. Tutor açıklamasının katılımcıya yararlı olup olmadığını ise gerçek kullanıcı oturumları ve geri bildirimi geçerler; sentetik test bunun yerine geçmez.

## HF'ye yayınla ve sabit sürümü Pages'e bağla

Yalnızca spec eval kapısını ve parite testlerini geçen artefaktı yayınla. Bir kez `hf auth login` ile Hugging Face hesabında oturum açtıktan sonra, 15 gerçek oturum varsa:

```powershell
.venv\Scripts\python publish_hf.py <hf-kullanici/the-primer-v2>
```

15 gerçek oturum bulamıyorsanız, ödevin izin verdiği ve veri kaleminde yarım puan alan sentetik sınıf demosunu açıkça seçin:

```powershell
.venv\Scripts\python publish_hf.py <hf-kullanici/the-primer-v2> --synthetic-demo
```

Yükleme yapmadan önce yayın kapısını doğrulamak için `--dry-run` ekleyin; Hugging Face hesabına bağlanmaz ve dosya yüklemez.

Betik public HF model reposu oluşturur/yükler, dönen gerçek commit hash'ini kullanarak `web/site.json`'a iki `resolve/<commit>/...` URL'sini yazar. Model kartı veri kökenini ve gerçek veriyle doğrulanma durumunu gösterir; `web/site.json` seçilen yayın modunu kaydeder. Ardından bu dosyaları GitHub reposuna commit/push edin. GitHub repo ayarlarında **Settings → Pages → Source: GitHub Actions** seçin; [Pages workflow](.github/workflows/pages.yml) `/web/` sayfasını ve repo dosyalarını yayınlar. Son link biçimi `https://<github-kullanici>.github.io/<repo>/web/` olur.

## Tasarım ve kaynaklar

Senaryo kendi özgünleştirmemiz: yazılım mühendisliğine yeni başlayan kişinin ekip içindeki test, güvenli yama, tekrar üretim ve geri alma kararları. Model tercih tahmini yapar; yetenek değerlendirmez. “Tutora ihtiyaç” etiketi, her karardan sonra oyuncunun açık self-report yanıtıdır. Uygulama yeni davranışlardan anlık öğrenmez; kayıtlar ancak ekip veriyi birleştirip `train.py`'yi yeniden çalıştırdığında eğitimde kullanılır.

- [Amershi et al. (2019), *Software Engineering for Machine Learning: A Case Study*](https://www.microsoft.com/en-us/research/wp-content/uploads/2019/03/amershi-icse-2019_Software_Engineering_for_Machine_Learning.pdf) — veri/sürümleme ve ML yaşam döngüsü.
- [Shankar et al. (2022), *Operationalizing Machine Learning: An Interview Study*](https://arxiv.org/abs/2209.09125) — Velocity, Validation, Versioning ve gözlem.
- [Mitchell et al. (2019), *Model Cards for Model Reporting*](https://arxiv.org/abs/1810.03993) — kullanım bağlamı, metrik ve sınırların şeffaf yazılması.
- [Breck et al. (2017), *The ML Test Score*](https://research.google/pubs/the-ml-test-score-a-rubric-for-ml-production-readiness-and-technical-debt-reduction/) — üretim testleri ve izleme.
- [Başlangıç reposu: `huggingface-hello-web`](https://github.com/seyyah/huggingface-hello-web) — `onnxruntime-web` istemci ve sözleşme deseni.
- [ONNX Runtime: browser web-app and inference flow](https://onnxruntime.ai/docs/tutorials/web/build-web-app.html) — in-browser inference choice and privacy implications.
- [GitHub Pages: custom workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages) — the checked-in Actions publish workflow.

## Coding-agent beyanı

- Codex (OpenAI) yönergeyi çözümleyip bu projeye özgü model sözleşmesini, değerlendirme kapısını ve 21 karar akışını taslakladı; ekip bu kararları gözden geçirmelidir.
- Codex sentetik veri üreticisini, eğitim/ONNX hattını, web veri toplama akışını, testleri ve teslim belgelerini oluşturmak için kullanıldı.
- Bu klasörde gerçek katılımcı girdisi veya ekip tarafından yapılmış manuel düzeltme beyan edilmiyor; henüz gerçek oturum olmadığı için ilk eğitim verisi sentetiktir.
- Ekip teslimden önce hangi çıktıları incelediğini, neyi elle düzelttiğini ve yeni toplanan verinin onayını kendi katkısını doğru anlatacak şekilde bu beyana eklemelidir.
- Demo senaryosu, gizlilik akışı, sabit eşik, sentetik veri ve test sonuçlarını ekip üyeleri anlamadan teslim etmemeli; metrikleri ve kendi katkılarını gözden geçirip değiştirdiklerini belirtmeli.

## Dış yayın ve teslim

Adımlar ve ödünleşimler [RELEASE.md](RELEASE.md)'de; bağlantı/form durumları [DELIVERY_CHECKLIST.md](DELIVERY_CHECKLIST.md)'de. HF `main` yerine commit'e sabitlenmiş URL ve gizli pencere doğrulaması zorunludur. Vize düşünce egzersizi [SINAV_TASARIMI.md](SINAV_TASARIMI.md)'de.
