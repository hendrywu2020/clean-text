import streamlit as st
import re
import textwrap

# ----------------------------------------------------
# 核心處理引擎 (V4 - 基於長度分段的自然排版邏輯)
# ----------------------------------------------------
def process_text_by_rules(raw_text, paragraph_length=120):
    """
    採用更自然的排版邏輯：
    1. 將換行符理解為逗號/停頓。
    2. 按指定的長度，在合適的標點處切分段落。
    """
    if not raw_text or not raw_text.strip():
        return ""

    # 步驟一：基礎清洗
    text = raw_text
    text = re.sub(r'\[?\b\d{1,2}:\d{2}(:\d{2})?\b\]?\s*', '', text) # 去除時間戳
    filler_words = ['嗯', '啊', '呃', '這個', '那個', '就是說', '然後', '所以']
    filler_pattern = r'\b(' + '|'.join(map(re.escape, filler_words)) + r')\b\s*'
    text = re.sub(filler_pattern, '', text, flags=re.IGNORECASE) # 去除口頭禪

    # 步驟二：處理換行符，將其轉換為標點
    # 將連續換行（有意分段）替換為一個特殊標記
    text = re.sub(r'\n\s*\n+', '___PARAGRAPH_BREAK___', text)
    # 將單個換行（語氣停頓）替換為逗號
    text = text.replace('\n', '，')
    # 還原有意分段
    text = text.replace('___PARAGRAPH_BREAK___', '\n\n')

    # 步驟三：標點和空格的精細清理
    text = re.sub(r'[ \t]+', ' ', text).strip() # 清理多餘空格
    text = re.sub(r'[，\s]+([。！？\?])', r'\1', text) # 清理句號前的逗號和空格，例如「，。」->「。」
    text = re.sub(r'([，。！？\?])\1+', r'\1', text) # 清理連續的相同標點，例如「，，」->「，」
    text = re.sub(r'^[，\s]+', '', text) # 清理開頭的逗號和空格

    # 步驟四：按長度智能分段
    final_paragraphs = []
    
    # 先按用戶已有的分段符進行初步切分
    initial_paragraphs = text.split('\n\n')

    for para in initial_paragraphs:
        if not para.strip():
            continue
        
        # 如果段落本身不長，就沒必要再切分
        if len(para) <= paragraph_length * 1.2:
            final_paragraphs.append(para)
            continue

        # 使用 textwrap 庫來智能處理長段落
        # 它會按長度切分，並盡量保持單詞完整
        wrapper = textwrap.TextWrapper(
            width=paragraph_length,
            break_long_words=False,
            replace_whitespace=False,
            break_on_hyphens=False,
            # 在這些標點後斷開是比較好的選擇
            break_at_separators=['，', '。', '！', '？', ' ']
        )
        # 覆寫 textwrap 的 `_split` 方法來適應中文標點
        wrapper.wordsep_re = re.compile(r'([，。！？\?\s]+)')
        
        wrapped_lines = wrapper.wrap(para)
        final_paragraphs.extend(wrapped_lines)

    # 步驟五：最後整理，確保每段結尾是句號
    result_text = ""
    for para in final_paragraphs:
        p = para.strip()
        if not p:
            continue
        # 如果段落不是以結束標點結尾，則補上句號
        if not p.endswith(('。', '！', '？', '」', '』')):
            # 如果結尾是逗號，則將其替換為句號
            if p.endswith('，'):
                p = p[:-1] + '。'
            else:
                p += '。'
        result_text += p + '\n\n' # 使用雙換行符來分隔段落

    return result_text.strip()

# ----------------------------------------------------
# Streamlit 網頁介面定義
# ----------------------------------------------------
st.set_page_config(layout="wide", page_title="高效文字處理器")
st.title('高效文字處理器 (Python 驅動)')

# 初始化 session_state
if "processed_text_output" not in st.session_state:
    st.session_state.processed_text_output = ""

def run_processing():
    input_text = st.session_state.get("original_text_input", "")
    para_length = st.session_state.get("paragraph_length_input", 120)
    if input_text:
        processed_result = process_text_by_rules(input_text, para_length)
        st.session_state.processed_text_output = processed_result
    else:
        st.session_state.processed_text_output = ""
        st.warning("請先在左上方的「1. 原始文字」框中貼上內容。")

col1, col2 = st.columns(2)

with col1:
    st.text_area("1. 原始文字", height=300, placeholder="在這裡貼上您需要處理的文字...", key="original_text_input")

with col2:
    st.markdown("**2. 處理規則與設定**")
    
    st.slider(
        '設定期望的段落長度 (字符數)',
        min_value=50,
        max_value=250,
        value=120,
        step=10,
        help="本工具將嘗試在接近此長度的合適標點處進行分段。",
        key="paragraph_length_input"
    )
    
    st.info(
        """
        **當前處理邏輯 (V4)**:
        - **理解停頓**: 將換行符視為逗號。
        - **長度分段**: 按您設定的期望長度，在標點處智能切分段落。
        - **基礎清洗**: 去除時間戳和常見口頭禪。
        """
    )

st.button('開始處理', type="primary", on_click=run_processing)

st.markdown("---")
st.markdown("### 處理結果")
col3, col4 = st.columns(2)

with col3:
    edited_text = st.text_area(
        "處理後的純文字 (可在此手動編輯)",
        height=350,
        key="processed_text_output"
    )

with col4:
    st.markdown("**4. 所見即所得的可發佈文字 (預覽)**")
    preview_container = st.container(height=350, border=True)
    with preview_container:
        st.markdown(edited_text)
