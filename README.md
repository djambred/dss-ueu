Rumus & Dokumen Teknis — Perhitungan Komponen IKD (Indeks Kinerja Dosen)

Dokumen ini menjabarkan rumus, definisi variabel, langkah perhitungan, dan aturan keputusan yang dipakai di aplikasi DSS Penilaian Kinerja Dosen (UEU). Disusun ringkas, formal, dan siap dipakai sebagai referensi pengembang/akademik.


---

Daftar isi

1. Tujuan singkat


2. Notasi & definisi variabel


3. Komponen perhitungan (Formula)

A. Mengajar

B. Penelitian

C. Publikasi

D. Pengabdian



4. Perhitungan Indeks Kinerja Dosen (IKD) — komposit


5. Alignment Score (kesesuaian tema riset)


6. SKS per semester & aturan kelayakan DT/DTT


7. Klasifikasi & threshold keputusan


8. Aturan apresiasi (award)


9. Contoh perhitungan (angka contoh)


10. Catatan implementasi & quality checks


11. Ringkasan rumus




---

Tujuan singkat

Memberi formula baku untuk menghitung komponen kinerja (mengajar, penelitian, publikasi, pengabdian), menyusun IKD komposit, serta aturan keputusan terkait kelayakan DT/DTT dan pemberian apresiasi. Dokumen ini menjadi acuan implementasi pada app.py.


---

Notasi & definisi variabel

d : satu dosen (id unik)

T : periode penilaian (mis. 1 tahun)

bulan : 1..12 (data per bulan)

SKS_b : SKS mengajar pada bulan b (integer)

SKS_sem1 = ∑_{b=1..6} SKS_b (jumlah SKS semester 1)

SKS_sem2 = ∑_{b=7..12} SKS_b (jumlah SKS semester 2)

SKS_year = SKS_sem1 + SKS_sem2

Penelitian_b : jumlah unit/aktivitas penelitian pada bulan b

Publikasi_b : jumlah publikasi pada bulan b

Pengabdian_b : jumlah kegiatan pengabdian pada bulan b

Penelitian_year = ∑_{b} Penelitian_b

Publikasi_year = ∑_{b} Publikasi_b

Pengabdian_year = ∑_{b} Pengabdian_b

AK : angka kredit (opsional)

Expertise_set : daftar tema riset yang dinyatakan dosen

Theme_pool_fak : tema prioritas fakultas

Theme_pool_uni : tema prioritas universitas


Semua variabel merujuk pada periode penilaian T (biasanya 1 tahun).


---

Komponen perhitungan (Formula)

Prinsip: setiap komponen dihitung sebagai skor komponen (0–100) berdasarkan rasio capaian aktual terhadap target/denominator yang disepakati. Denominator dipilih agar sebagian besar dosen tidak otomatis mencapai 100%.

A. Mengajar (Skor_Mengajar)

Definisi: mengukur beban & performa pengajaran dalam SKS selama 1 tahun.

Rumus:

Skor_Mengajar = min( (SKS_year / D_MENGAJAR) * 100 , 100 )

D_MENGAJAR = denominator target tahunan untuk pengajaran (contoh implementasi: 44 SKS/year).


Catatan: jika SKS_year = D_MENGAJAR → skor = 100%.


---

B. Penelitian (Skor_Penelitian)

Definisi: jumlah kegiatan penelitian terdokumentasi selama T.

Rumus:

Skor_Penelitian = min( (Penelitian_year / D_PENELITIAN) * 100 , 100 )

D_PENELITIAN = target penelitian per tahun untuk skor 100 (contoh: 6 kegiatan/year).



---

C. Publikasi (Skor_Publikasi)

Definisi: jumlah publikasi terverifikasi selama T.

Rumus:

Skor_Publikasi = min( (Publikasi_year / D_PUBLIKASI) * 100 , 100 )

D_PUBLIKASI = publikasi per tahun untuk 100% (contoh: 3 publikasi/year).



---

D. Pengabdian (Skor_Pengabdian)

Definisi: kegiatan pengabdian masyarakat terdokumentasi.

Rumus:

Skor_Pengabdian = min( (Pengabdian_year / D_PENGABDIAN) * 100 , 100 )

D_PENGABDIAN = target kegiatan/year untuk 100% (contoh: 4 kegiatan/year).



---

Perhitungan Indeks Kinerja Dosen (IKD) — komposit

Bobot default:

w_mengajar = 0.40

w_penelitian = 0.25

w_publikasi = 0.25

w_pengabdian = 0.10


Rumus:

IKD = w_mengajar * Skor_Mengajar
      + w_penelitian * Skor_Penelitian
      + w_publikasi * Skor_Publikasi
      + w_pengabdian * Skor_Pengabdian

Hasil IKD berada di rentang 0–100.


---

Alignment Score (kesesuaian tema riset)

Mengukur persentase kegiatan penelitian/publikasi dosen yang sejalan dengan tema prioritas fakultas/universitas atau expertise dosen.

Definisi:

N_total_items = Penelitian_year + Publikasi_year

N_matched = jumlah item yang bertag tema cocok dengan (Expertise_set ∪ Theme_pool_fak ∪ Theme_pool_uni)


Rumus:

Alignment (%) = 100 * N_matched / N_total_items    (jika N_total_items > 0)
Alignment = 0%                                     (jika N_total_items = 0)

Catatan: Pada produksi, wajibkan tag tema saat submit; pada demo boleh disimulasikan.


---

SKS per semester & aturan kelayakan DT/DTT

Perhitungan SKS per semester:

SKS_sem1 = ∑_{b=1..6} SKS_b
SKS_sem2 = ∑_{b=7..12} SKS_b
SKS_sem_max = max(SKS_sem1, SKS_sem2)

Batas kebijakan default:

DT: maksimal 18 SKS / semester

DTT: maksimal 11 SKS / semester


Aturan evaluasi:

Jika SKS_sem_max > allowed_cap(status) → flag beban melebihi batas.

Untuk rekomendasi kenaikan ke DT:

IKD >= IKD_threshold_DT (default 75)

Skor_Publikasi >= publikasi_threshold (default 50)

SKS_sem_max <= DT_cap (18)

Tidak ada recent rejected verification (opsional)


Jika semua terpenuhi → recommend_promote (layak DT).



---

Klasifikasi & threshold keputusan

IKD classification (contoh):

IKD >= 85 → Sangat Baik

70 <= IKD < 85 → Baik

55 <= IKD < 70 → Cukup

40 <= IKD < 55 → Kurang

IKD < 40 → Tidak Memadai


Threshold default kelayakan DT:

IKD_threshold_DT = 75.0

publikasi_threshold = 50.0


Status tindakan:

recommend_promote — layak DT

monitor — pemantauan & mentoring

probation — program peningkatan

reject — intervensi diperlukan



---

Aturan apresiasi (award)

Contoh aturan pemberian apresiasi berdasar IKD & komponen:

Gold jika IKD >= 85 → Sertifikat Prestasi Tinggi + prioritas pendanaan.

Silver jika IKD >= 75 → Sertifikat Prestasi.

Bronze jika IKD >= 70 → Penghargaan Kinerja.

Publikasi Unggul bila Skor_Publikasi >= 80.


> Catatan: kebijakan ini dapat dikonfigurasi oleh Admin.




---

Contoh perhitungan (angka contoh)

Data contoh dosen A (tahun):

SKS_sem1 = 14, SKS_sem2 = 12 → SKS_year = 26

Penelitian_year = 3

Publikasi_year = 1

Pengabdian_year = 1


Parameter denominator (default):

D_MENGAJAR = 44

D_PENELITIAN = 6

D_PUBLIKASI = 3

D_PENGABDIAN = 4


Langkah:

1. Skor_Mengajar = min((26/44)*100,100) = 59.09


2. Skor_Penelitian = min((3/6)*100,100) = 50.00


3. Skor_Publikasi = min((1/3)*100,100) = 33.33


4. Skor_Pengabdian = min((1/4)*100,100) = 25.00



IKD:

IKD = 0.40*59.09 + 0.25*50 + 0.25*33.33 + 0.10*25
    = 23.636 + 12.5 + 8.333 + 2.5 = 46.97

Klasifikasi: IKD ≈ 46.97 → Kurang

SKS per-semester max = 14 (tidak melebihi cap DT 18)


Alignment (misal):

Jika dari total 4 item penelitian+publikasi, 2 cocok → Alignment = 50%


Keputusan:

IKD < 75 → Tidak layak DT

Rekomendasi: program peningkatan penelitian & publikasi.



---

Catatan implementasi & quality checks

1. Tag Tema: Wajibkan field tema saat dosen submit penelitian/publikasi untuk alignment yang valid.


2. Parameter denominator / bobot: Simpan di file konfigurasi (JSON/DB) agar mudah disesuaikan kebijakan.


3. Satuan & konsistensi: SKS dikumpulkan per bulan; pastikan penjumlahan semester benar.


4. Verifikasi: Hanya gunakan item Approved untuk perhitungan final pada produksi (opsional kebijakan).


5. Audit trail: Simpan log perubahan klaim (tanggal, verifikator, komentar).


6. Rounding & presentasi: Tampilkan skor komponen dengan 2 desimal; alignment dengan 2 desimal + %.


7. Edge cases: Jika N_total_items = 0 (tidak ada penelitian/publikasi), set Alignment = 0% dan tampilkan catatan.


8. Validasi Input: (opsional) Validasi saat input agar SKS per semester tidak melebihi batas status (DT/DTT) — atau tampilkan warning.




---

Ringkasan rumus

Skor_Mengajar = min( (SKS_year / D_MENGAJAR) * 100 , 100 )
Skor_Penelitian = min( (Penelitian_year / D_PENELITIAN) * 100 , 100 )
Skor_Publikasi = min( (Publikasi_year / D_PUBLIKASI) * 100 , 100 )
Skor_Pengabdian = min( (Pengabdian_year / D_PENGABDIAN) * 100 , 100 )

IKD = 0.40*Skor_Mengajar + 0.25*Skor_Penelitian + 0.25*Skor_Publikasi + 0.10*Skor_Pengabdian

Alignment% = 100 * N_matched / (Penelitian_year + Publikasi_year)  (if denom>0)
