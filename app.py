import streamlit as st
from PIL import Image
import os
import predict_vn  # File backend của bạn

# Cấu hình trang
st.set_page_config(page_title="Nhận diện địa điểm", layout="centered")

def main():
    st.title("📸 Nhận diện Địa điểm TP.HCM")
    st.write("Chào Trí, hãy tải ảnh để AI xác định vị trí và mở bản đồ.")

    # Kiểm tra file cần thiết
    if not os.path.exists("model_vietnam.pth") or not os.path.exists("classes.txt"):
        st.error("Thiếu file model_vietnam.pth hoặc classes.txt trong thư mục!")
        return

    # 1. Thành phần tải ảnh
    uploaded_file = st.file_uploader("Chọn ảnh địa điểm (jpg, png)...", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        try:
            # Hiển thị ảnh
            image = Image.open(uploaded_file)
            st.image(image, caption='Ảnh đã tải lên', use_container_width=True)
            
            st.write("---")
            
            with st.spinner('Đang phân tích...'):
                # 2. Dự đoán
                label, confidence = predict_vn.predict_pil_image(image)
                location_name, map_url = predict_vn.build_map_url(label)
                
            # 3. Hiển thị kết quả
            col1, col2 = st.columns(2)
            with col1:
                st.success(f"**Địa điểm:** {location_name}")
            with col2:
                st.info(f"**Độ chính xác:** {confidence*100:.2f}%")

            # 4. Nút bấm mở Map
            st.link_button("📍 Xem trên Google Maps", map_url, use_container_width=True)

        except Exception as e:
            st.error(f"Có lỗi xảy ra: {e}")

if __name__ == "__main__":
    main()