import streamlit as st
import re

# ----------------------------------------------------
# 1. 核心處理引擎 (純 Python) - 版本 2.0
# ----------------------------------------------------
def process_text_by_rules(raw_text):
    """
    這是我們的文字清洗引擎，所有規則都在這裡定義。
    """
    text = raw_text
    
    # 規則一：去除時間戳 (例如 44:12 或 [01:23:45])
    text = re.sub(r'\[?\b\d{1,2}:\d{2}(:\d{2})?\b\]?\s*', '', text)
    
    # --- 修改點 1：移除政治詞語清洗規則 ---
    # 下面這行已被註解掉，不再執行
    # text = re.sub(r'习近平|习主席|中共', '', text)
    
    # 規則二：去除常見口頭禪
    filler_words = ['嗯', '啊', '呃', '這個', '那個', '就是說', '然後', '所以']
    text = re.sub(r'\b(' + '|'.join(filler_words) + r')\b', '', text, flags=re.IGNORECASE)
    
    # --- 修改點 2：為沒有標點的行尾添加句號 ---
    # 這個正則表達式尋找所有不是標點符號結尾的換行
    # ([^。！？\?]) 匹配任何非標點的字元，\n 匹配換行
    # \1 代表將匹配到的那個字元保留，然後在其後加上句號和換行
    text = re.sub(r'([^。！？\?])\n', r'\1。\n', text)
    # 確保文章最後一行也有標點
    if text and not text.endswith(('。', '！', '？', '?', ' ')):
        text += '。'

    # --- 修改點 3：更智能、更可靠的分段邏輯 ---
    # 先將整篇文章按“換行”拆分成一個列表
    lines = text.splitlines()
    # 過濾掉所有完全是空白的行
    non_empty_lines = [line.strip() for line in lines if line.strip()]
    # 用兩個換行符 (代表一個空行) 將它們重新組合起來，形成乾淨的段落
    text = '\n\n'.join(non_empty_lines)

    # 規則四：整理格式 (合併多餘空格)
    text = re.sub(r' +', ' ', text)
    
    return text.strip()


# ----------------------------------------------------
# 2. Streamlit 網頁介面定義 (這部分無需修改)
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
        height=300, # 編輯框依然使用固定高度，避免與自適應JS衝突
        key="editor"
    )

with col4:
    st.markdown("**4. 所見即所得的可發佈文字 (預覽)**")
    st.markdown(edited_text)
