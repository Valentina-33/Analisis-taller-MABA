import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración de la Página
st.set_page_config(
    page_title="Análisis de taller exponenciales y logaritmos",
    layout="wide",
    initial_sidebar_state="expanded"
)
# 2. Carga de Datos
try:
    # Intentar diferentes codificaciones
    encodings_to_try = ['utf-8-sig', 'latin-1', 'ISO-8859-1', 'cp1252', 'utf-8']

    df = None
    for encoding in encodings_to_try:
        try:
            df = pd.read_csv("datos_taller.csv",
                             encoding=encoding,
                             sep=';',
                             skiprows=1,
                             on_bad_lines='skip')
            print(f"✓ Archivo cargado exitosamente con encoding: {encoding}")
            break
        except UnicodeDecodeError:
            continue

    if df is None:
        st.error("No se pudo leer el archivo con ninguna codificación conocida.")
        st.stop()

    # Eliminar filas completamente vacías
    df = df.dropna(how='all')

    # **PUNTO 3: Eliminar estudiantes sin datos (solo con nombre y grupo)**
    # Solo mantener estudiantes que tengan al menos una nota
    df = df[df['Nota_Final'].notna()]

    # Limpieza de datos esencial
    df['Nota_Final'] = pd.to_numeric(df['Nota_Final'], errors='coerce')

    # **PUNTO 1: Limpiar columnas pero mantener "Regular"**
    for col in ['Uso_Grafico', 'Uso_IA']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            # Normalizar solo las variaciones de Sí/No, mantener Regular
            df[col] = df[col].str.replace('Sí', 'SI', case=False)
            df[col] = df[col].str.replace('SÍ', 'SI', case=False)
            # Capitalizar correctamente
            df[col] = df[col].str.capitalize()
            df[col] = df[col].replace('Si', 'Sí')
            df[col] = df[col].replace('No', 'No')

    # Asegurarse de que la columna 'Grupo' exista
    if 'Grupo' not in df.columns:
        df['Grupo'] = 'Sin Asignar'
    else:
        df['Grupo'] = pd.to_numeric(df['Grupo'], errors='coerce')
        df['Grupo'] = df['Grupo'].fillna('Sin Asignar')
        df['Grupo'] = df['Grupo'].astype(str)

except FileNotFoundError:
    st.error("🚨 Error: No se encontró el archivo 'datos_taller.csv'.")
    st.stop()
except Exception as e:
    st.error(f"🚨 Error al cargar o procesar los datos: {e}")
    import traceback

    st.error(traceback.format_exc())
    st.stop()

# FILTRO DE GRUPO PRINCIPAL
st.sidebar.title("Opciones de visualización")
grupo_seleccionado = st.sidebar.selectbox(
    "Seleccione el grupo a analizar",
    ['Todos los Grupos'] + list(df['Grupo'].unique())
)

# Aplicar filtro
if grupo_seleccionado != 'Todos los Grupos':
    df_filtrado = df[df['Grupo'] == grupo_seleccionado].copy()
else:
    df_filtrado = df.copy()

# Títulos
st.title("📊 Análisis de desempeño: Taller exponenciales y logaritmos")
st.subheader(f"Mostrando datos para: **{grupo_seleccionado}**")
st.markdown("---")
# 3. Métrica y Resumen General
col1, col2, col3 = st.columns(3)

if not df_filtrado.empty:
    nota_promedio = df_filtrado['Nota_Final'].mean()
    col1.metric("Nota promedio del grupo", f"{nota_promedio:.2f}")

    # **PUNTO 2: Corregir cálculo de porcentajes contando solo Sí**
    total_estudiantes = len(df_filtrado)

    porcentaje_grafico = (df_filtrado['Uso_Grafico'] == 'Sí').sum() / total_estudiantes * 100
    col2.metric("% Estudiantes que usaron gráficas", f"{porcentaje_grafico:.1f}%")

    porcentaje_ia = (df_filtrado['Uso_IA'] == 'Sí').sum() / total_estudiantes * 100
    col3.metric("% Estudiantes que usaron IA", f"{porcentaje_ia:.1f}%")
else:
    st.warning("No hay datos para mostrar con la selección actual.")
    st.stop()

## 4. Análisis Detallado (Punto 1 y 2 de la Profesora)
st.header("🔍 Enfoque Metodológico y Gráfico")

col_despeje, col_grafico = st.columns(2)

# Gráfico 1: Despeje Logarítmico
with col_despeje:
    st.subheader("1. Método de despeje logarítmico")
    conteo_despeje = df_filtrado['Metodo_Despeje'].value_counts().reset_index()
    conteo_despeje.columns = ['Método', 'Frecuencia']

    fig_despeje = px.bar(
        conteo_despeje, x='Método', y='Frecuencia',
        title='Distribución por Método de Despeje',
        color='Método', text='Frecuencia'
    )
    fig_despeje.update_layout(xaxis_title="", yaxis_title="Número de Estudiantes")
    st.plotly_chart(fig_despeje, use_container_width=True)

# Gráfico 2: Uso de la Representación Gráfica
with col_grafico:
    st.subheader("2. Uso y aplicación de la gráfica")
    conteo_grafico = df_filtrado['Uso_Grafico'].value_counts().reset_index()
    conteo_grafico.columns = ['Uso', 'Frecuencia']

    fig_grafico = px.pie(
        conteo_grafico, names='Uso', values='Frecuencia',
        title='Distribución de uso de la representación gráfica',
        color_discrete_sequence=px.colors.qualitative.Safe
    )
    st.plotly_chart(fig_grafico, use_container_width=True)

st.markdown("---")

## 5. Análisis del Uso de la IA (Punto 3 de la Profesora)
st.header("🤖 Análisis del uso y dificultades de la IA")

# 5.1. Gráfico de Histograma de Notas
st.subheader("Distribución general de notas")
fig_hist = px.histogram(df_filtrado, x='Nota_Final', nbins=10, title="Frecuencia de notas finales")
fig_hist.update_layout(xaxis_title="Nota Final", yaxis_title="Número de estudiantes")
st.plotly_chart(fig_hist, use_container_width=True)

# 5.2. Resumen de Desventajas/Dificultades de la IA
st.subheader("Resumen de desventajas y dificultades al usar la IA")

# **CORRECCIÓN: Filtrar correctamente estudiantes que usaron IA (Sí o Regular)**
df_ia = df_filtrado[df_filtrado['Uso_IA'].isin(['Sí', 'Regular'])]

if not df_ia.empty:
    # Filtrar solo los que tienen comentarios
    df_ia_con_comentarios = df_ia[df_ia['Expli_Uso_IA'].notna() & (df_ia['Expli_Uso_IA'].astype(str).str.strip() != '')]

    if not df_ia_con_comentarios.empty:
        st.dataframe(df_ia_con_comentarios[['Nombre', 'Uso_IA', 'Expli_Uso_IA']],
                     column_config={
                         "Nombre": st.column_config.TextColumn("Estudiante"),
                         "Uso_IA": st.column_config.TextColumn("Nivel de uso"),
                         "Expli_Uso_IA": st.column_config.TextColumn("Comentarios sobre uso de IA")
                     },
                     hide_index=True, use_container_width=True)
    else:
        st.info("Los estudiantes que usaron IA no tienen comentarios registrados.")
else:
    st.info("No hay datos de estudiantes que reportaron haber usado la IA en este grupo.")

## 6. Retroalimentación Individual (Acceso Fácil)
st.header("👤 Retroalimentación individual y calificación")

estudiante_seleccionado = st.selectbox(
    "Seleccione el estudiante para ver la retroalimentación:",
    df_filtrado['Nombre'].unique()
)

if estudiante_seleccionado:
    datos_estudiante = df_filtrado[df_filtrado['Nombre'] == estudiante_seleccionado].iloc[0]

    st.subheader(f"Resultados de {datos_estudiante['Nombre']}")

    col_score, col_feedback = st.columns([1, 2])

    with col_score:
        st.metric("Nota Final", datos_estudiante['Nota_Final'])

        retro_url = datos_estudiante['Link_Retro']
        if pd.notna(retro_url) and str(retro_url).strip() != '':
            # Limpiar el texto del link
            texto_link = str(retro_url).strip()
            
            # Verificar si parece un link (contiene http o .com/.pdf)
            if 'http' in texto_link or '.com' in texto_link or '.pdf' in texto_link:
                st.markdown(f"📄 [Ver retroalimentación]({texto_link})", unsafe_allow_html=True)
            else:
                st.info(f"📄 Documento: {texto_link}")
        else:
            st.info("⚠️ Link de retroalimentación no disponible")

    with col_feedback:
        st.markdown(f"**Despeje Logarítmico ({datos_estudiante['Metodo_Despeje']}):**")
        st.info(datos_estudiante['Expli_Despeje'])

        st.markdown(f"**Uso Gráfico ({datos_estudiante['Uso_Grafico']}):**")
        st.info(datos_estudiante['Expli_Grafico'])

        st.markdown(f"**Uso de IA ({datos_estudiante['Uso_IA']}):**")

        st.info(datos_estudiante['Expli_Uso_IA'])

