import streamlit as st
import re

# ----------------------------------------------------
# 核心處理引擎
# 新邏輯：基於無格式文本，按指定句子數量主動創造段落。
# ----------------------------------------------------
def process_text_by_rules(raw_text, sentences_per_paragraph=5):
    """
    這是一個穩定、可靠的文字清洗引擎。
    新邏輯：基於無格式文本，按指定句子數量主動創造段落。
    """
    # 如果輸入為空，直接返回
    if not raw_text or not raw_text.strip():
        return ""

    text = raw_text

    # 步驟一：基礎清洗
    text = re.sub(r'\[?\b\d{1,2}:\d{2}(:\d{2})?\b\]?\s*', '', text) # 去除時間戳
    filler_words = ['嗯', '啊', '呃', '這個', '那個', '就是說', '然後', '所以']
    filler_pattern = r'\b(' + '|'.join(map(re.escape, filler_words)) + r')\b\s*'
    text = re.sub(filler_pattern, '', text, flags=re.IGNORECASE) # 去除口頭禪
    text = re.sub(r'[ \t]+', ' ', text).strip() # 整理多餘空格

    # 步驟二：為沒有標點的行尾添加句號 (這是將原始斷句標準化的關鍵)
    # 這個正則表達式能找到沒有以標點結尾的換行符，並在前面加上句號
    text = re.sub(r'([^。！？\?])\n', r'\1。\n', text)
    # 確保全文最後一行也有標點
    if text.strip() and not re.search(r'[。！？\?]$', text.strip()):
         text = text.strip() + '。'

    # 步驟三：拆分成句子列表
    # splitlines() 會根據 \n 拆分，現在每個 \n 前面基本都有了標點，所以效果等於按句拆分
    sentences = [s.strip() for s in text.splitlines() if s.strip()]

    # 步驟四：按指定數量組合句子，形成段落
    paragraphs = []
    # 使用 range 的步長功能，以 sentences_per_paragraph 為單位進行切割
    for i in range(0, len(sentences), sentences_per_paragraph):
        # 將切割出的句子片段用空格連接成一個段落
        paragraph = ' '.join(sentences[i:i + sentences_per_paragraph])
        paragraphs.append(paragraph)

    # 步驟五：將新生成的段落用雙換行符連接並返回
    return '\n\n'.join(paragraphs)


# ----------------------------------------------------
# Streamlit 網頁介面定義
# ----------------------------------------------------
st.set_page_config(layout="wide", page_title="高效文字處理器")
st.title('高效文字處理器 (Python 驅動)')

col1, col2 = st.columns(2)

with col1:
    original_text = st.text_area("1. 原始文字", height=300, placeholder="在這裡貼上您需要處理的文字...")

with col2:
    st.markdown("**2. 處理規則與設定**")
    
    # 新增：段落句子數量控制器
    sentences_count = st.number_input(
        '設定每個段落包含的句子數量',
        min_value=1,
        max_value=20,
        value=4,  # 預設值，您可以根據喜好調整
        step=1,
        help="由於原始文字無格式，本工具將按此處設定的句子數量自動分段。句子是根據原始文字的換行來判斷的。"
    )
    
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
        # 在調用函數時，傳入控制器中的值
        processed_result = process_text_by_rules(original_text, sentences_count)
        st.session_state['processed_text'] = processed_result
    else:
        st.warning("請先在左上方的「1. 原始文字」框中貼上內容。")

st.markdown("---")

# 處理後與預覽區域
st.markdown("### 處理結果")
col3, col4 = st.columns(2)

with col3:
    edited_text = st.text_area(
        "3. 處理後的純文字 (可在此手動編輯)",
        value=st.session_state.get('processed_text', ''),
        height=350,
        key="editor"
    )

with col4:
    st.markdown("**4. 所見即所得的可發佈文字 (預覽)**")
    # 使用 st.container() 和 CSS 來模擬預覽框，使其滾動
    preview_container = st.container(height=350, border=True)
    with preview_container:
        st.markdown(edited_text)
