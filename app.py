import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ==========================================================
# 1. KONFIGURASI HALAMAN & CSS GREEN BENTO GRID JAKARTA
# ==========================================================
st.set_page_config(
    page_title="Dashboard Evaluasi IGRK DKI Jakarta",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

FONT = "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
WARNA = {
    "hijau_tua": "#14532D",     # Deep Forest Green
    "hijau_utama": "#15803D",   # Emerald Green
    "hijau_muda": "#10B981",    # Mint Green
    "hijau_pucat": "#DCFCE7",   # Soft Mint Fill
    "teal": "#0D9488",          # Teal Pendukung (Listrik/Indirect)
    "emas": "#D97706",          # Warm Amber (Transportasi/Target)
    "koral": "#E11D48",         # Coral (Penanda Evaluasi/Gap)
    "abu": "#64748B",           # Slate Muted
    "teks": "#0F172A",          # Dark Slate
}

st.markdown(
    """
    <style>
    /* Sembunyikan sidebar & menu bawaan secara permanen */
    [data-testid="stSidebar"], [data-testid="collapsedControl"], #MainMenu, footer {
        display: none !important;
    }
    /* Latar belakang Soft Sage Green seperti referensi */
    .stApp {
        background-color: #EAF3EE;
        font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        color: #0F172A;
    }
    .block-container {
        padding-top: 1.4rem;
        padding-bottom: 2.8rem;
        max-width: 1240px;
    }
    /* Navigasi Kapsul Atas (Pill Navigation) */
    div[role="radiogroup"] {
        background: #FFFFFF;
        padding: 6px 10px;
        border-radius: 999px;
        box-shadow: 0 4px 14px rgba(20, 83, 45, 0.06);
        border: 1px solid #D1E7DD;
        display: flex;
        justify-content: center;
        gap: 6px;
        margin-bottom: 1.2rem;
    }
    div[role="radiogroup"] label {
        border-radius: 999px !important;
        padding: 6px 16px !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        transition: all 0.2s ease;
    }
    /* Hero Banner Ikonik Jakarta dengan Ornamen Gigi Balang & Monas */
    .jkt-hero {
        background: linear-gradient(130deg, #0F3F24 0%, #15803D 62%, #0D9488 100%);
        border-radius: 20px;
        padding: 26px 32px 22px 32px;
        color: #FFFFFF;
        position: relative;
        overflow: hidden;
        box-shadow: 0 12px 28px rgba(20, 83, 45, 0.16);
        margin-bottom: 1.2rem;
    }
    .jkt-badge {
        display: inline-block;
        background: rgba(255, 255, 255, 0.18);
        color: #DCFCE7;
        padding: 4px 12px;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    .jkt-title {
        font-size: 1.75rem;
        font-weight: 800;
        margin: 0 0 6px 0;
        color: #FFFFFF;
        letter-spacing: -0.02em;
    }
    .jkt-sub {
        font-size: 0.92rem;
        color: #E2F8EC;
        max-width: 720px;
        line-height: 1.5;
        margin: 0;
        text-align: justify;
    }
    /* Kartu Bento Putih Bersudut Membulat */
    .bento-card {
        background: #FFFFFF;
        border-radius: 18px;
        padding: 18px 20px;
        border: 1px solid #DCECE3;
        box-shadow: 0 4px 14px rgba(15, 63, 36, 0.04);
        margin-bottom: 14px;
        height: 100%;
    }
    .bento-green {
        background: linear-gradient(135deg, #14532D 0%, #15803D 100%);
        color: #FFFFFF;
        border-radius: 18px;
        padding: 20px 22px;
        box-shadow: 0 8px 20px rgba(20, 83, 45, 0.15);
        margin-bottom: 14px;
    }
    /* Pill Header Hijau Tua ala Referensi Market Analysis */
    .pill-header {
        background: #14532D;
        color: #FFFFFF;
        font-size: 0.82rem;
        font-weight: 700;
        padding: 6px 16px;
        border-radius: 999px;
        display: inline-block;
        margin-bottom: 10px;
        letter-spacing: 0.02em;
    }
    .kpi-label {
        font-size: 0.78rem;
        color: #64748B;
        font-weight: 600;
        margin-bottom: 4px;
    }
    .kpi-val {
        font-size: 1.65rem;
        font-weight: 800;
        color: #0F172A;
        line-height: 1.15;
        margin-bottom: 6px;
    }
    .badge-up {
        background: #DCFCE7;
        color: #15803D;
        padding: 3px 9px;
        border-radius: 999px;
        font-size: 0.74rem;
        font-weight: 700;
    }
    .badge-warn {
        background: #FEF3C7;
        color: #B45309;
        padding: 3px 9px;
        border-radius: 999px;
        font-size: 0.74rem;
        font-weight: 700;
    }
    .badge-gap {
        background: #FFE4E6;
        color: #BE123C;
        padding: 3px 9px;
        border-radius: 999px;
        font-size: 0.74rem;
        font-weight: 700;
    }
    .insight-text {
        text-align: justify;
        font-size: 0.85rem;
        line-height: 1.55;
        color: #334155;
        margin: 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def fmt_id(x, d=1):
    return f"{x:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def fmt_tanda(x, d=1):
    if abs(x) < 0.5 * 10 ** (-d):
        return fmt_id(0, d)
    return ("+" if x > 0 else "−") + fmt_id(abs(x), d)


def tata_letak(fig, y_title=None, tinggi=290, show_legend=True):
    fig.update_layout(
        template="plotly_white",
        font=dict(family=FONT, size=11.5, color="#1E293B"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=8, r=8, t=24, b=8),
        height=tinggi,
        showlegend=show_legend,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, title_text=""),
        hovermode="x unified",
        yaxis=dict(title=y_title, gridcolor="#E2E8F0", zerolinecolor="#CBD5E1"),
        xaxis=dict(showgrid=False),
    )
    return fig


def buat_gauge_setengah(nilai, maks, judul, satuan="%", warna="#15803D", tinggi=175):
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=nilai,
            number={"suffix": satuan, "font": {"size": 26, "color": "#0F172A", "family": FONT}},
            title={"text": judul, "font": {"size": 12, "color": "#475569", "family": FONT}},
            gauge={
                "axis": {"range": [0, maks], "tickwidth": 1, "tickcolor": "#CBD5E1"},
                "bar": {"color": warna, "thickness": 0.75},
                "bgcolor": "#E2E8F0",
                "borderwidth": 0,
            },
        )
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=16, r=16, t=30, b=6),
        height=tinggi,
    )
    return fig


# ==========================================================
# 2. BASIS DATA RESMI LAPORAN DLH DKI JAKARTA (2023–2026)
# ==========================================================
@st.cache_data
def muat_data_dlh():
    tahun = list(range(2010, 2026))
    # Data Inventarisasi Gg CO2e (Ribu Ton) dari Tabel 2 (AR2) & Tabel 3 (AR5) Laporan 2026
    df_inv = pd.DataFrame({
        "Tahun": tahun,
        "Transportasi": [7258, 8201, 10722, 12453, 11424, 14102, 14293, 14671, 15325, 15364, 11903, 12642, 15543, 15992, 15806, 18293],
        "Pembangkit Listrik": [8044, 7785, 6843, 7521, 8010, 7737, 7227, 6673, 7938, 8744, 7301, 8530, 7217, 7443, 7803, 7128],
        "Industri Manufaktur": [2330, 2326, 2256, 2755, 1935, 2083, 2648, 3465, 3417, 2064, 2081, 2219, 2443, 1992, 2555, 2348],
        "Bangunan & Lainnya (Direct)": [1190, 1258, 1299, 1293, 1293, 1637, 1613, 1676, 1674, 1492, 1494, 1495, 1512, 1490, 1505, 1543],
        "Limbah_AR2": [1873, 1837, 1746, 1845, 1915, 2000, 2083, 2199, 2284, 2305, 2396, 2450, 2478, 2369, 2362, 2444],
        "Limbah_AR5": [2444, 2395, 2270, 2405, 2494, 2608, 2720, 2865, 2973, 3004, 3126, 3196, 3236, 3088, 3078, 3186],
        "AFOLU": [163, 187, 180, 184, 46, 39, 44, 51, 58, -14, -29, 38, -45, -60, -51, -40],
        "Listrik Indirect (Jamali)": [19733, 21787, 24988, 29028, 26927, 29065, 30982, 28378, 29309, 30907, 29015, 29301, 31145, 33420, 34509, 34507],
    })

    # Perbandingan Top-Down (Baseline vs Inventori) & Bottom-Up (Akumulasi Proyek) 2020-2025
    df_rekonsiliasi = pd.DataFrame({
        "Tahun": [2020, 2021, 2022, 2023, 2024, 2025],
        "Baseline_JtTon": [73.3, 77.7, 80.8, 85.0, 88.2, 92.0],
        "Inventori_JtTon": [54.2, 56.7, 60.3, 62.6, 64.5, 66.2],
        "Target_Rencana_JtTon": [11.95, 13.91, 14.94, 16.30, 17.63, 21.11],
        "Capaian_Sektoral_JtTon": [19.10, 21.00, 20.50, 21.90, 23.40, 25.80],
        "Klaim_Proyek_JtTon": [6.35, 6.72, 12.02, 15.73, 17.45, 16.44],
        "Persen_Sektoral": [26.0, 27.0, 25.4, 25.9, 26.5, 28.0],
    })

    # Rincian Aksi Mitigasi 2025 (Tabel 2 Laporan 2026)
    df_aksi = pd.DataFrame([
        {
            "Kelompok": "Manajemen Lalu Lintas (Sistem ITS)",
            "Kategori": "Pemodelan Lalu Lintas",
            "Reduksi_JtTon": 8.79,
            "Klaim_2023": 8.79, "Klaim_2024": 8.79, "Klaim_2025": 8.79,
            "Aktivitas_Label": "Kecepatan rata-rata pasca-ITS (km/jam)",
            "Akt_2023": 30.50, "Akt_2024": 26.07, "Akt_2025": 26.07,
            "Saran": "Angka reduksi tercatat statis 8,79 juta ton selama 2023–2025 meskipun kecepatan koridor turun dari 30,5 ke 26,07 km/jam. Disarankan pembaruan kalibrasi model bersama Dishub.",
        },
        {
            "Kelompok": "Substitusi Gas & Efisiensi Pembangkit",
            "Kategori": "Energi Hulu (BUMN/PLN)",
            "Reduksi_JtTon": 4.56,
            "Klaim_2023": 5.25, "Klaim_2024": 5.74, "Klaim_2025": 4.56,
            "Aktivitas_Label": "Faktor Emisi Grid Jamali (tCO₂/MWh)",
            "Akt_2023": 0.80, "Akt_2024": 0.80, "Akt_2025": 0.80,
            "Saran": "Menyumbang 27,7% reduksi proyek dari PLTGU Muara Karang & Priok. Pembaruan faktor emisi Jamali (konstan 0,80 tCO₂/MWh sejak 2019) akan menyelaraskan klaim hulu dengan listrik hilir.",
        },
        {
            "Kelompok": "Angkutan Massal (BRT, Feeder, KRL, MRT, Bus Listrik)",
            "Kategori": "Transportasi Publik (Hilir)",
            "Reduksi_JtTon": 1.63,
            "Klaim_2023": 0.93, "Klaim_2024": 1.98, "Klaim_2025": 1.63,
            "Aktivitas_Label": "Konsumsi Listrik MRT & KRL (GWh)",
            "Akt_2023": 340.0, "Akt_2024": 342.0, "Akt_2025": 356.0,
            "Saran": "Lonjakan penumpang dan armada bus listrik meningkatkan reduksi riil, namun parameter faktor perpindahan moda (modal shift BRT) masih mengacu survei tahun 2012.",
        },
        {
            "Kelompok": "Mandatori Biofuel (B35) & BBG",
            "Kategori": "Substitusi Bahan Bakar",
            "Reduksi_JtTon": 0.88,
            "Klaim_2023": 0.45, "Klaim_2024": 0.82, "Klaim_2025": 0.88,
            "Aktivitas_Label": "Penyaluran Biosolar Transportasi (Ribu kL)",
            "Akt_2023": 141.7, "Akt_2024": 712.5, "Akt_2025": 694.8,
            "Saran": "Peningkatan bauran biodiesel B35 mendongkrak capaian reduksi transportasi dan industri hingga hampir dua kali lipat dibandingkan tahun 2023.",
        },
        {
            "Kelompok": "Efisiensi Bangunan, PJU LHE & PLTS Atap",
            "Kategori": "Bangunan & Energi Terbarukan",
            "Reduksi_JtTon": 0.38,
            "Klaim_2023": 0.26, "Klaim_2024": 0.36, "Klaim_2025": 0.38,
            "Aktivitas_Label": "Kapasitas PLTS Rooftop Terpasang (MWp)",
            "Akt_2023": 11.18, "Akt_2024": 34.39, "Akt_2025": 24.18,
            "Saran": "Data konservasi gedung pemerintah (2024–2025) dan PJU Bina Marga masih menggunakan asumsi tahun sebelumnya, sehingga integrasi pelaporan rutin wali data perlu diperkuat.",
        },
        {
            "Kelompok": "Pengelolaan Sampah (3R, LFG, RDF) & RTH",
            "Kategori": "Limbah & Kehutanan (FOLU)",
            "Reduksi_JtTon": 0.19,
            "Klaim_2023": 0.23, "Klaim_2024": 0.27, "Klaim_2025": 0.19,
            "Aktivitas_Label": "Sampah Diolah 3R & RDF (Ribu Ton)",
            "Akt_2023": 864.4, "Akt_2024": 710.3, "Akt_2025": 899.0,
            "Saran": "Peralihan pencatatan ke GWP AR5 (metana naik dari 21 ke 28) akan meningkatkan bobot reduksi metana dari LFG Recovery, komposting, dan RDF sebesar 33%.",
        },
    ])

    # Peta Jalan Target Tahunan 2025-2030 (Tabel 3 Laporan 2026 dalam Ribu Ton / Gg CO2e)
    df_roadmap = pd.DataFrame({
        "Tahun": [2025, 2026, 2027, 2028, 2029, 2030],
        "Green Building Komersial": [3582, 4476, 5383, 6306, 7245, 8194],
        "Labelling Alat Rumah Tangga": [2442, 2610, 2814, 3054, 3329, 3630],
        "Transportasi Rendah Karbon": [4309, 4504, 4792, 5162, 5612, 6140],
        "Efisiensi & Biofuel Industri": [1864, 2621, 3330, 3991, 4606, 5178],
        "Pembangkit Listrik Bersih": [8471, 8251, 8546, 8775, 8995, 9170],
        "Pengelolaan Limbah & PLTSa": [416, 632, 803, 1085, 1316, 1598],
        "Peningkatan RTH (FOLU)": [29, 26, 23, 20, 18, 16],
        "Total Target": [21114, 23178, 25789, 28521, 31235, 34090],
    })
    return df_inv, df_rekonsiliasi, df_aksi, df_roadmap


df_inv, df_rek, df_aksi, df_road = muat_data_dlh()

# ==========================================================
# 3. HERO BANNER IKONIK JAKARTA & NAVIGASI KAPSUL
# ==========================================================
st.markdown(
    """
    <div class="jkt-hero">
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:16px;">
            <div style="flex:1;min-width:300px;z-index:2;">
                <div class="jkt-badge">🌿 Dinas Lingkungan Hidup Provinsi DKI Jakarta • Laporan IGRK 2026</div>
                <div class="jkt-title">Jakarta Sudah Menurunkan Emisi, Tapi Seberapa Jauh?</div>
                <p class="jkt-sub">
                    Eksplorasi visual profil emisi gas rumah kaca (2010–2025), rekonsiliasi capaian aksi mitigasi, 
                    dan simulasi transisi parameter menuju target iklim Jakarta 2030.
                </p>
            </div>
            <!-- Ilustrasi Vektor Siluet Monas, Gedung Jakarta, & MRT -->
            <div style="z-index:1;opacity:0.92;">
                <svg width="250" height="96" viewBox="0 0 250 96" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <!-- Ornamen Gigi Balang Betawi di Dasar -->
                    <path d="M0 90 L10 80 L20 90 L30 80 L40 90 L50 80 L60 90 L70 80 L80 90 L90 80 L100 90 L110 80 L120 90 L130 80 L140 90 L150 80 L160 90 L170 80 L180 90 L190 80 L200 90 L210 80 L220 90 L230 80 L240 90 L250 80 L250 96 L0 96 Z" fill="rgba(255,255,255,0.18)"/>
                    <!-- Siluet Gedung Sudirman-Thamrin -->
                    <rect x="18" y="42" width="22" height="42" rx="2" fill="rgba(255,255,255,0.22)"/>
                    <rect x="46" y="30" width="26" height="54" rx="2" fill="rgba(255,255,255,0.28)"/>
                    <rect x="178" y="34" width="24" height="50" rx="2" fill="rgba(255,255,255,0.25)"/>
                    <rect x="208" y="46" width="22" height="38" rx="2" fill="rgba(255,255,255,0.20)"/>
                    <!-- Siluet Ikonik MONAS di Tengah -->
                    <path d="M98 84 L152 84 L144 74 L106 74 Z" fill="rgba(255,255,255,0.45)"/>
                    <path d="M92 66 L158 66 L146 74 L104 74 Z" fill="rgba(255,255,255,0.65)"/>
                    <rect x="121" y="22" width="8" height="44" fill="#FFFFFF"/>
                    <rect x="116" y="19" width="18" height="4" rx="1" fill="#FFFFFF"/>
                    <!-- Lidah Api Emas Monas -->
                    <path d="M125 6 C129 11 131 15 125 19 C119 15 121 11 125 6 Z" fill="#FBBF24"/>
                </svg>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

MENU_HALAMAN = [
    "🏠 Beranda & Sorotan",
    "📊 1. Sudah Sampai Mana?",
    "🏭 2. Dari Mana Emisinya?",
    "🛠️ 3. Apa yang Dilakukan?",
    "🚀 4. Mau ke Mana? (2030)",
]

if "nav_pilihan" not in st.session_state:
    st.session_state["nav_pilihan"] = MENU_HALAMAN[0]


def buka_halaman(nama):
    st.session_state["nav_pilihan"] = nama


pilihan = st.radio(
    "Pilih Bagian:",
    MENU_HALAMAN,
    index=MENU_HALAMAN.index(st.session_state["nav_pilihan"]),
    horizontal=True,
    label_visibility="collapsed",
)
if pilihan != st.session_state["nav_pilihan"]:
    st.session_state["nav_pilihan"] = pilihan
    st.rerun()

# ==========================================================
# HALAMAN 0: BERANDA (30% TEKS : 70% VISUAL)
# ==========================================================
if st.session_state["nav_pilihan"] == MENU_HALAMAN[0]:
    # Baris 1: Kartu Hijau Utama + 3 Semi-Circle Gauge (Gaya Market Analysis Report)
    col_h1, col_h2, col_h3, col_h4 = st.columns([1.35, 1, 1, 1], gap="small")

    with col_h1:
        st.markdown(
            """
            <div class="bento-green">
                <div style="font-size:0.76rem;opacity:0.85;font-weight:600;text-transform:uppercase;">Potret Emisi & Mitigasi 2025</div>
                <div style="font-size:2.05rem;font-weight:800;margin:4px 0;">66,22 Jt Ton</div>
                <div style="font-size:0.84rem;color:#DCFCE7;margin-bottom:10px;">Total Emisi GRK DKI Jakarta (AR2)</div>
                <div style="background:rgba(255,255,255,0.16);padding:8px 12px;border-radius:10px;font-size:0.8rem;">
                    🌱 Reduksi: <b>25,8 Jt Ton (−28,0%)</b> dari Baseline
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_h2:
        st.markdown('<div class="bento-card" style="padding:8px 10px;">', unsafe_allow_html=True)
        st.plotly_chart(buat_gauge_setengah(28.0, 32.0, "Capaian vs Target 32%", "%", WARNA["hijau_utama"]), use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)
    with col_h3:
        st.markdown('<div class="bento-card" style="padding:8px 10px;">', unsafe_allow_html=True)
        st.plotly_chart(buat_gauge_setengah(52.1, 100.0, "Porsi Emisi Listrik PLN", "%", WARNA["teal"]), use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)
    with col_h4:
        st.markdown('<div class="bento-card" style="padding:8px 10px;">', unsafe_allow_html=True)
        st.plotly_chart(buat_gauge_setengah(63.7, 100.0, "Porsi Proyek Terverifikasi", "%", WARNA["emas"]), use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    # Baris 2: Grafik Visual Ringkasan (Kiri) + 3 Kartu Sorotan Studi (Kanan)
    c_vis, c_ins = st.columns([1.35, 1], gap="medium")

    with c_vis:
        st.markdown('<div class="bento-card">', unsafe_allow_html=True)
        st.markdown('<div class="pill-header">Tren Emisi Aktual vs Perkiraan Tanpa Program (Baseline) 2015–2025</div>', unsafe_allow_html=True)
        thn_b = [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]
        bau_b = [63.0, 64.0, 65.0, 69.0, 73.0, 73.3, 77.7, 80.8, 85.0, 88.2, 92.0]
        inv_b = [56.7, 58.9, 57.1, 60.0, 60.9, 54.2, 56.7, 60.3, 62.6, 64.5, 66.2]
        fig_home = go.Figure()
        fig_home.add_trace(go.Scatter(
            x=thn_b, y=bau_b, name="Baseline (Tanpa Program)",
            mode="lines+markers", line=dict(color=WARNA["abu"], width=2, dash="dash"),
        ))
        fig_home.add_trace(go.Scatter(
            x=thn_b, y=inv_b, name="Emisi Inventori Aktual",
            mode="lines+markers", fill="tonexty", fillcolor="rgba(21, 128, 61, 0.14)",
            line=dict(color=WARNA["hijau_utama"], width=3, shape="spline"),
        ))
        fig_home.add_annotation(
            x=2025, y=79.0, text="<b>−25,8 Jt Ton (−28,0%)</b>",
            showarrow=False, font=dict(color=WARNA["hijau_tua"], size=12),
        )
        st.plotly_chart(tata_letak(fig_home, "Juta Ton CO₂e", 275), use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    with c_ins:
        st.markdown(
            """
            <div class="bento-card">
                <div class="pill-header">3 Sorotan Evaluasi & Pengembangan Data</div>
                <p class="insight-text" style="margin-bottom:10px;">
                    <b>1. Rekonsiliasi Top-Down vs Bottom-Up:</b> Penurunan sektoral mencapai <b>25,80 juta ton</b>, 
                    sedangkan penjumlahan rincian proyek mencatat <b>16,44 juta ton</b> karena pendekatan sektoral turut 
                    menangkap dinamika makroekonomi di luar proyek.
                </p>
                <p class="insight-text" style="margin-bottom:10px;">
                    <b>2. Transisi Standar GWP AR2 ke AR5:</b> Pelaporan inventarisasi 2026 mulai mengadopsi GWP AR5 
                    yang menaikkan bobot emisi metana sektor limbah sebesar <b>+30,4%</b>, sehingga <i>baseline</i> 
                    mitigasi perlu diselaraskan ke AR5.
                </p>
                <p class="insight-text">
                    <b>3. Pembaruan Parameter Teknis:</b> Pemutakhiran faktor emisi listrik Jamali (konstan sejak 2019) 
                    dan parameter survei transportasi (2012) akan meningkatkan presisi evaluasi menuju 2030.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Baris 3: 4 Tombol Pintu Eksplorasi Bagian 1–4
    b1, b2, b3, b4 = st.columns(4, gap="small")
    with b1:
        st.button("📊 1. Sudah Sampai Mana? →", on_click=buka_halaman, args=(MENU_HALAMAN[1],), use_container_width=True)
    with b2:
        st.button("🏭 2. Dari Mana Emisinya? →", on_click=buka_halaman, args=(MENU_HALAMAN[2],), use_container_width=True)
    with b3:
        st.button("🛠️ 3. Apa yang Dilakukan? →", on_click=buka_halaman, args=(MENU_HALAMAN[3],), use_container_width=True)
    with b4:
        st.button("🚀 4. Mau ke Mana (2030)? →", on_click=buka_halaman, args=(MENU_HALAMAN[4],), use_container_width=True)


# ==========================================================
# HALAMAN 1: SUDAH SAMPAI MANA? (TOP-DOWN VS BOTTOM-UP)
# ==========================================================
elif st.session_state["nav_pilihan"] == MENU_HALAMAN[1]:
    c_ctrl1, c_ctrl2 = st.columns([1, 1.6], gap="medium")
    with c_ctrl1:
        thn_ev = st.selectbox("📅 Pilih Tahun Laporan Evaluasi:", [2022, 2023, 2024, 2025], index=3)
    with c_ctrl2:
        tampilkan_komponen = st.radio(
            "Tampilkan Metode Perhitungan Reduksi:",
            ["Sektoral (Baseline − Inventori)", "Akumulasi Proyek (Bottom-Up)", "Sandingkan Keduanya"],
            index=2,
            horizontal=True,
        )

    row_e = df_rek[df_rek["Tahun"] == thn_ev].iloc[0]
    selisih_metode = row_e["Capaian_Sektoral_JtTon"] - row_e["Klaim_Proyek_JtTon"]
    jarak_30 = 32.0 - row_e["Persen_Sektoral"]

    # 4 Kartu KPI Bento
    k1, k2, k3, k4 = st.columns(4, gap="small")
    with k1:
        st.markdown(
            f"""
            <div class="bento-card">
                <div class="kpi-label">Target Rencana ({thn_ev})</div>
                <div class="kpi-val">{fmt_id(row_e['Target_Rencana_JtTon'], 2)} Jt Ton</div>
                <span class="badge-up">Peta Jalan RAD-GRK</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with k2:
        st.markdown(
            f"""
            <div class="bento-card">
                <div class="kpi-label">Capaian Sektoral (Top-Down)</div>
                <div class="kpi-val">{fmt_id(row_e['Capaian_Sektoral_JtTon'], 2)} Jt Ton</div>
                <span class="badge-up">−{fmt_id(row_e['Persen_Sektoral'], 1)}% dari Baseline</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with k3:
        st.markdown(
            f"""
            <div class="bento-card">
                <div class="kpi-label">Klaim Aksi Proyek (Bottom-Up)</div>
                <div class="kpi-val">{fmt_id(row_e['Klaim_Proyek_JtTon'], 2)} Jt Ton</div>
                <span class="badge-warn">{fmt_id(row_e['Klaim_Proyek_JtTon']/row_e['Capaian_Sektoral_JtTon']*100, 1)}% dari Angka Sektoral</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with k4:
        st.markdown(
            f"""
            <div class="bento-card">
                <div class="kpi-label">Selisih Non-Proyek / Makro</div>
                <div class="kpi-val">{fmt_id(selisih_metode, 2)} Jt Ton</div>
                <span class="badge-gap">Jarak ke 2030: {fmt_id(jarak_30, 1)}% lagi</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    g_kiri, g_kanan = st.columns([1.35, 1], gap="medium")
    with g_kiri:
        st.markdown('<div class="bento-card">', unsafe_allow_html=True)
        st.markdown('<div class="pill-header">Perbandingan Target, Capaian Sektoral, dan Akumulasi Proyek (2020–2025)</div>', unsafe_allow_html=True)
        fig1 = go.Figure()
        fig1.add_trace(go.Bar(
            x=df_rek["Tahun"], y=df_rek["Target_Rencana_JtTon"],
            name="Target Rencana", marker_color="#94A3B8", marker_cornerradius=6,
        ))
        if tampilkan_komponen in ["Sektoral (Baseline − Inventori)", "Sandingkan Keduanya"]:
            fig1.add_trace(go.Bar(
                x=df_rek["Tahun"], y=df_rek["Capaian_Sektoral_JtTon"],
                name="Capaian Sektoral (Baseline − Inventori)", marker_color=WARNA["hijau_utama"], marker_cornerradius=6,
            ))
        if tampilkan_komponen in ["Akumulasi Proyek (Bottom-Up)", "Sandingkan Keduanya"]:
            fig1.add_trace(go.Bar(
                x=df_rek["Tahun"], y=df_rek["Klaim_Proyek_JtTon"],
                name="Akumulasi Proyek (Tabel 2)", marker_color=WARNA["emas"], marker_cornerradius=6,
            ))
        fig1.update_layout(barmode="group")
        st.plotly_chart(tata_letak(fig1, "Juta Ton CO₂e", 290), use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    with g_kanan:
        st.markdown('<div class="bento-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="pill-header">Proporsi Reduksi Proyek vs Efek Makro ({thn_ev})</div>', unsafe_allow_html=True)
        fig_d1 = go.Figure(go.Pie(
            labels=["Teridentifikasi dari Aksi Proyek", "Efek Makro & Non-Proyek"],
            values=[row_e["Klaim_Proyek_JtTon"], selisih_metode],
            hole=0.64,
            marker=dict(colors=[WARNA["hijau_utama"], "#CBD5E1"]),
            textinfo="percent",
        ))
        fig_d1.update_layout(
            annotations=[dict(text=f"<b>{fmt_id(row_e['Capaian_Sektoral_JtTon'], 1)}</b><br>Jt Ton", x=0.5, y=0.5, font_size=16, showarrow=False)],
            margin=dict(l=10, r=10, t=10, b=10), height=195, paper_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h", yanchor="bottom", y=-0.18, xanchor="center", x=0.5),
        )
        st.plotly_chart(fig_d1, use_container_width=True, config={"displayModeBar": False})
        st.markdown(
            f"""
            <p class="insight-text" style="margin-top:12px;">
                Mengacu pada Bab IV Laporan DLH, selisih <b>{fmt_id(selisih_metode, 2)} juta ton CO₂e</b> pada {thn_ev} 
                muncul karena perhitungan sektoral turut dipengaruhi fluktuasi ekonomi, harga energi, dan aksi masyarakat 
                yang belum tercatat di dalam tabel proyek.
            </p>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)


# ==========================================================
# HALAMAN 2: DARI MANA EMISI JAKARTA? (2010–2025 & AR2 vs AR5)
# ==========================================================
elif st.session_state["nav_pilihan"] == MENU_HALAMAN[2]:
    f1, f2, f3 = st.columns([1.3, 1, 1], gap="medium")
    with f1:
        thn_sek = st.slider("📅 Geser Tahun Pengamatan (2010–2025):", 2010, 2025, 2025)
    with f2:
        metrik_gwp = st.radio("Standar Konversi Gas (GWP):", ["GWP AR2 (Acuan Mitigasi)", "GWP AR5 (Standar Baru)"], horizontal=True)
    with f3:
        mode_cakupan = st.radio("Cakupan Sumber:", ["Total (Direct + Listrik)", "Hanya Emisi Langsung (Direct)"], horizontal=True)

    kol_limbah = "Limbah_AR5" if "AR5" in metrik_gwp else "Limbah_AR2"
    sektor_list = ["Transportasi", "Pembangkit Listrik", "Industri Manufaktur", "Bangunan & Lainnya (Direct)", kol_limbah]
    label_tampil = ["Transportasi", "Pembangkit Listrik", "Industri Manufaktur", "Bangunan (LPG/Gas)", "Pengelolaan Limbah"]
    warna_sektor = [WARNA["emas"], WARNA["hijau_tua"], "#64748B", "#10B981", WARNA["koral"]]

    if "Listrik" in mode_cakupan:
        sektor_list = ["Listrik Indirect (Jamali)"] + sektor_list
        label_tampil = ["Listrik PLN (Indirect)"] + label_tampil
        warna_sektor = [WARNA["teal"]] + warna_sektor

    r_now = df_inv[df_inv["Tahun"] == thn_sek].iloc[0]
    r_prev = df_inv[df_inv["Tahun"] == max(2010, thn_sek - 1)].iloc[0]

    nilai_sektor = [r_now[k] / 1000.0 for k in sektor_list]
    total_emisi_jt = sum(nilai_sektor)
    total_prev_jt = sum([r_prev[k] / 1000.0 for k in sektor_list])
    tumbuh_yoy = ((total_emisi_jt / total_prev_jt) - 1) * 100 if thn_sek > 2010 else 0.0
    selisih_ar5_limbah = (r_now["Limbah_AR5"] - r_now["Limbah_AR2"]) / 1000.0

    # 2 Grafik Utama Berdampingan (Donut Chart ala NevBank + Stacked Area/Bar Historis)
    col_v1, col_v2 = st.columns([1, 1.45], gap="medium")

    with col_v1:
        st.markdown('<div class="bento-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="pill-header">Porsi Sektor Tahun {thn_sek} ({metrik_gwp[:7]})</div>', unsafe_allow_html=True)
        fig_donut = go.Figure(go.Pie(
            labels=label_tampil,
            values=nilai_sektor,
            hole=0.62,
            marker=dict(colors=warna_sektor),
            textinfo="percent",
            hovertemplate="<b>%{label}</b><br>%{value:,.2f} Juta Ton CO₂e (%{percent})<extra></extra>",
        ))
        fig_donut.update_layout(
            annotations=[dict(
                text=f"<b>{fmt_id(total_emisi_jt, 2)}</b><br>Jt Ton CO₂e",
                x=0.5, y=0.5, font_size=16, showarrow=False,
            )],
            margin=dict(l=10, r=10, t=10, b=10),
            height=255,
            paper_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5, font=dict(size=10.5)),
        )
        st.plotly_chart(fig_donut, use_container_width=True, config={"displayModeBar": False})
        st.markdown(
            f"""
            <div style="margin-top:18px;padding-top:10px;border-top:1px solid #E2E8F0;display:flex;justify-content:space-between;align-items:center;">
                <span style="font-size:0.8rem;color:#475569;font-weight:600;">Perubahan dari {thn_sek-1}:</span>
                <span class="badge-up">{fmt_tanda(tumbuh_yoy, 1)}% YoY</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with col_v2:
        st.markdown('<div class="bento-card">', unsafe_allow_html=True)
        st.markdown('<div class="pill-header">Tren Historis Emisi per Sektor (2010–2025)</div>', unsafe_allow_html=True)
        fig_hist = go.Figure()
        for kol, lbl, wrn in zip(sektor_list, label_tampil, warna_sektor):
            fig_hist.add_trace(go.Bar(
                x=df_inv["Tahun"],
                y=df_inv[kol] / 1000.0,
                name=lbl,
                marker_color=wrn,
            ))
        fig_hist.update_layout(barmode="stack")
        st.plotly_chart(tata_letak(fig_hist, "Juta Ton CO₂e", 295), use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    # Baris Bawah: Kartu Sorotan Dampak GWP AR2 vs AR5 & Lonjakan Transportasi 2025
    s_a, s_b = st.columns(2, gap="medium")
    with s_a:
        st.markdown(
            f"""
            <div class="bento-card">
                <span class="badge-warn">Temuan Metodologi • Standar GWP AR2 vs AR5</span>
                <p class="insight-text" style="margin-top:8px;">
                    Pada tahun {thn_sek}, penggunaan standar <b>GWP AR5</b> meningkatkan angka emisi sektor limbah sebesar 
                    <b>+{fmt_id(selisih_ar5_limbah, 2)} juta ton CO₂e (+30,4%)</b> dibanding AR2 karena nilai GWP gas metana 
                    (CH₄) naik dari 21 menjadi 28. Penyesuaian garis <i>baseline</i> ke AR5 diperlukan agar evaluasi 
                    mitigasi limbah ke depan setara dengan tabel inventarisasi baru.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with s_b:
        lonjakan_trans = (r_now["Transportasi"] - r_prev["Transportasi"]) / 1000.0
        st.markdown(
            f"""
            <div class="bento-card">
                <span class="badge-up">Dinamika Sektoral • Tahun {thn_sek}</span>
                <p class="insight-text" style="margin-top:8px;">
                    Listrik tidak langsung menyumbang <b>{fmt_id(r_now['Listrik Indirect (Jamali)']/1000.0, 2)} juta ton CO₂e</b> 
                    (didominasi rumah tangga dan gedung komersial), sedangkan pada emisi langsung, sektor <b>Transportasi</b> 
                    mencapai <b>{fmt_id(r_now['Transportasi']/1000.0, 2)} juta ton CO₂e</b> (berubah <b>{fmt_tanda(lonjakan_trans, 2)} juta ton</b> 
                    dibanding tahun sebelumnya).
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ==========================================================
# HALAMAN 3: APA YANG SUDAH DILAKUKAN? (BEDAH AKSI & PARAMETER)
# ==========================================================
elif st.session_state["nav_pilihan"] == MENU_HALAMAN[3]:
    top_a, top_b = st.columns([1.2, 1], gap="medium")
    with top_a:
        pilih_klp = st.selectbox("🔍 Pilih Kelompok Aksi Mitigasi untuk Audit Data Aktivitas:", df_aksi["Kelompok"])
    with top_b:
        sim_ef_jamali = st.slider(
            "⚡ Simulasi Pembaruan Faktor Emisi Listrik Jamali (tCO₂/MWh):",
            0.65, 0.85, 0.80, step=0.01,
            help="Laporan DLH mengasumsikan EF Jamali konstan 0,80 tCO₂/MWh sejak 2019. Geser untuk melihat dampaknya terhadap emisi listrik Jakarta.",
        )

    d_aksi = df_aksi[df_aksi["Kelompok"] == pilih_klp].iloc[0]
    koreksi_emisi_listrik = 34.51 * ((sim_ef_jamali - 0.80) / 0.80)

    col_a1, col_a2 = st.columns([1.35, 1], gap="medium")
    with col_a1:
        st.markdown('<div class="bento-card">', unsafe_allow_html=True)
        st.markdown('<div class="pill-header">Kontribusi Penurunan Emisi per Kelompok Aksi Tahun 2025 (Total Proyek: 16,44 Jt Ton)</div>', unsafe_allow_html=True)
        warna_bar_a = [WARNA["hijau_utama"] if k == pilih_klp else "#94A3B8" for k in df_aksi["Kelompok"]]
        fig_a = go.Figure(go.Bar(
            x=df_aksi["Reduksi_JtTon"],
            y=df_aksi["Kelompok"],
            orientation="h",
            marker_color=warna_bar_a,
            marker_cornerradius=7,
            text=[f"{fmt_id(v, 2)} Jt Ton ({v/16.44*100:.1f}%)" for v in df_aksi["Reduksi_JtTon"]],
            textposition="auto",
        ))
        fig_a.update_layout(yaxis=dict(autorange="reversed"))
        st.plotly_chart(tata_letak(fig_a, None, 290, show_legend=False), use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    with col_a2:
        st.markdown('<div class="bento-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="pill-header">Tren Klaim Reduksi vs Data Aktivitas (2023–2025)</div>', unsafe_allow_html=True)
        thn_3 = [2023, 2024, 2025]
        klaim_3 = [d_aksi["Klaim_2023"], d_aksi["Klaim_2024"], d_aksi["Klaim_2025"]]
        akt_3 = [d_aksi["Akt_2023"], d_aksi["Akt_2024"], d_aksi["Akt_2025"]]

        fig_dual = go.Figure()
        fig_dual.add_trace(go.Bar(
            x=thn_3, y=klaim_3, name="Klaim Reduksi (Jt Ton)",
            marker_color=WARNA["hijau_utama"], marker_cornerradius=6, width=0.38,
        ))
        fig_dual.add_trace(go.Scatter(
            x=thn_3, y=akt_3, name=d_aksi["Aktivitas_Label"],
            yaxis="y2", mode="lines+markers", line=dict(color=WARNA["emas"], width=3),
        ))
        fig_dual.update_layout(
            template="plotly_white",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            height=210, margin=dict(l=8, r=8, t=24, b=8),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
            xaxis=dict(dtick=1, showgrid=False),
            yaxis=dict(title="Jt Ton CO₂e", gridcolor="#E2E8F0"),
            yaxis2=dict(title="Data Aktivitas", overlaying="y", side="right", showgrid=False),
        )
        st.plotly_chart(fig_dual, use_container_width=True, config={"displayModeBar": False})

        st.markdown(
            f"""
            <p class="insight-text" style="margin-top:6px;">
                <b>Catatan Evaluasi ({d_aksi['Kategori']}):</b> {d_aksi['Saran']}
            </p>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    # Baris Simulasi Faktor Emisi Listrik Jamali
    st.markdown(
        f"""
        <div class="bento-card" style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;">
            <div style="flex:2;min-width:280px;">
                <span class="badge-up">Simulasi Sensitivitas Faktor Emisi Listrik Jamali</span>
                <p class="insight-text" style="margin-top:6px;">
                    Dengan mengubah Faktor Emisi <i>on-grid</i> Jamali dari asumsi konstan 2019 (<b>0,80 tCO₂/MWh</b>) 
                    menjadi <b>{fmt_id(sim_ef_jamali, 2)} tCO₂/MWh</b>, beban emisi listrik tidak langsung DKI Jakarta 
                    (34,51 juta ton) akan berubah sebesar <b>{fmt_tanda(koreksi_emisi_listrik, 2)} juta ton CO₂e</b>.
                </p>
            </div>
            <div style="background:#F0FDF4;border:1px solid #BBF7D0;padding:12px 20px;border-radius:14px;text-align:center;">
                <div class="kpi-label">Koreksi Emisi Listrik 2025</div>
                <div style="font-size:1.45rem;font-weight:800;color:#14532D;">{fmt_tanda(koreksi_emisi_listrik, 2)} Jt Ton</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ==========================================================
# HALAMAN 4: MAU KE MANA? (PETA JALAN 2025–2030 & TABEL 3 KOLOM)
# ==========================================================
elif st.session_state["nav_pilihan"] == MENU_HALAMAN[4]:
    daftar_subsektor_tabel = [
        "Green Building Komersial",
        "Labelling Alat Rumah Tangga",
        "Transportasi Rendah Karbon",
        "Efisiensi & Biofuel Industri",
        "Pembangkit Listrik Bersih",
        "Pengelolaan Limbah & PLTSa",
        "Peningkatan RTH (FOLU)",
    ]

    col_r1, col_r2 = st.columns([1.38, 1], gap="medium")

    with col_r1:
        st.markdown('<div class="bento-card">', unsafe_allow_html=True)
        st.markdown('<div class="pill-header">Peta Jalan Target Penurunan Emisi Tahunan 2025–2030 (Tabel 3 Laporan DLH)</div>', unsafe_allow_html=True)
        fig_r = go.Figure()
        for kol, wrn in [
            ("Pembangkit Listrik Bersih", WARNA["hijau_tua"]),
            ("Green Building Komersial", WARNA["hijau_utama"]),
            ("Transportasi Rendah Karbon", WARNA["emas"]),
            ("Efisiensi & Biofuel Industri", WARNA["teal"]),
            ("Labelling Alat Rumah Tangga", WARNA["hijau_muda"]),
            ("Pengelolaan Limbah & PLTSa", WARNA["koral"]),
        ]:
            fig_r.add_trace(go.Bar(
                x=df_road["Tahun"],
                y=df_road[kol] / 1000.0,
                name=kol,
                marker_color=wrn,
            ))
        fig_r.add_trace(go.Scatter(
            x=df_road["Tahun"],
            y=[25.80] * len(df_road),
            name="Capaian Sektoral 2025 (25,80 Jt Ton)",
            mode="lines",
            line=dict(color="#0F172A", width=2.5, dash="dash"),
        ))
        fig_r.update_layout(barmode="stack")
        fig_r.update_xaxes(dtick=1)
        st.plotly_chart(tata_letak(fig_r, "Juta Ton CO₂e", 315), use_container_width=True, config={"displayModeBar": False})

        st.markdown(
            """
            <p class="insight-text" style="margin-top:8px;">
                <b>Pergeseran Tumpuan Dekarbonisasi 2025–2030:</b> Karena target reduksi pembangkit listrik di hulu sudah 
                mendatar di kisaran <b>8,47–9,17 juta ton</b>, maka tambahan reduksi sebesar <b>+12,98 juta ton CO₂e</b> 
                menuju 2030 bertumpu pada efisiensi bangunan hijau komersial, pelabelan alat rumah tangga, dan elektrifikasi transportasi.
            </p>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with col_r2:
        st.markdown('<div class="bento-card">', unsafe_allow_html=True)
        st.markdown('<div class="pill-header">Tabel Interaktif 3 Kolom per Subsektor (2025–2030)</div>', unsafe_allow_html=True)
        sub_pilih = st.selectbox("Pilih Subsektor pada Kolom Tengah:", daftar_subsektor_tabel, index=0)

        # Tabel 3 Kolom Bersih (Tahun | Subsektor Terpilih | Total Target) dalam Ribu Ton (Gg CO2e)
        df_tiga = pd.DataFrame({
            "Tahun": df_road["Tahun"].astype(str),
            f"{sub_pilih} (Gg)": df_road[sub_pilih].map(lambda v: fmt_id(v, 0)),
            "Total Target (Gg)": df_road["Total Target"].map(lambda v: fmt_id(v, 0)),
        })
        st.dataframe(df_tiga, hide_index=True, use_container_width=True, height=248)

        v25 = df_road[sub_pilih].iloc[0]
        v30 = df_road[sub_pilih].iloc[-1]
        tumbuh_sub = ((v30 / v25) - 1) * 100.0
        porsi_2030 = (v30 / df_road["Total Target"].iloc[-1]) * 100.0

        st.markdown(
            f"""
            <div style="background:#F0FDF4;border:1px solid #BBF7D0;border-radius:12px;padding:12px 14px;margin-top:8px;">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
                    <span style="font-size:0.8rem;font-weight:700;color:#14532D;">Target {sub_pilih} (2030)</span>
                    <span class="badge-up">{fmt_tanda(tumbuh_sub, 1)}% dari 2025</span>
                </div>
                <p class="insight-text" style="font-size:0.82rem;">
                    Menyumbang <b>{fmt_id(v30, 0)} Gg CO₂e</b> (<b>{fmt_id(porsi_2030, 1)}%</b> dari total target 34.090 Gg 
                    pada 2030), bergerak dari <b>{fmt_id(v25, 0)} Gg</b> pada tahun 2025.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)
