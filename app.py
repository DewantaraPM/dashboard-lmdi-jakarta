import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ==========================================================
# 1. KONFIGURASI HALAMAN & GAYA VISUAL GREEN BENTO JAKARTA
# ==========================================================
st.set_page_config(
    page_title="Simulator Dekarbonisasi DKI Jakarta 2025–2030",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

FONT = "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
WARNA = {
    "hijau_tua": "#14532D",
    "hijau_utama": "#15803D",
    "hijau_muda": "#10B981",
    "teal": "#0D9488",
    "emas": "#D97706",
    "koral": "#E11D48",
    "abu": "#64748B",
}

st.markdown(
    """
    <style>
    [data-testid="stSidebar"], [data-testid="collapsedControl"], #MainMenu, footer {
        display: none !important;
    }
    .stApp {
        background-color: #EAF3EE;
        font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        color: #0F172A;
    }
    .block-container {
        padding-top: 1.3rem;
        padding-bottom: 2.5rem;
        max-width: 1220px;
    }
    /* Navigasi Kapsul Atas */
    div[role="radiogroup"] {
        background: #FFFFFF;
        padding: 6px 12px;
        border-radius: 999px;
        box-shadow: 0 4px 12px rgba(20, 83, 45, 0.06);
        border: 1px solid #D1E7DD;
        display: flex;
        justify-content: center;
        gap: 8px;
        margin-bottom: 1rem;
    }
    div[role="radiogroup"] label {
        border-radius: 999px !important;
        padding: 6px 18px !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
    }
    /* Hero Banner Ikonik Jakarta */
    .jkt-hero {
        background: linear-gradient(130deg, #0F3F24 0%, #15803D 62%, #0D9488 100%);
        border-radius: 20px;
        padding: 24px 30px 20px 30px;
        color: #FFFFFF;
        box-shadow: 0 10px 24px rgba(20, 83, 45, 0.15);
        margin-bottom: 1.1rem;
    }
    .jkt-badge {
        display: inline-block;
        background: rgba(255, 255, 255, 0.18);
        color: #DCFCE7;
        padding: 4px 12px;
        border-radius: 999px;
        font-size: 0.74rem;
        font-weight: 600;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        margin-bottom: 6px;
    }
    .jkt-title {
        font-size: 1.7rem;
        font-weight: 800;
        margin: 0 0 6px 0;
        color: #FFFFFF;
    }
    .jkt-sub {
        font-size: 0.9rem;
        color: #E2F8EC;
        max-width: 720px;
        line-height: 1.5;
        margin: 0;
        text-align: justify;
    }
    /* Kartu Bento */
    .bento-card {
        background: #FFFFFF;
        border-radius: 18px;
        padding: 18px 20px;
        border: 1px solid #DCECE3;
        box-shadow: 0 4px 12px rgba(15, 63, 36, 0.04);
        margin-bottom: 14px;
    }
    .bento-green {
        background: linear-gradient(135deg, #14532D 0%, #15803D 100%);
        color: #FFFFFF;
        border-radius: 18px;
        padding: 18px 20px;
        box-shadow: 0 8px 18px rgba(20, 83, 45, 0.14);
        margin-bottom: 14px;
    }
    .pill-header {
        background: #14532D;
        color: #FFFFFF;
        font-size: 0.8rem;
        font-weight: 700;
        padding: 5px 15px;
        border-radius: 999px;
        display: inline-block;
        margin-bottom: 10px;
    }
    .kpi-label {
        font-size: 0.78rem;
        color: #64748B;
        font-weight: 600;
        margin-bottom: 3px;
    }
    .kpi-val {
        font-size: 1.6rem;
        font-weight: 800;
        color: #0F172A;
        margin-bottom: 5px;
    }
    .badge-ok {
        background: #DCFCE7;
        color: #15803D;
        padding: 3px 10px;
        border-radius: 999px;
        font-size: 0.74rem;
        font-weight: 700;
    }
    .badge-warn {
        background: #FEF3C7;
        color: #B45309;
        padding: 3px 10px;
        border-radius: 999px;
        font-size: 0.74rem;
        font-weight: 700;
    }
    .badge-gap {
        background: #FFE4E6;
        color: #BE123C;
        padding: 3px 10px;
        border-radius: 999px;
        font-size: 0.74rem;
        font-weight: 700;
    }
    .justify-box {
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


def fmt_id(x, d=2):
    return f"{x:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def fmt_tanda(x, d=2):
    if abs(x) < 0.5 * 10 ** (-d):
        return fmt_id(0, d)
    return ("+" if x > 0 else "−") + fmt_id(abs(x), d)


def tata_letak(fig, y_title=None, tinggi=285, show_legend=True):
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


def buat_gauge(nilai, maks, judul, satuan="%", warna="#15803D", tinggi=170):
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=nilai,
            number={"suffix": satuan, "font": {"size": 25, "color": "#0F172A", "family": FONT}},
            title={"text": judul, "font": {"size": 11.5, "color": "#475569", "family": FONT}},
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
        margin=dict(l=14, r=14, t=28, b=6),
        height=tinggi,
    )
    return fig


# ==========================================================
# 2. DATA TERKURASI (TABEL 3 & RINGKASAN EKSEKUTIF DLH 2026)
# ==========================================================
@st.cache_data
def muat_data_fokus():
    # Tabel 3 Laporan DLH 2026 dikonversi ke Juta Ton CO2e (1 Juta Ton = 1.000 Gg)
    df_pilar = pd.DataFrame({
        "Tahun": [2025, 2026, 2027, 2028, 2029, 2030],
        "Bangunan Komersial (Green Building)": [3.582, 4.513, 5.450, 6.396, 7.351, 8.309],
        "Transportasi Rendah Karbon": [4.309, 4.525, 4.820, 5.198, 5.656, 6.191],
        "Efisiensi & Biofuel Industri": [1.864, 2.621, 3.330, 3.991, 4.606, 5.178],
        "Rumah Tangga (Labelling Alat)": [2.442, 2.610, 2.814, 3.054, 3.329, 3.630],
        "Pembangkit Listrik Bersih (Hulu)": [8.471, 8.251, 8.546, 8.775, 8.995, 9.170],
        "Pengelolaan Limbah & RTH": [0.445, 0.658, 0.826, 1.105, 1.334, 1.614],
        "Total Target Resmi": [21.114, 23.178, 25.789, 28.521, 31.235, 34.090],
    })

    # Rincian Aksi Spesifik di Tabel 3 (dalam Ribu Ton / Gg CO2e) untuk Tabel 3 Kolom
    df_rincian = pd.DataFrame({
        "Tahun": [2025, 2026, 2027, 2028, 2029, 2030],
        "Green Building Gedung Komersial": [3582, 4476, 5383, 6306, 7245, 8194],
        "Labelling Rumah Tangga (AC, Lampu, Kulkas)": [2442, 2610, 2814, 3054, 3329, 3630],
        "Mandatori Biofuel Transportasi": [1975, 2177, 2379, 2581, 2783, 2987],
        "Boiler, Motor Listrik & Manajer Energi Industri": [1282, 1671, 2073, 2490, 2922, 2870],
        "Mandatori Biofuel Industri": [346, 685, 962, 1177, 1331, 1425],
        "PLTSa (Pengolahan Sampah & Pembangkit)": [750, 933, 1197, 1448, 1796, 2055],
        "Peremajaan & Uji Emisi Transportasi": [1229, 1130, 1077, 1072, 1114, 1194],
        "Angkutan Massal (BRT, MRT, LRT, KRL)": [1086, 1165, 1246, 1329, 1413, 1501],
        "Kendaraan Listrik (EV & Motor Listrik)": [13, 20, 72, 157, 275, 427],
        "Jaringan Gas (Jargas) Industri": [236, 265, 295, 324, 353, 878],
        "Fuel Switch & Efisiensi Pembangkit (Muara Karang & Priok)": [7737, 7530, 7712, 7949, 7988, 8195],
        "Total Target (Gg)": [21114, 23178, 25789, 28521, 31235, 34090],
    })
    return df_pilar, df_rincian


df_pilar, df_rincian = muat_data_fokus()

# ==========================================================
# 3. HERO BANNER IKONIK JAKARTA & NAVIGASI 3 BAGIAN
# ==========================================================
st.markdown(
    """
    <div class="jkt-hero">
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:16px;">
            <div style="flex:1;min-width:300px;">
                <div class="jkt-badge">🌿 Dinas Lingkungan Hidup Provinsi DKI Jakarta • Laporan Akhir 2026</div>
                <div class="jkt-title">Simulator Peta Jalan Dekarbonisasi Jakarta 2025–2030</div>
                <p class="jkt-sub">
                    Memetakan posisi penurunan emisi DKI Jakarta tahun 2025 dan menyimulasikan ketercapaian target 
                    aksi mitigasi menuju sasaran 32% (34,09 Juta Ton CO₂e) pada tahun 2030.
                </p>
            </div>
            <!-- Siluet Vektor Monas & Gigi Balang Betawi -->
            <div style="opacity:0.92;">
                <svg width="240" height="90" viewBox="0 0 250 96" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M0 90 L10 80 L20 90 L30 80 L40 90 L50 80 L60 90 L70 80 L80 90 L90 80 L100 90 L110 80 L120 90 L130 80 L140 90 L150 80 L160 90 L170 80 L180 90 L190 80 L200 90 L210 80 L220 90 L230 80 L240 90 L250 80 L250 96 L0 96 Z" fill="rgba(255,255,255,0.18)"/>
                    <rect x="22" y="42" width="22" height="42" rx="2" fill="rgba(255,255,255,0.22)"/>
                    <rect x="50" y="30" width="26" height="54" rx="2" fill="rgba(255,255,255,0.28)"/>
                    <rect x="176" y="34" width="24" height="50" rx="2" fill="rgba(255,255,255,0.25)"/>
                    <rect x="206" y="46" width="22" height="38" rx="2" fill="rgba(255,255,255,0.20)"/>
                    <path d="M98 84 L152 84 L144 74 L106 74 Z" fill="rgba(255,255,255,0.45)"/>
                    <path d="M92 66 L158 66 L146 74 L104 74 Z" fill="rgba(255,255,255,0.65)"/>
                    <rect x="121" y="22" width="8" height="44" fill="#FFFFFF"/>
                    <rect x="116" y="19" width="18" height="4" rx="1" fill="#FFFFFF"/>
                    <path d="M125 6 C129 11 131 15 125 19 C119 15 121 11 125 6 Z" fill="#FBBF24"/>
                </svg>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

HALAMAN = [
    "🏠 1. Beranda: Posisi Jakarta 2025",
    "🎛️ 2. Simulator Target 2030 (Stress-Test)",
    "📋 3. Peta Jalan & Tabel 3 Kolom",
]

if "hal_fokus" not in st.session_state:
    st.session_state["hal_fokus"] = HALAMAN[0]

nav = st.radio(
    "Navigasi:",
    HALAMAN,
    index=HALAMAN.index(st.session_state["hal_fokus"]),
    horizontal=True,
    label_visibility="collapsed",
)
if nav != st.session_state["hal_fokus"]:
    st.session_state["hal_fokus"] = nav
    st.rerun()

# ==========================================================
# BAGIAN 1: BERANDA — POSISI JAKARTA 2025 & TEMUAN KUNCI
# ==========================================================
if st.session_state["hal_fokus"] == HALAMAN[0]:
    # Baris 1: 1 Kartu Hijau Utama + 3 Semi-Circle Gauge
    c1, c2, c3, c4 = st.columns([1.3, 1, 1, 1], gap="small")
    with c1:
        st.markdown(
            """
            <div class="bento-green">
                <div style="font-size:0.75rem;opacity:0.85;font-weight:600;text-transform:uppercase;">Capaian Reduksi Sektoral 2025</div>
                <div style="font-size:2.05rem;font-weight:800;margin:4px 0;">25,80 Jt Ton</div>
                <div style="font-size:0.83rem;color:#DCFCE7;margin-bottom:10px;">Selisih Baseline (92,0) vs Inventori (66,2)</div>
                <div style="background:rgba(255,255,255,0.16);padding:7px 12px;border-radius:10px;font-size:0.8rem;">
                    🎯 Target 2030: <b>34,09 Jt Ton (32%)</b>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown('<div class="bento-card" style="padding:8px 10px;">', unsafe_allow_html=True)
        st.plotly_chart(buat_gauge(28.0, 32.0, "Posisi 2025 vs Target 32%", "%", WARNA["hijau_utama"]), use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="bento-card" style="padding:8px 10px;">', unsafe_allow_html=True)
        st.plotly_chart(buat_gauge(52.1, 100.0, "Porsi Listrik pada Emisi DKI", "%", WARNA["teal"]), use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)
    with c4:
        st.markdown('<div class="bento-card" style="padding:8px 10px;">', unsafe_allow_html=True)
        st.plotly_chart(buat_gauge(94.6, 100.0, "Porsi Hilir di Tambahan 2030", "%", WARNA["emas"]), use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    # Baris 2: 2 Visual Konteks (Menjawab Kelemahan 1 & Kelemahan 2 Opsi 1)
    v_kiri, v_kanan = st.columns([1, 1.35], gap="medium")

    with v_kiri:
        st.markdown('<div class="bento-card">', unsafe_allow_html=True)
        st.markdown('<div class="pill-header">Dari Mana Emisi Aktual Jakarta 2025? (66,22 Jt Ton)</div>', unsafe_allow_html=True)
        fig_pie = go.Figure(go.Pie(
            labels=["Listrik PLN (Indirect)", "Transportasi BBM", "Pembangkit Listrik", "Industri & Bangunan", "Limbah"],
            values=[34.51, 18.29, 7.13, 3.89, 2.44],
            hole=0.62,
            marker=dict(colors=[WARNA["teal"], WARNA["emas"], WARNA["hijau_tua"], WARNA["hijau_muda"], WARNA["koral"]]),
            textinfo="percent",
        ))
        fig_pie.update_layout(
            annotations=[dict(text="<b>66,22</b><br>Jt Ton", x=0.5, y=0.5, font_size=16, showarrow=False)],
            margin=dict(l=8, r=8, t=8, b=8), height=230, paper_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h", yanchor="bottom", y=-0.24, xanchor="center", x=0.5, font=dict(size=10.5)),
        )
        st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})
        st.markdown(
            """
            <p class="justify-box" style="margin-top:16px;">
                Lebih dari separuh emisi Jakarta (<b>52,1%</b> atau 34,51 juta ton) berasal dari penggunaan listrik di bangunan 
                dan rumah tangga, disusul transportasi darat (<b>27,6%</b>).
            </p>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with v_kanan:
        st.markdown('<div class="bento-card">', unsafe_allow_html=True)
        st.markdown('<div class="pill-header">Memahami 3 Angka Reduksi Tahun 2025 & Target 2030 di Laporan DLH</div>', unsafe_allow_html=True)
        kat_3 = [
            "1. Akumulasi Proyek<br>(Tabel 2 Bab IV)",
            "2. Target Rencana 2025<br>(Tabel 3 Bab VI)",
            "3. Capaian Sektoral 2025<br>(Baseline − Inventori)",
            "4. Target Akhir 2030<br>(Tabel 3: 32%)",
        ]
        val_3 = [16.44, 21.11, 25.80, 34.09]
        wrn_3 = ["#94A3B8", WARNA["teal"], WARNA["hijau_utama"], WARNA["hijau_tua"]]
        fig_3 = go.Figure(go.Bar(
            x=kat_3, y=val_3, marker_color=wrn_3, marker_cornerradius=8, width=0.46,
            text=[f"<b>{fmt_id(v)} Jt Ton</b>" for v in val_3], textposition="outside",
        ))
        fig_3 = tata_letak(fig_3, "Juta Ton CO₂e", 230, show_legend=False)
        fig_3.update_layout(yaxis=dict(range=[0, 40]))
        st.plotly_chart(fig_3, use_container_width=True, config={"displayModeBar": False})
        st.markdown(
            """
            <p class="justify-box" style="margin-top:6px;">
                <b>Mengapa ada 3 angka berbeda pada tahun 2025?</b> Sesuai Bab IV Laporan DLH, angka <b>25,80 juta ton</b> 
                adalah penurunan makro (selisih <i>baseline</i> dikurangi inventori), angka <b>21,11 juta ton</b> adalah kuota 
                rencana aksi pada Tabel 3, sedangkan <b>16,44 juta ton</b> adalah penjumlahan proyek terverifikasi. Untuk 
                mencapai <b>34,09 juta ton</b> pada 2030, kuota Tabel 3 wajib ditingkatkan sebesar <b>+12,98 juta ton</b>.
            </p>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)


# ==========================================================
# BAGIAN 2: SIMULATOR STRESS-TEST & AUTO GOAL-SEEK 2025–2030
# ==========================================================
elif st.session_state["hal_fokus"] == HALAMAN[1]:
    st.markdown('<div class="bento-card">', unsafe_allow_html=True)
    st.markdown('<div class="pill-header">1. Pilih Skenario atau Geser Pencapaian 5 Pilar Aksi Mitigasi (2025–2030)</div>', unsafe_allow_html=True)

    preset = st.radio(
        "Preset Skenario:",
        [
            "Sesuai Target DLH (100%)",
            "Risiko Hilir Melambat (Bangunan & RT 65%)",
            "Akselerasi Hilir (Bangunan & Transportasi 125%)",
            "Atur Sendiri (Custom Stress-Test)",
        ],
        index=0,
        horizontal=True,
        label_visibility="collapsed",
    )

    peta_preset = {
        "Sesuai Target DLH (100%)": (100, 100, 100, 100, 100),
        "Risiko Hilir Melambat (Bangunan & RT 65%)": (65, 75, 85, 65, 100),
        "Akselerasi Hilir (Bangunan & Transportasi 125%)": (125, 125, 110, 120, 100),
    }
    d_kom, d_trn, d_ind, d_rt, d_hulu = peta_preset.get(preset, (100, 100, 100, 100, 100))
    kunci = preset != "Atur Sendiri (Custom Stress-Test)"

    s1, s2, s3, s4, s5 = st.columns(5, gap="small")
    with s1:
        p_kom = st.slider("🏢 Green Building Komersial (%)", 0, 150, d_kom, step=5, disabled=kunci, help="Target 2030: 8,31 Juta Ton CO₂e")
    with s2:
        p_trn = st.slider("🚆 Transportasi & EV (%)", 0, 150, d_trn, step=5, disabled=kunci, help="Target 2030: 6,19 Juta Ton CO₂e")
    with s3:
        p_ind = st.slider("🏭 Efisiensi & Biofuel Industri (%)", 0, 150, d_ind, step=5, disabled=kunci, help="Target 2030: 5,18 Juta Ton CO₂e")
    with s4:
        p_rt = st.slider("🏠 Labelling Rumah Tangga (%)", 0, 150, d_rt, step=5, disabled=kunci, help="Target 2030: 3,63 Juta Ton CO₂e")
    with s5:
        p_hulu = st.slider("⚡ Pembangkit & Limbah (%)", 0, 150, d_hulu, step=5, disabled=kunci, help="Target 2030: 10,78 Juta Ton CO₂e")
    st.markdown("</div>", unsafe_allow_html=True)

    # Perhitungan Simulasi 2025-2030
    sim_series = (
        df_pilar["Bangunan Komersial (Green Building)"] * (p_kom / 100.0)
        + df_pilar["Transportasi Rendah Karbon"] * (p_trn / 100.0)
        + df_pilar["Efisiensi & Biofuel Industri"] * (p_ind / 100.0)
        + df_pilar["Rumah Tangga (Labelling Alat)"] * (p_rt / 100.0)
        + (df_pilar["Pembangkit Listrik Bersih (Hulu)"] + df_pilar["Pengelolaan Limbah & RTH"]) * (p_hulu / 100.0)
    )

    target_2030 = 34.090
    hasil_2030 = sim_series.iloc[-1]
    selisih_2030 = hasil_2030 - target_2030
    persen_tercapai = (hasil_2030 / target_2030) * 100.0
    ekuivalen_baseline_2030 = (hasil_2030 / 106.53) * 100.0  # Baseline 2030 = 106,53 Jt Ton

    # Baris Visual Hasil Simulasi (70% Visual)
    g1, g2 = st.columns([1.4, 1], gap="medium")

    with g1:
        st.markdown('<div class="bento-card">', unsafe_allow_html=True)
        st.markdown('<div class="pill-header">Lintasan Reduksi Emisi 2025–2030: Target Resmi Tabel 3 vs Hasil Simulasi</div>', unsafe_allow_html=True)
        fig_sim = go.Figure()
        fig_sim.add_trace(go.Scatter(
            x=df_pilar["Tahun"], y=df_pilar["Total Target Resmi"],
            name="Jalur Target Resmi Tabel 3 (34,09 Jt Ton)",
            mode="lines+markers", line=dict(color=WARNA["abu"], width=2.5, dash="dash"),
        ))
        fig_sim.add_trace(go.Scatter(
            x=df_pilar["Tahun"], y=sim_series,
            name="Hasil Simulasi Skenario Ini",
            mode="lines+markers", fill="tozeroy", fillcolor="rgba(21, 128, 61, 0.14)",
            line=dict(color=WARNA["hijau_utama"], width=3.5, shape="spline"),
        ))
        fig_sim.update_xaxes(dtick=1)
        st.plotly_chart(tata_letak(fig_sim, "Juta Ton CO₂e", 285), use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    with g2:
        st.markdown('<div class="bento-card">', unsafe_allow_html=True)
        st.markdown('<div class="pill-header">Status Ketercapaian Target 2030</div>', unsafe_allow_html=True)
        warna_g = WARNA["hijau_utama"] if selisih_2030 >= -0.05 else WARNA["emas"] if selisih_2030 >= -4.0 else WARNA["koral"]
        st.plotly_chart(
            buat_gauge(hasil_2030, 40.0, f"Reduksi 2030 (Target: 34,09 Jt Ton / 32%)", " Jt", warna_g, tinggi=180),
            use_container_width=True, config={"displayModeBar": False},
        )

        # Fitur Advanced: Auto Goal-Seek Recommendation
        if selisih_2030 < -0.05:
            defisit = abs(selisih_2030)
            butuh_gb_ekstra = (defisit / 8.309) * 100.0
            butuh_rt_ekstra = (defisit / 3.630) * 100.0
            pesan_goalseek = (
                f"Terjadi <b>defisit {fmt_id(defisit)} juta ton CO₂e</b> ({fmt_id(100 - persen_tercapai, 1)}% di bawah target 2030). "
                f"<b>Rekomendasi Auto Goal-Seek:</b> Defisit ini dapat ditutup dengan meningkatkan realisasi "
                f"<i>Green Building Komersial</i> sebesar <b>+{fmt_id(butuh_gb_ekstra, 0)}%</b> atau memperluas "
                f"<i>Labelling Alat Rumah Tangga</i> dan <i>Transportasi Listrik</i>."
            )
            badge_status = f'<span class="badge-gap">Defisit {fmt_id(defisit)} Jt Ton ({fmt_id(ekuivalen_baseline_2030, 1)}% Baseline)</span>'
        else:
            pesan_goalseek = (
                f"Target dekarbonisasi 2030 <b>tercapai ({fmt_id(persen_tercapai, 1)}%)</b> dengan total penurunan "
                f"<b>{fmt_id(hasil_2030)} juta ton CO₂e</b> (setara <b>{fmt_id(ekuivalen_baseline_2030, 1)}%</b> di bawah Baseline 2030) "
                f"dan surplus sebesar <b>+{fmt_id(selisih_2030)} juta ton CO₂e</b>."
            )
            badge_status = f'<span class="badge-ok">Target Tercapai ({fmt_id(ekuivalen_baseline_2030, 1)}% Baseline)</span>'

        st.markdown(
            f"""
            <div style="margin-top:4px;">
                <div style="margin-bottom:8px;">{badge_status}</div>
                <p class="justify-box">{pesan_goalseek}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)


# ==========================================================
# BAGIAN 3: PETA JALAN AKSI & TABEL INTERAKTIF 3 KOLOM
# ==========================================================
elif st.session_state["hal_fokus"] == HALAMAN[2]:
    col_p1, col_p2 = st.columns([1.28, 1], gap="medium")

    with col_p1:
        st.markdown('<div class="bento-card">', unsafe_allow_html=True)
        st.markdown('<div class="pill-header">Siapa Tumpuan Pertambahan Reduksi Baru Antara 2025 dan 2030? (+12,98 Jt Ton)</div>', unsafe_allow_html=True)
        pilar_names = [
            "Bangunan Komersial (Green Building)",
            "Efisiensi & Biofuel Industri",
            "Transportasi Rendah Karbon",
            "Rumah Tangga (Labelling Alat)",
            "Pengelolaan Limbah & RTH",
            "Pembangkit Listrik Bersih (Hulu)",
        ]
        tambahan_25_30 = [df_pilar[p].iloc[-1] - df_pilar[p].iloc[0] for p in pilar_names]
        wrn_pilar = [WARNA["hijau_utama"], WARNA["teal"], WARNA["emas"], WARNA["hijau_muda"], WARNA["koral"], "#94A3B8"]

        fig_add = go.Figure(go.Bar(
            x=tambahan_25_30,
            y=pilar_names,
            orientation="h",
            marker_color=wrn_pilar,
            marker_cornerradius=7,
            text=[f"+{fmt_id(v)} Jt Ton ({v/12.976*100:.1f}%)" for v in tambahan_25_30],
            textposition="auto",
        ))
        fig_add.update_layout(yaxis=dict(autorange="reversed"))
        st.plotly_chart(tata_letak(fig_add, "Tambahan Reduksi 2025→2030 (Juta Ton CO₂e)", 275, show_legend=False), use_container_width=True, config={"displayModeBar": False})

        st.markdown(
            """
            <p class="justify-box" style="margin-top:8px;">
                <b>Temuan Kunci Tabel 3:</b> Dari total tambahan target reduksi sebesar <b>+12,98 juta ton CO₂e</b> sepanjang 
                2025–2030, pembangkit listrik di hulu hanya menambah <b>+0,70 juta ton (5,4%)</b> karena kapasitas konversi 
                gas sudah mendekati batas maksimum. Sebesar <b>94,6%</b> sisanya wajib dikejar dari sektor hilir, terutama 
                <b>Green Building Komersial (+4,73 juta ton)</b> dan <b>Industri (+3,31 juta ton)</b>.
            </p>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with col_p2:
        st.markdown('<div class="bento-card">', unsafe_allow_html=True)
        st.markdown('<div class="pill-header">Tabel Interaktif 3 Kolom (2025–2030)</div>', unsafe_allow_html=True)

        opsi_aksi_tabel = [c for c in df_rincian.columns if c not in ["Tahun", "Total Target (Gg)"]]
        aksi_terpilih = st.selectbox("Pilih Program Aksi Mitigasi:", opsi_aksi_tabel, index=0)

        # Tabel 3 Kolom (Tahun | Aksi Terpilih | Total Target)
        tabel_3_kolom = pd.DataFrame({
            "Tahun": df_rincian["Tahun"].astype(str),
            f"{aksi_terpilih} (Gg)": df_rincian[aksi_terpilih].map(lambda v: f"{v:,.0f}".replace(",", ".")),
            "Total Target (Gg)": df_rincian["Total Target (Gg)"].map(lambda v: f"{v:,.0f}".replace(",", ".")),
        })
        st.dataframe(tabel_3_kolom, hide_index=True, use_container_width=True, height=245)

        a25 = df_rincian[aksi_terpilih].iloc[0]
        a30 = df_rincian[aksi_terpilih].iloc[-1]
        naik_gg = a30 - a25
        porsi_30 = (a30 / 34090.0) * 100.0

        st.markdown(
            f"""
            <div style="background:#F0FDF4;border:1px solid #BBF7D0;border-radius:12px;padding:10px 14px;margin-top:6px;">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
                    <span style="font-size:0.78rem;font-weight:700;color:#14532D;">Sorotan Target 2030 (1 Jt Ton = 1.000 Gg)</span>
                    <span class="badge-ok">{fmt_id(porsi_30, 1)}% dari Total 2030</span>
                </div>
                <p class="justify-box" style="font-size:0.81rem;">
                    Target <b>{aksi_terpilih}</b> bergerak dari <b>{a25:,.0f} Gg</b> (2025) menjadi 
                    <b>{a30:,.0f} Gg CO₂e</b> (2030), atau berubah sebesar <b>{naik_gg:+,.0f} Gg CO₂e</b>.
                </p>
            </div>
            """.replace(",", "."),
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)
