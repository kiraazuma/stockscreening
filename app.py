import streamlit as st
import datetime
from stock_screening_gui_line import screen_stocks

st.set_page_config(page_title="株スクリーニングツール", layout="wide")
st.title("📈 株スクリーニング＆通知ツール")

# ファイルアップロード
uploaded_file = st.file_uploader("銘柄リストファイル（Excel）をアップロードしてください", type=["xlsx"])

# 各種パラメータ入力
st.sidebar.header("🔧 スクリーニング設定")
days_back = st.sidebar.slider("過去何日分のデータを取得するか", min_value=30, max_value=90, value=60)

line_token = st.sidebar.text_input("LINE Notify トークン（通知を受けたい場合のみ）", type="password")

output_filename = st.text_input("出力ファイル名", value="screening_result.xlsx")

# 実行ボタン
if st.button("🚀 スクリーニングを実行"):
    if uploaded_file is not None:
        with st.spinner("スクリーニング中..."):
            try:
                screen_stocks(
                    input_file=uploaded_file,
                    output_file=output_filename,
                    sheet_name="Sheet1",
                    days_back=days_back,
                    line_token=line_token if line_token else None
                )
                st.success("✅ スクリーニング完了！")
                with open(output_filename, "rb") as f:
                    st.download_button(
                        label="📥 結果をダウンロード",
                        data=f,
                        file_name=output_filename,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            except Exception as e:
                st.error(f"❌ エラーが発生しました: {e}")
    else:
        st.warning("⚠️ Excelファイルをアップロードしてください。")
