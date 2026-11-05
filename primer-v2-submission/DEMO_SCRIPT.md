# 60–90 saniyelik demo kaydı

Gerçek katılımcı yoksa A/B oynanışları sentetik senaryo olarak gösterilebilir; videoda simülasyon olduğu baştan sona görünür olmalıdır. Bu, gerçek oyuncu demosu diye sunulmaz. `demo-simule.mp4` bu açık etiketle hazırlanmış 70 saniyelik animasyondur; gerçek uygulama ekran kaydı değildir.

1. **0–10 sn:** The Primer v2'yi aç, gizlilik metnini ve consent kutusunu göster. “Model ONNX ile tarayıcıda çalışıyor; bu sayfa ipuçlarını sunucuya yollamıyor.”
2. **10–30 sn:** Simülasyon A aynı sahnede hızlıca test seçeneğini işaretlesin. Model olasılığı yaklaşık %10,5; eşik altında kaldığı için kısa akış ve normal tempo sürsün.
3. **30–55 sn:** Simülasyon B aynı sahnede birkaç kez düşünüp seçimini değiştirsin, sonra aynı seçeneği işaretlesin. Model olasılığı yaklaşık %84,9; tutor açıklaması açılsın ve süre baskısı kalksın.
4. **55–70 sn:** Python parity kahini (`?test=parity`) ve beş vaka PASS çıktısını kısaca göster.
5. **70–85 sn (isteğe bağlı canlı kayıt uzatması):** CSV indirme ve `kaynak=sentetik`/PII içermeyen sütunları göster; 21-adım testinden veya release pin planından bir kareyle bitir. Hazır animasyon ilk 70 saniyede sona erer.

İki kişi gerçekten katılmadıysa, demo içindeki oyuncuları “simülasyon” diye açıkça adlandırın. Görüntüde gerçek ad/e-posta gibi kişisel bilgi bırakmayın. Son videoyu ekip erişilebilir bir bağlantıya yükleyip `DELIVERY_CHECKLIST.md`'ye eklemeli.
