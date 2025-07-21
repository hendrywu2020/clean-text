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
