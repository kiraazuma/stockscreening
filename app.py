import streamlit as st
from stock_screening_gui_line import screen_stocks
import tempfile
import os

st.set_page_config(page_title="株スクリーニングツール", layout="wide")
st.title("📊 株スクリーニングツール（Breakout & Pullback）")

# === ファイルアップロード ===
st.markdown("### Step 1: 銘柄リストのアップロード")
uploaded_file = st.file_uploader("日経225+αのExcelファイルを選択してください（.xlsx）", type="xlsx")

# === パラメータ設定 ===
st.markdown("### Step 2: スクリーニング設定")
days = st.slider("過去何日分の株価データを使用するか", min_value=30, max_value=120, value=60)
sheet_name = st.text_input("シート名（通常はSheet1）", value="Sheet1")

# === LINE通知設定 ===
use_line = st.checkbox("LINE通知を有効にする")
line_token = st.text_input("LINE Notifyのアクセストークン（※公開しないでください）", type="password") if use_line else None

# === 実行ボタン ===
if st.button("📈 スクリーニングを実行"):
    if uploaded_file is None:
        st.error("Excelファイルをアップロードしてください")
    else:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name

        output_path = os.path.join(tempfile.gettempdir(), "screening_result.xlsx")

        with st.spinner("スクリーニング実行中..."):
            screen_stocks(
                input_file=tmp_path,
                output_file=output_path,
                sheet_name=sheet_name,
                days_back=days,
                line_token=line_token
            )

        st.success("✅ スクリーニング完了！")
        with open(output_path, "rb") as f:
            st.download_button("📥 結果Excelをダウンロード", f, file_name="screening_result.xlsx")
