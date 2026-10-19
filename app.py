import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import html as _html

# ==========================================================
# KONFIGURASI HALAMAN & GAYA VISUAL
# ==========================================================
st.set_page_config(
    page_title="Emisi GRK Rumah Tangga DKI Jakarta",
    page_icon="🌿",
    layout="wide",
)

FONT = "Segoe UI, Roboto, Helvetica, Arial, sans-serif"
WARNA = {
    "listrik": "#2F5D8A", "lpg": "#E0A458", "gas": "#6BA292",
    "naik": "#C8553D", "turun": "#2A9D8F", "total": "#264653",
    "aktual": "#52606D", "bau": "#9AA5B1", "simulasi": "#1D4E89",
    "cpos": "#D08C2D", "nze": "#5B8E7D",
}

st.markdown(
    """
    <style>
    .block-container { padding-top: 1.6rem; padding-bottom: 3rem; max-width: 1200px; }
    .stApp, .stApp p, .stApp li, .stApp label, .stApp td, .stApp th,
    .stApp h1, .stApp h2, .stApp h3, .stApp h4 {
        font-family: -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    h2, h3 { font-weight: 700 !important; letter-spacing: -0.01em; }
    h3 { font-size: 1.15rem !important; margin-top: 0.6rem; }
    #MainMenu, footer { visibility: hidden; }

    /* ---------- HERO ---------- */
    .hero { position: relative; overflow: hidden; border-radius: 20px; padding: 34px 36px 26px; margin-bottom: 18px;
            background: linear-gradient(135deg, #0B3C5D 0%, #17607F 52%, #2A9D8F 100%);
            box-shadow: 0 10px 30px rgba(11,60,93,.25); }
    .hero:before { content: ""; position: absolute; right: -80px; top: -90px; width: 330px; height: 330px; border-radius: 50%;
            background: radial-gradient(circle, rgba(255,255,255,.22), rgba(255,255,255,0) 70%); }
    .hero:after { content: ""; position: absolute; right: 150px; bottom: -130px; width: 270px; height: 270px; border-radius: 50%;
            background: radial-gradient(circle, rgba(224,164,88,.38), rgba(224,164,88,0) 70%); }
    .hero > div { position: relative; z-index: 1; }
    .stApp .hero div, .stApp .hero span, .stApp .hero b { color: #ffffff; }
    .hero-title { font-size: 2.05rem; font-weight: 800; letter-spacing: -0.02em; line-height: 1.15; margin: 10px 0 8px; }
    .hero-sub { font-size: 1.02rem; opacity: .93; max-width: 740px; margin-bottom: 18px; }
    .chip { display: inline-block; padding: 4px 12px; margin: 0 8px 6px 0; border-radius: 999px; font-size: .78rem; font-weight: 500;
            background: rgba(255,255,255,.16); border: 1px solid rgba(255,255,255,.3); }
    .hero-nav { display: flex; gap: 10px; flex-wrap: wrap; }
    .hero-nav > div { background: rgba(255,255,255,.12); border-radius: 12px; padding: 8px 14px; font-size: .86rem; }
    .hero-nav b { display: block; font-size: .68rem; letter-spacing: .08em; opacity: .75; text-transform: uppercase; font-weight: 600; }

    /* ---------- KARTU KPI ---------- */
    .kpi { border-radius: 16px; padding: 15px 18px; background: rgba(128,128,128,.06);
           border: 1px solid rgba(128,128,128,.18); border-top: 4px solid var(--aksen); margin-bottom: 8px; }
    .kpi-ikon { font-size: 1.2rem; }
    .kpi-label { font-size: .78rem; opacity: .72; margin-top: 2px; }
    .kpi-nilai { font-size: 1.6rem; font-weight: 800; letter-spacing: -0.02em; margin: 2px 0; }
    .kpi-sub { font-size: .8rem; opacity: .85; }
    .kpi-sub.buruk { color: #C8553D; font-weight: 600; opacity: 1; }
    .kpi-sub.baik { color: #2A9D8F; font-weight: 600; opacity: 1; }

    /* ---------- LANGKAH / PANDUAN ---------- */
    .langkah { display: grid; grid-template-columns: repeat(auto-fit, minmax(235px, 1fr)); gap: 14px; margin: 8px 0 20px; }
    .lk { border-radius: 16px; padding: 16px 18px; background: rgba(128,128,128,.06); border: 1px solid rgba(128,128,128,.18); }
    .lk-no { width: 30px; height: 30px; border-radius: 50%; background: var(--aksen); color: #fff; font-weight: 700;
             display: flex; align-items: center; justify-content: center; margin-bottom: 8px; }
    .lk-judul { font-weight: 700; margin-bottom: 4px; }
    .lk-isi { font-size: .88rem; opacity: .85; line-height: 1.45; }

    /* ---------- KOTAK INFO ---------- */
    .kotak { border-left: 4px solid #1D4E89; background: rgba(29,78,137,0.07); padding: 14px 18px;
             border-radius: 0 12px 12px 0; margin: 6px 0 18px 0; }
    .kotak.peringatan { border-left-color: #D08C2D; background: rgba(208,140,45,0.09); }
    .kotak-judul { font-weight: 700; margin-bottom: 6px; }
    .kotak ul { margin: 0; padding-left: 1.1rem; }
    .kotak li { margin-bottom: 5px; }

    /* ---------- TABEL (tanpa scroll) ---------- */
    .tbl { width: 100%; border-collapse: separate; border-spacing: 0; font-size: .86rem; margin: 6px 0 14px;
           border: 1px solid rgba(128,128,128,.25); border-radius: 12px; overflow: hidden; }
    .tbl th { background: rgba(29,78,137,.10); font-weight: 600; padding: 9px 10px; text-align: right;
              font-size: .78rem; line-height: 1.25; vertical-align: bottom; }
    .tbl td { padding: 8px 10px; border-top: 1px solid rgba(128,128,128,.15); }
    .tbl td.kanan { text-align: right; font-variant-numeric: tabular-nums; }
    .tbl th:first-child, .tbl td.kiri { text-align: left; }
    .tbl tr:nth-child(even) td { background: rgba(128,128,128,.045); }
    .tbl td.naik { color: #C8553D; font-weight: 600; }
    .tbl td.turun { color: #2A9D8F; font-weight: 600; }
    .tbl.kecil { font-size: .75rem; }
    .tbl.kecil th, .tbl.kecil td { padding: 6px 6px; }
    .tbl.teks th { text-align: left; }
    .tbl.teks td { text-align: left; vertical-align: top; line-height: 1.4; }

    /* ---------- PERSAMAAN & VERDICT ---------- */
    .pers { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; margin: 6px 0 18px; }
    .pc { border-radius: 12px; padding: 8px 12px; text-align: center; min-width: 92px; border: 1px solid rgba(128,128,128,.25); }
    .pc span { display: block; font-size: .7rem; opacity: .78; }
    .pc b { font-size: 1.05rem; }
    .pc.awal { background: #264653; border-color: #264653; }
    .pc.awal span, .pc.awal b { color: #fff !important; }
    .pc.naik { background: rgba(200,85,61,.12); border-color: rgba(200,85,61,.4); }
    .pc.turun { background: rgba(42,157,143,.12); border-color: rgba(42,157,143,.4); }
    .op { font-weight: 800; opacity: .55; font-size: 1.1rem; }
    .verdict { border-radius: 16px; padding: 16px 18px; background: rgba(128,128,128,.06); border: 1px solid rgba(128,128,128,.18);
               border-top: 4px solid var(--aksen); margin-bottom: 10px; }
    .verdict-judul { font-weight: 700; margin-bottom: 6px; }
    .verdict p { font-size: .9rem; margin: 0 0 6px; line-height: 1.45; }

    /* ---------- SIMULASI ---------- */
    .legenda { display: flex; flex-wrap: wrap; gap: 16px; font-size: .86rem; margin: 4px 0 14px; }
    .legenda i { display: inline-block; width: 11px; height: 11px; border-radius: 3px; margin-right: 6px; }
    .split { display: flex; height: 14px; border-radius: 8px; overflow: hidden; margin: 8px 0 8px; background: rgba(128,128,128,.15); }
    button[data-baseweb="tab"] p { font-weight: 600; font-size: .98rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


def fmt_id(x, d=0):
    """Format angka gaya Indonesia: 1.234,5"""
    return f"{x:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def fmt_tanda(x, d=0):
    """Angka bertanda (+/−) gaya Indonesia"""
    if abs(x) < 0.5 * 10 ** (-d):
        return fmt_id(0, d)
    return ("+" if x > 0 else "−") + fmt_id(abs(x), d)


def kotak(judul, isi_html, peringatan=False):
    kelas = "kotak peringatan" if peringatan else "kotak"
    st.markdown(f'<div class="{kelas}"><div class="kotak-judul">{judul}</div>{isi_html}</div>', unsafe_allow_html=True)


def kpi(label, nilai, sub, aksen, ikon, nada=""):
    return (f'<div class="kpi" style="--aksen:{aksen}"><div class="kpi-ikon">{ikon}</div>'
            f'<div class="kpi-label">{label}</div><div class="kpi-nilai">{nilai}</div>'
            f'<div class="kpi-sub {nada}">{sub}</div></div>')


def html_tabel(disp, raw=None, warna=(), kecil=False, teks=False):
    """Tabel HTML yang melebar penuh (tanpa scroll). raw+warna: beri warna merah/hijau menurut tanda angka."""
    kelas = "tbl" + (" kecil" if kecil else "") + (" teks" if teks else "")
    h = f'<table class="{kelas}"><thead><tr>' + "".join(f"<th>{_html.escape(str(c))}</th>" for c in disp.columns) + "</tr></thead><tbody>"
    for i in range(len(disp)):
        h += "<tr>"
        for j, c in enumerate(disp.columns):
            v = _html.escape(str(disp.iloc[i, j]))
            cls = "kiri" if (j == 0 or teks) else "kanan"
            if raw is not None and c in warna:
                x = float(raw.iloc[i][c])
                cls += " naik" if x > 0.005 else " turun" if x < -0.005 else ""
            h += f'<td class="{cls}">{v}</td>'
        h += "</tr>"
    h += "</tbody></table>"
    st.markdown(h, unsafe_allow_html=True)


def tata_letak(fig, y_title=None, tinggi=380):
    fig.update_layout(
        template="plotly_white",
        font=dict(family=FONT, size=12, color="#1f2933"),
        paper_bgcolor="white", plot_bgcolor="white",
        margin=dict(l=10, r=10, t=40, b=10), height=tinggi,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, title_text=""),
        hovermode="x unified",
        yaxis=dict(title=y_title, gridcolor="#E8ECEF", zerolinecolor="#CBD2D9"),
        xaxis=dict(showgrid=False),
    )
    return fig


def tampil(fig):
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})


# ==========================================================
# 1. DATA (LAPORAN AKHIR DLH DKI JAKARTA 2026)
# ==========================================================
data_historis = {
    "Tahun": list(range(2010, 2025)),
    "Penduduk_Juta": [9.64, 9.89, 9.86, 9.97, 10.08, 10.18, 10.28, 10.37, 10.47, 10.56, 10.56, 10.61, 10.68, 10.67, 10.68],
    "PDRB_Konstan_T": [1080.00, 1260.00, 1222.53, 1296.69, 1373.39, 1454.56, 1539.92, 1635.36, 1735.21, 1836.24, 1792.29, 1856.00, 1953.49, 2050.47, 2151.04],
    "PDRB_Berlaku_T": [1075.0, 1224.0, 1369.0, 1547.0, 1762.0, 1989.0, 2159.0, 2365.0, 2593.0, 2816.0, 2767.0, 2913.0, 3189.0, 3443.0, 3679.0],
    "EF_Listrik_MWh": [0.830, 0.880, 0.927, 0.967, 0.949, 1.023, 0.990, 0.897, 0.894, 0.906, 0.902, 0.896, 0.901, 0.903, 0.903],
    "C_Listrik": [7560.0, 8400.0, 9590.0, 11100.0, 10500.0, 11700.0, 12500.0, 11300.0, 11800.0, 12600.0, 13100.0, 13100.0, 13300.0, 14100.0, 14828.0],
    "C_LPG": [982.0, 1044.0, 1082.0, 1076.0, 1076.0, 1393.0, 1366.0, 1444.0, 1447.0, 1266.0, 1289.0, 1300.0, 1318.0, 1338.0, 1348.0],
    "C_Gas": [0.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 7.0, 7.0, 7.0, 4.0],  # 2010: tabel DLH = 0 (pembulatan)
}
DELTA = 1e-20  # pengganti nilai nol agar logaritma terdefinisi (praktik umum pada LMDI)


def bangun_df(gas_2010):
    d = pd.DataFrame(data_historis)
    d.loc[d["Tahun"] == 2010, "C_Gas"] = gas_2010
    d["EF_Listrik_TJ"] = d["EF_Listrik_MWh"] / 3.6        # 1 GWh = 3,6 TJ
    d["EF_LPG_TJ"] = 0.06537                              # Tabel 3.5: 65.370 kg CO2/TJ
    d["EF_Gas_TJ"] = 0.05764                              # Tabel 3.5: 57.640 kg CO2/TJ
    d["E_Listrik_TJ"] = d["C_Listrik"] / d["EF_Listrik_TJ"]
    d["E_LPG_TJ"] = d["C_LPG"] / d["EF_LPG_TJ"]
    d["E_Gas_TJ"] = d["C_Gas"] / d["EF_Gas_TJ"]
    d["E_Total_TJ"] = d["E_Listrik_TJ"] + d["E_LPG_TJ"] + d["E_Gas_TJ"]
    d["C_Total_Gg"] = d["C_Listrik"] + d["C_LPG"] + d["C_Gas"]
    return d


# ==========================================================
# 2. SIDEBAR
# ==========================================================
with st.sidebar:
    st.markdown("#### Tentang penelitian")
    st.caption(
        "**Dekomposisi Pendorong Perubahan Emisi GRK Sektor Rumah Tangga DKI Jakarta (2010–2024) "
        "dan Simulasi Skenario Mitigasi Menuju 2050**"
    )
    st.caption(
        "Peneliti: Dewantara Putra Makmur  \nNIM: G2401231071  \n"
        "Pembimbing: Perdinan, S.Si., M.Nat.Res.Econ., Ph.D.  \n"
        "Departemen Geofisika dan Meteorologi, FMIPA IPB University"
    )
    st.divider()
    st.markdown("#### Metode")
    st.latex(r"C = \sum_i P \times \frac{Y}{P} \times \frac{E}{Y} \times \frac{E_i}{E} \times \frac{C_i}{E_i}")
    st.caption("LMDI-I aditif (Ang 2005, 2015). Sumber data: Laporan Akhir Inventarisasi Profil Emisi & Pelaporan Penurunan Emisi GRK Provinsi DKI Jakarta (DLH 2026).")
    st.divider()
    with st.expander("Pengaturan data (lanjutan)"):
        opsi_gas = st.radio(
            "Emisi gas bumi tahun 2010 (tabel DLH tertulis 0 karena pembulatan)",
            ["Nilai positif sangat kecil (10⁻²⁰)", "Diganti 0,4 Gg CO₂e"],
            index=0,
            help="LMDI memakai logaritma sehingga nilai nol perlu diganti. Selisih hasil kedua pilihan kurang dari 2 Gg CO₂e.",
        )

df = bangun_df(DELTA if opsi_gas.startswith("Nilai") else 0.4)

# ==========================================================
# 3. FUNGSI LMDI ADITIF
# ==========================================================
EFEK_KEYS = [
    "Efek Penduduk (ΔC_pop)", "Efek Kemakmuran (ΔC_aff)", "Efek Intensitas Energi (ΔC_int)",
    "Efek Bauran Energi (ΔC_mix)", "Efek Faktor Emisi (ΔC_ef)",
]
NAMA = {
    "Efek Penduduk (ΔC_pop)": "Pertumbuhan penduduk",
    "Efek Kemakmuran (ΔC_aff)": "Kemakmuran (PDRB per kapita)",
    "Efek Intensitas Energi (ΔC_int)": "Intensitas energi (efisiensi)",
    "Efek Bauran Energi (ΔC_mix)": "Bauran bahan bakar",
    "Efek Faktor Emisi (ΔC_ef)": "Faktor emisi listrik",
}
KEY_TOTAL = "Perubahan Total (ΔC)"


def log_mean(c_t, c_0):
    if np.isclose(c_t, c_0):
        return c_0
    return (c_t - c_0) / (np.log(c_t) - np.log(c_0))


def hitung_lmdi(df_data, thn_awal, thn_akhir, kolom_pdrb="PDRB_Konstan_T"):
    r0 = df_data[df_data["Tahun"] == thn_awal].iloc[0]
    rt = df_data[df_data["Tahun"] == thn_akhir].iloc[0]

    P0, Pt = r0["Penduduk_Juta"], rt["Penduduk_Juta"]
    Y0, Yt = r0[kolom_pdrb], rt[kolom_pdrb]
    E0, Et = r0["E_Total_TJ"], rt["E_Total_TJ"]
    g0, gt = Y0 / P0, Yt / Pt
    I0, It = E0 / Y0, Et / Yt

    fuels = [("C_Listrik", "E_Listrik_TJ", "EF_Listrik_TJ"),
             ("C_LPG", "E_LPG_TJ", "EF_LPG_TJ"),
             ("C_Gas", "E_Gas_TJ", "EF_Gas_TJ")]

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
        "Periode": f"{thn_awal}–{thn_akhir}",
        KEY_TOTAL: round(dC_total, 2),
        "Efek Penduduk (ΔC_pop)": round(dC_pop, 2),
        "Efek Kemakmuran (ΔC_aff)": round(dC_aff, 2),
        "Efek Intensitas Energi (ΔC_int)": round(dC_int, 2),
        "Efek Bauran Energi (ΔC_mix)": round(dC_mix, 2),
        "Efek Faktor Emisi (ΔC_ef)": round(dC_ef, 2),
        "Residual": round(dC_total - (dC_pop + dC_aff + dC_int + dC_mix + dC_ef), 4),
    }


SHORT = {
    "Pertumbuhan penduduk": "Penduduk", "Kemakmuran (PDRB per kapita)": "Kemakmuran",
    "Intensitas energi (efisiensi)": "Intensitas energi", "Bauran bahan bakar": "Bauran bahan bakar",
    "Faktor emisi listrik": "Faktor emisi listrik",
}


def tabel_efek(baris):
    """Kembalikan (tabel tampilan Indonesia, tabel angka mentah) untuk tabel efek."""
    d = pd.DataFrame(baris)
    disp = pd.DataFrame({"Periode": d["Periode"]})
    raw = pd.DataFrame({"Periode": d["Periode"]})
    disp["Total perubahan"] = d[KEY_TOTAL].map(lambda v: fmt_tanda(v, 1))
    for k in EFEK_KEYS:
        disp[NAMA[k]] = d[k].map(lambda v: fmt_tanda(v, 1))
        raw[NAMA[k]] = d[k]
    disp["Selisih hitung"] = d["Residual"].map(lambda v: fmt_id(0.0 if abs(v) < 0.005 else v, 2))
    return disp, raw


# ==========================================================
# 4. HEADER & KPI
# ==========================================================
r10 = df[df["Tahun"] == 2010].iloc[0]
r19 = df[df["Tahun"] == 2019].iloc[0]
r24 = df[df["Tahun"] == 2024].iloc[0]
c10, c19, c24 = r10["C_Total_Gg"], r19["C_Total_Gg"], r24["C_Total_Gg"]
porsi_listrik = r24["C_Listrik"] / c24
tumbuh_total = (c24 / c10 - 1) * 100
kapita10 = c10 / r10["Penduduk_Juta"] / 1000
kapita24 = c24 / r24["Penduduk_Juta"] / 1000
TARGET_LABELLING_2030 = 3630.0

st.markdown(
    """
    <div class="hero">
      <div>
        <span class="chip">Data 2010–2024</span><span class="chip">Metode LMDI</span>
        <span class="chip">Simulasi hingga 2050</span><span class="chip">Sumber: DLH DKI Jakarta 2026</span>
      </div>
      <div class="hero-title">Emisi Gas Rumah Kaca<br>Rumah Tangga DKI Jakarta</div>
      <div class="hero-sub">Apa yang mendorong naiknya emisi dalam 14 tahun terakhir, dan seberapa jauh program mitigasi bisa menurunkannya hingga 2050?</div>
      <div class="hero-nav">
        <div><b>Langkah 1</b>Lihat datanya</div><div><b>Langkah 2</b>Cari penyebabnya</div>
        <div><b>Langkah 3</b>Uji kepercayaannya</div><div><b>Langkah 4</b>Coba simulasinya</div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

k1, k2, k3, k4 = st.columns(4)
k1.markdown(kpi("Total emisi 2024", f"{fmt_id(c24)} Gg", f"{fmt_tanda(tumbuh_total, 1)}% dibanding 2010", "#C8553D", "🏙️", "buruk"), unsafe_allow_html=True)
k2.markdown(kpi("Emisi per penduduk 2024", f"{fmt_id(kapita24, 2)} tCO₂e", f"{fmt_tanda((kapita24 / kapita10 - 1) * 100, 1)}% dibanding 2010", "#D08C2D", "👥", "buruk"), unsafe_allow_html=True)
k3.markdown(kpi("Porsi emisi dari listrik", f"{fmt_id(porsi_listrik * 100, 1)}%", f"{fmt_id(r24['C_Listrik'])} Gg CO₂e pada 2024", "#2F5D8A", "⚡"), unsafe_allow_html=True)
k4.markdown(kpi("Target reduksi labelling 2030", f"{fmt_id(TARGET_LABELLING_2030)} Gg", f"setara {fmt_id(TARGET_LABELLING_2030 / c24 * 100, 1)}% emisi 2024 (DLH)", "#2A9D8F", "🎯"), unsafe_allow_html=True)

st.write("")
tab0, tab1, tab2, tab3, tab4 = st.tabs(
    ["🏠 Ringkasan", "📈 Data Historis", "🔍 Faktor Pendorong", "🧪 Uji Kepekaan", "🎛️ Simulasi Mitigasi"]
)

# ==========================================================
# TAB 0: RINGKASAN
# ==========================================================
with tab0:
    h_all = hitung_lmdi(df, 2010, 2024, "PDRB_Konstan_T")
    efek_all = {k: h_all[k] for k in EFEK_KEYS}
    k_naik = max(efek_all, key=efek_all.get)
    k_turun = min(efek_all, key=efek_all.get)
    poin = [
        f"Emisi rumah tangga naik dari <b>{fmt_id(c10)}</b> menjadi <b>{fmt_id(c24)}</b> Gg CO₂e pada 2010–2024 (<b>{fmt_tanda(tumbuh_total, 1)}%</b>).",
        f"Pendorong kenaikan terbesar: <b>{NAMA[k_naik].lower()}</b> ({fmt_tanda(efek_all[k_naik])} Gg CO₂e).",
    ]
    if efek_all[k_turun] < 0:
        poin.append(f"Faktor yang menahan kenaikan: <b>{NAMA[k_turun].lower()}</b> ({fmt_tanda(efek_all[k_turun])} Gg CO₂e).")
    poin.append(f"Sekitar <b>{fmt_id(porsi_listrik * 100, 1)}%</b> emisi berasal dari listrik, sehingga efisiensi peralatan listrik dan pembangkit yang lebih bersih adalah tuas utama penurunan emisi.")
    kotak("Temuan utama", "<ul>" + "".join(f"<li>{p}</li>" for p in poin) + "</ul>")

    st.markdown("### Cara membaca dashboard ini")
    st.markdown(
        """
        <div class="langkah">
          <div class="lk" style="--aksen:#2F5D8A"><div class="lk-no">1</div><div class="lk-judul">📈 Data Historis</div>
            <div class="lk-isi">Lihat emisi dan energi rumah tangga tiap tahun, serta dari sumber apa saja emisi itu berasal.</div></div>
          <div class="lk" style="--aksen:#C8553D"><div class="lk-no">2</div><div class="lk-judul">🔍 Faktor Pendorong</div>
            <div class="lk-isi">Pecah perubahan emisi menjadi lima penyebab, lalu lihat mana yang menaikkan dan mana yang menurunkan.</div></div>
          <div class="lk" style="--aksen:#D08C2D"><div class="lk-no">3</div><div class="lk-judul">🧪 Uji Kepekaan</div>
            <div class="lk-isi">Periksa apakah kesimpulan tetap sama jika data atau cara hitungnya diganti.</div></div>
          <div class="lk" style="--aksen:#2A9D8F"><div class="lk-no">4</div><div class="lk-judul">🎛️ Simulasi Mitigasi</div>
            <div class="lk-isi">Pilih skenario kebijakan dan lihat dampaknya pada emisi 2030 dan 2050.</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("Satuan emisi: Gg CO₂e. 1 Gg = 1.000 ton CO₂ ekuivalen.")

    with st.expander("Arti istilah yang dipakai"):
        istilah = pd.DataFrame([
            ("Pertumbuhan penduduk", "Emisi bertambah karena jumlah penduduk bertambah"),
            ("Kemakmuran", "Emisi bertambah karena ekonomi per orang tumbuh (konsumsi lebih banyak)"),
            ("Intensitas energi", "Energi yang dipakai untuk setiap rupiah PDRB. Turun berarti lebih efisien sehingga menahan emisi"),
            ("Bauran bahan bakar", "Perubahan porsi listrik, LPG, dan gas bumi"),
            ("Faktor emisi listrik", "Emisi per satuan listrik. Turun jika pembangkit makin bersih"),
            ("BaU (baseline)", "Lintasan emisi jika tidak ada program mitigasi tambahan"),
            ("CPOS dan NZE", "Skenario kebijakan berjalan (CPOS) dan nol emisi bersih 2050 (NZE), acuan DLH"),
        ], columns=["Istilah", "Arti sederhana"])
        html_tabel(istilah, teks=True)

# ==========================================================
# TAB 1: DATA HISTORIS
# ==========================================================
with tab1:
    st.subheader("Emisi dan konsumsi energi rumah tangga, 2010–2024")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Emisi GRK per sumber (Gg CO₂e)**")
        fig = go.Figure()
        for col, nama, w in [("C_Listrik", "Listrik (tidak langsung)", WARNA["listrik"]),
                             ("C_LPG", "LPG (langsung)", WARNA["lpg"]),
                             ("C_Gas", "Gas bumi (langsung)", WARNA["gas"])]:
            fig.add_trace(go.Bar(x=df["Tahun"], y=df[col], name=nama, marker_color=w, hovertemplate="%{y:,.0f}"))
        fig.update_layout(barmode="stack")
        tampil(tata_letak(fig))
    with col2:
        st.markdown("**Konsumsi energi final (TJ)**")
        fig = go.Figure()
        for col, nama, w in [("E_Listrik_TJ", "Listrik", WARNA["listrik"]),
                             ("E_LPG_TJ", "LPG", WARNA["lpg"]),
                             ("E_Gas_TJ", "Gas bumi", WARNA["gas"])]:
            fig.add_trace(go.Scatter(x=df["Tahun"], y=df[col], name=nama, mode="lines", stackgroup="e",
                                     line=dict(width=1, color=w), hovertemplate="%{y:,.0f}"))
        tampil(tata_letak(fig))

    st.markdown("**Tabel data**")
    tabel_raw = df[["Tahun", "Penduduk_Juta", "PDRB_Konstan_T", "PDRB_Berlaku_T", "EF_Listrik_MWh",
                    "C_Listrik", "C_LPG", "C_Gas", "C_Total_Gg", "E_Total_TJ"]].rename(columns={
        "Penduduk_Juta": "Penduduk (juta)", "PDRB_Konstan_T": "PDRB konstan (T Rp)", "PDRB_Berlaku_T": "PDRB berlaku (T Rp)",
        "EF_Listrik_MWh": "EF listrik (tCO₂/MWh)", "C_Listrik": "Emisi listrik (Gg)", "C_LPG": "Emisi LPG (Gg)",
        "C_Gas": "Emisi gas (Gg)", "C_Total_Gg": "Total emisi (Gg)", "E_Total_TJ": "Total energi (TJ)",
    })
    tabel_tampil = tabel_raw.copy()
    for kolom in tabel_tampil.columns[1:]:
        d_ = 3 if "EF listrik" in kolom else 2 if ("Penduduk" in kolom or "PDRB" in kolom) else 0
        tabel_tampil[kolom] = tabel_raw[kolom].map(lambda v, d_=d_: fmt_id(v, d_))
    tabel_tampil["Tahun"] = tabel_raw["Tahun"].astype(str)
    html_tabel(tabel_tampil, kecil=True)
    st.download_button("Unduh tabel (CSV)", tabel_raw.to_csv(index=False).encode("utf-8"),
                       "deret_data_rt_dki_2010_2024.csv", "text/csv")

    yoy = df["PDRB_Konstan_T"].pct_change() * 100
    with st.expander("Catatan kualitas data dan perlakuannya"):
        catatan = pd.DataFrame([
            ("PDRB harga konstan 2011", f"Naik {fmt_tanda(yoy.iloc[1], 1)}% (2011) lalu {fmt_tanda(yoy.iloc[2], 1)}% (2012), sedangkan tahun normal naik 4–6%.",
             "Dipakai apa adanya. Pengaruhnya diuji di Uji Kepekaan (B3). Perlu dicek ke sumber."),
            ("Penduduk 2019 dan 2020", f"Nilainya sama ({fmt_id(r19['Penduduk_Juta'], 2)} juta), sehingga efek penduduk 2019–2020 bernilai 0.",
             "Dipakai sesuai tabel DLH. Perlu dicek ke sumber."),
            ("Emisi gas bumi 2010", "Tertulis 0 di tabel (pembulatan), padahal LMDI memakai logaritma.",
             "Diganti nilai positif sangat kecil. Opsi 0,4 Gg ada di sidebar. Selisih hasil kurang dari 2 Gg."),
            ("Emisi 2019: inventaris vs acuan DLH", f"Inventaris {fmt_id(c19)} Gg, titik awal CPOS/NZE DLH 13.953 Gg (selisih {fmt_id(13953 - c19)} Gg).",
             "Ditampilkan terpisah dan diberi label pada grafik jangka panjang."),
        ], columns=["Item", "Temuan", "Perlakuan di dashboard"])
        html_tabel(catatan, teks=True)

# ==========================================================
# TAB 2: FAKTOR PENDORONG
# ==========================================================
with tab2:
    st.subheader("Apa yang mendorong perubahan emisi?")
    o1, o2, o3 = st.columns(3)
    with o1:
        jenis_pdrb = st.radio(
            "Basis PDRB", ["PDRB_Konstan_T", "PDRB_Berlaku_T"],
            format_func=lambda x: "Harga konstan (disarankan)" if x == "PDRB_Konstan_T" else "Harga berlaku",
            horizontal=True,
        )
    with o2:
        t_awal = st.selectbox("Tahun awal", list(range(2010, 2024)), index=0)
    with o3:
        opsi_akhir = list(range(t_awal + 1, 2025))
        t_akhir = st.selectbox("Tahun akhir", opsi_akhir, index=len(opsi_akhir) - 1)

    hasil = hitung_lmdi(df, t_awal, t_akhir, jenis_pdrb)
    e_awal = float(df.loc[df["Tahun"] == t_awal, "C_Total_Gg"].iloc[0])
    e_akhir = float(df.loc[df["Tahun"] == t_akhir, "C_Total_Gg"].iloc[0])
    total = hasil[KEY_TOTAL]

    st.markdown(f"##### Emisi {'naik' if total >= 0 else 'turun'} {fmt_id(abs(total))} Gg CO₂e pada {t_awal}–{t_akhir}. Dari mana asalnya?")
    kotak("Cara membaca",
          "Setiap batang adalah satu penyebab. Batang <b style='color:#C8553D'>merah ke kanan</b> berarti penyebab itu <b>menaikkan</b> emisi, "
          "batang <b style='color:#2A9D8F'>hijau ke kiri</b> berarti <b>menurunkan</b> emisi. Makin panjang batang, makin besar pengaruhnya. "
          "Jumlah semua batang sama dengan perubahan emisi total, seperti yang ditunjukkan persamaan di bawah grafik.")

    urut = sorted(EFEK_KEYS, key=lambda k: hasil[k])          # terbesar tampil di atas
    nilai = [hasil[k] for k in urut]
    rentang = max(abs(v) for v in nilai) or 1
    fig = go.Figure(go.Bar(
        x=nilai, y=[NAMA[k] for k in urut], orientation="h",
        marker_color=[WARNA["naik"] if v >= 0 else WARNA["turun"] for v in nilai],
        text=[fmt_tanda(v) for v in nilai], textposition="outside", cliponaxis=False,
        hovertemplate="%{y}: %{x:,.1f} Gg CO₂e<extra></extra>",
    ))
    fig = tata_letak(fig, None, 330)
    fig.update_layout(hovermode="closest", margin=dict(l=10, r=40, t=30, b=10), showlegend=False)
    fig.update_xaxes(range=[min(0, min(nilai)) - rentang * 0.25, max(0, max(nilai)) + rentang * 0.25],
                     zeroline=True, zerolinewidth=2, zerolinecolor="#52606D", showgrid=True, gridcolor="#E8ECEF", title="Gg CO₂e")
    fig.update_yaxes(showgrid=False)
    fig.add_annotation(xref="paper", yref="paper", x=0, y=1.1, showarrow=False, text="← menurunkan emisi", font=dict(color=WARNA["turun"], size=12), xanchor="left")
    fig.add_annotation(xref="paper", yref="paper", x=1, y=1.1, showarrow=False, text="menaikkan emisi →", font=dict(color=WARNA["naik"], size=12), xanchor="right")
    tampil(fig)

    pers = f'<div class="pers"><div class="pc awal"><span>Emisi {t_awal}</span><b>{fmt_id(e_awal)}</b></div>'
    for k in EFEK_KEYS:
        v = hasil[k]
        pers += (f'<div class="op">{"+" if v >= 0 else "−"}</div>'
                 f'<div class="pc {"naik" if v >= 0 else "turun"}"><span>{SHORT[NAMA[k]]}</span><b>{fmt_id(abs(v))}</b></div>')
    pers += f'<div class="op">=</div><div class="pc awal"><span>Emisi {t_akhir}</span><b>{fmt_id(e_akhir)}</b></div></div>'
    st.markdown(pers, unsafe_allow_html=True)

    st.markdown("##### Ringkasan per periode (Gg CO₂e)")
    ringkasan = [hitung_lmdi(df, a, b, jenis_pdrb) for a, b in
                 [(2010, 2019), (2019, 2020), (2020, 2024), (2019, 2024), (2010, 2024)]]
    disp, raw = tabel_efek(ringkasan)
    html_tabel(disp, raw, warna=[NAMA[k] for k in EFEK_KEYS])
    st.caption("Merah = menaikkan emisi, hijau = menurunkan. Periode: sebelum pandemi (2010–2019), tahun pandemi (2019–2020), "
               "sesudah pandemi (2020–2024), dan total. \"Selisih hitung\" harus 0: kelima penyebab menjumlah tepat ke total.")
    st.download_button("Unduh ringkasan (CSV)", pd.DataFrame(ringkasan).to_csv(index=False).encode("utf-8"),
                       "tabel_lmdi_multiperiode.csv", "text/csv")

    with st.expander("Lihat perubahan per tahun (2010–2024)"):
        rantai = pd.DataFrame([hitung_lmdi(df, y, y + 1, jenis_pdrb) for y in range(2010, 2024)])
        fig = go.Figure()
        warna_efek = {"Efek Penduduk (ΔC_pop)": "#E9B872", "Efek Kemakmuran (ΔC_aff)": WARNA["naik"],
                      "Efek Intensitas Energi (ΔC_int)": WARNA["turun"], "Efek Bauran Energi (ΔC_mix)": "#8E7CC3",
                      "Efek Faktor Emisi (ΔC_ef)": "#4FB3D9"}
        for k in EFEK_KEYS:
            fig.add_trace(go.Bar(name=NAMA[k], x=rantai["Periode"], y=rantai[k], marker_color=warna_efek[k]))
        fig.add_trace(go.Scatter(name="Total perubahan", x=rantai["Periode"], y=rantai[KEY_TOTAL],
                                 mode="lines+markers", line=dict(color="#111827", width=2.5)))
        fig.update_layout(barmode="relative")
        tampil(tata_letak(fig, "Gg CO₂e", 400))
        st.caption("Data PDRB konstan 2011 tampak tidak wajar, sehingga batang 2010–2011 dan 2011–2012 perlu dibaca hati-hati (lihat Uji Kepekaan B3).")

# ==========================================================
# TAB 3: UJI KEPEKAAN
# ==========================================================
with tab3:
    st.subheader("Apakah kesimpulan berubah jika asumsi diganti?")
    st.caption("Kami menghitung ulang dengan beberapa variasi. Jika penyebab terbesarnya tetap sama, kesimpulan kita kuat.")

    def baris_langsung(nama, basis):
        h = hitung_lmdi(df, 2010, 2024, basis)
        return {"Skenario": nama, **{k: h[k] for k in [KEY_TOTAL] + EFEK_KEYS}, "Residual": h["Residual"]}

    def baris_rantai(nama, basis, kecualikan=None, data=df):
        d = pd.DataFrame([hitung_lmdi(data, y, y + 1, basis) for y in range(2010, 2024) if y != kecualikan])
        return {"Skenario": nama, **{k: round(d[k].sum(), 2) for k in [KEY_TOTAL] + EFEK_KEYS},
                "Residual": round(d["Residual"].sum(), 4)}

    d11 = df.copy()   # PDRB konstan 2011 diinterpolasi (rata-rata geometrik 2010 dan 2012)
    d11.loc[d11["Tahun"] == 2011, "PDRB_Konstan_T"] = float(np.sqrt(
        d11.loc[d11["Tahun"] == 2010, "PDRB_Konstan_T"].iloc[0] * d11.loc[d11["Tahun"] == 2012, "PDRB_Konstan_T"].iloc[0]))

    sk = [
        baris_langsung("A1. Langsung 2010→2024, PDRB harga konstan", "PDRB_Konstan_T"),
        baris_langsung("A2. Langsung 2010→2024, PDRB harga berlaku", "PDRB_Berlaku_T"),
        baris_rantai("B1. Berantai tahunan, PDRB konstan (penuh)", "PDRB_Konstan_T"),
        baris_rantai("B2. Berantai tahunan, tanpa transisi 2019–2020", "PDRB_Konstan_T", kecualikan=2019),
        baris_rantai("B3. Berantai tahunan, PDRB 2011 diinterpolasi", "PDRB_Konstan_T", data=d11),
    ]

    def grup_bar(rows, labels, warna):
        fig = go.Figure()
        for r, lab, w in zip(rows, labels, warna):
            fig.add_trace(go.Bar(name=lab, x=[SHORT[NAMA[k]] for k in EFEK_KEYS], y=[r[k] for k in EFEK_KEYS],
                                 marker_color=w, hovertemplate="%{y:,.0f} Gg CO₂e"))
        fig.update_layout(barmode="group")
        fig = tata_letak(fig, "Gg CO₂e", 340)
        fig.update_xaxes(tickfont=dict(size=11))
        return fig

    def verdict(rows, aksen):
        naik = {max(EFEK_KEYS, key=lambda k: r[k]) for r in rows}
        turun = {min(EFEK_KEYS, key=lambda k: r[k]) for r in rows}
        sama = len(naik) == 1 and len(turun) == 1
        selisih = {k: max(r[k] for r in rows) - min(r[k] for r in rows) for k in EFEK_KEYS}
        k_ubah = max(selisih, key=selisih.get)
        angka = " → ".join(fmt_tanda(r[k_ubah]) for r in rows)
        if sama:
            judul = "✓ Kesimpulan utama tidak berubah"
            teks = (f"<b>{NAMA[next(iter(naik))]}</b> tetap pendorong terbesar dan <b>{NAMA[next(iter(turun))].lower()}</b> tetap penahan terbesar. "
                    "Yang berubah hanya ukurannya.")
        else:
            judul = "⚠ Peringkat penyebab berubah"
            teks = "Penyebab terbesar tidak sama di semua variasi, jadi kesimpulan perlu disampaikan dengan hati-hati."
        return (f'<div class="verdict" style="--aksen:{aksen}"><div class="verdict-judul">{judul}</div><p>{teks}</p>'
                f'<p><b>Efek yang paling bergeser:</b> {NAMA[k_ubah].lower()} ({angka} Gg CO₂e)</p></div>')

    cA, cB = st.columns(2, gap="large")
    with cA:
        st.markdown("##### A. Pakai PDRB harga konstan atau berlaku?")
        tampil(grup_bar(sk[:2], ["Harga konstan", "Harga berlaku"], [WARNA["simulasi"], WARNA["cpos"]]))
        st.markdown(verdict(sk[:2], WARNA["simulasi"]), unsafe_allow_html=True)
        st.caption("PDRB harga berlaku memuat inflasi sehingga membesarkan efek kemakmuran dan efisiensi secara semu. Harga konstan lebih sesuai sebagai basis utama.")
    with cB:
        st.markdown("##### B. Bagaimana jika pandemi dan data 2011 dikoreksi?")
        tampil(grup_bar(sk[2:], ["Penuh", "Tanpa 2019–2020", "PDRB 2011 diinterpolasi"], [WARNA["simulasi"], WARNA["naik"], WARNA["turun"]]))
        st.markdown(verdict(sk[2:], WARNA["naik"]), unsafe_allow_html=True)
        st.caption("Dugaan: pada 2020 konsumsi listrik rumah tangga naik saat PDRB turun (kemungkinan kerja dari rumah). Ini masih dugaan dan perlu rujukan.")

    with st.expander("Lihat angka lengkap"):
        d_sens = pd.DataFrame(sk)
        disp = pd.DataFrame({"Skenario": d_sens["Skenario"]})
        raw = pd.DataFrame({"Skenario": d_sens["Skenario"]})
        disp["Total perubahan"] = d_sens[KEY_TOTAL].map(lambda v: fmt_tanda(v, 1))
        for k in EFEK_KEYS:
            disp[NAMA[k]] = d_sens[k].map(lambda v: fmt_tanda(v, 1))
            raw[NAMA[k]] = d_sens[k]
        disp["Selisih hitung"] = d_sens["Residual"].map(lambda v: fmt_id(0.0 if abs(v) < 0.005 else v, 2))
        html_tabel(disp, raw, warna=[NAMA[k] for k in EFEK_KEYS])
        st.caption("Satuan: Gg CO₂e. A dan B tidak dibandingkan langsung karena dekomposisi langsung dan berantai membagi efek secara berbeda. "
                   "B3 mengganti PDRB 2011 dengan rata-rata geometrik 2010 dan 2012 (estimasi untuk pengujian, bukan data resmi).")

# ==========================================================
# TAB 4: SIMULASI MITIGASI
# ==========================================================
PRESET = {
    "Tanpa program": dict(s_label=0, s_grid=0, s_bau=2.2, s_nze=0),
    "Konservatif": dict(s_label=50, s_grid=5, s_bau=2.2, s_nze=50),
    "Sesuai target DLH": dict(s_label=100, s_grid=10, s_bau=2.2, s_nze=100),
    "Ambisius": dict(s_label=150, s_grid=30, s_bau=2.2, s_nze=150),
}
for _k, _v in PRESET["Sesuai target DLH"].items():
    st.session_state.setdefault(_k, _v)
st.session_state.setdefault("s_preset", "Sesuai target DLH")


def _pakai_preset():
    p = st.session_state["s_preset"]
    if p in PRESET:
        for k, v in PRESET[p].items():
            st.session_state[k] = v


def _ke_manual():
    st.session_state["s_preset"] = "Atur sendiri"


with tab4:
    st.subheader("Simulasi: seberapa jauh program mitigasi menurunkan emisi?")
    st.markdown("**1. Pilih skenario**")
    st.radio("Skenario cepat", list(PRESET) + ["Atur sendiri"], key="s_preset", horizontal=True,
             on_change=_pakai_preset, label_visibility="collapsed")

    cagr_1924 = ((c24 / c19) ** (1 / 5) - 1) * 100
    cagr_1024 = ((c24 / c10) ** (1 / 14) - 1) * 100
    p1, p2, p3, p4 = st.columns(4)
    with p1:
        capai_label = st.slider("Labelling efisiensi (% target DLH)", 0, 150, step=10, key="s_label", on_change=_ke_manual,
                                help="Program labelling AC, lampu, dan lemari es. 100% = target DLH tercapai penuh. Memengaruhi 2025–2030.")
    with p2:
        cut_grid = st.slider("Listrik lebih bersih pada 2030 (%)", 0, 40, step=5, key="s_grid", on_change=_ke_manual,
                             help="Penurunan faktor emisi listrik jaringan Jawa-Madura-Bali pada 2030. Memengaruhi 2025–2030.")
    with p3:
        laju_bau = st.slider("Pertumbuhan baseline (% per tahun)", 0.5, 4.0, step=0.1, key="s_bau", on_change=_ke_manual,
                             help=f"Laju historis: {fmt_id(cagr_1924, 1)}% per tahun (2019–2024), {fmt_id(cagr_1024, 1)}% per tahun (2010–2024).")
    with p4:
        capai_nze = st.slider("Realisasi target NZE (%)", 0, 150, step=10, key="s_nze", on_change=_ke_manual,
                              help="0% = hanya mengikuti CPOS, 100% = mencapai NZE, di atas 100% = melampaui NZE. Memengaruhi 2035–2050.")
    st.caption("Tiga pengaturan pertama memengaruhi hasil **2025–2030**, yang keempat memengaruhi **2035–2050**. "
               f"Sebagai pembanding, emisi aktual tumbuh {fmt_id(cagr_1924, 1)}% per tahun pada 2019–2024.")

    # ---- Jangka pendek 2024 -> 2030 (tanpa hitung ganda labelling dan grid)
    tahun_pendek = [2024, 2025, 2026, 2027, 2028, 2029, 2030]
    target_label = [0, 2442, 2610, 2814, 3054, 3329, TARGET_LABELLING_2030]
    bau, skenario = [c24], [c24]
    for idx in range(1, len(tahun_pendek)):
        bau_t = c24 * (1 + laju_bau / 100) ** idx
        red_label = target_label[idx] * capai_label / 100
        sisa_listrik = max(0.0, bau_t * porsi_listrik - red_label)
        red_grid = sisa_listrik * (cut_grid / 100) * (idx / 6)
        bau.append(bau_t)
        skenario.append(max(0.0, bau_t - red_label - red_grid))
    reduksi_2030 = bau[-1] - skenario[-1]
    persen_2030 = reduksi_2030 / bau[-1] * 100
    red_label_2030 = min(target_label[-1] * capai_label / 100, reduksi_2030)
    red_grid_2030 = max(0.0, reduksi_2030 - red_label_2030)

    # ---- Jangka panjang: acuan DLH
    tahun_dlh = [2019, 2035, 2040, 2045, 2050]
    cpos = [13953.0, 14356.0, 12760.0, 12023.0, 11237.0]
    nze = [13953.0, 14211.0, 11158.0, 9616.0, 5604.0]
    tahun_panjang = tahun_dlh[1:]
    sim_panjang = [max(0.0, cpos[i] - (cpos[i] - nze[i]) * capai_nze / 100) for i in range(1, len(tahun_dlh))]
    emisi_2050 = sim_panjang[-1]
    selisih_nze = emisi_2050 - nze[-1]

    st.markdown("**2. Lihat hasilnya**")
    r1, r2, r3 = st.columns(3)
    r1.markdown(kpi("Emisi 2030 dengan skenario ini", f"{fmt_id(skenario[-1])} Gg", f"{fmt_id(persen_2030, 1)}% lebih rendah dari baseline ({fmt_id(bau[-1])})", WARNA["simulasi"], "📉", "baik" if persen_2030 > 0 else ""), unsafe_allow_html=True)
    r2.markdown(kpi("Penurunan emisi 2030", f"{fmt_id(reduksi_2030)} Gg", f"dibanding baseline tanpa program", WARNA["turun"], "🌱"), unsafe_allow_html=True)
    r3.markdown(kpi("Emisi 2050 dengan skenario ini", f"{fmt_id(emisi_2050)} Gg",
                    "target NZE tercapai" if selisih_nze <= 0.5 else f"masih {fmt_id(selisih_nze)} Gg di atas target NZE",
                    WARNA["nze"], "🏁", "baik" if selisih_nze <= 0.5 else "buruk"), unsafe_allow_html=True)

    tot_r = max(reduksi_2030, 1e-9)
    w_l = red_label_2030 / tot_r * 100
    st.markdown(
        f"**Dari mana penurunan 2030 berasal?**"
        f'<div class="split"><div style="width:{w_l:.1f}%;background:{WARNA["listrik"]}"></div>'
        f'<div style="width:{100 - w_l:.1f}%;background:{WARNA["turun"]}"></div></div>'
        f'<div class="legenda"><span><i style="background:{WARNA["listrik"]}"></i>Program labelling: <b>{fmt_id(red_label_2030)} Gg</b></span>'
        f'<span><i style="background:{WARNA["turun"]}"></i>Listrik lebih bersih: <b>{fmt_id(red_grid_2030)} Gg</b></span></div>',
        unsafe_allow_html=True,
    )

    g1, g2 = st.columns(2, gap="large")
    hist = df[df["Tahun"] >= 2019]
    with g1:
        st.markdown("**Jangka pendek 2024–2030**")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=hist["Tahun"], y=hist["C_Total_Gg"], name="Aktual", mode="lines+markers",
                                 line=dict(color=WARNA["aktual"], width=2.5)))
        fig.add_trace(go.Scatter(x=tahun_pendek, y=bau, name="Tanpa program (baseline)", mode="lines",
                                 line=dict(color=WARNA["bau"], width=2, dash="dash")))
        fig.add_trace(go.Scatter(x=tahun_pendek, y=skenario, name="Dengan skenario ini", mode="lines+markers",
                                 line=dict(color=WARNA["simulasi"], width=3), fill="tonexty", fillcolor="rgba(29,78,137,0.14)"))
        fig = tata_letak(fig, "Gg CO₂e", 360)
        fig.update_xaxes(dtick=1)
        fig.add_annotation(x=2030, y=(bau[-1] + skenario[-1]) / 2, text=f"−{fmt_id(reduksi_2030)}", showarrow=False,
                           xanchor="left", xshift=8, font=dict(color=WARNA["simulasi"], size=12))
        tampil(fig)
        st.caption("Area biru = emisi yang berhasil dihindari dibanding tanpa program.")
    with g2:
        st.markdown("**Jangka panjang 2035–2050**")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=hist["Tahun"], y=hist["C_Total_Gg"], name="Aktual", mode="lines+markers",
                                 line=dict(color=WARNA["aktual"], width=2.5)))
        for nama, ys, w, dash in [("Acuan CPOS (DLH)", cpos, WARNA["cpos"], "dot"), ("Acuan NZE (DLH)", nze, WARNA["nze"], "dot")]:
            fig.add_trace(go.Scatter(x=tahun_dlh, y=ys, name=nama, mode="lines+markers+text", line=dict(color=w, width=2, dash=dash),
                                     text=[""] * (len(ys) - 1) + [fmt_id(ys[-1])], textposition="middle right"))
        fig.add_trace(go.Scatter(x=tahun_panjang, y=sim_panjang, name="Skenario ini", mode="lines+markers+text",
                                 line=dict(color=WARNA["simulasi"], width=3),
                                 text=[""] * (len(sim_panjang) - 1) + [fmt_id(sim_panjang[-1])], textposition="middle right"))
        fig = tata_letak(fig, "Gg CO₂e", 360)
        fig.update_xaxes(range=[2018, 2056])
        tampil(fig)
        st.caption("Garis putus-putus adalah angka acuan DLH dengan basis inventarisnya sendiri, sehingga tidak menyambung langsung dengan garis aktual.")

    tambah = "" if capai_label > 0 or cut_grid > 0 else " (tanpa program tambahan, emisi hanya mengikuti baseline)"
    kotak(
        "Kesimpulan skenario ini",
        "<ul>"
        f"<li><b>2030:</b> dengan labelling {fmt_id(capai_label)}% dari target dan listrik {fmt_id(cut_grid)}% lebih bersih, emisi diproyeksikan "
        f"<b>{fmt_id(skenario[-1])} Gg CO₂e</b>, atau {fmt_id(persen_2030, 1)}% lebih rendah dari baseline{tambah}.</li>"
        f"<li><b>2050:</b> dengan realisasi NZE {fmt_id(capai_nze)}%, emisi berada di <b>{fmt_id(emisi_2050)} Gg CO₂e</b>"
        f"{', yaitu target NZE DLH tercapai.' if selisih_nze <= 0.5 else f', masih {fmt_id(selisih_nze)} Gg di atas target NZE DLH ({fmt_id(nze[-1])} Gg).'}</li>"
        "</ul>",
    )
    st.caption("Sumber target: Tabel 3, 4, dan 5 Laporan Akhir DLH DKI Jakarta 2026. Penurunan faktor emisi listrik tidak ditambahkan pada 2035–2050 "
               "karena target NZE DLH sudah memuat dekarbonisasi pembangkit.")
