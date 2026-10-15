import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="Simulator Dekarbonisasi & LMDI DKI Jakarta", layout="wide")

# ==========================================
# 1. DATABASE INTERNAL (100% DARI PDF DLH 2026)
# ==========================================
data_historis = {
    "Tahun": list(range(2010, 2025)),
    "Penduduk_Juta": [9.64, 9.89, 9.86, 9.97, 10.08, 10.18, 10.28, 10.37, 10.47, 10.56, 10.56, 10.61, 10.68, 10.67, 10.68],
    "PDRB_Konstan_T": [1080.00, 1260.00, 1222.53, 1296.69, 1373.39, 1454.56, 1539.92, 1635.36, 1735.21, 1836.24, 1792.29, 1856.00, 1953.49, 2050.47, 2151.04],
    "PDRB_Berlaku_T": [1075, 1224, 1369, 1547, 1762, 1989, 2159, 2365, 2593, 2816, 2767, 2913, 3189, 3443, 3679],
    "EF_Listrik_MWh": [0.830, 0.880, 0.927, 0.967, 0.949, 1.023, 0.990, 0.897, 0.894, 0.906, 0.902, 0.896, 0.901, 0.903, 0.903],
    "C_Listrik": [7560.0, 8400.0, 9590.0, 11100.0, 10500.0, 11700.0, 12500.0, 11300.0, 11800.0, 12600.0, 13100.0, 13100.0, 13300.0, 14100.0, 14828.0],
    "C_LPG": [982.0, 1044.0, 1082.0, 1076.0, 1076.0, 1393.0, 1366.0, 1444.0, 1447.0, 1266.0, 1289.0, 1300.0, 1318.0, 1338.0, 1348.0],
    "C_Gas": [0.4, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 7.0, 7.0, 7.0, 4.0] # 2010 dibuat 0.4 Gg (pembulatan 0 di tabel) agar logaritma terdefinisi
}

df = pd.DataFrame(data_historis)

# Konversi Faktor Emisi ke Gg CO2e / TJ (1 GWh = 3.6 TJ)
# EF Listrik (Gg/TJ) = EF_Listrik_MWh / 3.6
df["EF_Listrik_TJ"] = df["EF_Listrik_MWh"] / 3.6
df["EF_LPG_TJ"] = 0.06537   # Tabel 3.5: 65.370 kg CO2/TJ = 0.06537 Gg/TJ
df["EF_Gas_TJ"] = 0.05764   # Tabel 3.5: 57.640 kg CO2/TJ = 0.05764 Gg/TJ

# Turunkan Konsumsi Energi Final (TJ) dari Emisi / Faktor Emisi (Prosedur No. 2)
df["E_Listrik_TJ"] = df["C_Listrik"] / df["EF_Listrik_TJ"]
df["E_LPG_TJ"] = df["C_LPG"] / df["EF_LPG_TJ"]
df["E_Gas_TJ"] = df["C_Gas"] / df["EF_Gas_TJ"]

df["E_Total_TJ"] = df["E_Listrik_TJ"] + df["E_LPG_TJ"] + df["E_Gas_TJ"]
df["C_Total_Gg"] = df["C_Listrik"] + df["C_LPG"] + df["C_Gas"]

# ==========================================
# 2. FUNGSI PERHITUNGAN LMDI ADITIF (ANG 2005, 2015)
# ==========================================
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
    
    g0, gt = Y0 / P0, Yt / Pt   # Kemakmuran (Y/P)
    I0, It = E0 / Y0, Et / Yt   # Intensitas Energi (E/Y)
    
    fuels = [("Listrik", "C_Listrik", "E_Listrik_TJ", "EF_Listrik_TJ"),
             ("LPG", "C_LPG", "E_LPG_TJ", "EF_LPG_TJ"),
             ("Gas", "C_Gas", "E_Gas_TJ", "EF_Gas_TJ")]
    
    dC_pop, dC_aff, dC_int, dC_mix, dC_ef = 0.0, 0.0, 0.0, 0.0, 0.0
    
    for nama, col_c, col_e, col_ef in fuels:
        c0, ct = r0[col_c], rt[col_c]
        e0, et = r0[col_e], rt[col_e]
        ef0, eft = r0[col_ef], rt[col_ef]
        s0, st = e0 / E0, et / Et
        
        L = log_mean(ct, c0)
        dC_pop += L * np.log(Pt / P0)
        dC_aff += L * np.log(gt / g0)
        dC_int += L * np.log(It / I0)
        dC_mix += L * np.log(st / s0)
        dC_ef  += L * np.log(eft / ef0)
        
    dC_total = rt["C_Total_Gg"] - r0["C_Total_Gg"]
    return {
        "Periode": f"{thn_awal}–{thn_akhir}",
        "Perubahan Total (ΔC)": round(dC_total, 2),
        "Efek Penduduk (ΔC_pop)": round(dC_pop, 2),
        "Efek Kemakmuran (ΔC_aff)": round(dC_aff, 2),
        "Efek Intensitas Energi (ΔC_int)": round(dC_int, 2),
        "Efek Bauran Energi (ΔC_mix)": round(dC_mix, 2),
        "Efek Faktor Emisi (ΔC_ef)": round(dC_ef, 2),
        "Residual": round(dC_total - (dC_pop + dC_aff + dC_int + dC_mix + dC_ef), 4)
    }

# ==========================================
# 3. ANTARMUKA DASHBOARD & KALKULATOR CAPSTONE
# ==========================================
st.title("📊 Dashboard Dekomposisi LMDI & Simulator Mitigasi GRK DKI Jakarta")
st.markdown("**Studi Kasus: Sektor Rumah Tangga & Roadmap Dekarbonisasi DKI Jakarta (2010–2050)**")

tab1, tab2, tab3 = st.tabs([
    "1. Deret Data & Profil Historis (2010–2024)",
    "2. Analisis Dekomposisi LMDI & Uji Kepekaan",
    "3. Kalkulator Simulasi Mitigasi (2025–2050)"
])

with tab1:
    st.subheader("Deret Data Emisi GRK & Konsumsi Energi Rumah Tangga (2010–2024)")
    col1, col2 = st.columns([1.2, 1])
    with col1:
        fig_hist = px.bar(
            df, x="Tahun", y=["C_Listrik", "C_LPG", "C_Gas"],
            title="Tren Emisi GRK Sektor Rumah Tangga DKI Jakarta (Gg CO2e)",
            labels={"value": "Emisi (Gg CO2e)", "variable": "Sumber Energi"}
        )
        st.plotly_chart(fig_hist, use_container_width=True)
    with col2:
        fig_en = px.area(
            df, x="Tahun", y=["E_Listrik_TJ", "E_LPG_TJ", "E_Gas_TJ"],
            title="Estimasi Konsumsi Energi Final Rumah Tangga (TJ)",
            labels={"value": "Energi (TJ)", "variable": "Jenis Energi"}
        )
        st.plotly_chart(fig_en, use_container_width=True)
    st.dataframe(df[["Tahun", "Penduduk_Juta", "PDRB_Konstan_T", "PDRB_Berlaku_T", "C_Listrik", "C_LPG", "C_Gas", "C_Total_Gg", "E_Total_TJ"]].style.format(precision=2))

with tab2:
    st.subheader("Hasil Dekomposisi LMDI-I Aditif & Uji Kepekaan PDRB")
    c_opt1, c_opt2, c_opt3 = st.columns(3)
    with c_opt1:
        jenis_pdrb = st.radio("Pilih Basis PDRB (Uji Kepekaan):", ["PDRB_Konstan_T", "PDRB_Berlaku_T"], format_func=lambda x: "PDRB Harga Konstan (2010)" if x=="PDRB_Konstan_T" else "PDRB Harga Berlaku")
    with c_opt2:
        t_awal = st.selectbox("Tahun Awal:", list(range(2010, 2024)), index=0)
    with c_opt3:
        t_akhir = st.selectbox("Tahun Akhir:", list(range(t_awal+1, 2025)), index=len(range(t_awal+1, 2025))-1)
        
    hasil_custom = hitung_lmdi(df, t_awal, t_akhir, jenis_pdrb)
    
    # Grafik Waterfall LMDI
    faktor_names = ["Efek Penduduk", "Efek Kemakmuran (PDRB/Kapita)", "Efek Intensitas Energi", "Efek Bauran Bahan Bakar", "Efek Faktor Emisi", "Total Perubahan (ΔC)"]
    faktor_vals = [
        hasil_custom["Efek Penduduk (ΔC_pop)"],
        hasil_custom["Efek Kemakmuran (ΔC_aff)"],
        hasil_custom["Efek Intensitas Energi (ΔC_int)"],
        hasil_custom["Efek Bauran Energi (ΔC_mix)"],
        hasil_custom["Efek Faktor Emisi (ΔC_ef)"],
        hasil_custom["Perubahan Total (ΔC)"]
    ]
    fig_wf = go.Figure(go.Waterfall(
        orientation="v",
        measure=["relative", "relative", "relative", "relative", "relative", "total"],
        x=faktor_names,
        y=faktor_vals,
        text=[f"{v:+.1f}" for v in faktor_vals],
        textposition="outside"
    ))
    fig_wf.update_layout(title=f"Grafik Waterfall Dekomposisi LMDI Periode {t_awal}–{t_akhir} (Gg CO2e)")
    st.plotly_chart(fig_wf, use_container_width=True)
    
    # Tabel Ringkasan Multi-Periode (Siap Masuk Bab 4 Skripsi)
    st.markdown("**Tabel Ringkasan Dekomposisi Multi-Periode (Pra-Pandemi, Pandemi 2020, Pasca-Pandemi, & Total):**")
    ringkasan_periode = pd.DataFrame([
        hitung_lmdi(df, 2010, 2019, jenis_pdrb),
        hitung_lmdi(df, 2019, 2020, jenis_pdrb),
        hitung_lmdi(df, 2020, 2024, jenis_pdrb),
        hitung_lmdi(df, 2019, 2024, jenis_pdrb),
        hitung_lmdi(df, 2010, 2024, jenis_pdrb)
    ])
    st.table(ringkasan_periode)

with tab3:
    st.subheader("Kalkulator Simulasi Target Mitigasi Rumah Tangga (2025–2030 & NZE 2050)")
    col_s1, col_s2 = st.columns([1, 2])
    with col_s1:
        st.markdown("**Parameter Kontrol Kebijakan:**")
        capai_labelling = st.slider("Ketercapaian Program Labelling (AC, Lampu, Refrigerasi) [% dari Target DLH]:", 0, 150, 100, step=10)
        reduksi_ef_grid = st.slider("Dekarbonisasi / Penurunan Faktor Emisi Listrik Grid Jamali s.d. 2030 (%):", 0, 40, 10, step=5)
        laju_bau = st.slider("Asumsi Pertumbuhan Emisi Baseline Tahunan (% per tahun):", 0.5, 4.0, 2.2, step=0.1)
        
    with col_s2:
        tahun_proj = [2024, 2025, 2026, 2027, 2028, 2029, 2030]
        target_labelling_dlh = [0, 2442, 2610, 2814, 3054, 3329, 3630] # Tabel 3 Laporan DLH
        
        c_2024 = 16180.0
        bau_vals, skenario_vals = [], []
        for idx, thn in enumerate(tahun_proj):
            if idx == 0:
                bau_vals.append(c_2024)
                skenario_vals.append(c_2024)
            else:
                bau_t = c_2024 * ((1 + laju_bau/100) ** idx)
                red_label = target_labelling_dlh[idx] * (capai_labelling / 100.0)
                # Efek penurunan faktor emisi grid bertahap hingga 2030 pada porsi listrik (~91.6% emisi RT)
                red_grid = (bau_t * 0.916) * ((reduksi_ef_grid / 100.0) * (idx / 6.0))
                bau_vals.append(bau_t)
                skenario_vals.append(max(0, bau_t - red_label - red_grid))
                
        df_sim = pd.DataFrame({
            "Tahun": tahun_proj,
            "Baseline (BaU)": bau_vals,
            "Skenario Simulasi Mitigasi": skenario_vals
        })
        fig_sim = px.line(df_sim, x="Tahun", y=["Baseline (BaU)", "Skenario Simulasi Mitigasi"], markers=True,
                          title="Simulasi Lintasan Emisi GRK Rumah Tangga DKI Jakarta 2024–2030 (Gg CO2e)")
        st.plotly_chart(fig_sim, use_container_width=True)
        
        reduksi_2030 = bau_vals[-1] - skenario_vals[-1]
        persen_red_2030 = (reduksi_2030 / bau_vals[-1]) * 100
        st.success(f"**Hasil Simulasi 2030:** Total reduksi emisi mencapai **{reduksi_2030:,.0f} Gg CO2e** (**{persen_red_2030:.1f}%** di bawah Baseline 2030).")