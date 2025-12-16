import streamlit as st
from openai import OpenAI
import time

# ============= 페이지 설정 =============
st.set_page_config(
    page_title="제목학원 나를 브랜딩 하기",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============= 신데렐라 동화 분위기 CSS 스타일 =============
st.markdown("""
<style>
    * {
        font-family: 'Segoe UI', 'Noto Sans', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    .main {
        background: linear-gradient(135deg, #faf5ff 0%, #ffe6f5 50%, #f5f0ff 100%);
        min-height: 100vh;
    }
    
    .stTitle {
        text-align: center;
        font-size: 2.8em !important;
        font-weight: 700;
        margin-bottom: 0.2em;
        background: linear-gradient(135deg, #d8a5e3 0%, #e8b4d0 50%, #c9a0d4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        user-select: none;
    }
    
    .subtitle {
        text-align: center;
        color: #b89ac9;
        font-size: 1.1em;
        margin-bottom: 2em;
        letter-spacing: 1px;
        font-weight: 500;
    }
    
    .input-section {
        background: rgba(255, 255, 255, 0.98);
        border-radius: 25px;
        padding: 2.5rem;
        box-shadow: 0 8px 32px rgba(216, 165, 227, 0.15);
        margin-bottom: 2rem;
        border: 2px solid rgba(216, 165, 227, 0.25);
    }
    
    .chat-container {
        background: rgba(255, 255, 255, 0.98);
        border-radius: 25px;
        padding: 1.5rem;
        box-shadow: 0 8px 32px rgba(216, 165, 227, 0.15);
        border: 2px solid rgba(216, 165, 227, 0.25);
    }
    
    .stChatMessage {
        border-radius: 15px;
        padding: 1rem;
        margin-bottom: 0.8rem;
    }
    
    /* User 메시지 스타일 */
    [data-testid="chat-message"][data-test-user-msg] {
        background: linear-gradient(135deg, #d8a5e3 0%, #e8b4d0 100%);
        color: white;
        border-radius: 15px;
    }
    
    /* Assistant 메시지 스타일 */
    [data-testid="chat-message"]:has([data-icon="bot"]) {
        background: linear-gradient(135deg, rgba(216, 165, 227, 0.12) 0%, rgba(232, 180, 208, 0.12) 100%);
        border-left: 4px solid #d8a5e3;
        border-radius: 15px;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #d8a5e3 0%, #e8b4d0 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.8rem 2.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 6px 20px rgba(216, 165, 227, 0.3);
        font-size: 1.05em;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(216, 165, 227, 0.4);
    }
    
    .stTextInput > div > div > input {
        border-radius: 12px;
        border: 2px solid rgba(216, 165, 227, 0.3);
        padding: 0.8rem;
        font-size: 1em;
        background: linear-gradient(135deg, rgba(250, 245, 255, 0.9) 0%, rgba(255, 230, 245, 0.9) 100%);
    }
    
    .stTextArea > div > div > textarea {
        border-radius: 12px;
        border: 2px solid rgba(216, 165, 227, 0.3);
        padding: 0.8rem;
        background: linear-gradient(135deg, rgba(250, 245, 255, 0.9) 0%, rgba(255, 230, 245, 0.9) 100%);
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #d8a5e3;
        box-shadow: 0 0 0 0.3rem rgba(216, 165, 227, 0.2);
    }
    
    .stChatInput {
        border-radius: 15px;
    }
    
    .stChatInput input {
        border-radius: 12px;
        border: 2px solid rgba(216, 165, 227, 0.3);
        background: linear-gradient(135deg, rgba(250, 245, 255, 0.95) 0%, rgba(255, 230, 245, 0.95) 100%);
    }
    
    .label-large {
        font-size: 1.6em;
        font-weight: 600;
        color: #b89ac9;
    }
</style>
""", unsafe_allow_html=True)

# ============= OpenAI 클라이언트 초기화 =============
@st.cache_resource
def load_openai_client():
    """OpenAI 클라이언트를 로드합니다."""
    api_key = st.secrets.get("OPENAI_API_KEY")
    if not api_key:
        st.error("❌ OpenAI API 키가 설정되지 않았습니다. .streamlit/secrets.toml 파일을 확인해주세요.")
        st.stop()
    return OpenAI(api_key=api_key)

client = load_openai_client()

# ============= 세션 상태 초기화 =============
if "messages" not in st.session_state:
    st.session_state.messages = []

if "nickname" not in st.session_state:
    st.session_state.nickname = None

if "user_interests" not in st.session_state:
    st.session_state.user_interests = None

if "user_situation" not in st.session_state:
    st.session_state.user_situation = None

if "nickname_created" not in st.session_state:
    st.session_state.nickname_created = False

# ============= 별명 생성 함수 =============
def generate_nickname(interests, situation):
    """사용자의 관심사와 상황을 바탕으로 창의적이고 웃긴 별명을 생성합니다."""
    system_prompt = """당신은 창의적이고 웃긴 별명 생성 전문가입니다.
사용자의 좋아하는 것과 현재 상황을 기반으로, 다음 조건에 따라 별명을 만들어주세요:

1. 창의적이고 웃긴 별명 3~5개를 제시하세요
2. 각 별명마다 왜 그렇게 지었는지 간단한 설명을 해주세요
3. 한글로 작성하세요
4. 별명들은 사용자의 개성과 현재 상황을 잘 반영하되, 긍정적이고 재미있어야 합니다
5. 별명 제시 후, 선택된 별명으로 사용자와 친근하게 대화를 시작하세요

마치 친한 친구처럼 따뜻하고 재미있는 톤으로 대화해주세요."""

    user_message = f"""내가 좋아하는 것: {interests}

지금의 상황: {situation}

이를 바탕으로 나에게 어울리는 창의적이고 웃긴 별명을 만들어줄래?"""
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        temperature=0.8,
        max_tokens=1000
    )
    
    return response.choices[0].message.content

# ============= 챗봇 시스템 프롬프트 =============
def get_system_prompt():
    """챗봇의 시스템 프롬프트를 생성합니다."""
    if st.session_state.nickname:
        return f"""당신은 친근하고 재미있는 친구 같은 챗봇입니다.
사용자의 별명은 '{st.session_state.nickname}'이고,
사용자가 좋아하는 것: {st.session_state.user_interests}
사용자의 현재 상황: {st.session_state.user_situation}

이 정보를 바탕으로 사용자와 따뜻하고 재미있는 대화를 나누세요.
인스타그램 감성으로 긍정적이고 응원하는 톤으로 대화해주세요.
사용자의 별명을 적절히 사용하여 더욱 친근하게 느껴지도록 하세요."""
    else:
        return "당신은 친근하고 재미있는 친구 같은 챗봇입니다. 사용자와 따뜻한 대화를 나누세요."

# ============= UI 메인 섹션 =============
st.markdown("<h1 class='stTitle'>제목학원 : 나를 브랜딩 하기</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>당신만의 개성을 찾아 독특한 별명을 만들어보세요</p>", unsafe_allow_html=True)

# ============= 별명 생성 섹션 =============
if not st.session_state.nickname_created:
    st.markdown("<div class='input-section'>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown("<p class='label-large'>💝 좋아하는 것을 알려주세요</p>", unsafe_allow_html=True)
        interests = st.text_input(
            label="좋아하는 것",
            placeholder="예: 핸드폰, 아니메, 요리, 음악 등...",
            key="interests_input",
            label_visibility="collapsed"
        )
    
    with col2:
        st.markdown("<p class='label-large'>🌙 지금의 상황을 알려주세요</p>", unsafe_allow_html=True)
        situation = st.text_area(
            label="지금의 상황",
            placeholder="예: 대학생, 직장인, 강아지와 함께 살고있어요, 요즘 공부중이야 등...",
            height=110,
            key="situation_input",
            label_visibility="collapsed"
        )
    
    if st.button("✨ 별명 만들기 ✨", use_container_width=True):
        if not interests or not situation:
            st.warning("⚠️ 좋아하는 것과 현재 상황을 모두 입력해주세요!")
        else:
            with st.spinner("마법의 별명을 만들고 있어요... ✨"):
                try:
                    nickname_response = generate_nickname(interests, situation)
                    st.session_state.user_interests = interests
                    st.session_state.user_situation = situation
                    
                    # 첫 번째 메시지를 채팅 히스토리에 추가
                    st.session_state.messages = [
                        {"role": "assistant", "content": nickname_response}
                    ]
                    st.session_state.nickname_created = True
                    
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ 오류가 발생했습니다: {str(e)}")
    
    st.markdown("</div>", unsafe_allow_html=True)

# ============= 대화 섹션 =============
if st.session_state.nickname_created:
    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
    
    st.markdown("<h3 style='text-align: center; color: #a855f7;'>💬 마법의 대화 시간</h3>", unsafe_allow_html=True)
    
    # 기존 메시지 표시
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # 채팅 입력
    if prompt := st.chat_input("뭐가 궁금해? 편하게 물어봐! 😊"):
        # 사용자 메시지 추가
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Assistant 응답 생성
        try:
            response_stream = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": get_system_prompt()},
                    *[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                ],
                temperature=0.7,
                max_tokens=1000,
                stream=True
            )
            
            with st.chat_message("assistant"):
                response_content = st.write_stream(response_stream)
            
            st.session_state.messages.append({"role": "assistant", "content": response_content})
        
        except Exception as e:
            st.error(f"❌ 응답 생성 중 오류가 발생했습니다: {str(e)}")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 초기화 버튼
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 다시 시작", use_container_width=True):
        st.session_state.messages = []
        st.session_state.nickname = None
        st.session_state.user_interests = None
        st.session_state.user_situation = None
        st.session_state.nickname_created = False
        st.rerun()
