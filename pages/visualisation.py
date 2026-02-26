import streamlit as st
import os, json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

DATA_DIR = "data"
st.set_page_config(page_title="Eval-IA", layout="wide")
st.title("📊 Visualisation des projets")

if not os.path.exists(DATA_DIR) or not os.listdir(DATA_DIR):
    st.warning("Aucun projet trouvé.")
else:
    projet = st.selectbox("Choisir un projet", os.listdir(DATA_DIR))
    projet_dir = os.path.join(DATA_DIR, projet)

    # Charger description
    with open(os.path.join(projet_dir, "projet.json")) as f:
        projet_data = json.load(f)
    st.markdown(f"## {projet_data['nom']}")
    st.markdown(projet_data.get("description", ""))

    # Charger solutions
    data = []
    details = {}
    for file in os.listdir(projet_dir):
        if file.endswith(".json") and file != "projet.json":
            with open(os.path.join(projet_dir, file)) as f:
                sol = json.load(f)
            df_sol = pd.DataFrame(sol["criteres"])
            means = df_sol.groupby("categorie")["note"].mean().to_dict()
            total = sum(means.values())
            
            # Calcul de l'équilibre (distance au centre du triangle)
            utile = means.get("Utile", 0)
            utilisable = means.get("Utilisable", 0)
            utilise = means.get("Utilisé", 0)
            # Le centre du triangle est à (total/3, total/3, total/3)
            centre = total / 3
            distance = ((utile - centre)**2 + (utilisable - centre)**2 + (utilise - centre)**2)**0.5
            # Distance maximale du centre à un coin (ex: (10,0,0) au centre (10/3,10/3,10/3))
            # Pour un point avec scores sur 10: distance_max = sqrt(3) * (2*10/3) = 10*sqrt(3)/sqrt(3) * 2/sqrt(3) = 20/sqrt(3)
            distance_max = (2 * total / 3) * (3**0.5) / (3**0.5) * (3**0.5)  # = 2*total/sqrt(3)
            distance_max = 2 * total / (3**0.5)
            # Normaliser entre 0 et 10, en inversant (10 = centre, 0 = coins)
            equilibre = 10 * (1 - distance / distance_max)
            
            data.append({
                "Solution": sol["solution"],
                "Utile": means.get("Utile", 0),
                "Utilisable": means.get("Utilisable", 0),
                "Utilisé": means.get("Utilisé", 0),
                "Perfo": total/3,
                "Equilibre": round(equilibre, 2)
            })
            details[sol["solution"]] = df_sol

    if data:
        df = pd.DataFrame(data)
        st.subheader("📑 Résumé des solutions")
        
        # Descriptions des colonnes
        col_descriptions = {
            "Solution": "Nom de la solution à évaluer",
            "Utile": "Score moyen sur 10 pour les critères 'Utile'",
            "Utilisable": "Score moyen sur 10 pour les critères d'utilisabilité",
            "Utilisé": "Score moyen sur 10 pour les critères d'adoption",
            "Perfo": "Performance globale (moyenne des trois scores)",
            "Equilibre": "Équilibre entre les trois dimensions (10 = parfaitement équilibré, 0 = très déséquilibré)"
        }
        
        # Afficher les descriptions
        with st.expander("ℹ️ Description des colonnes"):
            for col, desc in col_descriptions.items():
                st.markdown(f"**{col}** : {desc}")
        
        # Fonction pour appliquer le gradient de couleur en fonction de la note
        def color_gradient_summary(val):
            try:
                note = float(val)
                # Gradient plus doux et moins saturé (même que pour la table détail)
                # Rouge clair : rgb(255, 200, 200) pour note 0
                # Jaune clair : rgb(255, 245, 200) pour note 5
                # Vert clair : rgb(200, 255, 200) pour note 10
                if note <= 5:
                    # Interpolation rouge clair -> jaune clair
                    ratio = note / 5
                    r = 255
                    g = int(200 + (245 - 200) * ratio)
                    b = int(200 + (200 - 200) * ratio)
                else:
                    # Interpolation jaune clair -> vert clair
                    ratio = (note - 5) / 5
                    r = int(255 - (255 - 200) * ratio)
                    g = int(245 + (255 - 245) * ratio)
                    b = int(200 + (200 - 200) * ratio)
                
                # Texte en noir pour une bonne lisibilité
                text_color = '#333333'
                return f'background-color: rgb({r}, {g}, {b}); color: {text_color}; text-align: center; font-weight: 500;'
            except:
                return ''
        
        # Appliquer le style aux colonnes numériques (scores)
        styled_df_summary = df.style.applymap(
            color_gradient_summary,
            subset=["Utile", "Utilisable", "Utilisé", "Perfo", "Equilibre"]
        )
        
        st.dataframe(styled_df_summary, use_container_width=True, hide_index=True)

        df["Size"] = df["Perfo"].apply(lambda x: x**5)

        # # Créer deux colonnes pour la visualisation
        # col1, col2 = st.columns([1, 1])
        
        # with col1:
        st.subheader("🔼 Visualisation des projets/solutions")
        # Graphe triangle
        fig = px.scatter_ternary(
            df,
            a="Utile", b="Utilisable", c="Utilisé",
            size="Size", color="Solution",
            hover_name="Solution", size_max=75,
            custom_data=["Utile", "Utilisable", "Utilisé", "Perfo", "Equilibre"]
        )
        
        # Personnaliser le hover template et la couleur du tooltip pour chaque trace
        for i, trace in enumerate(fig.data):
            if hasattr(trace, 'marker') and hasattr(trace.marker, 'color'):
                # Récupérer la couleur du point
                color = trace.marker.color
                trace.update(
                    hovertemplate="<b>%{hovertext}</b><br>" +
                                 "Utile: %{customdata[0]:.2f}<br>" +
                                 "Utilisable: %{customdata[1]:.2f}<br>" +
                                 "Utilisé: %{customdata[2]:.2f}<br>" +
                                 "Perfo: %{customdata[3]:.2f}<br>" +
                                 "Equilibre: %{customdata[4]:.2f}<br>" +
                                 "<extra></extra>",
                    hoverlabel=dict(
                        bgcolor=color,  # Couleur de fond du tooltip = couleur du cercle
                        font_size=16,
                        font_color="white"  # Texte en blanc pour contraster
                    )
                )
        
        # Extraire les couleurs du graphique ternaire
        color_map = {}
        for trace in fig.data:
            if hasattr(trace, 'name') and trace.name:
                color_map[trace.name] = trace.marker.color
        
        fig.update_layout(
            height=650, font=dict(size=18),
            margin=dict(l=80, r=80, b=80, t=40),
            ternary=dict(
                aaxis=dict(showticklabels=False, showgrid=False),
                baxis=dict(showticklabels=False, showgrid=False),
                caxis=dict(showticklabels=False, showgrid=False)
            ),
            legend=dict(
                font=dict(size=16),  # Taille de police de la légende
                itemsizing='constant'
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
        
        # with col2:
        #     st.subheader("⚠️ Critères à risque (note < 5)")
            
        #     # Pour chaque critère, collecter toutes les notes
        #     all_criteria = []
        #     for sol_name, df_sol in details.items():
        #         for _, row in df_sol.iterrows():
        #             all_criteria.append({
        #                 'Solution': sol_name,
        #                 'Critère': row['critere'],
        #                 'Catégorie': row['categorie'],
        #                 'Note': row['note']
        #             })
            
        #     df_all = pd.DataFrame(all_criteria)
            
        #     # Filtrer les critères où au moins une solution a une note < 5
        #     criteres_faibles = df_all[df_all['Note'] < 5]['Critère'].unique()
            
        #     if len(criteres_faibles) > 0:
        #         # Calculer la moyenne par critère pour trier
        #         critere_means = df_all[df_all['Critère'].isin(criteres_faibles)].groupby('Critère')['Note'].mean().sort_values()
                
        #         # Prendre les critères triés par moyenne croissante
        #         top_weak_criteria = critere_means.index.tolist()
                
        #         # Filtrer pour ces critères seulement
        #         df_risk = df_all[df_all['Critère'].isin(top_weak_criteria)]
                
        #         # Créer un graphique à barres horizontal groupé par critère
        #         fig2 = go.Figure()
                
        #         for sol in df['Solution'].unique():
        #             df_sol_risk = df_risk[df_risk['Solution'] == sol].copy()
        #             # Trier par critère pour avoir le même ordre
        #             df_sol_risk = df_sol_risk.set_index('Critère').reindex(top_weak_criteria).reset_index()
                    
        #             fig2.add_trace(go.Bar(
        #                 name=sol,
        #                 y=[f"{crit[:35]}..." if len(crit) > 35 else crit 
        #                    for crit in df_sol_risk['Critère']],
        #                 x=df_sol_risk['Note'],
        #                 orientation='h',
        #                 marker=dict(color=color_map.get(sol, '#636EFA')),
        #                 text=df_sol_risk['Note'].round(1),
        #                 textposition='auto',
        #             ))
                
        #         fig2.update_layout(
        #             height=650,
        #             barmode='group',
        #             xaxis_title="Note",
        #             yaxis_title="",
        #             font=dict(size=11),
        #             margin=dict(l=20, r=20, b=40, t=40),
        #             showlegend=True,
        #             legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        #             xaxis=dict(range=[0, 10])
        #         )
                
        #         st.plotly_chart(fig2, use_container_width=True)
        #     else:
        #         st.info("Aucun critère avec une note inférieure à 5 ✅")

        # --- Détail des notes par critère et par solution ---
        st.subheader("🔍 Détail des critères")

        all_rows = []
        for cat in ["Utile", "Utilisable", "Utilisé"]:
            for crit in projet_data.get("criteres", {}).get(cat, []):
                row = {"Catégorie": cat, "Critère": crit}
                for sol_name, df_sol in details.items():
                    note = df_sol[(df_sol["categorie"] == cat) & (df_sol["critere"] == crit)]["note"]
                    row[sol_name] = int(note.values[0]) if not note.empty else "-"
                all_rows.append(row)

        df_details = pd.DataFrame(all_rows)
        
        # Fonction pour appliquer le gradient de couleur en fonction de la note
        def color_gradient(val):
            if val == "-" or pd.isna(val):
                return 'background-color: #f5f5f5; text-align: center; font-weight: 500; font-size: 1.1em;'
            try:
                note = float(val)
                # Gradient plus doux et moins saturé
                # Rouge clair : rgb(255, 200, 200) pour note 0
                # Jaune clair : rgb(255, 245, 200) pour note 5
                # Vert clair : rgb(200, 255, 200) pour note 10
                if note <= 5:
                    # Interpolation rouge clair -> jaune clair
                    ratio = note / 5
                    r = 255
                    g = int(200 + (245 - 200) * ratio)
                    b = int(200 + (200 - 200) * ratio)
                else:
                    # Interpolation jaune clair -> vert clair
                    ratio = (note - 5) / 5
                    r = int(255 - (255 - 200) * ratio)
                    g = int(245 + (255 - 245) * ratio)
                    b = int(200 + (200 - 200) * ratio)
                
                # Texte en noir pour une bonne lisibilité
                text_color = '#333333'
                return f'background-color: rgb({r}, {g}, {b}); color: {text_color}; text-align: center; font-weight: 500; font-size: 1.1em;'
            except:
                return 'text-align: center; font-weight: 500; font-size: 1.1em;'
        
        # Appliquer le style uniquement aux colonnes de solutions
        solution_cols = [col for col in df_details.columns if col not in ["Catégorie", "Critère"]]
        
        styled_df = df_details.style.applymap(
            color_gradient,
            subset=solution_cols
        )
        
        # Calculer la hauteur nécessaire : environ 35px par ligne + 38px pour l'en-tête
        table_height = len(df_details) * 35 + 38
        
        # Configuration des colonnes
        column_config = {
            "Catégorie": st.column_config.TextColumn("Catégorie", width="medium"),
            "Critère": st.column_config.TextColumn("Critère", width="large"),
        }
        
        for sol_name in details.keys():
            column_config[sol_name] = st.column_config.Column(
                sol_name,
                width="medium",
                help=f"Note pour {sol_name}"
            )
        
        st.dataframe(
            styled_df, 
            use_container_width=True, 
            hide_index=True, 
            height=table_height,
            column_config=column_config
        )

