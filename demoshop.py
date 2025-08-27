import streamlit as st

# Sidebar với logo
st.sidebar.image("images/logo.png", use_column_width=True)  # để file trong thư mục images
st.sidebar.title("Menu")

page = st.sidebar.radio("Chọn trang:", ["Trang chủ", "Giỏ hàng", "Đơn hàng của tôi", "Admin"])

# Nội dung trang
if page == "Trang chủ":
    st.title("Chào mừng đến cửa hàng")
elif page == "Giỏ hàng":
    st.title("Giỏ hàng")
elif page == "Đơn hàng của tôi":
    st.title("Đơn hàng của tôi")
elif page == "Admin":
    st.title("Quản lý đơn hàng (Admin)")
