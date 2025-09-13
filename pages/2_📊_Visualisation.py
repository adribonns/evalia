import streamlit as st
import os, json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

DATA_DIR = "data"

st.title("📊 Visualisation des scénarios")

if not os.path.exists(DATA_DIR) or not os.listdir(DATA_DIR):
    st.warning("Aucun scénario trouvé.")
else:
    scenario = st.selectbox("Choisir un scénario", os.listdir(DATA_DIR))
    scen_dir = os.path.join(DATA_DIR, scenario)

    # Charger description
    with open(os.path.join(scen_dir, "scenario.json")) as f:
        scenario_data = json.load(f)
    st.markdown(f"## {scenario_data['nom']}")
    st.markdown(scenario_data.get("description", ""))

    # Charger solutions
    data = []
    details = {}
    for file in os.listdir(scen_dir):
        if file.endswith(".json") and file != "scenario.json":
            with open(os.path.join(scen_dir, file)) as f:
                sol = json.load(f)
            df_sol = pd.DataFrame(sol["criteres"])
            means = df_sol.groupby("categorie")["note"].mean().to_dict()
            total = sum(means.values())
            data.append({
                "Solution": sol["solution"],
                "Utile": means.get("Utile", 0),
                "Utilisable": means.get("Utilisable", 0),
                "Utilisé": means.get("Utilisé", 0),
                "Total": total
            })
            details[sol["solution"]] = df_sol

    if data:
        df = pd.DataFrame(data)
        st.subheader("📑 Résumé des solutions")
        st.table(df)

        df["Size"] = df["Total"].apply(lambda x: x**4)

        # Graphe
        fig = px.scatter_ternary(
            df,
            a="Utile", b="Utilisable", c="Utilisé",
            size="Size", color="Solution",
            hover_name="Solution", size_max=75
        )
        fig.update_layout(
            height=850, font=dict(size=22),
            margin=dict(l=120, r=120, b=120, t=80),
            ternary=dict(
                aaxis=dict(showticklabels=False, showgrid=False),
                baxis=dict(showticklabels=False, showgrid=False),
                caxis=dict(showticklabels=False, showgrid=False)
            )
        )

        # --- Ajout des diagonales ---
        fig.add_trace(go.Scatterternary(
            a=[30, 15], b=[0, 15], c=[0, 15],
            mode="lines", line=dict(color="gray", dash="dot"), showlegend=False
        ))
        fig.add_trace(go.Scatterternary(
            a=[0, 15], b=[30, 15], c=[0, 15],
            mode="lines", line=dict(color="gray", dash="dot"), showlegend=False
        ))
        fig.add_trace(go.Scatterternary(
            a=[0, 15], b=[0, 15], c=[30, 15],
            mode="lines", line=dict(color="gray", dash="dot"), showlegend=False
        ))

        st.plotly_chart(fig, use_container_width=True)

        # --- Détail des notes par critère et par solution ---
        st.subheader("🔍 Détail des critères")

        all_rows = []
        for cat in ["Utile", "Utilisable", "Utilisé"]:
            for crit in scenario_data.get("criteres", {}).get(cat, []):
                row = {"Catégorie": cat, "Critère": crit}
                for sol_name, df_sol in details.items():
                    note = df_sol[(df_sol["categorie"] == cat) & (df_sol["critere"] == crit)]["note"]
                    row[sol_name] = int(note.values[0]) if not note.empty else "-"
                all_rows.append(row)

        df_details = pd.DataFrame(all_rows)
        st.table(df_details)

