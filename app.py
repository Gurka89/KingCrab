import sqlite3
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import datetime

# 🚀 Configuración del tema y ancho de página
st.set_page_config(page_title="KingCrab - Bolsa de Trabajo", page_icon="📊", layout="wide")

# 📂 Sidebar con información y logo
st.sidebar.title("KingCrab 📊")
st.sidebar.markdown("### Análisis de Mercado Laboral en Tiempo Real")
st.sidebar.info(
    "Esta aplicación extrae y analiza datos de diferentes portales de empleo "
    "para ofrecerte tendencias laborales actualizadas."
)
st.sidebar.markdown("---")
st.sidebar.write("👨‍💻 Desarrollado por [Tu Nombre]")

# 🎯 Conectar a la base de datos
conn = sqlite3.connect("database/kingcrab.db", check_same_thread=False)
df = pd.read_sql_query("SELECT titulo, url, fecha_publicacion FROM Trabajos", conn)
conn.close()

# 📊 **Extraer palabras más comunes desde SQL**
word_list = " ".join(df["titulo"].dropna().tolist()).lower().split()
word_freq = pd.Series(word_list).value_counts().reset_index()
word_freq.columns = ["Palabra", "Frecuencia"]
word_freq = word_freq[~word_freq["Palabra"].isin(["de", "y", "en", "para", "con", "el", "la"])]  # Palabras vacías
top_words = word_freq.head(5)

# 🔢 **Diseño de Streamlit con 3 columnas**
col1, col2, col3 = st.columns([1, 1, 1])

# 📊 **Gráfico de Barras en la primera columna**
with col1:
    st.markdown("### 📊 Palabras más repetidas")
    fig, ax = plt.subplots(figsize=(4, 3))
    sns.barplot(x=top_words["Frecuencia"], y=top_words["Palabra"], palette="magma", ax=ax)
    ax.set_title("Palabras Más Comunes", fontsize=10)
    ax.set_xlabel("Frecuencia", fontsize=9)
    ax.set_ylabel("Palabra", fontsize=9)
    st.pyplot(fig)

# ☁️ **Nube de Palabras en la segunda columna**
with col2:
    st.markdown("### ☁️ Nube de palabras")
    wordcloud = WordCloud(width=400, height=200, background_color="white").generate(" ".join(word_list))
    fig, ax = plt.subplots(figsize=(4, 3))
    ax.imshow(wordcloud, interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig)

# 📅 **Línea de Tiempo en la tercera columna**
with col3:
    st.markdown("### ⏳ Publicaciones a lo largo del tiempo")
    df["fecha_publicacion"] = pd.to_datetime(df["fecha_publicacion"], errors='coerce')
    df = df.dropna(subset=["fecha_publicacion"])
    df["fecha_publicacion"] = df["fecha_publicacion"].dt.date
    fecha_freq = df["fecha_publicacion"].value_counts().sort_index()
    
    if not fecha_freq.empty:
        fig, ax = plt.subplots(figsize=(4, 3))
        sns.lineplot(x=fecha_freq.index, y=fecha_freq.values, marker='o', ax=ax)
        ax.set_title("Publicaciones por Fecha", fontsize=10)
        ax.set_xlabel("Fecha", fontsize=9)
        ax.set_ylabel("Cantidad", fontsize=9)
        plt.xticks(rotation=45)
        st.pyplot(fig)
    else:
        st.write("📉 No hay suficientes datos para mostrar la línea de tiempo.")

# 🔍 **Filtro de Búsqueda**
st.markdown("## 🔎 Buscar Trabajo")
titulo_filtro = st.text_input("🔍 Escribe un título de trabajo:")

# 📝 **Filtrar en la base de datos en tiempo real**
if titulo_filtro:
    conn = sqlite3.connect("database/kingcrab.db", check_same_thread=False)
    query = "SELECT titulo, url FROM Trabajos WHERE titulo LIKE ?"
    df_filtrado = pd.read_sql_query(query, conn, params=(f"%{titulo_filtro}%",))
    conn.close()
else:
    df_filtrado = df.copy()

# 🔗 **Convertir URL en Hipervínculos**
df_filtrado["url"] = df_filtrado["url"].apply(lambda x: f"[🔗 Ver oferta]({x})" if x else "No disponible")

# 📋 **Mostrar Resultados en la tabla**
st.markdown("### 📋 Resultados de búsqueda:")
st.write(df_filtrado.to_markdown(index=False), unsafe_allow_html=True)
