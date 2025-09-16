# -*- coding: utf-8 -*-
"""
Created on Tue Sep 16 10:23:43 2025

@author: ALEX
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="CARACTERIZACIÓN GRANULOMÉTRICA", layout="centered")

st.markdown("<h1 style='text-align: center;'>CARACTERIZACIÓN GRANULOMÉTRICA</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center;'>Alex Fernando Quispe Mamani</h4>", unsafe_allow_html=True)

col1, col2 = st.columns([2, 2])

with col1:
    st.write("Ingrese el **peso total de la muestra**:")
    peso_total = st.number_input("Peso total (g)", min_value=0.01, step=0.01)

    st.write("Ingrese los datos de fracción retenida (mínimo 3 filas, máximo 20):")
    num_filas = st.number_input("Cantidad de fracciones", min_value=3, max_value=20, value=5, step=1)

    default_data = pd.DataFrame({
        "Tamaño (μm)": [0.0] * int(num_filas),
        "Peso retenido (g)": [0.0] * int(num_filas)
    })

    edited_df = st.data_editor(default_data, num_rows="dynamic", use_container_width=True)

with col2:
    st.markdown("""
    ### Esta herramienta permite analizar la **distribución granulométrica** de una muestra de partículas.

    A partir de los pesos retenidos sobre cada tamiz, calcula:
    - Tabla de análisis granulométrico.
    - Tamaños nominales (como d₅₀, d₈₀).
    - Estadísticos generales.
    - Diagramas de simple distribución y perfiles granulométricos
    - Estadísticos según Folk & Ward.

    Presiona **CALCULAR** para procesar los datos.
    """)

# Estado de cálculo
if "calculado" not in st.session_state:
    st.session_state["calculado"] = False

if st.button("CALCULAR", type="primary"):
    st.session_state["calculado"] = True

# Selector de gráfico (lista desplegable)
grafico_seleccionado = st.selectbox(
    "Seleccione el gráfico a mostrar:",
    ["DISTRIBUCIÓN POR CLASES (%Peso)", "%ACUMULADO PASANTE", "%ACUMULADO RETENIDO", "COMPARACIÓN DE CURVAS"]
)

if st.session_state["calculado"]:
    tab1, tab2 = st.tabs(["📊 Datos de entrada", "📈 Resultados"])

    with tab1:
        st.subheader("Tabla ingresada")
        st.dataframe(edited_df, use_container_width=True)

    with tab2:
        df = edited_df.dropna()
        df = df[df["Tamaño (μm)"] > 0].copy()

        if not df.empty and peso_total > 0:
            df = df.sort_values(by="Tamaño (μm)", ascending=False).reset_index(drop=True)

            peso_retenido_total = df["Peso retenido (g)"].sum()
            peso_menor = round(peso_total - peso_retenido_total, 6)

            if peso_menor > 0:
                ultimo_tamano = df["Tamaño (μm)"].iloc[-1]
                fila_extra = pd.DataFrame({
                    "Tamaño (μm)": [-ultimo_tamano],
                    "Peso retenido (g)": [peso_menor]
                })
                df = pd.concat([df, fila_extra], ignore_index=True).reset_index(drop=True)

            df["%Peso"] = (df["Peso retenido (g)"] / peso_total) * 100
            df["%R(d)"] = df["%Peso"].cumsum()
            df["%F(d)"] = 100 - df["%R(d)"]

            st.subheader("Tabla de datos procesados")
            st.dataframe(df[["Tamaño (μm)", "Peso retenido (g)", "%Peso", "%R(d)", "%F(d)"]],
                         use_container_width=True)

            df_plot = df[df["Tamaño (μm)"] > 0].sort_values(by="Tamaño (μm)")

            fig, ax = plt.subplots()
            ax.set_facecolor("white")
            fig.patch.set_facecolor("lightgray")
            ax.grid(False)
            ax.tick_params(colors='black')
            ax.set_xlabel("Tamaño de partícula (μm)")

            if grafico_seleccionado == "DISTRIBUCIÓN POR CLASES (%Peso)":
                ax.plot(df_plot["Tamaño (μm)"], df_plot["%Peso"], marker='x', color='green', linewidth=1)
                ax.set_ylabel("%Peso")
                ax.set_title("DISTRIBUCIÓN POR CLASES")

            elif grafico_seleccionado == "%ACUMULADO PASANTE":
                ax.set_ylim(0, 100)
                ax.plot(df_plot["Tamaño (μm)"], df_plot["%F(d)"], marker='x', color='red', linewidth=1)
                ax.set_ylabel("%F(d)")
                ax.set_title("%ACUMULADO PASANTE")

            elif grafico_seleccionado == "%ACUMULADO RETENIDO":
                ax.set_ylim(0, 100)
                ax.plot(df_plot["Tamaño (μm)"], df_plot["%R(d)"], marker='x', color='blue', linewidth=1)
                ax.set_ylabel("%R(d)")
                ax.set_title("%ACUMULADO RETENIDO")

            elif grafico_seleccionado == "COMPARACIÓN DE CURVAS":
                ax.set_ylim(0, 100)
                ax.plot(df_plot["Tamaño (μm)"], df_plot["%Peso"], marker='o', color='green', linewidth=1, label="%Peso")
                ax.plot(df_plot["Tamaño (μm)"], df_plot["%F(d)"], marker='s', color='red', linewidth=1, label="%F(d)")
                ax.plot(df_plot["Tamaño (μm)"], df_plot["%R(d)"], marker='^', color='blue', linewidth=1, label="%R(d)")
                ax.set_ylabel("Porcentaje (%)")
                ax.set_title("COMPARACIÓN DE CURVAS")
                ax.legend()

            st.pyplot(fig)

        else:
            st.warning("Por favor, ingrese datos válidos y un peso total mayor a cero.")
else:
    st.info("Ingrese los datos y presione **CALCULAR** para mostrar los resultados.")






