import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import html
import re

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
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    :root { --garis: rgba(128,128,128,0.22); }
    .block-container { padding-top: 1.6rem; padding-bottom: 3rem; max-width: 1200px; }
    .stApp, .stApp p, .stApp li, .stApp label, .stApp td, .stApp th,
    .stApp h1, .stApp h2, .stApp h3, .stApp h4 {
        font-family: "Plus Jakarta Sans", -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    h2, h3 { font-weight: 700 !important; letter-spacing: -0.01em; }
    h3 { font-size: 1.15rem !important; margin-top: 0.6rem; }
    #MainMenu, footer { visibility: hidden; }

    /* Tab */
    div[data-baseweb="tab-list"] { gap: 4px; }
    button[data-baseweb="tab"] { padding: 10px 16px; }
    button[data-baseweb="tab"] p { font-weight: 600; font-size: 0.97rem; }

    /* Hero */
    .hero { position: relative; overflow: hidden; border-radius: 22px; padding: 34px 38px 32px; margin: 0 0 18px 0; color: #fff;
        background: linear-gradient(115deg, #0B3335 0%, #14566B 48%, #1D4E89 100%); }
    .hero::before { content: ""; position: absolute; inset: 0;
        background: radial-gradient(700px 260px at 88% 0%, rgba(107,196,170,0.38), transparent 65%),
                    radial-gradient(520px 220px at 0% 115%, rgba(224,164,88,0.24), transparent 70%); }
    .hero > * { position: relative; }
    .hero svg { position: absolute; right: 0; bottom: 0; height: 80%; max-height: 240px; width: auto; pointer-events: none; }
    .hero-chips { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 16px; }
    .hero-chip { background: rgba(255,255,255,0.14); border: 1px solid rgba(255,255,255,0.26); padding: 4px 12px;
        border-radius: 999px; font-size: 0.78rem; font-weight: 500; }
    .hero-judul { font-size: clamp(1.7rem, 3.4vw, 2.6rem); font-weight: 800; letter-spacing: -0.025em; line-height: 1.12; max-width: 720px; }
    .hero-sub { margin-top: 12px; max-width: 600px; font-size: 1.02rem; line-height: 1.55; opacity: 0.9; }
    @media (max-width: 700px) { .hero { padding: 24px 22px; } .hero svg { opacity: 0.35; } }

    /* Kartu angka */
    .kpi-grid { display: grid; gap: 12px; margin: 6px 0 10px 0; }
    .kpi { border: 1px solid var(--garis); border-top: 4px solid var(--aksen, #1D4E89); border-radius: 14px;
        padding: 13px 16px 14px; background: rgba(128,128,128,0.05); }
    .kpi-label { font-size: 0.8rem; opacity: 0.78; margin-bottom: 4px; }
    .kpi-nilai { font-size: 1.55rem; font-weight: 800; letter-spacing: -0.02em; line-height: 1.15; }
    .kpi-satuan { font-size: 0.8rem; font-weight: 500; opacity: 0.7; margin-left: 5px; letter-spacing: 0; }
    .kpi-delta { display: inline-block; margin-top: 8px; font-size: 0.76rem; font-weight: 600; padding: 2px 9px;
        border-radius: 999px; background: rgba(128,128,128,0.14); }
    .kpi-delta.naik { background: rgba(200,85,61,0.15); color: #C8553D; }
    .kpi-delta.turun { background: rgba(42,157,143,0.17); color: #2A9D8F; }
    @media (max-width: 900px) { .kpi-grid { grid-template-columns: repeat(2, 1fr) !important; } }
    @media (max-width: 520px) { .kpi-grid { grid-template-columns: 1fr !important; } }

    /* Kotak info */
    .kotak { border-left: 4px solid #1D4E89; background: rgba(29,78,137,0.07); padding: 14px 18px;
        border-radius: 0 12px 12px 0; margin: 6px 0 18px 0; line-height: 1.55; }
    .kotak.peringatan { border-left-color: #D08C2D; background: rgba(208,140,45,0.09); }
    .kotak-judul { font-weight: 700; margin-bottom: 6px; }
    .kotak ul { margin: 0; padding-left: 1.1rem; }
    .kotak li { margin-bottom: 5px; }

    /* Panduan membaca */
    .panduan { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
    .panduan-kartu { border: 1px solid var(--garis); border-radius: 14px; padding: 16px; background: rgba(128,128,128,0.04); }
    .panduan-ikon { width: 42px; height: 42px; border-radius: 12px; display: flex; align-items: center; justify-content: center;
        font-size: 1.25rem; margin-bottom: 12px; background: color-mix(in srgb, var(--aksen) 18%, transparent); }
    .panduan-judul { font-weight: 700; }
    .panduan-tanya { font-size: 0.86rem; font-weight: 600; color: var(--aksen); margin: 2px 0 6px; }
    .panduan-isi { font-size: 0.86rem; line-height: 1.5; opacity: 0.85; }
    .legenda { display: flex; flex-wrap: wrap; gap: 8px 22px; margin: 16px 0 8px; font-size: 0.86rem; }
    .legenda-item i { display: inline-block; width: 12px; height: 12px; border-radius: 4px; margin-right: 7px; vertical-align: -1px; }
    .istilah-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
    .istilah { border: 1px solid var(--garis); border-radius: 12px; padding: 10px 13px; font-size: 0.86rem; line-height: 1.45; }
    .istilah b { display: block; margin-bottom: 2px; }
    @media (max-width: 1000px) { .panduan { grid-template-columns: repeat(2, 1fr); } .istilah-grid { grid-template-columns: repeat(2, 1fr); } }
    @media (max-width: 560px) { .panduan, .istilah-grid { grid-template-columns: 1fr; } }

    /* Tabel tanpa gulir */
    .tbl-wrap { border: 1px solid var(--garis); border-radius: 12px; overflow-x: auto; margin: 6px 0 12px 0; }
    table.tbl { width: 100%; border-collapse: collapse; font-size: 0.8rem; }
    .tbl th { background: rgba(29,78,137,0.12); font-weight: 700; padding: 9px 9px; line-height: 1.25; vertical-align: bottom; text-align: right; }
    .tbl td { padding: 7px 9px; border-top: 1px solid rgba(128,128,128,0.15); vertical-align: top; line-height: 1.4; }
    .tbl tbody tr:nth-child(even) td { background: rgba(128,128,128,0.045); }
    .tbl th.t, .tbl td.t { text-align: left; }
    .tbl td.n { text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }
    .tbl .pos { color: #C8553D; font-weight: 600; }
    .tbl .neg { color: #2A9D8F; font-weight: 600; }

    /* Hasil simulasi & uji kepekaan */
    .hasil-utama { border-radius: 16px; padding: 16px 20px; margin: 0 0 12px 0; font-size: 1.02rem; line-height: 1.6;
        background: linear-gradient(120deg, rgba(42,157,143,0.15), rgba(29,78,137,0.12)); border: 1px solid rgba(42,157,143,0.32); }
    .vonis { border: 1px solid var(--garis); border-radius: 14px; padding: 16px 18px; background: rgba(128,128,128,0.05); }
    .vonis-judul { font-weight: 700; margin: 10px 0 6px; }
    .vonis-isi { font-size: 0.9rem; line-height: 1.6; opacity: 0.92; }
    .lencana { display: inline-block; padding: 3px 11px; border-radius: 999px; font-size: 0.78rem; font-weight: 700; }
    .lencana.ok { background: rgba(42,157,143,0.18); color: #2A9D8F; }
    .lencana.waspada { background: rgba(208,140,45,0.2); color: #D08C2D; }
    .kontrib { display: flex; height: 14px; border-radius: 999px; overflow: hidden; margin: 10px 0 8px; background: rgba(128,128,128,0.18); }
    .kontrib-ket { display: flex; flex-wrap: wrap; gap: 6px 20px; font-size: 0.86rem; }
    .kontrib-ket i { display: inline-block; width: 11px; height: 11px; border-radius: 4px; margin-right: 6px; }
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



def blok(s):
    """Tampilkan HTML tanpa baris kosong agar tidak dipecah parser Markdown."""
    st.markdown(re.sub(r"\n\s*", "", s.strip()), unsafe_allow_html=True)


def kpi_grid(items, kolom=4):
    """items: (ikon, label, nilai, satuan, delta, kelas_delta, warna_aksen)"""
    kartu = ""
    for ikon, label, nilai, satuan, delta, kls, aksen in items:
        kartu += (
            f'<div class="kpi" style="--aksen:{aksen}"><div class="kpi-label">{ikon} {label}</div>'
            f'<div class="kpi-nilai">{nilai}<span class="kpi-satuan">{satuan}</span></div>'
            + (f'<span class="kpi-delta {kls}">{delta}</span>' if delta else "")
            + "</div>"
        )
    blok(f'<div class="kpi-grid" style="grid-template-columns:repeat({kolom},1fr)">{kartu}</div>')


def tabel_html(d, teks=1, tanda=False):
    """Tabel HTML yang menyesuaikan lebar layar, tanpa gulir. teks = jumlah kolom awal yang rata kiri."""
    kepala = "".join(
        f'<th class="{"t" if i < teks else "n"}">{html.escape(str(c))}</th>' for i, c in enumerate(d.columns)
    )
    baris = ""
    for _, r in d.iterrows():
        sel = ""
        for i, v in enumerate(r.tolist()):
            s = html.escape(str(v))
            if tanda and i >= teks:
                if s.startswith("+"):
                    s = f'<span class="pos">{s}</span>'
                elif s.startswith("−"):
                    s = f'<span class="neg">{s}</span>'
            sel += f'<td class="{"t" if i < teks else "n"}">{s}</td>'
        baris += f"<tr>{sel}</tr>"
    blok(f'<div class="tbl-wrap"><table class="tbl"><thead><tr>{kepala}</tr></thead><tbody>{baris}</tbody></table></div>')


def rentang_x(vals, lebar=1.3):
    """Rentang sumbu-x yang menyisakan ruang untuk label di ujung batang."""
    lo, hi = min(0.0, min(vals)), max(0.0, max(vals))
    kiri = lo * lebar if lo < 0 else -0.04 * hi
    kanan = hi * lebar if hi > 0 else -0.04 * lo
    return [kiri, kanan]


def hasil_utama(isi):
    blok(f'<div class="hasil-utama">{isi}</div>')


def hero():
    blok(
        """
        <div class="hero">
        <svg viewBox="0 0 520 220" preserveAspectRatio="xMaxYMax meet" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
        <g fill="#ffffff" fill-opacity="0.10"><rect x="10" y="120" width="38" height="100"/><rect x="54" y="88" width="32" height="132"/><rect x="92" y="136" width="46" height="84"/><rect x="146" y="64" width="36" height="156"/><rect x="188" y="110" width="42" height="110"/></g>
        <g fill="#ffffff" fill-opacity="0.18"><rect x="238" y="96" width="38" height="124"/><rect x="282" y="140" width="44" height="80"/><rect x="332" y="150" width="30" height="70"/></g>
        <g fill="#ffffff" fill-opacity="0.32"><rect x="372" y="196" width="104" height="24"/><rect x="388" y="180" width="72" height="16"/><polygon points="418,180 434,180 430,70 422,70"/><rect x="414" y="64" width="24" height="8"/></g>
        <ellipse cx="426" cy="50" rx="7" ry="13" fill="#E0A458"/>
        <g fill="#ffffff" fill-opacity="0.14"><rect x="486" y="128" width="30" height="92"/></g>
        </svg>
        <div class="hero-chips"><span class="hero-chip">🌿 Data 2010–2024</span><span class="hero-chip">Metode LMDI-I</span><span class="hero-chip">Sumber: DLH DKI Jakarta 2026</span><span class="hero-chip">Simulasi sampai 2050</span></div>
        <div class="hero-judul">Emisi Gas Rumah Kaca Rumah Tangga DKI Jakarta</div>
        <div class="hero-sub">Apa yang mendorong perubahan emisi 2010–2024, dan seberapa jauh program mitigasi dapat menurunkannya hingga 2050.</div>
        </div>
        """
    )

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

hero()

kpi_grid([
    ("🏭", "Total emisi 2024", fmt_id(c24), "Gg CO₂e", f"{fmt_tanda(tumbuh_total, 1)}% dibanding 2010",
     "naik" if tumbuh_total > 0 else "turun", "#C8553D"),
    ("👤", "Emisi per penduduk 2024", fmt_id(kapita24, 2), "tCO₂e", f"{fmt_tanda((kapita24 / kapita10 - 1) * 100, 1)}% dibanding 2010",
     "naik" if kapita24 > kapita10 else "turun", "#E0A458"),
    ("⚡", "Porsi emisi dari listrik 2024", f"{fmt_id(porsi_listrik * 100, 1)}%", "", f"{fmt_id(r24['C_Listrik'])} Gg CO₂e", "", "#2F5D8A"),
    ("🎯", "Target reduksi labelling 2030 (DLH)", fmt_id(TARGET_LABELLING_2030), "Gg CO₂e",
     f"{fmt_id(TARGET_LABELLING_2030 / c24 * 100, 1)}% dari emisi 2024", "", "#2A9D8F"),
])

st.write("")
tab0, tab1, tab2, tab3, tab4 = st.tabs(
    ["🏠 Ringkasan", "📊 Data Historis", "🧭 Faktor Pendorong", "🔬 Uji Kepekaan", "🎚️ Simulasi Mitigasi"]
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
    blok(
        """
        <div class="panduan">
        <div class="panduan-kartu" style="--aksen:#2F5D8A"><div class="panduan-ikon">📊</div><div class="panduan-judul">Data Historis</div><div class="panduan-tanya">Berapa emisinya?</div><div class="panduan-isi">Emisi dan energi rumah tangga tiap tahun, lengkap dengan tabel dan unduhan CSV.</div></div>
        <div class="panduan-kartu" style="--aksen:#C8553D"><div class="panduan-ikon">🧭</div><div class="panduan-judul">Faktor Pendorong</div><div class="panduan-tanya">Apa penyebab naik-turunnya?</div><div class="panduan-isi">Perubahan emisi diurai menjadi lima penyebab dengan metode LMDI.</div></div>
        <div class="panduan-kartu" style="--aksen:#D08C2D"><div class="panduan-ikon">🔬</div><div class="panduan-judul">Uji Kepekaan</div><div class="panduan-tanya">Apakah kesimpulannya kokoh?</div><div class="panduan-isi">Memeriksa apakah hasil berubah jika data atau metode diganti.</div></div>
        <div class="panduan-kartu" style="--aksen:#2A9D8F"><div class="panduan-ikon">🎚️</div><div class="panduan-judul">Simulasi Mitigasi</div><div class="panduan-tanya">Bagaimana jika kebijakan diubah?</div><div class="panduan-isi">Ubah asumsi kebijakan dan lihat dampaknya pada emisi 2030 dan 2050.</div></div>
        </div>
        <div class="legenda">
        <span class="legenda-item"><i style="background:#C8553D"></i>Merah: menaikkan emisi</span>
        <span class="legenda-item"><i style="background:#2A9D8F"></i>Hijau: menurunkan emisi</span>
        <span class="legenda-item">📐 Satuan emisi <b>Gg CO₂e</b> (1 Gg = 1.000 ton CO₂ ekuivalen)</span>
        </div>
        """
    )

    ISTILAH = [
        ("Pertumbuhan penduduk", "Emisi bertambah karena jumlah penduduk bertambah."),
        ("Kemakmuran", "Emisi bertambah karena ekonomi per orang tumbuh (konsumsi lebih banyak)."),
        ("Intensitas energi", "Energi yang dipakai untuk setiap rupiah PDRB. Turun berarti lebih efisien, sehingga menahan emisi."),
        ("Bauran bahan bakar", "Perubahan porsi listrik, LPG, dan gas bumi."),
        ("Faktor emisi listrik", "Emisi per satuan listrik. Turun jika pembangkit makin bersih."),
        ("BaU (baseline)", "Lintasan emisi jika tidak ada program mitigasi tambahan."),
        ("CPOS", "Skenario kebijakan yang sudah berjalan (acuan DLH)."),
        ("NZE", "Skenario nol emisi bersih 2050 (acuan DLH)."),
        ("TJ (terajoule)", "Satuan energi untuk konsumsi energi final."),
    ]
    with st.expander("Arti istilah yang dipakai"):
        blok('<div class="istilah-grid">' + "".join(f'<div class="istilah"><b>{t}</b>{d}</div>' for t, d in ISTILAH) + "</div>")

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
    tabel_html(tabel_tampil)
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
        tabel_html(catatan, teks=3)

# ==========================================================
# TAB 2: FAKTOR PENDORONG
# ==========================================================
with tab2:
    st.subheader("Apa yang mendorong perubahan emisi?")
    kotak(
        "Cara membaca",
        "Pilih rentang tahun, lalu lihat batang di bawah. Setiap batang adalah satu penyebab. "
        "Batang <b style='color:#C8553D'>merah ke kanan</b> berarti penyebab itu <b>menaikkan</b> emisi, "
        "batang <b style='color:#2A9D8F'>hijau ke kiri</b> berarti <b>menurunkan</b> emisi. "
        "Semakin panjang batang, semakin besar pengaruhnya.",
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
    e_awal = df.loc[df["Tahun"] == t_awal, "C_Total_Gg"].iloc[0]
    e_akhir = df.loc[df["Tahun"] == t_akhir, "C_Total_Gg"].iloc[0]
    d_tot = hasil[KEY_TOTAL]
    kpi_grid([
        ("🏁", f"Emisi {t_awal}", fmt_id(e_awal), "Gg CO₂e", "titik awal", "", WARNA["aktual"]),
        ("🎯", f"Emisi {t_akhir}", fmt_id(e_akhir), "Gg CO₂e", "titik akhir", "", WARNA["simulasi"]),
        ("📈" if d_tot > 0 else "📉", "Perubahan total", fmt_tanda(d_tot), "Gg CO₂e",
         f"{fmt_tanda(d_tot / e_awal * 100, 1)}% dari emisi {t_awal}", "naik" if d_tot > 0 else "turun",
         WARNA["naik"] if d_tot > 0 else WARNA["turun"]),
    ], kolom=3)

    st.markdown(f"**Seberapa besar tiap penyebab mengubah emisi, {t_awal}–{t_akhir} (Gg CO₂e)**")
    urut = sorted(EFEK_KEYS, key=lambda k: hasil[k])          # terbesar di atas
    nilai = [hasil[k] for k in urut]
    fig = go.Figure(go.Bar(
        y=[NAMA[k] for k in urut], x=nilai, orientation="h",
        marker_color=[WARNA["naik"] if v > 0 else WARNA["turun"] for v in nilai],
        text=[fmt_tanda(v) for v in nilai], textposition="outside", cliponaxis=False,
        hovertemplate="%{y}<br><b>%{x:,.1f} Gg CO₂e</b><extra></extra>",
    ))
    fig = tata_letak(fig, None, 360)
    fig.update_layout(hovermode="closest", showlegend=False, bargap=0.35, margin=dict(l=10, r=30, t=44, b=10))
    fig.update_xaxes(range=rentang_x(nilai), showgrid=True, gridcolor="#E8ECEF", zeroline=True,
                     zerolinecolor="#6B7280", zerolinewidth=1.5, title="Gg CO₂e")
    fig.update_yaxes(showgrid=False, automargin=True)
    fig.add_annotation(xref="paper", yref="paper", x=0, y=1.1, text="◀ menurunkan emisi", showarrow=False,
                       xanchor="left", font=dict(color=WARNA["turun"], size=12))
    fig.add_annotation(xref="paper", yref="paper", x=1, y=1.1, text="menaikkan emisi ▶", showarrow=False,
                       xanchor="right", font=dict(color=WARNA["naik"], size=12))
    tampil(fig)

    k_max = max(EFEK_KEYS, key=lambda k: hasil[k])
    k_min = min(EFEK_KEYS, key=lambda k: hasil[k])
    poin_efek = ""
    if hasil[k_max] > 0:
        poin_efek += f"<li>Penyebab kenaikan terbesar: <b>{NAMA[k_max].lower()}</b> ({fmt_tanda(hasil[k_max], 1)} Gg CO₂e).</li>"
    if hasil[k_min] < 0:
        poin_efek += f"<li>Penahan kenaikan terbesar: <b>{NAMA[k_min].lower()}</b> ({fmt_tanda(hasil[k_min], 1)} Gg CO₂e).</li>"
    poin_efek += f"<li>Kelima batang dijumlahkan sama dengan perubahan total emisi: <b>{fmt_tanda(d_tot, 1)} Gg CO₂e</b>.</li>"
    kotak("Cara membaca hasil di atas", f"<ul>{poin_efek}</ul>")
    st.caption("Arti tiap penyebab ada di tab Ringkasan, bagian “Arti istilah yang dipakai”.")

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
    tabel_html(tabel_efek(ringkasan), tanda=True)
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
        "Uji kepekaan mengulang perhitungan dengan data atau metode yang sedikit berbeda, lalu menaruh hasilnya berdampingan. "
        "Jika dua batang hampir sama dan arahnya tetap, kesimpulan <b>kokoh</b>. "
        "Jika ada penyebab yang bergeser jauh atau berbalik arah, hasilnya perlu dibaca lebih hati-hati.",
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

    kI, kA = "Efek Intensitas Energi (ΔC_int)", "Efek Kemakmuran (ΔC_aff)"
    arah_pandemi = "lebih kuat" if sk[3][kI] < sk[2][kI] else "lebih lemah"
    SINGKAT = dict(zip(EFEK_KEYS, ["Penduduk", "Kemakmuran", "Intensitas energi", "Bauran bahan bakar", "Faktor emisi listrik"]))

    def f1(v):
        return fmt_tanda(v, 1)

    uji = [
        dict(ikon="💰", pendek="Basis PDRB", kode="A1 vs A2", a=sk[0], b=sk[1],
             judul="Apakah memakai PDRB harga konstan atau harga berlaku berpengaruh?",
             na="Harga konstan (A1)", nb="Harga berlaku (A2)",
             teks=f"Pada harga berlaku, efek kemakmuran berubah dari {f1(sk[0][kA])} menjadi {f1(sk[1][kA])} "
                  f"dan efek intensitas energi dari {f1(sk[0][kI])} menjadi {f1(sk[1][kI])} Gg CO₂e. "
                  "Perubahan ini konsisten dengan masuknya inflasi harga pada PDRB berlaku, sehingga harga konstan lebih sesuai sebagai basis utama."),
        dict(ikon="🦠", pendek="Tahun pandemi", kode="B1 vs B2", a=sk[2], b=sk[3],
             judul="Apakah tahun pandemi 2019–2020 memengaruhi hasil?",
             na="Semua tahun (B1)", nb="Tanpa 2019–2020 (B2)",
             teks=f"Bila transisi 2019–2020 dikeluarkan, efek intensitas energi menjadi {arah_pandemi} ({f1(sk[2][kI])} → {f1(sk[3][kI])} Gg CO₂e). "
                  "Dugaan penyebabnya: pada 2020 konsumsi listrik rumah tangga naik saat PDRB turun (kemungkinan efek kerja dari rumah). "
                  "Ini masih dugaan dan perlu didukung data atau rujukan."),
        dict(ikon="📉", pendek="PDRB 2011", kode="B1 vs B3", a=sk[2], b=sk[4],
             judul="Apakah angka PDRB 2011 yang tampak janggal memengaruhi hasil?",
             na="Data asli (B1)", nb="PDRB 2011 diinterpolasi (B3)",
             teks=f"Efek kemakmuran berubah dari {f1(sk[2][kA])} menjadi {f1(sk[4][kA])} "
                  f"dan efek intensitas energi dari {f1(sk[2][kI])} menjadi {f1(sk[4][kI])} Gg CO₂e. Total perubahan tidak berubah."),
    ]

    def bandingkan(a, b):
        selisih = {k: b[k] - a[k] for k in EFEK_KEYS}
        k_geser = max(selisih, key=lambda k: abs(selisih[k]))
        berbalik = [k for k in EFEK_KEYS if a[k] * b[k] < 0 and max(abs(a[k]), abs(b[k])) >= 5]   # abaikan selisih < 5 Gg
        return selisih, k_geser, berbalik

    def grafik_banding(u):
        fig = go.Figure()
        for data, nama, warna in [(u["a"], u["na"], WARNA["bau"]), (u["b"], u["nb"], WARNA["simulasi"])]:
            fig.add_trace(go.Bar(
                y=[NAMA[k] for k in EFEK_KEYS], x=[data[k] for k in EFEK_KEYS], name=nama, orientation="h",
                marker_color=warna, text=[f1(data[k]) for k in EFEK_KEYS], textposition="outside", cliponaxis=False,
                hovertemplate="%{y}<br><b>%{x:,.1f} Gg CO₂e</b><extra>" + nama + "</extra>"))
        semua = [d[k] for d in (u["a"], u["b"]) for k in EFEK_KEYS]
        fig = tata_letak(fig, None, 380)
        fig.update_layout(barmode="group", hovermode="closest", bargap=0.3, bargroupgap=0.06,
                          margin=dict(l=10, r=30, t=44, b=10))
        fig.update_xaxes(range=rentang_x(semua, 1.35), showgrid=True, gridcolor="#E8ECEF", zeroline=True,
                         zerolinecolor="#6B7280", zerolinewidth=1.5, title="Gg CO₂e")
        fig.update_yaxes(autorange="reversed", showgrid=False, automargin=True)
        return fig

    hasil_uji = [bandingkan(u["a"], u["b"]) for u in uji]

    # ---- Ringkasan cepat
    kartu = []
    for u, (selisih, k_geser, berbalik) in zip(uji, hasil_uji):
        kartu.append((u["ikon"], f"{u['kode']} · {u['pendek']}", "Arah tetap" if not berbalik else "Ada yang berbalik", "",
                      f"Pergeseran terbesar: {SINGKAT[k_geser].lower()} {f1(selisih[k_geser])}", "",
                      WARNA["turun"] if not berbalik else "#D08C2D"))
    kpi_grid(kartu, kolom=3)

    # ---- Rincian tiap uji
    for u, (selisih, k_geser, berbalik) in zip(uji, hasil_uji):
        st.markdown(f"### {u['ikon']} {u['judul']}")
        c1, c2 = st.columns([3, 2], gap="large")
        with c1:
            tampil(grafik_banding(u))
        with c2:
            if berbalik:
                lencana = '<span class="lencana waspada">Ada penyebab yang berbalik arah</span>'
                judul_v = "Berbalik: " + ", ".join(SINGKAT[k].lower() for k in berbalik)
            else:
                lencana = '<span class="lencana ok">Arah semua penyebab tetap</span>'
                judul_v = "Kesimpulan relatif kokoh"
            blok(
                f'<div class="vonis">{lencana}<div class="vonis-judul">{judul_v}</div>'
                f'<div class="vonis-isi">{u["teks"]}<br><br><b>Pergeseran terbesar:</b> {SINGKAT[k_geser].lower()} '
                f'({f1(selisih[k_geser])} Gg CO₂e).</div></div>'
            )

    st.caption("Satuan: Gg CO₂e. Skenario A dan B tidak dibandingkan langsung karena dekomposisi langsung dan berantai memang membagi efek secara berbeda. "
               "B3 mengganti PDRB 2011 dengan rata-rata geometrik 2010 dan 2012 (estimasi untuk pengujian, bukan data resmi). "
               "Perubahan arah di bawah 5 Gg CO₂e dianggap tidak berarti.")

    with st.expander("Lihat tabel angka lengkap"):
        tampil_sens = pd.DataFrame({"Skenario": d_sens["Skenario"]})
        tampil_sens["Total perubahan"] = d_sens[KEY_TOTAL].map(lambda v: fmt_tanda(v, 1))
        for k in EFEK_KEYS:
            tampil_sens[NAMA[k]] = d_sens[k].map(lambda v: fmt_tanda(v, 1))
        tampil_sens["Selisih hitung"] = d_sens["Residual"].map(lambda v: fmt_id(0.0 if abs(v) < 0.005 else v, 2))
        tabel_html(tampil_sens, tanda=True)

# ==========================================================
# TAB 4: SIMULASI MITIGASI
# ==========================================================
with tab4:
    st.subheader("Simulasi skenario mitigasi")
    kotak(
        "Cara menggunakan",
        "Pilih <b>skenario cepat</b> untuk melihat contoh, atau atur sendiri dengan penggeser. Hasil berubah otomatis. "
        "Tab <b>Sampai 2030</b> dihitung dari emisi aktual 2024. Tab <b>Sampai 2050</b> memakai angka acuan skenario CPOS dan NZE dari DLH.",
    )

    PRESET = {
        "Konservatif": dict(sl_label=50, sl_grid=5, sl_laju=3.0, sl_nze=0),
        "Sesuai target DLH": dict(sl_label=100, sl_grid=10, sl_laju=2.2, sl_nze=100),
        "Ambisius": dict(sl_label=130, sl_grid=30, sl_laju=1.5, sl_nze=120),
    }
    DESKRIPSI = {
        "Konservatif": "Program berjalan separuh jalan dan emisi baseline tumbuh lebih cepat. Target 2050 hanya mengikuti CPOS.",
        "Sesuai target DLH": "Target labelling DLH tercapai penuh dan skenario NZE terealisasi 100%.",
        "Ambisius": "Melampaui target DLH, listrik jauh lebih bersih, dan pertumbuhan baseline lebih lambat.",
        "Kustom": "Atur sendiri lewat penggeser di tiap tab.",
    }
    if "preset" not in st.session_state:
        st.session_state.update(PRESET["Sesuai target DLH"])
        st.session_state["preset"] = "Sesuai target DLH"

    def _pakai_preset():
        p = PRESET.get(st.session_state["preset"])
        if p:
            st.session_state.update(p)

    def _kustom():
        st.session_state["preset"] = "Kustom"

    st.radio("Skenario cepat", ["Konservatif", "Sesuai target DLH", "Ambisius", "Kustom"], key="preset",
             horizontal=True, on_change=_pakai_preset)
    st.caption(DESKRIPSI[st.session_state["preset"]])

    sub1, sub2 = st.tabs(["Sampai 2030 (dari emisi aktual)", "Sampai 2050 (acuan DLH)"])

    cagr_1924 = ((c24 / c19) ** (1 / 5) - 1) * 100
    cagr_1024 = ((c24 / c10) ** (1 / 14) - 1) * 100

    # ------------------------------------------------------
    # Jangka pendek: 2024 -> 2030 (tanpa hitung ganda labelling & grid)
    # ------------------------------------------------------
    with sub1:
        col_s1, col_s2 = st.columns([1, 2.2], gap="large")
        with col_s1:
            with st.container(border=True):
                st.markdown("**Atur asumsi 2025–2030**")
                capai_label = st.slider("Pencapaian program labelling efisiensi (% target DLH)", 0, 150, step=10,
                                        key="sl_label", on_change=_kustom,
                                        help="Labelling untuk AC, lampu, dan lemari es. 100% berarti target DLH tercapai penuh.")
                cut_grid = st.slider("Penurunan faktor emisi listrik pada 2030 (%)", 0, 40, step=5,
                                     key="sl_grid", on_change=_kustom,
                                     help="Seberapa lebih bersih listrik jaringan Jawa-Madura-Bali pada 2030. Hanya memengaruhi hasil 2025–2030.")
                laju_bau = st.slider("Pertumbuhan emisi baseline (% per tahun)", 0.5, 4.0, step=0.1,
                                     key="sl_laju", on_change=_kustom,
                                     help="Seberapa cepat emisi naik jika tidak ada program mitigasi tambahan.")
                st.caption(f"Laju historis emisi rumah tangga: {fmt_id(cagr_1924, 1)}% per tahun (2019–2024) "
                           f"dan {fmt_id(cagr_1024, 1)}% per tahun (2010–2024).")

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
        red_label_2030, red_grid_2030 = red_label, red_grid
        reduksi_2030 = bau[-1] - skenario[-1]
        persen_2030 = reduksi_2030 / bau[-1] * 100
        vs_2024 = (skenario[-1] / c24 - 1) * 100

        with col_s2:
            posisi = (f"{fmt_id(abs(vs_2024), 1)}% di bawah emisi 2024" if vs_2024 < 0
                      else f"masih {fmt_id(vs_2024, 1)}% di atas emisi 2024")
            hasil_utama(
                f"Dengan pengaturan ini, emisi rumah tangga Jakarta pada 2030 diperkirakan <b>{fmt_id(skenario[-1])} Gg CO₂e</b>. "
                f"Itu <b>{fmt_id(persen_2030, 1)}%</b> ({fmt_id(reduksi_2030)} Gg) lebih rendah dari baseline {fmt_id(bau[-1])} Gg, dan {posisi}."
            )
            kpi_grid([
                ("📉", "Reduksi emisi 2030", fmt_id(reduksi_2030), "Gg CO₂e", f"{fmt_id(persen_2030, 1)}% di bawah baseline", "turun", WARNA["turun"]),
                ("🏙️", "Emisi 2030 (skenario)", fmt_id(skenario[-1]), "Gg CO₂e", f"baseline {fmt_id(bau[-1])}", "", WARNA["simulasi"]),
                ("📅", "Dibanding emisi 2024", f"{fmt_tanda(vs_2024, 1)}%", "", f"2024: {fmt_id(c24)} Gg CO₂e",
                 "naik" if vs_2024 > 0 else "turun", "#E0A458"),
            ], kolom=3)

            st.markdown("**Lintasan emisi 2024–2030 (Gg CO₂e)**")
            hist = df[df["Tahun"] >= 2019]
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=hist["Tahun"], y=hist["C_Total_Gg"], name="Aktual", mode="lines+markers",
                                     line=dict(color=WARNA["aktual"], width=2.5)))
            fig.add_trace(go.Scatter(x=tahun_pendek, y=bau, name="Baseline (tanpa program)", mode="lines+markers",
                                     line=dict(color=WARNA["bau"], width=2, dash="dash")))
            fig.add_trace(go.Scatter(x=tahun_pendek, y=skenario, name="Skenario Anda", mode="lines+markers",
                                     line=dict(color=WARNA["simulasi"], width=3), fill="tonexty",
                                     fillcolor="rgba(42,157,143,0.20)"))
            if reduksi_2030 > 0.5:
                fig.add_annotation(x=2030, y=(bau[-1] + skenario[-1]) / 2, text=f"−{fmt_id(reduksi_2030)}<br>Gg CO₂e",
                                   showarrow=False, xanchor="left", xshift=10, font=dict(color=WARNA["turun"], size=12))
            fig = tata_letak(fig, None, 360)
            fig.update_xaxes(dtick=1, range=[2018.6, 2031.4])
            tampil(fig)
            st.caption("Area hijau adalah emisi yang berhasil dihindari dibanding baseline.")

            total_red = red_label_2030 + red_grid_2030
            if reduksi_2030 > 0.5 and total_red > 0:
                p_l = red_label_2030 / total_red * 100
                p_g = 100 - p_l
                blok(
                    f'<div class="vonis"><div class="vonis-judul" style="margin-top:0">Dari mana penurunan 2030 berasal?</div>'
                    f'<div class="kontrib"><span style="width:{p_l:.1f}%;background:#2F5D8A"></span>'
                    f'<span style="width:{p_g:.1f}%;background:#6BA292"></span></div>'
                    f'<div class="kontrib-ket"><span><i style="background:#2F5D8A"></i>Program labelling: <b>{fmt_id(red_label_2030)}</b> Gg ({fmt_id(p_l)}%)</span>'
                    f'<span><i style="background:#6BA292"></i>Listrik lebih bersih: <b>{fmt_id(red_grid_2030)}</b> Gg ({fmt_id(p_g)}%)</span></div></div>'
                )
            else:
                st.info("Belum ada penurunan. Naikkan pencapaian labelling atau penurunan faktor emisi listrik di panel kiri.")

    # ------------------------------------------------------
    # Jangka panjang: acuan DLH
    # ------------------------------------------------------
    with sub2:
        tahun_dlh = [2019, 2035, 2040, 2045, 2050]
        cpos = [13953.0, 14356.0, 12760.0, 12023.0, 11237.0]
        nze = [13953.0, 14211.0, 11158.0, 9616.0, 5604.0]

        cl1, cl2 = st.columns([1, 2.2], gap="large")
        with cl1:
            with st.container(border=True):
                st.markdown("**Atur asumsi 2035–2050**")
                capai_nze = st.slider("Realisasi target NZE (% dari selisih CPOS ke NZE)", 0, 150, step=10,
                                      key="sl_nze", on_change=_kustom,
                                      help="0% berarti hanya mengikuti CPOS, 100% berarti mencapai NZE, di atas 100% berarti melampaui NZE.")
                st.caption("0% = hanya CPOS · 100% = capai NZE · di atas 100% = melampaui NZE")

        tahun_panjang = tahun_dlh[1:]
        sim_panjang = [max(0.0, cpos[i] - (cpos[i] - nze[i]) * capai_nze / 100) for i in range(1, len(tahun_dlh))]
        emisi_2050 = sim_panjang[-1]
        selisih_nze = emisi_2050 - nze[-1]
        pct_2050 = (emisi_2050 / cpos[0] - 1) * 100

        with cl2:
            hasil_utama(
                f"Jika <b>{capai_nze}%</b> selisih CPOS–NZE terealisasi, emisi rumah tangga Jakarta pada 2050 diperkirakan "
                f"<b>{fmt_id(emisi_2050)} Gg CO₂e</b>, atau <b>{fmt_id(abs(pct_2050), 1)}%</b> "
                f"{'lebih rendah' if pct_2050 < 0 else 'lebih tinggi'} dari titik awal 2019 menurut basis DLH."
            )
            kpi_grid([
                ("🌍", "Emisi 2050 (simulasi)", fmt_id(emisi_2050), "Gg CO₂e",
                 "target NZE tercapai" if selisih_nze <= 0.5 else f"{fmt_id(selisih_nze)} di atas NZE",
                 "turun" if selisih_nze <= 0.5 else "naik", WARNA["simulasi"]),
                ("📉", "Perubahan dari 2019 (basis DLH)", f"{fmt_tanda(pct_2050, 1)}%", "", f"2019: {fmt_id(cpos[0])} Gg CO₂e",
                 "turun" if pct_2050 < 0 else "naik", WARNA["nze"]),
                ("🧭", "Posisi antara CPOS dan NZE", f"{capai_nze}%", "", "0% = CPOS, 100% = NZE", "", WARNA["cpos"]),
            ], kolom=3)

            st.markdown("**Lintasan 2019–2050 menurut acuan DLH (Gg CO₂e)**")
            sim_line = [cpos[0]] + sim_panjang
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=tahun_dlh, y=nze, name="NZE (DLH)", mode="lines+markers+text",
                                     line=dict(color=WARNA["nze"], width=2, dash="dot"),
                                     text=[None] * 4 + [f"NZE {fmt_id(nze[-1])}"], textposition="middle right",
                                     textfont=dict(color=WARNA["nze"])))
            fig.add_trace(go.Scatter(x=tahun_dlh, y=cpos, name="CPOS (DLH)", mode="lines+markers+text",
                                     line=dict(color=WARNA["cpos"], width=2, dash="dot"),
                                     fill="tonexty", fillcolor="rgba(224,164,88,0.14)",
                                     text=[None] * 4 + [f"CPOS {fmt_id(cpos[-1])}"], textposition="middle right",
                                     textfont=dict(color=WARNA["cpos"])))
            fig.add_trace(go.Scatter(x=tahun_dlh, y=sim_line, name="Simulasi Anda", mode="lines+markers+text",
                                     line=dict(color=WARNA["simulasi"], width=3),
                                     text=[None] * 4 + [f"Anda {fmt_id(emisi_2050)}"], textposition="middle right",
                                     textfont=dict(color=WARNA["simulasi"])))
            fig = tata_letak(fig, None, 380)
            fig.update_xaxes(range=[2017.5, 2057], tickvals=tahun_dlh)
            tampil(fig)
            st.caption(
                "Area kuning adalah rentang antara CPOS dan NZE. "
                f"Angka acuan DLH memakai basis inventarisnya sendiri (2019 = {fmt_id(cpos[0])} Gg, sedangkan data inventaris 2019 = {fmt_id(c19)} Gg). "
                f"Emisi aktual 2024 ({fmt_id(c24)} Gg) sudah di atas CPOS 2035 ({fmt_id(cpos[1])} Gg), sehingga grafik ini dipakai untuk "
                "membandingkan arah dan besarnya ambisi, bukan sebagai kelanjutan garis aktual."
            )

    st.caption("Sumber target: Tabel 3, 4, dan 5 Laporan Akhir DLH DKI Jakarta 2026. Penurunan faktor emisi listrik tidak ditambahkan pada 2035–2050 "
               "karena target NZE DLH sudah memuat dekarbonisasi pembangkit.")
