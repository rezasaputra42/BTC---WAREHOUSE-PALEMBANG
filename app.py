import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="BTC Warehouse Palembang",
    page_icon="📦",
    layout="wide"
)

SPREADSHEET_ID = "1tn0F59DUG37uW7YmxerEEc721RUeGmfVtTzEazg5t9g"

# --- FUNGSI BACA DATA BACA LANGSUNG DARI CSV GOOGLE SHEETS ---
def get_data(sheet_name):
    try:
        url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
        df = pd.read_csv(url)
        df.columns = [str(col).strip().lower() for col in df.columns]
        return df
    except Exception as e:
        st.error(f"Gagal membaca tab {sheet_name}: {e}")
        return pd.DataFrame()

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
                        st.error("Email atau Password salah! Cek data di Google Sheets.")
                else:
                    st.error("Gagal membaca data tab AKUN.")
            else:
                st.warning("Masukkan Email dan Password.")
        st.caption("Belum punya akun? Minta admin untuk membuatkan sub-account.")
    st.stop()

# ==========================================
# 2. HALAMAN UTAMA
# ==========================================
st.sidebar.markdown(f"👤 **{st.session_state['user_info']['nama']}**")
st.sidebar.caption(f"Role: {st.session_state['user_info']['role']}\n\n{st.session_state['user_info']['email']}")

if st.sidebar.button("🚪 Logout / Keluar", use_container_width=True):
    st.session_state['logged_in'] = False
    st.session_state['user_info'] = {}
    st.rerun()

st.title("🏢 DASHBOARD GUDANG PALEMBANG")
st.markdown("---")

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

if st.session_state['active_menu'] == 'Stock':
    st.subheader("📊 Monitoring Stok Real-Time")
    df_barang = get_data("BARANG")
    if not df_barang.empty:
        search = st.text_input("🔍 Cari SKU / Nama Barang:")
        if search:
            df_barang = df_barang[
                df_barang['nama_barang'].astype(str).str.contains(search, case=False) |
                df_barang['kode_barang'].astype(str).str.contains(search, case=False)
            ]
        st.dataframe(df_barang, use_container_width=True, hide_index=True)

elif st.session_state['active_menu'] == 'Riwayat':
    st.subheader("📜 Log Transaksi Inbound & Outbound")
    st.dataframe(get_data("RIWAYAT"), use_container_width=True, hide_index=True)
