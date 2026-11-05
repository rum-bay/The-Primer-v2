# Veri sözlüğü — `oturumlar.csv`

Her satır bir karar; tek oturumdaki satırlarda `oturum_id` aynıdır. Gerçek oturum kimliği web uygulamasında kriptografik rastgele UUID ile üretilir. Kişiyi tanımlayan alan toplanmaz.

| Sütun | Anlam | Birim / kabul edilen değer |
|---|---|---|
| `oturum_id` | Rastgele oturum kimliği | UUID; sentetik satırlarda üreteçle sabitlenmiş UUID |
| `karar_no` | Oturumdaki karar sırası | 1–21, tamsayı |
| `bekleme_suresi_sn` | Karar ekranının açılmasından seçim taahhüdüne kadar geçen süre | saniye, 0–90 |
| `karar_degistirme` | Son seçimden önce seçim değişikliği sayısı | adet, 0+ |
| `tekrar_okuma` | “Tekrar oku” düğmesi sayısı | adet, 0+ |
| `onceki_yanlis` | Bu oturumda önceki sahnelerde seçilen acele dal sayısı | adet, 0+ |
| `onceki_ipucu` | Önceki kararlarda modelin açtığı tutor açıklaması sayısı | adet, 0+ |
| `zorluk` | Sahne zorluğu | 1–5, sıra kodu |
| `dal_kodu` | Seçilen dal | 0, 1 veya 2 |
| `ipucu_istendi` | Karardan sonra oyuncunun açıkça tutor açıklaması isteyip istemediği | 0 = hayır, 1 = evet |
| `kaynak` | Verinin kaynağı | `gercek` veya `sentetik` |

Sentetik üreteç hedef etiketi olasılığını etkileşim özelliklerinden simüle eder; gerçek kullanıcı davranışı değildir. Web uygulaması satırları cihazda bellekte tutar, yükleme yapmaz; CSV indirme gönüllüdür.
