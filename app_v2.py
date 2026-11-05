import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ==========================================================
# KONFIGURASI HALAMAN & GAYA VISUAL RAMAH AWAM
# ==========================================================
st.set_page_config(
    page_title="Jakarta Sudah Menurunkan Emisi, Tapi Seberapa Jauh?",
    page_icon="🌱",
    layout="wide",
)

FONT = "Segoe UI, Roboto, Helvetica, Arial, sans-serif"

st.markdown(
    """
    <style>
    .block-container { padding-top: 1.6rem; padding-bottom: 3rem; max-width: 1180px; }
    .stApp, .stApp p, .stApp li, .stApp label, .stApp h1, .stApp h2, .stApp h3 {
        font-family: -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    .banner {
        background: linear-gradient(135deg, #133B5C 0%, #1E5F74 55%, #289672 100%);
        color: white; padding: 26px 30px; border-radius: 16px;
        margin-bottom: 1.2rem; box-shadow: 0 8px 20px rgba(19, 59, 92, 0.14);
    }
    .banner-title { font-size: 1.85rem; font-weight: 800; margin: 0 0 6px 0; color: #FFFFFF; }
    .banner-sub { font-size: 1.0rem; opacity: 0.94; margin: 0; color: #E6FFFA; }
    .kpi-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 1.2rem; }
    .kpi-box {
        background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 14px;
        padding: 18px 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        border-top: 5px solid #1E5F74;
    }
    .kpi-box.green { border-top-color: #289672; }
    .kpi-box.orange { border-top-color: #E08E45; }
    .kpi-title { font-size: 0.86rem; color: #64748B; font-weight: 600; margin-bottom: 4px; }
    .kpi-value { font-size: 1.85rem; font-weight: 800; color: #0F172A; margin-bottom: 4px; }
    .kpi-desc { font-size: 0.84rem; color: #334155; font-weight: 500; }
    .tahukah-box {
        background: #F0FDF4; border: 1px solid #BBF7D0; border-left: 6px solid #16A34A;
        padding: 18px 22px; border-radius: 12px; margin: 12px 0 18px 0;
    }
    .tahukah-judul { font-size: 1.05rem; font-weight: 700; color: #14532D; margin-bottom: 6px; }
    .info-card {
        background: #F8FAFC; border: 1px solid #E2E8F0; border-left: 5px solid #1E5F74;
        padding: 16px 20px; border-radius: 10px; margin-top: 10px;
    }
    .prog-wrap {
        background: #E2E8F0; height: 22px; border-radius: 999px; overflow: hidden;
        margin: 8px 0 6px 0; position: relative;
    }
    button[data-baseweb="tab"] p { font-weight: 600; font-size: 0.96rem; }
    #MainMenu, footer { visibility: hidden; }
    @media (max-width: 850px) { .kpi-row { grid-template-columns: 1fr; } }
    </style>
    """,
    unsafe_allow_html=True,
)


def fmt_id(x, d=1):
    return f"{x:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def tata_letak(fig, y_title=None, tinggi=360):
    fig.update_layout(
        template="plotly_white",
        font=dict(family=FONT, size=12, color="#1E293B"),
        paper_bgcolor="white",
        plot_bgcolor="white",
        margin=dict(l=10, r=10, t=30, b=10),
        height=tinggi,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, title_text=""),
        hovermode="x unified",
        yaxis=dict(title=y_title, gridcolor="#F1F5F9", zerolinecolor="#CBD5E1"),
        xaxis=dict(showgrid=False),
    )
    return fig


# ==========================================================
# 1. DATA DARI LAPORAN AKHIR DLH DKI JAKARTA
# ==========================================================
@st.cache_data
def siapkan_data():
    # Data emisi historis per subsektor utama ( juta ton CO2e / 1.000 Gg ) periode 2010-2024
    df_sektor = pd.DataFrame({
        "Tahun": list(range(2010, 2025)),
        "Transportasi": [12.8, 15.1, 16.5, 17.2, 18.1, 19.8, 17.5, 18.2, 19.1, 20.3, 14.2, 15.1, 18.4, 19.6, 20.5],
        "Rumah Tangga": [8.5, 9.5, 10.7, 12.2, 11.6, 13.1, 13.9, 12.8, 13.3, 13.9, 14.4, 14.4, 14.6, 15.4, 16.2],
        "Komersial & Gedung": [9.2, 9.8, 10.9, 11.8, 11.5, 12.4, 12.9, 12.1, 12.6, 13.2, 11.8, 12.0, 12.7, 13.1, 13.7],
        "Industri & Pembangkit": [7.1, 7.3, 9.1, 11.4, 9.2, 11.3, 11.5, 10.9, 11.8, 10.3, 8.9, 9.4, 10.2, 10.5, 10.8],
        "Limbah (Sampah & Air Limbah)": [2.9, 3.0, 3.1, 3.2, 3.2, 3.3, 3.4, 3.5, 3.5, 3.6, 3.5, 3.5, 3.6, 3.6, 3.6],
    })

    # Data kontribusi per aksi mitigasi utama (Juta Ton CO2e)
    df_aksi = pd.DataFrame([
        {
            "Aksi": "Pembangkit Bersih (PLTGU Muara Karang & EBT)",
            "Reduksi_JutaTon": 11.45,
            "Sektor": "Pembangkit Listrik",
            "Apa_Itu": "Penggunaan bahan bakar gas bumi yang lebih bersih pada pembangkit listrik (seperti PLTGU Muara Karang) serta pemanfaatan energi terbarukan (PLTS).",
            "Dampak_Awam": "Karena lebih dari separuh emisi Jakarta berasal dari listrik, membersihkan pembangkit di hulu langsung memangkas emisi dalam jumlah paling besar.",
        },
        {
            "Aksi": "Intelligent Traffic System (ITS) & Manajemen Lalu Lintas",
            "Reduksi_JutaTon": 5.12,
            "Sektor": "Transportasi",
            "Apa_Itu": "Pengaturan lampu lalu lintas pintar berbasis kamera dan sensor untuk mengurai kemacetan di persimpangan utama Jakarta.",
            "Dampak_Awam": "Kendaraan yang tidak terjebak macet membakar lebih sedikit bensin/solar, sehingga emisi knalpot turun drastis.",
        },
        {
            "Aksi": "Efisiensi Peralatan Rumah Tangga & Komersial (Labelling)",
            "Reduksi_JutaTon": 4.28,
            "Sektor": "Bangunan (Rumah Tangga & Komersial)",
            "Apa_Itu": "Peralihan ke lampu LED, AC berlabel hemat energi (tanda bintang), dan penghematan listrik di gedung perkantoran/mal.",
            "Dampak_Awam": "Mengurangi tagihan listrik bulanan warga sekaligus mengurangi beban pembakaran batu bara dan gas di pembangkit PLN.",
        },
        {
            "Aksi": "Transportasi Massal (MRT, LRT, Transjakarta & Bus Listrik)",
            "Reduksi_JutaTon": 3.45,
            "Sektor": "Transportasi",
            "Apa_Itu": "Perluasan layanan angkutan umum massal rendah emisi dan peremajaan armada bus listrik untuk menggantikan kendaraan pribadi.",
            "Dampak_Awam": "Satu bus atau rangkaian kereta menggantikan puluhan mobil dan ratusan motor di jalan raya.",
        },
        {
            "Aksi": "Pengelolaan Sampah, Air Limbah & Ruang Terbuka Hijau",
            "Reduksi_JutaTon": 1.50,
            "Sektor": "Limbah & Kehutanan (FOLU)",
            "Apa_Itu": "Pengurangan sampah di sumber (3R/Bank Sampah), pengolahan kompos/gas metana TPA, serta penanaman pohon dan mangrove.",
            "Dampak_Awam": "Mencegah gas metana dari tumpukan sampah terlepas ke udara sekaligus menyerap kembali karbon melalui pepohonan kota.",
        },
    ])

    # Data jalur target reduksi tahunan 2025-2030 (Tabel 3 Laporan DLH, dikonversi dari Gg ke Juta Ton CO2e)
    df_jalur = pd.DataFrame({
        "Tahun": [2025, 2026, 2027, 2028, 2029, 2030],
        "Energi Final (Transportasi, Rumah Tangga, Gedung, Industri)": [12.20, 14.35, 16.51, 18.69, 20.94, 23.31],
        "Pembangkit Listrik": [8.47, 8.61, 8.75, 8.89, 9.03, 9.17],
        "Pengelolaan Limbah & RTH": [0.45, 0.68, 0.91, 1.15, 1.38, 1.61],
        "Total Target Reduksi (Tabel 3)": [21.11, 23.64, 26.17, 28.73, 31.35, 34.09],
    })
    return df_sektor, df_aksi, df_jalur


df_sektor, df_aksi, df_jalur = siapkan_data()

# ==========================================================
# 2. SIDEBAR RINGKAS
# ==========================================================
with st.sidebar:
    st.markdown("### 🌱 Tentang Dashboard")
    st.caption(
        "Dashboard edukasi publik untuk memantau sejauh mana Provinsi DKI Jakarta "
        "telah menurunkan emisi gas rumah kaca (GRK) menuju target tahun 2030."
    )
    st.divider()
    st.markdown("### 📌 Tiga Pertanyaan Utama")
    st.markdown(
        "1. **Sudah sampai mana?** (Tab Beranda)\n"
        "2. **Aksi mana yang menyumbang?** (Tab Sektor & Aksi)\n"
        "3. **Bagaimana jalur ke 2030?** (Tab Jalur 2030)"
    )
    st.divider()
    st.caption(
        "**Disusun oleh:** Dewantara Putra Makmur  \n"
        "Magang Bidang Tata Lingkungan, Dinas Lingkungan Hidup Provinsi DKI Jakarta  \n"
        "Sumber Data: Laporan Akhir Inventarisasi & Penurunan Emisi GRK DKI Jakarta (DLH 2026)."
    )

# ==========================================================
# 3. BANNER JUDUL BESAR
# ==========================================================
st.markdown(
    """
    <div class="banner">
        <div class="banner-title">Jakarta sudah menurunkan emisi, tapi seberapa jauh?</div>
        <div class="banner-sub">
            Menelusuri asal emisi Jakarta, program nyata yang sudah berjalan, dan seberapa dekat posisi kita dengan target iklim tahun 2030.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ==========================================================
# 4. EMPAT TAB ("BAB") UNTUK ORANG AWAM
# ==========================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "🏠 1. Beranda: Sudah sampai mana?",
    "🏭 2. Dari mana emisi Jakarta?",
    "🛠️ 3. Apa yang sudah dilakukan?",
    "🚀 4. Mau ke mana? (Jalur 2030)",
])

# ----------------------------------------------------------
# TAB 1: BERANDA
# ----------------------------------------------------------
with tab1:
    st.markdown(
        """
        <div class="kpi-row">
            <div class="kpi-box green">
                <div class="kpi-title">✅ Emisi yang Berhasil Dicegah (2025)</div>
                <div class="kpi-value">25,8 Juta Ton CO₂e</div>
                <div class="kpi-desc">Total pengurangan emisi dari berbagai program iklim</div>
            </div>
            <div class="kpi-box">
                <div class="kpi-title">📉 Persentase Penurunan dari Baseline</div>
                <div class="kpi-value">28,0%</div>
                <div class="kpi-desc">Berhasil ditekan dibanding jika tanpa program</div>
            </div>
            <div class="kpi-box orange">
                <div class="kpi-title">🎯 Jarak Menuju Target 2030 (32%)</div>
                <div class="kpi-value">Tinggal 4,0% Lagi</div>
                <div class="kpi-desc">Posisi Jakarta sudah mencapai 87,5% dari target 2030</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("**Seberapa dekat posisi Jakarta dengan target penurunan emisi 32% pada tahun 2030?**")
    persen_progres = (28.0 / 32.0) * 100
    st.markdown(
        f"""
        <div class="prog-wrap">
            <div style="width:{persen_progres:.1f}%;background:linear-gradient(90deg, #1E5F74, #289672);height:100%;"></div>
        </div>
        <div style="display:flex;justify-content:space-between;font-size:0.86rem;color:#334155;font-weight:600;margin-bottom:14px;">
            <span>Titik Awal (0%)</span>
            <span style="color:#16A34A;">📍 Posisi Saat Ini: 28,0% (25,8 Juta Ton CO₂e)</span>
            <span style="color:#133B5C;">🏁 Target 2030: 32,0%</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="tahukah-box">
            <div class="tahukah-judul">💡 Tahukah Kamu? Apa arti "Menurunkan Emisi dari Baseline"?</div>
            Bayangkan pengeluaran bulananmu biasa naik terus setiap tahun karena harga barang dan kebutuhan bertambah—perkiraan kenaikan normal tanpa usaha penghematan itulah yang disebut <b>Baseline</b>.<br><br>
            Ketika laporan menyebut Jakarta menurunkan emisi sebesar <b>25,8 juta ton CO₂e (28,0% dari baseline)</b>, artinya jika Jakarta tidak membangun transportasi umum, tidak mengatur kemacetan (ITS), dan tidak mengganti pembangkit listrik ke gas bersih, udara Jakarta seharusnya menerima tambahan 25,8 juta ton gas rumah kaca. Jumlah emisi yang berhasil dicegah ini setara dengan <b>menghentikan asap dari sekitar 5,6 juta mobil bensin selama satu tahun penuh!</b>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ----------------------------------------------------------
# TAB 2: DARI MANA EMISI JAKARTA?
# ----------------------------------------------------------
with tab2:
    st.subheader("Dari mana datangnya emisi gas rumah kaca di Jakarta?")
    thn_pilih = st.slider("Geser untuk memilih tahun pengamatan:", 2010, 2024, 2024)

    baris_thn = df_sektor[df_sektor["Tahun"] == thn_pilih].iloc[0]
    sektor_names = [
        "Transportasi",
        "Rumah Tangga",
        "Komersial & Gedung",
        "Industri & Pembangkit",
        "Limbah (Sampah & Air Limbah)",
    ]
    sektor_vals = [baris_thn[s] for s in sektor_names]
    total_thn = sum(sektor_vals)

    c1, c2 = st.columns([1.35, 1])
    with c1:
        st.markdown(f"**Komposisi Emisi Jakarta Tahun {thn_pilih} (Total: {fmt_id(total_thn)} Juta Ton CO₂e)**")
        fig_sek = go.Figure(
            go.Bar(
                x=sektor_vals,
                y=sektor_names,
                orientation="h",
                marker_color=["#1E5F74", "#289672", "#E08E45", "#4F6D7A", "#8E7CC3"],
                text=[f"{fmt_id(v)} Jt Ton ({v/total_thn*100:.1f}%)" for v in sektor_vals],
                textposition="auto",
            )
        )
        fig_sek.update_layout(yaxis=dict(autorange="reversed"))
        st.plotly_chart(tata_letak(fig_sek, None, 320), use_container_width=True, config={"displayModeBar": False})

    with c2:
        st.markdown("**Pilih satu sektor untuk melihat penjelasannya:**")
        pilih_info_sek = st.radio("Sektor:", sektor_names, label_visibility="collapsed")
        penjelasan_sektor = {
            "Transportasi": "Berasal dari pembakaran bensin dan solar kendaraan bermotor (motor, mobil, truk, dan bus) di jalan raya Jakarta. Sempat turun drastis pada tahun pandemi 2020 ketika warga bekerja dari rumah.",
            "Rumah Tangga": "Sebanyak 91,6% berasal dari pemakaian listrik di rumah (AC, kulkas, lampu, pompa air) dan sisanya dari pemakaian LPG/gas untuk memasak. Sektor ini terus naik bahkan saat pandemi 2020.",
            "Komersial & Gedung": "Berasal dari pemakaian listrik pendingin ruangan, pencahayaan, dan peralatan di gedung perkantoran, pusat perbelanjaan (mal), hotel, dan rumah sakit.",
            "Industri & Pembangkit": "Berasal dari pemakaian energi pada pabrik manufaktur serta proses pembangkitan listrik.",
            "Limbah (Sampah & Air Limbah)": "Berasal dari gas metana yang muncul saat tumpukan sampah organik membusuk di TPA serta dari pengolahan air limbah domestik dan industri.",
        }
        nilai_s = baris_thn[pilih_info_sek]
        st.markdown(
            f"""
            <div class="info-card">
                <div style="font-weight:700;font-size:1.05rem;color:#0F172A;margin-bottom:6px;">
                    {pilih_info_sek} — {fmt_id(nilai_s)} Juta Ton CO₂e ({nilai_s/total_thn*100:.1f}%)
                </div>
                <div style="font-size:0.92rem;color:#334155;">{penjelasan_sektor[pilih_info_sek]}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ----------------------------------------------------------
# TAB 3: APA YANG SUDAH DILAKUKAN?
# ----------------------------------------------------------
with tab3:
    st.subheader("Aksi mana yang paling banyak menyumbang penurunan emisi?")
    col_a1, col_a2 = st.columns([1.35, 1])

    with col_a1:
        st.markdown("**Sumbangan Penurunan Emisi per Kelompok Aksi Utama (Juta Ton CO₂e)**")
        fig_aksi = go.Figure(
            go.Bar(
                x=df_aksi["Reduksi_JutaTon"],
                y=df_aksi["Aksi"],
                orientation="h",
                marker_color=["#133B5C", "#1E5F74", "#289672", "#E08E45", "#6BA292"],
                text=[f"{fmt_id(v, 2)} Jt Ton ({v/25.8*100:.1f}%)" for v in df_aksi["Reduksi_JutaTon"]],
                textposition="auto",
            )
        )
        fig_aksi.update_layout(yaxis=dict(autorange="reversed"))
        st.plotly_chart(tata_letak(fig_aksi, None, 330), use_container_width=True, config={"displayModeBar": False})

    with col_a2:
        st.markdown("**Klik salah satu aksi untuk melihat cara kerjanya:**")
        pilihan_aksi = st.selectbox("Pilih Aksi Mitigasi:", df_aksi["Aksi"], label_visibility="collapsed")
        detail = df_aksi[df_aksi["Aksi"] == pilihan_aksi].iloc[0]
        st.markdown(
            f"""
            <div class="info-card">
                <div style="font-size:0.78rem;font-weight:700;color:#289672;text-transform:uppercase;">
                    Sektor: {detail['Sektor']}
                </div>
                <div style="font-weight:800;font-size:1.1rem;color:#0F172A;margin:4px 0 8px 0;">
                    {detail['Aksi']}
                </div>
                <div style="font-size:0.9rem;color:#334155;margin-bottom:8px;">
                    <b>Sumbangan Reduksi:</b> {fmt_id(detail['Reduksi_JutaTon'], 2)} Juta Ton CO₂e ({detail['Reduksi_JutaTon']/25.8*100:.1f}% dari total capaian)
                </div>
                <div style="font-size:0.9rem;color:#334155;margin-bottom:8px;">
                    <b>Apa itu?</b><br>{detail['Apa_Itu']}
                </div>
                <div style="font-size:0.9rem;color:#334155;">
                    <b>Mengapa dampaknya besar?</b><br>{detail['Dampak_Awam']}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ----------------------------------------------------------
# TAB 4: MAU KE MANA? (JALUR 2025-2030)
# ----------------------------------------------------------
with tab4:
    st.subheader("Bagaimana jalur target penurunan emisi Jakarta menuju 2030?")
    st.markdown(
        "Grafik di bawah ini membandingkan **jalur target pengurangan emisi tahunan 2025–2030 (Tabel 3 Laporan DLH)** "
        "dengan **capaian reduksi sebesar 25,8 juta ton CO₂e**."
    )

    col_j1, col_j2 = st.columns([1.45, 1])
    with col_j1:
        fig_j = go.Figure()
        fig_j.add_trace(
            go.Bar(
                x=df_jalur["Tahun"],
                y=df_jalur["Energi Final (Transportasi, Rumah Tangga, Gedung, Industri)"],
                name="Penghematan Energi & Transportasi",
                marker_color="#1E5F74",
            )
        )
        fig_j.add_trace(
            go.Bar(
                x=df_jalur["Tahun"],
                y=df_jalur["Pembangkit Listrik"],
                name="Pembangkit Listrik Bersih",
                marker_color="#289672",
            )
        )
        fig_j.add_trace(
            go.Bar(
                x=df_jalur["Tahun"],
                y=df_jalur["Pengelolaan Limbah & RTH"],
                name="Pengelolaan Limbah & RTH",
                marker_color="#E08E45",
            )
        )
        fig_j.add_trace(
            go.Scatter(
                x=df_jalur["Tahun"],
                y=[25.8] * len(df_jalur),
                name="Capaian 2025 (25,8 Jt Ton)",
                mode="lines",
                line=dict(color="#C8553D", width=3, dash="dash"),
            )
        )
        fig_j.update_layout(barmode="stack")
        fig_j.update_xaxes(dtick=1)
        st.plotly_chart(tata_letak(fig_j, "Juta Ton CO₂e", 350), use_container_width=True, config={"displayModeBar": False})

    with col_j2:
        st.markdown(
            """
            <div class="tahukah-box" style="margin-top:0;">
                <div class="tahukah-judul">📌 Apa yang Harus Dikejar hingga 2030?</div>
                <ul style="margin:0;padding-left:1.1rem;font-size:0.9rem;color:#1E293B;">
                    <li style="margin-bottom:6px;"><b>Target Rencana 2025 Terlampaui di Awal:</b> Capaian 25,8 juta ton CO₂e sudah melampaui target rencana Tabel 3 tahun 2025 (21,11 juta ton) dan mendekati target rencana tahun 2027 (26,17 juta ton).</li>
                    <li style="margin-bottom:6px;"><b>Tantangan Menuju 2030 (34,09 Juta Ton):</b> Mulai tahun 2027 hingga 2030, porsi reduksi dari pembangkit listrik cenderung mendatar (~9,17 juta ton), sehingga tambahan penurunan emisi wajib dikejar dari <b>penghematan energi rumah tangga, gedung komersial, dan peralihan kendaraan listrik/transportasi umum</b>.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.dataframe(
            df_jalur.rename(columns={
                "Energi Final (Transportasi, Rumah Tangga, Gedung, Industri)": "Energi & Transportasi",
                "Total Target Reduksi (Tabel 3)": "Total Target (Jt Ton)",
            }),
            hide_index=True,
            use_container_width=True,
        )
