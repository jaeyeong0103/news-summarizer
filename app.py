import streamlit as st
from transformers import pipeline
from newspaper import Article


# 요약 모델 로드 (한 번만 로드되도록 캐시)
@st.cache_resource
def load_summarizer():
    summarizer = pipeline(
        "summarization",
        model="facebook/bart-large-cnn"  # 영문 기사용 대표 요약 모델
    )
    return summarizer


def extract_article_text(url: str) -> str:
    """뉴스 URL에서 기사 본문 텍스트를 추출"""
    article = Article(url)
    article.download()
    article.parse()
    return article.text


def summarize_long_text(summarizer, text: str,
                        max_len: int = 130,
                        min_len: int = 40) -> str:
    """
    너무 긴 텍스트는 앞 부분만 사용해서 요약
    (단순하지만 과제 수준에서는 충분)
    """
    MAX_INPUT_CHARS = 4000
    if len(text) > MAX_INPUT_CHARS:
        text = text[:MAX_INPUT_CHARS]

    summary = summarizer(
        text,
        max_length=max_len,
        min_length=min_len,
        do_sample=False
    )[0]["summary_text"]

    return summary


# ------------ Streamlit UI ------------
st.title("📰 뉴스 링크 요약기")
st.write(
    "뉴스 기사 **링크(URL)** 를 입력하면, "
    "기사 내용을 불러와서 자동으로 요약해주는 프로그램입니다."
)

url = st.text_input(
    "뉴스 기사 링크(URL)를 입력하세요.",
    placeholder="예: https://www.bbc.com/news/..."
)

col1, col2 = st.columns(2)
with col1:
    max_len = st.slider("요약 최대 길이", 50, 300, 130, 10)
with col2:
    min_len = st.slider("요약 최소 길이", 10, 150, 40, 10)

summarizer = load_summarizer()

if st.button("요약하기"):
    if not url.strip():
        st.warning("먼저 뉴스 링크를 입력해주세요.")
    else:
        try:
            with st.spinner("기사를 불러오는 중입니다..."):
                article_text = extract_article_text(url)

            if not article_text.strip():
                st.error("기사를 읽어오지 못했습니다. URL을 다시 확인해 주세요.")
            else:
                st.success("기사 불러오기 완료! 요약 중입니다...")

                with st.spinner("요약 생성 중..."):
                    summary = summarize_long_text(
                        summarizer,
                        article_text,
                        max_len=max_len,
                        min_len=min_len
                    )

                st.subheader("✅ 요약 결과")
                st.write(summary)

                with st.expander("원문 기사 보기"):
                    st.write(article_text)

        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")
            st.info("뉴스 링크가 올바른지, 로그인/유료벽이 없는 기사인지 확인해주세요.")
