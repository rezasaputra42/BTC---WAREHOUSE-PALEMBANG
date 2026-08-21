import streamlit as st
import pandas as pd
import re
import io
import math
import struct
import base64
from datetime import datetime

try:
    import pdfplumber
    PDF_OK = True
except ImportError:
    PDF_OK = False

try:
    from pypdf import PdfWriter, PdfReader
    MERGE_OK = True
except ImportError:
    MERGE_OK = False

# ==================================================================
# KONFIGURASI HALAMAN
# ==================================================================
st.set_page_config(
    page_title="BTC Warehouse Palembang - Dashboard Gudang Internal",
    page_icon="📦",
    layout="wide",
)

SPREADSHEET_ID = "1tn0F59DUG37uW7YmxerEEc721RUeGmfVtTzEazg5t9g"

# ==================================================================
# BACA DATA DARI GOOGLE SHEETS (CSV publish-to-web, read-only)
# ==================================================================
def get_data(sheet_name):
    """Baca satu tab Google Sheets sebagai DataFrame. Return None kalau gagal/tab belum ada."""
    try:
        url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
        df = pd.read_csv(url)
        df.columns = [str(col).strip().lower() for col in df.columns]
        return df
    except Exception:
        return None


# Opsional: tulis balik ke Google Sheets pakai gspread + service account.
# Kalau st.secrets["gcp_service_account"] belum diisi, semua fungsi ini
# otomatis nonaktif dan aplikasi tetap jalan pakai session_state saja.
def get_gspread_client():
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        creds_dict = st.secrets["gcp_service_account"]
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        return gspread.authorize(creds)
    except Exception:
        return None


def append_row_to_sheet(sheet_name, row_values):
    client = get_gspread_client()
    if client is None:
        return False
    try:
        sh = client.open_by_key(SPREADSHEET_ID)
        try:
            ws = sh.worksheet(sheet_name)
        except Exception:
            ws = sh.add_worksheet(title=sheet_name, rows=1000, cols=10)
        ws.append_row(row_values)
        return True
    except Exception:
        return False


# ==================================================================
# STAFF / LOGIN
# ==================================================================
DEFAULT_STAFF = [
    {"username": "admin", "password": "admin123", "nama": "Admin Gudang", "role": "admin"},
    {"username": "staff", "password": "staff123", "nama": "Staff Gudang", "role": "staff"},
]

def get_staff_list():
    df = get_data("staff")
    if df is not None and "username" in df.columns and "password" in df.columns:
        return df.to_dict("records")
    return DEFAULT_STAFF.copy()


def login_form():
    st.markdown("""
    <div class="gk-header">
        <h1>📦 GudangKit</h1>
        <p>Masuk untuk mengakses dashboard sortir order.</p>
    </div>
    """, unsafe_allow_html=True)
    _, mid, _ = st.columns([1, 1.2, 1])
    with mid:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Masuk", type="primary", use_container_width=True)
        if submitted:
            staff_list = get_staff_list()
            match = next((s for s in staff_list if str(s.get("username", "")).strip() == username.strip()), None)
            if match and str(match.get("password", "")) == password:
                st.session_state.logged_in = True
                st.session_state.current_user = match
                st.rerun()
            else:
                st.error("Username atau password salah.")
        st.caption("Akun default: `admin` / `admin123` atau `staff` / `staff123`. Bisa diganti lewat tab `staff` di Google Sheets (kolom: username, password, nama, role).")


# ==================================================================
# GAYA / CSS
# ==================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@600;700&family=JetBrains+Mono:wght@500;700&display=swap');

.block-container{ padding-top: 1.2rem; max-width: 1180px; }

.gk-header{
    background: linear-gradient(120deg, #1F3E3B, #2B5450);
    color: #fff; padding: 22px 26px; border-radius: 14px; margin-bottom: 22px;
}
.gk-header h1{ font-family: 'Space Grotesk', sans-serif; font-size: 24px; margin: 0; font-weight: 700; }
.gk-header p{ opacity: 0.85; font-size: 13.5px; margin: 8px 0 0; max-width: 640px; line-height: 1.5; }

div[data-testid="stMetric"]{
    background: #fff; border: 1px solid #E4DECF; border-radius: 12px;
    padding: 12px 14px 6px; box-shadow: 0 1px 2px rgba(28,35,33,0.04);
}
div[data-testid="stMetricValue"]{ font-family: 'JetBrains Mono', monospace; color: #1F3E3B; }

.status-stamp{
    display:inline-block; font-size: 11px; font-weight:700; text-transform:uppercase;
    letter-spacing:0.03em; padding: 3px 10px; border-radius: 100px; border: 1.5px dashed transparent;
}
.stamp-menunggu{ background:#F5E7CC; color:#B9822B; border-color:#E8CE9C; }
.stamp-proses{ background:#DCE9EC; color:#2B5450; border-color:#B7D3D8; }
.stamp-selesai{ background:#E1EEE3; color:#3E7D57; border-color:#B9DBC1; }

.courier-tag{
    font-family:'JetBrains Mono', monospace; font-size:11.5px; font-weight:700;
    padding: 2px 9px; border-radius: 7px; background:#F1DCC7; color:#A8582F;
}
.resi-code{ font-family:'JetBrains Mono', monospace; color:#8B948F; font-size:12px; }

.gk-alert{
    background:#F5E7CC; border:1px solid #E8CE9C; border-radius:10px; padding:10px 14px;
    font-size:13px; color:#7A5A16; margin-bottom: 14px;
}
.big-metric{ text-align:center; padding: 10px 0; }
.big-metric .num{ font-family:'JetBrains Mono',monospace; font-size:84px; font-weight:700; color:#1F3E3B; line-height:1; }
.big-metric .label{ font-size:17px; color:#5C6763; margin-top:8px; letter-spacing:0.03em; }
</style>
""", unsafe_allow_html=True)

# ==================================================================
# LOGIN GATE
# ==================================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if not st.session_state.logged_in:
    login_form()
    st.stop()

# ==================================================================
# STATE AWAL
# ==================================================================
DEFAULT_COURIERS = [
    {"nama_kurir": "JNE", "keywords": "JNE, JALUR NUGRAHA"},
    {"nama_kurir": "J&T", "keywords": "J&T, JNT, J & T"},
    {"nama_kurir": "SiCepat", "keywords": "SICEPAT, SI CEPAT"},
    {"nama_kurir": "AnterAja", "keywords": "ANTERAJA, ANTER AJA"},
    {"nama_kurir": "Ninja Xpress", "keywords": "NINJA, NINJA XPRESS"},
    {"nama_kurir": "ID Express", "keywords": "ID EXPRESS, IDEXPRESS"},
    {"nama_kurir": "Lion Parcel", "keywords": "LION PARCEL, LION"},
    {"nama_kurir": "Wahana", "keywords": "WAHANA"},
    {"nama_kurir": "Pos Indonesia", "keywords": "POS INDONESIA, POS-"},
]

if "couriers" not in st.session_state:
    sheet_df = get_data("master_kurir")
    if sheet_df is not None and "nama_kurir" in sheet_df.columns and "keywords" in sheet_df.columns:
        st.session_state.couriers = sheet_df.to_dict("records")
    else:
        st.session_state.couriers = DEFAULT_COURIERS.copy()

if "batches" not in st.session_state:
    st.session_state.batches = []
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0
if "warehouse_name" not in st.session_state:
    st.session_state.warehouse_name = "Reza Warehouse Palembang"
if "staff_email" not in st.session_state:
    st.session_state.staff_email = "rezasaputra42@gmail.com"
if "layar_gudang" not in st.session_state:
    st.session_state.layar_gudang = False
if "prev_menunggu" not in st.session_state:
    st.session_state.prev_menunggu = 0
if "gspread_enabled" not in st.session_state:
    st.session_state.gspread_enabled = False


# ==================================================================
# FUNGSI DETEKSI PDF
# ==================================================================
def extract_pdf_text(file_bytes, max_pages=3):
    if not PDF_OK:
        return ""
    try:
        text = ""
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages[:max_pages]:
                t = page.extract_text() or ""
                text += " " + t
        return text.upper()
    except Exception:
        return ""


def detect_courier(text):
    for c in st.session_state.couriers:
        keywords = [k.strip().upper() for k in str(c["keywords"]).split(",") if k.strip()]
        for kw in keywords:
            if kw in text:
                return c["nama_kurir"]
    return None


def detect_resi(text):
    patterns = [
        r"\b[A-Z]{2,4}\d{8,14}\b",
        r"RESI[:\s]*([A-Z0-9]{8,16})",
        r"\b\d{10,16}\b",
    ]
    for p in patterns:
        m = re.search(p, text)
        if m:
            return (m.group(1) if m.groups() else m.group(0))[:16]
    return None


def fmt_size(num_bytes):
    if num_bytes < 1024:
        return f"{num_bytes} B"
    if num_bytes < 1024 * 1024:
        return f"{num_bytes/1024:.1f} KB"
    return f"{num_bytes/1024/1024:.2f} MB"


# ==================================================================
# CETAK LABEL PER KURIR (gabungkan PDF asli jadi 1 file per kurir)
# ==================================================================
def generate_courier_pdf(kurir_name, only_today=True):
    if not MERGE_OK:
        return None
    writer = PdfWriter()
    today = datetime.now().date()
    added = 0
    for b in st.session_state.batches:
        if only_today and b["created_at"].date() != today:
            continue
        for f in b["files"]:
            if f["status"] == "selesai" and f["kurir"] == kurir_name and f.get("bytes"):
                try:
                    reader = PdfReader(io.BytesIO(f["bytes"]))
                    for page in reader.pages:
                        writer.add_page(page)
                    added += 1
                except Exception:
                    continue
    if added == 0:
        return None
    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()


# ==================================================================
# EXPORT REKAP KE EXCEL
# ==================================================================
def export_rekap_excel(df):
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Rekap Harian")
    return buf.getvalue()


# ==================================================================
# BUNYI NOTIFIKASI (WAV beep dibuat langsung, tanpa file eksternal)
# ==================================================================
def make_beep_data_uri(freq=880, duration=0.18, volume=0.4, rate=44100):
    n_samples = int(rate * duration)
    frames = bytearray()
    for i in range(n_samples):
        t = i / rate
        value = int(volume * 32767 * math.sin(2 * math.pi * freq * t))
        frames += struct.pack("<h", value)
    data_size = len(frames)
    header = (
        b"RIFF" + struct.pack("<I", 36 + data_size) + b"WAVEfmt "
        + struct.pack("<IHHIIHH", 16, 1, 1, rate, rate * 2, 2, 16)
        + b"data" + struct.pack("<I", data_size)
    )
    return "data:audio/wav;base64," + base64.b64encode(header + bytes(frames)).decode()

BEEP_URI = make_beep_data_uri()


# ==================================================================
# AKSI
# ==================================================================
def buat_batch(files):
    if not files:
        return
    batch_id = "B" + datetime.now().strftime("%y%m%d-%H%M%S")
    file_entries = []
    for f in files:
        raw = f.read()
        file_entries.append({
            "name": f.name, "size": len(raw), "status": "menunggu",
            "kurir": None, "resi": None, "bytes": raw,
        })
    batch = {
        "id": batch_id,
        "created_at": datetime.now(),
        "dari": st.session_state.warehouse_name.split(" ")[0],
        "oleh": st.session_state.current_user.get("nama", "-"),
        "status": "menunggu",
        "files": file_entries,
    }
    st.session_state.batches.insert(0, batch)
    st.session_state.uploader_key += 1
    st.success(f"Batch {batch_id} dibuat dengan {len(files)} file.")


def proses_batch(batch_id):
    batch = next((b for b in st.session_state.batches if b["id"] == batch_id), None)
    if not batch:
        return
    batch["status"] = "diproses"
    progress = st.progress(0, text="Memproses file...")
    total = len(batch["files"])
    for i, f in enumerate(batch["files"]):
        f["status"] = "proses"
        text = extract_pdf_text(f["bytes"])
        kurir = detect_courier(text) or st.session_state.couriers[i % len(st.session_state.couriers)]["nama_kurir"]
        resi = detect_resi(text) or f"AUTO{datetime.now().strftime('%H%M%S')}{i:03d}"
        f["kurir"] = kurir
        f["resi"] = resi
        f["status"] = "selesai"
        if st.session_state.gspread_enabled:
            append_row_to_sheet("log_resi", [batch_id, f["name"], kurir, resi, datetime.now().isoformat()])
        progress.progress((i + 1) / total, text=f"Memproses {f['name']}...")
    batch["status"] = "selesai"
    progress.empty()
    st.success(f"Batch {batch_id} selesai diproses ✅")


# ==================================================================
# HEADER + BUNYI NOTIFIKASI
# ==================================================================
current_menunggu = sum(1 for b in st.session_state.batches if b["status"] == "menunggu")
if st.session_state.layar_gudang and current_menunggu > st.session_state.prev_menunggu:
    st.markdown(f'<audio autoplay><source src="{BEEP_URI}" type="audio/wav"></audio>', unsafe_allow_html=True)
st.session_state.prev_menunggu = current_menunggu

st.markdown("""
<div class="gk-header">
    <h1>📦 GudangKit — Dashboard Sortir Order</h1>
    <p>Upload PDF label/resi → label tersortir per kurir + data + rekap. Data kurir & staff dibaca dari Google Sheets; hasil sortir tersimpan di sesi ini.</p>
</div>
""", unsafe_allow_html=True)

# ==================================================================
# SIDEBAR
# ==================================================================
with st.sidebar:
    user = st.session_state.current_user
    st.markdown(f"**{st.session_state.warehouse_name}**")
    st.caption(f"{user.get('nama','-')} · {user.get('role','staff')}")
    if st.button("🚪 Keluar", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.rerun()
    st.divider()

    if current_menunggu:
        st.markdown(f'<div class="gk-alert">📥 <b>{current_menunggu} kiriman</b> menunggu diproses.</div>', unsafe_allow_html=True)

    page = st.radio(
        "Menu",
        ["Input File", "Proses Batch", "Rekap Harian", "Master Data", "Pengaturan"],
        label_visibility="collapsed",
    )
    st.divider()
    st.caption("GudangKit v2 · data diproses di sesi Streamlit ini")
    missing = []
    if not PDF_OK: missing.append("pdfplumber")
    if not MERGE_OK: missing.append("pypdf")
    if missing:
        st.warning(f"Modul belum terpasang: {', '.join(missing)}. Tambahkan ke requirements.txt.", icon="⚠️")

# ==================================================================
# HALAMAN: INPUT FILE
# ==================================================================
if page == "Input File":
    st.subheader("📤 Input File — Upload Label / Resi")
    files = st.file_uploader(
        "Upload PDF label pengiriman / resi (bisa pilih banyak file)",
        type=["pdf"],
        accept_multiple_files=True,
        key=f"uploader_{st.session_state.uploader_key}",
    )
    if files:
        st.write(f"**{len(files)} file siap dijadikan batch:**")
        for f in files:
            st.write(f"📄 {f.name} — {fmt_size(f.size)}")
        if st.button("📦 Buat Batch", type="primary"):
            buat_batch(files)
            st.rerun()
    else:
        st.info("Belum ada file dipilih. Upload PDF label/resi untuk memulai batch baru.")

# ==================================================================
# HALAMAN: PROSES BATCH
# ==================================================================
elif page == "Proses Batch":
    st.subheader("⚙️ Proses Batch — kiriman dari Finance")
    st.session_state.layar_gudang = st.toggle(
        "🖥️ Mode layar gudang — papan besar + bunyi saat ada kiriman baru",
        value=st.session_state.layar_gudang,
    )

    today = datetime.now().date()
    resi_today = sum(1 for b in st.session_state.batches if b["created_at"].date() == today for f in b["files"] if f["status"] == "selesai")
    qty_today = sum(len(b["files"]) for b in st.session_state.batches if b["created_at"].date() == today)
    size_today = sum(f["size"] for b in st.session_state.batches if b["created_at"].date() == today for f in b["files"])
    menunggu = sum(1 for b in st.session_state.batches if b["status"] == "menunggu")
    diproses = sum(1 for b in st.session_state.batches if b["status"] == "diproses")

    if st.session_state.layar_gudang:
        # ---- MODE LAYAR GUDANG (papan besar) ----
        cols = st.columns(3)
        big_data = [("⏳ MENUNGGU", menunggu), ("⚙️ DIPROSES", diproses), ("🏷️ RESI HARI INI", resi_today)]
        for col, (label, val) in zip(cols, big_data):
            col.markdown(f'<div class="big-metric"><div class="num">{val}</div><div class="label">{label}</div></div>', unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center;color:#8B948F;margin-top:16px;'>Update terakhir: {datetime.now().strftime('%H:%M:%S')}</p>", unsafe_allow_html=True)
        try:
            from streamlit_autorefresh import st_autorefresh
            st_autorefresh(interval=15000, key="layar_gudang_refresh")
        except ImportError:
            st.button("🔄 Refresh manual")
            st.caption("Tambahkan `streamlit-autorefresh` ke requirements.txt supaya papan ini refresh otomatis.")
    else:
        # ---- MODE NORMAL ----
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("⏳ Menunggu diproses", menunggu)
        c2.metric("⚙️ Sedang diproses", diproses)
        c3.metric("🏷️ Resi hari ini", resi_today)
        c4.metric("📦 Qty hari ini", qty_today)
        c5.metric("🗃️ Isi kotak masuk", fmt_size(size_today))

        st.markdown("#### Antrian (yang paling lama dulu)")
        if not st.session_state.batches:
            st.info("Belum ada batch. Buka **Input File** untuk upload PDF pertamamu.")
        else:
            for batch in st.session_state.batches:
                total_size = fmt_size(sum(f["size"] for f in batch["files"]))
                label = f'{batch["status"].upper()} · {batch["id"]} · {batch["created_at"].strftime("%d %b %H:%M")} · {len(batch["files"])} file · {total_size} · dari {batch["dari"]}'
                with st.expander(label, expanded=(batch["status"] == "diproses")):
                    stamp_class = {"menunggu": "stamp-menunggu", "diproses": "stamp-proses", "selesai": "stamp-selesai"}[batch["status"]]
                    st.markdown(f'<span class="status-stamp {stamp_class}">{batch["status"]}</span>', unsafe_allow_html=True)
                    if batch["status"] == "menunggu":
                        if st.button("▶ Proses Sekarang", key=f"proses_{batch['id']}"):
                            proses_batch(batch["id"])
                            st.rerun()
                    for f in batch["files"]:
                        icon = "✅" if f["status"] == "selesai" else ("⏳" if f["status"] == "proses" else "📄")
                        kurir_html = f'<span class="courier-tag">{f["kurir"]}</span>' if f["kurir"] else ""
                        resi_html = f'<span class="resi-code">{f["resi"]}</span>' if f["resi"] else ""
                        st.markdown(f"{icon} {f['name']} &nbsp; {resi_html} &nbsp; {kurir_html}", unsafe_allow_html=True)

        # ---- CETAK LABEL PER KURIR ----
        st.markdown("#### 🖨️ Cetak label per kurir (hari ini)")
        if not MERGE_OK:
            st.info("Tambahkan `pypdf` ke requirements.txt supaya fitur cetak label aktif.")
        else:
            kurir_today = {}
            for b in st.session_state.batches:
                if b["created_at"].date() != today:
                    continue
                for f in b["files"]:
                    if f["status"] == "selesai" and f["kurir"]:
                        kurir_today[f["kurir"]] = kurir_today.get(f["kurir"], 0) + 1
            if not kurir_today:
                st.caption("Belum ada label selesai diproses hari ini.")
            else:
                cols = st.columns(min(4, len(kurir_today)))
                for i, (kurir, count) in enumerate(sorted(kurir_today.items(), key=lambda x: -x[1])):
                    pdf_bytes = generate_courier_pdf(kurir)
                    with cols[i % len(cols)]:
                        st.write(f"**{kurir}** · {count} label")
                        if pdf_bytes:
                            st.download_button(
                                "⬇️ Download PDF",
                                data=pdf_bytes,
                                file_name=f"label_{kurir.replace(' ', '_')}_{today.isoformat()}.pdf",
                                mime="application/pdf",
                                key=f"dl_{kurir}",
                            )

# ==================================================================
# HALAMAN: REKAP HARIAN
# ==================================================================
elif page == "Rekap Harian":
    st.subheader("📊 Rekap Harian")
    today = datetime.now().date()
    rows = []
    for b in st.session_state.batches:
        if b["created_at"].date() != today:
            continue
        for f in b["files"]:
            if f["kurir"]:
                rows.append(f["kurir"])

    if not rows:
        st.info("Belum ada resi diproses hari ini.")
    else:
        rekap_df = pd.Series(rows).value_counts().rename_axis("kurir").reset_index(name="jumlah_resi")
        c1, c2 = st.columns(2)
        c1.metric("🏷️ Total resi hari ini", len(rows))
        c2.metric("📦 Batch selesai", sum(1 for b in st.session_state.batches if b["status"] == "selesai"))
        st.markdown("#### Rekap per kurir — hari ini")
        st.bar_chart(rekap_df.set_index("kurir"))
        st.dataframe(rekap_df, use_container_width=True, hide_index=True)

        excel_bytes = export_rekap_excel(rekap_df)
        st.download_button(
            "⬇️ Export rekap ke Excel",
            data=excel_bytes,
            file_name=f"rekap_harian_{today.isoformat()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

# ==================================================================
# HALAMAN: MASTER DATA
# ==================================================================
elif page == "Master Data":
    st.subheader("🗂️ Master Data — Daftar Kurir")
    st.caption("Sumber data: tab `master_kurir` di Google Sheets (kolom `nama_kurir`, `keywords`). Kalau tab belum ada, dipakai daftar bawaan.")

    df = pd.DataFrame(st.session_state.couriers)
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("#### Tambah kurir baru (berlaku untuk sesi ini)")
    with st.form("tambah_kurir", clear_on_submit=True):
        col1, col2 = st.columns([1, 2])
        nama = col1.text_input("Nama kurir")
        keywords = col2.text_input("Kata kunci deteksi (pisahkan koma)")
        submitted = st.form_submit_button("+ Tambah kurir")
        if submitted and nama.strip():
            st.session_state.couriers.append({"nama_kurir": nama.strip(), "keywords": keywords})
            st.success(f"Kurir '{nama}' ditambahkan.")
            st.rerun()

    hapus = st.selectbox("Hapus kurir", ["—"] + [c["nama_kurir"] for c in st.session_state.couriers])
    if hapus != "—" and st.button("🗑️ Hapus kurir terpilih"):
        st.session_state.couriers = [c for c in st.session_state.couriers if c["nama_kurir"] != hapus]
        st.rerun()

# ==================================================================
# HALAMAN: PENGATURAN
# ==================================================================
elif page == "Pengaturan":
    st.subheader("🔧 Pengaturan")
    st.session_state.warehouse_name = st.text_input("Nama gudang", value=st.session_state.warehouse_name)
    st.session_state.staff_email = st.text_input("Email staff", value=st.session_state.staff_email)

    st.divider()
    st.markdown("#### Status koneksi Google Sheets")
    test_df = get_data("master_kurir")
    if test_df is not None:
        st.success(f"Berhasil membaca tab `master_kurir` ({len(test_df)} baris).")
    else:
        st.warning("Tab `master_kurir` belum terbaca — cek apakah Sheet sudah di-publish ke web dan nama tab sudah benar.")

    client = get_gspread_client()
    st.session_state.gspread_enabled = client is not None
    if client:
        st.success("Kredensial Google service account terdeteksi — hasil proses akan ditulis ke tab `log_resi`.")
    else:
        st.info("Kredensial service account belum diatur — hasil proses hanya tersimpan di sesi ini (hilang saat refresh). Kalau nanti butuh penyimpanan permanen, tinggal isi `st.secrets['gcp_service_account']`.")

    st.divider()
    st.markdown("#### Daftar staff")
    st.caption("Sumber: tab `staff` di Google Sheets (kolom: username, password, nama, role). Kalau belum ada, dipakai akun bawaan.")
    staff_df = pd.DataFrame(get_staff_list())
    if "password" in staff_df.columns:
        staff_df = staff_df.drop(columns=["password"])
    st.dataframe(staff_df, use_container_width=True, hide_index=True)
