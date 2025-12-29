import streamlit as st
import base64
import os
import html as _html
import textwrap
try:
    from core.algo6_chatbot.chatbot_engine import ChatbotEngine
except ImportError:
    ChatbotEngine = None


# ==============================================================================
# 1. CẤU HÌNH CSS (CHAT BUTTON + GIAO DIỆN CHUNG)
# ==============================================================================
def inject_custom_css(logo_b64=None, chat_open=False):
    # Xác định style cho nút dựa trên trạng thái (Mở/Đóng) và có logo hay không
    if logo_b64 and not chat_open:
        # Trạng thái ĐÓNG: Hiển thị Logo WindyAI, nền trắng, ẩn text emoji
        btn_background = f"url('data:image/png;base64,{logo_b64}') center/70% no-repeat white"
        btn_color = "transparent" # Ẩn emoji "💬"
        btn_border = "1px solid #e0e0e0" # Viền nhẹ cho nút trắng
        hover_transform = "scale(1.1)"
    else:
        # Trạng thái MỞ (hoặc không có logo): Hiển thị nút Xanh/Đỏ mặc định
        btn_background = "#0084ff"
        btn_color = "white"
        btn_border = "none"
        hover_transform = "scale(1.1) rotate(90deg)" if chat_open else "scale(1.1)"

    st.markdown(f"""
    <style>
        /* ---------------------------------------------------------------------- */
        /* 1. ĐỊNH VỊ NÚT CHAT TRÒN (FIXED POSITION) */
        /* ---------------------------------------------------------------------- */
        div.element-container:has(#chat-btn-marker) + div.element-container button {{
            position: fixed !important;
            bottom: 20px !important;
            right: 20px !important;
            width: 60px !important;
            height: 60px !important;
            border-radius: 50% !important;
            background: {btn_background} !important;
            color: {btn_color} !important;
            border: {btn_border} !important;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2) !important;
            font-size: 24px !important;
            z-index: 999999 !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        }}
        div.element-container:has(#chat-btn-marker) + div.element-container button:hover {{
            transform: {hover_transform} !important;
            box-shadow: 0 6px 20px rgba(0,0,0,0.3) !important;
        }}

        /* ---------------------------------------------------------------------- */
        /* 2. KHUNG CHAT WINDOW */
        /* ---------------------------------------------------------------------- */
        div.floating-chat-window {{
            position: fixed;
            bottom: 90px;
            right: 20px;
            width: 350px;
            height: 500px;
            background: #ffffff;
            border-radius: 20px;
            box-shadow: 0 5px 30px rgba(0,0,0,0.2);
            z-index: 999998;
            display: flex; flex-direction: column;
            overflow: hidden;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            animation: slideIn 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        }}
        @keyframes slideIn {{ from {{ opacity: 0; transform: translateY(20px) scale(0.95); }} to {{ opacity: 1; transform: translateY(0) scale(1); }} }}

        .chat-header {{
            padding: 15px; background: #fff; border-bottom: 1px solid #f0f0f0;
            display: flex; align-items: center; justify-content: space-between;
        }}
        .chat-header .title {{ font-weight: bold; color: #0084ff; font-size: 1.1rem; }}
        .chat-header .status {{ font-size: 0.8rem; color: #31a24c; }}

        .chat-body-scroll {{
            flex: 1; overflow-y: auto; padding: 15px; background: #fff;
            display: flex; flex-direction: column;
            margin-bottom: 70px;
        }}
        .chat-body-scroll::-webkit-scrollbar {{ width: 5px; }}
        .chat-body-scroll::-webkit-scrollbar-thumb {{ background: #ccc; border-radius: 10px; }}

        .msg-row {{ display: flex; margin-bottom: 10px; width: 100%; }}
        .msg-row.user {{ justify-content: flex-end; }}
        .msg-row.assistant {{ justify-content: flex-start; }}
        
        .msg-bubble {{
            max-width: 80%; padding: 10px 14px; border-radius: 18px;
            font-size: 14px; line-height: 1.4; position: relative;
        }}
        .msg-bubble.user {{ background: #0084ff; color: white; border-bottom-right-radius: 4px; }}
        .msg-bubble.assistant {{ background: #f0f0f0; color: #333; border-bottom-left-radius: 4px; }}

        .chat-footer-bg {{
            position: absolute; bottom: 0; left: 0; width: 100%; height: 75px;
            background: #fff; border-top: 1px solid #f0f0f0; z-index: 1;
        }}

        /* ---------------------------------------------------------------------- */
        /* 3. INPUT HACK */
        /* ---------------------------------------------------------------------- */
        div.element-container:has(#chat-input-marker) + div.element-container div[data-testid="stTextInput"] {{
            position: fixed !important;
            bottom: 108px !important;
            right: 35px !important;
            width: 320px !important;
            z-index: 999999 !important;
        }}
        div[data-testid="stTextInput"] input {{
            border-radius: 25px !important;
            background: #f0f2f5 !important;
            border: none !important;
            padding: 10px 20px !important;
        }}
        div[data-testid="stTextInput"] input:focus {{
            background: #fff !important;
            box-shadow: 0 0 0 2px #0084ff !important;
        }}
        div[data-testid="stTextInput"] label {{ display: none !important; }}

        /* Ẩn header footer mặc định của Streamlit */
        header {{ visibility: hidden; }}
        footer {{ visibility: hidden; }}
        
        /* Ẩn padding mặc định của block-container để video tràn viền đẹp hơn */
        .block-container {{
            padding-top: 1rem !important;
            padding-bottom: 2rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            max-width: 100% !important;
        }}

    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 2. HÀM XỬ LÝ MEDIA (UPDATED)
# ==============================================================================
@st.cache_data
def get_base64_media(filename, folder="background"):
    """Đọc file media (video/image) và chuyển sang base64 (có cache)"""
    # Tìm đường dẫn file linh hoạt (chạy ở root hoặc trong pages)
    try: current_dir = os.path.dirname(os.path.abspath(__file__))
    except: current_dir = os.getcwd()
    
    # Thử tìm trực tiếp trong folder assets
    file_path = os.path.join(current_dir, "assets", folder, filename)
    
    # Nếu không thấy, thử lùi ra 1 cấp (trường hợp chạy trong thư mục con)
    if not os.path.exists(file_path):
        file_path = os.path.join(os.path.dirname(current_dir), "assets", folder, filename)

    if not os.path.exists(file_path):
        return None, None
        
    try:
        with open(file_path, "rb") as f:
            data = f.read()
            # Ensure no newlines or carriage returns in base64 string
            b64 = base64.b64encode(data).decode("utf-8").replace("\n", "").replace("\r", "")
            
            ext = filename.split('.')[-1].lower()
            if ext in ['mp4', 'mov']:
                return b64, 'video/mp4'
            elif ext in ['png', 'jpg', 'jpeg']:
                mime_type = 'image/jpeg' if ext in ['jpg', 'jpeg'] else f'image/{ext}'
                return b64, mime_type
            elif ext == 'gif':
                return b64, 'image/gif'
            else:
                return None, None
    except Exception as e:
        st.error(f"Lỗi khi đọc file {filename}: {e}")
        return None, None

def render_hero_section(filename, content_html, height="85vh", overlay_opacity=0.5, folder="background"):
    content_html = textwrap.dedent(content_html).strip()
    b64, mime = get_base64_media(filename, folder=folder)
    
    media_html = ""
    if not b64:
        media_html = '<div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: linear-gradient(45deg, #1e293b, #0f172a); z-index: 0;"></div>'
    else:
        if mime.startswith("video"):
            media_html = f"""<video autoplay muted loop playsinline style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover; z-index: 0;"><source src="data:{mime};base64,{b64}" type="{mime}"></video>"""
        else:
            media_html = f"""<img src="data:{mime};base64,{b64}" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover; z-index: 0;">"""

    full_html = f"""
    <div class="video-section" style="min-height: {height}; position: relative; overflow: hidden; border-radius: 20px; margin-bottom: 2rem; display: flex; align-items: center; justify-content: center; background-color: #1e293b;">
        {media_html}
        <div class="overlay-dark" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,{overlay_opacity}); z-index: 1; pointer-events: none;"></div>
        <div class="content-box" style="position: relative; z-index: 2; width: 100%; padding: 2rem;">
            {content_html}
        </div>
    </div>
    """
    st.markdown(full_html, unsafe_allow_html=True)

# ==============================================================================
# 3. LOGIC CHATBOT (GIỮ NGUYÊN)
# ==============================================================================
def render_floating_chat():
    # 1. Init State (Đã được xử lý ở đầu trang_chu nhưng giữ lại để an toàn)
    if 'show_chat' not in st.session_state: st.session_state.show_chat = False
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = [
            {"role": "assistant", "content": "Chào bạn! WindyAI đây. 👋\nMình có thể giúp gì cho chuyến đi của bạn?"}
        ]

    # Init Chatbot Engine
    if 'chatbot_engine' not in st.session_state and ChatbotEngine:
        st.session_state.chatbot_engine = ChatbotEngine()

    # 2. MARKER CHO NÚT CHAT
    st.markdown('<span id="chat-btn-marker"></span>', unsafe_allow_html=True)
    
    # Render Nút - Text sẽ được ẩn bởi CSS nếu ở trạng thái đóng và có logo
    if st.button("💬" if not st.session_state.show_chat else "✕", key="btn_chat"):
        st.session_state.show_chat = not st.session_state.show_chat
        st.rerun()

    # 3. Render Khung Chat
    if st.session_state.show_chat:
        messages_html = ""
        for msg in st.session_state.chat_history:
            role = "assistant" if msg["role"] == "assistant" else "user"
            content = _html.escape(msg["content"]).replace("\n", "<br>")
            messages_html += f'<div class="msg-row {role}"><div class="msg-bubble {role}">{content}</div></div>'

        full_chat_html = textwrap.dedent(f"""
            <div class="floating-chat-window">
                <div class="chat-header">
                    <span class="title">WindyAI Assistant</span>
                    <span class="status">● Online</span>
                </div>
                <div class="chat-body-scroll">
                    {messages_html}
                </div>
                <div class="chat-footer-bg"></div>
            </div>
        """)
        st.markdown(full_chat_html, unsafe_allow_html=True)

        st.markdown('<span id="chat-input-marker"></span>', unsafe_allow_html=True)
        
        def submit_chat():
            user_input = st.session_state.temp_input
            if user_input:
                st.session_state.chat_history.append({"role": "user", "content": user_input})
                
                reply = ""
                if 'chatbot_engine' in st.session_state and st.session_state.chatbot_engine:
                    reply = st.session_state.chatbot_engine.process_message(user_input)
                else:
                    txt_lower = user_input.lower()
                    # ... (Giữ nguyên logic trả lời chatbot) ...
                    if "lịch trình" in txt_lower or "kế hoạch" in txt_lower:
                        reply = "Để tạo lịch trình, bạn vui lòng truy cập tab 'Chức năng' ở trên, sau đó chọn mục '📅 Tạo lịch trình gợi ý' để bắt đầu nhé!"
                    elif "đường" in txt_lower or "chỉ đường" in txt_lower:
                        reply = "Bạn muốn tìm đường đi? Hãy vào tab 'Chức năng' và nhấn vào nút '🚗 Tìm đường đi' nha."
                    elif "thời tiết" in txt_lower:
                        reply = "Để xem thời tiết, bạn có thể vào tab 'Chức năng' và chọn '🌤️ Báo thời tiết vị trí', hoặc hỏi mình trực tiếp như 'Thời tiết ở Quận 1' nhé!"
                    elif "gợi ý địa điểm" in txt_lower or "địa điểm" in txt_lower:
                        reply = "Mình có thể giúp bạn gợi ý địa điểm dựa trên sở thích của bạn. Hãy vào tab 'Chức năng' và chọn '📍 Gợi ý địa điểm' để trải nghiệm nhé!"
                    elif "ảnh" in txt_lower or "hình" in txt_lower:
                        reply = "Bạn muốn tìm vị trí ảnh? Vui lòng vào tab 'Chức năng' và chọn '📸 Tìm vị trí ảnh' để sử dụng tính năng này."
                    elif "các chức năng" in txt_lower or "tính năng" in txt_lower or "help" in txt_lower:
                        reply = "WindyAI có các tính năng chính: Lịch trình, Tìm đường, Thời tiết, Gợi ý địa điểm, Tìm vị trí ảnh. Vào tab 'Chức năng' để trải nghiệm nhé!"
                    elif "xin chào" in txt_lower or "chào" in txt_lower:
                        reply = "Chào bạn! Mình là WindyAI, trợ lý du lịch thông minh của bạn. Mình có thể giúp gì cho chuyến đi của bạn?"
                    else:
                        reply = "Chào bạn! WindyAI có các tính năng: Lịch trình, Tìm đường, Thời tiết... Bạn hãy vào tab 'Chức năng' để trải nghiệm đầy đủ nhé."

                st.session_state.chat_history.append({"role": "assistant", "content": reply})
                st.session_state.temp_input = "" 

        st.text_input("input_placeholder", key="temp_input", on_change=submit_chat, placeholder="Hỏi về lịch trình...", label_visibility="collapsed")

# ==============================================================================
# 4. MAIN APP (CẬP NHẬT GIAO DIỆN MỚI)
# ==============================================================================
def page_trang_chu():
    st.set_page_config(layout="wide", page_title="WindyAI", initial_sidebar_state="collapsed")
    
    # Đảm bảo state được khởi tạo trước khi inject CSS để điều khiển nút chat
    if 'show_chat' not in st.session_state: st.session_state.show_chat = False

    # 1. Load Logo WindyAI cho nút chat
    # File: assets/logo/logo.png
    logo_b64, _ = get_base64_media("logo.png", folder="logo")
    
    # 2. Inject CSS chung (Chat button + Logo)
    # Truyền logo_b64 và trạng thái chat hiện tại vào hàm CSS
    inject_custom_css(logo_b64, st.session_state.show_chat)

    # 3. Inject CSS riêng cho trang chủ (Sections)
    st.markdown("""
    <style>
        .video-section {
            position: relative; width: 100%; min-height: 85vh;
            overflow: hidden; display: flex; align-items: center; justify-content: center;
            border-radius: 20px; margin-bottom: 2rem;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            background-color: #1e293b;
        }
        .content-box {
            position: relative; z-index: 2; text-align: center; color: white;
            padding: 2rem; max-width: 1200px;
            animation: fadeIn 1.5s ease-in-out;
        }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
        
        .home-title {
            font-size: 3.5rem; font-weight: 800; line-height: 1.2; margin-bottom: 1.5rem;
            text-shadow: 0 4px 10px rgba(0,0,0,0.5);
            background: linear-gradient(90deg, #60A5FA, #FFFFFF);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }
        .home-subtitle {
            font-size: 1.2rem; line-height: 1.6; margin-bottom: 2rem;
            color: #E2E8F0; text-shadow: 0 2px 4px rgba(0,0,0,0.5);
        }
        .feature-box {
            background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            padding: 1.5rem; border-radius: 16px; margin: 10px;
            flex: 1; min-width: 200px; transition: transform 0.3s ease;
        }
        .feature-box:hover { transform: translateY(-5px); background: rgba(255, 255, 255, 0.2); }
        
        .stat-number { font-size: 2.5rem; font-weight: 700; color: #60A5FA; margin-bottom: 0.5rem; }
        .flex-row { display: flex; flex-wrap: wrap; gap: 1.5rem; justify-content: center; margin-top: 2rem; }
        
        .badge-pill {
            display: inline-block; padding: 0.5rem 1.5rem;
            background: rgba(37, 99, 235, 0.8); color: white;
            border-radius: 99px; font-weight: 600; margin-bottom: 1.5rem;
            box-shadow: 0 4px 15px rgba(37, 99, 235, 0.4);
        }
    </style>
    """, unsafe_allow_html=True)

    # --- SECTION 1: HERO (City Night) ---
    render_hero_section("section-1_optimized.jpg", """
        <div class="badge-pill">✨ WindyAI - Smart Travel Planner</div>
        <h1 class="home-title">Lên kế hoạch du lịch<br>thông minh với AI</h1>
        <p class="home-subtitle">
            Chỉ cần nhập điểm đến, ngân sách và thời gian rảnh.<br>
            Hệ thống sẽ giúp bạn tạo lịch trình <b>thông minh – nhanh chóng – tối ưu</b>.
        </p>
    """, overlay_opacity=0.5)

    # --- SECTION 2: HIGHLIGHTS (Global Connection) ---
    render_hero_section("section-2_optimized.jpg", """
        <h2 style="font-size: 2.5rem; margin-bottom: 2rem; font-weight: 700;">Điểm nổi bật</h2>
        <div class="flex-row">
            <div class="feature-box">
                <div style="font-size: 3rem; margin-bottom: 1rem;">⏱️</div>
                <h3>Tối ưu thời gian</h3>
                <p style="font-size: 0.9rem; opacity: 0.9;">Sắp xếp lộ trình khoa học, không lo kẹt xe hay đi đường vòng.</p>
            </div>
            <div class="feature-box">
                <div style="font-size: 3rem; margin-bottom: 1rem;">💸</div>
                <h3>Cân đối chi phí</h3>
                <p style="font-size: 0.9rem; opacity: 0.9;">Gợi ý điểm đến phù hợp với túi tiền của bạn.</p>
            </div>
            <div class="feature-box">
                <div style="font-size: 3rem; margin-bottom: 1rem;">🧭</div>
                <h3>Dễ sử dụng</h3>
                <p style="font-size: 0.9rem; opacity: 0.9;">Giao diện thân thiện, thao tác đơn giản cho mọi lứa tuổi.</p>
            </div>
        </div>
    """, overlay_opacity=0.6)

    # --- SECTION 3: STATS (Coding/Encryption) ---
    render_hero_section("section-3.mp4", """
        <h2 style="font-size: 2.5rem; margin-bottom: 2rem; font-weight: 700;">Hiệu suất vượt trội</h2>
        <div class="flex-row">
            <div class="feature-box">
                <div class="stat-number">~ 2 phút</div>
                <div style="font-weight: 600;">Thời gian chuẩn bị</div>
            </div>
            <div class="feature-box">
                <div class="stat-number">3 – 20</div>
                <div style="font-weight: 600;">Điểm đến / ngày</div>
            </div>
            <div class="feature-box">
                <div class="stat-number">100%</div>
                <div style="font-weight: 600;">Tự động hóa</div>
            </div>
        </div>
    """, overlay_opacity=0.7)

    # --- SECTION 4: FOOTER (Clouds) ---
    render_hero_section("section-4.MP4", """
        <h2 style="font-size: 2.5rem; margin-bottom: 1rem; font-weight: 700;">Trải nghiệm ngay hôm nay</h2>
        <p style="font-size: 1.2rem; margin-bottom: 2rem;">Khám phá thế giới theo cách riêng của bạn.</p>
        <div style="font-size: 0.9rem; opacity: 0.8;">© 2025 WindyAI - Smart Travel Planner</div>
    """, height="60vh", overlay_opacity=0.3)

    # 4. Render Chatbot
    render_floating_chat()

if __name__ == "__main__":
    page_trang_chu()
