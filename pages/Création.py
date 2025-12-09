import streamlit as st
import os, json

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)
st.set_page_config(page_title="Eval-IA", layout="wide")
st.title("📌 Création de projets et solutions")

# --- Choix ou création d'un projet ---
projets = [d for d in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, d))]
choix = st.selectbox("Choisir un projet existant ou créer un nouveau :", ["➕ Nouveau projet"] + projets)

if choix == "➕ Nouveau projet":
    nom_projet = st.text_input("Nom du projet")
    description = st.text_area("Description du projet")
    if st.button("Créer le projet"):
        scen_dir = os.path.join(DATA_DIR, nom_projet)
        os.makedirs(scen_dir, exist_ok=True)
        with open(os.path.join(scen_dir, "projet.json"), "w") as f:
            json.dump({"nom": nom_projet, "description": description, "criteres": {}}, f, indent=2)
        st.success(f"Scénario {nom_projet} créé ✅")
else:
    projet_dir = os.path.join(DATA_DIR, choix)
    with open(os.path.join(projet_dir, "projet.json")) as f:
        projet_data = json.load(f)
    st.markdown(f"### {projet_data['nom']}")
    st.markdown(projet_data.get("description", ""))

    # --- Définir les critères ---
    st.subheader("⚙️ Définir les critères")
    criteres = {}
    for cat in ["Utile", "Utilisable", "Utilisé"]:
        with st.expander(f"Catégorie {cat}"):
            n = st.number_input(f"Nombre de critères pour {cat}", min_value=1, value=3, key=f"{cat}_nb")
            criteres[cat] = [st.text_input(f"Nom du critère {i+1} ({cat})", key=f"{cat}_{i}") for i in range(n)]

    if st.button("Sauvegarder critères"):
        projet_data["criteres"] = criteres
        with open(os.path.join(projet_dir, "projet.json"), "w") as f:
            json.dump(projet_data, f, indent=2)
        st.success("Critères sauvegardés ✅")

    # --- Ajouter une solution ---
    st.subheader("📝 Ajouter une solution")
    nom_solution = st.text_input("Nom de la solution")
    notes = []
    if "criteres" in projet_data:
        for cat, crits in projet_data["criteres"].items():
            st.markdown(f"**{cat}**")
            for crit in crits:
                val = st.slider(f"{crit}", 0, 10, 5, key=f"{nom_solution}_{crit}")
                notes.append({"categorie": cat, "critere": crit, "note": val})

    if st.button("Sauvegarder la solution"):
        sol_data = {"solution": nom_solution, "criteres": notes}
        with open(os.path.join(projet_dir, f"{nom_solution}.json"), "w") as f:
            json.dump(sol_data, f, indent=2)
        st.success(f"Solution {nom_solution} ajoutée ✅")

