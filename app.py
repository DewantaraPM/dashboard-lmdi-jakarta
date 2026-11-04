import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# ==========================================================
# KONFIGURASI HALAMAN & DESAIN UI/UX EKSEKUTIF
# ==========================================================
st.set_page_config(
    page_title="LMDI & Simulasi Mitigasi Emisi Rumah Tangga DKI Jakarta",
    page_icon="🌿",
    layout="wide",
)

FONT = "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
WARNA = {
    "listrik": "#1E4E79",
    "lpg": "#D98A3C",
    "gas": "#4E9A84",
    "naik": "#C84B31",
    "turun": "#1F8A70",
    "total": "#1F2937",
    "aktual": "#334155",
    "bau": "#94A3B8",
    "simulasi": "#0F52BA",
}

st.markdown(
    """
    <style>
    .block-container { padding-top: 1.8rem; padding-bottom: 3rem; max-width: 1220px; }
    .stApp, .stApp p, .stApp li, .stApp label, .stApp td, .stApp th,
    .stApp h1, .stApp h2, .stApp h3, .stApp h4 {
        font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    .hero-box {
        background: linear-gradient(135deg, #0F3443 0%, #1E5F74 60%, #2A8C82 100%);
        color: white; padding: 26px 30px; border-radius: 16px;
        box-shadow: 0 10px 25px rgba(15, 52, 67, 0.14); margin-bottom: 1.3rem;
    }
    .hero-badge {
        display: inline-block; background: rgba(255,255,255,0.16); color: #E6FFFA;
        font-size: 0.78rem; font-weight: 600; padding: 4px 12px; border-radius: 999px;
        letter-spacing: 0.03em; text-transform: uppercase; margin-bottom: 10px;
    }
    .hero-title {
        font-size: 1.75rem; font-weight: 700; margin: 0 0 6px 0;
        letter-spacing: -0.02em; color: #FFFFFF; line-height: 1.25;
    }
    .hero-sub {
        font-size: 0.96rem; opacity: 0.9; margin: 0; line-height: 1.5; max-width: 920px; color: #F0FDF4;
    }
    .kpi-grid {
        display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 1.4rem;
    }
    .kpi-card {
        background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 14px;
        padding: 16px 18px; box-shadow: 0 2px 6px rgba(15, 23, 42, 0.04);
        border-top: 4px solid #1E4E79;
    }
    .kpi-card.warn { border-top-color: #C84B31; }
    .kpi-card.good { border-top-color: #1F8A70; }
    .kpi-card.gold { border-top-color: #D98A3C; }
    .kpi-label { font-size: 0.8rem; color: #64748B; font-weight: 500; margin-bottom: 4px; }
    .kpi-val { font-size: 1.55rem; font-weight: 700; color: #0F172A; margin-bottom: 4px; }
    .kpi-delta { font-size: 0.78rem; font-weight: 600; }
    .kpi-delta.up { color: #C84B31; }
    .kpi-delta.down { color: #1F8A70; }
    .kpi-delta.neutral { color: #475569; }
    .kotak {
        border-left: 4px solid #1E4E79; background: #F8FAFC;
        border-top: 1px solid #E2E8F0; border-right: 1px solid #E2E8F0; border-bottom: 1px solid #E2E8F0;
        padding: 14px 18px; border-radius: 0 12px 12px 0; margin: 8px 0 18px 0;
    }
    .kotak.hijau { border-left-color: #1F8A70; background: #F0FDF4; }
    .kotak-judul { font-weight: 600; color: #0F172A; margin-bottom: 4px; font-size: 0.95rem; }
    .bar-split {
        height: 14px; border-radius: 999px; overflow: hidden; display: flex;
        background: #E2E8F0; margin: 8px 0 6px 0;
    }
    button[data-baseweb="tab"] p { font-weight: 600; font-size: 0.94rem; }
    #MainMenu, footer { visibility: hidden; }
    @media (max-width: 900px) { .kpi-grid { grid-template-columns: repeat(2, 1fr); } }
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


def kotak(judul, isi_html, hijau=False):
    kelas = "kotak hijau" if hijau else "kotak"
    st.markdown(
        f'<div class="{kelas}"><div class="kotak-judul">{judul}</div><div style="font-size:0.9rem;color:#334155;">{isi_html}</div></div>',
        unsafe_allow_html=True,
    )


def tata_letak(fig, y_title=None, tinggi=370):
    fig.update_layout(
        template="plotly_white",
        font=dict(family=FONT, size=12, color="#1E293B"),
        paper_bgcolor="white",
        plot_bgcolor="white",
        margin=dict(l=10, r=10, t=36, b=10),
        height=tinggi,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, title_text=""),
        hovermode="x unified",
        yaxis=dict(title=y_title, gridcolor="#F1F5F9", zerolinecolor="#CBD5E1"),
        xaxis=dict(showgrid=False),
    )
    return fig


def tampil(fig):
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# ==========================================================
# 1. DATA HISTORIS (LAPORAN AKHIR DLH DKI JAKARTA 2026)
# ==========================================================
data_historis = {
    "Tahun": list(range(2010, 2025)),
    "Penduduk_Juta": [9.64, 9.89, 9.86, 9.97, 10.08, 10.18, 10.28, 10.37, 10.47, 10.56, 10.56, 10.61, 10.68, 10.67, 10.68],
    "PDRB_Konstan_T": [1080.00, 1260.00, 1222.53, 1296.69, 1373.39, 1454.56, 1539.92, 1635.36, 1735.21, 1836.24, 1792.29, 1856.00, 1953.49, 2050.47, 2151.04],
    "PDRB_Berlaku_T": [1075.0, 1224.0, 1369.0, 1547.0, 1762.0, 1989.0, 2159.0, 2365.0, 2593.0, 2816.0, 2767.0, 2913.0, 3189.0, 3443.0, 3679.0],
    "EF_Listrik_MWh": [0.830, 0.880, 0.927, 0.967, 0.949, 1.023, 0.990, 0.897, 0.894, 0.906, 0.902, 0.896, 0.901, 0.903, 0.903],
    "C_Listrik": [7560.0, 8400.0, 9590.0, 11100.0, 10500.0, 11700.0, 12500.0, 11300.0, 11800.0, 12600.0, 13100.0, 13100.0, 13300.0, 14100.0, 14828.0],
    "C_LPG": [982.0, 1044.0, 1082.0, 1076.0, 1076.0, 1393.0, 1366.0, 1444.0, 1447.0, 1266.0, 1289.0, 1300.0, 1318.0, 1338.0, 1348.0],
    "C_Gas": [0.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 7.0, 7.0, 7.0, 4.0],
}
DELTA = 1e-20  # Konstanta nilai nol sesuai panduan Ang (2005, 2015)


def bangun_df(gas_2010=DELTA):
    d = pd.DataFrame(data_historis)
    d.loc[d["Tahun"] == 2010, "C_Gas"] = gas_2010
    d["EF_Listrik_TJ"] = d["EF_Listrik_MWh"] / 3.6  # 1 GWh = 3,6 TJ
    d["EF_LPG_TJ"] = 0.06537                        # Tier 2 ESDM: 65.370 kg CO2/TJ
    d["EF_Gas_TJ"] = 0.05764                        # Tier 2 ESDM: 57.640 kg CO2/TJ
    d["E_Listrik_TJ"] = d["C_Listrik"] / d["EF_Listrik_TJ"]
    d["E_LPG_TJ"] = d["C_LPG"] / d["EF_LPG_TJ"]
    d["E_Gas_TJ"] = d["C_Gas"] / d["EF_Gas_TJ"]
    d["E_Total_TJ"] = d["E_Listrik_TJ"] + d["E_LPG_TJ"] + d["E_Gas_TJ"]
    d["C_Total_Gg"] = d["C_Listrik"] + d["C_LPG"] + d["C_Gas"]
    return d


df = bangun_df(DELTA)

# ==========================================================
# 2. SIDEBAR RINGKAS & TERSTRUKTUR
# ==========================================================
with st.sidebar:
    st.markdown("### 🎓 Identitas Penelitian")
    st.caption(
        "**Dekomposisi Pendorong Perubahan Emisi GRK Sektor Rumah Tangga DKI Jakarta (2010–2024) "
        "dan Simulasi Mitigasi Berbasis LMDI (2024–2030)**"
    )
    st.caption(
        "**Peneliti:** Dewantara Putra Makmur  \n"
        "**NIM:** G2401231071  \n"
        "**Pembimbing 1:** Perdinan, S.Si., M.Nat.Res.Econ., Ph.D.  \n"
        "**Program Studi:** Meteorologi Terapan, GFM FMIPA IPB"
    )
    st.divider()
    st.markdown("### 🔗 Satu Kerangka Metode Utuh")
    st.latex(r"C = \sum_i P \cdot \frac{Y}{P} \cdot \frac{E}{Y} \cdot \frac{E_i}{E} \cdot \frac{C_i}{E_i}")
    st.caption(
        "Persamaan Identitas Kaya & LMDI-I Aditif (Ang 2005, 2015; Kurniawan et al. 2018) digunakan secara konsisten untuk:\n"
        "1. **Mendiagnosis** pendorong emisi historis (2010–2024).\n"
        "2. **Menyimulasikan** intervensi efisiensi ($E/Y$) dan faktor emisi listrik ($C_i/E_i$) pada 2024–2030."
    )
    st.divider()
    st.caption("Sumber Data Resmi: Laporan Akhir Inventarisasi & Penurunan Emisi GRK Provinsi DKI Jakarta (DLH 2026).")

# ==========================================================
# 3. MESIN PERHITUNGAN LMDI-I ADITIF
# ==========================================================
EFEK_KEYS = [
    "Efek Penduduk (ΔC_pop)",
    "Efek Kemakmuran (ΔC_aff)",
    "Efek Intensitas Energi (ΔC_int)",
    "Efek Bauran Energi (ΔC_mix)",
    "Efek Faktor Emisi (ΔC_ef)",
]
NAMA = {
    "Efek Penduduk (ΔC_pop)": "Pertumbuhan penduduk",
    "Efek Kemakmuran (ΔC_aff)": "Kemakmuran (PDRB/kapita)",
    "Efek Intensitas Energi (ΔC_int)": "Intensitas energi (efisiensi)",
    "Efek Bauran Energi (ΔC_mix)": "Bauran bahan bakar",
    "Efek Faktor Emisi (ΔC_ef)": "Faktor emisi listrik",
}
KEY_TOTAL = "Perubahan Total (ΔC)"


def log_mean(c_t, c_0):
    if np.isclose(c_t, c_0):
        return c_0
    return (c_t - c_0) / (np.log(c_t) - np.log(c_0))


def hitung_lmdi_baris(r0, rt, kolom_pdrb="PDRB_Konstan_T", label_periode=""):
    P0, Pt = r0["Penduduk_Juta"], rt["Penduduk_Juta"]
    Y0, Yt = r0[kolom_pdrb], rt[kolom_pdrb]
    E0, Et = r0["E_Total_TJ"], rt["E_Total_TJ"]
    g0, gt = Y0 / P0, Yt / Pt
    I0, It = E0 / Y0, Et / Yt

    fuels = [
        ("C_Listrik", "E_Listrik_TJ", "EF_Listrik_TJ"),
        ("C_LPG", "E_LPG_TJ", "EF_LPG_TJ"),
        ("C_Gas", "E_Gas_TJ", "EF_Gas_TJ"),
    ]

    dC_pop = dC_aff = dC_int = dC_mix = dC_ef = 0.0
    for col_c, col_e, col_ef in fuels:
        c0, ct = r0[col_c], rt[col_c]
        e0, et = r0[col_e], rt[col_e]
        ef0, eft = r0[col_ef], rt[col_ef]
        s0, st_ = e0 / E0, et / Et
        L = log_mean(ct, c0)
        dC_pop += L * np.log(Pt / P0)
        dC_aff += L * np.log(gt / g0)
        dC_int += L * np.log(It / I0)
        dC_mix += L * np.log(st_ / s0)
        dC_ef += L * np.log(eft / ef0)

    dC_total = rt["C_Total_Gg"] - r0["C_Total_Gg"]
    return {
        "Periode": label_periode,
        KEY_TOTAL: round(dC_total, 2),
        "Efek Penduduk (ΔC_pop)": round(dC_pop, 2),
        "Efek Kemakmuran (ΔC_aff)": round(dC_aff, 2),
        "Efek Intensitas Energi (ΔC_int)": round(dC_int, 2),
        "Efek Bauran Energi (ΔC_mix)": round(dC_mix, 2),
        "Efek Faktor Emisi (ΔC_ef)": round(dC_ef, 2),
        "Residual": round(dC_total - (dC_pop + dC_aff + dC_int + dC_mix + dC_ef), 4),
    }


def hitung_lmdi(df_data, thn_awal, thn_akhir, kolom_pdrb="PDRB_Konstan_T"):
    r0 = df_data[df_data["Tahun"] == thn_awal].iloc[0]
    rt = df_data[df_data["Tahun"] == thn_akhir].iloc[0]
    return hitung_lmdi_baris(r0, rt, kolom_pdrb, f"{thn_awal}–{thn_akhir}")


def tabel_efek(baris, nama_kolom_awal="Periode"):
    d = pd.DataFrame(baris)
    out = pd.DataFrame({nama_kolom_awal: d["Periode"]})
    out["Total perubahan"] = d[KEY_TOTAL].map(lambda v: fmt_tanda(v, 1))
    for k in EFEK_KEYS:
        out[NAMA[k]] = d[k].map(lambda v: fmt_tanda(v, 1))
    return out


def buat_waterfall(hasil_dict, tinggi=390):
    nilai = [hasil_dict[k] for k in EFEK_KEYS] + [hasil_dict[KEY_TOTAL]]
    label = [NAMA[k].replace(" (", "<br>(") for k in EFEK_KEYS] + ["Total<br>perubahan"]
    fig = go.Figure(
        go.Waterfall(
            orientation="v",
            measure=["relative"] * 5 + ["total"],
            x=label,
            y=nilai,
            text=[fmt_tanda(v) for v in nilai],
            textposition="outside",
            cliponaxis=False,
            connector={"line": {"color": "#CBD5E1", "width": 1}},
            increasing={"marker": {"color": WARNA["naik"]}},
            decreasing={"marker": {"color": WARNA["turun"]}},
            totals={"marker": {"color": WARNA["total"]}},
            hovertemplate="%{y:,.1f} Gg CO₂e<extra></extra>",
        )
    )
    fig = tata_letak(fig, "Gg CO₂e", tinggi=tinggi)
    fig.update_layout(hovermode="closest", margin=dict(l=10, r=10, t=35, b=10))
    return fig


# ==========================================================
# 4. HERO BANNER & 4 KARTU METRIK UTAMA
# ==========================================================
r10 = df[df["Tahun"] == 2010].iloc[0]
r20 = df[df["Tahun"] == 2020].iloc[0]
r24 = df[df["Tahun"] == 2024].iloc[0]
c10, c24 = r10["C_Total_Gg"], r24["C_Total_Gg"]
porsi_listrik = r24["C_Listrik"] / c24
tumbuh_total = (c24 / c10 - 1) * 100
kapita10 = c10 / r10["Penduduk_Juta"] / 1000
kapita24 = c24 / r24["Penduduk_Juta"] / 1000
TARGET_LABELLING_2030 = 3630.0

st.markdown(
    """
    <div class="hero-box">
        <div class="hero-badge">Sistem Analisis Dekomposisi & Simulasi Kebijakan Iklim</div>
        <div class="hero-title">Emisi Gas Rumah Kaca Sektor Rumah Tangga DKI Jakarta</div>
        <div class="hero-sub">
            Menguraikan faktor pendorong kenaikan emisi historis (2010–2024) dengan metode <b>LMDI-I Aditif</b>,
            dan menggunakannya secara langsung untuk menyimulasikan target penurunan emisi (2024–2030).
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="kpi-grid">
        <div class="kpi-card warn">
            <div class="kpi-label">Total Emisi Rumah Tangga (2024)</div>
            <div class="kpi-val">{fmt_id(c24)} Gg CO₂e</div>
            <div class="kpi-delta up">{fmt_tanda(tumbuh_total, 1)}% dibanding 2010 ({fmt_id(c10)} Gg)</div>
        </div>
        <div class="kpi-card gold">
            <div class="kpi-label">Emisi per Penduduk (2024)</div>
            <div class="kpi-val">{fmt_id(kapita24, 2)} tCO₂e/jiwa</div>
            <div class="kpi-delta up">{fmt_tanda((kapita24 / kapita10 - 1) * 100, 1)}% dibanding 2010</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Dominasi Emisi Listrik (2024)</div>
            <div class="kpi-val">{fmt_id(porsi_listrik * 100, 1)}%</div>
            <div class="kpi-delta neutral">{fmt_id(r24['C_Listrik'])} Gg CO₂e (Emisi Tidak Langsung)</div>
        </div>
        <div class="kpi-card good">
            <div class="kpi-label">Target Reduksi Labelling 2030 (DLH)</div>
            <div class="kpi-val">{fmt_id(TARGET_LABELLING_2030)} Gg CO₂e</div>
            <div class="kpi-delta down">Setara {fmt_id(TARGET_LABELLING_2030 / c24 * 100, 1)}% emisi tahun 2024</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ==========================================================
# 5. NAVIGASI TAB (SELARAS BAB 4 SKRIPSI)
# ==========================================================
tab0, tab1, tab2, tab3, tab4 = st.tabs(
    [
        "🏠 Ringkasan Alur",
        "📊 4.1 Data Historis",
        "🔍 4.2 Faktor Pendorong (LMDI)",
        "⚖️ 4.3 Uji Kepekaan",
        "🎛️ 4.4 Simulasi Mitigasi (LMDI)",
    ]
)

# ==========================================================
# TAB 0: RINGKASAN ALUR
# ==========================================================
with tab0:
    h_all = hitung_lmdi(df, 2010, 2024, "PDRB_Konstan_T")
    kotak(
        "Benang Merah Penelitian (Mengapa Semuanya Saling Terkait)",
        "<ul>"
        f"<li><b>1. Fakta Historis (Tab 4.1):</b> Emisi rumah tangga DKI Jakarta naik <b>{fmt_tanda(tumbuh_total, 1)}%</b> (menjadi {fmt_id(c24)} Gg CO₂e pada 2024), dan <b>{fmt_id(porsi_listrik * 100, 1)}%</b> berasal dari konsumsi listrik PLN.</li>"
        f"<li><b>2. Diagnosis Penyebab dengan LMDI (Tab 4.2):</b> Metode LMDI membuktikan kenaikan emisi didorong oleh <b>kemakmuran/PDRB per kapita ({fmt_tanda(h_all['Efek Kemakmuran (ΔC_aff)'])} Gg)</b> dan <b>penduduk ({fmt_tanda(h_all['Efek Penduduk (ΔC_pop)'])} Gg)</b>, sedangkan perbaikan <b>intensitas energi ({fmt_tanda(h_all['Efek Intensitas Energi (ΔC_int)'])} Gg)</b> menahan laju emisi.</li>"
        "<li><b>3. Validasi Ketahanan Metode (Tab 4.3):</b> Urutan faktor pendorong utama terbukti konsisten dan valid baik ketika diuji terhadap basis PDRB maupun ketika guncangan pandemi 2020 dikeluarkan.</li>"
        "<li><b>4. Simulasi Mitigasi Berbasis LMDI (Tab 4.4):</b> Karena penduduk dan ekonomi tidak mungkin direm, maka penurunan emisi 2024–2030 disimulasikan langsung dengan menekan <b>Faktor Intensitas Energi (lewat Program Labelling AC/Lampu DLH)</b> dan <b>Faktor Emisi Listrik (lewat Dekarbonisasi Grid Jamali)</b> di dalam persamaan LMDI yang sama.</li>"
        "</ul>",
        hijau=True,
    )

    with st.expander("📖 Kamus Ringkas 5 Faktor LMDI yang Dipakai di Seluruh Tab"):
        st.markdown(
            """
| Variabel dalam Rumus LMDI | Nama Faktor | Perannya pada Masa Lalu (2010–2024) | Perannya pada Simulasi (2024–2030) |
|---|---|---|---|
| **$P$** | **Pertumbuhan penduduk** | Mendorong kenaikan emisi seiring bertambahnya warga | Diproyeksikan terus tumbuh mengikuti tren historis |
| **$Y/P$** | **Kemakmuran (PDRB/kapita)** | **Pendorong terbesar** kenaikan emisi rumah tangga | Diproyeksikan terus tumbuh mengikuti tren ekonomi |
| **$E/Y$** | **Intensitas energi (efisiensi)** | **Penahan utama** kenaikan emisi (makin efisien) | **Tuas Kebijakan 1:** Ditekan lebih kuat lewat *Program Labelling* peralatan rumah tangga (Tabel 3 DLH) |
| **$E_i/E$** | **Bauran bahan bakar** | Pergeseran porsi energi antara listrik, LPG, dan gas | Berubah otomatis saat konsumsi listrik dihemat oleh *Program Labelling* |
| **$C_i/E_i$** | **Faktor emisi listrik** | Naik pada 2010–2015, lalu diasumsikan konstan pasca-2019 | **Tuas Kebijakan 2:** Ditekan lewat skenario penurunan faktor emisi pembangkit listrik Jamali |
"""
        )

# ==========================================================
# TAB 1: DATA HISTORIS (SUBBAB 4.1)
# ==========================================================
with tab1:
    st.subheader("4.1 Profil Emisi GRK dan Konsumsi Energi Rumah Tangga (2010–2024)")
    kotak(
        "Inti Pembahasan Subbab 4.1",
        f"Selama 2010–2024, emisi GRK sektor rumah tangga meningkat dari <b>{fmt_id(c10)} Gg</b> menjadi <b>{fmt_id(c24)} Gg CO₂e</b>. "
        f"Konsumsi energi diturunkan dari rasio emisi terhadap faktor emisi Tier 2 ESDM dan jaringan Jamali ($E_i = C_i / EF_i$). "
        f"Listrik menyumbang <b>{fmt_id(porsi_listrik * 100, 1)}%</b> dari total emisi rumah tangga.",
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Emisi GRK Rumah Tangga per Sumber Energi (Gg CO₂e)**")
        fig = go.Figure()
        for col, nama, w in [
            ("C_Listrik", "Listrik (tidak langsung)", WARNA["listrik"]),
            ("C_LPG", "LPG (langsung)", WARNA["lpg"]),
            ("C_Gas", "Gas bumi (langsung)", WARNA["gas"]),
        ]:
            fig.add_trace(go.Bar(x=df["Tahun"], y=df[col], name=nama, marker_color=w, hovertemplate="%{y:,.0f} Gg"))
        fig.update_layout(barmode="stack")
        tampil(tata_letak(fig, "Gg CO₂e"))

    with col2:
        st.markdown("**Estimasi Konsumsi Energi Final Rumah Tangga (Terajoule / TJ)**")
        fig = go.Figure()
        for col, nama, w in [
            ("E_Listrik_TJ", "Listrik PLN", WARNA["listrik"]),
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
        tampil(tata_letak(fig, "Terajoule (TJ)"))

    with st.expander("📋 Lihat & Unduh Tabel Deret Data Lengkap (2010–2024)"):
        tabel_raw = df[
            [
                "Tahun", "Penduduk_Juta", "PDRB_Konstan_T", "PDRB_Berlaku_T",
                "EF_Listrik_MWh", "C_Listrik", "C_LPG", "C_Gas", "C_Total_Gg", "E_Total_TJ",
            ]
        ].rename(
            columns={
                "Penduduk_Juta": "Penduduk (juta)",
                "PDRB_Konstan_T": "PDRB konstan (T Rp)",
                "PDRB_Berlaku_T": "PDRB berlaku (T Rp)",
                "EF_Listrik_MWh": "EF listrik (tCO₂/MWh)",
                "C_Listrik": "Emisi listrik (Gg)",
                "C_LPG": "Emisi LPG (Gg)",
                "C_Gas": "Emisi gas (Gg)",
                "C_Total_Gg": "Total emisi (Gg)",
                "E_Total_TJ": "Total energi (TJ)",
            }
        )
        st.dataframe(tabel_raw.style.format(precision=2), hide_index=True, use_container_width=True)
        st.download_button(
            "📥 Unduh Tabel Historis (CSV)",
            tabel_raw.to_csv(index=False).encode("utf-8"),
            "tabel_4_1_data_historis_rt_dki.csv",
            "text/csv",
        )

# ==========================================================
# TAB 2: FAKTOR PENDORONG LMDI (SUBBAB 4.2)
# ==========================================================
with tab2:
    st.subheader("4.2 Dekomposisi Faktor Pendorong Emisi Rumah Tangga (2010–2024)")
    kotak(
        "Cara Membaca Grafik Dekomposisi LMDI",
        "Batang <b style='color:#C84B31'>merah</b> menunjukkan faktor yang <b>mendorong kenaikan</b> emisi, sedangkan batang "
        "<b style='color:#1F8A70'>hijau</b> adalah faktor yang <b>menahan/menurunkan</b> emisi. "
        "Jumlah kelima faktor sama persis dengan <b>Total Perubahan</b> tanpa sisa (<i>residual</i> = 0).",
    )

    o1, o2 = st.columns(2)
    with o1:
        t_awal = st.selectbox("Pilih Tahun Awal", list(range(2010, 2024)), index=0)
    with o2:
        opsi_akhir = list(range(t_awal + 1, 2025))
        t_akhir = st.selectbox("Pilih Tahun Akhir", opsi_akhir, index=len(opsi_akhir) - 1)

    hasil_periode = hitung_lmdi(df, t_awal, t_akhir, "PDRB_Konstan_T")
    st.markdown(f"**Grafik Waterfall Dekomposisi LMDI Periode {t_awal}–{t_akhir} (Gg CO₂e)**")
    tampil(buat_waterfall(hasil_periode, tinggi=390))

    st.markdown("**Perbandingan Kontribusi Faktor pada Tiga Fase: Pra-Pandemi, Saat Pandemi (2020), dan Pasca-Pandemi**")
    ringkasan_fase = [
        hitung_lmdi(df, 2010, 2019, "PDRB_Konstan_T"),
        hitung_lmdi(df, 2019, 2020, "PDRB_Konstan_T"),
        hitung_lmdi(df, 2020, 2024, "PDRB_Konstan_T"),
        hitung_lmdi(df, 2010, 2024, "PDRB_Konstan_T"),
    ]
    ringkasan_fase[0]["Periode"] = "Pra-Pandemi (2010–2019)"
    ringkasan_fase[1]["Periode"] = "Guncangan Pandemi (2019–2020)"
    ringkasan_fase[2]["Periode"] = "Pasca-Pandemi (2020–2024)"
    ringkasan_fase[3]["Periode"] = "Total Keseluruhan (2010–2024)"

    st.dataframe(tabel_efek(ringkasan_fase, "Fase Analisis"), hide_index=True, use_container_width=True)

    with st.expander("📈 Lihat Dinamika Dekomposisi Tahunan Berantai (Year-over-Year 2010–2024)"):
        rantai = pd.DataFrame([hitung_lmdi(df, y, y + 1, "PDRB_Konstan_T") for y in range(2010, 2024)])
        fig_c = go.Figure()
        warna_efek = {
            "Efek Penduduk (ΔC_pop)": "#E9B872",
            "Efek Kemakmuran (ΔC_aff)": WARNA["naik"],
            "Efek Intensitas Energi (ΔC_int)": WARNA["turun"],
            "Efek Bauran Energi (ΔC_mix)": "#8E7CC3",
            "Efek Faktor Emisi (ΔC_ef)": "#4FB3D9",
        }
        for k in EFEK_KEYS:
            fig_c.add_trace(go.Bar(name=NAMA[k], x=rantai["Periode"], y=rantai[k], marker_color=warna_efek[k]))
        fig_c.add_trace(
            go.Scatter(
                name="Total perubahan",
                x=rantai["Periode"],
                y=rantai[KEY_TOTAL],
                mode="lines+markers",
                line=dict(color="#0F172A", width=2.5),
            )
        )
        fig_c.update_layout(barmode="relative")
        tampil(tata_letak(fig_c, "Gg CO₂e", 360))
        st.download_button(
            "📥 Unduh Tabel Dekomposisi Multi-Fase (CSV)",
            pd.DataFrame(ringkasan_fase).to_csv(index=False).encode("utf-8"),
            "tabel_4_2_dekomposisi_lmdi.csv",
            "text/csv",
        )

# ==========================================================
# TAB 3: UJI KEPEKAAN (SUBBAB 4.3)
# ==========================================================
with tab3:
    st.subheader("4.3 Uji Kepekaan Metode: Basis PDRB & Anomali Pandemi 2020")
    kotak(
        "Tujuan Uji Kepekaan (Mengacu Tanoto & Praptiningsih 2013)",
        "Menguji apakah kesimpulan faktor pendorong berubah apabila: <b>(1)</b> PDRB Harga Konstan diganti menjadi PDRB Harga Berlaku, "
        "dan <b>(2)</b> tahun anomali pandemi COVID-19 (2019–2020) dikeluarkan dari perhitungan rantai tahunan.",
    )

    h_konstan = hitung_lmdi(df, 2010, 2024, "PDRB_Konstan_T")
    h_berlaku = hitung_lmdi(df, 2010, 2024, "PDRB_Berlaku_T")

    rantai_penuh = pd.DataFrame([hitung_lmdi(df, y, y + 1, "PDRB_Konstan_T") for y in range(2010, 2024)])
    rantai_tanpa2020 = pd.DataFrame([hitung_lmdi(df, y, y + 1, "PDRB_Konstan_T") for y in range(2010, 2024) if y != 2019])

    col_u1, col_u2 = st.columns(2)
    with col_u1:
        st.markdown("**Uji 1: PDRB Harga Konstan vs. Harga Berlaku (2010–2024)**")
        fig_u1 = go.Figure()
        fig_u1.add_trace(
            go.Bar(
                name="PDRB Harga Konstan (Riil - Acuan Utama)",
                x=[NAMA[k] for k in EFEK_KEYS],
                y=[h_konstan[k] for k in EFEK_KEYS],
                marker_color="#1E4E79",
            )
        )
        fig_u1.add_trace(
            go.Bar(
                name="PDRB Harga Berlaku (Nominal - Mengandung Inflasi)",
                x=[NAMA[k] for k in EFEK_KEYS],
                y=[h_berlaku[k] for k in EFEK_KEYS],
                marker_color="#D98A3C",
            )
        )
        fig_u1.update_layout(barmode="group")
        tampil(tata_letak(fig_u1, "Gg CO₂e", 350))

    with col_u2:
        st.markdown("**Uji 2: Dampak Pengeluaran Tahun Pandemi (2019–2020)**")
        fig_u2 = go.Figure()
        fig_u2.add_trace(
            go.Bar(
                name="Deret Penuh (Dengan 2019–2020)",
                x=[NAMA[k] for k in EFEK_KEYS],
                y=[rantai_penuh[k].sum() for k in EFEK_KEYS],
                marker_color="#1E4E79",
            )
        )
        fig_u2.add_trace(
            go.Bar(
                name="Tanpa Tahun Pandemi (Excl. 2019–2020)",
                x=[NAMA[k] for k in EFEK_KEYS],
                y=[rantai_tanpa2020[k].sum() for k in EFEK_KEYS],
                marker_color="#1F8A70",
            )
        )
        fig_u2.update_layout(barmode="group")
        tampil(tata_letak(fig_u2, "Gg CO₂e", 350))

    baris_sens = [
        {"Periode": "1A. PDRB Harga Konstan (2010–2024)", **{k: h_konstan[k] for k in [KEY_TOTAL] + EFEK_KEYS}},
        {"Periode": "1B. PDRB Harga Berlaku (2010–2024)", **{k: h_berlaku[k] for k in [KEY_TOTAL] + EFEK_KEYS}},
        {"Periode": "2A. Rantai Tahunan Penuh (Dengan 2020)", **{k: round(rantai_penuh[k].sum(), 2) for k in [KEY_TOTAL] + EFEK_KEYS}},
        {"Periode": "2B. Rantai Tahunan Tanpa Pandemi 2019–2020", **{k: round(rantai_tanpa2020[k].sum(), 2) for k in [KEY_TOTAL] + EFEK_KEYS}},
    ]
    st.markdown("**Tabel Ringkasan Uji Kepekaan (Gg CO₂e)**")
    st.dataframe(tabel_efek(baris_sens, "Skenario Pengujian"), hide_index=True, use_container_width=True)

    kotak(
        "Kesimpulan Uji Kepekaan untuk Bab 4.3",
        "<ul>"
        f"<li><b>Pengaruh Inflasi pada PDRB Berlaku (1A vs 1B):</b> Pemakaian PDRB harga berlaku menggelembungkan efek kemakmuran dari <b>{fmt_tanda(h_konstan['Efek Kemakmuran (ΔC_aff)'])} Gg</b> menjadi <b>{fmt_tanda(h_berlaku['Efek Kemakmuran (ΔC_aff)'])} Gg</b> dan efek intensitas energi dari <b>{fmt_tanda(h_konstan['Efek Intensitas Energi (ΔC_int)'])} Gg</b> menjadi <b>{fmt_tanda(h_berlaku['Efek Intensitas Energi (ΔC_int)'])} Gg</b> akibat terikutnya inflasi harga. Karena itu, PDRB harga konstan wajib digunakan.</li>"
        f"<li><b>Efek WFH saat Pandemi 2020 (2A vs 2B):</b> Saat transisi pandemi 2019–2020 dikeluarkan, efek penghematan intensitas energi menjadi jauh lebih kuat (<b>{fmt_tanda(rantai_tanpa2020['Efek Intensitas Energi (ΔC_int)'].sum())} Gg</b> dibanding <b>{fmt_tanda(rantai_penuh['Efek Intensitas Energi (ΔC_int)'].sum())} Gg</b>), membuktikan bahwa pada tahun 2020 terjadi lonjakan konsumsi listrik di dalam hunian saat ekonomi turun.</li>"
        "</ul>",
        hijau=True,
    )

# ==========================================================
# TAB 4: SIMULASI MITIGASI BERBASIS LMDI (SUBBAB 4.4)
# ==========================================================
with tab4:
    st.subheader("4.4 Simulasi Mitigasi 2024–2030 Berbasis Persamaan LMDI")
    kotak(
        "Bagaimana Simulasi Ini Terhubung Langsung dengan Rumus LMDI?",
        "Proyeksi 2024–2030 dihitung langsung menggunakan kelima komponen identitas LMDI: "
        "<b>Penduduk ($P$)</b> dan <b>Kemakmuran ($Y/P$)</b> tumbuh mengikuti tren pemulihan pasca-pandemi, "
        "sedangkan intervensi kebijakan bekerja langsung menekan <b>Intensitas Energi ($E/Y$) melalui Program Labelling DLH</b> "
        "dan menurunkan <b>Faktor Emisi Listrik ($C_i/E_i$) melalui Dekarbonisasi Grid Jamali</b> tanpa hitung ganda (<i>no double counting</i>).",
    )

    st.markdown("**1. Pilih Skenario Kebijakan (2024–2030)**")
    pilihan_preset = st.radio(
        "Preset Skenario:",
        ["Tanpa program (BaU)", "Konservatif", "Sesuai target DLH", "Dekarbonisasi ambisius", "Atur sendiri"],
        index=2,
        horizontal=True,
        label_visibility="collapsed",
    )

    preset_map = {
        "Tanpa program (BaU)": (0, 0, 2.2),
        "Konservatif": (60, 5, 2.2),
        "Sesuai target DLH": (100, 10, 2.2),
        "Dekarbonisasi ambisius": (130, 20, 2.2),
    }
    def_label, def_grid, def_bau = preset_map.get(pilihan_preset, (100, 10, 2.2))
    kunci_slider = pilihan_preset != "Atur sendiri"

    s1, s2, s3 = st.columns(3)
    with s1:
        capai_label = st.slider(
            "Intervensi Intensitas Energi (E/Y): Pencapaian Labelling DLH (%)",
            0, 150, def_label, step=10, disabled=kunci_slider,
            help="Program pelabelan efisiensi AC, lampu, dan kulkas (Tabel 3 DLH: target 3.630 Gg pada 2030). Menurunkan konsumsi energi listrik (TJ) dan intensitas energi rumah tangga.",
        )
    with s2:
        cut_grid = st.slider(
            "Intervensi Faktor Emisi (Ci/Ei): Penurunan EF Listrik 2030 (%)",
            0, 40, def_grid, step=5, disabled=kunci_slider,
            help="Penurunan faktor emisi jaringan listrik Jawa-Madura-Bali secara bertahap hingga 2030, dihitung hanya pada sisa listrik setelah penghematan labelling.",
        )
    with s3:
        laju_bau = st.slider(
            "Dorongan Aktivitas Baseline (Penduduk + Kemakmuran Bersih, %/thn)",
            0.5, 4.0, def_bau, step=0.1, disabled=kunci_slider,
            help="Laju pertumbuhan tahunan baseline dari interaksi pertumbuhan penduduk, PDRB per kapita, dan efisiensi alami tanpa program baru.",
        )

    # ---- Perhitungan Proyeksi Berbasis Komponen LMDI (2024–2030) ----
    # Laju historis pasca-pandemi (2020–2024) untuk memisahkan P dan Y/P secara realistis:
    r_pop_hist = (r24["Penduduk_Juta"] / r20["Penduduk_Juta"]) ** (1 / 4) - 1      # ~0,28% per tahun
    r_aff_hist = ((r24["PDRB_Konstan_T"] / r24["Penduduk_Juta"]) / (r20["PDRB_Konstan_T"] / r20["Penduduk_Juta"])) ** (1 / 4) - 1  # ~4,37% per tahun
    # Laju intensitas energi baseline disesuaikan agar kombinasi (1+r_P)(1+r_aff)(1+r_int_bau) = (1 + laju_bau/100)
    r_int_bau = (1 + laju_bau / 100.0) / ((1 + r_pop_hist) * (1 + r_aff_hist)) - 1

    tahun_proj = [2024, 2025, 2026, 2027, 2028, 2029, 2030]
    target_label_dlh = [0.0, 2442.0, 2610.0, 2814.0, 3054.0, 3329.0, TARGET_LABELLING_2030]

    bau_list, sim_list = [], []
    baris_2030_sim = None

    for idx, thn in enumerate(tahun_proj):
        if idx == 0:
            bau_list.append(c24)
            sim_list.append(c24)
        else:
            P_t = r24["Penduduk_Juta"] * ((1 + r_pop_hist) ** idx)
            g_t = (r24["PDRB_Konstan_T"] / r24["Penduduk_Juta"]) * ((1 + r_aff_hist) ** idx)
            Y_t = P_t * g_t

            faktor_bau = (1 + laju_bau / 100.0) ** idx
            E_listrik_bau = r24["E_Listrik_TJ"] * faktor_bau
            E_lpg_bau = r24["E_LPG_TJ"] * faktor_bau
            E_gas_bau = r24["E_Gas_TJ"] * faktor_bau
            C_bau_t = c24 * faktor_bau

            # Intervensi 1: Program Labelling mengurangi kebutuhan energi listrik (TJ) -> menekan Intensitas Energi (E/Y)
            red_label_gg = target_label_dlh[idx] * (capai_label / 100.0)
            hemat_listrik_tj = red_label_gg / r24["EF_Listrik_TJ"]
            E_listrik_sim = max(1.0, E_listrik_bau - hemat_listrik_tj)

            # Intervensi 2: Dekarbonisasi Grid menurunkan Faktor Emisi Listrik (Ci/Ei) pada sisa listrik
            ef_listrik_sim_tj = r24["EF_Listrik_TJ"] * (1.0 - (cut_grid / 100.0) * (idx / 6.0))
            C_listrik_sim = E_listrik_sim * ef_listrik_sim_tj
            C_lpg_sim = E_lpg_bau * r24["EF_LPG_TJ"]
            C_gas_sim = E_gas_bau * r24["EF_Gas_TJ"]
            C_sim_t = C_listrik_sim + C_lpg_sim + C_gas_sim

            bau_list.append(C_bau_t)
            sim_list.append(C_sim_t)

            if thn == 2030:
                red_grid_2030 = (E_listrik_sim * r24["EF_Listrik_TJ"]) - C_listrik_sim
                red_label_2030 = (E_listrik_bau - E_listrik_sim) * r24["EF_Listrik_TJ"]
                baris_2030_sim = pd.Series(
                    {
                        "Tahun": 2030,
                        "Penduduk_Juta": P_t,
                        "PDRB_Konstan_T": Y_t,
                        "EF_Listrik_TJ": ef_listrik_sim_tj,
                        "EF_LPG_TJ": r24["EF_LPG_TJ"],
                        "EF_Gas_TJ": r24["EF_Gas_TJ"],
                        "E_Listrik_TJ": E_listrik_sim,
                        "E_LPG_TJ": E_lpg_bau,
                        "E_Gas_TJ": E_gas_bau,
                        "E_Total_TJ": E_listrik_sim + E_lpg_bau + E_gas_bau,
                        "C_Listrik": C_listrik_sim,
                        "C_LPG": C_lpg_sim,
                        "C_Gas": C_gas_sim,
                        "C_Total_Gg": C_sim_t,
                    }
                )

    emisi_2030_bau = bau_list[-1]
    emisi_2030_sim = sim_list[-1]
    total_reduksi_2030 = emisi_2030_bau - emisi_2030_sim
    persen_reduksi_2030 = (total_reduksi_2030 / emisi_2030_bau) * 100.0
    perubahan_vs_2024 = emisi_2030_sim - c24

    st.markdown("**2. Ringkasan Hasil Simulasi Tahun 2030**")
    m1, m2, m3 = st.columns(3)
    m1.metric(
        "Emisi Rumah Tangga 2030 (Skenario)",
        f"{fmt_id(emisi_2030_sim)} Gg CO₂e",
        f"{fmt_tanda(perubahan_vs_2024)} Gg dibanding aktual 2024",
        delta_color="inverse",
    )
    m2.metric(
        "Total Penurunan Emisi terhadap Baseline 2030",
        f"{fmt_id(total_reduksi_2030)} Gg CO₂e",
        f"−{fmt_id(persen_reduksi_2030, 1)}% dari Baseline ({fmt_id(emisi_2030_bau)} Gg)",
        delta_color="normal",
    )
    porsi_label = (red_label_2030 / total_reduksi_2030 * 100) if total_reduksi_2030 > 0 else 0.0
    porsi_grid = (red_grid_2030 / total_reduksi_2030 * 100) if total_reduksi_2030 > 0 else 0.0
    m3.metric(
        "Sumber Reduksi 2030 (Bebas Hitung Ganda)",
        f"{fmt_id(porsi_label, 0)}% Efisiensi : {fmt_id(porsi_grid, 0)}% Grid",
        f"Labelling {fmt_id(red_label_2030)} Gg + Grid {fmt_id(red_grid_2030)} Gg",
        delta_color="off",
    )

    if total_reduksi_2030 > 0:
        st.markdown(
            f"""
            <div style="margin: 4px 0 18px 0;">
                <div style="font-size:0.85rem;font-weight:600;color:#334155;">
                    Komposisi Penurunan Emisi 2030: Program Labelling Efisiensi ({fmt_id(red_label_2030)} Gg) vs. Listrik Lebih Bersih ({fmt_id(red_grid_2030)} Gg)
                </div>
                <div class="bar-split">
                    <div style="width:{porsi_label:.1f}%;background:#1E4E79;"></div>
                    <div style="width:{porsi_grid:.1f}%;background:#1F8A70;"></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.markdown("**Lintasan Emisi Aktual (2019–2024) & Simulasi (2024–2030)**")
        hist = df[df["Tahun"] >= 2019]
        fig_sim = go.Figure()
        fig_sim.add_trace(
            go.Scatter(
                x=hist["Tahun"], y=hist["C_Total_Gg"], name="Aktual (2019–2024)",
                mode="lines+markers", line=dict(color=WARNA["aktual"], width=2.5),
            )
        )
        fig_sim.add_trace(
            go.Scatter(
                x=tahun_proj, y=bau_list, name="Tanpa Program (Baseline BaU)",
                mode="lines+markers", line=dict(color=WARNA["bau"], width=2, dash="dash"),
            )
        )
        fig_sim.add_trace(
            go.Scatter(
                x=tahun_proj, y=sim_list, name="Skenario Simulasi LMDI",
                mode="lines+markers", fill="tonexty", fillcolor="rgba(15, 82, 186, 0.12)",
                line=dict(color=WARNA["simulasi"], width=3),
            )
        )
        fig_sim = tata_letak(fig_sim, "Gg CO₂e", 370)
        fig_sim.update_xaxes(dtick=1)
        tampil(fig_sim)

    with col_g2:
        st.markdown("**Dekomposisi LMDI pada Skenario Simulasi (2024–2030)**")
        lmdi_sim_24_30 = hitung_lmdi_baris(r24, baris_2030_sim, "PDRB_Konstan_T", "2024–2030 (Simulasi)")
        tampil(buat_waterfall(lmdi_sim_24_30, tinggi=370))

    kotak(
        "Interpretasi Otomatis Simulasi Berbasis LMDI (Siap Masuk Subbab 4.4 Skripsi)",
        f"Pada periode proyeksi <b>2024–2030</b>, pertumbuhan penduduk dan peningkatan kemakmuran tetap mendorong kenaikan emisi sebesar "
        f"<b>{fmt_tanda(lmdi_sim_24_30['Efek Penduduk (ΔC_pop)'])} Gg</b> dan <b>{fmt_tanda(lmdi_sim_24_30['Efek Kemakmuran (ΔC_aff)'])} Gg CO₂e</b>. "
        f"Namun, melalui intervensi efisiensi <i>Program Labelling</i> ({capai_label}% target DLH) dan penurunan faktor emisi jaringan listrik ({cut_grid}%), "
        f"<b>Efek Intensitas Energi ({fmt_tanda(lmdi_sim_24_30['Efek Intensitas Energi (ΔC_int)'])} Gg)</b> dan "
        f"<b>Efek Faktor Emisi ({fmt_tanda(lmdi_sim_24_30['Efek Faktor Emisi (ΔC_ef)'])} Gg)</b> mampu membalikkan arah emisi sehingga "
        f"total emisi rumah tangga tahun 2030 berhasil ditekan sebesar <b>{fmt_tanda(lmdi_sim_24_30[KEY_TOTAL])} Gg CO₂e</b> dibanding tahun 2024 "
        f"(atau lebih rendah <b>{fmt_id(total_reduksi_2030)} Gg / {fmt_id(persen_reduksi_2030, 1)}%</b> dari Baseline 2030).",
        hijau=True,
    )
