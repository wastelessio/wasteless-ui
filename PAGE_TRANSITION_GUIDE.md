# Guide des Transitions de Page - Style Claude

Animation élégante de chargement avec apparition progressive des mots, comme la réflexion de Claude.

---

## 🎨 Aperçu Visuel

L'animation affiche une page blanche avec des mots qui apparaissent un par un:

```
[Page blanche]

        Loading  your  dashboard

        Wasteless
```

Chaque mot apparaît avec un léger délai, créant un effet fluide et professionnel.

---

## 🚀 Utilisation Simple

### Option 1: Transition Automatique (Recommandé)

Ajouter une ligne au début de votre page:

```python
import streamlit as st
from utils.page_transition import transition_on_first_load

st.set_page_config(
    page_title="Dashboard - Wasteless",
    page_icon="📊",
    layout="wide"
)

# Transition automatique au premier chargement
transition_on_first_load("Dashboard")

# Votre code de page normal
st.title("📊 Dashboard")
# ... reste du code
```

**Avantages:**
- ✅ S'affiche automatiquement au premier chargement
- ✅ Ne se répète pas ensuite (utilise session_state)
- ✅ Phrases adaptées au type de page

---

### Option 2: Phrases Personnalisées

Pour contrôler exactement ce qui s'affiche:

```python
from utils.page_transition import show_page_transition

# Définir vos phrases
custom_phrases = [
    ["Loading", "cost", "data"],
    ["Analyzing", "recommendations"],
    ["Preparing", "your", "dashboard"],
    ["Almost", "ready"]
]

# Afficher la transition
show_page_transition("Dashboard", custom_phrases)
```

---

### Option 3: Avec Progression

Pour synchroniser avec de vraies étapes de chargement:

```python
from utils.page_transition import transition_with_progress

# Définir les étapes
steps = [
    "Connecting to database",
    "Loading recommendations",
    "Rendering charts"
]

# Utiliser comme générateur
transition = transition_with_progress("Dashboard", steps)

# Étape 1
next(transition)
conn = get_db_connection()

# Étape 2
next(transition)
data = load_data()

# Étape 3
next(transition)
render_charts()
```

---

## 📋 Phrases par Défaut

Les phrases sont automatiquement adaptées selon la page:

### Dashboard
```
Loading  executive  dashboard
Fetching  cost  metrics
Analyzing  savings  data
Preparing  your  view
Almost  ready
```

### Recommendations
```
Loading  recommendations
Analyzing  idle  resources
Calculating  potential  savings
Preparing  your  view
Almost  ready
```

### History
```
Loading  action  history
Retrieving  audit  trail
Processing  events
Preparing  your  view
Almost  ready
```

### Settings
```
Loading  configuration
Checking  safeguards
Retrieving  settings
Preparing  your  view
Almost  ready
```

---

## 🎯 Exemple Complet - Dashboard

```python
#!/usr/bin/env python3
"""
Dashboard with elegant page transition
"""
import streamlit as st
from utils.sidebar import setup_sidebar
from utils.page_transition import transition_on_first_load

# Configuration
st.set_page_config(
    page_title="Dashboard - Wasteless.io",
    page_icon="static/images/favicon.svg",
    layout="wide"
)

# Show transition on first load only
transition_on_first_load("Dashboard")

# Page content
st.title("📊 Executive Dashboard")
st.markdown("Real-time cloud cost optimization metrics")
st.markdown("---")

# Setup sidebar
conn = setup_sidebar()
if not conn:
    st.error("❌ Cannot connect to database")
    st.stop()

# Rest of your dashboard code...
```

---

## 🎨 Personnalisation Avancée

### Changer le Style Visuel

Modifier les couleurs et le style dans `page_transition.py`:

```python
# Couleur du texte
color: #2d2d2d;  /* Noir doux */

# Taille de police
font-size: 1.5rem;  /* Augmenter ou diminuer */

# Vitesse d'animation
animation: wordAppear 0.4s;  /* Plus rapide: 0.2s, Plus lent: 0.6s */

# Délai entre les mots
delay = i * 0.12  # Plus rapide: 0.08, Plus lent: 0.20
```

### Créer des Thèmes

```python
# Thème sombre
st.markdown("""
<style>
.page-transition {
    background: #1a1a1a !important;
}
.transition-word {
    color: #ffffff !important;
}
</style>
""", unsafe_allow_html=True)
```

---

## 🔄 Variantes

### 1. Transition Rapide

Pour les pages qui chargent vite:

```python
from utils.page_transition import show_quick_transition

show_quick_transition("Loading")
# Votre code...
```

### 2. Transition Personnalisée Ultra-Simple

```python
custom_phrases = [
    ["Loading"],
    ["Ready"]
]

show_page_transition("Page", custom_phrases)
```

### 3. Transition avec Logo

Modifier pour inclure le logo:

```python
# Dans page_transition.py, ajouter avant transition-text:
<div class="logo-container">
    <img src="app/static/images/logo.svg"
         alt="Wasteless"
         style="width: 200px; opacity: 0.3; margin-bottom: 40px;">
</div>
```

---

## ⚡ Performance

### Timing Optimal

```python
# Nombre de phrases: 3-5
# Mots par phrase: 2-4
# Délai par mot: 0.12s
# Délai entre phrases: 0.8s

# Temps total: ~3-4 secondes
```

### Session State

L'animation utilise `st.session_state` pour éviter de se répéter:

```python
if 'page_loaded_Dashboard' not in st.session_state:
    show_page_transition("Dashboard")
    st.session_state.page_loaded_Dashboard = True
    st.rerun()
```

---

## 🎭 Différences avec l'Animation de Démarrage

| Caractéristique | Animation Démarrage | Transition Page |
|----------------|---------------------|-----------------|
| **Quand** | Premier lancement app | Chaque navigation |
| **Fond** | Gradient violet/bleu | Blanc minimaliste |
| **Style** | Plus stylé, logo | Épuré, texte seul |
| **Durée** | ~7 secondes | ~3 secondes |
| **Fichier** | `utils/loading_animation.py` | `utils/page_transition.py` |

---

## 🔧 Intégration Complète

Pour toutes les pages:

### 1. Modifier chaque page

```python
# pages/1_📊_Dashboard.py
from utils.page_transition import transition_on_first_load

st.set_page_config(...)
transition_on_first_load("Dashboard")
# reste du code...
```

### 2. Créer un wrapper

```python
# utils/page_wrapper.py
def setup_page(page_name, **config):
    """Setup page with transition and config"""
    st.set_page_config(**config)
    transition_on_first_load(page_name)

# Usage
from utils.page_wrapper import setup_page

setup_page("Dashboard",
    page_title="Dashboard - Wasteless",
    page_icon="📊",
    layout="wide"
)
```

---

## ✅ Checklist d'Intégration

- [ ] Copier `utils/page_transition.py`
- [ ] Ajouter `transition_on_first_load()` dans chaque page
- [ ] Tester sur chaque page
- [ ] Personnaliser les phrases si nécessaire
- [ ] Vérifier les performances (temps < 4s)

---

## 🎯 Résultat Final

L'utilisateur voit:

1. **Première visite** → Transition élégante avec mots progressifs
2. **Navigation suivante** → Page s'affiche directement (pas de répétition)
3. **Nouvelle session** → Transition à nouveau

**Expérience:** Professionnelle, fluide, style Claude ✨

---

*Développé pour Wasteless UI par Claude Sonnet 4.5*
