# Guide des Indicateurs de Chargement - Wasteless UI

Ce guide explique comment détecter et afficher l'état de chargement des pages dans Streamlit.

---

## 🎯 Méthodes Disponibles

### 1. **Context Manager de Chargement** (Recommandé)

Encadre le chargement complet d'une page avec un indicateur:

```python
from utils.page_loader import page_loading_state

with page_loading_state("Dashboard"):
    # Tout votre code de page ici
    conn = get_db_connection()
    data = load_data()
    render_charts()
```

**Avantages:**
- ✅ Indicateur automatique pendant le chargement
- ✅ Suppression automatique quand terminé
- ✅ Gestion d'erreurs intégrée

---

### 2. **Barre de Progression Multi-Étapes**

Pour des chargements complexes avec plusieurs étapes:

```python
from utils.page_loader import track_loading_progress

# Définir les étapes
update_progress = track_loading_progress([
    "Connexion à la base de données",
    "Chargement des recommandations",
    "Génération des graphiques",
    "Calcul des métriques"
])

# Mettre à jour au fur et à mesure
update_progress(0)  # Étape 1
conn = get_db_connection()

update_progress(1)  # Étape 2
recs = load_recommendations()

update_progress(2)  # Étape 3
charts = generate_charts()

update_progress(3)  # Étape 4 - Terminé!
```

**Affichage:**
```
████████░░ 75%
⏳ Génération des graphiques...
```

---

### 3. **Spinner Simple**

Pour des opérations rapides:

```python
from utils.page_loader import show_loading_spinner

spinner = show_loading_spinner("Chargement des données...")

# Faire le travail
data = fetch_data()

# Terminer le chargement
spinner.empty()
```

---

### 4. **Chargement par Section**

Pour charger différentes parties de la page séparément:

```python
from utils.page_loader import loading_section

st.title("Dashboard")

# Section 1
with loading_section("KPIs"):
    render_kpis()

# Section 2
with loading_section("Charts"):
    render_charts()

# Section 3
with loading_section("Table"):
    render_table()
```

---

### 5. **Vérification de l'État de Chargement**

Pour vérifier si la page est complètement chargée:

```python
from utils.page_loader import check_page_ready

# Vérifier les prérequis
if not check_page_ready({
    "database": conn,
    "data": df,
    "config": config
}):
    st.stop()  # Arrête le rendu si incomplet

# Continuer si tout est OK
st.success("✅ Page chargée à 100%")
```

---

### 6. **Temps de Chargement**

Pour afficher le temps de chargement de la page:

```python
from utils.page_loader import add_page_load_time
import time

# Au début de la page
if 'page_load_start' not in st.session_state:
    st.session_state.page_load_start = time.time()

# Votre code de page...

# À la fin de la page
add_page_load_time()
```

**Affichage dans la sidebar:**
```
⏱️ Page loaded in 0.45s
```

---

## 📋 Exemple Complet - Dashboard

Voici comment intégrer les indicateurs dans le Dashboard:

```python
#!/usr/bin/env python3
import streamlit as st
import time
from utils.sidebar import setup_sidebar
from utils.page_loader import (
    page_loading_state,
    track_loading_progress,
    check_page_ready,
    add_page_load_time
)

# Configuration
st.set_page_config(
    page_title="Dashboard - Wasteless.io",
    page_icon="static/images/favicon.svg",
    layout="wide"
)

# Démarrer le chronomètre
if 'page_load_start' not in st.session_state:
    st.session_state.page_load_start = time.time()

# Chargement complet de la page
with page_loading_state("Dashboard"):

    st.title("📊 Executive Dashboard")

    # Setup sidebar
    conn = setup_sidebar()

    # Vérifier les prérequis
    if not check_page_ready({"database": conn}):
        st.error("❌ Cannot load page - database not available")
        st.stop()

    # Progress tracking pour les données
    update_progress = track_loading_progress([
        "Loading KPIs",
        "Loading charts data",
        "Rendering visualizations"
    ])

    # Étape 1: KPIs
    update_progress(0)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM recommendations")
    total_recs = cursor.fetchone()[0]

    # Étape 2: Données des charts
    update_progress(1)
    cursor.execute("SELECT * FROM actions_log LIMIT 100")
    actions = cursor.fetchall()

    # Étape 3: Rendu
    update_progress(2)
    st.metric("Total Recommendations", total_recs)
    st.bar_chart(data)

    # Terminer le suivi
    update_progress(3)

# Afficher le temps de chargement
add_page_load_time()
```

---

## 🎨 Détection Native Streamlit

Streamlit a aussi des méthodes natives:

### Spinner Built-in
```python
with st.spinner("Loading data..."):
    time.sleep(2)
    data = load_data()
```

### Status Container
```python
with st.status("Downloading data...", expanded=True) as status:
    st.write("Searching for data...")
    time.sleep(2)
    st.write("Found data!")
    time.sleep(1)
    status.update(label="Download complete!", state="complete", expanded=False)
```

### Progress Bar
```python
progress_bar = st.progress(0)
for percent_complete in range(100):
    time.sleep(0.01)
    progress_bar.progress(percent_complete + 1)
```

---

## 🚀 Détection Côté Client (JavaScript)

Pour détecter le chargement côté navigateur:

```python
st.markdown("""
<script>
// Détecte quand Streamlit a fini de charger
window.addEventListener('load', function() {
    console.log('Page loaded at:', new Date().toISOString());

    // Envoyer un événement à Streamlit
    window.parent.postMessage({
        type: 'streamlit:pageLoaded',
        timestamp: Date.now()
    }, '*');
});

// Détecter les mises à jour Streamlit
const observer = new MutationObserver(function(mutations) {
    console.log('Streamlit updated content');
});

observer.observe(document.body, {
    childList: true,
    subtree: true
});
</script>
""", unsafe_allow_html=True)
```

---

## 📊 Métriques de Performance

Pour monitorer les performances de chargement:

```python
import time
from functools import wraps

def measure_load_time(section_name):
    """Decorator pour mesurer le temps de chargement"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            elapsed = time.time() - start

            # Logger ou afficher
            st.sidebar.caption(f"⏱️ {section_name}: {elapsed:.2f}s")

            return result
        return wrapper
    return decorator

# Usage
@measure_load_time("Load KPIs")
def load_kpis():
    # Code de chargement
    return data
```

---

## ✅ Meilleures Pratiques

1. **Toujours montrer un feedback** pour opérations > 200ms
2. **Utiliser des barres de progression** pour opérations longues (>3s)
3. **Afficher des messages spécifiques** plutôt que généri ques
4. **Vérifier les prérequis** avant de charger la page
5. **Mesurer les temps de chargement** en développement

---

## 🎯 Choix Rapide

| Situation | Méthode Recommandée |
|-----------|---------------------|
| Chargement page complète | `page_loading_state()` |
| Plusieurs étapes | `track_loading_progress()` |
| Opération simple | `st.spinner()` (natif) |
| Section spécifique | `loading_section()` |
| Vérifier l'état | `check_page_ready()` |
| Monitoring | `add_page_load_time()` |

---

*Développé pour Wasteless UI par Claude Sonnet 4.5*
