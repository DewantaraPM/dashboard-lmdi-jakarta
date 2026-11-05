import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ==========================================================
# KONFIGURASI HALAMAN (TANPA SIDEBAR)
# ==========================================================
st.set_page_config(
    page_title="Evaluasi Emisi & Mitigasi GRK DKI Jakarta",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

FONT = "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
PALET = {
    "utama": "#0F172A",       # Slate 900
    "sekunder": "#1E3A5F",    # Deep Navy
    "aksen": "#334155",       # Slate 700
    "redup": "#64748B",       # Slate 500
    "terang": "#94A3B8",      # Slate 400
    "garis": "#E2E8F0",       # Slate 200
    "latar": "#F8FAFC",       # Slate 50
    "sorot": "#0284C7",       # Muted Blue
}

st.markdown(
    """
    <style>
    /* Sembunyikan sidebar & tombol buka-tutupnya secara permanen */
    [data-testid="stSidebar"], [data-testid="collapsedControl"] {
        display: none !important;
    }
    .block-container {
        padding-top: 2.2rem;
        padding-bottom: 3.5rem;
        max-width: 1120px;
    }
    .stApp, .stApp p, .stApp li, .stApp label, .stApp h1, .stApp h2, .stApp h3, .stApp h4 {
        font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        color: #0F172A;
    }
    /* Header Minimalis */
    .top-header {
        border-bottom: 1px solid #E2E8F0;
        padding-bottom: 1.2rem;
        margin-bottom: 1.6rem;
    }
    .top-meta {
        font-size: 0.78rem;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 6px;
    }
    .top-title {
        font-size: 1.85rem;
        font-weight: 700;
        color: #0F172A;
        letter-spacing: -0.02em;
        margin: 0 0 6px 0;
    }
    .top-sub {
        font-size: 0.96rem;
        color: #475569;
        margin: 0;
        line-height: 1.55;
    }
    /* Kartu Minimalis & Whitespace */
    .card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 20px 22px;
        margin-bottom: 16px;
    }
    .card-subtle {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 18px 22px;
        margin-bottom: 16px;
    }
    .card-title {
        font-size: 0.96rem;
        font-weight: 600;
        color: #0F172A;
        margin-bottom: 8px;
    }
    .card-metric-label {
        font-size: 0.8rem;
        color: #64748B;
        font-weight: 500;
        margin-bottom: 4px;
    }
    .card-metric-val {
        font-size: 1.7rem;
        font-weight: 700;
        color: #0F172A;
        letter-spacing: -0.02em;
        margin-bottom: 4px;
    }
    .card-metric-sub {
        font-size: 0.8rem;
        color: #475569;
    }
    /* Format Rata Kanan-Kiri (Justify) untuk seluruh narasi informasi */
    .justify-text {
        text-align: justify;
        font-size: 0.91rem;
        line-height: 1.65;
        color: #334155;
        margin: 0;
    }
    .justify-list {
        text-align: justify;
        font-size: 0.9rem;
        line-height: 1.65;
        color: #334155;
        margin: 0;
        padding-left: 1.15rem;
    }
    .justify-list li {
        margin-bottom: 8px;
    }
    .badge-tag {
        display: inline-block;
        background: #F1F5F9;
        color: #1E3A5F;
        border: 1px solid #CBD5E1;
        padding: 2px 9px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-bottom: 8px;
    }
    .prog-track {
        background: #E2E8F0;
        height: 12px;
        border-radius: 999px;
        overflow: hidden;
        margin: 10px 0 8px 0;
    }
    #MainMenu, footer { visibility: hidden; }
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


def tata_letak(fig, y_title=None, tinggi=340):
    fig.update_layout(
        template="plotly_white",
        font=dict(family=FONT, size=12, color="#1E293B"),
        paper_bgcolor="white",
        plot_bgcolor="white",
        margin=dict(l=8, r=8, t=26, b=8),
        height=tinggi,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, title_text=""),
        hovermode="x unified",
        yaxis=dict(title=y_title, gridcolor="#F1F5F9", zerolinecolor="#CBD5E1"),
        xaxis=dict(showgrid=False),
    )
    return fig


# ==========================================================
# 1. BASIS DATA (TERMASUK EKSTENSI 2025–2026)
# ==========================================================
@st.cache_data
def muat_semua_data():
    # Catatan: Nilai 2025 & 2026 dapat langsung disesuaikan dengan angka file Excel-mu
    df_sektor = pd.DataFrame({
        "Tahun": list(range(2010, 2027)),
        "Transportasi": [12.80, 15.10, 16.50, 17.20, 18.10, 19.80, 17.50, 18.20, 19.10, 20.30, 14.20, 15.10, 18.40, 19.60, 20.50, 20.95, 21.30],
        "Rumah Tangga": [8.54, 9.45, 10.68, 12.18, 11.58, 13.10, 13.87, 12.75, 13.25, 13.87, 14.40, 14.41, 14.63, 15.45, 16.18, 16.55, 16.90],
        "Komersial & Gedung": [9.20, 9.80, 10.90, 11.80, 11.50, 12.40, 12.90, 12.10, 12.60, 13.20, 11.80, 12.00, 12.70, 13.10, 13.70, 13.95, 14.20],
        "Industri & Pembangkit": [7.10, 7.30, 9.10, 11.40, 9.20, 11.30, 11.50, 10.90, 11.80, 10.30, 8.90, 9.40, 10.20, 10.50, 10.80, 10.90, 11.05],
        "Limbah (Sampah & Air Limbah)": [2.90, 3.00, 3.10, 3.20, 3.20, 3.30, 3.40, 3.50, 3.50, 3.60, 3.50, 3.50, 3.60, 3.60, 3.65, 3.68, 3.70],
    })

    # Ringkasan evaluasi capaian tahunan terhadap baseline (Juta Ton CO2e)
    df_evaluasi = pd.DataFrame({
        "Tahun": [2023, 2024, 2025, 2026],
        "Baseline_JtTon": [87.5, 89.8, 92.1, 94.5],
        "Reduksi_Klaim_JtTon": [22.4, 24.1, 25.8, 26.9],
        "Aktual_Inventaris_JtTon": [62.25, 64.83, 66.03, 67.15],
    })

    # Evaluasi kritis per kelompok aksi mitigasi
    df_aksi = pd.DataFrame([
        {
            "Aksi": "Pembangkit Bersih (PLTGU Muara Karang & EBT)",
            "Reduksi_JutaTon": 11.45,
            "Sektor": "Pembangkit Listrik (Hulu)",
            "Perkembangan": (
                "Aksi ini menyumbang porsi reduksi terbesar, yakni 11,45 juta ton CO₂e (44,4% dari total "
                "capaian reduksi 25,8 juta ton CO₂e). Penurunan diperoleh dari peralihan bahan bakar pembangkit "
                "ke gas bumi pada PLTGU Muara Karang serta integrasi energi terbarukan."
            ),
            "Temuan_Anomali": (
                "Terdapat ketimpangan struktural antara capaian hulu dan konsumsi hilir. Walaupun pembangkit "
                "di hulu mencatat klaim penurunan emisi yang sangat besar, konsumsi listrik aktual di sektor "
                "rumah tangga dan gedung komersial justru terus meningkat rata-rata 3,1% per tahun pasca-pandemi. "
                "Selain itu, dalam tabel inventarisasi DLH, faktor emisi jaringan listrik Jawa-Madura-Bali "
                "(Jamali) tahun 2020–2024 masih dipatok konstan mengikuti nilai tahun 2019 (0,903 tCO₂/MWh), "
                "sehingga klaim pembersihan pembangkit belum tercermin pada penurunan faktor emisi listrik konsumen."
            ),
        },
        {
            "Aksi": "Intelligent Traffic System (ITS) & Manajemen Lalu Lintas",
            "Reduksi_JutaTon": 5.12,
            "Sektor": "Transportasi Darat",
            "Perkembangan": (
                "Menyumbang pengurangan emisi sebesar 5,12 juta ton CO₂e (19,8% dari total capaian). "
                "Perhitungan reduksi didasarkan pada peningkatan kecepatan rata-rata kendaraan dan pengurangan "
                "waktu henti (idling) di persimpangan yang telah dilengkapi sensor lalu lintas adaptif."
            ),
            "Temuan_Anomali": (
                "Terdapat perbedaan arah antara klaim reduksi berbasis pemodelan kecepatan lalu lintas dengan "
                "data penjualan bahan bakar aktual. Pada inventarisasi sektoral, emisi transportasi darat "
                "tetap tumbuh dari 19,6 juta ton (2023) menjadi 20,5 juta ton CO₂e (2024). Hal ini menunjukkan "
                "bahwa efisiensi kelancaran lalu lintas pada titik ITS berpotensi terimbangi oleh pertambahan "
                "jumlah kendaraan bermotor dan fenomena bangkitan perjalanan (rebound effect)."
            ),
        },
        {
            "Aksi": "Efisiensi Peralatan Rumah Tangga & Gedung (Labelling)",
            "Reduksi_JutaTon": 4.28,
            "Sektor": "Bangunan (Rumah Tangga & Komersial)",
            "Perkembangan": (
                "Berkontribusi menurunkan emisi sebesar 4,28 juta ton CO₂e (16,6% dari total capaian) melalui "
                "penerapan Standar Kinerja Energi Minimum (SKEM) dan label tanda hemat energi pada penyejuk "
                "udara (AC), lampu LED, dan lemari es."
            ),
            "Temuan_Anomali": (
                "Ditemukan ketidaksinkronan antara garis proyeksi perencanaan dan realisasi aktual. Dalam Tabel 4 "
                "dokumen DLH, emisi skenario kebijakan berjalan (CPOS) subsektor rumah tangga tahun 2035 "
                "diproyeksikan sebesar 14,36 juta ton CO₂e, padahal realisasi emisi rumah tangga pada tahun 2024 "
                "saja sudah menembus 16,18 juta ton CO₂e. Artinya, penghematan per unit alat elektronik kalah "
                "cepat dibandingkan lonjakan kepemilikan perangkat baru di rumah tangga."
            ),
        },
        {
            "Aksi": "Transportasi Massal (MRT, LRT, Transjakarta & Bus Listrik)",
            "Reduksi_JutaTon": 3.45,
            "Sektor": "Transportasi Publik",
            "Perkembangan": (
                "Menyumbang reduksi sebesar 3,45 juta ton CO₂e (13,4% dari total capaian) melalui perpindahan "
                "pengguna kendaraan pribadi ke angkutan umum massal (modal shift) serta elektrifikasi armada "
                "bus Transjakarta."
            ),
            "Temuan_Anomali": (
                "Besarnya reduksi emisi dari elektrifikasi bus sangat bergantung pada faktor emisi listrik PLN. "
                "Selama jaringan listrik interkoneksi Jamali masih didominasi pembangkit batu bara dengan faktor "
                "emisi terkoreksi 0,903 tCO₂/MWh, peralihan dari bus solar ke bus listrik sebenarnya memindahkan "
                "sebagian emisi dari jalan raya (emisi langsung) ke pembangkit listrik (emisi tidak langsung)."
            ),
        },
        {
            "Aksi": "Pengelolaan Sampah, Air Limbah & Ruang Terbuka Hijau",
            "Reduksi_JutaTon": 1.50,
            "Sektor": "Limbah & Kehutanan (FOLU)",
            "Perkembangan": (
                "Menyumbang pengurangan dan penyerapan emisi sebesar 1,50 juta ton CO₂e (5,8% dari total capaian) "
                "melalui pengurangan sampah di sumber (3R), pengolahan air limbah domestik, serta pemeliharaan "
                "ruang terbuka hijau (RTH) dan mangrove pesisir."
            ),
            "Temuan_Anomali": (
                "Dalam Tabel 3 peta jalan 2025–2030, target penyerapan karbon sektor FOLU (RTH) justru tercatat "
                "menurun dari 29 ribu ton CO₂e pada 2025 menjadi 16 ribu ton CO₂e pada 2030 akibat keterbatasan "
                "lahan baru di Jakarta. Sebaliknya, target reduksi sektor limbah diproyeksikan melonjak drastis "
                "เกือบ empat kali lipat (dari 0,42 juta ton di 2025 menjadi 1,60 juta ton di 2030) yang "
                "keberhasilannya sangat bergantung pada beroperasinya fasilitas pengolahan sampah skala besar."
            ),
        },
    ])

    # Data jalur target 2025-2030 (Tabel 3 Laporan DLH dalam Juta Ton CO2e)
    df_jalur = pd.DataFrame({
        "Tahun": [2025, 2026, 2027, 2028, 2029, 2030],
        "Energi & Transportasi": [12.20, 14.35, 16.51, 18.69, 20.94, 23.31],
        "Pembangkit Listrik": [8.47, 8.61, 8.75, 8.89, 9.03, 9.17],
        "Pengelolaan Limbah & RTH": [0.45, 0.68, 0.91, 1.15, 1.38, 1.61],
        "Total Target (Jt Ton)": [21.11, 23.64, 26.17, 28.73, 31.35, 34.09],
    })

    return df_sektor, df_evaluasi, df_aksi, df_jalur


df_sektor, df_evaluasi, df_aksi, df_jalur = siapkan_data()

# ==========================================================
# 2. STATE NAVIGASI HALAMAN (DEFAULT: BERANDA)
# ==========================================================
DAFTAR_HALAMAN = [
    "Beranda: Pengenalan & Temuan",
    "1. Sudah sampai mana?",
    "2. Dari mana emisi Jakarta?",
    "3. Apa yang sudah dilakukan?",
    "4. Mau ke mana? (2025–2030)",
]

if "hal_aktif" not in st.session_state:
    st.session_state["hal_aktif"] = DAFTAR_HALAMAN[0]


def pindah_ke(nama_hal):
    st.session_state["hal_aktif"] = nama_hal


# ==========================================================
# 3. HEADER UTAMA & BAR NAVIGASI MINIMALIS
# ==========================================================
st.markdown(
    """
    <div class="top-header">
        <div class="top-meta">Evaluasi Inventarisasi & Mitigasi GRK Provinsi DKI Jakarta • Bidang Tata Lingkungan DLH</div>
        <div class="top-title">Jakarta sudah menurunkan emisi, tapi seberapa jauh?</div>
        <div class="top-sub">
            Telaah interaktif atas profil emisi sektoral, capaian aksi mitigasi, serta temuan anomali data menuju target iklim 2030.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

pilihan_nav = st.radio(
    "Navigasi Bagian:",
    DAFTAR_HALAMAN,
    index=DAFTAR_HALAMAN.index(st.session_state["hal_aktif"]),
    horizontal=True,
    label_visibility="collapsed",
)
if pilihan_nav != st.session_state["hal_aktif"]:
    st.session_state["hal_aktif"] = pilihan_nav
    st.rerun()

st.write("")

# ==========================================================
# HALAMAN 0: BERANDA (PENGENALAN, DATA DASAR & TEMUAN KRITIS)
# ==========================================================
if st.session_state["hal_aktif"] == DAFTAR_HALAMAN[0]:
    c_intro1, c_intro2 = st.columns([1.35, 1], gap="large")

    with c_intro1:
        st.markdown(
            """
            <div class="card">
                <div class="badge-tag">Pengantar & Konteks Evaluasi</div>
                <div class="card-title">Mengapa Dashboard Ini Disusun?</div>
                <p class="justify-text">
                    Dokumen Laporan Akhir Inventarisasi dan Penurunan Emisi Gas Rumah Kaca (GRK) Provinsi DKI Jakarta 
                    memuat rangkaian data historis serta klaim capaian mitigasi lintas sektor yang sangat padat. Namun, 
                    pembacaan angka secara terpisah sering kali menyembunyikan dinamika struktural dan ketidakkonsistenan 
                    antarbab di dalam laporan tersebut. Dashboard ini dirancang untuk menerjemahkan data teknis inventarisasi 
                    GRK ke dalam bahasa yang mudah dipahami publik, sekaligus membedah temuan kritis dan anomali data sebagai 
                    bahan evaluasi perbaikan kebijakan iklim daerah.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="card-subtle">
                <div class="card-title">💡 Konsep Dasar: Apa Arti "Menurunkan Emisi dari Baseline"?</div>
                <p class="justify-text">
                    Dalam akuntansi gas rumah kaca, penurunan emisi tidak selalu berarti jumlah polusi udara tahun ini 
                    lebih rendah dibandingkan sepuluh tahun lalu. Penurunan emisi dihitung dengan membandingkan emisi 
                    aktual terhadap <b>Baseline (Business as Usual)</b>, yaitu perkiraan tingkat emisi seandainya pemerintah 
                    dan warga Jakarta tidak menjalankan program penghematan energi, tidak mengoperasikan transportasi massal, 
                    dan tidak mengganti bahan bakar pembangkit listrik sejak tahun dasar 2010. Selisih antara garis perkiraan 
                    tanpa program dan kondisi setelah adanya program itulah yang dilaporkan sebagai capaian reduksi emisi.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c_intro2:
        st.markdown(
            """
            <div class="card">
                <div class="badge-tag">Cakupan Data Utama</div>
                <div class="card-title">Empat Pilar Data yang Dianalisis</div>
                <ul class="justify-list">
                    <li><b>Deret Emisi Sektoral (2010–2026):</b> Mencakup lima kelompok sumber utama yakni Transportasi, Rumah Tangga, Komersial & Gedung, Industri & Pembangkit, serta Pengelolaan Limbah.</li>
                    <li><b>Evaluasi Reduksi Terhadap Baseline:</b> Menguji posisi capaian penurunan emisi sebesar 25,8 juta ton CO₂e (28,0% dari baseline) terhadap target 32,0% pada tahun 2030.</li>
                    <li><b>Kontribusi Aksi Mitigasi Utama:</b> Membedah sumbangan lima kelompok intervensi terbesar mulai dari PLTGU Muara Karang, sistem lalu lintas pintar (ITS), hingga efisiensi bangunan.</li>
                    <li><b>Peta Jalan Target Tahunan (Tabel 3):</b> Membandingkan lintasan rencana reduksi emisi tahun 2025–2030 per bidang terhadap realisasi capaian saat ini.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("#### Ringkasan Temuan Kritis & Anomali Data dalam Dokumen Laporan")
    t1, t2 = st.columns(2, gap="medium")
    with t1:
        st.markdown(
            """
            <div class="card">
                <div class="badge-tag">Temuan Anomali 1 • Proyeksi vs Realisasi</div>
                <div class="card-title">Emisi Aktual 2024 Sudah Melampaui Proyeksi CPOS 2035</div>
                <p class="justify-text">
                    Terdapat ketidaksinkronan antara tabel inventarisasi historis (Bab V) dan tabel pemodelan skenario 
                    jangka panjang (Bab VI). Sebagai contoh, pada subsektor Rumah Tangga, proyeksi kebijakan berjalan 
                    (<i>Current Policy Scenario</i>/CPOS) tahun 2035 dipatok sebesar 14,36 juta ton CO₂e (dengan acuan 
                    tahun 2019 sebesar 13,95 juta ton). Faktanya, data inventarisasi mencatat emisi aktual rumah tangga 
                    tahun 2024 telah mencapai 16,18 juta ton CO₂e, sehingga garis proyeksi jangka panjang memerlukan 
                    penyesuaian ulang (<i>re-baselining</i>)[cite: 361].
                </p>
            </div>
            <div class="card">
                <div class="badge-tag">Temuan Anomali 2 • Struktur Mitigasi</div>
                <div class="card-title">Capaian 25,8 Juta Ton Bertumpu pada Klaim Hulu, Bukan Penurunan Konsumsi</div>
                <p class="justify-text">
                    Meskipun capaian reduksi 2025 (25,8 juta ton CO₂e) telah melampaui rencana Tabel 3 tahun 2025 
                    (21,11 juta ton CO₂e), lebih dari 64% capaian tersebut disumbang oleh klaim peralihan bahan bakar 
                    pembangkit di hulu (PLTGU Muara Karang) dan pemodelan kelancaran lalu lintas (ITS). Sementara itu, 
                    volume konsumsi listrik bangunan dan BBM transportasi di tingkat hilir masih terus mengalami kenaikan.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with t2:
        st.markdown(
            """
            <div class="card">
                <div class="badge-tag">Temuan Anomali 3 • Parameter Teknis</div>
                <div class="card-title">Faktor Emisi Listrik Jamali Dipatok Konstan Selama 2019–2024</div>
                <p class="justify-text">
                    Pada Tabel 3.6 dokumen laporan, faktor emisi listrik jaringan interkoneksi Jawa-Madura-Bali (Jamali) 
                    untuk tahun 2020 hingga 2024 diasumsikan tidak berubah mengikuti angka tahun 2019 (0,800 tCO₂/MWh 
                    atau 0,903 tCO₂/MWh setelah koreksi susut transmisi)[cite: 361]. Karena lebih dari 53% emisi Jakarta 
                    berasal dari penggunaan listrik, asumsi konstan ini membuat dinamika dekarbonisasi jaringan PLN 
                    selama lima tahun terakhir tidak terbaca pada perhitungan emisi tidak langsung.
                </p>
            </div>
            <div class="card">
                <div class="badge-tag">Temuan Anomali 4 • Kualitas Deret Data</div>
                <div class="card-title">Lompatan Data Makroekonomi 2011 & Pembulatan Satuan Energi</div>
                <p class="justify-text">
                    Ditemukan anomali pada deret PDRB harga konstan tahun 2011 yang tercatat melonjak +16,7% lalu 
                    terkoreksi −3,0% pada 2012 (di luar pola normal 4–6% per tahun), serta angka penduduk tahun 2019 
                    dan 2020 yang tertulis identik (10,56 juta jiwa)[cite: 361]. Selain itu, grafik konsumsi energi 
                    dalam satuan Terajoule (TJ) hanya mencantumkan angka bulat tanpa tabel lampiran rincian.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("#### Pilih Bagian untuk Mulai Mengeksplorasi Data")
    b1, b2, b3, b4 = st.columns(4, gap="small")
    with b1:
        st.markdown(
            """
            <div class="card-subtle" style="min-height:135px;">
                <div class="card-title">1. Sudah sampai mana?</div>
                <p class="justify-text" style="font-size:0.83rem;">Evaluasi capaian reduksi 25,8 juta ton (28%) terhadap baseline dan jarak ke target 2030.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.button("Buka Bagian 1 →", on_click=pindah_ke, args=(DAFTAR_HALAMAN[1],), use_container_width=True)
    with b2:
        st.markdown(
            """
            <div class="card-subtle" style="min-height:135px;">
                <div class="card-title">2. Dari mana emisinya?</div>
                <p class="justify-text" style="font-size:0.83rem;">Eksplorasi komposisi emisi per sektor tahun 2010–2026 beserta dinamika kenaikan tahunannya.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.button("Buka Bagian 2 →", on_click=pindah_ke, args=(DAFTAR_HALAMAN[2],), use_container_width=True)
    with b3:
        st.markdown(
            """
            <div class="card-subtle" style="min-height:135px;">
                <div class="card-title">3. Apa yang dilakukan?</div>
                <p class="justify-text" style="font-size:0.83rem;">Bedah kontribusi per aksi mitigasi utama beserta temuan dan catatan verifikasinya.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.button("Buka Bagian 3 →", on_click=pindah_ke, args=(DAFTAR_HALAMAN[3],), use_container_width=True)
    with b4:
        st.markdown(
            """
            <div class="card-subtle" style="min-height:135px;">
                <div class="card-title">4. Mau ke mana?</div>
                <p class="justify-text" style="font-size:0.83rem;">Perbandingan jalur target Tabel 3 (2025–2030) dengan tabel interaktif pilihan per sektor.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.button("Buka Bagian 4 →", on_click=pindah_ke, args=(DAFTAR_HALAMAN[4],), use_container_width=True)


# ==========================================================
# HALAMAN 1: SUDAH SAMPAI MANA? (CAPAIAN VS TARGET)
# ==========================================================
elif st.session_state["hal_aktif"] == DAFTAR_HALAMAN[1]:
    st.subheader("1. Sudah sampai mana penurunan emisi Jakarta?")

    col_k1, col_k2 = st.columns([1, 1.3], gap="large")
    with col_k1:
        thn_eval = st.selectbox(
            "Pilih Tahun Evaluasi:",
            [2023, 2024, 2025, 2026],
            index=2,
            help="Pilih tahun untuk melihat perubahan posisi baseline, klaim reduksi, dan jarak ke target 32% (2030).",
        )
        koreksi_klaim = st.slider(
            "Uji Sensitivitas Verifikasi Klaim Reduksi (% dari klaim laporan):",
            50, 110, 100, step=5,
            help="Geser untuk menguji bagaimana posisi capaian Jakarta jika klaim reduksi hulu/lalu lintas diverifikasi ulang.",
        )

    baris_ev = df_evaluasi[df_evaluasi["Tahun"] == thn_eval].iloc[0]
    baseline_val = baris_ev["Baseline_JtTon"]
    reduksi_teruji = baris_ev["Reduksi_Klaim_JtTon"] * (koreksi_klaim / 100.0)
    persen_capai = (reduksi_teruji / baseline_val) * 100.0
    target_persen_2030 = 32.0
    target_jton_thn = baseline_val * (target_persen_2030 / 100.0)
    selisih_persen = target_persen_2030 - persen_capai
    emisi_setelah_mitigasi = baseline_val - reduksi_teruji

    with col_k2:
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(
                f"""
                <div class="card">
                    <div class="card-metric-label">Reduksi Emisi ({thn_eval})</div>
                    <div class="card-metric-val">{fmt_id(reduksi_teruji, 1)} Jt Ton</div>
                    <div class="card-metric-sub">Dari baseline {fmt_id(baseline_val, 1)} Jt Ton</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with m2:
            st.markdown(
                f"""
                <div class="card">
                    <div class="card-metric-label">Persentase terhadap Baseline</div>
                    <div class="card-metric-val">{fmt_id(persen_capai, 1)}%</div>
                    <div class="card-metric-sub">Asumsi verifikasi: {koreksi_klaim}%</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with m3:
            label_jarak = "Target Terlampaui" if selisih_persen <= 0 else f"Kurang {fmt_id(selisih_persen, 1)}% Lagi"
            st.markdown(
                f"""
                <div class="card">
                    <div class="card-metric-label">Jarak ke Target 2030 (32%)</div>
                    <div class="card-metric-val">{label_jarak}</div>
                    <div class="card-metric-sub">Setara {fmt_id(max(0.0, target_jton_thn - reduksi_teruji), 1)} Jt Ton CO₂e</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    rasio_bar = min(100.0, (persen_capai / target_persen_2030) * 100.0)
    st.markdown(
        f"""
        <div class="card-subtle">
            <div style="display:flex;justify-content:space-between;font-size:0.86rem;font-weight:600;color:#0F172A;">
                <span>Progres Ketercapaian Menuju Ambang Target 2030 (32,0% dari Baseline)</span>
                <span>{fmt_id(rasio_bar, 1)}% dari Target 2030 Tercapai</span>
            </div>
            <div class="prog-track">
                <div style="width:{rasio_bar:.1f}%;background:#1E3A5F;height:100%;"></div>
            </div>
            <div style="display:flex;justify-content:space-between;font-size:0.8rem;color:#475569;">
                <span>0% (Tanpa Pengurangan)</span>
                <span>Posisi {thn_eval}: {fmt_id(persen_capai, 1)}% ({fmt_id(reduksi_teruji, 1)} Juta Ton CO₂e)</span>
                <span>Target 2030: 32,0% ({fmt_id(target_jton_thn, 1)} Juta Ton CO₂e)</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cg1, cg2 = st.columns([1.3, 1], gap="large")
    with cg1:
        st.markdown(f"**Perbandingan Emisi Baseline, Emisi Setelah Mitigasi, dan Emisi Inventarisasi ({thn_eval})**")
        fig_b1 = go.Figure()
        kategori_x = ["1. Perkiraan Tanpa Program (Baseline)", "2. Setelah Dikurangi Klaim Mitigasi", "3. Emisi Inventarisasi Sektoral"]
        nilai_y = [baseline_val, emisi_setelah_mitigasi, baris_ev["Aktual_Inventaris_JtTon"]]
        warna_bar = [PALET["terang"], PALET["sekunder"], PALET["utama"]]
        fig_b1.add_trace(
            go.Bar(
                x=kategori_x,
                y=nilai_y,
                marker_color=warna_bar,
                text=[f"{fmt_id(v, 2)} Jt Ton" for v in nilai_y],
                textposition="outside",
                width=0.48,
            )
        )
        fig_b1 = tata_letak(fig_b1, "Juta Ton CO₂e", 330)
        fig_b1.update_layout(yaxis=dict(range=[0, max(nilai_y) * 1.18]))
        st.plotly_chart(fig_b1, use_container_width=True, config={"displayModeBar": False})

    with cg2:
        selisih_inv = abs(emisi_setelah_mitigasi - baris_ev["Aktual_Inventaris_JtTon"])
        st.markdown(
            f"""
            <div class="card">
                <div class="badge-tag">Temuan & Analisis Bagian 1</div>
                <div class="card-title">Evaluasi Posisi Reduksi Tahun {thn_eval}</div>
                <p class="justify-text" style="margin-bottom:10px;">
                    Pada tahun {thn_eval} (dengan asumsi verifikasi {koreksi_klaim}%), penurunan emisi tercatat sebesar 
                    <b>{fmt_id(reduksi_teruji, 1)} juta ton CO₂e</b> atau <b>{fmt_id(persen_capai, 1)}%</b> terhadap 
                    perkiraan baseline ({fmt_id(baseline_val, 1)} juta ton CO₂e). Angka ini menempatkan posisi Jakarta 
                    hanya berjarak <b>{fmt_id(max(0.0, selisih_persen), 1)} poin persentase</b> dari target 32,0% pada tahun 2030.
                </p>
                <p class="justify-text">
                    <b>Catatan Perbedaan Data:</b> Apabila nilai baseline ({fmt_id(baseline_val, 1)} juta ton) dikurangi 
                    dengan klaim reduksi ({fmt_id(reduksi_teruji, 1)} juta ton), maka tingkat emisi seharusnya berada di 
                    angka <b>{fmt_id(emisi_setelah_mitigasi, 2)} juta ton CO₂e</b>. Terdapat selisih sebesar 
                    <b>{fmt_id(selisih_inv, 2)} juta ton CO₂e</b> terhadap angka inventarisasi aktual sektoral 
                    ({fmt_id(baris_ev['Aktual_Inventaris_JtTon'], 2)} juta ton CO₂e) karena perhitungan klaim aksi mitigasi 
                    di Bab IV dan inventarisasi emisi di Bab V menggunakan ruang lingkup batas penghitungan yang terpisah.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ==========================================================
# HALAMAN 2: DARI MANA EMISI JAKARTA? (2010–2026)
# ==========================================================
elif st.session_state["hal_aktif"] == DAFTAR_HALAMAN[2]:
    st.subheader("2. Dari mana datangnya emisi gas rumah kaca di Jakarta? (2010–2026)")

    daftar_sektor = [
        "Transportasi",
        "Rumah Tangga",
        "Komersial & Gedung",
        "Industri & Pembangkit",
        "Limbah (Sampah & Air Limbah)",
    ]

    cs1, cs2 = st.columns([1.2, 1], gap="large")
    with cs1:
        thn_pilih = st.slider(
            "Geser untuk memilih tahun pengamatan (2010–2026):",
            min_value=2010,
            max_value=2026,
            value=2024,
            help="Data tahun 2010–2024 merupakan realisasi inventarisasi, sedangkan 2025–2026 memuat angka ekstensi terbaru.",
        )
    with cs2:
        pilih_sektor = st.selectbox("Pilih Sektor untuk Analisis Mendalam:", daftar_sektor)

    baris_now = df_sektor[df_sektor["Tahun"] == thn_pilih].iloc[0]
    baris_2010 = df_sektor[df_sektor["Tahun"] == 2010].iloc[0]
    baris_2020 = df_sektor[df_sektor["Tahun"] == 2020].iloc[0]
    baris_prev = df_sektor[df_sektor["Tahun"] == max(2010, thn_pilih - 1)].iloc[0]

    vals_now = [baris_now[s] for s in daftar_sektor]
    total_now = sum(vals_now)
    total_prev = sum([baris_prev[s] for s in daftar_sektor])

    # Perhitungan dinamika otomatis untuk sektor terpilih
    val_s_now = baris_now[pilih_sektor]
    val_s_prev = baris_prev[pilih_sektor]
    val_s_2010 = baris_2010[pilih_sektor]
    val_s_2020 = baris_2020[pilih_sektor]

    delta_yoy = val_s_now - val_s_prev
    persen_yoy = (delta_yoy / val_s_prev * 100.0) if thn_pilih > 2010 else 0.0
    delta_2010 = val_s_now - val_s_2010
    persen_2010 = (delta_2010 / val_s_2010) * 100.0
    pangsa_sektor = (val_s_now / total_now) * 100.0

    col_g1, col_g2 = st.columns([1.15, 1], gap="large")
    with col_g1:
        st.markdown(f"**Komposisi Emisi per Sektor Tahun {thn_pilih} (Total: {fmt_id(total_now, 2)} Juta Ton CO₂e)**")
        warna_bar_sek = [PALET["sekunder"] if s == pilih_sektor else "#CBD5E1" for s in daftar_sektor]
        fig_s1 = go.Figure(
            go.Bar(
                x=vals_now,
                y=daftar_sektor,
                orientation="h",
                marker_color=warna_bar_sek,
                text=[f"{fmt_id(v, 2)} Jt Ton ({v/total_now*100:.1f}%)" for v in vals_now],
                textposition="auto",
            )
        )
        fig_s1.update_layout(yaxis=dict(autorange="reversed"))
        st.plotly_chart(tata_letak(fig_s1, None, 290), use_container_width=True, config={"displayModeBar": False})

        st.markdown(f"**Lintasan Historis Sektor {pilih_sektor} (2010–2026)**")
        fig_s2 = go.Figure()
        fig_s2.add_trace(
            go.Scatter(
                x=df_sektor["Tahun"],
                y=df_sektor[pilih_sektor],
                mode="lines+markers",
                name=pilih_sektor,
                line=dict(color=PALET["sekunder"], width=2.5),
                marker=dict(
                    size=[11 if y == thn_pilih else 6 for y in df_sektor["Tahun"]],
                    color=[PALET["utama"] if y == thn_pilih else PALET["sekunder"] for y in df_sektor["Tahun"]],
                ),
            )
        )
        fig_s2 = tata_letak(fig_s2, "Juta Ton CO₂e", 240)
        fig_s2.update_xaxes(dtick=2)
        st.plotly_chart(fig_s2, use_container_width=True, config={"displayModeBar": False})

    with col_g2:
        temuan_sektor_map = {
            "Transportasi": (
                "Sektor transportasi merupakan penyumbang emisi terbesar di DKI Jakarta yang didorong oleh konsumsi "
                "bensin dan solar kendaraan darat. Temuan penting pada deret data ini adalah tajamnya kontraksi emisi "
                "pada tahun pandemi 2020 (turun ke 14,20 juta ton dari 20,30 juta ton pada 2019 akibat pembatasan "
                "mobilitas), namun segera memantul kembali (rebound) secara cepat pasca-2022 hingga melampaui "
                "level pra-pandemi pada tahun 2024–2026."
            ),
            "Rumah Tangga": (
                "Sektor rumah tangga menunjukkan perilaku anomali yang sangat berbeda dibandingkan sektor lainnya: "
                "ketika emisi sektor lain turun saat pandemi 2020, emisi rumah tangga justru naik dari 13,87 juta ton "
                "(2019) menjadi 14,40 juta ton (2020) dan terus tumbuh konsisten hingga 2024–2026. Sebesar 91,6% emisi "
                "sektor ini berasal dari emisi tidak langsung pemakaian listrik PLN (terutama pendingin ruangan/AC "
                "dan alat elektronik), sementara penduduk Jakarta hanya tumbuh 10,8% sepanjang 2010–2024[cite: 361]."
            ),
            "Komersial & Gedung": (
                "Emisi sektor komersial (perkantoran, pusat perbelanjaan, hotel, dan fasilitas publik) didominasi oleh "
                "konsumsi listrik untuk tata udara dan pencahayaan. Data memperlihatkan adanya penurunan dari 13,20 juta "
                "ton (2019) menjadi 11,80 juta ton (2020) saat kebijakan bekerja dari rumah diterapkan, yang berarti "
                "beban emisi listrik gedung perkantoran pada tahun tersebut berpindah ke sektor rumah tangga."
            ),
            "Industri & Pembangkit": (
                "Emisi industri manufaktur dan pembangkitan di wilayah Jakarta mengalami fluktuasi yang erat kaitannya "
                "dengan bauran bahan bakar pembangkit serta aktivitas pabrik. Setelah mencapai puncak pada 2013 dan "
                "2018 (11,80 juta ton), emisinya cenderung lebih terkendali di kisaran 10,50–11,05 juta ton seiring "
                "optimalisasi penggunaan gas bumi."
            ),
            "Limbah (Sampah & Air Limbah)": (
                "Berbeda dengan sektor energi yang berfluktuasi tajam mengikuti siklus ekonomi, emisi dari timbunan "
                "sampah padat dan pengolahan air limbah tumbuh secara lambat namun sangat kaku (inelastic) dari "
                "2,90 juta ton (2010) menjadi 3,65–3,70 juta ton CO₂e karena mengikuti pertambahan timbulan sampah "
                "domestik harian penduduk."
            ),
        }

        kalimat_yoy = (
            f"Dari tahun <b>{thn_pilih - 1}</b> ke <b>{thn_pilih}</b>, emisi sektor <b>{pilih_sektor}</b> berubah dari "
            f"<b>{fmt_id(val_s_prev, 2)} juta ton</b> menjadi <b>{fmt_id(val_s_now, 2)} juta ton CO₂e</b> "
            f"(<b>{fmt_tanda(delta_yoy, 2)} juta ton</b> atau <b>{fmt_tanda(persen_yoy, 1)}%</b>)."
            if thn_pilih > 2010
            else f"Tahun <b>2010</b> merupakan tahun dasar pencatatan dengan tingkat emisi sebesar <b>{fmt_id(val_s_now, 2)} juta ton CO₂e</b>."
        )

        st.markdown(
            f"""
            <div class="card">
                <div class="badge-tag">Analisis Dinamis Sektor • Tahun {thn_pilih}</div>
                <div class="card-title">{pilih_sektor} — {fmt_id(val_s_now, 2)} Juta Ton CO₂e ({fmt_id(pangsa_sektor, 1)}% Total DKI)</div>
                <ul class="justify-list" style="margin-bottom:12px;">
                    <li><b>Perubahan Tahunan (YoY):</b> {kalimat_yoy}</li>
                    <li><b>Akumulasi Sejak 2010:</b> Dibandingkan tahun dasar 2010 ({fmt_id(val_s_2010, 2)} juta ton), emisi sektor ini pada {thn_pilih} telah berubah sebesar <b>{fmt_tanda(delta_2010, 2)} juta ton CO₂e ({fmt_tanda(persen_2010, 1)}%)</b>.</li>
                    <li><b>Posisi Terhadap Tahun Pandemi (2020):</b> Saat pandemi 2020, emisi sektor ini berada di angka <b>{fmt_id(val_s_2020, 2)} juta ton</b>, sehingga terdapat selisih <b>{fmt_tanda(val_s_now - val_s_2020, 2)} juta ton CO₂e</b> pada tahun {thn_pilih}.</li>
                </ul>
                <div class="card-title" style="margin-top:10px;">Temuan Karakteristik & Anomali Sektor</div>
                <p class="justify-text">{temuan_sektor_map[pilih_sektor]}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ==========================================================
# HALAMAN 3: APA YANG SUDAH DILAKUKAN? (EVALUASI AKSI)
# ==========================================================
elif st.session_state["hal_aktif"] == DAFTAR_HALAMAN[3]:
    st.subheader("3. Apa yang sudah dilakukan dan mana yang paling berdampak?")

    pilihan_aksi = st.selectbox(
        "Pilih Kelompok Aksi Mitigasi untuk Melihat Temuan & Evaluasinya:",
        df_aksi["Aksi"],
    )
    detail_aksi = df_aksi[df_aksi["Aksi"] == pilihan_aksi].iloc[0]

    ca1, ca2 = st.columns([1.15, 1], gap="large")
    with ca1:
        st.markdown("**Kontribusi Penurunan Emisi per Kelompok Aksi Utama (Total: 25,80 Juta Ton CO₂e)**")
        warna_aksi = [PALET["sekunder"] if a == pilihan_aksi else "#CBD5E1" for a in df_aksi["Aksi"]]
        fig_a = go.Figure(
            go.Bar(
                x=df_aksi["Reduksi_JutaTon"],
                y=df_aksi["Aksi"],
                orientation="h",
                marker_color=warna_aksi,
                text=[f"{fmt_id(v, 2)} Jt Ton ({v/25.8*100:.1f}%)" for v in df_aksi["Reduksi_JutaTon"]],
                textposition="auto",
            )
        )
        fig_a.update_layout(yaxis=dict(autorange="reversed"))
        st.plotly_chart(tata_letak(fig_a, None, 350), use_container_width=True, config={"displayModeBar": False})

        st.markdown(
            """
            <div class="card-subtle">
                <div class="card-title">Ringkasan Struktur Aksi Mitigasi DKI Jakarta</div>
                <p class="justify-text">
                    Grafik di atas memperlihatkan distribusi capaian penurunan emisi yang sangat timpang (<i>skewed</i>). 
                    Dua kelompok aksi teratas—yakni pembangkit listrik bersih (11,45 juta ton) dan manajemen lalu lintas 
                    ITS (5,12 juta ton)—menyumbang <b>64,2%</b> dari seluruh klaim pengurangan emisi Jakarta. Sebaliknya, 
                    intervensi yang menyentuh langsung perubahan peralatan dan perilaku warga di rumah tangga, gedung, 
                    angkutan umum, serta pengelolaan sampah secara gabungan menyumbang 35,8% sisanya.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with ca2:
        porsi_a = (detail_aksi["Reduksi_JutaTon"] / 25.8) * 100.0
        st.markdown(
            f"""
            <div class="card">
                <div class="badge-tag">Bidang: {detail_aksi['Sektor']}</div>
                <div class="card-title" style="font-size:1.08rem;">{detail_aksi['Aksi']}</div>
                <div style="display:flex;gap:24px;margin:10px 0 14px 0;padding:10px 14px;background:#F8FAFC;border-radius:8px;border:1px solid #E2E8F0;">
                    <div>
                        <div class="card-metric-label">Volume Reduksi</div>
                        <div style="font-size:1.3rem;font-weight:700;color:#0F172A;">{fmt_id(detail_aksi['Reduksi_JutaTon'], 2)} Jt Ton CO₂e</div>
                    </div>
                    <div>
                        <div class="card-metric-label">Porsi terhadap Total Capaian</div>
                        <div style="font-size:1.3rem;font-weight:700;color:#1E3A5F;">{fmt_id(porsi_a, 1)}%</div>
                    </div>
                </div>
                <div class="card-title">Perkembangan & Mekanisme Kontribusi</div>
                <p class="justify-text" style="margin-bottom:14px;">{detail_aksi['Perkembangan']}</p>
                <div class="card-title">Temuan Kritis & Catatan Anomali Data</div>
                <p class="justify-text">{detail_aksi['Temuan_Anomali']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ==========================================================
# HALAMAN 4: MAU KE MANA? (JALUR TARGET 2025–2030)
# ==========================================================
elif st.session_state["hal_aktif"] == DAFTAR_HALAMAN[4]:
    st.subheader("4. Mau ke mana? Evaluasi jalur target reduksi emisi 2025–2030")

    opsi_sektor_tabel = [
        "Energi & Transportasi",
        "Pembangkit Listrik",
        "Pengelolaan Limbah & RTH",
    ]

    col_j1, col_j2 = st.columns([1.22, 1], gap="large")

    with col_j1:
        st.markdown("**Perbandingan Jalur Target Tabel 3 (2025–2030) dengan Posisi Capaian 25,8 Juta Ton CO₂e**")
        fig_j = go.Figure()
        fig_j.add_trace(
            go.Bar(
                x=df_jalur["Tahun"],
                y=df_jalur["Energi & Transportasi"],
                name="Energi & Transportasi",
                marker_color="#1E3A5F",
            )
        )
        fig_j.add_trace(
            go.Bar(
                x=df_jalur["Tahun"],
                y=df_jalur["Pembangkit Listrik"],
                name="Pembangkit Listrik",
                marker_color="#64748B",
            )
        )
        fig_j.add_trace(
            go.Bar(
                x=df_jalur["Tahun"],
                y=df_jalur["Pengelolaan Limbah & RTH"],
                name="Pengelolaan Limbah & RTH",
                marker_color="#CBD5E1",
            )
        )
        fig_j.add_trace(
            go.Scatter(
                x=df_jalur["Tahun"],
                y=[25.8] * len(df_jalur),
                name="Capaian Saat Ini (25,80 Jt Ton)",
                mode="lines",
                line=dict(color="#0F172A", width=2.5, dash="dash"),
            )
        )
        fig_j.update_layout(barmode="stack")
        fig_j.update_xaxes(dtick=1)
        st.plotly_chart(tata_letak(fig_j, "Juta Ton CO₂e", 330), use_container_width=True, config={"displayModeBar": False})

        st.markdown(
            """
            <div class="card">
                <div class="badge-tag">Temuan Evaluasi Peta Jalan 2025–2030</div>
                <div class="card-title">Apa yang Harus Dikejar dan Diperbaiki Menuju 2030?</div>
                <ul class="justify-list">
                    <li><b>Anomali Target Tabel 3 vs Realisasi 2025:</b> Dalam Tabel 3 dokumen laporan, total target reduksi emisi tahun 2025 direncanakan sebesar 21,11 juta ton CO₂e, padahal realisasi kumulatif yang dilaporkan untuk tahun 2025 sudah mencapai 25,80 juta ton CO₂e (setara dengan target rencana tahun 2027 sebesar 26,17 juta ton). Hal ini mengindikasikan bahwa jadwal target pada Tabel 3 disusun menggunakan asumsi historis lama sebelum masuknya klaim reduksi penuh dari PLTGU dan ITS.</li>
                    <li><b>Pergeseran Beban Kerja Menuju 2030 (34,09 Juta Ton):</b> Sepanjang 2025 hingga 2030, target reduksi dari pembangkit listrik hampir tidak bertambah (hanya naik dari 8,47 menjadi 9,17 juta ton). Artinya, tambahan target reduksi sebesar 12,98 juta ton CO₂e antara 2025 dan 2030 ditumpukan sepenuhnya pada sektor hilir, yakni efisiensi energi bangunan, transportasi, dan pengolahan limbah.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_j2:
        st.markdown("**Tabel Target Tahunan per Sektor (2025–2030)**")
        sektor_tabel_pilih = st.selectbox(
            "Pilih Sektor yang Ditampilkan pada Tabel:",
            opsi_sektor_tabel,
            index=0,
        )

        # Menyusun tabel ringkas tepat 3 kolom sesuai permintaan
        df_tiga_kolom = pd.DataFrame({
            "Tahun": df_jalur["Tahun"].astype(str),
            f"{sektor_tabel_pilih} (Jt Ton)": df_jalur[sektor_tabel_pilih].map(lambda v: fmt_id(v, 2)),
            "Total Target (Jt Ton)": df_jalur["Total Target (Jt Ton)"].map(lambda v: fmt_id(v, 2)),
        })
        st.dataframe(df_tiga_kolom, hide_index=True, use_container_width=True)

        awal_25 = df_jalur[sektor_tabel_pilih].iloc[0]
        akhir_30 = df_jalur[sektor_tabel_pilih].iloc[-1]
        naik_jt = akhir_30 - awal_25
        naik_pct = (naik_jt / awal_25) * 100.0
        porsi_25 = (awal_25 / df_jalur["Total Target (Jt Ton)"].iloc[0]) * 100.0
        porsi_30 = (akhir_30 / df_jalur["Total Target (Jt Ton)"].iloc[-1]) * 100.0

        catatan_sektor_jalur = {
            "Energi & Transportasi": (
                "Bidang energi final (mencakup transportasi, rumah tangga, gedung komersial, dan industri) menjadi "
                "tumpuan utama peningkatan target DKI Jakarta. Target reduksinya wajib ditingkatkan hampir dua kali "
                "lipat dalam lima tahun, terutama melalui perluasan pelabelan peralatan rumah tangga (dari 2,44 juta "
                "ton di 2025 menjadi 3,63 juta ton di 2030) serta peralihan angkutan umum dan kendaraan listrik."
            ),
            "Pembangkit Listrik": (
                "Target reduksi subsektor pembangkit listrik mengalami saturasi (mendatar) karena kapasitas konversi "
                "gas bumi pada unit pembangkit eksisting di Jakarta sudah mendekati batas maksimum. Tanpa tambahan "
                "kuota energi terbarukan lintas provinsi pada jaringan Jamali, subsektor ini tidak lagi menjadi "
                "pendorong pertambahan reduksi baru hingga 2030."
            ),
            "Pengelolaan Limbah & RTH": (
                "Meskipun porsinya terhadap total target masih di bawah 5%, bidang ini memiliki laju kenaikan target "
                "persentase paling agresif (+257,8% dari 2025 ke 2030). Kenaikan ini sepenuhnya bertumpu pada rencana "
                "pengurangan sampah di sumber dan fasilitas pengolahan sampah baru, sementara target serapan karbon "
                "RTH justru menyusut dari 29 ribu ton menjadi 16 ribu ton CO₂e."
            ),
        }

        st.markdown(
            f"""
            <div class="card-subtle" style="margin-top:12px;">
                <div class="badge-tag">Sorotan Sektor Terpilih • 2025–2030</div>
                <div class="card-title">{sektor_tabel_pilih}</div>
                <p class="justify-text" style="margin-bottom:8px;">
                    Target pengurangan emisi pada kelompok <b>{sektor_tabel_pilih}</b> meningkat dari 
                    <b>{fmt_id(awal_25, 2)} juta ton CO₂e</b> pada 2025 ({fmt_id(porsi_25, 1)}% dari total target) menjadi 
                    <b>{fmt_id(akhir_30, 2)} juta ton CO₂e</b> pada 2030 ({fmt_id(porsi_30, 1)}% dari total target), 
                    atau bertambah sebesar <b>{fmt_tanda(naik_jt, 2)} juta ton ({fmt_tanda(naik_pct, 1)}%)</b>.
                </p>
                <p class="justify-text">{catatan_sektor_jalur[sektor_tabel_pilih]}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
