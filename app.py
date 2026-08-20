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

# === SPREADSHEET ID GOOGLE SHEETS ===
SPREADSHEET_ID = "1tn0F59DUG37uW7YmxerEEc721RUeGmfVtTzEazg5t9g"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}"

# --- KONEKSI GSHEETS DENGAN SERVICE ACCOUNT ---
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data(sheet_name):
    try:
        df = conn.read(spreadsheet=SHEET_URL, worksheet=sheet_name, ttl=0)
        df.columns = [str(col).strip().lower() for col in df.columns]
        return df
    except Exception as e:
        st.error(f"Gagal membaca tab '{sheet_name}'. Detail: {e}")
        return pd.DataFrame()

def save_data(sheet_name, df):
    try:
        conn.update(spreadsheet=SHEET_URL, worksheet=sheet_name, data=df)
    except Exception as e:
        st.error(f"Gagal menyimpan ke tab '{sheet_name}'. Detail: {e}")

# --- SESSION STATE LOGIN & NAVIGASI ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_info' not in st.session_state:
    st.session_state['user_info'] = {}
if 'active_menu' not in st.session_state:
    st.session_state['active_menu'] = 'Stock'

# ==========================================
# 1. HALAMAN LOGIN
# ==========================================
if not st.session_state['logged_in']:
    st.markdown("""
        <div style="background-color: #2b7a78; padding: 18px 25px; border-radius: 12px; color: white; margin-bottom: 25px;">
            <h2 style="margin:0; color: white; font-weight: 600;">📦 BTC Warehouse — Dashboard Sortir Order</h2>
            <p style="margin:6px 0 0 0; opacity: 0.9; font-size: 14px;">Masuk dengan akun kamu untuk melanjutkan.</p>
        </div>
    """, unsafe_allow_html=True)
    
    col_l1, col_l2, col_l3 = st.columns([1, 1.2, 1])
    
    with col_l2:
        st.subheader("🔒 Masuk")
        
        email_input = st.text_input("Email", placeholder="nama@gmail.com")
        pass_input = st.text_input("Password", type="password")
        st.checkbox("Tetap masuk di perangkat ini (12 jam)", value=True)
        
        if st.button("Masuk", use_container_width=True, type="primary"):
            if email_input and pass_input:
                df_users = get_data("AKUN")
                
                if not df_users.empty and 'email' in df_users.columns and 'password' in df_users.columns:
                    clean_email = email_input.lower().strip()
                    clean_pass = pass_input.strip()
                    
                    df_users['email_clean'] = df_users['email'].astype(str).str.lower().str.strip()
                    df_users['pass_clean'] = df_users['password'].astype(str).str.strip()
                    
                    user_match = df_users[
                        (df_users['email_clean'] == clean_email) & 
                        (df_users['pass_clean'] == clean_pass)
                    ]
                    
                    if not user_match.empty:
                        user_data = user_match.iloc[0]
                        st.session_state['logged_in'] = True
                        st.session_state['user_info'] = {
                            'email': user_data['email'],
                            'nama': user_data.get('nama', 'Staf Gudang'),
                            'role': user_data.get('role', 'Staf')
                        }
                        st.rerun()
                    else:
                        st.error("Email atau Password salah! Periksa kembali data Anda di tab AKUN Google Sheets.")
                else:
                    st.error("Gagal membaca struktur data di tab AKUN Google Sheets.")
            else:
                st.warning("Masukkan Email dan Password terlebih dahulu.")
                
        st.caption("Belum punya akun? Minta admin untuk membuatkan sub-account.")
    st.stop()

# ==========================================
# 2. HALAMAN UTAMA (DASHBOARD OPERASIONAL)
# ==========================================

# Sidebar Profil & Logout
st.sidebar.markdown(f"👤 **{st.session_state['user_info']['nama']}**")
st.sidebar.caption(f"Role: {st.session_state['user_info']['role']}\n\nEmail: {st.session_state['user_info']['email']}")

if st.sidebar.button("🚪 Logout / Keluar", use_container_width=True):
    st.session_state['logged_in'] = False
    st.session_state['user_info'] = {}
    st.rerun()

st.title("🏢 DASHBOARD GUDANG PALEMBANG")
st.caption("Sistem Operational Inbound & Outbound Real-Time")
st.markdown("---")

# Menu Navigasi Kartu
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

# --- A. STOCK MONITORING ---
if st.session_state['active_menu'] == 'Stock':
    st.subheader("📊 Monitoring Stok Real-Time (Tab BARANG)")
    df_barang = get_data("BARANG")
    
    if not df_barang.empty:
        if 'stok' in df_barang.columns:
            df_barang['stok'] = pd.to_numeric(df_barang['stok'], errors='coerce').fillna(0).astype(int)
            
        search = st.text_input("🔍 Cari SKU / Nama Barang:")
        if search:
            df_barang = df_barang[
                df_barang['nama_barang'].astype(str).str.contains(search, case=False) |
                df_barang['kode_barang'].astype(str).str.contains(search, case=False)
            ]
        st.dataframe(df_barang, use_container_width=True, hide_index=True)
    else:
        st.info("Data barang kosong atau tidak dapat dimuat.")

# --- B. INBOUND (BARANG MASUK) ---
elif st.session_state['active_menu'] == 'Inbound':
    st.subheader("📥 Inbound - Penerimaan Barang Masuk")
    df_barang = get_data("BARANG")
    
    if not df_barang.empty and 'kode_barang' in df_barang.columns:
        df_barang['stok'] = pd.to_numeric(df_barang.get('stok', 0), errors='coerce').fillna(0).astype(int)
        
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
            
            submit = st.form_submit_button("📥 Simpan ke Google Sheets", use_container_width=True)
            
            if submit:
                stok_baru = stok_saat_ini + int(qty)
                tgl_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Update stok di BARANG
                df_barang.at[idx, 'stok'] = stok_baru
                save_data("BARANG", df_barang)
                
                # Catat ke RIWAYAT
                df_riwayat = get_data("RIWAYAT")
                new_log = pd.DataFrame([{
                    'tanggal': tgl_now,
                    'kode_barang': kode_selected,
                    'nama_barang': nama_selected,
                    'jenis': "INBOUND",
                    'jumlah': int(qty),
                    'keterangan': no_po,
                    'operator': st.session_state['user_info']['nama']
                }])
                save_data("RIWAYAT", pd.concat([df_riwayat, new_log], ignore_index=True))
                
                st.success(f"✅ Inbound Berhasil! Stok baru: {stok_baru} Pcs.")
                st.rerun()

# --- C. OUTBOUND (BARANG KELUAR) ---
elif st.session_state['active_menu'] == 'Outbound':
    st.subheader("📤 Outbound - Pengeluaran Barang / Packing")
    df_barang = get_data("BARANG")
    
    if not df_barang.empty and 'kode_barang' in df_barang.columns:
        df_barang['stok'] = pd.to_numeric(df_barang.get('stok', 0), errors='coerce').fillna(0).astype(int)
        
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
            
            submit = st.form_submit_button("📤 Simpan ke Google Sheets", use_container_width=True)
            
            if submit:
                if int(qty) > stok_saat_ini:
                    st.error(f"❌ Gagal Outbound! Stok tidak mencukupi (Tersedia: {stok_saat_ini} Pcs).")
                else:
                    stok_baru = stok_saat_ini - int(qty)
                    tgl_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Update stok di BARANG
                    df_barang.at[idx, 'stok'] = stok_baru
                    save_data("BARANG", df_barang)
                    
                    # Catat ke RIWAYAT
                    df_riwayat = get_data("RIWAYAT")
                    new_log = pd.DataFrame([{
                        'tanggal': tgl_now,
                        'kode_barang': kode_selected,
                        'nama_barang': nama_selected,
                        'jenis': "OUTBOUND",
                        'jumlah': int(qty),
                        'keterangan': no_resi,
                        'operator': st.session_state['user_info']['nama']
                    }])
                    save_data("RIWAYAT", pd.concat([df_riwayat, new_log], ignore_index=True))
                    
                    st.success(f"✅ Outbound Berhasil! Sisa stok: {stok_baru} Pcs.")
                    st.rerun()

# --- D. RIWAYAT TRANSAKSI ---
elif st.session_state['active_menu'] == 'Riwayat':
    st.subheader("📜 Log Transaksi Inbound & Outbound (Tab RIWAYAT)")
    df_riwayat = get_data("RIWAYAT")
    if not df_riwayat.empty:
        st.dataframe(df_riwayat, use_container_width=True, hide_index=True)
    else:
        st.info("Belum ada riwayat transaksi recorded.")
