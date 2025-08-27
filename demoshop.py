import streamlit as st
from PIL import Image
import requests
from io import BytesIO
import datetime
import uuid
import copy

# ==============================
# Cấu hình trang
# ==============================
st.set_page_config(page_title="Mini Shop", page_icon="🛍️", layout="wide")

# ==============================
# Helpers
# ==============================
def gdrive_thumbnail(link: str, width: int = 800) -> str:
    """Chuyển link Drive thành link thumbnail (nhẹ, nhanh)"""
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
    """Tải ảnh (ưu tiên thumbnail drive). Có thể bỏ qua nếu muốn dùng st.image(link) trực tiếp."""
    try:
        url = gdrive_thumbnail(link, 800)
        r = requests.get(url, timeout=8)
        r.raise_for_status()
        return Image.open(BytesIO(r.content))
    except Exception:
        return None

def ensure_cart_schema():
    """Đảm bảo mọi item trong giỏ đều có qty"""
    for it in st.session_state.cart:
        if "qty" not in it:
            it["qty"] = 1

def add_to_cart(product, qty: int = 1):
    """Cộng dồn sản phẩm vào giỏ"""
    ensure_cart_schema()
    for it in st.session_state.cart:
        if it["id"] == product["id"]:
            it["qty"] += qty
            return
    item = product.copy()
    item["qty"] = qty
    st.session_state.cart.append(item)

def cart_total():
    return sum(it["price"] * it["qty"] for it in st.session_state.cart)

def order_total(order):
    return sum(it["price"] * it["qty"] for it in order["items"])

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
ADMIN_PASS = "123"   # đổi tùy ý

# ==============================
# Session state
# ==============================
if "cart" not in st.session_state:
    st.session_state.cart = []
if "orders" not in st.session_state:
    st.session_state.orders = []   # tất cả đơn của mọi user
if "username" not in st.session_state:
    st.session_state.username = "" # "" = khách vãng lai
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "new_order" not in st.session_state:
    st.session_state.new_order = False  # bật khi có đơn mới để báo admin

# ==============================
# Sidebar: Login/Role + Menu
# ==============================
st.sidebar.markdown("## 👤 Tài khoản")

if not st.session_state.logged_in:
    with st.sidebar.expander("Đăng nhập / Đăng ký nhanh", expanded=True):
        user = st.text_input("Tên đăng nhập (để theo dõi đơn)", key="username_input")
        pwd  = st.text_input("Mật khẩu", type="password", key="password_input")
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("Đăng nhập thường"):
                if user.strip():
                    st.session_state.logged_in = True
                    st.session_state.is_admin = False
                    st.session_state.username = user.strip()
                    st.success(f"Xin chào {st.session_state.username} 👋")
                    st.rerun()
                else:
                    st.warning("Nhập tên đăng nhập để tiếp tục.")
        with col_b:
            if st.button("Đăng nhập Admin"):
                if user == ADMIN_USER and pwd == ADMIN_PASS:
                    st.session_state.logged_in = True
                    st.session_state.is_admin = True
                    st.session_state.username = ADMIN_USER
                    st.success("Đăng nhập Admin thành công ✅")
                    st.rerun()
                else:
                    st.error("Sai tài khoản/mật khẩu admin.")
else:
    st.sidebar.write(f"**Đang đăng nhập:** {st.session_state.username or 'Khách'}")
    if st.sidebar.button("🚪 Đăng xuất"):
        st.session_state.logged_in = False
        st.session_state.is_admin = False
        st.session_state.username = ""
        st.success("Đã đăng xuất.")
        st.rerun()

# Badge thông báo cho admin khi có đơn mới
if st.session_state.is_admin and st.session_state.new_order:
    st.sidebar.error("🔔 Có đơn hàng mới!")

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

    ensure_cart_schema()

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
        remove_indices = []

        for i, item in enumerate(st.session_state.cart):
            c1, c2, c3, c4 = st.columns([4, 2, 2, 1])
            with c1:
                st.write(f"**{item['name']}**")
                st.caption(f"Đơn giá: {item['price']:,} VND")
            with c2:
                new_qty = st.number_input("Số lượng", min_value=1, value=int(item["qty"]), key=f"cart_qty_{i}")
                item["qty"] = int(new_qty)
            with c3:
                st.write(f"Thành tiền: {(item['qty']*item['price']):,} VND")
            with c4:
                if st.button("❌", key=f"rm_{i}"):
                    remove_indices.append(i)

            total += item["price"] * item["qty"]

        # Xóa sau khi lặp để tránh lỗi
        for idx in sorted(remove_indices, reverse=True):
            st.session_state.cart.pop(idx)
            st.experimental_rerun()

        st.subheader(f"✅ Tổng cộng: {total:,} VND")

        # Đặt hàng
        if st.button("📦 Xác nhận đặt hàng"):
            buyer = st.session_state.username if st.session_state.username else "Khách"
            order = {
                "id": str(uuid.uuid4())[:8],
                "user": buyer,
                "items": copy.deepcopy(st.session_state.cart),
                "status": "Chờ xác nhận",
                "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            st.session_state.orders.append(order)
            st.session_state.cart.clear()
            st.session_state.new_order = True  # 🔔 báo admin
            st.success(f"Đặt hàng thành công! Mã đơn: {order['id']}")
            st.rerun()

# ==============================
# Đơn hàng của tôi (chỉ của user hiện tại)
# ==============================
elif menu == "📦 Đơn của tôi":
    st.title("📦 Đơn hàng của tôi")

    current_user = st.session_state.username if st.session_state.username else "Khách"
    my_orders = [o for o in st.session_state.orders if o["user"] == current_user]

    if not my_orders:
        st.info("Bạn chưa có đơn hàng nào.")
    else:
        for o in my_orders:
            with st.expander(f"🆔 Đơn #{o['id']} • {o['time']} • Trạng thái: {o['status']}", expanded=False):
                total = 0
                for it in o["items"]:
                    st.write(f"- {it['name']} x {it['qty']} = {(it['price']*it['qty']):,} VND")
                    total += it["price"] * it["qty"]
                st.write(f"**Tổng cộng:** {total:,} VND")

                if o["status"] == "Chờ xác nhận":
                    if st.button(f"❌ Hủy đơn #{o['id']}", key=f"cancel_{o['id']}"):
                        # Có thể xóa hẳn, nhưng tốt hơn chuyển trạng thái để admin vẫn thấy lịch sử
                        o["status"] = "Đã hủy"
                        st.warning(f"Đã hủy đơn #{o['id']}.")
                        st.rerun()

# ==============================
# Admin: Quản lý tất cả đơn
# ==============================
elif menu == "📋 Quản lý đơn hàng":
    if not st.session_state.is_admin:
        st.error("Bạn không có quyền truy cập trang này.")
    else:
        st.title("📋 Quản lý tất cả đơn hàng")

        # Hiển thị thông báo đơn mới một lần, sau đó tắt cờ
        if st.session_state.new_order:
            st.info("🔔 Có đơn hàng mới vừa được tạo.")
            st.session_state.new_order = False

        if not st.session_state.orders:
            st.info("Chưa có đơn hàng nào.")
        else:
            # Filter nhanh
            filter_status = st.multiselect(
                "Lọc theo trạng thái",
                options=["Chờ xác nhận", "Đã xác nhận", "Đã hủy"],
                default=["Chờ xác nhận", "Đã xác nhận", "Đã hủy"]
            )

            # Danh sách đơn
            for o in st.session_state.orders:
                if o["status"] not in filter_status:
                    continue

                with st.expander(f"🆔 Đơn #{o['id']} • {o['user']} • {o['time']} • {o['status']}", expanded=False):
                    total = 0
                    for it in o["items"]:
                        st.write(f"- {it['name']} x {it['qty']} = {(it['price']*it['qty']):,} VND")
                        total += it["price"] * it["qty"]
                    st.write(f"**Tổng cộng:** {total:,} VND")

                    c1, c2, c3 = st.columns(3)
                    with c1:
                        if o["status"] == "Chờ xác nhận":
                            if st.button(f"✅ Xác nhận #{o['id']}", key=f"adm_ok_{o['id']}"):
                                o["status"] = "Đã xác nhận"
                                st.success(f"Đã xác nhận đơn #{o['id']}")
                                st.rerun()
                    with c2:
                        if o["status"] == "Chờ xác nhận":
                            if st.button(f"❌ Hủy #{o['id']}", key=f"adm_cancel_{o['id']}"):
                                o["status"] = "Đã hủy"
                                st.warning(f"Đã hủy đơn #{o['id']}")
                                st.rerun()
                    with c3:
                        if st.button(f"🧾 In/Export #{o['id']}", key=f"adm_export_{o['id']}"):
                            st.info("Demo: chỗ này có thể xuất PDF/CSV về sau.")





