import streamlit as st
import re

# ----------------------------------------------------
# 核心處理引擎 (純規則版，保證運行)
# ----------------------------------------------------
def process_text_by_rules(raw_text):
    """
    這是一個穩定、可靠的文字清洗引擎。
    """
    text = raw_text
    
    # 規則一：去除時間戳
    text = re.sub(r'\[?\b\d{1,2}:\d{2}(:\d{2})?\b\]?\s*', '', text)
    
    # 規則二：去除常見口頭禪
    filler_words = ['嗯', '啊', '呃', '這個', '那個', '就是說', '然後', '所以']
    text = re.sub(r'\b(' + '|'.join(filler_words) + r')\b', '', text, flags=re.IGNORECASE)
    
    # 規則三：為沒有標點的行尾添加句號
    text = re.sub(r'([^。！？\?])\n', r'\1。\n', text)
    if text and not text.endswith(('。', '！', '？', '?', ' ')):
        text += '。'

    # 規則四：分段邏輯
    lines = text.splitlines()
    non_empty_lines = [line.strip() for line in lines if line.strip()]
    text = '\n\n'.join(non_empty_lines)

    # 規則五：整理多餘空格
    text = re.sub(r' +', ' ', text)
    
    return text.strip()


# ----------------------------------------------------
# Streamlit 網頁介面定義
# ----------------------------------------------------
st.set_page_config(layout="wide", page_title="高效文字處理器")
st.title('高效文字處理器 (Python 驅動)')

col1, col2 = st.columns(2)

with col1:
    original_text = st.text_area("1. 原始文字", height=250, placeholder="在這裡貼上您需要處理的文字...")

with col2:
    st.markdown("**2. 內建處理規則 (程式碼驅動)**")
    st.info(
        """
        本工具已內建以下核心清洗規則：
        - **可靠去除**：時間戳 (如 `44:12`)
        - **可靠去除**：常見口頭禪 (如 `嗯`, `啊`...)
        - **自動添加**：為段落結尾補充句號
        - **智能分段**：將內容整理成格式正確的段落
        - **自動整理**：多餘的空格
        """
    )

if st.button('開始處理', type="primary"):
    if original_text:
        processed_result = process_text_by_rules(original_text)
        st.session_state['processed_text'] = processed_result
    else:
        st.warning("請先在左上方的「1. 原始文字」框中貼上內容。")

st.markdown("---")

col3, col4 = st.columns(2)

with col3:
    edited_text = st.text_area(
        "3. 處理後的純文本文字 (可在此手動編輯)",
        value=st.session_state.get('processed_text', ''),
        height=300,
        key="editor"
    )

with col4:
    st.markdown("**4. 所見即所得的可發佈文字 (預覽)**")
    st.markdown(edited_text)
