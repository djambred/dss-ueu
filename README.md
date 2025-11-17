# dss-ueu

DSS Penilaian Kinerja Dosen

Universitas Esa Unggul

Dokumen ini memberikan gambaran umum mengenai aplikasi Decision Support System (DSS) Penilaian Kinerja Dosen, sebuah platform internal berbasis Streamlit yang dikembangkan untuk mendukung pengukuran kinerja dosen berdasarkan indikator Tridharma Perguruan Tinggi.


---

1. Tujuan Sistem

Sistem ini dirancang untuk:

Menyediakan pemantauan kinerja dosen secara kuantitatif dan periodik.

Mendukung proses pengambilan keputusan pada tingkat Prodi, Fakultas, dan Universitas.

Menstandarkan proses verifikasi kinerja dosen sesuai ketentuan akademik internal.



---

2. Fitur Utama

2.1 Dashboard Universitas (Akses Publik – Rektor)

Ringkasan indikator kinerja tingkat universitas

Tren angka kredit tahunan

Distribusi dosen per fakultas

Total publikasi dan aktivitas Tridharma

Peringkat dosen berdasarkan angka kredit


2.2 Role-Based Access

Role	Fitur

Dosen	Profil, dashboard pribadi, input kinerja, riwayat penilaian
Kaprodi	Dashboard prodi, verifikasi data, monitoring kinerja
Dekan	Dashboard fakultas, verifikasi, analitik fakultas
Rektor	Dashboard universitas (tanpa login)


2.3 Data Dummy Otomatis

20 dosen dari 5 fakultas

Data kinerja 12 bulan per dosen

15 entri antrian verifikasi

Tersedia fitur regenerasi data melalui sidebar
