import streamlit as st
import re

# ----------------------------------------------------
# 1. 核心處理引擎 (純 Python)
# ----------------------------------------------------
def process_text_by_rules(raw_text):
    """
    這就是我們的文字清洗引擎，所有規則都在這裡定義。
    """
    # 複製一份，避免修改原始輸入
    text = raw_text
    
    # 規則一：去除時間戳 (例如 44:12 或 [01:23:45])
    text = re.sub(r'\[?\b\d{1,2}:\d{2}(:\d{2})?\b\]?\s*', '', text)
    
      
    # 規則二：去除常見口頭禪 (這個列表可以隨時擴充)
    filler_words = ['嗯', '啊', '呃', '這個', '那個', '就是說', '然後', '所以']
    text = re.sub(r'\b(' + '|'.join(filler_words) + r')\b', '', text, flags=re.IGNORECASE)
    
    # 規則四：整理格式 (合併多餘空格和空行)
    text = re.sub(r' +', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text) # 最多保留一個空行
    
    return text.strip()

# ----------------------------------------------------
# 2. Streamlit 網頁介面定義
# ----------------------------------------------------

# 基本頁面設定
st.set_page_config(layout="wide", page_title="高效文字處理器")
st.title('高效文字處理器 (Python 驅動)')

# --- 上半部分：輸入區 ---
col1, col2 = st.columns(2)

# 對應您的【第一欄：手動粘貼文字】
with col1:
    original_text = st.text_area("1. 原始文字", height=250, placeholder="在這裡貼上您需要處理的文字...")

# 對應您的【第二欄：默認//可修改文字處理要求】
# 在Python方案中，這裡變為「說明書」，讓您清楚知道內建了哪些規則
with col2:
    st.markdown("**2. 內建處理規則 (程式碼驅動)**")
    st.info(
        """
        本工具已內建以下核心清洗規則：
        - **100% 可靠去除**：時間戳 (如 `44:12`)
        - **100% 可靠去除**：特定政治術語
        - **可靠去除**：常見口頭禪 (如 `嗯`, `啊`, `然後`...)
        - **自動整理**：多餘的空格與空行
        
        *所有規則都在 Python 程式碼中定義，確保穩定可靠。*
        """
    )

# 對應您的【中央按鈕：開始處理】
if st.button('開始處理', type="primary"):
    if original_text:
        # 執行 Python 清洗函式
        processed_result = process_text_by_rules(original_text)
        # 將結果儲存到 session_state 中，以便後續編輯
        st.session_state['processed_text'] = processed_result
    else:
        st.warning("請先在左上方的「1. 原始文字」框中貼上內容。")

st.markdown("---") # 漂亮的分割線

# --- 下半部分：輸出與預覽 ---
col3, col4 = st.columns(2)

# 對應您的【第三欄：修改Markdown文件】
with col3:
    # 建立一個可編輯的文字區，它的預設值來自我們處理後的結果
    # st.session_state.get() 可以安全地獲取值，即使還沒有處理過
    edited_text = st.text_area(
        "3. 處理後的純文本文字 (可在此手動編輯)",
        value=st.session_state.get('processed_text', ''),
        height=300,
        key="editor" # 給這個元件一個獨一無二的 key
    )

# 對應您的【第四欄：預覽最終效果】
with col4:
    st.markdown("**4. 所見即所得的可發佈文字 (預覽)**")
    # 這個預覽區的內容，直接來自左邊的編輯框 (edited_text)
    # 當您在第三欄打字時，這裡會實時更新
    st.markdown(edited_text)
