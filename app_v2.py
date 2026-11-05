import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# ==========================================================
# KONFIGURASI HALAMAN & GAYA VISUAL
# ==========================================================
st.set_page_config(
    page_title="Dashboard Emisi GRK Rumah Tangga DKI Jakarta",
    page_icon="🌿",
    layout="wide",
)

FONT = "Segoe UI, Roboto, Helvetica, Arial, sans-serif"
WARNA = {
    "listrik": "#2F5D8A",
    "lpg": "#E0A458",
    "gas": "#6BA292",
    "aktual": "#52606D",
    "bau": "#9AA5B1",
    "simulasi": "#1D4E89",
    "cpos": "#D08C2D",
    "nze": "#2A9D8F",
}

st.markdown(
    """
    <style>
    .block-container { padding-top: 1.8rem; padding-bottom: 3rem; max-width: 1200px; }
    .stApp, .stApp p, .stApp li, .stApp label, .stApp td, .stApp th,
    .stApp h1, .stApp h2, .stApp h3, .stApp h4 {
        font-family: -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    .hero-banner {
        background: linear-gradient(135deg, #163A59 0%, #1F5E6B 55%, #2D8A7B 100%);
        color: white; padding: 24px 28px; border-radius: 16px;
        margin-bottom: 1.2rem; box-shadow: 0 8px 20px rgba(22, 58, 89, 0.12);
    }
    .hero-title { font-size: 1.7rem; font-weight: 700; margin: 0 0 6px 0; color: white; }
    .hero-sub { font-size: 0.96rem; opacity: 0.92; margin: 0 0 14px 0; color: #E6FFFA; }
    .hero-pills span {
        display: inline-block; background: rgba(255,255,255,0.16); color: white;
        padding: 5px 13px; border-radius: 999px; font-size: 0.82rem; margin-right: 8px; font-weight: 500;
    }
    .kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 1.4rem; }
    .kpi-card {
        background: white; border: 1px solid #E2E8F0; border-radius: 14px;
        padding: 16px 18px; box-shadow: 0 2px 6px rgba(0,0,0,0.03);
        border-top: 4px solid #2F5D8A;
    }
    .kpi-card.c1 { border-top-color: #C8553D; }
    .kpi-card.c2 { border-top-color: #E0A458; }
    .kpi-card.c3 { border-top-color: #2F5D8A; }
    .kpi-card.c4 { border-top-color: #2A9D8F; }
    .kpi-top { font-size: 0.82rem; color: #64748B; margin-bottom: 4px; font-weight: 500; }
    .kpi-num { font-size: 1.6rem; font-weight: 700; color: #0F172A; margin-bottom: 4px; }
    .kpi-sub { font-size: 0.8rem; font-weight: 600; }
    .kpi-sub.red { color: #C8553D; }
    .kpi-sub.green { color: #2A9D8F; }
    .kpi-sub.gray { color: #475569; }
    .res-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; margin: 10px 0 18px 0; }
    .kotak {
        border-left: 4px solid #1D4E89; background: rgba(29,78,137,0.06);
        padding: 14px 18px; border-radius: 0 10px 10px 0; margin: 8px 0 18px 0;
    }
    .kotak-judul { font-weight: 600; margin-bottom: 6px; color: #0F172A; }
    .bar-wrap {
        height: 14px; border-radius: 999px; overflow: hidden; display: flex;
        background: #E2E8F0; margin: 8px 0 6px 0;
    }
    button[data-baseweb="tab"] p { font-weight: 600; font-size: 0.96rem; }
    #MainMenu, footer { visibility: hidden; }
    @media (max-width: 900px) {
        .kpi-grid, .res-grid { grid-template-columns: 1fr; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def fmt_id(x, d=0):
    return f"{x:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def fmt_tanda(x, d=0):
    if abs(x) < 0.5 * 10 ** (-d):
        return fmt_id(0, d)
    return ("+" if x > 0 else "−") + fmt_id(abs(x), d)


def kotak(judul, isi_html):
    st.markdown(
        f'<div class="kotak"><div class="kotak-judul">{judul}</div>{isi_html}</div>',
        unsafe_allow_html=True,
    )


def tata_letak(fig, y_title=None, tinggi=350):
    fig.update_layout(
        template="plotly_white",
        font=dict(family=FONT, size=12, color="#1f2933"),
        paper_bgcolor="white",
        plot_bgcolor="white",
        margin=dict(l=10, r=10, t=32, b=10),
        height=tinggi,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, title_text=""),
        hovermode="x unified",
        yaxis=dict(title=y_title, gridcolor="#E8ECEF", zerolinecolor="#CBD2D9"),
        xaxis=dict(showgrid=False),
    )
    return fig


def tampil(fig):
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# ==========================================================
# 1. DATA RESMI (LAPORAN AKHIR DLH DKI JAKARTA 2026)
# ==========================================================
@st.cache_data
def muat_data():
    data_historis = {
        "Tahun": list(range(2010, 2025)),
        "Penduduk_Juta": [9.64, 9.89, 9.86, 9.97, 10.08, 10.18, 10.28, 10.37, 10.47, 10.56, 10.56, 10.61, 10.68, 10.67, 10.68],
        "PDRB_Konstan_T": [1080.00, 1260.00, 1222.53, 1296.69, 1373.39, 1454.56, 1539.92, 1635.36, 1735.21, 1836.24, 1792.29, 1856.00, 1953.49, 2050.47, 2151.04],
        "EF_Listrik_MWh": [0.830, 0.880, 0.927, 0.967, 0.949, 1.023, 0.990, 0.897, 0.894, 0.906, 0.902, 0.896, 0.901, 0.903, 0.903],
        "C_Listrik": [7560.0, 8400.0, 9590.0, 11100.0, 10500.0, 11700.0, 12500.0, 11300.0, 11800.0, 12600.0, 13100.0, 13100.0, 13300.0, 14100.0, 14828.0],
        "C_LPG": [982.0, 1044.0, 1082.0, 1076.0, 1076.0, 1393.0, 1366.0, 1444.0, 1447.0, 1266.0, 1289.0, 1300.0, 1318.0, 1338.0, 1348.0],
        "C_Gas": [0.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 7.0, 7.0, 7.0, 4.0],
    }
    d = pd.DataFrame(data_historis)
    d["EF_Listrik_TJ"] = d["EF_Listrik_MWh"] / 3.6  # 1 GWh = 3,6 TJ
    d["EF_LPG_TJ"] = 0.06537                        # Tabel 3.5: 65.370 kg CO2/TJ
    d["EF_Gas_TJ"] = 0.05764                        # Tabel 3.5: 57.640 kg CO2/TJ
    d["E_Listrik_TJ"] = d["C_Listrik"] / d["EF_Listrik_TJ"]
    d["E_LPG_TJ"] = d["C_LPG"] / d["EF_LPG_TJ"]
    d["E_Gas_TJ"] = d["C_Gas"] / d["EF_Gas_TJ"]
    d["E_Total_TJ"] = d["E_Listrik_TJ"] + d["E_LPG_TJ"] + d["E_Gas_TJ"]
    d["C_Total_Gg"] = d["C_Listrik"] + d["C_LPG"] + d["C_Gas"]
    d["Emisi_per_Kapita"] = d["C_Total_Gg"] / d["Penduduk_Juta"] / 1000.0
    return d


df = muat_data()

# ==========================================================
# 2. SIDEBAR IDENTITAS MAGANG
# ==========================================================
with st.sidebar:
    st.markdown("#### Dashboard Output Magang")
    st.caption(
        "**Visualisasi Profil Historis (2010–2024) dan Simulasi Capaian Target Mitigasi "
        "Emisi GRK Sektor Rumah Tangga Provinsi DKI Jakarta (2025–2050)**"
    )
    st.caption(
        "**Penyusun:** Dewantara Putra Makmur  \n"
        "**Instansi Magang:** Bidang Tata Lingkungan, Dinas Lingkungan Hidup Provinsi DKI Jakarta  \n"
        "**Program Studi:** Meteorologi Terapan, IPB University"
    )
    st.divider()
    st.markdown("#### Sumber Data Resmi")
    st.caption(
        "Seluruh data diolah dari **Laporan Akhir Inventarisasi Profil Emisi dan Pelaporan "
        "Penurunan Emisi Gas Rumah Kaca Provinsi DKI Jakarta (DLH 2026)**:\n"
        "- **Bab III & V:** Emisi historis & faktor emisi (2010–2024)\n"
        "- **Bab IV & VI (Tabel 3–5):** Target reduksi tahunan (2025–2030) & skenario CPOS/NZE (2035–2050)"
    )

# ==========================================================
# 3. HEADER & 4 KARTU METRIK UTAMA
# ==========================================================
r10 = df[df["Tahun"] == 2010].iloc[0]
r19 = df[df["Tahun"] == 2019].iloc[0]
r24 = df[df["Tahun"] == 2024].iloc[0]
c10, c19, c24 = r10["C_Total_Gg"], r19["C_Total_Gg"], r24["C_Total_Gg"]
porsi_listrik = r24["C_Listrik"] / c24
tumbuh_total = (c24 / c10 - 1) * 100
kapita10 = r10["Emisi_per_Kapita"]
kapita24 = r24["Emisi_per_Kapita"]
TARGET_LABELLING_2030 = 3630.0

st.markdown(
    """
    <div class="hero-banner">
        <div class="hero-title">Dashboard Emisi GRK Sektor Rumah Tangga DKI Jakarta</div>
        <div class="hero-sub">Pemantauan tren emisi historis (2010–2024) dan simulasi pencapaian target aksi mitigasi daerah menuju 2030 & 2050.</div>
        <div class="hero-pills">
            <span>📊 Lihat datanya</span>
            <span>🎛️ Coba simulasinya</span>
            <span>📥 Unduh tabelnya</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="kpi-grid">
        <div class="kpi-card c1">
            <div class="kpi-top">🏢 Total emisi 2024</div>
            <div class="kpi-num">{fmt_id(c24)} Gg</div>
            <div class="kpi-sub red">{fmt_tanda(tumbuh_total, 1)}% dibanding 2010 ({fmt_id(c10)} Gg)</div>
        </div>
        <div class="kpi-card c2">
            <div class="kpi-top">👥 Emisi per penduduk 2024</div>
            <div class="kpi-num">{fmt_id(kapita24, 2)} tCO₂e</div>
            <div class="kpi-sub red">{fmt_tanda((kapita24 / kapita10 - 1) * 100, 1)}% dibanding 2010</div>
        </div>
        <div class="kpi-card c3">
            <div class="kpi-top">⚡ Porsi emisi dari listrik</div>
            <div class="kpi-num">{fmt_id(porsi_listrik * 100, 1)}%</div>
            <div class="kpi-sub gray">{fmt_id(r24['C_Listrik'])} Gg CO₂e pada 2024</div>
        </div>
        <div class="kpi-card c4">
            <div class="kpi-top">🎯 Target reduksi labelling 2030</div>
            <div class="kpi-num">{fmt_id(TARGET_LABELLING_2030)} Gg</div>
            <div class="kpi-sub green">setara {fmt_id(TARGET_LABELLING_2030 / c24 * 100, 1)}% emisi 2024 (DLH)</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ==========================================================
# 4. NAVIGASI 3 TAB SEDERHANA
# ==========================================================
tab0, tab1, tab2 = st.tabs(["🏠 Ringkasan", "📊 Data Historis", "🎛️ Simulasi Mitigasi"])

# ==========================================================
# TAB 0: RINGKASAN
# ==========================================================
with tab0:
    kotak(
        "Sorotan Utama Profil Emisi Rumah Tangga DKI Jakarta",
        "<ul>"
        f"<li><b>Pertumbuhan Emisi (2010–2024):</b> Emisi GRK sektor rumah tangga meningkat dari <b>{fmt_id(c10)} Gg</b> menjadi <b>{fmt_id(c24)} Gg CO₂e</b> (<b>{fmt_tanda(tumbuh_total, 1)}%</b>), dengan rata-rata pertumbuhan <b>3,1% per tahun</b> pada lima tahun terakhir (2019–2024).</li>"
        f"<li><b>Dominasi Konsumsi Listrik:</b> Sebesar <b>{fmt_id(porsi_listrik * 100, 1)}%</b> ({fmt_id(r24['C_Listrik'])} Gg CO₂e) emisi rumah tangga berasal dari emisi tidak langsung pemakaian listrik PLN, sedangkan sisanya berasal dari penggunaan LPG ({fmt_id(r24['C_LPG'])} Gg) dan gas bumi ({fmt_id(r24['C_Gas'])} Gg).</li>"
        f"<li><b>Fokus Aksi Mitigasi Daerah:</b> Mengacu pada laporan DLH, penurunan emisi rumah tangga difokuskan pada <b>Program Pelabelan (Labelling) Efisiensi Peralatan Rumah Tangga</b> (lampu, AC, dan lemari es) dengan target reduksi <b>{fmt_id(TARGET_LABELLING_2030)} Gg CO₂e</b> pada 2030 serta pemanfaatan PLTS atap menuju target <i>Net Zero Emission</i> (NZE) sebesar <b>5.604 Gg CO₂e</b> pada 2050.</li>"
        "</ul>",
    )

    st.markdown("### Struktur Dashboard")
    c_a, c_b = st.columns(2)
    with c_a:
        st.markdown(
            "**1. Data Historis (2010–2024)**  \n"
            "Menampilkan perkembangan tahunan emisi GRK, estimasi konsumsi energi dalam satuan Terajoule (TJ), "
            "serta tabel rekapitulasi lengkap yang dapat diunduh ke format Excel/CSV."
        )
    with c_b:
        st.markdown(
            "**2. Simulasi Mitigasi (2024–2030 & 2050)**  \n"
            "Menyediakan kalkulator skenario interaktif untuk melihat seberapa jauh program efisiensi peralatan listrik "
            "dan penurunan faktor emisi jaringan listrik mampu menekan laju emisi rumah tangga."
        )

    with st.expander("📖 Penjelasan Satuan dan Istilah di Laporan DLH"):
        st.markdown(
            """
| Istilah / Satuan | Penjelasan Singkat |
|---|---|
| **Gg CO₂e (Gigagram CO₂ ekuivalen)** | Satuan standar inventarisasi emisi GRK (1 Gg = 1.000 ton CO₂e). |
| **TJ (Terajoule)** | Satuan energi standar IPCC untuk menyatakan besaran konsumsi listrik, LPG, dan gas bumi. |
| **Emisi Langsung (Direct)** | Emisi dari pembakaran bahan bakar langsung di rumah tangga (LPG dan gas pipa). |
| **Emisi Tidak Langsung (Indirect)** | Emisi dari pembangkitan listrik PLN yang dikonsumsi oleh rumah tangga. |
| **Baseline (Tanpa Program / BaU)** | Proyeksi emisi jika tidak ada intervensi aksi mitigasi tambahan setelah tahun 2024. |
| **CPOS (Current Policy Scenario)** | Proyeksi emisi jangka panjang DLH berdasarkan kebijakan yang sudah berjalan. |
| **NZE (Net Zero Emission)** | Target emisi jangka panjang DLH menuju nol emisi bersih pada tahun 2050. |
"""
        )

# ==========================================================
# TAB 1: DATA HISTORIS
# ==========================================================
with tab1:
    st.subheader("Perkembangan Emisi GRK dan Konsumsi Energi Rumah Tangga (2010–2024)")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Emisi GRK per Sumber (Gg CO₂e)**")
        fig = go.Figure()
        for col, nama, w in [
            ("C_Listrik", "Listrik (tidak langsung)", WARNA["listrik"]),
            ("C_LPG", "LPG (langsung)", WARNA["lpg"]),
            ("C_Gas", "Gas bumi (langsung)", WARNA["gas"]),
        ]:
            fig.add_trace(go.Bar(x=df["Tahun"], y=df[col], name=nama, marker_color=w, hovertemplate="%{y:,.0f} Gg"))
        fig.update_layout(barmode="stack")
        tampil(tata_letak(fig))

    with col2:
        st.markdown("**Estimasi Konsumsi Energi Final (Terajoule / TJ)**")
        fig = go.Figure()
        for col, nama, w in [
            ("E_Listrik_TJ", "Listrik", WARNA["listrik"]),
            ("E_LPG_TJ", "LPG", WARNA["lpg"]),
            ("E_Gas_TJ", "Gas bumi", WARNA["gas"]),
        ]:
            fig.add_trace(
                go.Scatter(
                    x=df["Tahun"],
                    y=df[col],
                    name=nama,
                    mode="lines",
                    stackgroup="e",
                    line=dict(width=1.2, color=w),
                    hovertemplate="%{y:,.0f} TJ",
                )
            )
        tampil(tata_letak(fig))

    st.markdown("**Tabel Rekapitulasi Data Historis Sektor Rumah Tangga (2010–2024)**")
    tabel_raw = df[
        [
            "Tahun", "Penduduk_Juta", "PDRB_Konstan_T", "EF_Listrik_MWh",
            "C_Listrik", "C_LPG", "C_Gas", "C_Total_Gg", "E_Total_TJ", "Emisi_per_Kapita",
        ]
    ].rename(
        columns={
            "Penduduk_Juta": "Penduduk (juta)",
            "PDRB_Konstan_T": "PDRB konstan (T Rp)",
            "EF_Listrik_MWh": "EF listrik (tCO₂/MWh)",
            "C_Listrik": "Emisi listrik (Gg)",
            "C_LPG": "Emisi LPG (Gg)",
            "C_Gas": "Emisi gas (Gg)",
            "C_Total_Gg": "Total emisi (Gg)",
            "E_Total_TJ": "Total energi (TJ)",
            "Emisi_per_Kapita": "Emisi/penduduk (tCO₂e)",
        }
    )
    tabel_tampil = tabel_raw.copy()
    for kolom in tabel_tampil.columns[1:]:
        d_ = 3 if "EF listrik" in kolom else 2 if ("Penduduk" in kolom or "PDRB" in kolom or "Emisi/penduduk" in kolom) else 1
        tabel_tampil[kolom] = tabel_raw[kolom].map(lambda v, d_=d_: fmt_id(v, d_))
    tabel_tampil["Tahun"] = tabel_raw["Tahun"].astype(str)
    st.dataframe(tabel_tampil, hide_index=True, use_container_width=True)
    st.download_button(
        "📥 Unduh Tabel Historis (CSV)",
        tabel_raw.to_csv(index=False).encode("utf-8"),
        "profil_emisi_rumah_tangga_dki_2010_2024.csv",
        "text/csv",
    )

# ==========================================================
# TAB 2: SIMULASI MITIGASI (SESUAI TAMPILAN PROTOTIPE)
# ==========================================================
with tab2:
    st.subheader("Simulasi: seberapa jauh program mitigasi menurunkan emisi?")

    st.markdown("**1. Pilih skenario**")
    pilihan_skenario = st.radio(
        "Pilih skenario",
        ["Tanpa program", "Konservatif", "Sesuai target DLH", "Ambisius", "Atur sendiri"],
        index=2,
        horizontal=True,
        label_visibility="collapsed",
    )

    peta_preset = {
        "Tanpa program": (0, 0, 2.20, 0),
        "Konservatif": (60, 5, 2.20, 50),
        "Sesuai target DLH": (100, 10, 2.20, 100),
        "Ambisius": (130, 20, 2.20, 120),
    }
    def_lbl, def_grd, def_bau, def_nze = peta_preset.get(pilihan_skenario, (100, 10, 2.20, 100))
    kunci = pilihan_skenario != "Atur sendiri"

    s1, s2, s3, s4 = st.columns(4)
    with s1:
        capai_label = st.slider(
            "Labelling efisiensi (% target DLH)",
            0, 150, def_lbl, step=10, disabled=kunci,
            help="Program pelabelan efisiensi untuk AC, lampu, dan lemari es (Tabel 3 DLH: target 3.630 Gg pada 2030).",
        )
    with s2:
        cut_grid = st.slider(
            "Listrik lebih bersih pada 2030 (%)",
            0, 40, def_grd, step=5, disabled=kunci,
            help="Penurunan faktor emisi jaringan listrik Jawa-Madura-Bali secara bertahap hingga 2030.",
        )
    with s3:
        laju_bau = st.slider(
            "Pertumbuhan baseline (% per tahun)",
            0.50, 4.00, def_bau, step=0.10, disabled=kunci,
            help="Asumsi laju kenaikan emisi tahunan tanpa adanya program mitigasi tambahan.",
        )
    with s4:
        capai_nze = st.slider(
            "Realisasi target NZE (%)",
            0, 150, def_nze, step=10, disabled=kunci,
            help="0% mengikuti skenario CPOS DLH, 100% mencapai target NZE DLH pada 2050.",
        )

    cagr_1924 = ((c24 / c19) ** (1 / 5) - 1) * 100
    st.caption(
        f"Tiga pengaturan pertama memengaruhi hasil 2025–2030, yang keempat memengaruhi 2035–2050. "
        f"Sebagai pembanding, emisi aktual tumbuh {fmt_id(cagr_1924, 1)}% per tahun pada 2019–2024."
    )

    # ---- Perhitungan Jangka Pendek 2024–2030 (Bebas Hitung Ganda) ----
    tahun_pendek = [2024, 2025, 2026, 2027, 2028, 2029, 2030]
    target_label = [0, 2442, 2610, 2814, 3054, 3329, TARGET_LABELLING_2030]  # Tabel 3 DLH
    bau, skenario = [c24], [c24]
    red_label_2030, red_grid_2030 = 0.0, 0.0

    for idx in range(1, len(tahun_pendek)):
        bau_t = c24 * (1 + laju_bau / 100) ** idx
        red_l = target_label[idx] * capai_label / 100
        sisa_listrik = max(0.0, bau_t * porsi_listrik - red_l)
        red_g = sisa_listrik * (cut_grid / 100) * (idx / 6)
        bau.append(bau_t)
        skenario.append(max(0.0, bau_t - red_l - red_g))
        if idx == 6:
            red_label_2030 = red_l
            red_grid_2030 = red_g

    reduksi_2030 = bau[-1] - skenario[-1]
    persen_2030 = reduksi_2030 / bau[-1] * 100

    # ---- Perhitungan Jangka Panjang 2035–2050 (Tabel 4 & 5 DLH) ----
    tahun_dlh = [2019, 2035, 2040, 2045, 2050]
    cpos = [13953.0, 14356.0, 12760.0, 12023.0, 11237.0]
    nze = [13953.0, 14211.0, 11158.0, 9616.0, 5604.0]
    tahun_panjang = tahun_dlh[1:]
    sim_panjang = [max(0.0, cpos[i] - (cpos[i] - nze[i]) * capai_nze / 100) for i in range(1, len(tahun_dlh))]
    emisi_2050 = sim_panjang[-1]
    selisih_nze = emisi_2050 - nze[-1]

    st.markdown("**2. Lihat hasilnya**")
    status_2050 = "target NZE tercapai" if selisih_nze <= 0.5 else f"{fmt_id(selisih_nze)} Gg di atas target NZE"
    st.markdown(
        f"""
        <div class="res-grid">
            <div class="kpi-card c3">
                <div class="kpi-top">📉 Emisi 2030 dengan skenario ini</div>
                <div class="kpi-num">{fmt_id(skenario[-1])} Gg</div>
                <div class="kpi-sub green">{fmt_id(persen_2030, 1)}% lebih rendah dari baseline ({fmt_id(bau[-1])})</div>
            </div>
            <div class="kpi-card c4">
                <div class="kpi-top">🌱 Penurunan emisi 2030</div>
                <div class="kpi-num">{fmt_id(reduksi_2030)} Gg</div>
                <div class="kpi-sub gray">dibanding baseline tanpa program</div>
            </div>
            <div class="kpi-card c4">
                <div class="kpi-top">🏁 Emisi 2050 dengan skenario ini</div>
                <div class="kpi-num">{fmt_id(emisi_2050)} Gg</div>
                <div class="kpi-sub green">{status_2050}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    p_lbl = (red_label_2030 / reduksi_2030 * 100) if reduksi_2030 > 0 else 0.0
    p_grd = (red_grid_2030 / reduksi_2030 * 100) if reduksi_2030 > 0 else 0.0
    st.markdown("**Dari mana penurunan 2030 berasal?**")
    st.markdown(
        f"""
        <div class="bar-wrap">
            <div style="width:{p_lbl:.1f}%;background:#1D4E89;"></div>
            <div style="width:{p_grd:.1f}%;background:#2A9D8F;"></div>
        </div>
        <div style="font-size:0.84rem;color:#334155;margin-bottom:16px;">
            <span style="color:#1D4E89;font-weight:700;">●</span> Program labelling: <b>{fmt_id(red_label_2030)} Gg</b> &nbsp;&nbsp;
            <span style="color:#2A9D8F;font-weight:700;">●</span> Listrik lebih bersih: <b>{fmt_id(red_grid_2030)} Gg</b>
        </div>
        """,
        unsafe_allow_html=True,
    )

    g1, g2 = st.columns(2)
    hist = df[df["Tahun"] >= 2019]

    with g1:
        st.markdown("**Jangka pendek 2024–2030**")
        fig1 = go.Figure()
        fig1.add_trace(
            go.Scatter(
                x=tahun_pendek, y=bau, name="Tanpa program (baseline)",
                mode="lines", line=dict(color=WARNA["bau"], width=2, dash="dash"),
            )
        )
        fig1.add_trace(
            go.Scatter(
                x=tahun_pendek, y=skenario, name="Dengan skenario ini",
                mode="lines+markers", fill="tonexty", fillcolor="rgba(29, 78, 137, 0.13)",
                line=dict(color=WARNA["simulasi"], width=3),
            )
        )
        fig1.add_trace(
            go.Scatter(
                x=hist["Tahun"], y=hist["C_Total_Gg"], name="Aktual",
                mode="lines+markers", line=dict(color=WARNA["aktual"], width=2.5),
            )
        )
        if reduksi_2030 > 0:
            fig1.add_annotation(
                x=2030, y=(bau[-1] + skenario[-1]) / 2,
                text=f"−{fmt_id(reduksi_2030)}", showarrow=False, xshift=28,
                font=dict(size=11, color="#1D4E89"),
            )
        fig1 = tata_letak(fig1, "Gg CO₂e", 340)
        fig1.update_xaxes(dtick=1, range=[2018.8, 2031.2])
        tampil(fig1)
        st.caption("Area biru = emisi yang berhasil dihindari dibanding tanpa program.")

    with g2:
        st.markdown("**Jangka panjang 2035–2050**")
        fig2 = go.Figure()
        fig2.add_trace(
            go.Scatter(
                x=hist["Tahun"], y=hist["C_Total_Gg"], name="Aktual",
                mode="lines+markers", line=dict(color=WARNA["aktual"], width=2.5),
            )
        )
        fig2.add_trace(
            go.Scatter(
                x=tahun_dlh, y=cpos, name="Acuan CPOS (DLH)",
                mode="lines+markers", line=dict(color=WARNA["cpos"], width=2, dash="dot"),
            )
        )
        fig2.add_trace(
            go.Scatter(
                x=tahun_dlh, y=nze, name="Acuan NZE (DLH)",
                mode="lines+markers", line=dict(color=WARNA["nze"], width=2, dash="dot"),
            )
        )
        fig2.add_trace(
            go.Scatter(
                x=tahun_panjang, y=sim_panjang, name="Skenario ini",
                mode="lines+markers", line=dict(color=WARNA["simulasi"], width=3),
            )
        )
        fig2.add_annotation(x=2050, y=cpos[-1], text=fmt_id(cpos[-1]), showarrow=False, xshift=26, font=dict(size=11, color=WARNA["cpos"]))
        fig2.add_annotation(x=2050, y=emisi_2050, text=fmt_id(emisi_2050), showarrow=False, xshift=26, font=dict(size=11, color=WARNA["simulasi"]))
        fig2 = tata_letak(fig2, "Gg CO₂e", 340)
        fig2.update_xaxes(range=[2018, 2054])
        tampil(fig2)
        st.caption("Garis putus-putus adalah angka acuan DLH dengan basis inventarisnya sendiri, sehingga tidak menyambung langsung dengan garis aktual.")

    kotak(
        "Kesimpulan skenario ini",
        f"Pada tahun <b>2030</b>, dengan capaian program labelling <b>{capai_label}%</b> dari target DLH dan jaringan listrik <b>{cut_grid}%</b> lebih bersih, "
        f"emisi rumah tangga diperkirakan berada di <b>{fmt_id(skenario[-1])} Gg CO₂e</b> atau <b>{fmt_id(persen_2030, 1)}% lebih rendah dari baseline</b> "
        f"(menghindari emisi sebesar <b>{fmt_id(reduksi_2030)} Gg CO₂e</b>). Pada jangka panjang (<b>2050</b>), tingkat emisi mencapai <b>{fmt_id(emisi_2050)} Gg CO₂e</b> ({status_2050}).",
    )
