# app.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta

# ---------------- Page config ----------------
st.set_page_config(
    page_title="DSS Penilaian Kinerja Dosen - UEU",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- Custom CSS ----------------
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 3rem;
        padding: 0 2rem;
    }
</style>
""", unsafe_allow_html=True)

# ---------------- Session state defaults ----------------
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.user_name = None
    st.session_state.user_id = None
    st.session_state.fakultas = None
    st.session_state.prodi = None

# ---------------- Dummy data generator ----------------
@st.cache_data
def generate_dummy_data(seed: int = 42):
    """Generate dummy data for 5 faculties and 20 lecturers + performance + verification queue."""
    np.random.seed(seed)
    # Define faculties and study programs
    faculties = {
        "Teknik": ["Informatika", "Sipil", "Arsitektur"],
        "Ekonomi": ["Manajemen", "Akuntansi"],
        "Hukum": ["Ilmu Hukum"],
        "Kedokteran": ["Kedokteran Umum", "Keperawatan"],
        "Ilmu Sosial": ["Komunikasi", "Psikologi"]
    }

    nama_list = [
        "Andi", "Budi", "Citra", "Dewi", "Eka", "Fajar", "Gita", "Hendra", "Indra", "Joko",
        "Kartika", "Lina", "Maya", "Nina", "Oscar", "Putri", "Qori", "Rini", "Sari", "Tono"
    ]

    # Generate 20 lecturers
    dosen_list = []
    ids = list(range(1, 21))
    faculty_names = list(faculties.keys())
    for i, id_ in enumerate(ids, start=1):
        fak = np.random.choice(faculty_names)
        prodi = np.random.choice(faculties[fak])
        dosen = {
            "id": int(id_),
            "nama": f"Dr. {nama_list[i-1]}",
            "nidn": f"{np.random.randint(10000000,99999999)}",
            "fakultas": fak,
            "prodi": prodi,
            "status": np.random.choice(["DT","DTT"]),
            "jabatan": np.random.choice(["Asisten Ahli","Lektor","Lektor Kepala","Guru Besar"]),
            "email": f"dosen{id_}@esaunggul.ac.id"
        }
        dosen_list.append(dosen)

    dosen_df = pd.DataFrame(dosen_list)

    # Performance data (12 months per dosen)
    performance_rows = []
    for dosen_id in dosen_df['id']:
        for bulan in range(1,13):
            row = {
                "dosen_id": int(dosen_id),
                "bulan": int(bulan),
                "tahun": 2024,
                "mengajar_sks": int(np.random.randint(6,18)),
                "penelitian": int(np.random.poisson(0.8)),
                "pengabdian": int(np.random.poisson(0.5)),
                "publikasi": int(np.random.binomial(1,0.2)),
                "angka_kredit": round(np.random.uniform(3.0,18.0),2)
            }
            performance_rows.append(row)

    performance_df = pd.DataFrame(performance_rows)

    # Verification queue (15 items)
    verif_rows = []
    now = datetime(2024,11,1)
    for i in range(1,16):
        dosen_id = int(np.random.choice(dosen_df['id']))
        jenis = np.random.choice(["Penelitian","Pengabdian","Publikasi","Pengajaran"])
        judul = f"{jenis} - Kegiatan Contoh {i}"
        tanggal_submit = now + timedelta(days=int(np.random.randint(0,30)))
        status = np.random.choice(["Pending","Approved","Rejected"], p=[0.6,0.25,0.15])
        verif_rows.append({
            "id": int(i),
            "dosen_id": dosen_id,
            "jenis": jenis,
            "judul": judul,
            "tanggal_submit": tanggal_submit.date(),
            "status": status,
            "keterangan": "" if status=="Pending" else ("Disetujui" if status=="Approved" else "Dokumentasi tidak lengkap")
        })

    verification_df = pd.DataFrame(verif_rows)

    # Try saving CSVs if environment allows
    csv_paths = {}
    try:
        dosen_csv = "/mnt/data/dummy_dosen_20.csv"
        perf_csv = "/mnt/data/dummy_performance_20x12.csv"
        verif_csv = "/mnt/data/dummy_verification_queue.csv"
        dosen_df.to_csv(dosen_csv, index=False)
        performance_df.to_csv(perf_csv, index=False)
        verification_df.to_csv(verif_csv, index=False)
        csv_paths = {"dosen": dosen_csv, "performance": perf_csv, "verification": verif_csv}
    except Exception:
        csv_paths = {"dosen": None, "performance": None, "verification": None}

    return dosen_df, performance_df, verification_df, csv_paths

# ---------------- Load / regenerate dummy data into session state ----------------
def load_dummy_to_session(seed: int = 42):
    dosen_df, performance_df, verification_df, csv_paths = generate_dummy_data(seed)
    st.session_state.dosen_data = dosen_df
    st.session_state.performance_data = performance_df
    st.session_state.verification_queue = verification_df
    st.session_state.dummy_csv_paths = csv_paths

# Ensure dummy data exists
if 'dosen_data' not in st.session_state:
    load_dummy_to_session()

# ---------------- User credentials (demo) ----------------
USERS = {
    'dosen1': {
        'password': 'dosen123',
        'role': 'Dosen',
        'name': 'Dr. Dosen 1',
        'id': 1,
        'fakultas': 'Teknik',
        'prodi': 'Informatika'
    },
    'dosen2': {
        'password': 'dosen123',
        'role': 'Dosen',
        'name': 'Dr. Dosen 2',
        'id': 2,
        'fakultas': 'Teknik',
        'prodi': 'Sipil'
    },
    'kaprodi1': {
        'password': 'kaprodi123',
        'role': 'Kaprodi',
        'name': 'Dr. Kaprodi Informatika',
        'id': None,
        'fakultas': 'Teknik',
        'prodi': 'Informatika'
    },
    'dekan1': {
        'password': 'dekan123',
        'role': 'Dekan',
        'name': 'Prof. Dekan Teknik',
        'id': None,
        'fakultas': 'Teknik',
        'prodi': None
    },
    'rektor': {
        'password': 'rektor123',
        'role': 'Rektor',
        'name': 'Prof. Rektor UEU',
        'id': None,
        'fakultas': None,
        'prodi': None
    }
}

# ---------------- UI Pages & Functions ----------------
def rektor_dashboard():
    """Public dashboard shown by default (no login required)."""
    st.markdown("<h1 class='main-header'>🎓 Dashboard Indeks Kinerja Dosen - Universitas</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#666;'>Ringkasan kinerja universitas (tampilan Rektor tanpa login)</p>", unsafe_allow_html=True)

    df = st.session_state.dosen_data
    perf = st.session_state.performance_data

    # Universitas: total dosen per fakultas
    col1, col2, col3 = st.columns([1,1,1])
    with col1:
        fak_counts = df['fakultas'].value_counts().reset_index()
        fak_counts.columns = ['Fakultas','Jumlah Dosen']
        st.markdown("### 📚 Jumlah Dosen per Fakultas")
        st.table(fak_counts)
    with col2:
        # Average angka kredit per dosen (tahun 2024)
        kredit_per_dosen = perf.groupby('dosen_id')['angka_kredit'].sum().reset_index()
        kredit_per_dosen.columns = ['dosen_id','total_kredit']
        avg_kredit = kredit_per_dosen['total_kredit'].mean()
        st.metric("Rata-rata Angka Kredit per Dosen (2024)", f"{avg_kredit:.2f}")
        st.markdown("### 🔢 Statistik Singkat")
        st.write(f"- Total Dosen: **{len(df)}**")
        st.write(f"- Total Entri Kinerja (2024): **{len(perf)}**")
    with col3:
        # Publikasi total dan rata-rata
        pub_per_dosen = perf.groupby('dosen_id')['publikasi'].sum().reset_index()
        total_pub = pub_per_dosen['publikasi'].sum()
        avg_pub = pub_per_dosen['publikasi'].mean()
        st.metric("Total Publikasi (2024)", int(total_pub))
        st.metric("Rata-rata Publikasi per Dosen (2024)", f"{avg_pub:.2f}")

    st.markdown("---")
    # Trend universitas: average angka kredit per bulan
    avg_month = perf.groupby('bulan')['angka_kredit'].mean().reset_index()
    fig = px.line(avg_month, x='bulan', y='angka_kredit', title='Rata-rata Angka Kredit Bulanan (Universitas 2024)', labels={'bulan':'Bulan','angka_kredit':'Rata-rata Angka Kredit'}, markers=True)
    fig.update_layout(height=350)
    st.plotly_chart(fig, use_container_width=True)

    # Table: top 10 dosen by total angka kredit
    kredit_per_dosen = kredit_per_dosen.merge(df[['id','nama','fakultas','prodi']], left_on='dosen_id', right_on='id', how='left')
    top10 = kredit_per_dosen.sort_values('total_kredit', ascending=False).head(10)[['nama','fakultas','prodi','total_kredit']]
    st.markdown("### 🏅 Top 10 Dosen berdasarkan Angka Kredit (2024)")
    st.table(top10)

def login_area_inline():
    """Inline login area shown when user is not logged in (expander)."""
    with st.expander("🔐 Login (untuk Dosen / Kaprodi / Dekan)", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            username = st.text_input("Username", key="login_user")
        with col2:
            password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login", use_container_width=True, type="primary"):
            if username in USERS and USERS[username]['password'] == password:
                st.session_state.logged_in = True
                st.session_state.user_role = USERS[username]['role']
                st.session_state.user_name = USERS[username]['name']
                st.session_state.user_id = USERS[username]['id']
                st.session_state.fakultas = USERS[username]['fakultas']
                st.session_state.prodi = USERS[username]['prodi']
                st.success(f"Selamat datang, {st.session_state.user_name}!")
                st.experimental_rerun()
            else:
                st.error("❌ Username atau password salah!")

def sidebar_common_controls():
    """Sidebar controls visible both when logged in and not logged in."""
    st.sidebar.image("https://via.placeholder.com/150x50/1f77b4/ffffff?text=UEU+DSS", use_container_width=True)
    st.sidebar.markdown("---")

    if st.sidebar.button("🔁 Regenerate Dummy Data (new seed)", use_container_width=True):
        new_seed = np.random.randint(1, 10000)
        load_dummy_to_session(seed=new_seed)
        st.success("Dummy data regenerated.")
        st.experimental_rerun()

    st.sidebar.markdown("### 📥 Download Dummy CSV")
    paths = st.session_state.get('dummy_csv_paths', {})
    if paths.get('dosen'):
        try:
            st.sidebar.download_button("Download Dosen (CSV)", data=open(paths['dosen'], 'rb'), file_name="dummy_dosen_20.csv")
            st.sidebar.download_button("Download Performance (CSV)", data=open(paths['performance'], 'rb'), file_name="dummy_performance_20x12.csv")
            st.sidebar.download_button("Download Verification (CSV)", data=open(paths['verification'], 'rb'), file_name="dummy_verification_queue.csv")
        except Exception:
            st.sidebar.info("CSV tidak dapat dibuka di environment ini.")
    else:
        st.sidebar.info("CSV path tidak tersedia di environment ini.")
    st.sidebar.markdown("---")

def login_page_full():
    """Full login page (used after user clicks login in sidebar menu when already logged out)"""
    st.markdown("<h1 class='main-header'>🎓 Sistem Penunjang Keputusan - Login</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#666;'>Masuk untuk akses Kaprodi / Dekan / Dosen</p>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        username = st.text_input("Username", placeholder="Masukkan username (contoh: dosen1)")
        password = st.text_input("Password", type="password", placeholder="Masukkan password")
        if st.button("Login", use_container_width=True, type="primary"):
            if username in USERS and USERS[username]['password'] == password:
                st.session_state.logged_in = True
                st.session_state.user_role = USERS[username]['role']
                st.session_state.user_name = USERS[username]['name']
                st.session_state.user_id = USERS[username]['id']
                st.session_state.fakultas = USERS[username]['fakultas']
                st.session_state.prodi = USERS[username]['prodi']
                st.success(f"Selamat datang, {st.session_state.user_name}!")
                st.experimental_rerun()
            else:
                st.error("❌ Username atau password salah!")

def sidebar_navigation():
    """Sidebar when user is logged in; returns selected menu."""
    st.sidebar.markdown(f"### 👤 {st.session_state.user_name}")
    st.sidebar.markdown(f"**Role:** {st.session_state.user_role}")
    if st.session_state.fakultas:
        st.sidebar.markdown(f"**Fakultas:** {st.session_state.fakultas}")
    if st.session_state.prodi:
        st.sidebar.markdown(f"**Prodi:** {st.session_state.prodi}")
    st.sidebar.markdown("---")

    # Menu based on role
    if st.session_state.user_role == 'Dosen':
        menu = ["Dashboard", "Profil & Input Kinerja", "Riwayat Penilaian"]
        icons = ["📊", "📝", "📜"]
    elif st.session_state.user_role == 'Kaprodi':
        menu = ["Dashboard", "Verifikasi Data", "Analitik Prodi", "Rekomendasi DSS"]
        icons = ["📊", "✅", "📈", "🤖"]
    elif st.session_state.user_role == 'Dekan':
        menu = ["Dashboard", "Verifikasi Data", "Analitik Fakultas", "Rekomendasi DSS"]
        icons = ["📊", "✅", "📈", "🤖"]
    else:
        menu = ["Dashboard"]
        icons = ["📊"]

    menu_options = [f"{icon} {label}" for icon, label in zip(icons, menu)]
    selected = st.sidebar.radio("Menu Navigasi", menu_options, label_visibility="collapsed")
    selected_menu = selected.split(" ", 1)[1]

    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout", use_container_width=True, type="secondary"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.experimental_rerun()

    return selected_menu

def dosen_dashboard(dosen_data, performance_data):
    st.markdown("## 📊 Dashboard Kinerja Dosen")
    if st.session_state.user_id is None:
        st.error("ID dosen tidak tersedia.")
        return
    dosen_info = dosen_data[dosen_data['id'] == st.session_state.user_id].iloc[0]
    perf_data = performance_data[performance_data['dosen_id'] == st.session_state.user_id]
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown(f"### Selamat datang, {dosen_info['nama']}")
        st.markdown(f"**NIDN:** {dosen_info['nidn']} | **Email:** {dosen_info['email']}")
    with col2:
        st.info(f"**Status:** {dosen_info['status']}")
    with col3:
        st.info(f"**Jabatan:** {dosen_info['jabatan']}")
    st.markdown("---")
    st.markdown("### 📈 Ringkasan Kinerja Tahun 2024")
    col1, col2, col3, col4 = st.columns(4)
    total_sks = int(perf_data['mengajar_sks'].sum())
    total_penelitian = int(perf_data['penelitian'].sum())
    total_pengabdian = int(perf_data['pengabdian'].sum())
    total_publikasi = int(perf_data['publikasi'].sum())
    total_angka_kredit = float(perf_data['angka_kredit'].sum())
    with col1:
        st.metric("Total SKS Mengajar", total_sks, delta=f"+{int(total_sks/12)} avg/bulan")
    with col2:
        st.metric("Penelitian", total_penelitian, delta="kegiatan")
    with col3:
        st.metric("Pengabdian", total_pengabdian, delta="kegiatan")
    with col4:
        st.metric("Publikasi", total_publikasi, delta="artikel")
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 📊 Trend Angka Kredit Bulanan")
        fig = px.line(perf_data, x='bulan', y='angka_kredit', title='Perkembangan Angka Kredit 2024', labels={'bulan': 'Bulan', 'angka_kredit': 'Angka Kredit'}, markers=True)
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
        st.metric("Total Angka Kredit", f"{total_angka_kredit:.2f}")
    with col2:
        st.markdown("### 🎯 Distribusi Aktivitas Tridharma")
        tridharma = pd.DataFrame({
            'Kategori': ['Mengajar (SKS)', 'Penelitian', 'Pengabdian', 'Publikasi'],
            'Jumlah': [total_sks / 10 if total_sks > 0 else 0, total_penelitian, total_pengabdian, total_publikasi]
        })
        fig = px.pie(tridharma, values='Jumlah', names='Kategori', title='Porsi Aktivitas Tridharma')
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    st.markdown("### 📅 Rincian Kinerja Bulanan")
    perf_display = perf_data[['bulan', 'mengajar_sks', 'penelitian', 'pengabdian', 'publikasi', 'angka_kredit']].copy()
    perf_display.columns = ['Bulan', 'SKS Mengajar', 'Penelitian', 'Pengabdian', 'Publikasi', 'Angka Kredit']
    st.dataframe(perf_display, use_container_width=True, hide_index=True)
    st.markdown("### 💡 Rekomendasi Pengembangan")
    avg_penelitian = perf_data['penelitian'].mean()
    avg_publikasi = perf_data['publikasi'].mean()
    if avg_publikasi < 0.5:
        st.warning("⚠️ Produktivitas publikasi dapat ditingkatkan. Pertimbangkan mengikuti workshop penulisan artikel.")
    if avg_penelitian < 0.5:
        st.warning("⚠️ Aktivitas penelitian dapat ditingkatkan. Pertimbangkan bergabung dengan kelompok riset.")
    if avg_publikasi >= 1.0 and avg_penelitian >= 1.0:
        st.success("✅ Kinerja Anda sangat baik! Pertahankan dan tingkatkan terus.")

def dosen_input_kinerja():
    st.markdown("## 📝 Input Kinerja Tridharma")
    st.info("💡 Silakan input data kinerja Tridharma Anda. Data akan diverifikasi oleh Kaprodi/Dekan.")
    tab1, tab2, tab3, tab4 = st.tabs(["📚 Pengajaran", "🔬 Penelitian", "🤝 Pengabdian", "📄 Publikasi"])
    with tab1:
        st.markdown("### Input Data Pengajaran")
        col1, col2 = st.columns(2)
        with col1:
            mata_kuliah = st.text_input("Nama Mata Kuliah", placeholder="Contoh: Sistem Basis Data")
            kelas = st.text_input("Kelas", placeholder="Contoh: A, B, C")
            semester = st.selectbox("Semester", ["Ganjil", "Genap"])
        with col2:
            sks = st.number_input("SKS", min_value=1, max_value=6, value=3)
            jumlah_mahasiswa = st.number_input("Jumlah Mahasiswa", min_value=1, value=30)
            tahun_akademik = st.text_input("Tahun Akademik", value="2024/2025")
        deskripsi_mk = st.text_area("Deskripsi/Catatan", placeholder="Opsional: catatan tambahan tentang mata kuliah ini")
        if st.button("💾 Simpan Data Pengajaran", type="primary", use_container_width=True):
            if mata_kuliah and kelas:
                st.success("✅ Data pengajaran berhasil disimpan!")
                st.balloons()
            else:
                st.error("❌ Nama Mata Kuliah dan Kelas harus diisi!")
    with tab2:
        st.markdown("### Input Data Penelitian")
        judul_penelitian = st.text_input("Judul Penelitian", placeholder="Judul lengkap penelitian")
        col1, col2 = st.columns(2)
        with col1:
            jenis = st.selectbox("Jenis Penelitian", ["Penelitian Mandiri", "Penelitian Kelompok", "Penelitian Hibah Internal","Penelitian Hibah Eksternal (Dikti)","Penelitian Hibah Eksternal (Swasta)"])
            tahun_penelitian = st.number_input("Tahun", min_value=2020, max_value=2025, value=2024)
            skema = st.text_input("Skema/Sumber Dana", placeholder="Contoh: Penelitian Dosen Pemula")
        with col2:
            status = st.selectbox("Status", ["Proposal", "Sedang Berjalan", "Selesai", "Publikasi"])
            dana = st.number_input("Dana Penelitian (Rp)", min_value=0, value=0, step=1000000)
            anggota = st.text_area("Anggota Tim", placeholder="Nama anggota penelitian (pisahkan dengan koma)")
        abstrak = st.text_area("Abstrak/Ringkasan", placeholder="Ringkasan singkat penelitian", height=100)
        file = st.file_uploader("Upload Dokumen Penelitian (PDF)", type=['pdf'])
        if st.button("💾 Simpan Data Penelitian", type="primary", use_container_width=True):
            if judul_penelitian:
                st.success("✅ Data penelitian berhasil disimpan dan menunggu verifikasi Kaprodi!")
                st.info("📧 Notifikasi telah dikirim ke Kaprodi untuk verifikasi.")
            else:
                st.error("❌ Judul penelitian harus diisi!")
    with tab3:
        st.markdown("### Input Data Pengabdian Masyarakat")
        judul_pengabdian = st.text_input("Judul Kegiatan Pengabdian", placeholder="Judul lengkap kegiatan")
        col1, col2 = st.columns(2)
        with col1:
            jenis_pengabdian = st.selectbox("Jenis Kegiatan", ["Penyuluhan","Pelatihan","Pendampingan","Konsultasi","Pemberdayaan Masyarakat"])
            lokasi = st.text_input("Lokasi", placeholder="Tempat pelaksanaan")
            mitra = st.text_input("Mitra/Target", placeholder="Nama kelompok/organisasi mitra")
        with col2:
            tanggal_mulai = st.date_input("Tanggal Mulai")
            tanggal_selesai = st.date_input("Tanggal Selesai")
            peserta = st.number_input("Jumlah Peserta", min_value=1, value=50)
        deskripsi_pengabdian = st.text_area("Deskripsi Kegiatan", placeholder="Jelaskan kegiatan pengabdian", height=100)
        file_pengabdian = st.file_uploader("Upload Dokumentasi (PDF/Foto)", type=['pdf', 'jpg', 'png'])
        if st.button("💾 Simpan Data Pengabdian", type="primary", use_container_width=True):
            if judul_pengabdian:
                st.success("✅ Data pengabdian berhasil disimpan dan menunggu verifikasi Kaprodi!")
                st.info("📧 Notifikasi telah dikirim ke Kaprodi untuk verifikasi.")
            else:
                st.error("❌ Judul kegiatan harus diisi!")
    with tab4:
        st.markdown("### Input Data Publikasi")
        judul_publikasi = st.text_input("Judul Publikasi", placeholder="Judul artikel/paper")
        col1, col2 = st.columns(2)
        with col1:
            jenis_pub = st.selectbox("Jenis Publikasi", ["Jurnal Internasional Bereputasi","Jurnal Internasional","Jurnal Nasional Terakreditasi","Jurnal Nasional","Prosiding Internasional","Prosiding Nasional","Book Chapter","Buku"])
            nama_jurnal = st.text_input("Nama Jurnal/Penerbit", placeholder="Nama jurnal atau penerbit")
            indexing = st.multiselect("Indexing/Akreditasi", ["Scopus","Web of Science","SINTA 1","SINTA 2","SINTA 3","SINTA 4","SINTA 5","SINTA 6"])
        with col2:
            tahun_pub = st.number_input("Tahun Publikasi", min_value=2020, max_value=2025, value=2024)
            volume = st.text_input("Volume/Issue", placeholder="Contoh: Vol. 10 No. 2")
            halaman = st.text_input("Halaman", placeholder="Contoh: 45-60")
        penulis = st.text_area("Daftar Penulis", placeholder="Nama penulis (pisahkan dengan koma)")
        url = st.text_input("URL/DOI", placeholder="Link ke publikasi atau DOI")
        file_pub = st.file_uploader("Upload File Publikasi (PDF)", type=['pdf'], key="pub_file")
        if st.button("💾 Simpan Data Publikasi", type="primary", use_container_width=True):
            if judul_publikasi and nama_jurnal:
                st.success("✅ Data publikasi berhasil disimpan dan menunggu verifikasi Kaprodi!")
                st.info("📧 Notifikasi telah dikirim ke Kaprodi untuk verifikasi.")
            else:
                st.error("❌ Judul dan nama jurnal harus diisi!")

def dosen_riwayat_penilaian(performance_data):
    perf_data = performance_data[performance_data['dosen_id'] == st.session_state.user_id].copy()
    st.markdown("## 📜 Riwayat Penilaian Kinerja")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info(f"**Total Entri Data:** {len(perf_data)}")
    with col2:
        st.info(f"**Periode:** Januari - Desember 2024")
    with col3:
        total_kredit = perf_data['angka_kredit'].sum()
        st.info(f"**Total Angka Kredit:** {total_kredit:.2f}")
    st.markdown("---")
    col1, col2 = st.columns([1,3])
    with col1:
        filter_bulan = st.multiselect("Filter Bulan", options=list(range(1,13)), default=list(range(1,13)))
    filtered_data = perf_data[perf_data['bulan'].isin(filter_bulan)]
    st.markdown("### 📊 Tabel Riwayat Kinerja")
    display_data = filtered_data[['bulan','tahun','mengajar_sks','penelitian','pengabdian','publikasi','angka_kredit']].copy()
    display_data.columns = ['Bulan','Tahun','SKS Mengajar','Penelitian','Pengabdian','Publikasi','Angka Kredit']
    st.dataframe(display_data.style.background_gradient(subset=['Angka Kredit'], cmap='Blues'), use_container_width=True, hide_index=True)
    csv = display_data.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Riwayat (CSV)", data=csv, file_name=f'riwayat_kinerja_{st.session_state.user_id}_2024.csv', mime='text/csv')

def verification_workflow(verification_queue, dosen_data):
    st.markdown("## ✅ Verifikasi & Validasi Data Dosen")
    filtered_data = verification_queue.copy()
    col1, col2, col3, col4 = st.columns(4)
    pending = filtered_data[filtered_data['status'] == 'Pending']
    with col1:
        st.metric("Total Submission", len(filtered_data))
    with col2:
        st.metric("Pending", len(pending), delta=f"{len(pending)} to verify")
    with col3:
        approved = len(filtered_data[filtered_data['status'] == 'Approved'])
        st.metric("Approved", approved)
    with col4:
        rejected = len(filtered_data[filtered_data['status'] == 'Rejected'])
        st.metric("Rejected", rejected)
    st.markdown("---")
    st.markdown(f"### 📋 Antrian Verifikasi ({len(pending)} item)")
    if len(pending) == 0:
        st.success("✅ Tidak ada data yang perlu diverifikasi saat ini.")
    else:
        for idx, row in pending.iterrows():
            dosen_row = dosen_data[dosen_data['id'] == row['dosen_id']].iloc[0]
            dosen_name = dosen_row['nama']
            with st.expander(f"#{row['id']} - {row['jenis']}: {row['judul']} - {dosen_name}", expanded=False):
                col1, col2 = st.columns([3,1])
                with col1:
                    st.markdown(f"**Dosen:** {dosen_name}")
                    st.markdown(f"**NIDN:** {dosen_row['nidn']}")
                    st.markdown(f"**Fakultas/Prodi:** {dosen_row['fakultas']} / {dosen_row['prodi']}")
                    st.markdown(f"**Tanggal Submit:** {pd.to_datetime(row['tanggal_submit']).date()}")
                    st.markdown(f"**Jenis:** {row['jenis']}")
                    st.markdown(f"**Judul:** {row['judul']}")
                    txt_key = f"keterangan_{row['id']}"
                    keterangan = st.text_area("Keterangan Verifikator (opsional)", value=row.get('keterangan',''), key=txt_key)
                with col2:
                    if st.button("✅ Approve", key=f"approve_{row['id']}"):
                        st.session_state.verification_queue.loc[st.session_state.verification_queue['id'] == row['id'], 'status'] = 'Approved'
                        st.session_state.verification_queue.loc[st.session_state.verification_queue['id'] == row['id'], 'keterangan'] = keterangan
                        st.success(f"Submission #{row['id']} disetujui.")
                        st.experimental_rerun()
                    if st.button("❌ Reject", key=f"reject_{row['id']}"):
                        st.session_state.verification_queue.loc[st.session_state.verification_queue['id'] == row['id'], 'status'] = 'Rejected'
                        st.session_state.verification_queue.loc[st.session_state.verification_queue['id'] == row['id'], 'keterangan'] = keterangan or "Dokumentasi tidak lengkap"
                        st.success(f"Submission #{row['id']} ditolak.")
                        st.experimental_rerun()

def kaprodi_dashboard():
    st.markdown("## 📊 Dashboard Kaprodi")
    st.info(f"Menampilkan ringkasan untuk Prodi: **{st.session_state.prodi}**")
    df = st.session_state.dosen_data
    prodi_df = df[df['prodi'] == st.session_state.prodi]
    counts = prodi_df['status'].value_counts().reset_index()
    counts.columns = ['Status', 'Jumlah']
    st.table(counts)

def dekan_dashboard():
    st.markdown("## 📊 Dashboard Dekan")
    st.info(f"Menampilkan ringkasan untuk Fakultas: **{st.session_state.fakultas}**")
    df = st.session_state.dosen_data
    fak_df = df[df['fakultas'] == st.session_state.fakultas]
    counts = fak_df['prodi'].value_counts().reset_index()
    counts.columns = ['Prodi', 'Jumlah Dosen']
    st.table(counts)

# ---------------- Main app routing ----------------
def main():
    # When not logged in: show rektor dashboard and a login expander
    if not st.session_state.logged_in:
        # Sidebar common controls (regen/download)
        sidebar_common_controls()
        # Show rektor dashboard as default public page
        rektor_dashboard()
        # Inline login expander so others can login
        login_area_inline()
        return

    # If logged in: show sidebar navigation and route according to role
    sidebar_common_controls()
    selected_menu = sidebar_navigation()
    role = st.session_state.user_role

    if role == 'Dosen':
        if selected_menu == "Dashboard":
            dosen_dashboard(st.session_state.dosen_data, st.session_state.performance_data)
        elif selected_menu == "Profil & Input Kinerja":
            dosen_input_kinerja()
        elif selected_menu == "Riwayat Penilaian":
            dosen_riwayat_penilaian(st.session_state.performance_data)
        else:
            st.info("Menu belum tersedia.")
    elif role == 'Kaprodi':
        if selected_menu == "Dashboard":
            kaprodi_dashboard()
        elif selected_menu == "Verifikasi Data":
            verification_workflow(st.session_state.verification_queue, st.session_state.dosen_data)
        elif selected_menu == "Analitik Prodi":
            st.markdown("## 📈 Analitik Prodi (Demo)")
            kaprodi_dashboard()
        elif selected_menu == "Rekomendasi DSS":
            st.markdown("## 🤖 Rekomendasi DSS (Demo)")
            st.table(st.session_state.dosen_data.head(10))
        else:
            st.info("Menu belum tersedia.")
    elif role == 'Dekan':
        if selected_menu == "Dashboard":
            dekan_dashboard()
        elif selected_menu == "Verifikasi Data":
            verification_workflow(st.session_state.verification_queue, st.session_state.dosen_data)
        elif selected_menu == "Analitik Fakultas":
            st.markdown("## 📈 Analitik Fakultas (Demo)")
            dekan_dashboard()
        elif selected_menu == "Rekomendasi DSS":
            st.markdown("## 🤖 Rekomendasi DSS (Demo)")
            st.table(st.session_state.dosen_data.head(10))
        else:
            st.info("Menu belum tersedia.")
    else:
        st.info("Role belum dikenali.")

if __name__ == "__main__":
    main()
