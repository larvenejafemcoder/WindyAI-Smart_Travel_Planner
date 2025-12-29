import streamlit as st
from PIL import Image
import urllib.parse
import services.utils as utils

# Import algo3 modules (Image Recognition)
try:
    from core.algo3.predict_vn import predict_pil_image as algo3_predict
    IMAGE_RECOGNITION_AVAILABLE = True
except ImportError:
    IMAGE_RECOGNITION_AVAILABLE = False

# Import algo2 modules (Routing/Navigation) for geocoding
try:
    from core.algo2.routing import geocode
    ROUTING_AVAILABLE = True
except ImportError:
    geocode = None
    ROUTING_AVAILABLE = False

def predict_pil_image(image):
    """Helper function to use the singleton predictor."""
    if not IMAGE_RECOGNITION_AVAILABLE:
        return "Unknown", 0.0
    return algo3_predict(image)

def render_nhan_dien_anh():
    """Render phần Tìm vị trí ảnh - Layout Cân Đối & Bản đồ Style Mới"""
    st.markdown("### 📷 Tìm vị trí ảnh")
    st.markdown(
        "<p class='feature-muted'>Tải lên ảnh địa điểm, hệ thống sẽ nhận diện và hiển thị bản đồ.</p>",
        unsafe_allow_html=True,
    )

    if not IMAGE_RECOGNITION_AVAILABLE:
        st.error("❌ Module nhận diện ảnh chưa được cài đặt hoặc bị lỗi.")
        return

    img_file = st.file_uploader("Tải ảnh địa điểm (JPG/PNG)", type=["jpg", "jpeg", "png"])
    if img_file is not None:
        image = Image.open(img_file)
        
    
        if st.button("🔍 Nhận diện & Tìm vị trí", type="primary", use_container_width=True):
            with st.spinner("🤖 Đang phân tích ảnh & tìm tọa độ..."):
                try:
            
                
                    label, confidence = predict_pil_image(image)
                    location_name = label.replace("_", " ").strip()
                    
                    # 2. Tìm tọa độ (Geocoding)
                    lat, lon, formatted_name = None, None, None
                    has_coords = False
                    
                    if ROUTING_AVAILABLE and geocode:
                        search_query = f"{location_name}, TP Hồ Chí Minh"
                        geo_result = geocode(search_query)
                        if geo_result:
                            lat, lon, formatted_name = geo_result
                            has_coords = True

                  
                    
                  
                    col_img, col_info = st.columns([1, 1], gap="medium")
                    
                    with col_img:
                        st.image(image, caption="Ảnh bạn tải lên", use_container_width=True)
                    
                    with col_info:
                        st.success(f"📍 AI Dự đoán: **{location_name}**")
                        st.progress(confidence, text=f"Độ tin cậy: {confidence*100:.1f}%")
                        
                        if has_coords:
                            st.info(f"🏠 **Địa chỉ tìm thấy:**\n\n{formatted_name}")
                        else:
                            st.warning(f"⚠️ Không tìm thấy tọa độ chính xác cho địa điểm này.")

                
                    
                    if has_coords:
                        st.markdown("---")
                        st.markdown("### 🗺️ Vị trí trên bản đồ")
                        
                   
                        
                        map_html = f"""
                        <!DOCTYPE html>
                        <html>
                        <head>
                            <meta charset="utf-8" />
                            <meta name="viewport" content="width=device-width, initial-scale=1.0">
                            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
                            <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
                            <style>
                                body {{ margin: 0; padding: 0; }}
                                #map {{ width: 100%; height: 500px; }}
                                /* CSS cho marker hình tròn màu xanh có số */
                                .marker-pin {{
                                    width: 30px;
                                    height: 30px;
                                    border-radius: 50%;
                                    background-color: #2196F3; /* Màu xanh dương */
                                    border: 2px solid #FFFFFF;
                                    color: white;
                                    display: flex;
                                    align-items: center;
                                    justify-content: center;
                                    font-weight: bold;
                                    font-family: sans-serif;
                                    box-shadow: 0 2px 5px rgba(0,0,0,0.3);
                                }}
                            </style>
                        </head>
                        <body>
                            <div id="map"></div>
                            <script>
                                // 1. Khởi tạo bản đồ tại tọa độ tìm được, zoom 16
                                var map = L.map('map').setView([{lat}, {lon}], 16);

                         
                                L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                                    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
                                    maxZoom: 19
                                }}).addTo(map);

                                
                                var numberedIcon = L.divIcon({{
                                    html: '<div class="marker-pin">1</div>',
                                    className: '', // Bỏ class mặc định của Leaflet
                                    iconSize: [30, 30],
                                    iconAnchor: [15, 15], // Neo ở tâm
                                    popupAnchor: [0, -15] // Popup hiện phía trên
                                }});

                                L.marker([{lat}, {lon}], {{icon: numberedIcon}})
                                    .bindPopup('<b>{formatted_name}</b>')
                                    .addTo(map)
                                    .openPopup();
                            </script>
                        </body>
                        </html>
                        """
                        
                        import streamlit.components.v1 as components
                        components.html(map_html, height=500)
                      
                        
                    elif confidence > 0.4:
                        # Fallback nếu không có tọa độ
                        st.markdown("---")
                        query = urllib.parse.quote(f"{location_name} TP Hồ Chí Minh")
                        map_url = f"https://www.google.com/maps/search/?api=1&query={query}"
                        st.link_button("↗️ Mở Google Maps (Tab mới)", map_url)
                        
                except Exception as e:
                    st.error(f"Lỗi hệ thống: {str(e)}")
