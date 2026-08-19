import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# --- CONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="BTC Warehouse - Operational Portal",
    page_icon="📦",
    layout="wide"
)

# --- DATABASE SETUP ---
conn = sqlite3.connect('gudang_btc_card.db', check_same_thread=False)
c = conn.cursor()

c.execute('''
    CREATE TABLE IF NOT EXISTS barang (
        kode_barang TEXT PRIMARY KEY,
        nama_barang TEXT,
        kategori TEXT,
        stok INTEGER,
        lokasi TEXT
    )
''')

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

# --- DAFTAR SKU MASTER ---
DATA_SKU_INITIAL = [
    ("MC001", "JAKET HOODIE WOOKEY WIGHT", "Merchandise", 0, "Rak A"),
    ("MC002", "KAOS WOOKEY WIGHT", "Merchandise", 0, "Rak A"),
    ("MC004", "TOTEBAG WOOKEY", "Merchandise", 0, "Rak A"),
    ("MC005", "TUMBLER WOOKEY", "Merchandise", 0, "Rak A"),
    ("MC007", "PUZZLE SOHONEY", "Merchandise", 0, "Rak A"),
    ("MC010", "TUMBLER SOHONEY", "Merchandise", 0, "Rak A"),
    ("MC011", "KOTAK MAKAN SOHONEY", "Merchandise", 0, "Rak A"),
    ("MC012", "TAS BEKEL SOHONEY", "Merchandise", 0, "Rak A"),
    ("MC013", "BONEKA DINO SOHONEY", "Merchandise", 0, "Rak A"),
    ("MC014", "BOTOL SHAKER WOOKEY", "Merchandise", 0, "Rak A"),
    ("MC015", "MUG STIRER WOOKEY", "Merchandise", 0, "Rak A"),
    ("MC016", "TIMBANGAN WOOKEY", "Merchandise", 0, "Rak A"),
    ("MC017", "KAOS WOOKEY CRM", "Merchandise", 0, "Rak A"),
    ("MC018", "Tasbih Digital", "Merchandise", 0, "Rak A"),
    ("PC001", "KARDUS WOOKEY WIGHT", "Packaging", 0, "Rak B"),
    ("PC002", "KARDUS WOOKEY WIGHT 2PC", "Packaging", 0, "Rak B"),
    ("PC003", "KARDUS WOOKEY WIGHT 3PC", "Packaging", 0, "Rak B"),
    ("PC004", "KARDUS SOHONEY JR", "Packaging", 0, "Rak B"),
    ("PC005", "KARDUS SOHONEY JR 2PC", "Packaging", 0, "Rak B"),
    ("PC006", "KARDUS SOHONEY JR 3PC", "Packaging", 0, "Rak B"),
    ("PC007", "LAKBAN", "Packaging", 0, "Rak B"),
    ("PC008", "THERMAL", "Packaging", 0, "Rak B"),
    ("PC009", "BUBLE WRAP", "Packaging", 0, "Rak B"),
    ("PC013", "STIKER KEASLIAN WW", "Packaging", 0, "Rak B"),
    ("PC014", "THANKS CARD WW", "Packaging", 0, "Rak B"),
    ("PC015", "THANKS CARD SHJR", "Packaging", 0, "Rak B"),
    ("PC016", "PLASTIK POLYMAILER UK 25", "Packaging", 0, "Rak B"),
    ("PC017", "PLASTIK POLYMAILER UK 35", "Packaging", 0, "Rak B"),
    ("PC019", "LAKBAN FRAGILE", "Packaging", 0, "Rak B"),
    ("PC020", "PLASTIK WOOKEY (20 X 30)", "Packaging", 0, "Rak B"),
    ("PC021", "PLASTIK WOOKEY 2 PCS (25 X 35)", "Packaging", 0, "Rak B"),
    ("PC022", "PLASTIK WOOKEY 3 PCS", "Packaging", 0, "Rak B"),
    ("PC023", "PLASTIK WOOKEY 4 PCS", "Packaging", 0, "Rak B"),
    ("PC025", "PLASTIK SOHONEY 1 PCS", "Packaging", 0, "Rak B"),
    ("PC026", "PLASTIK SOHONEY 2 PCS", "Packaging", 0, "Rak B"),
    ("PC027", "PLASTIK SOHONEY 3 PCS", "Packaging", 0, "Rak B"),
    ("PC028", "PLASTIK SOHONEY 4 PCS", "Packaging", 0, "Rak B"),
    ("PC029", "PLASTIK SOHONEY 5 PCS", "Packaging", 0, "Rak B"),
    ("PC052", "KARDUS WOOKEY BULKUP HONEY", "Packaging", 0, "Rak B"),
    ("SJ001", "SOHONEY JR", "Produk Sohoney", 0, "Rak C"),
    ("SJ002", "SOHONEY HUG BABY CREAM", "Produk Sohoney", 0, "Rak C"),
    ("WW001", "WOOKEY WIGHT 220gr", "Produk Wookey", 0, "Rak C"),
    ("WW003", "WOOKEY WIGHT 220gr Coklat", "Produk Wookey", 0, "Rak C"),
    ("WW005", "Wookey Optigain", "Produk Wookey", 0, "Rak C"),
    ("WW006", "WOOKEY BULKUP HONEY", "Produk Wookey", 0, "Rak C")
]

for sku in DATA_SKU_INITIAL:
    c.execute("INSERT OR IGNORE INTO barang (kode_barang, nama_barang, kategori, stok, lokasi) VALUES (?, ?, ?, ?, ?)", sku)
conn.commit()

# --- FUNGSI AMBIL DATA ---
def get_barang():
    df = pd.read_sql_query("SELECT * FROM barang", conn)
    df['stok'] = pd.to_numeric(df['stok'], errors='coerce').fillna(0).astype(int)
    return df

def get_riwayat():
    return pd.read_sql_query("SELECT * FROM riwayat ORDER BY id DESC", conn)

# --- SESSION MENU UTAMA ---
if 'active_menu' not in st.session_state:
    st.session_state['active_menu'] = 'Stock'

# --- HEADER PORTAL ---
st.title("🏢 BTC WAREHOUSE PALEMBANG")
st.caption("Sistem Manajemen Inbound, Outbound & Stok Barang Terpadu")
st.markdown("---")

# ==========================================
# GRID CARD NAVIGATION (OPTION 2)
# ==========================================
col1, col2, col3, col4 = st.columns(4)

if col1.button("📊\n\n**STOCK MONITORING**", use_container_width=True):
    st.session_state['active_menu'] = 'Stock'

if col2.button("📥\n\n**INBOUND (MASUK)**", use_container_width=True):
    st.session_state['active_menu'] = 'Inbound'

if col3.button("📤\n\n**OUTBOUND (KELUAR)**", use_container_width=True):
    st.session_state['active_menu'] = 'Outbound'

if col4.button("📜\n\n**RIWAYAT TRANSAKSI**", use_container_width=True):
    st.session_state['active_menu'] = 'Riwayat'

st.markdown("---")

# ==========================================
# 1. MENU STOCK MONITORING
# ==========================================
if st.session_state['active_menu'] == 'Stock':
    st.subheader("📊 Monitoring Stok Real-Time")
    
    df_barang = get_barang()
    
    # Pencarian
    search = st.text_input("🔍 Cari SKU / Nama Barang:")
    if search:
        df_barang = df_barang[
            df_barang['nama_barang'].str.contains(search, case=False) |
            df_barang['kode_barang'].str.contains(search, case=False)
        ]
        
    st.dataframe(df_barang, use_container_width=True, hide_index=True)

# ==========================================
# 2. MENU INBOUND (BARANG MASUK)
# ==========================================
elif st.session_state['active_menu'] == 'Inbound':
    st.subheader("📥 Inbound - Penerimaan Barang Masuk")
    
    df_barang = get_barang()
    options = df_barang['kode_barang'] + " | " + df_barang['nama_barang']
    
    selected = st.selectbox("Pilih SKU Barang Masuk:", options)
    kode_selected = selected.split(" | ")[0]
    
    row = df_barang[df_barang['kode_barang'] == kode_selected].iloc[0]
    stok_saat_ini = int(row['stok'])
    
    st.info(f"📌 **SKU:** {row['kode_barang']} — **Nama:** {row['nama_barang']} | **Stok Saat Ini:** {stok_saat_ini} Pcs")
    
    with st.form("form_inbound", clear_on_submit=True):
        c_in1, c_in2 = st.columns(2)
        qty = c_in1.number_input("Jumlah Barang Masuk (Pcs):", min_value=1, value=1)
        no_po = c_in2.text_input("Nomor PO / Surat Jalan Masuk:", placeholder="Contoh: PO-2026-001")
        operator = st.text_input("Nama Checker / Operator Inbound:", value="Reza Saputra")
        
        submit = st.form_submit_button("📥 Simpan Inbound", use_container_width=True)
        
        if submit:
            stok_baru = stok_saat_ini + int(qty)
            tgl_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            c.execute("UPDATE barang SET stok = ? WHERE kode_barang = ?", (stok_baru, kode_selected))
            c.execute(
                "INSERT INTO riwayat (tanggal, kode_barang, nama_barang, jenis, jumlah, keterangan, operator) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (tgl_now, kode_selected, row['nama_barang'], "INBOUND", int(qty), no_po, operator)
            )
            conn.commit()
            st.success(f"✅ Inbound Berhasil! Stok {row['nama_barang']} bertambah dari {stok_saat_ini} ➔ {stok_baru} Pcs.")
            st.rerun()

# ==========================================
# 3. MENU OUTBOUND (BARANG KELUAR)
# ==========================================
elif st.session_state['active_menu'] == 'Outbound':
    st.subheader("📤 Outbound - Pengeluaran Barang / Packing")
    
    df_barang = get_barang()
    options = df_barang['kode_barang'] + " | " + df_barang['nama_barang']
    
    selected = st.selectbox("Pilih SKU Barang Keluar:", options)
    kode_selected = selected.split(" | ")[0]
    
    row = df_barang[df_barang['kode_barang'] == kode_selected].iloc[0]
    stok_saat_ini = int(row['stok'])
    
    st.info(f"📌 **SKU:** {row['kode_barang']} — **Nama:** {row['nama_barang']} | **Stok Saat Ini:** {stok_saat_ini} Pcs")
    
    with st.form("form_outbound", clear_on_submit=True):
        c_out1, c_out2 = st.columns(2)
        qty = c_out1.number_input("Jumlah Barang Keluar (Pcs):", min_value=1, value=1)
        no_resi = c_out2.text_input("Nomor Resi / Keterangan Kirim:", placeholder="Contoh: SPX-12345678")
        operator = st.text_input("Nama Packer / Operator Outbound:", value="Reza Saputra")
        
        submit = st.form_submit_button("📤 Simpan Outbound", use_container_width=True)
        
        if submit:
            if int(qty) > stok_saat_ini:
                st.error(f"❌ Gagal Outbound! Stok tidak mencukupi (Tersedia: {stok_saat_ini} Pcs, Diminta: {qty} Pcs).")
            else:
                stok_baru = stok_saat_ini - int(qty)
                tgl_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                c.execute("UPDATE barang SET stok = ? WHERE kode_barang = ?", (stok_baru, kode_selected))
                c.execute(
                    "INSERT INTO riwayat (tanggal, kode_barang, nama_barang, jenis, jumlah, keterangan, operator) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (tgl_now, kode_selected, row['nama_barang'], "OUTBOUND", int(qty), no_resi, operator)
                )
                conn.commit()
                st.success(f"✅ Outbound Berhasil! Stok {row['nama_barang']} berkurang dari {stok_saat_ini} ➔ {stok_baru} Pcs.")
                st.rerun()

# ==========================================
# 4. MENU RIWAYAT TRANSAKSI
# ==========================================
elif st.session_state['active_menu'] == 'Riwayat':
    st.subheader("📜 Log Transaksi Inbound & Outbound")
    
    df_riwayat = get_riwayat()
    if not df_riwayat.empty:
        st.dataframe(df_riwayat, use_container_width=True, hide_index=True)
    else:
        st.info("Belum ada riwayat transaksi recorded.")
