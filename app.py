# app.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ---------------- Page config ----------------
st.set_page_config(
    page_title="DSS Penilaian Kinerja Dosen - UEU (With IKD & Explanations)",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- Custom CSS ----------------
st.markdown("""
<style>
    .main-header { font-size: 2.0rem; font-weight: 700; color: #0b5cff; text-align: center; margin-bottom: 0.25rem; }
    .sub-header { text-align:center; color:#666; margin-top:0; margin-bottom:1rem; }
    .metric-card { background-color:#f7f9ff; padding:10px; border-radius:8px; }
    .small-note { font-size:0.9rem; color:#555; }
</style>
""", unsafe_allow_html=True)

# ---------------- Session defaults ----------------
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.user_name = None
    st.session_state.user_id = None
    st.session_state.fakultas = None
    st.session_state.prodi = None

# ---------------- Dummy data generator (with better variance) ----------------
@st.cache_data
def generate_dummy_data(seed: int = 42):
    """
    Generate dummy data with enough variance so not everyone has max scores.
    Reduced probabilities/means for publications/penelitian to create spread.
    """
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
            "status": np.random.choice(["DT","DTT"], p=[0.7,0.3]),
            "jabatan": np.random.choice(["Asisten Ahli","Lektor","Lektor Kepala","Guru Besar"], p=[0.4,0.35,0.2,0.05]),
            "email": f"dosen{id_}@esaunggul.ac.id"
        }
        dosen_list.append(dosen)

    dosen_df = pd.DataFrame(dosen_list)

    # Performance data with controlled variance
    performance_rows = []
    for dosen_id in dosen_df['id']:
        # per-dosen baseline to vary across dosen
        base_sks = np.random.randint(8,14)  # baseline monthly-ish
        base_penelitian_rate = np.random.uniform(0.4,1.2)  # mean for poisson
        base_pengabdian_rate = np.random.uniform(0.2,0.8)
        pub_prob = np.random.uniform(0.05,0.35)  # chance of publication per month

        for bulan in range(1,13):
            row = {
                "dosen_id": int(dosen_id),
                "bulan": int(bulan),
                "tahun": 2024,
                # monthly SKS (so annual ~12x)
                "mengajar_sks": int(max(4, np.random.poisson(base_sks/2) + np.random.randint(0,3))),
                "penelitian": int(np.random.poisson(base_penelitian_rate)),
                "pengabdian": int(np.random.poisson(base_pengabdian_rate)),
                "publikasi": int(np.random.binomial(1, pub_prob)),
                # angka kredit random but correlated with SKS + pub + penelitian
                "angka_kredit": round(max(2.0, np.random.normal(loc=6 + (base_sks/4) + np.random.randint(0,3), scale=2.5)),2)
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

    # Save CSV if possible
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

# ---------------- IKD calculation & utilities ----------------
def hitung_kpi_dosen(perf_df):
    total_sks = float(perf_df['mengajar_sks'].sum())  # yearly approx
    total_penelitian = float(perf_df['penelitian'].sum())
    total_pengabdian = float(perf_df['pengabdian'].sum())
    total_publikasi = float(perf_df['publikasi'].sum())

    skor_mengajar = min((total_sks / 32.0) * 100.0, 100.0)
    skor_penelitian = min((total_penelitian / 2.0) * 100.0, 100.0)
    skor_pengabdian = min((total_pengabdian / 2.0) * 100.0, 100.0)
    skor_publikasi = min((total_publikasi / 2.0) * 100.0, 100.0)

    # Bobot default
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
    rows = []
    for idd in dosen_df['id']:
        perf = performance_df[performance_df['dosen_id'] == idd]
        ikd, comps = hitung_kpi_dosen(perf)
        rows.append({
            "id": int(idd),
            "nama": dosen_df.loc[dosen_df['id'] == idd, 'nama'].values[0],
            "fakultas": dosen_df.loc[dosen_df['id'] == idd, 'fakultas'].values[0],
            "prodi": dosen_df.loc[dosen_df['id'] == idd, 'prodi'].values[0],
            "IKD": ikd,
            "skor_mengajar": comps['mengajar'],
            "skor_penelitian": comps['penelitian'],
            "skor_publikasi": comps['publikasi'],
            "skor_pengabdian": comps['pengabdian']
        })
    return pd.DataFrame(rows)

def klasifikasi_ikd(ikd):
    if ikd >= 85:
        return "Sangat Baik", "green"
    if ikd >= 70:
        return "Baik", "limegreen"
    if ikd >= 55:
        return "Cukup", "orange"
    if ikd >= 40:
        return "Kurang", "orangered"
    return "Tidak Memadai", "red"

def alasan_keputusan(components, ikd):
    """
    Build human-readable reasons for the IKD decision.
    Rules:
      - If a component < threshold, mention it as a reason.
      - If all components high, say 'kinerja sangat baik'.
    """
    reasons = []
    # thresholds to flag items
    if components['mengajar'] < 60:
        reasons.append(f"SKS mengajar rendah ({components['mengajar']:.0f}/100) — periksa beban dan dokumentasi pengajaran.")
    if components['penelitian'] < 50:
        reasons.append(f"Aktivitas penelitian relatif rendah ({components['penelitian']:.0f}/100).")
    if components['publikasi'] < 50:
        reasons.append(f"Produktivitas publikasi rendah ({components['publikasi']:.0f}/100).")
    if components['pengabdian'] < 50:
        reasons.append(f"Kegiatan pengabdian masih minim ({components['pengabdian']:.0f}/100).")

    if not reasons:
        reasons.append("Komponen kinerja berada pada level baik/tinggi; kandidat menunjukkan kinerja yang seimbang antara pengajaran, penelitian, publikasi, dan pengabdian.")
    # Add overall IKD comment
    if ikd >= 85:
        reasons.append("IKD sangat tinggi — potensi untuk penghargaan/promosi.")
    elif ikd >= 70:
        reasons.append("IKD berada di kisaran baik — pertahankan dan tingkatkan khususnya publikasi untuk level lebih tinggi.")
    elif ikd >= 55:
        reasons.append("IKD cukup — perlunya perbaikan terfokus pada penelitian/publikasi atau pengabdian.")
    else:
        reasons.append("IKD rendah — perlu intervensi (pelatihan, pengurangan beban administratif, dukungan riset).")

    return reasons

def rekomendasi_dosen_from_components(components):
    recs = []
    if components['skor_publikasi'] < 50:
        recs.append("Ikut workshop penulisan & perencanaan publikasi, kolaborasi dengan rekan berpublikasi tinggi.")
    if components['skor_penelitian'] < 50:
        recs.append("Dorong partisipasi pada proposal penelitian & kolaborasi riset.")
    if components['skor_pengabdian'] < 50:
        recs.append("Rencanakan minimal 1 kegiatan pengabdian yang terdokumentasi tiap tahun.")
    if components['skor_mengajar'] < 60:
        recs.append("Review beban mengajar & tingkatkan metode pembelajaran (pelatihan pedagogik).")
    if not recs:
        recs.append("Pertahankan kinerja; dokumentasikan hasil untuk kenaikan karir dan penghargaan.")
    return recs

# ---------------- UI helpers ----------------
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

# ---------------- Rektor (public) dashboard with spider & results detail ----------------
def public_rektor_dashboard():
    st.markdown("<h1 class='main-header'>🎓 Dashboard Indeks Kinerja Dosen - Universitas</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Ringkasan Indeks Kinerja Dosen (IKD) — Tampilan Rektor (tanpa login)</p>", unsafe_allow_html=True)

    dosen_df = st.session_state.dosen_data
    perf_df = st.session_state.performance_data

    ikd_df = hitung_ikd_semua(dosen_df, perf_df)
    # classification and color
    ikd_df[['predikat','color']] = ikd_df['IKD'].apply(lambda x: pd.Series(klasifikasi_ikd(x)))

    st.session_state.ikd_df = ikd_df  # store for other pages

    # Top metrics
    col1, col2, col3 = st.columns([1,1,1])
    with col1:
        st.metric("Total Dosen", len(dosen_df))
    with col2:
        st.metric("Rata-rata IKD (2024)", f"{ikd_df['IKD'].mean():.2f}")
    with col3:
        total_pub = perf_df['publikasi'].sum()
        st.metric("Total Publikasi (2024)", int(total_pub))

    st.markdown("---")

    # Spider chart: average components (all) and option to view by fakultas
    st.markdown("### 📡 Radar Chart — Rata-rata Komponen IKD")
    # compute average components
    overall_avg = {
        'Mengajar': ikd_df['skor_mengajar'].mean(),
        'Penelitian': ikd_df['skor_penelitian'].mean(),
        'Publikasi': ikd_df['skor_publikasi'].mean(),
        'Pengabdian': ikd_df['skor_pengabdian'].mean()
    }
    fakultas_options = ["Semua Fakultas"] + sorted(dosen_df['fakultas'].unique().tolist())
    sel_fak = st.selectbox("Tampilkan rata-rata per Fakultas:", fakultas_options, index=0)
    if sel_fak != "Semua Fakultas":
        sub = ikd_df[ikd_df['fakultas'] == sel_fak]
        avg = {
            'Mengajar': sub['skor_mengajar'].mean(),
            'Penelitian': sub['skor_penelitian'].mean(),
            'Publikasi': sub['skor_publikasi'].mean(),
            'Pengabdian': sub['skor_pengabdian'].mean()
        }
    else:
        avg = overall_avg

    categories = list(avg.keys())
    values = list(avg.values())
    # close the loop
    values_loop = values + [values[0]]
    categories_loop = categories + [categories[0]]

    radar = go.Figure()
    radar.add_trace(go.Scatterpolar(r=values_loop, theta=categories_loop, fill='toself', name=f"Rata-rata ({sel_fak})"))
    radar.update_layout(polar=dict(radialaxis=dict(range=[0,100])), showlegend=True, height=420)
    st.plotly_chart(radar, use_container_width=True)

    st.markdown("---")

    # Top 10 table
    st.markdown("### 🏆 Top 10 Dosen (IKD)")
    top10 = ikd_df.sort_values('IKD', ascending=False).head(10)
    top10_display = top10[['nama','fakultas','prodi','IKD','predikat']].copy()
    top10_display['IKD'] = top10_display['IKD'].round(2)
    st.table(top10_display.reset_index(drop=True))

    st.markdown("---")

    # Hasil Penilaian Dosen - full table with detail expandable
    st.markdown("### 🧾 Hasil Penilaian Dosen (Semua)")
    display_df = ikd_df[['id','nama','fakultas','prodi','IKD','predikat']].sort_values('IKD', ascending=False).reset_index(drop=True)
    display_df['IKD'] = display_df['IKD'].round(2)
    # show paginated-ish table
    st.dataframe(display_df, use_container_width=True)

    st.markdown("#### Detail & Alasan Keputusan")
    # allow selecting a specific dosen or list expanders below
    select_mode = st.radio("Lihat detail:", ["Pilih Dosen", "Tampilkan Semua Detail (expander)"], index=0, horizontal=True)

    if select_mode == "Pilih Dosen":
        sel_name = st.selectbox("Pilih Dosen:", display_df['nama'].tolist())
        row = ikd_df[ikd_df['nama'] == sel_name].iloc[0]
        show_dosen_detail_row(row, st.session_state.performance_data)
    else:
        for _, row in ikd_df.sort_values('IKD', ascending=False).iterrows():
            with st.expander(f"{row['nama']} — IKD: {row['IKD']:.2f} — {row.get('predikat','')}"):
                show_dosen_detail_row(row, st.session_state.performance_data)

    st.markdown("---")
    st.markdown("**Catatan:** Alasan keputusan dan rekomendasi bersifat otomatis (aturan dasar). Silakan tinjau dan sesuaikan kebijakan bobot/threshold pada modul IKD untuk kebutuhan institusi.")

def show_dosen_detail_row(row, perf_df):
    """
    Render detail for single dosen row (from ikd_df).
    row: Series with fields id,nama,fakultas,prodi,IKD, skor_*
    """
    dosen_id = int(row['id'])
    st.markdown(f"**Nama:** {row['nama']} — **Fakultas/Prodi:** {row['fakultas']} / {row['prodi']}")
    st.markdown(f"- **IKD:** {row['IKD']:.2f}")
    st.markdown(f"- **Predikat:** {row.get('predikat','')}")
    comps = {
        'mengajar': row['skor_mengajar'],
        'penelitian': row['skor_penelitian'],
        'publikasi': row['skor_publikasi'],
        'pengabdian': row['skor_pengabdian']
    }
    # component table
    comp_df = pd.DataFrame([
        {"Komponen":"Mengajar","Skor":comps['mengajar']},
        {"Komponen":"Penelitian","Skor":comps['penelitian']},
        {"Komponen":"Publikasi","Skor":comps['publikasi']},
        {"Komponen":"Pengabdian","Skor":comps['pengabdian']}
    ])
    st.table(comp_df)

    # radar per dosen
    categories = ["Mengajar","Penelitian","Publikasi","Pengabdian"]
    values = [comps['mengajar'], comps['penelitian'], comps['publikasi'], comps['pengabdian']]
    figr = go.Figure()
    figr.add_trace(go.Scatterpolar(r=values+[values[0]], theta=categories+[categories[0]], fill='toself', name=row['nama']))
    figr.update_layout(polar=dict(radialaxis=dict(range=[0,100])), showlegend=False, height=360)
    st.plotly_chart(figr, use_container_width=True)

    # reasons & recommendations
    reasons = alasan_keputusan(comps, row['IKD'])
    recs = rekomendasi_dosen_from_components({
        'skor_mengajar': comps['mengajar'],
        'skor_penelitian': comps['penelitian'],
        'skor_publikasi': comps['publikasi'],
        'skor_pengabdian': comps['pengabdian']
    })
    st.markdown("**Alasan Keputusan:**")
    for r in reasons:
        st.write(f"- {r}")
    st.markdown("**Rekomendasi:**")
    for r in recs:
        st.info(r)

# ---------------- Other pages (logged-in) ----------------
def sidebar_navigation_logged_in():
    if st.session_state.user_role == 'Dosen':
        menu = ["Dashboard","Profil & Input Kinerja","Riwayat Penilaian"]
        icons = ["📊","📝","📜"]
    elif st.session_state.user_role == 'Kaprodi':
        menu = ["Dashboard","Verifikasi Data","Analitik Prodi","Ranking IKD Prodi"]
        icons = ["📊","✅","📈","🏷"]
    elif st.session_state.user_role == 'Dekan':
        menu = ["Dashboard","Verifikasi Data","Analitik Fakultas","Ranking IKD Fakultas"]
        icons = ["📊","✅","📈","🏷"]
    else:
        menu = ["Dashboard"]
        icons = ["📊"]
    opts = [f"{i} {m}" for i,m in zip(icons,menu)]
    sel = st.sidebar.radio("Menu Navigasi", opts, label_visibility="collapsed")
    return sel.split(" ",1)[1]

def dosen_dashboard():
    dosen_df = st.session_state.dosen_data
    perf_df = st.session_state.performance_data
    if st.session_state.user_id is None:
        st.error("User ID dosen tidak tersedia.")
        return
    dosen_info = dosen_df[dosen_df['id'] == st.session_state.user_id].iloc[0]
    perf = perf_df[perf_df['dosen_id'] == st.session_state.user_id]

    st.markdown(f"## 📊 Dashboard Kinerja — {dosen_info['nama']}")
    ikd, comps = hitung_kpi_dosen(perf)
    predikat, _ = klasifikasi_ikd(ikd)
    st.metric("Indeks Kinerja Dosen (IKD)", f"{ikd}", delta=predikat)
    st.markdown("### Komponen")
    st.table(pd.DataFrame([
        {"Komponen":"Mengajar","Skor":comps['mengajar']},
        {"Komponen":"Penelitian","Skor":comps['penelitian']},
        {"Komponen":"Publikasi","Skor":comps['publikasi']},
        {"Komponen":"Pengabdian","Skor":comps['pengabdian']}
    ]))
    st.markdown("### Rekomendasi & Alasan")
    reasons = alasan_keputusan(comps, ikd)
    recs = rekomendasi_dosen_from_components({
        'skor_mengajar': comps['mengajar'],
        'skor_penelitian': comps['penelitian'],
        'skor_publikasi': comps['publikasi'],
        'skor_pengabdian': comps['pengabdian']
    })
    for r in reasons:
        st.write(f"- {r}")
    for r in recs:
        st.info(r)

def dosen_input_kinerja():
    st.markdown("## 📝 Input Kinerja Tridharma")
    st.info("Form input (demo) — data tidak tersimpan permanen pada versi demo ini.")
    # simplified forms (no persistence)
    tab1,tab2,tab3,tab4 = st.tabs(["Pengajaran","Penelitian","Pengabdian","Publikasi"])
    with tab1:
        st.text_input("Nama Mata Kuliah")
        st.number_input("SKS", min_value=1, max_value=6, value=3)
        if st.button("Simpan Pengajaran"):
            st.success("Data pengajaran disimpan (demo).")
    with tab2:
        st.text_input("Judul Penelitian")
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
    perf_d = perf[perf['dosen_id']==st.session_state.user_id].sort_values(['tahun','bulan'])
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
    st.write(f"Total Antrian: {len(verification_queue)}  |  Pending: {len(pending)}")
    if len(pending)==0:
        st.success("Tidak ada item pending.")
        return
    for _, row in pending.iterrows():
        dosen_row = dosen_df[dosen_df['id'] == row['dosen_id']].iloc[0]
        with st.expander(f"#{row['id']} — {row['jenis']} — {row['judul']} ({dosen_row['nama']})"):
            st.write(f"**Dosen:** {dosen_row['nama']} — {dosen_row['fakultas']} / {dosen_row['prodi']}")
            st.write(f"**Tanggal submit:** {row['tanggal_submit']}")
            k = st.text_area("Keterangan verifikator (opsional)", value=row.get('keterangan',''), key=f"ket_{row['id']}")
            c1,c2 = st.columns(2)
            if c1.button("✅ Approve", key=f"approve_{row['id']}"):
                st.session_state.verification_queue.loc[st.session_state.verification_queue['id']==row['id'],'status'] = 'Approved'
                st.session_state.verification_queue.loc[st.session_state.verification_queue['id']==row['id'],'keterangan'] = k
                st.success("Disetujui"); st.experimental_rerun()
            if c2.button("❌ Reject", key=f"reject_{row['id']}"):
                st.session_state.verification_queue.loc[st.session_state.verification_queue['id']==row['id'],'status'] = 'Rejected'
                st.session_state.verification_queue.loc[st.session_state.verification_queue['id']==row['id'],'keterangan'] = k or "Dokumentasi tidak lengkap"
                st.success("Ditolak"); st.experimental_rerun()

def kaprodi_dashboard():
    prodi = st.session_state.prodi
    if not prodi:
        st.warning("Prodi tidak ditentukan.")
    ikd_df = st.session_state.ikd_df if 'ikd_df' in st.session_state else hitung_ikd_semua(st.session_state.dosen_data, st.session_state.performance_data)
    prodi_df = ikd_df[ikd_df['prodi'] == prodi]
    st.markdown(f"## 📊 Dashboard Kaprodi — {prodi}")
    st.metric("Jumlah Dosen", len(prodi_df))
    st.metric("Rata-rata IKD", f"{prodi_df['IKD'].mean():.2f}")
    st.markdown("### Ranking IKD Prodi")
    st.table(prodi_df.sort_values('IKD', ascending=False)[['nama','IKD','predikat']].reset_index(drop=True))

def dekan_dashboard():
    fak = st.session_state.fakultas
    if not fak:
        st.warning("Fakultas tidak ditentukan.")
    ikd_df = st.session_state.ikd_df if 'ikd_df' in st.session_state else hitung_ikd_semua(st.session_state.dosen_data, st.session_state.performance_data)
    fak_df = ikd_df[ikd_df['fakultas'] == fak]
    st.markdown(f"## 📊 Dashboard Dekan — {fak}")
    st.metric("Jumlah Dosen (Fakultas)", len(fak_df))
    st.metric("Rata-rata IKD (Fakultas)", f"{fak_df['IKD'].mean():.2f}")
    st.markdown("### Rata-rata IKD per Prodi")
    st.table(fak_df.groupby('prodi')['IKD'].mean().reset_index().sort_values('IKD', ascending=False))

# ---------------- Main ----------------
def main():
    # public rektor view when not logged in
    if not st.session_state.logged_in:
        sidebar_common_controls()
        public_rektor_dashboard()
        login_area_inline()
        return

    # logged in
    sidebar_common_controls()
    st.sidebar.image("https://via.placeholder.com/150x50/0b5cff/ffffff?text=UEU+DSS", use_container_width=True)
    if st.session_state.user_role:
        st.sidebar.markdown(f"### 👤 {st.session_state.user_name}")
        st.sidebar.markdown(f"**Role:** {st.session_state.user_role}")
        if st.session_state.fakultas:
            st.sidebar.markdown(f"**Fakultas:** {st.session_state.fakultas}")
        if st.session_state.prodi:
            st.sidebar.markdown(f"**Prodi:** {st.session_state.prodi}")
        st.sidebar.markdown("---")
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
            kaprodi_dashboard()
        elif selected_menu == "Ranking IKD Prodi":
            kaprodi_dashboard()
        else:
            st.info("Menu belum tersedia.")
    elif role == 'Dekan':
        if selected_menu == "Dashboard":
            dekan_dashboard()
        elif selected_menu == "Verifikasi Data":
            verification_page()
        elif selected_menu == "Analitik Fakultas":
            dekan_dashboard()
        elif selected_menu == "Ranking IKD Fakultas":
            dekan_dashboard()
        else:
            st.info("Menu belum tersedia.")
    else:
        st.info("Role belum dikenali.")

if __name__ == "__main__":
    main()
