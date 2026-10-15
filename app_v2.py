import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# ==========================================
# KONFIGURASI HALAMAN & GAYA VISUAL
# ==========================================
st.set_page_config(
    page_title="Dashboard LMDI & Simulator Mitigasi GRK DKI Jakarta",
    page_icon="🌿",
    layout="wide"
)

# ==========================================
# 1. DATABASE INTERNAL (LAPORAN AKHIR DLH DKI JAKARTA 2026)
# ==========================================
data_historis = {
    "Tahun": list(range(2010, 2025)),
    "Penduduk_Juta": [9.64, 9.89, 9.86, 9.97, 10.08, 10.18, 10.28, 10.37, 10.47, 10.56, 10.56, 10.61, 10.68, 10.67, 10.68],
    "PDRB_Konstan_T": [1080.00, 1260.00, 1222.53, 1296.69, 1373.39, 1454.56, 1539.92, 1635.36, 1735.21, 1836.24, 1792.29, 1856.00, 1953.49, 2050.47, 2151.04],
    "PDRB_Berlaku_T": [1075.0, 1224.0, 1369.0, 1547.0, 1762.0, 1989.0, 2159.0, 2365.0, 2593.0, 2816.0, 2767.0, 2913.0, 3189.0, 3443.0, 3679.0],
    "EF_Listrik_MWh": [0.830, 0.880, 0.927, 0.967, 0.949, 1.023, 0.990, 0.897, 0.894, 0.906, 0.902, 0.896, 0.901, 0.903, 0.903],
    "C_Listrik": [7560.0, 8400.0, 9590.0, 11100.0, 10500.0, 11700.0, 12500.0, 11300.0, 11800.0, 12600.0, 13100.0, 13100.0, 13300.0, 14100.0, 14828.0],
    "C_LPG": [982.0, 1044.0, 1082.0, 1076.0, 1076.0, 1393.0, 1366.0, 1444.0, 1447.0, 1266.0, 1289.0, 1300.0, 1318.0, 1338.0, 1348.0],
    "C_Gas": [0.4, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 7.0, 7.0, 7.0, 4.0],
    "Intensitas_DKI": [37.53, 34.39, 39.25, 42.44, 37.50, 38.92, 38.21, 34.89, 34.56, 33.12, 30.20, 30.52, 30.85, 30.54, 30.14]
}

df = pd.DataFrame(data_historis)

# Konversi Faktor Emisi ke Gg CO2e / TJ (1 GWh = 3.6 TJ)
df["EF_Listrik_TJ"] = df["EF_Listrik_MWh"] / 3.6
df["EF_LPG_TJ"] = 0.06537   # Tabel 3.5: 65.370 kg CO2/TJ
df["EF_Gas_TJ"] = 0.05764   # Tabel 3.5: 57.640 kg CO2/TJ

# Turunkan Konsumsi Energi Final (TJ)
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
    
    g0, gt = Y0 / P0, Yt / Pt
    I0, It = E0 / Y0, Et / Yt
    
    fuels = [("Listrik", "C_Listrik", "E_Listrik_TJ", "EF_Listrik_TJ"),
             ("LPG", "C_LPG", "E_LPG_TJ", "EF_LPG_TJ"),
             ("Gas", "C_Gas", "E_Gas_TJ", "EF_Gas_TJ")]
    
    dC_pop, dC_aff, dC_int, dC_mix, dC_ef = 0.0, 0.0, 0.0, 0.0, 0.0
    
    for _, col_c, col_e, col_ef in fuels:
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
# 3. SIDEBAR IDENTITAS & METODOLOGI
# ==========================================
with st.sidebar:
    st.markdown("### 🎓 Identitas Penelitian")
    st.markdown("""
    **Judul:** Dekomposisi Pendorong Perubahan Emisi GRK Sektor Rumah Tangga DKI Jakarta (2010–2024) dan Simulasi Skenario Mitigasi Menuju 2050
    
    **Peneliti:** Dewantara Putra Makmur  
    **NIM:** G2401231071  
    **Pembimbing:** Perdinan, S.Si., M.Nat.Res.Econ., Ph.D.  
    **Departemen:** Geofisika dan Meteorologi, FMIPA IPB University
    """)
    st.divider()
    st.markdown("### 📖 Ringkasan Metode LMDI")
    st.latex(r"C = \sum_i P \times \frac{Y}{P} \times \frac{E}{Y} \times \frac{E_i}{E} \times \frac{C_i}{E_i}")
    st.caption("Sumber Data Utama: Laporan Akhir Inventarisasi Profil Emisi & Pelaporan Penurunan Emisi GRK Provinsi DKI Jakarta (DLH 2026).")

# ==========================================
# 4. HEADER & KARTU METRIK UTAMA (KPI CARDS)
# ==========================================
st.title("🌿 Dashboard Dekomposisi LMDI & Simulator Mitigasi GRK DKI Jakarta")
st.markdown("**Sistem Pendukung KeputusanAnalisis Faktor Pendorong Historis (2010–2024) dan Evaluasi Skenario Dekarbonisasi Rumah Tangga (2025–2050)**")

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Total Emisi RT (2024)", "16.180 Gg CO₂e", "+89,4% dari 2010", delta_color="inverse")
kpi2.metric("Porsi Emisi Listrik RT (2024)", "91,6%", "14.828 Gg CO₂e (Indirect)", delta_color="off")
kpi3.metric("Intensitas Emisi Ekonomi DKI", "30,14 tCO₂e/Miliar Rp", "-19,7% dari 2010 (37,53)", delta_color="normal")
kpi4.metric("Target Reduksi RT (2030)", "3.630 Gg CO₂e", "Program Labelling & Efisiensi", delta_color="normal")

st.divider()

# ==========================================
# 5. TAB NAVIGASI UTAMA
# ==========================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 1. Profil Historis (2010–2024)",
    "🔍 2. Dekomposisi LMDI & Dinamika Tahunan",
    "⚖️ 3. Uji Kepekaan (PDRB & Faktor Emisi)",
    "🎛️ 4. Kalkulator Simulasi Mitigasi (2025–2050)"
])

# --- TAB 1: PROFIL HISTORIS ---
with tab1:
    st.subheader("Deret Data Emisi GRK & Konsumsi Energi Sektor Rumah Tangga (2010–2024)")
    col1, col2 = st.columns(2)
    
    with col1:
        df_plot_c = df.rename(columns={
            "C_Listrik": "Listrik (Emisi Tidak Langsung)",
            "C_LPG": "LPG (Emisi Langsung)",
            "C_Gas": "Gas Bumi (Emisi Langsung)"
        })
        fig_hist = px.bar(
            df_plot_c, x="Tahun",
            y=["Listrik (Emisi Tidak Langsung)", "LPG (Emisi Langsung)", "Gas Bumi (Emisi Langsung)"],
            title="Tren Emisi GRK Sektor Rumah Tangga DKI Jakarta (Gg CO₂e)",
            labels={"value": "Emisi GRK (Gg CO₂e)", "variable": "Sumber Emisi"},
            color_discrete_sequence=["#1f77b4", "#ff7f0e", "#2ca02c"]
        )
        fig_hist.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig_hist, use_container_width=True)
        
    with col2:
        df_plot_e = df.rename(columns={
            "E_Listrik_TJ": "Listrik PLN (TJ)",
            "E_LPG_TJ": "LPG (TJ)",
            "E_Gas_TJ": "Gas Bumi (TJ)"
        })
        fig_en = px.area(
            df_plot_e, x="Tahun",
            y=["Listrik PLN (TJ)", "LPG (TJ)", "Gas Bumi (TJ)"],
            title="Estimasi Konsumsi Energi Final Rumah Tangga (Terajoule / TJ)",
            labels={"value": "Konsumsi Energi (TJ)", "variable": "Jenis Energi"},
            color_discrete_sequence=["#1f77b4", "#ff7f0e", "#2ca02c"]
        )
        fig_en.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig_en, use_container_width=True)

    st.markdown("#### Tabel Deret Data Historis Sektor Rumah Tangga (2010–2024)")
    tabel_tampil = df[[
        "Tahun", "Penduduk_Juta", "PDRB_Konstan_T", "PDRB_Berlaku_T",
        "EF_Listrik_MWh", "C_Listrik", "C_LPG", "C_Gas", "C_Total_Gg", "E_Total_TJ"
    ]].rename(columns={
        "Penduduk_Juta": "Penduduk (Juta)",
        "PDRB_Konstan_T": "PDRB Konstan (Triliun Rp)",
        "PDRB_Berlaku_T": "PDRB Berlaku (Triliun Rp)",
        "EF_Listrik_MWh": "EF Listrik (tCO2/MWh)",
        "C_Listrik": "Emisi Listrik (Gg)",
        "C_LPG": "Emisi LPG (Gg)",
        "C_Gas": "Emisi Gas (Gg)",
        "C_Total_Gg": "Total Emisi RT (Gg)",
        "E_Total_TJ": "Total Energi RT (TJ)"
    })
    st.dataframe(tabel_tampil.style.format(precision=2), use_container_width=True)
    st.download_button("📥 Unduh Tabel Deret Data (CSV)", tabel_tampil.to_csv(index=False).encode("utf-8"), "deret_data_rt_dki_2010_2024.csv", "text/csv")

# --- TAB 2: DEKOMPOSISI LMDI ---
with tab2:
    st.subheader("Analisis Dekomposisi LMDI-I Aditif: Multi-Periode & Tahunan Berantai")
    c_opt1, c_opt2, c_opt3 = st.columns(3)
    with c_opt1:
        jenis_pdrb = st.radio(
            "Pilih Basis PDRB:",
            ["PDRB_Konstan_T", "PDRB_Berlaku_T"],
            format_func=lambda x: "PDRB Harga Konstan (2010)" if x=="PDRB_Konstan_T" else "PDRB Harga Berlaku"
        )
    with c_opt2:
        t_awal = st.selectbox("Tahun Awal:", list(range(2010, 2024)), index=0)
    with c_opt3:
        t_akhir = st.selectbox("Tahun Akhir:", list(range(t_awal+1, 2025)), index=len(range(t_awal+1, 2025))-1)
        
    hasil_custom = hitung_lmdi(df, t_awal, t_akhir, jenis_pdrb)
    
    faktor_names = [
        "Efek Penduduk (ΔC_pop)", "Efek Kemakmuran (ΔC_aff)",
        "Efek Intensitas Energi (ΔC_int)", "Efek Bauran Energi (ΔC_mix)",
        "Efek Faktor Emisi (ΔC_ef)", "Total Perubahan (ΔC)"
    ]
    faktor_vals = [
        hasil_custom["Efek Penduduk (ΔC_pop)"],
        hasil_custom["Efek Kemakmuran (ΔC_aff)"],
        hasil_custom["Efek Intensitas Energi (ΔC_int)"],
        hasil_custom["Efek Bauran Energi (ΔC_mix)"],
        hasil_custom["Efek Faktor Emisi (ΔC_ef)"],
        hasil_custom["Perubahan Total (ΔC)"]
    ]
    
    # Margin otomatis agar label angka di atas batang tidak terpotong
    max_val = max(faktor_vals + [sum([v for v in faktor_vals[:-1] if v > 0])])
    min_val = min(faktor_vals + [0])
    
    fig_wf = go.Figure(go.Waterfall(
        orientation="v",
        measure=["relative", "relative", "relative", "relative", "relative", "total"],
        x=faktor_names,
        y=faktor_vals,
        text=[f"{v:+.1f}" for v in faktor_vals],
        textposition="outside",
        increasing={"marker": {"color": "#ef553b"}},  # Merah = mendorong kenaikan emisi
        decreasing={"marker": {"color": "#00cc96"}},  # Hijau = menahan/menurunkan emisi
        totals={"marker": {"color": "#636efa"}}
    ))
    fig_wf.update_layout(
        title=f"Grafik Waterfall Dekomposisi LMDI Periode {t_awal}–{t_akhir} (Gg CO₂e) — Merah: Pendorong Emisi | Hijau: Penahan Emisi",
        yaxis=dict(range=[min_val * 1.25 - 500, max_val * 1.25 + 1000], title="Perubahan Emisi (Gg CO₂e)")
    )
    st.plotly_chart(fig_wf, use_container_width=True)
    
    # Grafik Dekomposisi Tahunan Berantai (Chained YoY) sesuai Prosedur No. 4 Skripsi
    st.markdown("#### Grafik Dekomposisi Tahunan Berantai (*Chained Year-over-Year* 2010–2024)")
    chained_list = [hitung_lmdi(df, y, y+1, jenis_pdrb) for y in range(2010, 2024)]
    df_chained = pd.DataFrame(chained_list)
    
    fig_chain = go.Figure()
    komponen_cols = [
        ("Efek Penduduk (ΔC_pop)", "#ffa15a"),
        ("Efek Kemakmuran (ΔC_aff)", "#ef553b"),
        ("Efek Intensitas Energi (ΔC_int)", "#00cc96"),
        ("Efek Bauran Energi (ΔC_mix)", "#ab63fa"),
        ("Efek Faktor Emisi (ΔC_ef)", "#19d3f3")
    ]
    for col_name, warna in komponen_cols:
        fig_chain.add_trace(go.Bar(name=col_name, x=df_chained["Periode"], y=df_chained[col_name], marker_color=warna))
    fig_chain.add_trace(go.Scatter(
        name="Perubahan Total (ΔC)", x=df_chained["Periode"], y=df_chained["Perubahan Total (ΔC)"],
        mode="lines+markers", line=dict(color="black", width=2.5)
    ))
    fig_chain.update_layout(
        barmode="relative",
        title="Dinamika Kontribusi Faktor Pendorong Emisi Rumah Tangga Antartahun (2010–2024)",
        yaxis_title="Perubahan Emisi (Gg CO₂e)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_chain, use_container_width=True)

    st.markdown("#### Tabel Ringkasan Dekomposisi Multi-Periode (Siap Salin ke Bab 4 Skripsi)")
    ringkasan_periode = pd.DataFrame([
        hitung_lmdi(df, 2010, 2019, jenis_pdrb),
        hitung_lmdi(df, 2019, 2020, jenis_pdrb),
        hitung_lmdi(df, 2020, 2024, jenis_pdrb),
        hitung_lmdi(df, 2019, 2024, jenis_pdrb),
        hitung_lmdi(df, 2010, 2024, jenis_pdrb)
    ])
    st.dataframe(ringkasan_periode.style.format(precision=2), use_container_width=True)
    st.download_button("📥 Unduh Tabel Ringkasan Multi-Periode (CSV)", ringkasan_periode.to_csv(index=False).encode("utf-8"), "tabel_lmdi_multiperiode.csv", "text/csv")

# --- TAB 3: UJI KEPEKAAN ---
with tab3:
    st.subheader("Uji Kepekaan: PDRB Harga Konstan vs. Harga Berlaku & Efek Tahun Pandemi 2020")
    st.markdown("Sesuai **Prosedur Penelitian No. 6**, bagian ini membandingkan hasil dekomposisi menggunakan **PDRB Harga Konstan (2010)** dan **PDRB Harga Berlaku** (Tanoto dan Praptiningsih 2013), serta mengevaluasi dampak anomali pandemi 2020.")
    
    k_2010_2024 = hitung_lmdi(df, 2010, 2024, "PDRB_Konstan_T")
    b_2010_2024 = hitung_lmdi(df, 2010, 2024, "PDRB_Berlaku_T")
    
    # Akumulasi rantai tahunan tanpa transisi pandemi 2019-2020
    chain_konstan_no2020 = [hitung_lmdi(df, y, y+1, "PDRB_Konstan_T") for y in range(2010, 2024) if y != 2019]
    df_no2020 = pd.DataFrame(chain_konstan_no2020)
    
    df_sens = pd.DataFrame([
        {"Skenario Uji Kepekaan": "1. Basis PDRB Harga Konstan (2010–2024 Penuh)", **k_2010_2024},
        {"Skenario Uji Kepekaan": "2. Basis PDRB Harga Berlaku (2010–2024 Penuh)", **b_2010_2024},
        {
            "Skenario Uji Kepekaan": "3. Basis PDRB Harga Konstan (Tanpa Transisi Pandemi 2019–2020)",
            "Periode": "2010–2024 (Excl. 2019–2020)",
            "Perubahan Total (ΔC)": round(df_no2020["Perubahan Total (ΔC)"].sum(), 2),
            "Efek Penduduk (ΔC_pop)": round(df_no2020["Efek Penduduk (ΔC_pop)"].sum(), 2),
            "Efek Kemakmuran (ΔC_aff)": round(df_no2020["Efek Kemakmuran (ΔC_aff)"].sum(), 2),
            "Efek Intensitas Energi (ΔC_int)": round(df_no2020["Efek Intensitas Energi (ΔC_int)"].sum(), 2),
            "Efek Bauran Energi (ΔC_mix)": round(df_no2020["Efek Bauran Energi (ΔC_mix)"].sum(), 2),
            "Efek Faktor Emisi (ΔC_ef)": round(df_no2020["Efek Faktor Emisi (ΔC_ef)"].sum(), 2),
            "Residual": 0.0
        }
    ]).drop(columns=["Periode"])
    
    st.dataframe(df_sens.style.format(precision=2), use_container_width=True)
    st.info("💡 **Interpretasi Kunci untuk Bab 4:** Penggunaan PDRB Harga Berlaku memperbesar nilai positif Efek Kemakmuran (ΔC_aff) dan nilai negatif Efek Intensitas Energi (ΔC_int) secara semu akibat terikutnya komponen inflasi harga pada PDRB Berlaku. Selain itu, jika tahun pandemi 2019–2020 dikeluarkan, efek penghematan intensitas energi (ΔC_int) menjadi jauh lebih kuat (-2.574,2 Gg CO₂e vs. -1.652,9 Gg CO₂e) karena pada tahun 2020 terjadi lonjakan konsumsi listrik di dalam rumah (WFH) saat PDRB turun.")

# --- TAB 4: KALKULATOR SIMULASI 2025-2050 ---
with tab4:
    st.subheader("Kalkulator Simulasi Skenario Mitigasi Sektor Rumah Tangga (2025–2030 & NZE 2050)")
    col_s1, col_s2 = st.columns([1, 2.2])
    
    with col_s1:
        st.markdown("#### 🎛️ Parameter Kontrol Simulasi")
        capai_labelling = st.slider("1. Ketercapaian Program Labelling Efisiensi (AC, Lampu, Refrigerasi) [% Target DLH]:", 0, 150, 100, step=10)
        capai_plts_nze = st.slider("2. Realisasi Transisi PLTS Rooftop & Elektrifikasi Bersih Menuju 2050 [% Target NZE]:", 0, 150, 100, step=10)
        reduksi_ef_grid = st.slider("3. Tambahan Penurunan Faktor Emisi Grid Listrik Jamali s.d. 2030 (%):", 0, 40, 10, step=5)
        laju_bau = st.slider("4. Laju Pertumbuhan Emisi Baseline Tahunan (% per tahun):", 0.5, 4.0, 2.2, step=0.1)
        
    with col_s2:
        sub_c1, sub_c2 = st.columns(2)
        
        # Grafik 1: Proyeksi Tahunan 2024-2030 (Tabel 3 Laporan DLH)
        with sub_c1:
            tahun_proj = [2024, 2025, 2026, 2027, 2028, 2029, 2030]
            target_labelling_dlh = [0, 2442, 2610, 2814, 3054, 3329, 3630]
            c_2024 = 16180.0
            bau_vals, skenario_vals = [], []
            for idx, _ in enumerate(tahun_proj):
                if idx == 0:
                    bau_vals.append(c_2024)
                    skenario_vals.append(c_2024)
                else:
                    bau_t = c_2024 * ((1 + laju_bau/100) ** idx)
                    red_label = target_labelling_dlh[idx] * (capai_labelling / 100.0)
                    red_grid = (bau_t * 0.916) * ((reduksi_ef_grid / 100.0) * (idx / 6.0))
                    bau_vals.append(bau_t)
                    skenario_vals.append(max(0, bau_t - red_label - red_grid))
                    
            df_sim30 = pd.DataFrame({
                "Tahun": tahun_proj,
                "Baseline (BaU)": bau_vals,
                "Skenario Simulasi": skenario_vals
            })
            fig_sim30 = px.line(
                df_sim30, x="Tahun", y=["Baseline (BaU)", "Skenario Simulasi"], markers=True,
                title="Simulasi Tahunan 2024–2030 (Tabel 3 DLH)",
                labels={"value": "Emisi GRK (Gg CO₂e)", "variable": "Lintasan"}
            )
            fig_sim30.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
            st.plotly_chart(fig_sim30, use_container_width=True)
            
        # Grafik 2: Proyeksi Lima Tahunan 2035-2050 CPOS vs NZE (Tabel 4 & 5 Laporan DLH)
        with sub_c2:
            thn_nze = [2019, 2035, 2040, 2045, 2050]
            cpos_dlh = [13953.0, 14356.0, 12760.0, 12023.0, 11237.0]
            nze_dlh  = [13953.0, 14211.0, 11158.0, 9616.0, 5604.0]
            
            sim_nze = [13953.0]
            for i in range(1, len(thn_nze)):
                gap_mitigasi = cpos_dlh[i] - nze_dlh[i]
                emisi_tercapai = cpos_dlh[i] - (gap_mitigasi * (capai_plts_nze / 100.0))
                # Tambahan efek dekarbonisasi grid listrik
                emisi_tercapai = emisi_tercapai * (1 - (reduksi_ef_grid / 100.0) * 0.5)
                sim_nze.append(max(0, emisi_tercapai))
                
            df_sim50 = pd.DataFrame({
                "Tahun": thn_nze,
                "Skenario CPOS (DLH)": cpos_dlh,
                "Target NZE (DLH)": nze_dlh,
                "Simulasi Pengguna": sim_nze
            })
            fig_sim50 = px.line(
                df_sim50, x="Tahun", y=["Skenario CPOS (DLH)", "Target NZE (DLH)", "Simulasi Pengguna"], markers=True,
                title="Proyeksi Jangka Panjang 2035–2050 (Tabel 4 & 5 DLH)",
                labels={"value": "Emisi GRK (Gg CO₂e)", "variable": "Skenario"}
            )
            fig_sim50.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
            st.plotly_chart(fig_sim50, use_container_width=True)

        reduksi_2030 = bau_vals[-1] - skenario_vals[-1]
        persen_red_2030 = (reduksi_2030 / bau_vals[-1]) * 100
        residu_2050 = sim_nze[-1]
        st.success(
            f"**Ringkasan Hasil Simulasi:**\n"
            f"- **Tahun 2030:** Reduksi emisi sektor rumah tangga mencapai **{reduksi_2030:,.0f} Gg CO₂e** (**{persen_red_2030:.1f}%** di bawah Baseline 2030).\n"
            f"- **Tahun 2050:** Tingkat emisi rumah tangga berada pada **{residu_2050:,.0f} Gg CO₂e** (Target NZE DLH: **5.604 Gg CO₂e**; sisa emisi residu tersebut memerlukan mekanisme *carbon offset*)."
        )