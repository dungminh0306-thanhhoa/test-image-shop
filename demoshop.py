import streamlit as st

# ================== DỮ LIỆU SẢN PHẨM ==================
products = [
    {"id": 1, "name": "Áo thun", "price": 120000, "image": "https://via.placeholder.com/150"},
    {"id": 2, "name": "Áo sơ mi", "price": 250000, "image": "https://via.placeholder.com/150"},
    {"id": 3, "name": "Quần jean", "price": 350000, "image": "https://via.placeholder.com/150"},
]

# ================== KHỞI TẠO SESSION ==================
if "cart" not in st.session_state:
    st.session_state.cart = []
if "orders" not in st.session_state:
    st.session_state.orders = []
if "admin_view" not in st.session_state:
    st.session_state.admin_view = []
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

# ================== SIDEBAR ==================
st.sidebar.image("90f7196d-0489-4a6c-a3c2-758f151eee1e.png", use_column_width=True)
menu = st.sidebar.radio("Chọn chức năng", ["Trang chủ", "Giỏ hàng", "Đơn hàng của tôi", "Đăng nhập", "Quản lý (Admin)"])

# ================== HÀM HỖ TRỢ ==================
def add_to_cart(product, qty):
    for item in st.session_state.cart:
        if item["id"] == product["id"]:
            item["qty"] += qty
            return
    st.session_state.cart.append({"id": product["id"], "name": product["name"], "price": product["price"], "qty": qty})

def remove_from_cart(product_id):
    st.session_state.cart = [item for item in st.session_state.cart if item["id"] != product_id]

def place_order():
    if st.session_state.cart:
        order = {"items": st.session_state.cart.copy(), "status": "Chờ xác nhận"}
        st.session_state.orders.append(order)
        st.session_state.admin_view.append(order)  # báo cho admin ngay khi khách đặt
        st.session_state.cart.clear()
        st.success("Đặt hàng thành công! Đơn hàng đang chờ xác nhận.")

# ================== GIAO DIỆN TRANG ==================
if menu == "Trang chủ":
    st.header("🛍️ Sản phẩm")
    for p in products:
        col1, col2 = st.columns([1, 3])
        with col1:
            st.image(p["image"], width=120)
        with col2:
            st.subheader(p["name"])
            st.write(f"Giá: {p['price']:,} VND")
            qty = st.number_input("Số lượng", min_value=1, value=1, key=f"qty_{p['id']}")
            if st.button("Thêm vào giỏ", key=f"btn_{p['id']}"):
                add_to_cart(p, qty)
                st.success(f"Đã thêm {qty} x {p['name']} vào giỏ hàng!")

elif menu == "Giỏ hàng":
    st.header("🛒 Giỏ hàng")
    if not st.session_state.cart:
        st.info("Giỏ hàng trống.")
    else:
        total = 0
        for item in st.session_state.cart:
            st.write(f"{item['name']} - {item['qty']} x {item['price']:,} VND")
            total += item['qty'] * item['price']
            if st.button(f"Xóa {item['name']}", key=f"rm_{item['id']}"):
                remove_from_cart(item["id"])
                st.warning(f"Đã xóa {item['name']}")
        st.subheader(f"💵 Tổng cộng: {total:,} VND")
        if st.button("Đặt hàng"):
            place_order()

elif menu == "Đơn hàng của tôi":
    st.header("📦 Đơn hàng của tôi")
    if not st.session_state.orders:
        st.info("Bạn chưa có đơn hàng nào.")
    else:
        for i, order in enumerate(st.session_state.orders):
            st.write(f"Đơn hàng {i+1} - Trạng thái: {order['status']}")
            for item in order["items"]:
                st.write(f"- {item['name']} ({item['qty']} x {item['price']:,} VND)")

elif menu == "Đăng nhập":
    st.header("🔑 Đăng nhập")
    user = st.text_input("Tên đăng nhập")
    pw = st.text_input("Mật khẩu", type="password")
    if st.button("Đăng nhập"):
        if user == "admin" and pw == "123":
            st.session_state.logged_in = True
            st.session_state.is_admin = True
            st.success("Đăng nhập thành công với quyền Admin!")
        else:
            st.error("Sai tài khoản hoặc mật khẩu.")

elif menu == "Quản lý (Admin)":
    if not st.session_state.is_admin:
        st.error("Bạn cần đăng nhập Admin để xem.")
    else:
        st.header("📊 Quản lý đơn hàng")
        if not st.session_state.admin_view:
            st.info("Chưa có đơn hàng nào.")
        else:
            for i, order in enumerate(st.session_state.admin_view):
                st.write(f"Đơn hàng {i+1} - Trạng thái: {order['status']}")
                for item in order["items"]:
                    st.write(f"- {item['name']} ({item['qty']} x {item['price']:,} VND)")
                if order["status"] == "Chờ xác nhận":
                    if st.button(f"Xác nhận đơn {i+1}", key=f"cfm_{i}"):
                        order["status"] = "Đã xác nhận"
                        st.success(f"Đơn {i+1} đã được xác nhận!")
