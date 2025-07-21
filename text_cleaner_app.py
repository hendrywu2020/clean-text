import streamlit as st
import re
import spacy

# ----------------------------------------------------
# 1. 核心處理引擎 (純 Python + spaCy) - 版本 3.0
# ----------------------------------------------------

# --- 使用 Streamlit 的快取功能，讓模型只載入一次，大幅提升速度 ---
@st.cache_resource
def load_spacy_model():
    """安全地載入 spaCy 中文模型"""
    # 從下載的套件中載入模型
    return spacy.load("zh_core_web_sm")

# 載入模型
nlp = load_spacy_model()

def process_text_with_nlp(raw_text):
    """
    這是我們最終的文字清洗引擎，結合了規則和 NLP。
    """
    # --- 預處理：先做一些基本的、不影響句子結構的清洗 ---
    text = raw_text
    # 規則一：去除時間戳
    text = re.sub(r'\[?\b\d{1,2}:\d{2}(:\d{2})?\b\]?\s*', '', text)
    # 規則二：去除常見口頭禪
    filler_words = ['嗯', '啊', '呃', '這個', '那個', '就是說', '然後', '所以']
    text = re.sub(r'\b(' + '|'.join(filler_words) + r')\b', '', text, flags=re.IGNORECASE)
    # 將多個換行符合併為一個，方便 spaCy 處理
    text = re.sub(r'\s*\n\s*', ' ', text.strip())


    # --- 核心步驟：使用 spaCy 進行智能分句和分段 ---
    doc = nlp(text)
    
    paragraphs = []
    current_paragraph = ""
    
    # 遍歷 spaCy 準確切分出的每一個句子
    for sent in doc.sents:
        sentence_text = sent.text.strip()
        
        # 如果當前段落加上新句子會超過200字
        if len(current_paragraph) + len(sentence_text) > 200 and current_paragraph:
            # 就把當前的段落存起來
            paragraphs.append(current_paragraph)
            # 開始一個新段落
            current_paragraph = sentence_text
        else:
            # 否則，就把新句子加到當前段落後面 (如果段落不為空，加個空格)
            if current_paragraph:
                current_paragraph += " " + sentence_text
            else:
                current_paragraph = sentence_text
                
    # 不要忘記把最後一個段落也加進去
    if current_paragraph:
        paragraphs.append(current_paragraph)
        
    # 用兩個換行符 (代表一個空行) 將所有段落組合起來
    final_text = "\n\n".join(paragraphs)
    
    return final_text

# ----------------------------------------------------
# 2. Streamlit 網頁介面定義 (這部分無需修改)
# ----------------------------------------------------
st.set_page_config(layout="wide", page_title="高效文字處理器")
st.title('高效文字處理器 (Python + NLP 驅動)')

col1, col2 = st.columns(2)

with col1:
    original_text = st.text_area("1. 原始文字", height=250, placeholder="在這裡貼上您需要處理的文字...")

with col2:
    st.markdown("**2. 內建處理規則 (程式碼驅動)**")
    st.info(
        """
        本工具採用 **spaCy NLP 引擎** 進行智能處理：
        - **智能分句**：能準確識別句子邊界，而不僅僅依賴標點。
        - **自動分段**：將句子組合成不超過200字的最佳段落。
        - **可靠去除**：時間戳和常見口頭禪。
        """
    )

if st.button('開始處理', type="primary"):
    if original_text:
        # 調用我們新的 NLP 處理函式
        processed_result = process_text_with_nlp(original_text)
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
