# app.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

# ---------------- Page config ----------------
st.set_page_config(
    page_title="DSS Penilaian Kinerja Dosen - UEU (Full Integration)",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- Custom CSS ----------------
st.markdown("""
<style>
    .main-header { font-size: 1.9rem; font-weight: 700; color: #0b5cff; text-align: center; margin-bottom: 0.25rem; }
    .sub-header { text-align:center; color:#666; margin-top:0; margin-bottom:1rem; }
    .metric-card { background-color:#f7f9ff; padding:10px; border-radius:8px; }
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

# ---------------- Faculty & Programs (ESA UNGGUL-like) ----------------
FACULTIES_PRODI = {
    "Fakultas Ekonomi dan Bisnis": [
        "Manajemen", "Akuntansi Sektor Bisnis", "Magister Manajemen", "Magister Akuntansi", "Magister Administrasi Publik", "Doktor Ilmu Manajemen"
    ],
    "Fakultas Teknik": [
        "Teknik Industri", "Perencanaan Wilayah & Kota", "Survei dan Pemetaan", "Teknik Sipil", "Teknik Mesin", "Teknik Elektro"
    ],
    "Fakultas Desain & Industri Kreatif": [
        "Desain Komunikasi Visual", "Desain Produk", "Desain Interior"
    ],
    "Fakultas Ilmu-Ilmu Kesehatan": [
        "Kesehatan Masyarakat", "Ilmu Gizi", "Ilmu Keperawatan", "Profesi Ners", "Rekam Medis", "Manajemen Informasi Kesehatan", "Farmasi", "Bioteknologi"
    ],
    "Fakultas Fisioterapi": [
        "Fisioterapi", "Profesi Fisioterapis", "Magister Fisioterapi"
    ],
    "Fakultas Ilmu Komunikasi": [
        "Marketing Communication", "Jurnalistik", "Hubungan Masyarakat", "Broadcasting"
    ],
    "Fakultas Ilmu Komputer": [
        "Teknik Informatika", "Sistem Informasi", "Teknik Informatika (PJJ)", "Magister Ilmu Komputer"
    ],
    "Fakultas Hukum": [
        "Ilmu Hukum", "Magister Ilmu Hukum"
    ],
    "Fakultas Psikologi": [
        "Psikologi"
    ],
    "Fakultas Keguruan dan Ilmu Pendidikan": [
        "Pendidikan Bahasa Inggris", "Pendidikan Guru SD (PGSD)"
    ]
}

# ---------------- Default Research Directions (can be edited via Admin UI) ----------------
DEFAULT_RESEARCH_DIRECTIONS = {
    "University": [
        "Sustainable Development & Urban Resilience",
        "Digital Health & Health Informatics",
        "AI for Social Good",
        "Creative Industry & Cultural Economy"
    ],
    "Fakultas Teknik": [
        "Smart Cities & Infrastructure Resilience",
        "Renewable Energy & Efficiency",
        "Construction Materials & Low-Carbon Tech"
    ],
    "Fakultas Ilmu Komputer": [
        "AI for Health & Education",
        "Cybersecurity & Privacy",
        "Data Science for Public Policy"
    ],
    "Fakultas Ilmu-Ilmu Kesehatan": [
        "Community Health Interventions",
        "Telemedicine & Digital Health",
        "Nutrition & Public Health"
    ],
    "Fakultas Ekonomi dan Bisnis": [
        "Digital Economy & FinTech",
        "SME Resilience & Entrepreneurship",
        "Sustainable Business Models"
    ],
    "Fakultas Desain & Industri Kreatif": [
        "Design for Sustainability",
        "Human-centered Service Design",
        "Digital Creative Technologies"
    ]
}
# store in session so Admin UI can modify at runtime
if 'research_directions' not in st.session_state:
    st.session_state.research_directions = DEFAULT_RESEARCH_DIRECTIONS.copy()

# ---------------- Dummy data generator (with tema column and expertise) ----------------
@st.cache_data
def generate_dummy_data(seed: int = 42):
    np.random.seed(seed)
    faculty_names = list(FACULTIES_PRODI.keys())
    nama_list = [
        "Andi", "Budi", "Citra", "Dewi", "Eka", "Fajar", "Gita", "Hendra", "Indra", "Joko",
        "Kartika", "Lina", "Maya", "Nina", "Oscar", "Putri", "Qori", "Rini", "Sari", "Tono"
    ]
    dosen_list = []
    ids = list(range(1, 21))
    for i, id_ in enumerate(ids, start=1):
        fak = np.random.choice(faculty_names)
        prodi = np.random.choice(FACULTIES_PRODI[fak])
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

    performance_rows = []
    # include optional 'tema' field (None by default)
    for dosen_id in dosen_df['id']:
        base_sks = np.random.randint(8,14)
        base_penelitian_rate = np.random.uniform(0.3,1.2)
        base_pengabdian_rate = np.random.uniform(0.1,0.8)
        pub_prob = np.random.uniform(0.05,0.35)
        for bulan in range(1,13):
            row = {
                "dosen_id": int(dosen_id),
                "bulan": int(bulan),
                "tahun": 2024,
                "mengajar_sks": int(max(3, np.random.poisson(base_sks/2) + np.random.randint(0,3))),
                "penelitian": int(np.random.poisson(base_penelitian_rate)),
                "pengabdian": int(np.random.poisson(base_pengabdian_rate)),
                "publikasi": int(np.random.binomial(1, pub_prob)),
                "angka_kredit": round(max(2.0, np.random.normal(loc=6 + (base_sks/4) + np.random.randint(0,3), scale=2.5)),2),
                "tema": None  # dummy entries not tagged
            }
            performance_rows.append(row)
    performance_df = pd.DataFrame(performance_rows)

    # verification queue includes 'tema' as optional
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
            "keterangan": "" if status=="Pending" else ("Disetujui" if status=="Approved" else "Dokumentasi tidak lengkap"),
            "tema": None
        })
    verification_df = pd.DataFrame(verif_rows)

    # Save CSV if environment supports
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

# ---------------- Utilities: expertise assignment, alignment ----------------
def assign_expertise_to_dosen(dosen_df, seed=42):
    """Assign 1-3 research themes (expertise) to each dosen from faculty or university pool."""
    np.random.seed(seed)
    rd = st.session_state.get('research_directions', DEFAULT_RESEARCH_DIRECTIONS)
    expertise_list = []
    for _, r in dosen_df.iterrows():
        fak = r['fakultas']
        pool = []
        if fak in rd:
            pool += rd[fak]
        pool += rd.get("University", [])
        pool = list(dict.fromkeys(pool))  # unique
        n = np.random.choice([1,1,2])  # mostly 1, some 2
        picks = list(np.random.choice(pool, size=min(n,len(pool)), replace=False))
        expertise_list.append(", ".join(picks))
    dosen_df = dosen_df.copy()
    dosen_df['expertise'] = expertise_list
    return dosen_df

def compute_alignment_for_dosen(dosen_row, perf_df):
    """
    Compute alignment score as percent of research items (penelitian+publikasi)
    that have tema matching dosen expertise or faculty themes.
    For dummy items without tema we simulate tagging (random) to avoid zero alignment bias.
    """
    rd = st.session_state.get('research_directions', DEFAULT_RESEARCH_DIRECTIONS)
    fak = dosen_row['fakultas']
    faculty_pool = rd.get(fak, []) + rd.get("University", [])
    expertise = str(dosen_row.get('expertise', '')).lower().split(", ")
    # count total research items
    total_items = int(perf_df['penelitian'].sum() + perf_df['publikasi'].sum())
    if total_items == 0:
        return 0.0
    match = 0
    rng = np.random.default_rng(dosen_row['id'])
    for _, item in perf_df.iterrows():
        # for each month, if penelitian>0 or publikasi>0, treat each unit as an item (approx)
        count_items = int(item['penelitian'] + item['publikasi'])
        for _ in range(count_items):
            tema = item.get('tema', None)
            if tema and isinstance(tema, str) and tema.strip():
                # explicit tag -> check match
                if tema.lower() in [t.lower() for t in expertise] or tema in faculty_pool:
                    match += 1
            else:
                # simulate tag from pool
                if len(faculty_pool) == 0:
                    # no themes -> cannot match
                    pass
                else:
                    chosen = rng.choice(faculty_pool)
                    if chosen.lower() in [t.lower() for t in expertise]:
                        match += 1
    return round((match / total_items) * 100.0, 2)

# ---------------- IKD & helpers ----------------
def hitung_kpi_dosen(perf_df):
    total_sks = float(perf_df['mengajar_sks'].sum())
    total_penelitian = float(perf_df['penelitian'].sum())
    total_pengabdian = float(perf_df['pengabdian'].sum())
    total_publikasi = float(perf_df['publikasi'].sum())

    skor_mengajar = min((total_sks / 32.0) * 100.0, 100.0)
    skor_penelitian = min((total_penelitian / 2.0) * 100.0, 100.0)
    skor_pengabdian = min((total_pengabdian / 2.0) * 100.0, 100.0)
    skor_publikasi = min((total_publikasi / 2.0) * 100.0, 100.0)

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
    # ensure dosen_df has 'expertise'
    if 'expertise' not in dosen_df.columns:
        dosen_df = assign_expertise_to_dosen(dosen_df)
    for idd in dosen_df['id']:
        perf = performance_df[performance_df['dosen_id'] == idd]
        ikd, comps = hitung_kpi_dosen(perf)
        dosen_row = dosen_df.loc[dosen_df['id'] == idd].iloc[0]
        alignment = compute_alignment_for_dosen(dosen_row, perf)
        rows.append({
            "id": int(idd),
            "nama": dosen_row['nama'],
            "fakultas": dosen_row['fakultas'],
            "prodi": dosen_row['prodi'],
            "IKD": ikd,
            "skor_mengajar": comps['mengajar'],
            "skor_penelitian": comps['penelitian'],
            "skor_publikasi": comps['publikasi'],
            "skor_pengabdian": comps['pengabdian'],
            "expertise": dosen_row.get('expertise', ''),
            "alignment_score": alignment
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

# ---------------- Eligibility & Apresiasi ----------------
def evaluate_status_eligibility(dosen_row, perf_df_year, ikd, components, verification_df=None, thresholds=None):
    default = {
        'ikd_dt': 75.0,
        'publikasi_dt': 60.0,
        'sks_tahunan_dt': 24,
        'ikd_monitor': 55.0,
        'ikd_probation': 40.0
    }
    if thresholds:
        default.update(thresholds)

    reasons = []
    action = 'monitor'
    eligible_DT = False
    total_sks = float(perf_df_year['mengajar_sks'].sum()) if len(perf_df_year) > 0 else 0.0

    has_recent_reject = False
    if verification_df is not None and len(verification_df) > 0:
        try:
            doc = verification_df.copy()
            if 'tanggal_submit' in doc.columns:
                doc['tanggal_submit'] = pd.to_datetime(doc['tanggal_submit'])
                cutoff = pd.Timestamp.now() - pd.Timedelta(days=365)
                recent = doc[(doc['dosen_id'] == dosen_row['id']) & (doc['tanggal_submit'] >= cutoff)]
                if len(recent[recent['status'] == 'Rejected']) > 0:
                    has_recent_reject = True
        except Exception:
            pass

    cond_ikd = ikd >= default['ikd_dt']
    cond_pub = components.get('publikasi', 0) >= default['publikasi_dt']
    cond_sks = total_sks >= default['sks_tahunan_dt']

    if has_recent_reject:
        reasons.append("Terdapat item verifikasi ditolak dalam 12 bulan terakhir.")
    if not cond_ikd:
        reasons.append(f"IKD belum mencapai threshold DT ({ikd:.1f} < {default['ikd_dt']}).")
    if not cond_pub:
        reasons.append(f"Skor publikasi kurang ({components.get('publikasi',0):.0f} < {default['publikasi_dt']}).")
    if not cond_sks:
        reasons.append(f"Total SKS tahunan kurang ({total_sks:.0f} < {default['sks_tahunan_dt']}).")

    if cond_ikd and cond_pub and cond_sks and not has_recent_reject:
        eligible_DT = True
        action = 'recommend_promote'
        recommendation = "Layak dipertimbangkan untuk pengangkatan/kenaikan status (DT)."
    else:
        eligible_DT = False
        if ikd >= default['ikd_monitor']:
            action = 'monitor'
            recommendation = "Perlu pemantauan dan rencana peningkatan (mentoring/dukungan)."
        elif ikd >= default['ikd_probation']:
            action = 'probation'
            recommendation = "Perlu program peningkatan terstruktur (probation plan)."
        else:
            action = 'reject'
            recommendation = "Tidak memenuhi syarat; diperlukan intervensi segera."

    return {
        'eligible_DT': bool(eligible_DT),
        'action': action,
        'recommendation': recommendation,
        'reasons': reasons,
        'total_sks': total_sks
    }

def award_apresiasi(ikd, components, policy=None):
    if policy is None:
        policy = {'gold': 85, 'silver': 75, 'bronze': 70}
    awards = []
    if ikd >= policy['gold']:
        awards.append({'tier':'Gold','label':'Sertifikat Prestasi Tinggi','notes':'Prioritas dana riset & pengurangan beban pengajaran (opsional).'})
    elif ikd >= policy['silver']:
        awards.append({'tier':'Silver','label':'Sertifikat Prestasi','notes':'Prioritas pelatihan & dukungan administrasi publikasi.'})
    elif ikd >= policy['bronze']:
        awards.append({'tier':'Bronze','label':'Penghargaan Kinerja','notes':'Rekomendasi pengembangan lanjutan.'})
    if components.get('publikasi',0) >= 80:
        awards.append({'tier':'PubStar','label':'Publikasi Unggul','notes':'Publikasi berkualitas tinggi — prioritas dana publikasi.'})
    return awards

def display_status_and_apresiasi(dosen_row, perf_df_year, ikd, components, verification_df=None):
    eval_result = evaluate_status_eligibility(dosen_row, perf_df_year, ikd, components, verification_df=verification_df)
    awards = award_apresiasi(ikd, components)

    st.markdown("### 🔖 Evaluasi Kelayakan Status & Apresiasi")
    st.write(f"- **Total SKS (tahun):** {eval_result['total_sks']:.0f}")
    st.write(f"- **Kelayakan DT:** {'Layak' if eval_result['eligible_DT'] else 'Tidak Layak'}")
    st.write(f"- **Rekomendasi aksi:** {eval_result['recommendation']}")
    if eval_result['reasons']:
        st.markdown("**Alasan / Catatan:**")
        for r in eval_result['reasons']:
            st.write(f"- {r}")

    if awards:
        st.markdown("**Apresiasi yang direkomendasikan:**")
        for a in awards:
            st.success(f"{a['tier']}: {a['label']} — {a['notes']}")
    else:
        st.info("Tidak ada apresiasi khusus saat ini. Fokus pada rencana peningkatan.")

# ---------------- Safe regenerate helper ----------------
def _safe_regenerate_dummy():
    try:
        try:
            generate_dummy_data.clear()
            hitung_ikd_semua.clear()
        except Exception:
            pass
        keys_to_remove = ['dosen_data', 'performance_data', 'verification_queue', 'dummy_csv_paths', 'ikd_df']
        for k in keys_to_remove:
            if k in st.session_state:
                del st.session_state[k]
        new_seed = np.random.randint(1, 1000000)
        load_dummy_to_session(seed=new_seed)
        st.success(f"✅ Dummy data regenerated (seed: {new_seed}).")
        st.experimental_rerun()
    except Exception as e:
        st.error(f"Gagal meregenerasi dummy data: {e}")

# ---------------- Loader into session (assign expertise) ----------------
def load_dummy_to_session(seed: int = 42):
    dosen_df, performance_df, verification_df, csv_paths = generate_dummy_data(seed)
    # assign expertise based on session research directions
    dosen_df = assign_expertise_to_dosen(dosen_df, seed=seed)
    st.session_state.dosen_data = dosen_df
    st.session_state.performance_data = performance_df
    st.session_state.verification_queue = verification_df
    st.session_state.dummy_csv_paths = csv_paths

# ensure data exists
if 'dosen_data' not in st.session_state:
    load_dummy_to_session()

# ---------------- Demo users ----------------
USERS = {
    'dosen1': {'password': 'dosen123','role': 'Dosen','name': 'Dr. Dosen 1','id': 1,'fakultas':'Fakultas Teknik','prodi':'Teknik Informatika'},
    'dosen2': {'password': 'dosen123','role': 'Dosen','name': 'Dr. Dosen 2','id': 2,'fakultas':'Fakultas Teknik','prodi':'Teknik Sipil'},
    'kaprodi1': {'password': 'kaprodi123','role': 'Kaprodi','name': 'Dr. Kaprodi Informatika','id': None,'fakultas':'Fakultas Ilmu Komputer','prodi':'Teknik Informatika'},
    'dekan1': {'password': 'dekan123','role': 'Dekan','name': 'Prof. Dekan Teknik','id': None,'fakultas':'Fakultas Teknik','prodi': None},
    # Admin account for theme management (optional)
    'admin': {'password': 'admin123','role': 'Admin','name': 'Administrator','id': None,'fakultas':None,'prodi': None}
}

# ---------------- Sidebar common controls ----------------
def sidebar_common_controls():
    st.sidebar.image("https://via.placeholder.com/150x50/0b5cff/ffffff?text=UEU+DSS", use_container_width=True)
    st.sidebar.markdown("---")
    if st.sidebar.button("🔁 Regenerate Dummy Data (new seed)", use_container_width=True):
        _safe_regenerate_dummy()
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

# ---------------- Login area ----------------
def login_area_inline():
    with st.expander("🔐 Login (Dosen / Kaprodi / Dekan / Admin)", expanded=False):
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

# ---------------- Rektor public dashboard & detail (with theme filter) ----------------
def show_dosen_detail_row(row, perf_df):
    dosen_id = int(row['id'])
    st.markdown(f"**Nama:** {row['nama']} — **Fakultas/Prodi:** {row['fakultas']} / {row['prodi']}")
    st.markdown(f"- **IKD:** {row['IKD']:.2f}  |  **Alignment:** {row.get('alignment_score',0)}%")
    st.markdown(f"- **Predikat:** {row.get('predikat','')}")
    st.markdown(f"- **Expertise:** {row.get('expertise','')}")
    comps = {
        'mengajar': row['skor_mengajar'],
        'penelitian': row['skor_penelitian'],
        'publikasi': row['skor_publikasi'],
        'pengabdian': row['skor_pengabdian']
    }
    comp_df = pd.DataFrame([
        {"Komponen":"Mengajar","Skor":comps['mengajar']},
        {"Komponen":"Penelitian","Skor":comps['penelitian']},
        {"Komponen":"Publikasi","Skor":comps['publikasi']},
        {"Komponen":"Pengabdian","Skor":comps['pengabdian']}
    ])
    st.table(comp_df)
    categories = ["Mengajar","Penelitian","Publikasi","Pengabdian"]
    values = [comps['mengajar'], comps['penelitian'], comps['publikasi'], comps['pengabdian']]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=values+[values[0]], theta=categories+[categories[0]], fill='toself', name=row['nama']))
    fig.update_layout(polar=dict(radialaxis=dict(range=[0,100])), showlegend=False, height=360)
    st.plotly_chart(fig, use_container_width=True)

    perf_year = st.session_state.performance_data[st.session_state.performance_data['dosen_id']==dosen_id]
    display_status_and_apresiasi(row, perf_year, row['IKD'], comps, verification_df=st.session_state.get('verification_queue'))

def public_rektor_dashboard():
    st.markdown("<h1 class='main-header'>🎓 Dashboard Indeks Kinerja Dosen - Universitas</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Ringkasan IKD — Tampilan Rektor (tanpa login)</p>", unsafe_allow_html=True)

    dosen_df = st.session_state.dosen_data
    perf_df = st.session_state.performance_data
    rd = st.session_state.get('research_directions', DEFAULT_RESEARCH_DIRECTIONS)

    ikd_df = hitung_ikd_semua(dosen_df, perf_df)
    ikd_df[['predikat','color']] = ikd_df['IKD'].apply(lambda x: pd.Series(klasifikasi_ikd(x)))
    st.session_state.ikd_df = ikd_df

    # basic metrics
    col1, col2, col3 = st.columns([1,1,1])
    with col1:
        st.metric("Total Dosen", len(dosen_df))
    with col2:
        st.metric("Rata-rata IKD (2024)", f"{ikd_df['IKD'].mean():.2f}")
    with col3:
        total_pub = perf_df['publikasi'].sum()
        st.metric("Total Publikasi (2024)", int(total_pub))

    st.markdown("---")

    # Eligibility summary
    verification_df = st.session_state.get('verification_queue', pd.DataFrame())
    statuses = []
    for _, r in ikd_df.iterrows():
        perf_year = perf_df[perf_df['dosen_id'] == r['id']]
        comps = {'publikasi': r['skor_publikasi'], 'penelitian': r['skor_penelitian'], 'pengabdian': r['skor_pengabdian'], 'mengajar': r['skor_mengajar']}
        eval_res = evaluate_status_eligibility(r, perf_year, r['IKD'], comps, verification_df=verification_df)
        statuses.append(eval_res['action'])
    status_counts = pd.Series(statuses).value_counts().to_dict()
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Jumlah Layak DT (rekomendasi)", status_counts.get('recommend_promote',0))
    with col2:
        st.metric("Perlu Pemantauan", status_counts.get('monitor',0))
    with col3:
        st.metric("Probation", status_counts.get('probation',0))
    with col4:
        st.metric("Intervensi (reject)", status_counts.get('reject',0))

    st.markdown("---")

    # Radar (choose faculty)
    st.markdown("### 📡 Radar Chart — Rata-rata Komponen IKD")
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
    values = [0 if pd.isna(v) else v for v in avg.values()]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=values+[values[0]], theta=categories+[categories[0]], fill='toself', name=f"Rata-rata ({sel_fak})"))
    fig.update_layout(polar=dict(radialaxis=dict(range=[0,100])), showlegend=True, height=420)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # theme filter & top contributors
    st.markdown("### 🔎 Analisis Tema Riset")
    uni_themes = rd.get("University", [])
    fak_themes = []
    if sel_fak != "Semua Fakultas":
        fak_themes = rd.get(sel_fak, [])
    theme_options = ["Semua Tema"] + uni_themes + fak_themes
    theme_sel = st.selectbox("Filter berdasarkan Tema Riset:", theme_options)
    if theme_sel and theme_sel != "Semua Tema":
        filtered = ikd_df[ikd_df['expertise'].str.contains(theme_sel, case=False, na=False)]
        st.markdown(f"Top kontributor untuk tema: **{theme_sel}** (berdasarkan alignment & IKD)")
        if len(filtered) == 0:
            st.info("Tidak ada dosen dengan expertise terdaftar pada tema ini (atau belum ada tag).")
        else:
            filtered = filtered.sort_values(['alignment_score','IKD'], ascending=[False, False]).head(10)
            st.table(filtered[['nama','fakultas','prodi','IKD','alignment_score','expertise']].reset_index(drop=True))
    else:
        st.info("Pilih tema untuk melihat top kontributor per tema.")

    st.markdown("---")
    st.markdown("### 🏆 Top 10 Dosen (IKD)")
    top10 = ikd_df.sort_values('IKD', ascending=False).head(10)
    top10_display = top10[['nama','fakultas','prodi','IKD','predikat','alignment_score']].copy()
    top10_display['IKD'] = top10_display['IKD'].round(2)
    st.table(top10_display.reset_index(drop=True))

    st.markdown("---")
    st.markdown("### 🧾 Hasil Penilaian Dosen (Semua)")
    display_df = ikd_df[['id','nama','fakultas','prodi','IKD','alignment_score','predikat']].sort_values('IKD', ascending=False).reset_index(drop=True)
    display_df['IKD'] = display_df['IKD'].round(2)
    st.dataframe(display_df, use_container_width=True)

    st.markdown("#### Detail & Alasan Keputusan")
    select_mode = st.radio("Lihat detail:", ["Pilih Dosen", "Tampilkan Semua Detail (expander)"], index=0, horizontal=True)
    if select_mode == "Pilih Dosen":
        sel_name = st.selectbox("Pilih Dosen:", display_df['nama'].tolist())
        row = ikd_df[ikd_df['nama'] == sel_name].iloc[0]
        show_dosen_detail_row(row, perf_df)
    else:
        for _, row in ikd_df.sort_values('IKD', ascending=False).iterrows():
            with st.expander(f"{row['nama']} — IKD: {row['IKD']:.2f} — {row.get('predikat','')}"):
                show_dosen_detail_row(row, perf_df)

    st.markdown("---")
    st.markdown("**Catatan:** Theme alignment dihitung berdasarkan tag tema di data penelitian/publikasi atau (untuk dummy) simulasi tagging. Untuk produksi, minta dosen memilih tema saat submit penelitian/publikasi.")

# ---------------- Logged-in navigation helpers ----------------
def sidebar_navigation_logged_in():
    if st.session_state.user_role == 'Dosen':
        menu = ["Dashboard","Profil & Input Kinerja","Riwayat Penilaian"]
        icons = ["📊","📝","📜"]
    elif st.session_state.user_role == 'Kaprodi':
        menu = ["Dashboard","Verifikasi Data","Analitik Prodi","Manage Themes"]
        icons = ["📊","✅","📈","⚙️"]
    elif st.session_state.user_role == 'Dekan':
        menu = ["Dashboard","Verifikasi Data","Analitik Fakultas","Manage Themes"]
        icons = ["📊","✅","📈","⚙️"]
    elif st.session_state.user_role == 'Admin':
        menu = ["Dashboard","Manage Themes","Export Evaluations"]
        icons = ["📊","⚙️","📁"]
    else:
        menu = ["Dashboard"]
        icons = ["📊"]
    opts = [f"{i} {m}" for i,m in zip(icons,menu)]
    sel = st.sidebar.radio("Menu Navigasi", opts, label_visibility="collapsed")
    return sel.split(" ",1)[1]

# ---------------- Dosen pages (input now supports tema) ----------------
def dosen_dashboard():
    dosen_df = st.session_state.dosen_data
    perf_df = st.session_state.performance_data
    if st.session_state.user_id is None:
        st.error("User ID dosen tidak tersedia."); return
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
    st.markdown("### Expertises")
    st.write(dosen_info.get('expertise','-'))
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
    perf_year = perf_df[perf_df['dosen_id']==st.session_state.user_id]
    display_status_and_apresiasi(dosen_info, perf_year, ikd, comps, verification_df=st.session_state.get('verification_queue'))

def dosen_input_kinerja():
    st.markdown("## 📝 Input Kinerja Tridharma (Penelitian / Publikasi / Pengabdian)")
    st.info("Data demo — akan ditambahkan ke performance_data & verification_queue (status: Pending).")
    tab = st.tabs(["Input Kegiatan"])[0]
    with tab:
        jenis = st.selectbox("Jenis Kegiatan", ["Penelitian","Pengabdian","Publikasi","Pengajaran"])
        judul = st.text_input("Judul Kegiatan")
        tahun = st.number_input("Tahun", min_value=2020, max_value=2030, value=2024)
        # tema selection from research_directions (university + faculty)
        rd = st.session_state.get('research_directions', DEFAULT_RESEARCH_DIRECTIONS)
        fakultas = st.session_state.fakultas or st.session_state.dosen_data.loc[st.session_state.dosen_data['id']==st.session_state.user_id,'fakultas'].values[0]
        themes = rd.get(fakultas, []) + rd.get("University", [])
        tema = st.selectbox("Tema Riset (pilih yang relevan)", ["(tidak ditentukan)"] + themes)
        dana = st.number_input("Dana (Rp) - opsional", min_value=0, value=0, step=1000000)
        fileu = st.file_uploader("Lampiran (opsional PDF/JPG/PNG)", type=['pdf','jpg','png'])
        if st.button("💾 Simpan Kegiatan"):
            if not judul:
                st.error("Judul harus diisi.")
            else:
                # append to performance_data as 1 unit (demo). We'll add 1 publikasi/penelitian/pengabdian entry in current month
                new_id = st.session_state.user_id
                month = datetime.now().month
                # create a new row (copy structure)
                new_row = {
                    "dosen_id": new_id,
                    "bulan": month,
                    "tahun": tahun,
                    "mengajar_sks": 0,
                    "penelitian": 1 if jenis=="Penelitian" else 0,
                    "pengabdian": 1 if jenis=="Pengabdian" else 0,
                    "publikasi": 1 if jenis=="Publikasi" else 0,
                    "angka_kredit": 0.0,
                    "tema": None if tema == "(tidak ditentukan)" else tema
                }
                # append
                st.session_state.performance_data = pd.concat([st.session_state.performance_data, pd.DataFrame([new_row])], ignore_index=True)
                # add to verification queue
                vq = st.session_state.verification_queue
                new_v = {
                    "id": int(vq['id'].max() + 1) if len(vq)>0 else 1,
                    "dosen_id": new_id,
                    "jenis": jenis,
                    "judul": judul,
                    "tanggal_submit": datetime.now().date(),
                    "status": "Pending",
                    "keterangan": "",
                    "tema": None if tema == "(tidak ditentukan)" else tema
                }
                st.session_state.verification_queue = pd.concat([vq, pd.DataFrame([new_v])], ignore_index=True)
                st.success("Kegiatan disimpan dan menunggu verifikasi (demo).")

def dosen_riwayat_penilaian():
    st.markdown("## 📜 Riwayat Penilaian Kinerja")
    perf = st.session_state.performance_data
    if st.session_state.user_id is None:
        st.error("ID dosen tidak tersedia."); return
    perf_d = perf[perf['dosen_id']==st.session_state.user_id].sort_values(['tahun','bulan'])
    st.dataframe(perf_d[['tahun','bulan','mengajar_sks','penelitian','pengabdian','publikasi','angka_kredit','tema']].rename(columns={
        'tahun':'Tahun','bulan':'Bulan','mengajar_sks':'SKS','penelitian':'Penelitian','pengabdian':'Pengabdian','publikasi':'Publikasi','angka_kredit':'Angka Kredit'
    }), use_container_width=True, hide_index=True)
    csv = perf_d.to_csv(index=False).encode('utf-8')
    st.download_button("Download (CSV)", data=csv, file_name=f"riwayat_{st.session_state.user_id}.csv")

# ---------------- Verifikasi & theme management pages ----------------
def verification_page():
    verification_queue = st.session_state.verification_queue
    dosen_df = st.session_state.dosen_data
    st.markdown("## ✅ Verifikasi & Validasi Data Dosen")
    pending = verification_queue[verification_queue['status']=='Pending']
    st.write(f"Total Antrian: {len(verification_queue)}  |  Pending: {len(pending)}")
    if len(pending)==0:
        st.success("Tidak ada item pending."); return
    for _, row in pending.iterrows():
        dosen_row = dosen_df[dosen_df['id'] == row['dosen_id']].iloc[0]
        with st.expander(f"#{row['id']} — {row['jenis']} — {row['judul']} ({dosen_row['nama']})"):
            st.write(f"**Dosen:** {dosen_row['nama']} — {dosen_row['fakultas']} / {dosen_row['prodi']}")
            st.write(f"**Tanggal submit:** {row['tanggal_submit']}")
            st.write(f"**Tema (klaim):** {row.get('tema', None)}")
            k = st.text_area("Keterangan verifikator (opsional)", value=row.get('keterangan',''), key=f"ket_{row['id']}")
            c1,c2 = st.columns(2)
            if c1.button("✅ Approve", key=f"approve_{row['id']}"):
                st.session_state.verification_queue.loc[st.session_state.verification_queue['id']==row['id'],'status'] = 'Approved'
                st.session_state.verification_queue.loc[st.session_state.verification_queue['id']==row['id'],'keterangan'] = k
                # also persist tema into performance_data rows that match (simple heuristic)
                # find latest appended row for this dosen and jenis without tema -> assign tema
                mask = (st.session_state.performance_data['dosen_id']==row['dosen_id']) & (st.session_state.performance_data['tema'].isnull())
                idxs = st.session_state.performance_data[mask].tail(5).index.tolist()
                if idxs:
                    st.session_state.performance_data.loc[idxs[-1],'tema'] = row.get('tema', None)
                st.success("Disetujui"); st.experimental_rerun()
            if c2.button("❌ Reject", key=f"reject_{row['id']}"):
                st.session_state.verification_queue.loc[st.session_state.verification_queue['id']==row['id'],'status'] = 'Rejected'
                st.session_state.verification_queue.loc[st.session_state.verification_queue['id']==row['id'],'keterangan'] = k or "Dokumentasi tidak lengkap"
                st.success("Ditolak"); st.experimental_rerun()

def manage_themes_page():
    st.markdown("## ⚙️ Manage Research Themes (Admin / Dekan / Kaprodi)")
    rd = st.session_state.get('research_directions', DEFAULT_RESEARCH_DIRECTIONS)
    st.markdown("### Current themes by Faculty / University")
    for k,v in rd.items():
        with st.expander(k):
            st.write(v)
            col1,col2 = st.columns([3,1])
            with col1:
                new_t = st.text_input(f"Tambah tema ke {k}", key=f"add_{k}")
            with col2:
                if st.button(f"Tambah ke {k}", key=f"btn_add_{k}"):
                    if new_t and new_t.strip():
                        rd[k] = rd.get(k,[]) + [new_t.strip()]
                        st.session_state.research_directions = rd
                        st.success(f"Ditambahkan '{new_t.strip()}' ke {k}")
                        st.experimental_rerun()
            # remove item
            to_remove = st.selectbox(f"Pilih tema hapus dari {k}", ["(pilih)"] + rd.get(k,[]), key=f"rem_{k}")
            if st.button(f"Hapus dari {k}", key=f"btn_rem_{k}"):
                if to_remove != "(pilih)":
                    rd[k] = [t for t in rd.get(k,[]) if t!=to_remove]
                    st.session_state.research_directions = rd
                    st.success(f"Dihapus '{to_remove}' dari {k}")
                    st.experimental_rerun()

def export_evaluations():
    st.markdown("## 📁 Export Evaluations (CSV)")
    ikd_df = st.session_state.ikd_df if 'ikd_df' in st.session_state else hitung_ikd_semua(st.session_state.dosen_data, st.session_state.performance_data)
    # compute evaluations
    perf_df = st.session_state.performance_data
    verification_df = st.session_state.verification_queue
    rows = []
    for _, r in ikd_df.iterrows():
        perf_year = perf_df[perf_df['dosen_id']==r['id']]
        comps = {'publikasi': r['skor_publikasi'], 'penelitian': r['skor_penelitian'], 'pengabdian': r['skor_pengabdian'], 'mengajar': r['skor_mengajar']}
        eval_res = evaluate_status_eligibility(r, perf_year, r['IKD'], comps, verification_df=verification_df)
        rows.append({
            'id': r['id'],
            'nama': r['nama'],
            'fakultas': r['fakultas'],
            'prodi': r['prodi'],
            'IKD': r['IKD'],
            'action': eval_res['action'],
            'recommendation': eval_res['recommendation'],
            'total_sks': eval_res['total_sks'],
            'reasons': "; ".join(eval_res['reasons'])
        })
    df = pd.DataFrame(rows)
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Evaluations (CSV)", data=csv, file_name=f"evaluations_{datetime.now().strftime('%Y%m%d')}.csv")

# ---------------- Helper small functions used in multiple places ----------------
def alasan_keputusan(components, ikd):
    reasons = []
    if components['mengajar'] < 60:
        reasons.append(f"SKS mengajar rendah ({components['mengajar']:.0f}/100) — periksa beban & dokumentasi.")
    if components['penelitian'] < 50:
        reasons.append(f"Aktivitas penelitian relatif rendah ({components['penelitian']:.0f}/100).")
    if components['publikasi'] < 50:
        reasons.append(f"Produktivitas publikasi rendah ({components['publikasi']:.0f}/100).")
    if components['pengabdian'] < 50:
        reasons.append(f"Kegiatan pengabdian minim ({components['pengabdian']:.0f}/100).")
    if not reasons:
        reasons.append("Komponen kinerja baik; kinerja seimbang antara pengajaran, penelitian, publikasi, dan pengabdian.")
    if ikd >= 85:
        reasons.append("IKD sangat tinggi — potensi penghargaan/promosi.")
    elif ikd >= 70:
        reasons.append("IKD berada di kisaran baik — pertahankan & tingkatkan publikasi.")
    elif ikd >= 55:
        reasons.append("IKD cukup — perbaikan terfokus dianjurkan.")
    else:
        reasons.append("IKD rendah — butuh intervensi (pelatihan/dukungan riset).")
    return reasons

def rekomendasi_dosen_from_components(components):
    recs = []
    if components['skor_publikasi'] < 50:
        recs.append("Ikuti workshop penulisan & kolaborasi riset.")
    if components['skor_penelitian'] < 50:
        recs.append("Dorong partisipasi pada proposal & kolaborasi penelitian.")
    if components['skor_pengabdian'] < 50:
        recs.append("Rencanakan minimal 1 kegiatan pengabdian terdokumentasi tiap tahun.")
    if components['skor_mengajar'] < 60:
        recs.append("Review beban mengajar & tingkatkan metode pembelajaran.")
    if not recs:
        recs.append("Pertahankan kinerja dan dokumentasikan untuk kenaikan karir.")
    return recs

# ---------------- Main ----------------
def main():
    if not st.session_state.logged_in:
        sidebar_common_controls()
        public_rektor_dashboard()
        login_area_inline()
        return

    # logged in
    sidebar_common_controls()
    if st.session_state.user_role:
        st.sidebar.markdown(f"### 👤 {st.session_state.user_name}")
        st.sidebar.markdown(f"**Role:** {st.session_state.user_role}")
        if st.session_state.fakultas:
            st.sidebar.markdown(f"**Fakultas:** {st.session_state.fakultas}")
        if st.session_state.prodi:
            st.sidebar.markdown(f"**Prodi:** {st.session_state.prodi}")
        st.sidebar.markdown("---")
        if st.sidebar.button("🚪 Logout", use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.experimental_rerun()

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
            # kaprodi dashboard uses rektor dashboard logic filtered to prodi/fakultas
            st.markdown("## 📊 Dashboard Kaprodi (Ringkasan)")
            public_rektor_dashboard()
        elif selected_menu == "Verifikasi Data":
            verification_page()
        elif selected_menu == "Analitik Prodi":
            st.markdown("## 📈 Analitik Prodi (Demo)")
            public_rektor_dashboard()
        elif selected_menu == "Manage Themes":
            manage_themes_page()
        else:
            st.info("Menu belum tersedia.")
    elif role == 'Dekan':
        if selected_menu == "Dashboard":
            st.markdown("## 📊 Dashboard Dekan (Ringkasan)")
            public_rektor_dashboard()
        elif selected_menu == "Verifikasi Data":
            verification_page()
        elif selected_menu == "Analitik Fakultas":
            st.markdown("## 📈 Analitik Fakultas (Demo)")
            public_rektor_dashboard()
        elif selected_menu == "Manage Themes":
            manage_themes_page()
        else:
            st.info("Menu belum tersedia.")
    elif role == 'Admin':
        if selected_menu == "Dashboard":
            public_rektor_dashboard()
        elif selected_menu == "Manage Themes":
            manage_themes_page()
        elif selected_menu == "Export Evaluations":
            export_evaluations()
        else:
            st.info("Menu belum tersedia.")
    else:
        st.info("Role belum dikenali.")

if __name__ == "__main__":
    main()
