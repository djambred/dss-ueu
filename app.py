# app.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ---------------- Page config ----------------
st.set_page_config(
    page_title="DSS Penilaian Kinerja Dosen - UEU (With IKD)",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- Custom CSS ----------------
st.markdown("""
<style>
    .main-header {
        font-size: 2.0rem;
        font-weight: 700;
        color: #0b5cff;
        text-align: center;
        margin-bottom: 0.25rem;
    }
    .sub-header {
        text-align:center;
        color:#666;
        margin-top:0;
        margin-bottom:1rem;
    }
    .metric-card { background-color:#f7f9ff; padding:10px; border-radius:8px; }
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

def load_dummy_to_session(seed: int = 42):
    dosen_df, performance_df, verification_df, csv_paths = generate_dummy_data(seed)
    st.session_state.dosen_data = dosen_df
    st.session_state.performance_data = performance_df
    st.session_state.verification_queue = verification_df
    st.session_state.dummy_csv_paths = csv_paths

if 'dosen_data' not in st.session_state:
    load_dummy_to_session()

# ---------------- Demo users ----------------
USERS = {
    'dosen1': {'password': 'dosen123','role': 'Dosen','name': 'Dr. Dosen 1','id': 1,'fakultas':'Teknik','prodi':'Informatika'},
    'dosen2': {'password': 'dosen123','role': 'Dosen','name': 'Dr. Dosen 2','id': 2,'fakultas':'Teknik','prodi':'Sipil'},
    'kaprodi1': {'password': 'kaprodi123','role': 'Kaprodi','name': 'Dr. Kaprodi Informatika','id': None,'fakultas':'Teknik','prodi':'Informatika'},
    'dekan1': {'password': 'dekan123','role': 'Dekan','name': 'Prof. Dekan Teknik','id': None,'fakultas':'Teknik','prodi': None},
}

# ---------------- IKD Calculation Functions ----------------
def hitung_kpi_dosen(perf_df):
    """
    Input: performance data subset untuk 1 dosen (12 bulan)
    Output: IKD (0-100) dan komponen (mengajar, penelitian, publikasi, pengabdian) dalam 0-100
    Default bobot:
        mengajar: 40%
        penelitian: 25%
        publikasi: 25%
        pengabdian: 10%
    Normalisasi menggunakan aturan dari desain:
    - Mengajar: target 32 SKS/tahun -> skor = min((sks/32)*100, 100)
    - Penelitian: target 2 kegiatan -> skor = min((penelitian/2)*100, 100)
    - Publikasi: target 2 artikel -> skor = min((publikasi/2)*100, 100)
    - Pengabdian: target 2 kegiatan -> skor = min((pengabdian/2)*100, 100)
    """
    total_sks = float(perf_df['mengajar_sks'].sum())
    total_penelitian = float(perf_df['penelitian'].sum())
    total_pengabdian = float(perf_df['pengabdian'].sum())
    total_publikasi = float(perf_df['publikasi'].sum())

    skor_mengajar = min((total_sks / 32.0) * 100.0, 100.0)
    skor_penelitian = min((total_penelitian / 2.0) * 100.0, 100.0)
    skor_pengabdian = min((total_pengabdian / 2.0) * 100.0, 100.0)
    skor_publikasi = min((total_publikasi / 2.0) * 100.0, 100.0)

    # Bobot default (bisa disesuaikan)
    b_mengajar = 0.40
    b_penelitian = 0.25
    b_publikasi = 0.25
    b_pengabdian = 0.10

    IKD = (b_mengajar * skor_mengajar +
           b_penelitian * skor_penelitian +
           b_publikasi * skor_publikasi +
           b_pengabdian * skor_pengabdian)

    components = {
        "mengajar": round(skor_mengajar,2),
        "penelitian": round(skor_penelitian,2),
        "publikasi": round(skor_publikasi,2),
        "pengabdian": round(skor_pengabdian,2)
    }
    return round(IKD,2), components

@st.cache_data
def hitung_ikd_semua(dosen_df, performance_df):
    """Menghitung IKD untuk semua dosen dan mengembalikan DataFrame hasil."""
    hasil = []
    for idd in dosen_df['id']:
        perf = performance_df[performance_df['dosen_id'] == idd]
        ikd, comps = hitung_kpi_dosen(perf)
        row = {
            "id": int(idd),
            "nama": dosen_df.loc[dosen_df['id']==idd,'nama'].values[0],
            "fakultas": dosen_df.loc[dosen_df['id']==idd,'fakultas'].values[0],
            "prodi": dosen_df.loc[dosen_df['id']==idd,'prodi'].values[0],
            "IKD": ikd,
            "skor_mengajar": comps['mengajar'],
            "skor_penelitian": comps['penelitian'],
            "skor_publikasi": comps['publikasi'],
            "skor_pengabdian": comps['pengabdian']
        }
        hasil.append(row)
    df = pd.DataFrame(hasil)
    return df

def klasifikasi_ikd(ikd):
    """Klasifikasi IKD menjadi label & warna."""
    if ikd >= 85:
        return "Sangat Baik", "green"
    if ikd >= 70:
        return "Baik", "limegreen"
    if ikd >= 55:
        return "Cukup", "orange"
    if ikd >= 40:
        return "Kurang", "orangered"
    return "Tidak Memadai", "red"

def rekomendasi_dosen(components):
    """Rekomendasi sederhana berdasarkan nilai komponen."""
    rekom = []
    if components['skor_publikasi'] < 50:
        rekom.append("Tingkatkan publikasi: ikuti workshop penulisan & submit ke jurnal bereputasi.")
    if components['skor_penelitian'] < 50:
        rekom.append("Fokus pada kegiatan penelitian — pertimbangkan kolaborasi riset.")
    if components['skor_pengabdian'] < 50:
        rekom.append("Tambah kegiatan pengabdian minimal 1-2 kegiatan per tahun.")
    if components['skor_mengajar'] < 60:
        rekom.append("Evaluasi beban mengajar dan kualitas pedagogi; pertimbangkan peningkatan metode pembelajaran.")
    if not rekom:
        rekom.append("Kinerja baik — pertahankan dan dokumentasikan kegiatan untuk kenaikan karir.")
    return rekom

# ---------------- UI Components ----------------
def sidebar_common_controls():
    st.sidebar.image("https://via.placeholder.com/150x50/0b5cff/ffffff?text=UEU+DSS", use_container_width=True)
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
            st.sidebar.download_button("Dosen (CSV)", data=open(paths['dosen'],'rb'), file_name="dummy_dosen_20.csv")
            st.sidebar.download_button("Performance (CSV)", data=open(paths['performance'],'rb'), file_name="dummy_performance_20x12.csv")
            st.sidebar.download_button("Verification (CSV)", data=open(paths['verification'],'rb'), file_name="dummy_verification_queue.csv")
        except Exception:
            st.sidebar.info("CSV tidak tersedia di environment ini.")
    else:
        st.sidebar.info("CSV path tidak tersedia di environment ini.")
    st.sidebar.markdown("---")

def login_area_inline():
    with st.expander("🔐 Login (Dosen / Kaprodi / Dekan)", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            username = st.text_input("Username", key="login_user")
        with col2:
            password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login", use_container_width=True):
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
                st.error("Username atau password salah.")

def public_rektor_dashboard():
    """Dashboard publik untuk Rektor (default sebelum login)."""
    st.markdown("<h1 class='main-header'>🎓 Dashboard Indeks Kinerja Dosen - Universitas</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Ringkasan Indeks Kinerja Dosen (IKD) — Tampilan Rektor (tanpa login)</p>", unsafe_allow_html=True)

    dosen_df = st.session_state.dosen_data
    perf_df = st.session_state.performance_data

    ikd_df = hitung_ikd_semua(dosen_df, perf_df)
    # store for reuse
    st.session_state.ikd_df = ikd_df

    # Summary metrics
    col1, col2, col3 = st.columns([1,1,1])
    with col1:
        st.metric("Total Dosen", len(dosen_df))
    with col2:
        avg_ikd = ikd_df['IKD'].mean()
        st.metric("Rata-rata IKD (2024)", f"{avg_ikd:.2f}")
    with col3:
        total_pub = perf_df.groupby('dosen_id')['publikasi'].sum().sum()
        st.metric("Total Publikasi (2024)", int(total_pub))

    st.markdown("---")

    # Top 10 IKD
    st.markdown("### 🏆 Top 10 Dosen (IKD)")
    top10 = ikd_df.sort_values('IKD', ascending=False).head(10)
    top10_display = top10[['nama','fakultas','prodi','IKD']].copy()
    top10_display['IKD'] = top10_display['IKD'].round(2)
    st.table(top10_display.reset_index(drop=True))

    # IKD per Fakultas (average)
    st.markdown("### 📊 Rata-rata IKD per Fakultas")
    avg_fak = ikd_df.groupby('fakultas')['IKD'].mean().reset_index().sort_values('IKD', ascending=False)
    fig_fak = px.bar(avg_fak, x='fakultas', y='IKD', text='IKD', labels={'fakultas':'Fakultas','IKD':'Rata-rata IKD'})
    fig_fak.update_layout(height=350)
    st.plotly_chart(fig_fak, use_container_width=True)

    # Heatmap sederhana: IKD by prodi (avg)
    st.markdown("### 🔥 Peta Panas IKD per Prodi")
    prodi_avg = ikd_df.groupby(['fakultas','prodi'])['IKD'].mean().reset_index()
    # pivot for heatmap
    heat = prodi_avg.pivot(index='prodi', columns='fakultas', values='IKD').fillna(0)
    fig_h = go.Figure(data=go.Heatmap(
        z=heat.values,
        x=heat.columns.tolist(),
        y=heat.index.tolist(),
        colorscale='YlOrRd',
        colorbar=dict(title='IKD')
    ))
    fig_h.update_layout(height=450, yaxis=dict(autorange='reversed'))
    st.plotly_chart(fig_h, use_container_width=True)

    st.markdown("---")

    # Trend rata-rata angka kredit bulanan (universitas)
    avg_month = perf_df.groupby('bulan')['angka_kredit'].mean().reset_index()
    fig_line = px.line(avg_month, x='bulan', y='angka_kredit', markers=True, labels={'bulan':'Bulan','angka_kredit':'Avg Angka Kredit'}, title='Rata-rata Angka Kredit Bulanan (Universitas 2024)')
    fig_line.update_layout(height=350)
    st.plotly_chart(fig_line, use_container_width=True)

    st.markdown("---")
    st.markdown("**Catatan:** IKD merupakan skor teragregasi (0-100) dari komponen: mengajar, penelitian, publikasi, dan pengabdian. Gunakan filter dan detail per prodi untuk analisa lebih lanjut diakses melalui login Kaprodi/Dekan.")

def sidebar_when_logged_in():
    st.sidebar.image("https://via.placeholder.com/150x50/0b5cff/ffffff?text=UEU+DSS", use_container_width=True)
    st.sidebar.markdown(f"### 👤 {st.session_state.user_name}")
    st.sidebar.markdown(f"**Role:** {st.session_state.user_role}")
    if st.session_state.fakultas:
        st.sidebar.markdown(f"**Fakultas:** {st.session_state.fakultas}")
    if st.session_state.prodi:
        st.sidebar.markdown(f"**Prodi:** {st.session_state.prodi}")
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
            st.sidebar.download_button("Dosen (CSV)", data=open(paths['dosen'],'rb'), file_name="dummy_dosen_20.csv")
            st.sidebar.download_button("Performance (CSV)", data=open(paths['performance'],'rb'), file_name="dummy_performance_20x12.csv")
            st.sidebar.download_button("Verification (CSV)", data=open(paths['verification'],'rb'), file_name="dummy_verification_queue.csv")
        except Exception:
            st.sidebar.info("CSV tidak tersedia di environment ini.")
    else:
        st.sidebar.info("CSV path tidak tersedia di environment ini.")
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.experimental_rerun()

def sidebar_navigation_logged_in():
    # Menu based on role
    if st.session_state.user_role == 'Dosen':
        menu = ["Dashboard", "Profil & Input Kinerja", "Riwayat Penilaian"]
        icons = ["📊","📝","📜"]
    elif st.session_state.user_role == 'Kaprodi':
        menu = ["Dashboard", "Verifikasi Data", "Analitik Prodi", "Ranking IKD Prodi"]
        icons = ["📊","✅","📈","🏷"]
    elif st.session_state.user_role == 'Dekan':
        menu = ["Dashboard", "Verifikasi Data", "Analitik Fakultas", "Ranking IKD Fakultas"]
        icons = ["📊","✅","📈","🏷"]
    else:
        menu = ["Dashboard"]
        icons = ["📊"]

    options = [f"{i} {m}" for i,m in zip(icons,menu)]
    selected = st.sidebar.radio("Menu Navigasi", options, label_visibility="collapsed")
    return selected.split(" ",1)[1]

# ---------------- Pages ----------------
def dosen_dashboard():
    dosen_df = st.session_state.dosen_data
    perf_df = st.session_state.performance_data
    if st.session_state.user_id is None:
        st.error("User ID dosen tidak tersedia.")
        return
    dosen_info = dosen_df[dosen_df['id'] == st.session_state.user_id].iloc[0]
    perf = perf_df[perf_df['dosen_id'] == st.session_state.user_id]

    st.markdown(f"## 📊 Dashboard Kinerja — {dosen_info['nama']}")
    st.markdown(f"**Fakultas:** {dosen_info['fakultas']}  |  **Prodi:** {dosen_info['prodi']}  |  **Jabatan:** {dosen_info['jabatan']}")

    ikd, comps = hitung_kpi_dosen(perf)
    label, color = klasifikasi_ikd(ikd)

    col1, col2, col3 = st.columns([1.5,1,1])
    with col1:
        st.metric("Indeks Kinerja Dosen (IKD)", f"{ikd}", delta=f"{label}")
    with col2:
        st.metric("Total Angka Kredit (2024)", f"{perf['angka_kredit'].sum():.2f}")
    with col3:
        st.metric("Total Publikasi (2024)", int(perf['publikasi'].sum()))

    st.markdown("---")
    st.markdown("### 🔍 Rincian Komponen IKD")
    comp_df = pd.DataFrame([{
        "Komponen": "Mengajar",
        "Skor (0-100)": comps['mengajar']
    },{
        "Komponen": "Penelitian",
        "Skor (0-100)": comps['penelitian']
    },{
        "Komponen": "Publikasi",
        "Skor (0-100)": comps['publikasi']
    },{
        "Komponen": "Pengabdian",
        "Skor (0-100)": comps['pengabdian']
    }])
    st.table(comp_df)

    # Radar chart
    categories = ["Mengajar","Penelitian","Publikasi","Pengabdian"]
    values = [comps['mengajar'], comps['penelitian'], comps['publikasi'], comps['pengabdian']]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=values, theta=categories, fill='toself', name=dosen_info['nama']))
    fig.update_layout(polar=dict(radialaxis=dict(range=[0,100])), showlegend=False, height=400)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 💡 Rekomendasi")
    # supply components with prefixed keys to match expected input
    comp_for_rekom = {
        "skor_mengajar": comps['mengajar'],
        "skor_penelitian": comps['penelitian'],
        "skor_publikasi": comps['publikasi'],
        "skor_pengabdian": comps['pengabdian']
    }
    rekom = rekomendasi_dosen(comp_for_rekom)
    for r in rekom:
        st.info(r)

    st.markdown("---")
    st.markdown("### 📅 Rincian Bulanan (2024)")
    perf_display = perf[['bulan','mengajar_sks','penelitian','pengabdian','publikasi','angka_kredit']].copy()
    perf_display.columns = ['Bulan','SKS Mengajar','Penelitian','Pengabdian','Publikasi','Angka Kredit']
    st.dataframe(perf_display.sort_values('Bulan'), use_container_width=True, hide_index=True)

def dosen_input_kinerja():
    st.markdown("## 📝 Input Kinerja Tridharma")
    st.info("Form input (demo) — data tidak tersimpan permanen pada versi demo ini.")
    tab1, tab2, tab3, tab4 = st.tabs(["📚 Pengajaran", "🔬 Penelitian", "🤝 Pengabdian", "📄 Publikasi"])
    with tab1:
        st.text_input("Nama Mata Kuliah")
        st.text_input("Kelas")
        st.selectbox("Semester", ["Ganjil","Genap"])
        st.number_input("SKS", min_value=1, max_value=6, value=3)
        if st.button("Simpan Pengajaran"):
            st.success("Data pengajaran disimpan (demo).")
    with tab2:
        st.text_input("Judul Penelitian")
        st.selectbox("Status", ["Proposal","Sedang Berjalan","Selesai","Publikasi"])
        if st.button("Simpan Penelitian"):
            st.success("Data penelitian disimpan (demo).")
    with tab3:
        st.text_input("Judul Pengabdian")
        if st.button("Simpan Pengabdian"):
            st.success("Data pengabdian disimpan (demo).")
    with tab4:
        st.text_input("Judul Publikasi")
        if st.button("Simpan Publikasi"):
            st.success("Data publikasi disimpan (demo).")

def dosen_riwayat_penilaian():
    st.markdown("## 📜 Riwayat Penilaian Kinerja")
    perf = st.session_state.performance_data
    if st.session_state.user_id is None:
        st.error("ID dosen tidak tersedia.")
        return
    perf_d = perf[perf['dosen_id']==st.session_state.user_id].copy()
    perf_d = perf_d.sort_values(['tahun','bulan'])
    st.dataframe(perf_d[['tahun','bulan','mengajar_sks','penelitian','pengabdian','publikasi','angka_kredit']].rename(columns={
        'tahun':'Tahun','bulan':'Bulan','mengajar_sks':'SKS','penelitian':'Penelitian','pengabdian':'Pengabdian','publikasi':'Publikasi','angka_kredit':'Angka Kredit'
    }), use_container_width=True, hide_index=True)
    csv = perf_d.to_csv(index=False).encode('utf-8')
    st.download_button("Download (CSV)", data=csv, file_name=f"riwayat_{st.session_state.user_id}.csv")

def verification_page():
    verification_queue = st.session_state.verification_queue
    dosen_df = st.session_state.dosen_data

    st.markdown("## ✅ Verifikasi & Validasi Data Dosen")
    pending = verification_queue[verification_queue['status']=='Pending']
    st.markdown(f"Total Antrian: {len(verification_queue)}  |  Pending: {len(pending)}")

    if len(pending) == 0:
        st.success("Tidak ada item pending.")
        return

    for _, row in pending.iterrows():
        dosen_row = dosen_df[dosen_df['id'] == row['dosen_id']].iloc[0]
        with st.expander(f"#{row['id']} — {row['jenis']} — {row['judul']} ({dosen_row['nama']})"):
            st.write(f"**Dosen:** {dosen_row['nama']} — {dosen_row['fakultas']} / {dosen_row['prodi']}")
            st.write(f"**Tanggal submit:** {row['tanggal_submit']}")
            k = st.text_area("Keterangan verifikator (opsional)", value=row.get('keterangan',''), key=f"ket_{row['id']}")
            col1, col2 = st.columns(2)
            if col1.button("✅ Approve", key=f"approve_{row['id']}"):
                st.session_state.verification_queue.loc[st.session_state.verification_queue['id']==row['id'],'status'] = 'Approved'
                st.session_state.verification_queue.loc[st.session_state.verification_queue['id']==row['id'],'keterangan'] = k
                st.success("Disetujui")
                st.experimental_rerun()
            if col2.button("❌ Reject", key=f"reject_{row['id']}"):
                st.session_state.verification_queue.loc[st.session_state.verification_queue['id']==row['id'],'status'] = 'Rejected'
                st.session_state.verification_queue.loc[st.session_state.verification_queue['id']==row['id'],'keterangan'] = k or "Dokumentasi tidak lengkap"
                st.success("Ditolak")
                st.experimental_rerun()

def kaprodi_dashboard():
    st.markdown("## 📊 Dashboard Kaprodi")
    prodi = st.session_state.prodi
    if not prodi:
        st.warning("Prodi tidak ditentukan pada user demo.")
    ikd_df = st.session_state.ikd_df if 'ikd_df' in st.session_state else hitung_ikd_semua(st.session_state.dosen_data, st.session_state.performance_data)
    prodi_df = ikd_df[ikd_df['prodi'] == prodi]
    st.markdown(f"### Ringkasan Prodi: {prodi}")
    st.metric("Jumlah Dosen", len(prodi_df))
    st.metric("Rata-rata IKD", f"{prodi_df['IKD'].mean():.2f}")
    st.markdown("### Ranking IKD Prodi")
    st.table(prodi_df.sort_values('IKD', ascending=False)[['nama','IKD']].reset_index(drop=True))

def dekan_dashboard():
    st.markdown("## 📊 Dashboard Dekan")
    fak = st.session_state.fakultas
    if not fak:
        st.warning("Fakultas tidak ditentukan pada user demo.")
    ikd_df = st.session_state.ikd_df if 'ikd_df' in st.session_state else hitung_ikd_semua(st.session_state.dosen_data, st.session_state.performance_data)
    fak_df = ikd_df[ikd_df['fakultas'] == fak]
    st.metric("Jumlah Dosen (Fakultas)", len(fak_df))
    st.metric("Rata-rata IKD (Fakultas)", f"{fak_df['IKD'].mean():.2f}")
    st.markdown("### Rata-rata IKD per Prodi")
    st.table(fak_df.groupby('prodi')['IKD'].mean().reset_index().sort_values('IKD', ascending=False))

# ---------------- Main routing ----------------
def main():
    # If not logged in, show public rektor dashboard + inline login
    if not st.session_state.logged_in:
        sidebar_common_controls()
        public_rektor_dashboard()
        login_area_inline()
        return

    # Logged in flows
    sidebar_common_controls()
    # reuse common controls menu when logged in
    selected_menu = sidebar_navigation_logged_in()

    role = st.session_state.user_role

    if role == 'Dosen':
        if selected_menu == "Dashboard":
            dosen_dashboard()
        elif selected_menu == "Profil & Input Kinerja":
            dosen_input_kinerja()
        elif selected_menu == "Riwayat Penilaian":
            dosen_riwayat_penilaian()
        else:
            st.info("Menu belum tersedia.")
    elif role == 'Kaprodi':
        if selected_menu == "Dashboard":
            kaprodi_dashboard()
        elif selected_menu == "Verifikasi Data":
            verification_page()
        elif selected_menu == "Analitik Prodi":
            st.markdown("## 📈 Analitik Prodi (Demo)")
            kaprodi_dashboard()
        elif selected_menu == "Ranking IKD Prodi":
            st.markdown("## 🏷 Ranking IKD Prodi")
            kaprodi_dashboard()
        else:
            st.info("Menu belum tersedia.")
    elif role == 'Dekan':
        if selected_menu == "Dashboard":
            dekan_dashboard()
        elif selected_menu == "Verifikasi Data":
            verification_page()
        elif selected_menu == "Analitik Fakultas":
            st.markdown("## 📈 Analitik Fakultas (Demo)")
            dekan_dashboard()
        elif selected_menu == "Ranking IKD Fakultas":
            st.markdown("## 🏷 Ranking IKD Fakultas")
            dekan_dashboard()
        else:
            st.info("Menu belum tersedia.")
    else:
        st.info("Role belum dikenali.")

if __name__ == "__main__":
    main()
