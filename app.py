import streamlit as st
from openai import OpenAI

# تنظیمات اصلی صفحه
st.set_page_config(
    page_title="کتاب‌یار پلاس | دستیار اختصاصی مربی کتابدانه",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# استایل راست‌چین (RTL) و فونت وزیر
st.markdown("""
<style>
    @import url('https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css');
    * {
        font-family: 'Vazirmatn', sans-serif !important;
        direction: rtl;
        text-align: right;
    }
    .stChatMessage {
        text-align: right;
        direction: rtl;
    }
</style>
""", unsafe_allow_html=True)

# پرامپت پایه‌ای و تخصصی کتابدانه
BASE_PROMPT = """
تو "کتاب‌یار پلاس" هستی؛ بازوی استراتژیک، مارکتینگ و فروش برای "علیرضا جزی"، مربی رسمی کتابدانه در اصفهان.
کسب‌وکار: آموزش تندخوانی، تقویت حافظه، تمرکز و توسعه ذهن و بیان.
قوانین پاسخ‌دهی:
۱. از کلی‌گویی خودداری کن؛ متون تبلیغاتی و سناریوها باید دقیق، کلمه به کلمه و آماده انتشار باشند.
۲. شرایط بومی اصفهان (کافه‌کتاب‌ها، مدارس، دانشگاه‌ها) را در نظر بگیر.
۳. در انتهای هر پاسخ، حداقل یک گام اجرایی شفاف (Action Item) مشخص کن.
"""

ROLES = {
    "🎯 مدیر تبلیغات و جذب": BASE_PROMPT + "\nتخصص فعلی: نوشتن سناریوی ریلز، استوری، تبلیغات محلی اصفهان، قلاب‌های متوقف‌کننده اسکرول و پیامک‌های دعوت.",
    "💰 استراتژیست فروش و ثبت‌نام": BASE_PROMPT + "\nتخصص فعلی: فروش مستقیم دوره‌ها، هندل کردن اعتراضات مالی، اسکریپت دایرکت اینستاگرام و پرزنت در معارفه‌ها.",
    "🧠 طراح دوره و کارگاه حضوری": BASE_PROMPT + "\nتخصص فعلی: طراحی سرفصل کارگاه‌های ۱ ساعته در اصفهان، مینی‌دوره‌های اختصاصی علیرضا برای جذب لید، و چالش‌های تمرینی.",
    "💡 اتاق فکر B2B و نوآوری": BASE_PROMPT + "\nتخصص فعلی: همکاری با مدارس، دانشگاه اصفهان، مراکز کنکوری، کافه‌کتاب‌ها و بسته‌های سازمانی."
}

# نوار کناری (Sidebar)
with st.sidebar:
    st.title("📚 کتاب‌یار پلاس")
    st.caption("دستیار هوشمند مربی کتابدانه - شعبه اصفهان")
    
    st.divider()
    api_key = st.text_input("کلید هوش مصنوعی (API Key):", type="password")
    api_base = st.text_input("آدرس سرویس (Base URL):", value="https://api.openai.com/v1")
    model_name = st.text_input("نام مدل:", value="gpt-4o-mini")
    
    st.divider()
    selected_role = st.selectbox("انتخاب هم‌تیمی تخصصی:", list(ROLES.keys()))
    st.success(f"نقش فعال: {selected_role}")
    
    if st.button("پاک کردن گفتگو"):
        st.session_state.messages = []
        st.rerun()

# مدیریت پیام‌ها
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# دریافت ورودی کاربر
if user_prompt := st.chat_input("سوال، ایده، سناریوی ریلز یا مشکل فروشت رو بنویس علیرضا..."):
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    if not api_key:
        st.warning("علیرضا جان، ابتدا در منوی سمت راست API Key رو وارد کن.")
    else:
        client = OpenAI(api_key=api_key, base_url=api_base.strip() if api_base.strip() else None)
        
        system_content = ROLES[selected_role]
        full_messages = [{"role": "system", "content": system_content}] + [
            {"role": m["role"], "content": m["content"]} for m in st.session_state.messages
        ]
        
        with st.chat_message("assistant"):
            response_box = st.empty()
            collected_text = ""
            try:
                stream = client.chat.completions.create(
                    model=model_name.strip(),
                    messages=full_messages,
                    stream=True,
                )
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        collected_text += chunk.choices[0].delta.content
                        response_box.markdown(collected_text + "▌")
                response_box.markdown(collected_text)
                st.session_state.messages.append({"role": "assistant", "content": collected_text})
            except Exception as e:
                st.error(f"خطا در برقراری ارتباط: {e}")
