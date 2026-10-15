import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

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
    .block-container { padding-top: 2.2rem; padding-bottom: 3rem; max-width: 1200px; }
    .stApp, .stApp p, .stApp li, .stApp label, .stApp td, .stApp th,
    .stApp h1, .stApp h2, .stApp h3, .stApp h4 {
        font-family: -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    h1 { font-weight: 700 !important; letter-spacing: -0.02em; font-size: 2rem !important; padding-bottom: 0.2rem; }
    h2, h3 { font-weight: 600 !important; letter-spacing: -0.01em; }
    h3 { font-size: 1.15rem !important; margin-top: 0.6rem; }
    .subjudul { opacity: 0.7; font-size: 1.02rem; margin: -0.3rem 0 1.4rem 0; }
    [data-testid="stMetric"] {
        background: rgba(128,128,128,0.06); border: 1px solid rgba(128,128,128,0.2);
        border-radius: 12px; padding: 14px 16px;
    }
    [data-testid="stMetricLabel"] p { font-size: 0.82rem; opacity: 0.75; }
    [data-testid="stMetricValue"] { font-size: 1.55rem; font-weight: 700; }
    button[data-baseweb="tab"] p { font-weight: 500; font-size: 0.98rem; }
    .kotak {
        border-left: 4px solid #1D4E89; background: rgba(29,78,137,0.07);
        padding: 14px 18px; border-radius: 0 10px 10px 0; margin: 6px 0 18px 0;
    }
    .kotak.peringatan { border-left-color: #D08C2D; background: rgba(208,140,45,0.09); }
    .kotak-judul { font-weight: 600; margin-bottom: 6px; }
    .kotak ul { margin: 0; padding-left: 1.1rem; }
    .kotak li { margin-bottom: 5px; }
    #MainMenu, footer { visibility: hidden; }
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
    st.markdown(
        f'<div class="{kelas}"><div class="kotak-judul">{judul}</div>{isi_html}</div>',
        unsafe_allow_html=True,
    )


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


def tabel_efek(baris):
    """Tabel efek dalam format Indonesia untuk ditampilkan."""
    d = pd.DataFrame(baris)
    out = pd.DataFrame({"Periode": d["Periode"]})
    out["Total perubahan"] = d[KEY_TOTAL].map(lambda v: fmt_tanda(v, 1))
    for k in EFEK_KEYS:
        out[NAMA[k]] = d[k].map(lambda v: fmt_tanda(v, 1))
    out["Selisih hitung"] = d["Residual"].map(lambda v: fmt_id(0.0 if abs(v) < 0.005 else v, 2))
    return out


# ==========================================================
# 4. HEADER & KPI
# ==========================================================
r10 = df[df["Tahun"] == 2010].iloc[0]
r19 = df[df["Tahun"] == 2019].iloc[0]
r24 = df[df["Tahun"] == 2024].iloc[0]
c10, c19, c24 = r10["C_Total_Gg"], r19["C_Total_Gg"], r24["C_Total_Gg"]
porsi_listrik = r24["C_Listrik"] / c24
tumbuh_total = (c24 / c10 - 1) * 100
kapita10 = c10 / r10["Penduduk_Juta"] / 1000   # tCO2e per penduduk (Gg per juta jiwa / 1000)
kapita24 = c24 / r24["Penduduk_Juta"] / 1000
TARGET_LABELLING_2030 = 3630.0

st.title("Emisi Gas Rumah Kaca Rumah Tangga DKI Jakarta")
st.markdown(
    '<div class="subjudul">Apa yang mendorong perubahan emisi 2010–2024, dan seberapa jauh program mitigasi dapat menurunkannya hingga 2050.</div>',
    unsafe_allow_html=True,
)

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total emisi 2024", f"{fmt_id(c24)} Gg CO₂e", f"{fmt_tanda(tumbuh_total, 1)}% dibanding 2010", delta_color="inverse")
k2.metric("Emisi per penduduk 2024", f"{fmt_id(kapita24, 2)} tCO₂e", f"{fmt_tanda((kapita24 / kapita10 - 1) * 100, 1)}% dibanding 2010", delta_color="inverse")
k3.metric("Porsi emisi dari listrik 2024", f"{fmt_id(porsi_listrik * 100, 1)}%", f"{fmt_id(r24['C_Listrik'])} Gg CO₂e", delta_color="off")
k4.metric("Target reduksi labelling 2030 (DLH)", f"{fmt_id(TARGET_LABELLING_2030)} Gg CO₂e", f"{fmt_id(TARGET_LABELLING_2030 / c24 * 100, 1)}% dari emisi 2024", delta_color="off")

st.write("")
tab0, tab1, tab2, tab3, tab4 = st.tabs(
    ["Ringkasan", "Data Historis", "Faktor Pendorong", "Uji Kepekaan", "Simulasi Mitigasi"]
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
        f"Pendorong kenaikan terbesar adalah <b>{NAMA[k_naik].lower()}</b> ({fmt_tanda(efek_all[k_naik])} Gg CO₂e).",
    ]
    if efek_all[k_turun] < 0:
        poin.append(f"Faktor yang menahan kenaikan adalah <b>{NAMA[k_turun].lower()}</b> ({fmt_tanda(efek_all[k_turun])} Gg CO₂e).")
    poin.append(
        f"Sekitar <b>{fmt_id(porsi_listrik * 100, 1)}%</b> emisi rumah tangga berasal dari listrik, sehingga efisiensi peralatan listrik dan dekarbonisasi pembangkit menjadi tuas utama penurunan emisi."
    )
    kotak("Temuan utama", "<ul>" + "".join(f"<li>{p}</li>" for p in poin) + "</ul>")

    st.markdown("### Cara membaca dashboard ini")
    c_a, c_b = st.columns(2)
    with c_a:
        st.markdown(
            "**1. Data Historis** menampilkan emisi dan energi rumah tangga tiap tahun.  \n"
            "**2. Faktor Pendorong** menguraikan perubahan emisi menjadi lima penyebab (metode LMDI).  \n"
            "**3. Uji Kepekaan** memeriksa apakah kesimpulan berubah jika data atau metode diganti."
        )
    with c_b:
        st.markdown(
            "**4. Simulasi Mitigasi** memungkinkan Anda mengubah asumsi kebijakan dan melihat dampaknya pada emisi 2030 dan 2050.  \n"
            "Satuan emisi: **Gg CO₂e** (1 Gg = 1.000 ton CO₂ ekuivalen)."
        )

    with st.expander("Arti istilah yang dipakai"):
        st.markdown(
            """
| Istilah | Arti sederhana |
|---|---|
| **Pertumbuhan penduduk** | Emisi bertambah karena jumlah penduduk bertambah |
| **Kemakmuran** | Emisi bertambah karena ekonomi per orang tumbuh (konsumsi lebih banyak) |
| **Intensitas energi** | Energi yang dipakai untuk setiap rupiah PDRB. Turun berarti lebih efisien, sehingga menahan emisi |
| **Bauran bahan bakar** | Perubahan porsi listrik, LPG, dan gas bumi |
| **Faktor emisi listrik** | Emisi yang dihasilkan per satuan listrik. Turun jika pembangkit makin bersih |
| **BaU (Baseline)** | Lintasan emisi jika tidak ada program mitigasi tambahan |
| **CPOS** | Skenario kebijakan yang sudah berjalan (acuan DLH) |
| **NZE** | Skenario nol emisi bersih 2050 (acuan DLH) |
| **TJ (Terajoule)** | Satuan energi, dipakai untuk konsumsi energi final |
"""
        )

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
        d_ = 3 if "EF listrik" in kolom else 2 if ("Penduduk" in kolom or "PDRB" in kolom) else 1
        tabel_tampil[kolom] = tabel_raw[kolom].map(lambda v, d_=d_: fmt_id(v, d_))
    tabel_tampil["Tahun"] = tabel_raw["Tahun"].astype(str)
    st.dataframe(tabel_tampil, hide_index=True, width="stretch")
    st.download_button("Unduh tabel (CSV)", tabel_raw.to_csv(index=False).encode("utf-8"),
                       "deret_data_rt_dki_2010_2024.csv", "text/csv")

    yoy = df["PDRB_Konstan_T"].pct_change() * 100
    with st.expander("Catatan kualitas data dan perlakuannya"):
        catatan = pd.DataFrame([
            {"Item": "PDRB harga konstan 2011",
             "Temuan": f"Naik {fmt_tanda(yoy.iloc[1], 1)}% (2011) lalu {fmt_tanda(yoy.iloc[2], 1)}% (2012), sedangkan tahun normal naik 4–6%.",
             "Perlakuan di dashboard": "Dipakai apa adanya sesuai tabel DLH. Pengaruhnya diuji pada Uji Kepekaan (skenario B3). Perlu dicek ke sumber."},
            {"Item": "Penduduk 2019 dan 2020",
             "Temuan": f"Nilainya sama ({fmt_id(r19['Penduduk_Juta'], 2)} juta), sehingga efek penduduk periode 2019–2020 bernilai 0.",
             "Perlakuan di dashboard": "Dipakai sesuai tabel DLH. Perlu dicek ke sumber."},
            {"Item": "Emisi gas bumi 2010",
             "Temuan": "Tertulis 0 di tabel (pembulatan), padahal LMDI memakai logaritma.",
             "Perlakuan di dashboard": "Diganti nilai positif sangat kecil. Opsi 0,4 Gg tersedia di Pengaturan data (sidebar). Selisih hasil kurang dari 2 Gg."},
            {"Item": "Total emisi 2019: inventaris vs acuan DLH",
             "Temuan": f"Data inventaris {fmt_id(c19)} Gg, sedangkan titik awal skenario CPOS/NZE DLH 13.953 Gg (selisih {fmt_id(13953 - c19)} Gg).",
             "Perlakuan di dashboard": "Keduanya ditampilkan terpisah dan diberi label pada grafik jangka panjang."},
        ])
        st.dataframe(catatan, hide_index=True, width="stretch")

# ==========================================================
# TAB 2: FAKTOR PENDORONG
# ==========================================================
with tab2:
    st.subheader("Apa yang mendorong perubahan emisi?")
    kotak(
        "Cara membaca",
        "Batang <b style='color:#C8553D'>merah</b> adalah faktor yang <b>menaikkan</b> emisi, batang "
        "<b style='color:#2A9D8F'>hijau</b> adalah faktor yang <b>menurunkan</b> emisi. "
        "Batang biru tua di ujung adalah total perubahan emisi pada periode yang dipilih.",
    )

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
    nilai = [hasil[k] for k in EFEK_KEYS] + [hasil[KEY_TOTAL]]
    label = [NAMA[k].replace(" (", "<br>(") for k in EFEK_KEYS] + ["Total<br>perubahan"]
    fig = go.Figure(go.Waterfall(
        orientation="v", measure=["relative"] * 5 + ["total"], x=label, y=nilai,
        text=[fmt_tanda(v) for v in nilai], textposition="outside", cliponaxis=False,
        connector={"line": {"color": "#CBD2D9", "width": 1}},
        increasing={"marker": {"color": WARNA["naik"]}},
        decreasing={"marker": {"color": WARNA["turun"]}},
        totals={"marker": {"color": WARNA["total"]}},
        hovertemplate="%{y:,.1f} Gg CO₂e<extra></extra>",
    ))
    st.markdown(f"**Perubahan emisi {t_awal}–{t_akhir} (Gg CO₂e)**")
    fig = tata_letak(fig, tinggi=420)
    fig.update_layout(hovermode="closest", margin=dict(l=10, r=10, t=30, b=10))
    tampil(fig)

    st.markdown("**Perubahan emisi per tahun (2010–2024)**")
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
    st.caption(
        "Catatan: data PDRB konstan 2011 tampak tidak wajar (lihat Data Historis → Catatan kualitas data), "
        "sehingga batang 2010–2011 dan 2011–2012 perlu dibaca hati-hati. Pengaruhnya diuji pada Uji Kepekaan (B3)."
    )

    st.markdown("**Ringkasan per periode (Gg CO₂e)**")
    ringkasan = [hitung_lmdi(df, a, b, jenis_pdrb) for a, b in
                 [(2010, 2019), (2019, 2020), (2020, 2024), (2019, 2024), (2010, 2024)]]
    st.dataframe(tabel_efek(ringkasan), hide_index=True, width="stretch")
    st.caption("Periode: sebelum pandemi (2010–2019), tahun pandemi (2019–2020), sesudah pandemi (2020–2024), dan total. "
               "\"Selisih hitung\" harus 0: artinya kelima faktor menjumlah tepat ke total perubahan.")
    st.download_button("Unduh ringkasan (CSV)", pd.DataFrame(ringkasan).to_csv(index=False).encode("utf-8"),
                       "tabel_lmdi_multiperiode.csv", "text/csv")

# ==========================================================
# TAB 3: UJI KEPEKAAN
# ==========================================================
with tab3:
    st.subheader("Apakah kesimpulan berubah jika asumsi diganti?")
    kotak(
        "Cara membaca",
        "Setiap baris adalah satu variasi perhitungan. Bandingkan <b>baris yang metodenya sama</b>: "
        "<b>A1 vs A2</b> (efek memakai PDRB harga konstan atau berlaku), <b>B1 vs B2</b> (efek tahun pandemi), "
        "dan <b>B1 vs B3</b> (efek data PDRB 2011 yang tidak wajar).",
    )

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
    d_sens = pd.DataFrame(sk)
    tampil_sens = pd.DataFrame({"Skenario": d_sens["Skenario"]})
    tampil_sens["Total perubahan"] = d_sens[KEY_TOTAL].map(lambda v: fmt_tanda(v, 1))
    for k in EFEK_KEYS:
        tampil_sens[NAMA[k]] = d_sens[k].map(lambda v: fmt_tanda(v, 1))
    tampil_sens["Selisih hitung"] = d_sens["Residual"].map(lambda v: fmt_id(0.0 if abs(v) < 0.005 else v, 2))
    st.dataframe(tampil_sens, hide_index=True, width="stretch")
    st.caption("Satuan: Gg CO₂e. Skenario A dan B tidak dibandingkan langsung karena dekomposisi langsung dan berantai memang membagi efek secara berbeda. "
               "B3 mengganti PDRB 2011 dengan rata-rata geometrik 2010 dan 2012 (estimasi untuk pengujian, bukan data resmi).")

    kI, kA = "Efek Intensitas Energi (ΔC_int)", "Efek Kemakmuran (ΔC_aff)"
    arah_pandemi = "lebih kuat" if sk[3][kI] < sk[2][kI] else "lebih lemah"
    kotak(
        "Temuan (angka dihitung otomatis dari tabel)",
        "<ul>"
        f"<li><b>Basis PDRB (A1 vs A2):</b> pada harga berlaku, efek kemakmuran berubah dari {fmt_tanda(sk[0][kA], 1)} menjadi {fmt_tanda(sk[1][kA], 1)} "
        f"dan efek intensitas energi dari {fmt_tanda(sk[0][kI], 1)} menjadi {fmt_tanda(sk[1][kI], 1)} Gg CO₂e. "
        "Pembesaran ini konsisten dengan masuknya inflasi harga pada PDRB berlaku, sehingga harga konstan lebih sesuai sebagai basis utama.</li>"
        f"<li><b>Pandemi (B1 vs B2):</b> bila transisi 2019–2020 dikeluarkan, efek intensitas energi menjadi {arah_pandemi} "
        f"({fmt_tanda(sk[2][kI], 1)} → {fmt_tanda(sk[3][kI], 1)} Gg CO₂e). Dugaan penyebabnya: pada 2020 konsumsi listrik rumah tangga naik saat PDRB turun "
        "(kemungkinan efek kerja dari rumah). Ini masih dugaan dan perlu didukung data atau rujukan.</li>"
        f"<li><b>Data PDRB 2011 (B1 vs B3):</b> efek kemakmuran berubah dari {fmt_tanda(sk[2][kA], 1)} menjadi {fmt_tanda(sk[4][kA], 1)} "
        f"dan efek intensitas energi dari {fmt_tanda(sk[2][kI], 1)} menjadi {fmt_tanda(sk[4][kI], 1)} Gg CO₂e. "
        "Total perubahan tidak berubah.</li>"
        "</ul>",
    )

# ==========================================================
# TAB 4: SIMULASI MITIGASI
# ==========================================================
with tab4:
    st.subheader("Simulasi skenario mitigasi")
    kotak(
        "Cara menggunakan",
        "Geser pengaturan di sebelah kiri. Grafik dan angka hasil di sebelah kanan akan berubah otomatis. "
        "Bagian <b>jangka pendek (2024–2030)</b> dihitung dari emisi aktual 2024, sedangkan "
        "<b>jangka panjang (2035–2050)</b> memakai angka acuan skenario CPOS dan NZE dari DLH.",
    )

    cagr_1924 = ((c24 / c19) ** (1 / 5) - 1) * 100
    cagr_1024 = ((c24 / c10) ** (1 / 14) - 1) * 100

    col_s1, col_s2 = st.columns([1, 2.3], gap="large")
    with col_s1:
        st.markdown("**Pengaturan jangka pendek (2025–2030)**")
        capai_label = st.slider("Pencapaian program labelling efisiensi (% target DLH)", 0, 150, 100, step=10,
                                help="Labelling untuk AC, lampu, dan lemari es. 100% berarti target DLH tercapai penuh.")
        cut_grid = st.slider("Penurunan faktor emisi listrik pada 2030 (%)", 0, 40, 10, step=5,
                             help="Seberapa lebih bersih listrik jaringan Jawa-Madura-Bali pada 2030. Hanya memengaruhi hasil 2025–2030.")
        laju_bau = st.slider("Pertumbuhan emisi baseline (% per tahun)", 0.5, 4.0, 2.2, step=0.1)
        st.caption(f"Laju historis emisi rumah tangga: {fmt_id(cagr_1924, 1)}% per tahun (2019–2024) dan {fmt_id(cagr_1024, 1)}% per tahun (2010–2024).")
        st.markdown("**Pengaturan jangka panjang (2035–2050)**")
        capai_nze = st.slider("Realisasi target NZE (% dari selisih CPOS ke NZE)", 0, 150, 100, step=10,
                              help="0% berarti hanya mengikuti CPOS, 100% berarti mencapai NZE, di atas 100% berarti melampaui NZE.")

    # ---- Jangka pendek: 2024 -> 2030 (tanpa hitung ganda labelling & grid)
    tahun_pendek = [2024, 2025, 2026, 2027, 2028, 2029, 2030]
    target_label = [0, 2442, 2610, 2814, 3054, 3329, TARGET_LABELLING_2030]   # Tabel 3 Laporan DLH
    bau, skenario = [c24], [c24]
    for idx in range(1, len(tahun_pendek)):
        bau_t = c24 * (1 + laju_bau / 100) ** idx
        red_label = target_label[idx] * capai_label / 100
        sisa_listrik = max(0.0, bau_t * porsi_listrik - red_label)    # emisi listrik yang belum dihemat labelling
        red_grid = sisa_listrik * (cut_grid / 100) * (idx / 6)        # penurunan EF grid bertahap sampai 2030
        bau.append(bau_t)
        skenario.append(max(0.0, bau_t - red_label - red_grid))
    reduksi_2030 = bau[-1] - skenario[-1]
    persen_2030 = reduksi_2030 / bau[-1] * 100

    # ---- Jangka panjang: acuan DLH
    tahun_dlh = [2019, 2035, 2040, 2045, 2050]
    cpos = [13953.0, 14356.0, 12760.0, 12023.0, 11237.0]
    nze = [13953.0, 14211.0, 11158.0, 9616.0, 5604.0]
    tahun_panjang = tahun_dlh[1:]
    sim_panjang = [max(0.0, cpos[i] - (cpos[i] - nze[i]) * capai_nze / 100) for i in range(1, len(tahun_dlh))]
    emisi_2050 = sim_panjang[-1]
    selisih_nze = emisi_2050 - nze[-1]

    with col_s2:
        m1, m2, m3 = st.columns(3)
        m1.metric("Reduksi emisi 2030", f"{fmt_id(reduksi_2030)} Gg CO₂e", f"{fmt_id(persen_2030, 1)}% di bawah baseline", delta_color="off")
        m2.metric("Emisi 2030 (skenario)", f"{fmt_id(skenario[-1])} Gg CO₂e", f"baseline {fmt_id(bau[-1])}", delta_color="off")
        m3.metric("Emisi 2050 (simulasi)", f"{fmt_id(emisi_2050)} Gg CO₂e",
                  "target NZE tercapai" if selisih_nze <= 0.5 else f"{fmt_id(selisih_nze)} di atas NZE", delta_color="off")

        st.markdown("**Jangka pendek 2024–2030 (Gg CO₂e)**")
        hist = df[df["Tahun"] >= 2019]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=hist["Tahun"], y=hist["C_Total_Gg"], name="Aktual", mode="lines+markers",
                                 line=dict(color=WARNA["aktual"], width=2.5)))
        fig.add_trace(go.Scatter(x=tahun_pendek, y=bau, name="Baseline (BaU)", mode="lines+markers",
                                 line=dict(color=WARNA["bau"], width=2, dash="dash")))
        fig.add_trace(go.Scatter(x=tahun_pendek, y=skenario, name="Skenario simulasi", mode="lines+markers",
                                 line=dict(color=WARNA["simulasi"], width=3)))
        fig = tata_letak(fig, None, 340)
        fig.update_xaxes(dtick=1)
        tampil(fig)

        st.markdown("**Jangka panjang 2035–2050 menurut acuan DLH (Gg CO₂e)**")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=hist["Tahun"], y=hist["C_Total_Gg"], name="Aktual (inventaris)", mode="lines+markers",
                                 line=dict(color=WARNA["aktual"], width=2.5)))
        fig.add_trace(go.Scatter(x=tahun_dlh, y=cpos, name="CPOS (DLH)", mode="lines+markers",
                                 line=dict(color=WARNA["cpos"], width=2, dash="dot")))
        fig.add_trace(go.Scatter(x=tahun_dlh, y=nze, name="NZE (DLH)", mode="lines+markers",
                                 line=dict(color=WARNA["nze"], width=2, dash="dot")))
        fig.add_trace(go.Scatter(x=tahun_panjang, y=sim_panjang, name="Simulasi Anda", mode="lines+markers",
                                 line=dict(color=WARNA["simulasi"], width=3)))
        tampil(tata_letak(fig, None, 340))
        st.caption(
            f"Acuan DLH memakai basis inventarisnya sendiri (2019 = {fmt_id(13953)} Gg, sedangkan data inventaris 2019 = {fmt_id(c19)} Gg). "
            f"Emisi aktual 2024 ({fmt_id(c24)} Gg) sudah di atas angka CPOS 2035 ({fmt_id(cpos[1])} Gg), sehingga acuan DLH dan data aktual "
            "tidak menyambung langsung. Gunakan grafik ini untuk membandingkan arah dan besarnya ambisi, bukan sebagai kelanjutan garis aktual."
        )

    st.caption("Sumber target: Tabel 3, 4, dan 5 Laporan Akhir DLH DKI Jakarta 2026. Penurunan faktor emisi listrik tidak ditambahkan pada 2035–2050 "
               "karena target NZE DLH sudah memuat dekarbonisasi pembangkit.")
