import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- CONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="BTC Warehouse System - Palembang",
    page_icon="🏢",
    layout="wide"
)

# --- DATABASE SETUP ---
conn = sqlite3.connect('gudang_palembang.db', check_same_thread=False)
c = conn.cursor()

# Tabel Master Barang
c.execute('''
    CREATE TABLE IF NOT EXISTS barang (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        kode_barang TEXT UNIQUE,
        nama_barang TEXT,
        kategori TEXT,
        stok INTEGER,
        harga INTEGER,
        lokasi TEXT,
        pemasok TEXT
    )
''')

# Tabel Riwayat Transaksi
c.execute('''
    CREATE TABLE IF NOT EXISTS riwayat (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tanggal TEXT,
        kode_barang TEXT,
        nama_barang TEXT,
        jenis TEXT,
        jumlah INTEGER,
        keterangan TEXT,
        operator TEXT
    )
''')
conn.commit()

# --- FUNGSI HELPER DATABASE ---
def get_all_barang():
    return pd.read_sql_query("SELECT * FROM barang", conn)

def get_all_riwayat():
    return pd.read_sql_query("SELECT * FROM riwayat ORDER BY id DESC", conn)

# --- INI SISTEM SESSION & LOGIN ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['role'] = ''
    st.session_state['user'] = ''

if not st.session_state['logged_in']:
    st.title("🔐 BTC WAREHOUSE PALEMBANG - LOGIN")
    st.markdown("---")
    
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        st.subheader("Masuk ke Sistem Gudang")
        username = st.text_input("Username (Contoh: reza/admin)")
        password = st.text_input("Password", type="password")
        role = st.selectbox("Akses Hak Pengguna", ["Admin Gudang", "Staf Lapangan"])
        
        if st.button("🚀 Masuk Sistem", use_container_width=True):
            if username and password:
                st.session_state['logged_in'] = True
                st.session_state['role'] = role
                st.session_state['user'] = username
                st.success(f"Selamat datang, {username}! Hak Akses: {role}")
                st.rerun()
            else:
                st.error("Masukkan Username dan Password terlebih dahulu!")
    st.stop()

# --- SIDEBAR NAVIGASI UTAMA ---
st.sidebar.title("🏢 BTC WAREHOUSE")
st.sidebar.caption("Sistem Gudang Terpadu Palembang")
st.sidebar.info(f"👤 **Operator:** {st.session_state['user']}\n🔰 **Role:** {st.session_state['role']}")

if st.sidebar.button("🚪 Keluar (Logout)", use_container_width=True):
    st.session_state['logged_in'] = False
    st.rerun()

st.sidebar.markdown("---")

menu_options = [
    "📊 Dashboard Analytics", 
    "🗃️ Master Data & Edit Barang", 
    "📥 Transaksi Barang Masuk/Keluar", 
    "📜 Cetak Surat Jalan & Riwayat",
    "📤 Bulk Import & Export Excel"
]

menu = st.sidebar.radio("Pilih Menu Operational:", menu_options)

# ==========================================
# 1. DASHBOARD ANALYTICS & MONITORING
# ==========================================
if menu == "📊 Dashboard Analytics":
    st.title("📊 Dashboard Analytics & Live Monitoring")
    st.caption("Pusat Kontrol Stok Barang BTC Warehouse Palembang")
    st.markdown("---")
    
    df_barang = get_all_barang()
    
    if not df_barang.empty:
        total_jenis = len(df_barang)
        total_stok = df_barang['stok'].sum()
        total_nilai = (df_barang['stok'] * df_barang['harga']).sum()
        stok_kritis = len(df_barang[df_barang['stok'] <= 5])
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Jenis Barang", f"{total_jenis} SKU")
        c2.metric("Total Kuantitas Stok", f"{total_stok:,.0f} Pcs")
        c3.metric("Aset Inventaris Gudang", f"Rp {total_nilai:,.0f}")
        c4.metric("Stok Kritis (<= 5)", f"{stok_kritis} Item", delta_color="inverse")
        
        st.markdown("---")
        
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.subheader("📦 Top 10 Stok Barang Terbanyak")
            fig_stok = px.bar(
                df_barang.nlargest(10, 'stok'), 
                x='nama_barang', y='stok', 
                color='kategori', text='stok',
                labels={'nama_barang':'Nama Barang', 'stok':'Jumlah Stok'}
            )
            st.plotly_chart(fig_stok, use_container_width=True)
            
        with col_g2:
            st.subheader("🏷️ Persentase Stok per Kategori")
            fig_pie = px.pie(df_barang, names='kategori', values='stok', hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)
            
        # Peringatan Stok Kritis
        if stok_kritis > 0:
            st.error("⚠️ **PERHATIAN: Barang berikut dalam kondisi kritis / menipis!**")
            st.dataframe(
                df_barang[df_barang['stok'] <= 5][['kode_barang', 'nama_barang', 'stok', 'lokasi', 'pemasok']], 
                use_container_width=True
            )
    else:
        st.info("Database gudang masih kosong. Tambahkan data di menu Master Data.")

# ==========================================
# 2. MASTER DATA (EDIT, HAPUS, EDITABLE TABLE)
# ==========================================
elif menu == "🗃️ Master Data & Edit Barang":
    st.title("🗃️ Pengelolaan Master Data Barang")
    
    tab1, tab2, tab3 = st.tabs(["⚡ Editable Data Table (Excel Mode)", "➕ Tambah Barang Baru", "❌ Hapus / Edit Spesifik"])
    
    # TAB 1: EDITABLE TABLE
    with tab1:
        st.subheader("Edit Langsung Tabel Data Gudang")
        st.info("💡 **Tips:** Klik kolom pada tabel untuk merubah nilai secara instan, lalu klik **Simpan Perubahan**.")
        
        df_barang = get_all_barang()
        edited_df = st.data_editor(
            df_barang, 
            num_rows="dynamic",
            use_container_width=True,
            key="editor_gudang_master"
        )
        
        if st.button("💾 Simpan Semua Perubahan Tabel", use_container_width=True):
            edited_df.to_sql('barang', conn, if_exists='replace', index=False)
            st.success("Seluruh data di database berhasil diperbarui!")
            st.rerun()

    # TAB 2: FORM TAMBAH
    with tab2:
        st.subheader("Form Input Master Barang Baru")
        with st.form("form_tambah_master", clear_on_submit=True):
            f1, f2 = st.columns(2)
            kode = f1.text_input("Kode / Barcode Barang (Unik)*", placeholder="Contoh: BRG-PLM-001")
            nama = f2.text_input("Nama Barang*", placeholder="Contoh: Semen Gresik 50kg")
            
            f3, f4, f5 = st.columns(3)
            kategori = f3.selectbox("Kategori Barang", ["Material/Konstruksi", "Elektronik", "Suku Cadang", "Sembako", "Perkakas", "Lainnya"])
            lokasi = f4.text_input("Lokasi Rak / Blok", placeholder="A-01-B")
            pemasok = f5.text_input("Pemasok / Supplier", placeholder="PT. Distributor Utama")
            
            f6, f7 = st.columns(2)
            stok = f6.number_input("Jumlah Stok Awal", min_value=0, value=10)
            harga = f7.number_input("Harga Satuan (Rp)", min_value=0, value=50000)
            
            if st.form_submit_button("💾 Simpan Barang Baru", use_container_width=True):
                if kode and nama:
                    try:
                        c.execute(
                            "INSERT INTO barang (kode_barang, nama_barang, kategori, stok, harga, lokasi, pemasok) VALUES (?, ?, ?, ?, ?, ?, ?)",
                            (kode, nama, kategori, stok, harga, lokasi, pemasok)
                        )
                        conn.commit()
                        st.success(f"Berhasil menambahkan {nama} ke database!")
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("Gagal! Kode Barang sudah terdaftar di database.")
                else:
                    st.error("Kode Barang dan Nama Barang wajib diisi!")

    # TAB 3: HAPUS / EDIT SPESIFIK
    with tab3:
        st.subheader("Hapus Data Barang dari Database")
        df_barang = get_all_barang()
        if not df_barang.empty:
            item_delete = st.selectbox("Pilih Barang yang Akan Dihapus:", df_barang['kode_barang'] + " - " + df_barang['nama_barang'])
            kode_del = item_delete.split(" - ")[0]
            
            if st.button("🗑️ Hapus Barang Ini Permanen", type="primary"):
                c.execute("DELETE FROM barang WHERE kode_barang = ?", (kode_del,))
                conn.commit()
                st.warning(f"Barang {item_delete} berhasil dihapus dari database!")
                st.rerun()
        else:
            st.info("Tidak ada data barang untuk dihapus.")

# ==========================================
# 3. TRANSAKSI BARANG MASUK / KELUAR
# ==========================================
elif menu == "📥 Transaksi Barang Masuk/Keluar":
    st.title("📥 Transaksi Stok In / Out")
    
    df_barang = get_all_barang()
    
    if not df_barang.empty:
        # Search & Selection
        search_kw = st.text_input("🔍 Cari Barang (Kode / Nama):")
        filtered_df = df_barang[
            df_barang['nama_barang'].str.contains(search_kw, case=False) | 
            df_barang['kode_barang'].str.contains(search_kw, case=False)
        ] if search_kw else df_barang
        
        if not filtered_df.empty:
            list_item = filtered_df['kode_barang'] + " - " + filtered_df['nama_barang']
            selected_item = st.selectbox("Pilih Barang Hasil Pencarian:", list_item)
            kode_sel = selected_item.split(" - ")[0]
            
            row_curr = df_barang[df_barang['kode_barang'] == kode_sel].iloc[0]
            
            # Info Card
            st.info(f"📌 **Detail Barang:** {row_curr['nama_barang']} | **Stok Saat Ini:** {row_curr['stok']} Pcs | **Lokasi:** {row_curr['lokasi']}")
            
            t1, t2 = st.columns(2)
            jenis_tx = t1.radio("Jenis Pergerakan Stok:", ["Barang Masuk (Restok +)", "Barang Keluar (Pengiriman -)"])
            jumlah_tx = t2.number_input("Jumlah (Pcs)", min_value=1, value=1)
            ket_tx = st.text_area("Keterangan / Nomor DO / PO:", "Nomor PO: " if "Masuk" in jenis_tx else "Nomor Surat Jalan: ")
            
            if st.button("⚡ Diproses & Perbarui Database", use_container_width=True):
                tgl_skrg = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                stok_lama = row_curr['stok']
                operator_nama = st.session_state['user']
                
                if "Masuk" in jenis_tx:
                    stok_baru = stok_lama + jumlah_tx
                    c.execute("UPDATE barang SET stok = ? WHERE kode_barang = ?", (stok_baru, kode_sel))
                    c.execute(
                        "INSERT INTO riwayat (tanggal, kode_barang, nama_barang, jenis, jumlah, keterangan, operator) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (tgl_skrg, kode_sel, row_curr['nama_barang'], "MASUK", jumlah_tx, ket_tx, operator_nama)
                    )
                    conn.commit()
                    st.success(f"Transaksi Masuk Berhasil! Stok diperbarui dari {stok_lama} ➔ {stok_baru} Pcs.")
                    st.rerun()
                else:
                    if jumlah_tx > stok_lama:
                        st.error("Gagal! Kuantitas barang keluar melebihi stok yang tersedia saat ini.")
                    else:
                        stok_baru = stok_lama - jumlah_tx
                        c.execute("UPDATE barang SET stok = ? WHERE kode_barang = ?", (stok_baru, kode_sel))
                        c.execute(
                            "INSERT INTO riwayat (tanggal, kode_barang, nama_barang, jenis, jumlah, keterangan, operator) VALUES (?, ?, ?, ?, ?, ?, ?)",
                            (tgl_skrg, kode_sel, row_curr['nama_barang'], "KELUAR", jumlah_tx, ket_tx, operator_nama)
                        )
                        conn.commit()
                        st.success(f"Transaksi Keluar Berhasil! Stok berkurang dari {stok_lama} ➔ {stok_baru} Pcs.")
                        st.rerun()
        else:
            st.warning("Barang tidak ditemukan berdasarkan pencarian Anda.")
    else:
        st.info("Master data barang masih kosong.")

# ==========================================
# 4. CETAK SURAT JALAN & RIWAYAT
# ==========================================
elif menu == "📜 Cetak Surat Jalan & Riwayat":
    st.title("📜 Riwayat Transaksi & Generator Surat Jalan")
    
    df_riwayat = get_all_riwayat()
    
    if not df_riwayat.empty:
        tab_r1, tab_r2 = st.tabs(["📋 Tabel Riwayat Transaksi", "🖨️ Cetak Bukti / Surat Jalan"])
        
        with tab_r1:
            st.dataframe(df_riwayat, use_container_width=True)
            
        with tab_r2:
            st.subheader("Cetak Bukti Transaksi Resmi")
            id_trans = st.selectbox("Pilih ID Transaksi Terbaru:", df_riwayat['id'].astype(str) + " - " + df_riwayat['jenis'] + " - " + df_riwayat['nama_barang'])
            id_selected = int(id_trans.split(" - ")[0])
            
            row_r = df_riwayat[df_riwayat['id'] == id_selected].iloc[0]
            
            # Format Bukti Surat Jalan
            surat_jalan_text = f"""
=====================================================
            BTC WAREHOUSE PALEMBANG
       BUKTI TRANSAKSI GUDANG RESMI (SURAT JALAN)
=====================================================
ID Transaksi : TX-{row_r['id']:05d}
Tanggal      : {row_r['tanggal']}
Jenis        : {row_r['jenis']}
-----------------------------------------------------
Kode Barang  : {row_r['kode_barang']}
Nama Barang  : {row_r['nama_barang']}
Kuantitas    : {row_r['jumlah']} Pcs
Keterangan   : {row_r['keterangan']}
-----------------------------------------------------
Operator     : {row_r['operator']}
=====================================================
  Terima Kasih atas Kerja Samanya - BTC Warehouse
=====================================================
            """
            
            st.code(surat_jalan_text, language="text")
            
            st.download_button(
                label="📄 Download Surat Jalan (.txt)",
                data=surat_jalan_text,
                file_name=f"Surat_Jalan_TX{row_r['id']:05d}.txt",
                mime="text/plain"
            )
    else:
        st.info("Belum ada riwayat transaksi recorded.")

# ==========================================
# 5. IMPORT / EXPORT MASSAL EXCEL
# ==========================================
elif menu == "📤 Bulk Import & Export Excel":
    st.title("📤 Mass Import & Backup Data CSV/Excel")
    
    col_e1, col_e2 = st.columns(2)
    
    with col_e1:
        st.subheader("📥 Export / Backup Data")
        df_b = get_all_barang()
        if not df_b.empty:
            csv_data = df_b.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Seluruh Data Barang (CSV)",
                data=csv_data,
                file_name=f"Backup_Gudang_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
            
    with col_e2:
        st.subheader("📤 Upload / Bulk Import Data")
        uploaded_file = st.file_uploader("Unggah File Data Gudang (Format CSV)", type=["csv"])
        
        if uploaded_file is not None:
            try:
                df_up = pd.read_csv(uploaded_file)
                st.write("Preview Data Import:")
                st.dataframe(df_up, use_container_width=True)
                
                if st.button("🚀 Upload & Masukkan ke Database", use_container_width=True):
                    df_up.to_sql('barang', conn, if_exists='append', index=False)
                    st.success("Import Data Berhasil Disimpan!")
                    st.rerun()
            except Exception as e:
                st.error(f"Error memproses file CSV: {e}")
