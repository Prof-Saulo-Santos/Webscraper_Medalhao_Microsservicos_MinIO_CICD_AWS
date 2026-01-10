import streamlit as st
from app.services.search_engine import SearchEngine


def main():
    st.set_page_config(page_title="ArXiv Semantic Search", layout="wide")

    st.title("📚 ArXiv Semantic Search")
    st.markdown("Busca inteligente em artigos científicos usando BERT embeddings.")

    # Sidebar
    with st.sidebar:
        st.header("Configurações")
        top_k = st.slider("Número de resultados", 1, 20, 5)
        if st.button("Reload Data"):
            st.cache_data.clear()
            st.success("Cache limpo! Recarregue a busca.")

    engine = SearchEngine()
    
    bronze_count = engine.get_bronze_count()
    silver_count = engine.get_silver_count()
    
    st.markdown(f":orange[Bronze: {bronze_count}] | :blue[Silver: {silver_count}]")

    # Input
    query = st.text_input(
        "O que você está procurando?",
        placeholder="Ex: 'Applications of LLMs in Healthcare'",
    )

    if query:
        with st.spinner("Pesquisando..."):
            results = engine.search(query, top_k=top_k)

        st.write(f"Encontrados {len(results)} resultados relevantes.")

        for item in results:
            with st.expander(f"{item['title']} (Score: {item['score']:.4f})"):
                st.markdown(f"**Categories:** {item['categories']}")
                st.markdown(f"**Summary:** {item['summary']}")
                st.caption(f"ID: {item['id']}")


if __name__ == "__main__":
    main()
