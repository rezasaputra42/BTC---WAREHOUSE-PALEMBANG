import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- CONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Sistem Gudang Interaktif",
    page_icon="📦",
    layout="wide"
)

# --- DATABASE SETUP ---
conn = sqlite3.connect('gudang.db', check_same_thread=False)
c = conn.cursor()

c.execute('''
    CREATE TABLE IF NOT EXISTS barang (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        kode_barang TEXT UNIQUE,
        nama_barang TEXT,
        kategori TEXT,
        stok INTEGER,
        harga INTEGER,
        lokasi TEXT
    )
''')

c.execute('''
    CREATE TABLE IF NOT EXISTS riwayat (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tanggal TEXT,
        kode_barang TEXT,
        jenis TEXT,
        jumlah INTEGER,
        keterangan TEXT,
        operator TEXT
    )
''')
conn.commit()

# --- FUNGSI HELPER ---
def get_all_barang():
    return pd.read_sql_query("SELECT * FROM barang", conn)

def get_all_riwayat():
    return pd.read_sql_query("SELECT * FROM riwayat ORDER BY id DESC", conn)

# --- SISTEM LOGIN SERDERHANA ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['role'] = ''
    st.session_state['user'] = ''

if not st.session_state['logged_in']:
    st.title("🔐 Login Sistem Gudang")
    st.markdown("---")
    
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        role = st.selectbox("Akses Sebagai", ["Admin", "Staf Gudang"])
        
        if st.button("Login", use_container_width=True):
            if username and password:
                st.session_state['logged_in'] = True
                st.session_state['role'] = role
                st.session_state['user'] = username
                st.success(f"Selamat datang, {username} ({role})!")
                st.rerun()
            else:
                st.error("Isi Username dan Password dengan benar!")
    st.stop()

# --- SIDEBAR & AKUN USER ---
st.sidebar.title("📦 Navigation Gudang")
st.sidebar.info(f"👤 **User:** {st.session_state['user']} ({st.session_state['role']})")

if st.sidebar.button("🚪 Logout"):
    st.session_state['logged_in'] = False
    st.rerun()

st.sidebar.markdown("---")

menu_options = ["📊 Dashboard", "🗃️ Master Data (Interactive Table)", "📥 Barang Masuk & Keluar", "📜 Riwayat Transaksi"]
if st.session_state['role'] == "Admin":
    menu_options.append("📤 Import Data Excel/CSV")

menu = st.sidebar.radio("Pilih Menu:", menu_options)

# ==========================================
# 1. MENU DASHBOARD
# ==========================================
if menu == "📊 Dashboard":
    st.title("📊 Dashboard Analytics Gudang")
    st.markdown("---")
    
    df_barang = get_all_barang()
    
    if not df_barang.empty:
        total_jenis = len(df_barang)
        total_stok = df_barang['stok'].sum()
        total_nilai = (df_barang['stok'] * df_barang['harga']).sum()
        stok_menipis = len(df_barang[df_barang['stok'] <= 5])
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Jenis Barang", f"{total_jenis} Item")
        col2.metric("Total Seluruh Stok", f"{total_stok} Pcs")
        col3.metric("Nilai Total Inventaris", f"Rp {total_nilai:,.0f}")
        col4.metric("Stok Menipis (<= 5)", f"{stok_menipis} Item")
        
        st.markdown("---")
        
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.subheader("📦 Top 10 Stok Barang Terbanyak")
            fig_stok = px.bar(df_barang.nlargest(10, 'stok'), x='nama_barang', y='stok', color='kategori', text='stok')
            st.plotly_chart(fig_stok, use_container_width=True)
            
        with col_c2:
            st.subheader("🏷️ Distribusi Kategori Barang")
            fig_kat = px.pie(df_barang, names='kategori', values='stok', hole=0.4)
            st.plotly_chart(fig_kat, use_container_width=True)
            
        if stok_menipis > 0:
            st.warning("⚠️ **Perhatian:** Barang berikut membutuhkan restok segera!")
            st.dataframe(df_barang[df_barang['stok'] <= 5][['kode_barang', 'nama_barang', 'stok', 'lokasi']], use_container_width=True)
    else:
        st.info("Database gudang masih kosong. Tambah data terlebih dahulu!")

# ==========================================
# 2. MENU MASTER DATA (TABEL INTERAKTIF)
# ==========================================
elif menu == "🗃️ Master Data (Interactive Table)":
    st.title("🗃️ Kelola Data Gudang")
    st.info("💡 **Fitur Interaktif:** Klik dan ubah data langsung di dalam tabel seperti Microsoft Excel, lalu tekan tombol **Simpan Perubahan**!")
    
    tab_a, tab_b = st.tabs(["⚡ Editable Data Table", "➕ Form Tambah Manual"])
    
    with tab_a:
        df_barang = get_all_barang()
        
        # Tabel Interaktif yang Bisa Langsung Di-edit
        edited_df = st.data_editor(
            df_barang, 
            num_rows="dynamic",
            use_container_width=True,
            key="editor_gudang",
            disabled=[] if st.session_state['role'] == 'Admin' else ['kode_barang']
        )
        
        col_btn1, col_btn2 = st.columns([1, 4])
        with col_btn1:
            if st.button("💾 Simpan Perubahan", use_container_width=True):
                edited_df.to_sql('barang', conn, if_exists='replace', index=False)
                st.success("Database berhasil diperbarui!")
                st.rerun()
                
        with col_btn2:
            csv = edited_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Export ke CSV / Excel",
                data=csv,
                file_name=f"export_gudang_{datetime.now().strftime('%Y%m%d')}.csv",
                mime='text/csv'
            )

    with tab_b:
        st.subheader("Tambah Barang Baru Secara Manual")
        with st.form("form_tambah", clear_on_submit=True):
            c1, c2 = st.columns(2)
            kode = c1.text_input("Kode Barang (Unik)*")
            nama = c2.text_input("Nama Barang*")
            
            c3, c4 = st.columns(2)
            kategori = c3.selectbox("Kategori", ["Elektronik", "Pakaian", "Makanan/Minuman", "Peralatan", "Lainnya"])
            lokasi = c4.text_input("Lokasi Rak (Contoh: Rak A-01)")
            
            c5, c6 = st.columns(2)
            stok = c5.number_input("Stok Awal", min_value=0, value=10)
            harga = c6.number_input("Harga Satuan (Rp)", min_value=0, value=10000)
            
            if st.form_submit_button("Simpan Barang"):
                if kode and nama:
                    try:
                        c.execute("INSERT INTO barang (kode_barang, nama_barang, kategori, stok, harga, lokasi) VALUES (?, ?, ?, ?, ?, ?)",
                                  (kode, nama, kategori, stok, harga, lokasi))
                        conn.commit()
                        st.success(f"Berhasil menyimpan {nama}!")
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("Kode barang sudah terdaftar!")
                else:
                    st.error("Kode dan Nama barang wajib diisi!")

# ==========================================
# 3. MENU BARANG MASUK & KELUAR
# ==========================================
elif menu == "📥 Barang Masuk & Keluar":
    st.title("📥 Transaksi Stok (In / Out)")
    
    df_barang = get_all_barang()
    
    if not df_barang.empty:
        list_barang = df_barang['kode_barang'] + " - " + df_barang['nama_barang']
        selected_item = st.selectbox("Pilih Barang:", list_barang)
        kode_selected = selected_item.split(" - ")[0]
        
        stok_sekarang = df_barang[df_barang['kode_barang'] == kode_selected]['stok'].values[0]
        st.info(f"Stok saat ini: **{stok_sekarang} Pcs**")
        
        col_t1, col_t2 = st.columns(2)
        jenis_transaksi = col_t1.radio("Jenis Transaksi:", ["Barang Masuk (+)", "Barang Keluar (-)"])
        jumlah = col_t2.number_input("Jumlah (Pcs):", min_value=1, value=1)
        keterangan = st.text_area("Keterangan / Catatan:", "Restok" if "Masuk" in jenis_transaksi else "Pengiriman")
        
        if st.button("Proses Transaksi", use_container_width=True):
            tgl_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            operator = st.session_state['user']
            
            if "Masuk" in jenis_transaksi:
                stok_baru = stok_sekarang + jumlah
                c.execute("UPDATE barang SET stok = ? WHERE kode_barang = ?", (stok_baru, kode_selected))
                c.execute("INSERT INTO riwayat (tanggal, kode_barang, jenis, jumlah, keterangan, operator) VALUES (?, ?, ?, ?, ?, ?)",
                          (tgl_now, kode_selected, "MASUK", jumlah, keterangan, operator))
                conn.commit()
                st.success(f"Stok berhasil ditambahkan! Stok baru: {stok_baru}")
                st.rerun()
            else:
                if jumlah > stok_sekarang:
                    st.error("Stok tidak mencukupi untuk transaksi barang keluar!")
                else:
                    stok_baru = stok_sekarang - jumlah
                    c.execute("UPDATE barang SET stok = ? WHERE kode_barang = ?", (stok_baru, kode_selected))
                    c.execute("INSERT INTO riwayat (tanggal, kode_barang, jenis, jumlah, keterangan, operator) VALUES (?, ?, ?, ?, ?, ?)",
                              (tgl_now, kode_selected, "KELUAR", jumlah, keterangan, operator))
                    conn.commit()
                    st.success(f"Stok berhasil dikurangi! Stok sisa: {stok_baru}")
                    st.rerun()
    else:
        st.info("Belum ada data barang di database.")

# ==========================================
# 4. MENU RIWAYAT TRANSAKSI
# ==========================================
elif menu == "📜 Riwayat Transaksi":
    st.title("📜 Log Transaksi Gudang")
    df_riwayat = get_all_riwayat()
    
    if not df_riwayat.empty:
        st.dataframe(df_riwayat, use_container_width=True)
    else:
        st.info("Belum ada riwayat transaksi.")

# ==========================================
# 5. MENU IMPORT FILE EXCEL/CSV (ADMIN ONLY)
# ==========================================
elif menu == "📤 Import Data Excel/CSV":
    st.title("📤 Mass Import Data Gudang")
    st.markdown("Upload file `.csv` untuk memasukkan banyak data barang sekaligus secara otomatis.")
    
    uploaded_file = st.file_uploader("Pilih File CSV", type=["csv"])
    
    if uploaded_file is not None:
        try:
            df_upload = pd.read_csv(uploaded_file)
            st.subheader("Preview Data yang Akan Di-import:")
            st.dataframe(df_upload, use_container_width=True)
            
            if st.button("Proses Upload ke Database"):
                df_upload.to_sql('barang', conn, if_exists='append', index=False)
                st.success("Seluruh data berhasil di-import ke database gudang!")
                st.rerun()
        except Exception as e:
            st.error(f"Gagal memproses file. Pastikan format kolom sesuai. Detail: {e}")