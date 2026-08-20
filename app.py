import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="BTC Warehouse - Dashboard Sortir Order",
    page_icon="📦",
    layout="wide"
)

# === SPREADSHEET ID SAMA DENGAN LINK GOOGLE SHEETS KAMU ===
SPREADSHEET_ID = "1tn0F59DUG37uW7YmxerEEc721RUeGmfVtTzEazg5t9g"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}"

# --- CONNECTOR GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

def get_users():
    try:
        df = conn.read(spreadsheet=SHEET_URL, worksheet="AKUN", ttl=0)
        return df
    except Exception:
        # Fallback jika tab AKUN belum dibaca/dibuat
        return pd.DataFrame([
            {"email": "rezasaputra42@gmail.com", "password": "admin", "nama": "Reza Saputra", "role": "Admin"}
        ])

def get_barang():
    try:
        df = conn.read(spreadsheet=SHEET_URL, worksheet="BARANG", ttl=0)
        if not df.empty and 'stok' in df.columns:
            df['stok'] = pd.to_numeric(df['stok'], errors='coerce').fillna(0).astype(int)
        return df
    except Exception:
        return pd.DataFrame()

def get_riwayat():
    try:
        return conn.read(spreadsheet=SHEET_URL, worksheet="RIWAYAT", ttl=0)
    except Exception:
        return pd.DataFrame()

def save_barang(df):
    conn.update(spreadsheet=SHEET_URL, worksheet="BARANG", data=df)

def save_riwayat(df):
    conn.update(spreadsheet=SHEET_URL, worksheet="RIWAYAT", data=df)

# --- SESSION STATE LOGIN ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_info' not in st.session_state:
    st.session_state['user_info'] = {}
if 'active_menu' not in st.session_state:
    st.session_state['active_menu'] = 'Stock'

# ==========================================
# HALAMAN LOGIN (SAMA DENGAN TAMPILAN GAMBAR)
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
        remember = st.checkbox("Tetap masuk di perangkat ini (12 jam)", value=True)
        
        if st.button("Masuk", use_container_width=True, type="primary"):
            if email_input and pass_input:
                df_users = get_users()
                
                # Cek kecocokan Email & Password dari tab AKUN Google Sheets
                user_match = df_users[
                    (df_users['email'].astype(str).str.lower() == email_input.lower().strip()) & 
                    (df_users['password'].astype(str) == pass_input.strip())
                ]
                
                if not user_match.empty:
                    user_data = user_match.iloc[0]
                    st.session_state['logged_in'] = True
                    st.session_state['user_info'] = {
                        'email': user_data['email'],
                        'nama': user_data['nama'],
                        'role': user_data['role']
                    }
                    st.success(f"Selamat datang, {user_data['nama']}!")
                    st.rerun()
                else:
                    st.error("Email atau Password salah! Periksa kembali data Anda di tab AKUN Google Sheets.")
            else:
                st.warning("Masukkan Email dan Password terlebih dahulu.")
                
        st.caption("Belum punya akun? Minta admin untuk membuatkan sub-account.")
    st.stop()

# ==========================================
# HALAMAN UTAMA (SETELAH LOGIN BERHASIL)
# ==========================================

# Info User & Logout di Sidebar
st.sidebar.markdown(f"👤 **{st.session_state['user_info']['nama']}**")
st.sidebar.caption(f"Role: {st.session_state['user_info']['role']} ({st.session_state['user_info']['email']})")

if st.sidebar.button("🚪 Logout / Keluar", use_container_width=True):
    st.session_state['logged_in'] = False
    st.session_state['user_info'] = {}
    st.rerun()

st.title("🏢 DASHBOARD GUDANG PALEMBANG")
st.caption("Sistem Operational Inbound & Outbound Real-Time")
st.markdown("---")

# Navigation Grid Card
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

# --- 1. STOCK MONITORING ---
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

# --- 2. INBOUND ---
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
            
            submit = st.form_submit_button("📥 Simpan ke Google Sheets", use_container_width=True)
            
            if submit:
                stok_baru = stok_saat_ini + int(qty)
                tgl_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                df_barang.at[idx, 'stok'] = stok_baru
                save_barang(df_barang)
                
                df_riwayat = get_riwayat()
                new_log = pd.DataFrame([{
                    'Tanggal': tgl_now,
                    'Kode_Barang': kode_selected,
                    'Nama_Barang': nama_selected,
                    'Jenis': "INBOUND",
                    'Jumlah': int(qty),
                    'Keterangan': no_po,
                    'Operator': st.session_state['user_info']['nama']
                }])
                save_riwayat(pd.concat([df_riwayat, new_log], ignore_index=True))
                
                st.success(f"✅ Inbound Berhasil! Stok baru: {stok_baru} Pcs.")
                st.rerun()

# --- 3. OUTBOUND ---
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
            
            submit = st.form_submit_button("📤 Simpan ke Google Sheets", use_container_width=True)
            
            if submit:
                if int(qty) > stok_saat_ini:
                    st.error(f"❌ Gagal Outbound! Stok tidak mencukupi (Tersedia: {stok_saat_ini} Pcs).")
                else:
                    stok_baru = stok_saat_ini - int(qty)
                    tgl_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    df_barang.at[idx, 'stok'] = stok_baru
                    save_barang(df_barang)
                    
                    df_riwayat = get_riwayat()
                    new_log = pd.DataFrame([{
                        'Tanggal': tgl_now,
                        'Kode_Barang': kode_selected,
                        'Nama_Barang': nama_selected,
                        'Jenis': "OUTBOUND",
                        'Jumlah': int(qty),
                        'Keterangan': no_resi,
                        'Operator': st.session_state['user_info']['nama']
                    }])
                    save_riwayat(pd.concat([df_riwayat, new_log], ignore_index=True))
                    
                    st.success(f"✅ Outbound Berhasil! Sisa stok: {stok_baru} Pcs.")
                    st.rerun()

# --- 4. RIWAYAT ---
elif st.session_state['active_menu'] == 'Riwayat':
    st.subheader("📜 Log Transaksi Inbound & Outbound (Tab RIWAYAT)")
    st.dataframe(get_riwayat(), use_container_width=True, hide_index=True)
