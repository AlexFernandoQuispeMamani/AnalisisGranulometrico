# -*- coding: utf-8 -*-
"""
Created on Sat May 24 23:48:44 2025

@author: ALEX
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="CARACTERIZACIÓN GRANULOMÉTRICA", layout="centered")

st.markdown("<h1 style='text-align: center;'>CARACTERIZACIÓN GRANULOMÉTRICA</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center;'>Alex Fernando Quispe Mamani</h4>", unsafe_allow_html=True)

# --- PARTE 3: ENTRADA DE DATOS ---

# Inicializar el estado de la página si no existe
if "page" not in st.session_state:
    st.session_state.page = "input"

if st.session_state.page == "input":

    col1, col2 = st.columns([2, 2])

    with col1:
        st.write("Ingrese el **peso total de la muestra**:")
        peso_total = st.number_input("Peso total (g)", min_value=0.01, step=0.01)

        st.write("Ingrese los datos de fracción retenida (mínimo 3 filas, máximo 20):")
        num_filas = st.number_input("Cantidad de fracciones", min_value=3, max_value=20, value=5, step=1)

        default_data = pd.DataFrame({
            "Tamaño [μm]": [0.0] * int(num_filas),
            "Peso retenido [g]": [0.0] * int(num_filas)
        })

        edited_df = st.data_editor(
            default_data,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "Tamaño [μm]": st.column_config.NumberColumn(width="small"),
                "Peso retenido [g]": st.column_config.NumberColumn(width="small"),
            }
        )

        # Botón para pasar a la ventana de resultados
        if st.button("CALCULAR"):
            # Guardar los datos en session_state
            st.session_state.peso_total = peso_total
            st.session_state.edited_df = edited_df
            st.session_state.page = "results"

    with col2:
        st.markdown("""
        ### Esta herramienta permite analizar la **distribución granulométrica** de una muestra de partículas.

        A partir de los pesos retenidos sobre cada tamiz, calcula:
        - Tabla de análisis granulométrico.
        - Tamaños nominales (como d₅₀, d₈₀).
        - Estadísticos generales.
        - Diagramas de simple distribución y perfiles granulométricos.
        - Estadísticos según Folk & Ward.

        Presiona **CALCULAR** para procesar los datos.
        """)
        
# Estado de cálculo
if "calculado" not in st.session_state:
    st.session_state["calculado"] = False

if st.button("CALCULAR", type="primary"):
    st.session_state["calculado"] = True

# Control de gráfico (fuera del botón)
grafico_seleccionado = st.radio(
    "Seleccione el gráfico a mostrar:",
    ["DISTRIBUCIÓN POR CLASES (%Peso)", "%ACUMULADO PASANTE", "%ACUMULADO RETENIDO"],
    horizontal=True
)

if st.session_state["calculado"]:
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

            tamaños = df_plot["Tamaño (μm)"]
            pesos = df_plot["%Peso"]
            media = np.average(tamaños, weights=pesos)
            moda = tamaños.loc[pesos.idxmax()]
            acumulado = pesos.cumsum()
            mediana = tamaños.loc[acumulado[acumulado >= 50].index[0]]

            st.markdown(f"""
            **Estadísticos de la distribución por clases (%Peso):**  
            - Media: {media:.2f} μm  
            - Moda: {moda:.2f} μm  
            - Mediana: {mediana:.2f} μm
            """)

        elif grafico_seleccionado == "%ACUMULADO PASANTE":
            df_pasante = pd.concat([
                pd.DataFrame({"Tamaño (μm)": [0], "%F(d)": [0]}),
                df_plot[["Tamaño (μm)", "%F(d)"]]
            ]).sort_values(by="Tamaño (μm)")
            ax.set_ylim(0, 100)
            ax.plot(df_pasante["Tamaño (μm)"], df_pasante["%F(d)"], marker='x', color='red', linewidth=1)
            ax.set_ylabel("%F(d)")
            ax.set_title("%ACUMULADO PASANTE")

        elif grafico_seleccionado == "%ACUMULADO RETENIDO":
            df_retenido = pd.concat([
                pd.DataFrame({"Tamaño (μm)": [0], "%R(d)": [100]}),
                df_plot[["Tamaño (μm)", "%R(d)"]]
            ]).sort_values(by="Tamaño (μm)")
            ax.set_ylim(0, 100)
            ax.plot(df_retenido["Tamaño (μm)"], df_retenido["%R(d)"], marker='x', color='blue', linewidth=1)
            ax.set_ylabel("%R(d)")
            ax.set_title("%ACUMULADO RETENIDO")

        st.pyplot(fig)

        # Tamaños nominales (d05, d16, etc.)
        st.subheader("Tamaños nominales")
        objetivos = [5, 16, 25, 50, 75, 80, 84, 95]
        resultados = {}
        d05_extrapolado = False
        d95_extrapolado = False

        # Asegurar que los datos estén ordenados por %F(d)
        df_interp = df_plot[["Tamaño (μm)", "%F(d)"]].sort_values(by="%F(d)").drop_duplicates(subset=["%F(d)"])

        def interpolar_percentil(x_vals, y_vals, percentil):
            for i in range(len(y_vals) - 1):
                if y_vals[i] < percentil <= y_vals[i + 1]:
                    x0, x1 = x_vals[i], x_vals[i + 1]
                    y0, y1 = y_vals[i], y_vals[i + 1]
                    if y1 != y0:
                        return x0 + (percentil - y0) * (x1 - x0) / (y1 - y0)
            return None

        x = df_interp["Tamaño (μm)"].values
        y = df_interp["%F(d)"].values

        for obj in objetivos:
            val = interpolar_percentil(x, y, obj)
    
            # Extrapolación para d_05 si no se puede interpolar
            for obj in objetivos:
                val = interpolar_percentil(x, y, obj)
    
                # Extrapolar/interpolar d_05 si no se pudo interpolar y curva no llega a 5%
                if val is None and obj == 5 and len(x) >= 1:
                    if y[0] > 5:
                        # Punto ficticio (0,0)
                        x0, y0 = 0, 0
                        x1, y1 = x[0], y[0]
                        pendiente = (x1 - x0) / (y1 - y0)
                        val = x0 + (obj - y0) * pendiente
                        d05_extrapolado = True

                # Extrapolar/interpolar d_16 y d_25 similar a d_05 si no hay valor interpolado y curva no llega a esos percentiles
                if val is None and obj in [16, 25] and len(x) >= 1:
                    if y[0] > obj:
                        # Punto ficticio (0,0)
                        x0, y0 = 0, 0
                        x1, y1 = x[0], y[0]
                        pendiente = (x1 - x0) / (y1 - y0)
                        val = x0 + (obj - y0) * pendiente
                        if obj == 16:
                            d16_extrapolado = True
                        else:
                            d25_extrapolado = True

                # Extrapolar d_95 si no se pudo interpolar
                if val is None and obj == 95 and len(x) >= 2:
                    x0, x1 = x[-2], x[-1]
                    y0, y1 = y[-2], y[-1]
                    if y1 > y0 and x1 > x0:
                        pendiente = (x1 - x0) / (y1 - y0)
                        val = x1 + (obj - y1) * pendiente
                        d95_extrapolado = True

                resultados[f"d_{obj:02}"] = round(val, 2) if isinstance(val, (int, float)) else "No disponible"

            # Extrapolación para d_95 si no se puede interpolar
            if val is None and obj == 95 and len(x) >= 2:
                # Tomamos los dos últimos puntos para extrapolar hacia arriba
                x0, x1 = x[-2], x[-1]
                y0, y1 = y[-2], y[-1]
                if y1 > y0 and x1 > x0:
                    pendiente = (x1 - x0) / (y1 - y0)
                    val = x1 + (obj - y1) * pendiente
                    d95_extrapolado = True

            resultados[f"d_{obj:02}"] = round(val, 2) if isinstance(val, (int, float)) else "No disponible"

        # Mostrar valores en columnas
        cols_nominales = st.columns(len(resultados))
        for i, (clave, valor) in enumerate(resultados.items()):
            with cols_nominales[i]:
                st.markdown(f"**{clave} =** {valor} μm")

        # Mostrar advertencias si hubo extrapolación
        if d05_extrapolado:
            st.info("Nota: El valor de **d_05** fue estimado por extrapolación a partir de los dos primeros puntos de la curva.")
        if d95_extrapolado:
            st.info("Nota: El valor de **d_95** fue estimado por extrapolación a partir de los dos últimos puntos de la curva.")

        # Estadística Folk & Ward
        st.subheader("Estadística granulométrica según Folk y Ward")

        def es_num(x):
            return isinstance(x, (int, float))

        d_05 = resultados.get("d_05")
        d_16 = resultados.get("d_16")
        d_25 = resultados.get("d_25")
        d_50 = resultados.get("d_50")
        d_75 = resultados.get("d_75")
        d_84 = resultados.get("d_84")
        d_95 = resultados.get("d_95")

        Md = f"{d_50:.2f} μm" if es_num(d_50) else "No disponible"
        M = f"{((d_16 + d_50 + d_84) / 3):.2f} μm" if all(es_num(x) for x in [d_16, d_50, d_84]) else "No disponible"
        sigma_val = ((d_84 - d_16) / 4) + ((d_95 - d_05) / 6.6) if all(es_num(x) for x in [d_16, d_84, d_05, d_95]) else None
        sigma = f"{sigma_val:.2f} μm" if sigma_val is not None else "No disponible"
        Sk_val = (((d_84 + d_16 - 2 * d_50) / (2 * (d_84 - d_16))) + ((d_95 + d_05 - 2 * d_50) / (2 * (d_95 - d_05)))) if all(es_num(x) for x in [d_16, d_84, d_50, d_05, d_95]) else None
        Sk = f"{Sk_val:.2f}" if Sk_val is not None else "No disponible"
        KG_val = (d_95 - d_05) / (2.44 * (d_75 - d_25)) if all(es_num(x) for x in [d_95, d_05, d_75, d_25]) and (d_75 - d_25) != 0 else None
        KG = f"{KG_val:.2f}" if KG_val is not None else "No disponible"

        st.markdown(f"""
                    - Md = {Md}  
                    - M = {M}  
                    - σ = {sigma}  
                    - Sk = {Sk}  
                    - K = {KG}
                    """)

        # Comentarios de interpretación
        st.subheader("Interpretación de los estadísticos Folk & Ward")

        if sigma_val is None or Sk_val is None or KG_val is None:
            st.warning("No se pueden generar interpretaciones completas debido a datos incompletos.")
        else:
            if sigma_val < 0.35:
                disp = "La muestra presenta una distribución granulométrica muy uniforme (bien seleccionada)."
            elif sigma_val < 0.50:
                disp = "La muestra presenta una distribución relativamente uniforme (moderadamente seleccionada)."
            else:
                disp = "La muestra presenta una amplia dispersión de tamaños"

            if Sk_val < -0.3:
                asim = "La distribución es sesgada hacia partículas finas."
            elif Sk_val > 0.3:
                asim = "La distribución es sesgada hacia partículas gruesas."
            else:
                asim = "La distribución es relativamente simétrica."

            if KG_val < 0.67:
                curt = "La distribución es platicúrtica (colas anchas, pico bajo)."
            elif KG_val > 1.00:
                curt = "La distribución es leptocúrtica (colas delgadas, pico alto)."
            else:
                curt = "La distribución es mesocúrtica (forma normal)."

            st.markdown(f"""
                        - **Dispersión (σ):** {disp}  
                        - **Asimetría (Sk):** {asim}  
                        - **Curtosis (K):** {curt}
                        """)

        st.info("Los estadísticos con la descripción **No disponible** se deben a que uno o más valores nominales no pudieron ser definidos a partir de los datos ingresados.")

    else:
        st.warning("Por favor, ingrese datos válidos y un peso total mayor a cero.")
else:
    st.info("Ingrese los datos y presione **CALCULAR** para mostrar los resultados.")


