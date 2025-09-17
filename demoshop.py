import streamlit as st
from PIL import Image
import requests
from io import BytesIO
import datetime
import uuid
import copy
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

# ==============================
# Cấu hình trang
# ==============================
st.set_page_config(page_title="Mini Shop", page_icon="🛍️", layout="wide")

# ==============================
# Google Sheets Setup
# ==============================
SHEET_NAME = "Orders"
SPREADSHEET_ID = "YOUR_SHEET_ID_HERE"  # 👉 thay bằng ID Google Sheet của bạn

# Tải credentials từ file JSON (Service Account)
creds = Credentials.from_service_account_file(
    "service_account.json",   # 👉 thay đường dẫn file JSON key
    scopes=["https://www.googleapis.com/auth/spreadsheets"]
)
client = gspread.authorize(creds)
sheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)

# ==============================
# Helpers
# ==============================
def gdrive_thumbnail(link: str, width: int = 800) -> str:
    if "drive.google.com" not in link:
        return link
    file_id = None
    if "/file/d/" in link:
        file_id = link.split("/file/d/")[1].split("/")[0]
    elif "id=" in link:
        file_id = link.split("id=")[1].split("&")[0]
    if not file_id:
        return link
    return f"https://drive.google.com/thumbnail?id={file_id}&sz=w{width}"

def load_image(link: str):
    try:
        url = gdrive_thumbnail(link, 800)
        r = requests.get(url, timeout=8)
        r.raise_for_status()
        return Image.open(BytesIO(r.content))
    except Exception:
        return None

def ensure_cart_schema():
    for it in st.session_state.cart:
        if "qty" not in it:
            it["qty"] = 1

def add_to_cart(product, qty: int = 1):
    ensure_cart_schema()
    for it in st.session_state.cart:
        if it["id"] == product["id"]:
            it["qty"] += qty
            return
    item = product.copy()
    item["qty"] = qty
    st.session_state.cart.append(item)

# ==============================
# Google Sheets Functions
# ==============================
def load_orders():
    data = sheet.get_all_records()
    return pd.DataFrame(data)

def save_order(order):
    row = [
        order["id"],
        order["user"],
        str(order["items"]),
        order["status"],
        order["time"]
    ]
    sheet.append_row(row)

def update_order_status(order_id, new_status):
    """Tìm dòng có order_id và update status"""
    values = sheet.get_all_values()
    header = values[0]
    id_index = header.index("id") + 1  # cột id
    status_index = header.index("status") + 1  # cột status

    for i, row in enumerate(values[1:], start=2):  # bắt đầu từ dòng 2
        if row[id_index - 1] == order_id:
            sheet.update_cell(i, status_index, new_status)
            return True
    return False

# ==============================
# Dữ liệu mẫu
# ==============================
products = [
    {"id": 1, "name": "Quần bơi",   "price": 120000,
     "image": "https://drive.google.com/file/d/1s6sJALOs2IxX5f9nqa4Tf8zut_U9KE3O/view?usp=drive_link"},
    {"id": 2, "name": "Quần sịp", "price": 250000,
     "image": "https://drive.google.com/file/d/1UpNF_Fd5gWbrtEliUbD7KDRilpcnQK3H/view?usp=drive_link"},
    {"id": 3, "name": "Áo khoác",  "price": 350000,
     "image": "https://drive.google.com/file/d/1hZ2skulhj5YB1EOV1ElcAQG9bRe-m8Ta/view?usp=drive_link"},
    {"id": 4, "name": "Áo ba lỗ",   "price": 450000,
     "image": "https://drive.google.com/file/d/1tfyYp_9L2GU5zUh3w_GSvfcpa_hNlJUk/view?usp=drive_link"},
    {"id": 5, "name" : "Áo gòn",       "price" : 600000,
     "image": "https://drive.google.com/file/d/144OpPO0kfqMUUuNga8LJIFwqnNlYQMQG/view?usp=drive_link"}
]

ADMIN_USER = "admin"
ADMIN_PASS = "123"

# ==============================
# Session state
# ==============================
if "cart" not in st.session_state:
    st.session_state.cart = []
if "username" not in st.session_state:
    st.session_state.username = ""
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ==============================
# Sidebar Login
# ==============================
st.sidebar.markdown("## 👤 Tài khoản")

if not st.session_state.logged_in:
    with st.sidebar.expander("Đăng nhập / Đăng ký nhanh", expanded=True):
        user = st.text_input("Tên đăng nhập", key="username_input")
        pwd  = st.text_input("Mật khẩu", type="password", key="password_input")
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("Đăng nhập thường"):
                if user.strip():
                    st.session_state.logged_in = True
                    st.session_state.is_admin = False
                    st.session_state.username = user.strip()
                    st.rerun()
        with col_b:
            if st.button("Đăng nhập Admin"):
                if user == ADMIN_USER and pwd == ADMIN_PASS:
                    st.session_state.logged_in = True
                    st.session_state.is_admin = True
                    st.session_state.username = ADMIN_USER
                    st.rerun()
                else:
                    st.error("Sai tài khoản/mật khẩu admin.")
else:
    st.sidebar.write(f"**Đang đăng nhập:** {st.session_state.username or 'Khách'}")
    if st.sidebar.button("🚪 Đăng xuất"):
        st.session_state.logged_in = False
        st.session_state.is_admin = False
        st.session_state.username = ""
        st.rerun()

# Menu
if st.session_state.is_admin:
    menu = st.sidebar.radio("Menu", ["🏬 Trang chủ", "🛒 Giỏ hàng", "📦 Đơn của tôi", "📋 Quản lý đơn hàng"])
else:
    menu = st.sidebar.radio("Menu", ["🏬 Trang chủ", "🛒 Giỏ hàng", "📦 Đơn của tôi"])

# ==============================
# Trang chủ
# ==============================
if menu == "🏬 Trang chủ":
    st.title("🛍️ Cửa hàng online")

    cols = st.columns(2)
    for idx, p in enumerate(products):
        with cols[idx % 2]:
            img = load_image(p["image"])
            if img:
                st.image(img, caption=p["name"], use_column_width=True)
            else:
                st.image(gdrive_thumbnail(p["image"]), caption=p["name"], use_column_width=True)

            st.markdown(f"**{p['name']}**")
            st.write(f"💰 {p['price']:,} VND")

            qty = st.number_input(f"Số lượng ({p['name']})", min_value=1, value=1, key=f"home_qty_{p['id']}")
            if st.button("🛒 Thêm vào giỏ", key=f"add_{p['id']}"):
                add_to_cart(p, qty)
                st.success(f"Đã thêm {qty} {p['name']} vào giỏ!")

# ==============================
# Giỏ hàng
# ==============================
elif menu == "🛒 Giỏ hàng":
    st.title("🛒 Giỏ hàng của bạn")
    ensure_cart_schema()

    if not st.session_state.cart:
        st.info("Giỏ hàng đang trống.")
    else:
        total = 0
        for item in st.session_state.cart:
            st.write(f"- {item['name']} x {item['qty']} = {(item['price']*item['qty']):,} VND")
            total += item["price"] * item["qty"]

        st.subheader(f"✅ Tổng cộng: {total:,} VND")

        if st.button("📦 Xác nhận đặt hàng"):
            buyer = st.session_state.username if st.session_state.username else "Khách"
            order = {
                "id": str(uuid.uuid4())[:8],
                "user": buyer,
                "items": copy.deepcopy(st.session_state.cart),
                "status": "Chờ xác nhận",
                "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            save_order(order)
            st.session_state.cart.clear()
            st.success(f"Đặt hàng thành công! Mã đơn: {order['id']}")
            st.rerun()

# ==============================
# Đơn hàng của tôi
# ==============================
elif menu == "📦 Đơn của tôi":
    st.title("📦 Đơn hàng của tôi")
    current_user = st.session_state.username if st.session_state.username else "Khách"
    df_orders = load_orders()
    if df_orders.empty:
        st.info("Bạn chưa có đơn hàng nào.")
    else:
        my_orders = df_orders[df_orders["user"] == current_user]
        if my_orders.empty:
            st.info("Bạn chưa có đơn hàng nào.")
        else:
            st.dataframe(my_orders)

# ==============================
# Admin: Quản lý đơn hàng
# ==============================
elif menu == "📋 Quản lý đơn hàng":
    if not st.session_state.is_admin:
        st.error("Bạn không có quyền truy cập.")
    else:
        st.title("📋 Quản lý tất cả đơn hàng")
        df_orders = load_orders()
        if df_orders.empty:
            st.info("Chưa có đơn hàng nào.")
        else:
            for _, row in df_orders.iterrows():
                with st.expander(f"🆔 Đơn #{row['id']} • {row['user']} • {row['time']} • {row['status']}"):
                    st.write(f"**Chi tiết items:** {row['items']}")
                    col1, col2 = st.columns(2)
                    with col1:
                        if row["status"] == "Chờ xác nhận":
                            if st.button(f"✅ Xác nhận #{row['id']}"):
                                update_order_status(row["id"], "Đã xác nhận")
                                st.success(f"Đã xác nhận đơn #{row['id']}")
                                st.rerun()
                    with col2:
                        if row["status"] == "Chờ xác nhận":
                            if st.button(f"❌ Hủy #{row['id']}"):
                                update_order_status(row["id"], "Đã hủy")
                                st.warning(f"Đã hủy đơn #{row['id']}")
                                st.rerun()
