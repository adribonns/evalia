import streamlit as st
import os, json

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

st.title("📌 Création de scénario et solutions")

# --- Choix ou création d'un scénario ---
scenarios = [d for d in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, d))]
choix = st.selectbox("Choisir un scénario existant ou créer un nouveau :", ["➕ Nouveau scénario"] + scenarios)

if choix == "➕ Nouveau scénario":
    nom_scenario = st.text_input("Nom du scénario")
    description = st.text_area("Description du scénario")
    if st.button("Créer le scénario"):
        scen_dir = os.path.join(DATA_DIR, nom_scenario)
        os.makedirs(scen_dir, exist_ok=True)
        with open(os.path.join(scen_dir, "scenario.json"), "w") as f:
            json.dump({"nom": nom_scenario, "description": description, "criteres": {}}, f, indent=2)
        st.success(f"Scénario {nom_scenario} créé ✅")
else:
    scen_dir = os.path.join(DATA_DIR, choix)
    with open(os.path.join(scen_dir, "scenario.json")) as f:
        scenario_data = json.load(f)
    st.markdown(f"### {scenario_data['nom']}")
    st.markdown(scenario_data.get("description", ""))

    # --- Définir les critères ---
    st.subheader("⚙️ Définir les critères")
    criteres = {}
    for cat in ["Utile", "Utilisable", "Utilisé"]:
        with st.expander(f"Catégorie {cat}"):
            n = st.number_input(f"Nombre de critères pour {cat}", min_value=1, value=3, key=f"{cat}_nb")
            criteres[cat] = [st.text_input(f"Nom du critère {i+1} ({cat})", key=f"{cat}_{i}") for i in range(n)]

    if st.button("Sauvegarder critères"):
        scenario_data["criteres"] = criteres
        with open(os.path.join(scen_dir, "scenario.json"), "w") as f:
            json.dump(scenario_data, f, indent=2)
        st.success("Critères sauvegardés ✅")

    # --- Ajouter une solution ---
    st.subheader("📝 Ajouter une solution")
    nom_solution = st.text_input("Nom de la solution")
    notes = []
    if "criteres" in scenario_data:
        for cat, crits in scenario_data["criteres"].items():
            st.markdown(f"**{cat}**")
            for crit in crits:
                val = st.slider(f"{crit}", 0, 10, 5, key=f"{nom_solution}_{crit}")
                notes.append({"categorie": cat, "critere": crit, "note": val})

    if st.button("Sauvegarder la solution"):
        sol_data = {"solution": nom_solution, "criteres": notes}
        with open(os.path.join(scen_dir, f"{nom_solution}.json"), "w") as f:
            json.dump(sol_data, f, indent=2)
        st.success(f"Solution {nom_solution} ajoutée ✅")

