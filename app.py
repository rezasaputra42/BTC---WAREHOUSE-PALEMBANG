import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="BTC Warehouse Palembang",
    page_icon="📦",
    layout="wide"
)

# === SPREADSHEET ID SAMA DENGAN LINK GOOGLE SHEETS KAMU ===
SPREADSHEET_ID = "1tn0F59DUG37uW7YmxerEEc721RUeGmfVtTzEazg5t9g"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}"

# --- DAFTAR SKU MASTER DEFAULT ---
DATA_SKU_MASTER = [
    {"kode_barang": "MC001", "nama_barang": "JAKET HOODIE WOOKEY WIGHT", "kategori": "Merchandise", "stok": 0, "lokasi": "Rak A"},
    {"kode_barang": "MC002", "nama_barang": "KAOS WOOKEY WIGHT", "kategori": "Merchandise", "stok": 0, "lokasi": "Rak A"},
    {"kode_barang": "MC004", "nama_barang": "TOTEBAG WOOKEY", "kategori": "Merchandise", "stok": 0, "lokasi": "Rak A"},
    {"kode_barang": "MC005", "nama_barang": "TUMBLER WOOKEY", "kategori": "Merchandise", "stok": 0, "lokasi": "Rak A"},
    {"kode_barang": "MC007", "nama_barang": "PUZZLE SOHONEY", "kategori": "Merchandise", "stok": 0, "lokasi": "Rak A"},
    {"kode_barang": "MC010", "nama_barang": "TUMBLER SOHONEY", "kategori": "Merchandise", "stok": 0, "lokasi": "Rak A"},
    {"kode_barang": "MC011", "nama_barang": "KOTAK MAKAN SOHONEY", "kategori": "Merchandise", "stok": 0, "lokasi": "Rak A"},
    {"kode_barang": "MC012", "nama_barang": "TAS BEKEL SOHONEY", "kategori": "Merchandise", "stok": 0, "lokasi": "Rak A"},
    {"kode_barang": "MC013", "nama_barang": "BONEKA DINO SOHONEY", "kategori": "Merchandise", "stok": 0, "lokasi": "Rak A"},
    {"kode_barang": "MC014", "nama_barang": "BOTOL SHAKER WOOKEY", "kategori": "Merchandise", "stok": 0, "lokasi": "Rak A"},
    {"kode_barang": "MC015", "nama_barang": "MUG STIRER WOOKEY", "kategori": "Merchandise", "stok": 0, "lokasi": "Rak A"},
    {"kode_barang": "MC016", "nama_barang": "TIMBANGAN WOOKEY", "kategori": "Merchandise", "stok": 0, "lokasi": "Rak A"},
    {"kode_barang": "MC017", "nama_barang": "KAOS WOOKEY CRM", "kategori": "Merchandise", "stok": 0, "lokasi": "Rak A"},
    {"kode_barang": "MC018", "nama_barang": "Tasbih Digital", "kategori": "Merchandise", "stok": 0, "lokasi": "Rak A"},
    {"kode_barang": "PC001", "nama_barang": "KARDUS WOOKEY WIGHT", "kategori": "Packaging", "stok": 0, "lokasi": "Rak B"},
    {"kode_barang": "PC002", "nama_barang": "KARDUS WOOKEY WIGHT 2PC", "kategori": "Packaging", "stok": 0, "lokasi": "Rak B"},
    {"kode_barang": "PC003", "nama_barang": "KARDUS WOOKEY WIGHT 3PC", "kategori": "Packaging", "stok": 0, "lokasi": "Rak B"},
    {"kode_barang": "PC004", "nama_barang": "KARDUS SOHONEY JR", "kategori": "Packaging", "stok": 0, "lokasi": "Rak B"},
    {"kode_barang": "PC005", "nama_barang": "KARDUS SOHONEY JR 2PC", "kategori": "Packaging", "stok": 0, "lokasi": "Rak B"},
    {"kode_barang": "PC006", "nama_barang": "KARDUS SOHONEY JR 3PC", "kategori": "Packaging", "stok": 0, "lokasi": "Rak B"},
    {"kode_barang": "PC007", "nama_barang": "LAKBAN", "kategori": "Packaging", "stok": 0, "lokasi": "Rak B"},
    {"kode_barang": "PC008", "nama_barang": "THERMAL", "kategori": "Packaging", "stok": 0, "lokasi": "Rak B"},
    {"kode_barang": "PC009", "nama_barang": "BUBLE WRAP", "kategori": "Packaging", "stok": 0, "lokasi": "Rak B"},
    {"kode_barang": "PC013", "nama_barang": "STIKER KEASLIAN WW", "kategori": "Packaging", "stok": 0, "lokasi": "Rak B"},
    {"kode_barang": "PC014", "nama_barang": "THANKS CARD WW", "kategori": "Packaging", "stok": 0, "lokasi": "Rak B"},
    {"kode_barang": "PC015", "nama_barang": "THANKS CARD SHJR", "kategori": "Packaging", "stok": 0, "lokasi": "Rak B"},
    {"kode_barang": "PC016", "nama_barang": "PLASTIK POLYMAILER UK 25", "kategori": "Packaging", "stok": 0, "lokasi": "Rak B"},
    {"kode_barang": "PC017", "nama_barang": "PLASTIK POLYMAILER UK 35", "kategori": "Packaging", "stok": 0, "lokasi": "Rak B"},
    {"kode_barang": "PC019", "nama_barang": "LAKBAN FRAGILE", "kategori": "Packaging", "stok": 0, "lokasi": "Rak B"},
    {"kode_barang": "PC020", "nama_barang": "PLASTIK WOOKEY (20 X 30)", "kategori": "Packaging", "stok": 0, "lokasi": "Rak B"},
    {"kode_barang": "PC021", "nama_barang": "PLASTIK WOOKEY 2 PCS (25 X 35)", "kategori": "Packaging", "stok": 0, "lokasi": "Rak B"},
    {"kode_barang": "PC022", "nama_barang": "PLASTIK WOOKEY 3 PCS", "kategori": "Packaging", "stok": 0, "lokasi": "Rak B"},
    {"kode_barang": "PC023", "nama_barang": "PLASTIK WOOKEY 4 PCS", "kategori": "Packaging", "stok": 0, "lokasi": "Rak B"},
    {"kode_barang": "PC025", "nama_barang": "PLASTIK SOHONEY 1 PCS", "kategori": "Packaging", "stok": 0, "lokasi": "Rak B"},
    {"kode_barang": "PC026", "nama_barang": "PLASTIK SOHONEY 2 PCS", "kategori": "Packaging", "stok": 0, "lokasi": "Rak B"},
    {"kode_barang": "PC027", "nama_barang": "PLASTIK SOHONEY 3 PCS", "kategori": "Packaging", "stok": 0, "lokasi": "Rak B"},
    {"kode_barang": "PC028", "nama_barang": "PLASTIK SOHONEY 4 PCS", "kategori": "Packaging", "stok": 0, "lokasi": "Rak B"},
    {"kode_barang": "PC029", "nama_barang": "PLASTIK SOHONEY 5 PCS", "kategori": "Packaging", "stok": 0, "lokasi": "Rak B"},
    {"kode_barang": "PC052", "nama_barang": "KARDUS WOOKEY BULKUP HONEY", "kategori": "Packaging", "stok": 0, "lokasi": "Rak B"},
    {"kode_barang": "SJ001", "nama_barang": "SOHONEY JR", "kategori": "Produk Sohoney", "stok": 0, "lokasi": "Rak C"},
    {"kode_barang": "SJ002", "nama_barang": "SOHONEY HUG BABY CREAM", "kategori": "Produk Sohoney", "stok": 0, "lokasi": "Rak C"},
    {"kode_barang": "WW001", "nama_barang": "WOOKEY WIGHT 220gr", "kategori": "Produk Wookey", "stok": 0, "lokasi": "Rak C"},
    {"kode_barang": "WW003", "nama_barang": "WOOKEY WIGHT 220gr Coklat", "kategori": "Produk Wookey", "stok": 0, "lokasi": "Rak C"},
    {"kode_barang": "WW005", "nama_barang": "Wookey Optigain", "kategori": "Produk Wookey", "stok": 0, "lokasi": "Rak C"},
    {"kode_barang": "WW006", "nama_barang": "WOOKEY BULKUP HONEY", "kategori": "Produk Wookey", "stok": 0, "lokasi": "Rak C"}
]

# --- CONNECTOR GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

def get_barang():
    try:
        df = conn.read(spreadsheet=SHEET_URL, worksheet="BARANG", ttl=0)
        if df.empty or len(df) == 0:
            df = pd.DataFrame(DATA_SKU_MASTER)
            save_barang(df)
        else:
            df['stok'] = pd.to_numeric(df['stok'], errors='coerce').fillna(0).astype(int)
        return df
    except Exception:
        df = pd.DataFrame(DATA_SKU_MASTER)
        return df

def get_riwayat():
    try:
        df = conn.read(spreadsheet=SHEET_URL, worksheet="RIWAYAT", ttl=0)
        return df
    except Exception:
        return pd.DataFrame(columns=['Tanggal', 'Kode_Barang', 'Nama_Barang', 'Jenis', 'Jumlah', 'Keterangan', 'Operator'])

def save_barang(df):
    conn.update(spreadsheet=SHEET_URL, worksheet="BARANG", data=df)

def save_riwayat(df):
    conn.update(spreadsheet=SHEET_URL, worksheet="RIWAYAT", data=df)

# --- SESSION MENU UTAMA ---
if 'active_menu' not in st.session_state:
    st.session_state['active_menu'] = 'Stock'

# --- HEADER PORTAL ---
st.title("🏢 DASHBOARD GUDANG PALEMBANG")
st.caption("Sistem Inbound & Outbound Terhubung Google Sheets Real-Time")
st.markdown("---")

# ==========================================
# GRID CARD NAVIGATION (TOMBOL UTAMA)
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
    st.subheader("📊 Monitoring Stok Real-Time (Tab BARANG)")
    
    df_barang = get_barang()
    
    search = st.text_input("🔍 Cari SKU / Nama Barang:")
    if search and not df_barang.empty:
        df_barang = df_barang[
            df_barang['nama_barang'].astype(str).str.contains(search, case=False) |
            df_barang['kode_barang'].astype(str).str.contains(search, case=False)
        ]
        
    st.dataframe(df_barang, use_container_width=True, hide_index=True)

# ==========================================
# 2. MENU INBOUND (BARANG MASUK)
# ==========================================
elif st.session_state['active_menu'] == 'Inbound':
    st.subheader("📥 Inbound - Penerimaan Barang Masuk")
    
    df_barang = get_barang()
    
    if not df_barang.empty:
        options = df_barang['kode_barang'].astype(str) + " | " + df_barang['nama_barang'].astype(str)
        selected = st.selectbox("Pilih SKU Barang Masuk:", options)
        kode_selected = selected.split(" | ")[0]
        
        idx = df_barang[df_barang['kode_barang'].astype(str) == kode_selected].index[0]
        stok_saat_ini = int(df_barang.at[idx, 'stok'])
        nama_selected = df_barang.at[idx, 'nama_barang']
        
        st.info(f"📌 **SKU:** {kode_selected} — **Nama:** {nama_selected} | **Stok Saat Ini:** {stok_saat_ini} Pcs")
        
        with st.form("form_inbound", clear_on_submit=True):
            c_in1, c_in2 = st.columns(2)
            qty = c_in1.number_input("Jumlah Barang Masuk (Pcs):", min_value=1, value=1)
            no_po = c_in2.text_input("Nomor PO / Surat Jalan Masuk:", placeholder="Contoh: PO-2026-001")
            operator = st.text_input("Nama Checker / Operator Inbound:", value="Reza Saputra")
            
            submit = st.form_submit_button("📥 Simpan ke Google Sheets", use_container_width=True)
            
            if submit:
                stok_baru = stok_saat_ini + int(qty)
                tgl_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Update stok di sheet BARANG
                df_barang.at[idx, 'stok'] = stok_baru
                save_barang(df_barang)
                
                # Tambah log di sheet RIWAYAT
                df_riwayat = get_riwayat()
                new_log = pd.DataFrame([{
                    'Tanggal': tgl_now,
                    'Kode_Barang': kode_selected,
                    'Nama_Barang': nama_selected,
                    'Jenis': "INBOUND",
                    'Jumlah': int(qty),
                    'Keterangan': no_po,
                    'Operator': operator
                }])
                save_riwayat(pd.concat([df_riwayat, new_log], ignore_index=True))
                
                st.success(f"✅ Inbound Berhasil! Data tersimpan di Google Sheets. Stok baru: {stok_baru} Pcs.")
                st.rerun()

# ==========================================
# 3. MENU OUTBOUND (BARANG KELUAR)
# ==========================================
elif st.session_state['active_menu'] == 'Outbound':
    st.subheader("📤 Outbound - Pengeluaran Barang / Packing")
    
    df_barang = get_barang()
    
    if not df_barang.empty:
        options = df_barang['kode_barang'].astype(str) + " | " + df_barang['nama_barang'].astype(str)
        selected = st.selectbox("Pilih SKU Barang Keluar:", options)
        kode_selected = selected.split(" | ")[0]
        
        idx = df_barang[df_barang['kode_barang'].astype(str) == kode_selected].index[0]
        stok_saat_ini = int(df_barang.at[idx, 'stok'])
        nama_selected = df_barang.at[idx, 'nama_barang']
        
        st.info(f"📌 **SKU:** {kode_selected} — **Nama:** {nama_selected} | **Stok Saat Ini:** {stok_saat_ini} Pcs")
        
        with st.form("form_outbound", clear_on_submit=True):
            c_out1, c_out2 = st.columns(2)
            qty = c_out1.number_input("Jumlah Barang Keluar (Pcs):", min_value=1, value=1)
            no_resi = c_out2.text_input("Nomor Resi / Keterangan Kirim:", placeholder="Contoh: SPX-12345678")
            operator = st.text_input("Nama Packer / Operator Outbound:", value="Reza Saputra")
            
            submit = st.form_submit_button("📤 Simpan ke Google Sheets", use_container_width=True)
            
            if submit:
                if int(qty) > stok_saat_ini:
                    st.error(f"❌ Gagal Outbound! Stok tidak mencukupi (Tersedia: {stok_saat_ini} Pcs).")
                else:
                    stok_baru = stok_saat_ini - int(qty)
                    tgl_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Update stok di sheet BARANG
                    df_barang.at[idx, 'stok'] = stok_baru
                    save_barang(df_barang)
                    
                    # Tambah log di sheet RIWAYAT
                    df_riwayat = get_riwayat()
                    new_log = pd.DataFrame([{
                        'Tanggal': tgl_now,
                        'Kode_Barang': kode_selected,
                        'Nama_Barang': nama_selected,
                        'Jenis': "OUTBOUND",
                        'Jumlah': int(qty),
                        'Keterangan': no_resi,
                        'Operator': operator
                    }])
                    save_riwayat(pd.concat([df_riwayat, new_log], ignore_index=True))
                    
                    st.success(f"✅ Outbound Berhasil! Data tersimpan di Google Sheets. Sisa stok: {stok_baru} Pcs.")
                    st.rerun()

# ==========================================
# 4. MENU RIWAYAT TRANSAKSI
# ==========================================
elif st.session_state['active_menu'] == 'Riwayat':
    st.subheader("📜 Log Transaksi Inbound & Outbound (Tab RIWAYAT)")
    
    df_riwayat = get_riwayat()
    if not df_riwayat.empty:
        st.dataframe(df_riwayat, use_container_width=True, hide_index=True)
    else:
        st.info("Belum ada riwayat transaksi di Google Sheets.")
