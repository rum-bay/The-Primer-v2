# Teslim formu için son bağlantılar

Bu dosyadaki boşluklar, hesap ve insan etkileşimi gerektirdiği için bu çalışma alanında tamamlanmadı. Dış bağlantı olmadan teslim etmeyin.

- GitHub repo: **yayın bekliyor**
- Hugging Face model repo + commit'e sabitlenmiş `model.onnx`: **yayın bekliyor**
- Canlı uygulama (GitHub Pages): **yayın bekliyor**
- Demo materyali: [70 saniyelik sentetik simülasyon MP4](demo-simule.mp4) hazır. Simüle A/B davranışını gösteren tasarımlı animasyondur; gerçek ekran kaydı veya katılımcı videosu değildir. Hoca ekran kaydını şart koşuyorsa, takımın uygulamayı açıp kendi ekran kaydını alması gerekir.
- Veri: **48 sentetik oturum / 240 karar; gerçek oturum 0**. Ödev sentetik veriye izin verir, veri kaleminde yarım puan alınır.
- Model yayın kapısı: 15+ gerçek oturumla normal yayın; yoksa `publish_hf.py <repo> --synthetic-demo` açık seçimiyle, sentetik sınıf demosu olarak yayın.
- Teslim formu: <https://forms.gle/pr9QVEfLJuaFiXw39>
- Özgünlük beyanı: projede Codex kullanımı README'de belirtilmiştir; ekip kendi incelemesini ve elle yaptığı düzeltmeleri teslimden önce doğru biçimde eklemeli.

Her linki çıkış yapmış/gizli pencerede açıp erişim kontrolü yaptıktan sonra forma koyun.

## Yerel doğrulama

- Python ONNX Oracle/parite: **5/5 vaka geçti**; her vakada Python çıktısı ile aynı ONNX olasılık farkı `0.00e+00`.
- Sentetik yayın kapısı: `--synthetic-demo --dry-run` **geçti**; aynı veri normal yayın seçeneğiyle denenince yayın betiği beklenen şekilde reddetti. Hub'a yükleme yapılmadı.
- Yerel web sunucusu: `http://127.0.0.1:4173/web/` HTTP 200 döndürdü ve Primer sayfasını sundu.
- Cypress tarayıcı regresyonu: **başlatılamadı**; Cypress 14.5 kuruldu fakat bu Windows ortamında Cypress çalıştırıcısı gerekli sistem kütüphanesi/bağımlılık eksikliğiyle açılmadı (exit 2147483651). Test dosyası ve komut hazır. Cypress'in desteklediği yerel bir bilgisayarda `npm install`, bir terminalde `npm run serve`, ikinci terminalde `npm run e2e` çalıştırıp sonucu doğrulayın.
