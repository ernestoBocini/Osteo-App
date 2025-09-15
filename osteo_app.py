import streamlit as st
import random
import json
import os
import pickle
from typing import Dict, List, Tuple
from pathlib import Path

# File to store persistent statistics
STATS_FILE = "osteology_stats.pkl"

# Anatomical data extracted from the PDF
ANATOMICAL_DATA = {
    "Scapula": {
        "title": "Scapula gauche de cheval",
        "views": ["Médiale", "Latérale"],
        "image_files": ["scapula_mediale.png", "scapula_laterale.png"],
        "components": {
            1: "Cartilage scapulaire",
            2: "Bord dorsal ou vertébral", 
            3: "Angle crânial",
            4: "Angle caudal",
            5: "Fosse supra-épineuse",
            6: "Fosse infra-épineuse",
            7: "Tubérosité de l'épine scapulaire",
            8: "Bord caudal ou axillaire",
            9: "Bord crânial ou cervical",
            10: "Empreintes d'insertions",
            11: "Epine scapulaire",
            12: "Incisure scapulaire",
            13: "Foramen vasculaire",
            14: "Col de la scapula",
            15: "Empreinte vasculaire",
            16: "Angle ventral ou articulaire",
            17: "Tubérosité supra-glénoïdal",
            18: "Cavité glénoïdale",
            19: "Surface dentelée caudale",
            20: "Surface dentelée crâniale",
            21: "Fosse subscapulaire",
            22: "Sillons vasculaires",
            23: "Tubercule infra-glénoïdal",
            24: "Processus coracoïde"
        }
    },
    "Humérus": {
        "title": "Humérus gauche de cheval",
        "views": ["Crâniale", "Latérale", "Caudale", "Médiale"],
        "image_files": ["humerus_craniale.png", "humerus_laterale.png", "humerus_caudale.png", "humerus_mediale.png"],
        "components": {
            1: "Tubercule mineur",
            2: "Sillon intertuberculaire",
            3: "Tubercule majeur",
            4: "Foramens vasculaires",
            5: "Face crâniale",
            6: "Tubérosité deltoïdienne",
            7: "Tubérosité du grand rond",
            8: "Crête humérale",
            9: "Face médiale",
            10: "Face latérale : sillon brachial",
            11: "Crête épicondylaire",
            12: "Fosse coronoïdienne",
            13: "Fosse radiale",
            14: "Capitulum",
            15: "Lèvre médiale",
            16: "Fossette synoviale",
            17: "Lèvre latérale",
            18: "Tête articulaire",
            19: "Ligne tricipitale",
            20: "Tubérosité du petit rond",
            21: "Face caudale",
            22: "Crête humérale",
            23: "Trochlée humérale",
            24: "Epicondyle latéral",
            25: "Fosse olécrânienne",
            26: "Epicondyle médial",
            27: "Col",
            28: "Sillon brachial",
            29: "Foramen nourricier",
            30: "Capitulum"
        }
    },
    "Radius et Ulna": {
        "title": "Radius et ulna gauches de cheval",
        "views": ["Dorsale", "Latérale", "Palmaire", "Médiale"],
        "image_files": ["radius_ulna_dorsale.png", "radius_ulna_laterale.png", "radius_ulna_palmaire.png", "radius_ulna_mediale.png"],
        "components": {
            1: "Tubérosité de l'olécrâne",
            2: "Bord crânial de l'olécrâne",
            3: "Processus anconé",
            4: "Incisure trochléaire",
            5: "Fossette synoviale",
            6: "Processus coronoïde",
            7: "Relief latéral d'insertion",
            8: "Tubérosité du radius",
            9: "Col du radius",
            10: "Bord caudal de l'olécrâne",
            11: "Espace interosseux",
            12: "Sillon tendineux",
            13: "Corps de l'ulna",
            14: "Bord latéral du radius",
            15: "Face dorsale du radius",
            16: "Face palmaire du radius",
            17: "Sillon pour l'ext. oblique du carpe",
            18: "Sillon pour l'ext. radial du carpe",
            19: "Sillon pour l'ext. dorsal du doigt",
            20: "Sillon pour l'ext. latéral du doigt",
            21: "Surface articulaire pour le carpe",
            22: "Rudiment de proc. styloïde radial",
            23: "Crête transverse",
            24: "Rudiment de proc. ulnaire"
        }
    },
    "Carpe": {
        "title": "Carpe gauche de cheval",
        "views": ["Dorsale", "Latérale", "Médiale", "Dorsale (os disjoints)"],
        "image_files": ["carpe_dorsale.png", "carpe_laterale.png", "carpe_mediale.png", "carpe_dorsale_disjoints.png"],
        "components": {
            1: "Radius (extrémité distale)",
            2: "Sillon pour l'ext. radial carpe",
            3: "Sillon pour l'ext. dorsal du doigt",
            4: "Sillon pour l'ext. oblique du carpe",
            5: "Os scaphoïde",
            6: "Os pyramidal",
            7: "Os lunatum",
            8: "Os capitatum",
            9: "Os trapézoïde",
            10: "Os hamatum",
            11: "Tubérosité dorso-médiale",
            12: "Métacarpien IV",
            13: "Métacarpien II",
            14: "Métacarpien principal (III)",
            15: "Sillon pour l'ext. latéral du doigt",
            16: "Crête transverse",
            17: "Sillon pour le tendon long du m. ulnaire latérale",
            18: "Os pisiforme",
            19: "Facette articulaire répondant au radius",
            20: "Facette articulaire pour l'os pyramidal"
        }
    },
    "Métacarpe": {
        "title": "Métacarpe gauche de cheval",
        "views": ["Dorsale", "Latérale", "Palmaire (os disjoints)"],
        "image_files": ["metacarpe_dorsale.png", "metacarpe_laterale.png", "metacarpe_palmaire.png"],
        "components": {
            1: "Tubérosité dorso-médiale",
            2: "Métacarpien IV",
            3: "Métacarpien II",
            4: "Métacarpien principal (III)",
            5: "Bord médial du métacarpien principal (III)",
            6: "Bord latéral du métacarpien principal (III)",
            7: "Fossette d'insertion ligamenteuse",
            8: "Condyle latéral",
            9: "Condyle médiale",
            10: "Relief intermédiaire",
            11: "Surface articulaire proximale",
            12: "Bouton terminal de l'os métacarpien IV",
            13: "Surface articulaire pour l'os hamatum",
            14: "Surface articulaire pour l'os capitatum",
            15: "Surface articulaire pour l'os trapézoïde",
            16: "Surfaces articulaires intermétacarpiennes (IV et III)",
            17: "Surfaces articulaires intermétacarpiennes (II et III)",
            18: "Empreinte d'insertion du m. interosseux",
            19: "Surface de syndesmose intermétacarpienne",
            20: "Foramen nourricier",
            21: "Face palmaire",
            22: "Bord médial",
            23: "Bouton terminal"
        }
    },
    "Phalanges": {
        "title": "Os du doigt de cheval",
        "views": ["Latérale", "Proximale", "Dorsale", "Distale"],
        "image_files": ["phalanges_laterale.png", "phalanges_proximale.png", "phalanges_dorsale.png", "phalanges_distale.png"],
        "components": {
            1: "Métacarpien principal (III)",
            2: "Phalange proximale",
            3: "Os grands sésamoïdes",
            4: "Phalange moyenne",
            5: "Processus extensorius",
            6: "Phalange distale",
            7: "Processus basilaire",
            8: "Incisure du processus palmaire",
            9: "Processus rétrossal",
            10: "Processus extensorius",
            11: "Bord coronaire",
            12: "Face dorsale ou pariétale",
            13: "Surface articulaire",
            14: "Os naviculaire ou petit sésamoïde",
            15: "Incisure du processus palmaire",
            16: "Processus basilaire",
            17: "Empreinte d'insertion ligamenteuse",
            18: "Foramens vasculaires",
            19: "Processus rétrossal",
            20: "Bord solaire",
            21: "Sillon pariétal",
            22: "Cavité glénoïdale (glène) latérale",
            23: "Echancrure médiane du bord solaire",
            24: "Cavité glénoïdale (glène) médiale",
            25: "Processus palmaire"
        }
    },
    "Vertèbres Cervicales": {
        "title": "Vertèbres cervicales de cheval",
        "views": ["Latérale", "Dorsale", "Ventrale"],
        "image_files": ["vertebres_cervicales_laterale.png", "vertebres_cervicales_dorsale.png", "vertebres_cervicales_ventrale.png"],
        "components": {
            1: "Processus épineux",
            2: "Processus articulaire crânial",
            3: "Processus articulaire caudal",
            4: "Incisure vertébrale crâniale",
            5: "Incisure vertébrale caudale",
            6: "Foramen transversaire",
            7: "Tubercule dorsal du processus transverse",
            8: "Tête de la vertèbre",
            9: "Processus transverse",
            10: "Tubercule ventral",
            11: "Dent de l'axis",
            12: "Fosse de la vertèbre"
        }
    },
    "Fémur": {
        "title": "Fémur de cheval",
        "views": ["Crâniale", "Caudale", "Médiale", "Latérale"],
        "image_files": ["femur_craniale.png", "femur_caudale.png", "femur_mediale.png", "femur_laterale.png"],
        "components": {
            1: "Sommet du grand trochanter",
            2: "Convexité du grand trochanter",
            3: "Incisure trochantérique",
            4: "Tête du fémur",
            5: "Col du fémur",
            6: "Crête du grand trochanter",
            7: "Fovea capitis",
            8: "Crête intertrochantérique",
            9: "Troisième trochanter",
            10: "Petit trochanter",
            11: "Face médiale",
            12: "Bord crânial",
            13: "Face latérale",
            14: "Empreinte des vaisseaux fémoraux",
            15: "Tubérosité supracondylaire",
            16: "Foramen nourricier",
            17: "Tubérosité de la trochlée",
            18: "Epicondyle médial",
            19: "Epicondyle latéral",
            20: "Condyle médial",
            21: "Lèvre médiale de la trochlée",
            22: "Condyle latéral",
            23: "Lèvre latérale de la trochlée",
            24: "Gorge de la trochlée",
            25: "Fossette du m. poplité",
            26: "Fosse intercondylaire"
        }
    },
    "Tibia et Fibula": {
        "title": "Tibia et fibula gauches de cheval",
        "views": ["Crâniale", "Caudale", "Latérale", "Médiale"],
        "image_files": ["tibia_fibula_craniale.png", "tibia_fibula_caudale.png", "tibia_fibula_laterale.png", "tibia_fibula_mediale.png"],
        "components": {
            1: "Condyle médial",
            2: "Eminence intercondylaire",
            3: "Condyle latéral",
            4: "Tubérosité du tibia",
            5: "Sillon de la tubérosité",
            6: "Sillon de l'extenseur",
            7: "Fosse du tibia",
            8: "Fibula",
            9: "Crête du tibia",
            10: "Espace interosseux",
            11: "Face médiale",
            12: "Face latérale",
            13: "Bord crânial",
            14: "Face caudale",
            15: "Malléole médiale",
            16: "Malléole latérale",
            17: "Surface articulaire distale (cochlée tibiale)"
        }
    }
}

def load_persistent_stats():
    """Load statistics from file."""
    try:
        if os.path.exists(STATS_FILE):
            with open(STATS_FILE, 'rb') as f:
                stats = pickle.load(f)
            return stats
        else:
            return {
                'total_score': 0,
                'total_questions': 0,
                'best_streak': 0,
                'sessions_played': 0,
                'last_celebration_streak': 0
            }
    except:
        return {
            'total_score': 0,
            'total_questions': 0,
            'best_streak': 0,
            'sessions_played': 0,
            'last_celebration_streak': 0
        }

def save_persistent_stats():
    """Save statistics to file."""
    try:
        stats = {
            'total_score': st.session_state.get('persistent_total_score', 0),
            'total_questions': st.session_state.get('persistent_total_questions', 0),
            'best_streak': st.session_state.get('persistent_best_streak', 0),
            'sessions_played': st.session_state.get('persistent_sessions_played', 0),
            'last_celebration_streak': st.session_state.get('last_celebration_streak', 0)
        }
        with open(STATS_FILE, 'wb') as f:
            pickle.dump(stats, f)
    except:
        pass  # Fail silently if can't save

def show_celebration_message():
    """Show Ernesto's celebration message as a dramatic full-screen overlay."""
    # Create a dramatic full-screen celebration
    st.markdown("""
    <style>
    @keyframes celebration-fade-in {
        0% { 
            opacity: 0; 
            transform: scale(0.5); 
        }
        100% { 
            opacity: 1; 
            transform: scale(1); 
        }
    }
    
    .celebration-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        z-index: 9999;
        animation: celebration-fade-in 0.8s ease-out;
        color: white;
        text-align: center;
        padding: 20px;
        box-sizing: border-box;
    }
    
    .celebration-title {
        font-size: 4rem;
        font-weight: bold;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        animation: celebration-fade-in 1.2s ease-out;
    }
    
    .celebration-message {
        font-size: 2rem;
        margin-bottom: 2rem;
        max-width: 800px;
        line-height: 1.4;
        animation: celebration-fade-in 1.6s ease-out;
    }
    
    .celebration-signature {
        font-size: 1.5rem;
        font-style: italic;
        animation: celebration-fade-in 2s ease-out;
    }
    
    .celebration-emojis {
        font-size: 3rem;
        margin: 1rem 0;
        animation: celebration-fade-in 1.4s ease-out;
    }
    </style>
    
    <div class="celebration-overlay">
        <div class="celebration-title">🎉 FANTÁSTICO! 🎉</div>
        <div class="celebration-emojis">✨ 🌟 ⭐ 🌟 ✨</div>
        <div class="celebration-message">
            Wow Caro! You're going great!<br>
            Keep pushing ❤️
        </div>
        <div class="celebration-signature">
            Yours Ernesto
        </div>
        <div class="celebration-emojis">🐎 📚 💪</div>
    </div>
    
    <script>
    // Auto-hide the celebration after 4 seconds
    setTimeout(function() {
        const overlay = document.querySelector('.celebration-overlay');
        if (overlay) {
            overlay.style.transition = 'opacity 1s ease-out';
            overlay.style.opacity = '0';
            setTimeout(function() {
                overlay.remove();
            }, 1000);
        }
    }, 4000);
    </script>
    """, unsafe_allow_html=True)
    
    # Also trigger balloons
    st.balloons()

def initialize_session_state():
    """Initialize session state variables."""
    # Load persistent stats
    persistent_stats = load_persistent_stats()
    
    # Session-specific stats
    if 'score' not in st.session_state:
        st.session_state.score = 0
    if 'total_questions' not in st.session_state:
        st.session_state.total_questions = 0
    if 'current_question' not in st.session_state:
        st.session_state.current_question = None
    if 'answer_submitted' not in st.session_state:
        st.session_state.answer_submitted = False
    if 'selected_bones' not in st.session_state:
        st.session_state.selected_bones = list(ANATOMICAL_DATA.keys())
    if 'streak' not in st.session_state:
        st.session_state.streak = 0
    if 'best_streak' not in st.session_state:
        st.session_state.best_streak = 0
    
    # Persistent stats
    if 'persistent_total_score' not in st.session_state:
        st.session_state.persistent_total_score = persistent_stats['total_score']
    if 'persistent_total_questions' not in st.session_state:
        st.session_state.persistent_total_questions = persistent_stats['total_questions']
    if 'persistent_best_streak' not in st.session_state:
        st.session_state.persistent_best_streak = persistent_stats['best_streak']
    if 'persistent_sessions_played' not in st.session_state:
        st.session_state.persistent_sessions_played = persistent_stats['sessions_played']
    if 'last_celebration_streak' not in st.session_state:
        st.session_state.last_celebration_streak = persistent_stats['last_celebration_streak']
    
    # Mark as new session if this is the first time
    if 'session_initialized' not in st.session_state:
        st.session_state.persistent_sessions_played += 1
        st.session_state.session_initialized = True
        save_persistent_stats()

def generate_question(selected_bones: List[str]) -> Tuple[str, int, str, str]:
    """Generate a random question from selected bone groups."""
    bone_group = random.choice(selected_bones)
    bone_data = ANATOMICAL_DATA[bone_group]
    component_number = random.choice(list(bone_data["components"].keys()))
    correct_answer = bone_data["components"][component_number]
    
    return bone_group, component_number, correct_answer, bone_data["title"]

def normalize_answer(answer: str) -> str:
    """Normalize answer for comparison (remove accents, lowercase, etc.)."""
    return answer.lower().strip().replace("é", "e").replace("è", "e").replace("ê", "e").replace("à", "a").replace("ô", "o").replace("ç", "c")

def check_answer(user_answer: str, correct_answer: str) -> bool:
    """Check if the user's answer matches the correct answer."""
    user_normalized = normalize_answer(user_answer)
    correct_normalized = normalize_answer(correct_answer)
    
    # Check exact match first
    if user_normalized == correct_normalized:
        return True
    
    # Check if user answer contains key words from correct answer
    correct_words = correct_normalized.split()
    user_words = user_normalized.split()
    
    # If user provides at least 60% of the important words, consider it correct
    important_words = [w for w in correct_words if len(w) > 3]  # Words longer than 3 chars
    if important_words:
        matches = sum(1 for word in important_words if word in user_words)
        return matches >= len(important_words) * 0.6
    
    return False

def reset_game():
    """Reset game statistics."""
    st.session_state.score = 0
    st.session_state.total_questions = 0
    st.session_state.current_question = None
    st.session_state.answer_submitted = False
    st.session_state.streak = 0

def display_anatomical_image(bone_group: str, image_folder: str = "images"):
    """Display anatomical images for the given bone group."""
    bone_data = ANATOMICAL_DATA[bone_group]
    image_files = bone_data.get("image_files", [])
    
    if not image_files:
        st.warning(f"Aucune image configurée pour {bone_group}")
        return
    
    # Check if images folder exists
    if not os.path.exists(image_folder):
        st.error(f"📁 Dossier d'images '{image_folder}' introuvable. Veuillez créer le dossier et y ajouter les images anatomiques.")
        return
    
    # Display images in tabs or columns depending on number
    if len(image_files) == 1:
        # Single image
        image_path = os.path.join(image_folder, image_files[0])
        if os.path.exists(image_path):
            st.image(image_path, caption=f"{bone_data['title']} - {bone_data['views'][0]}", use_container_width=True)
        else:
            st.warning(f"Image manquante: {image_files[0]}")
    
    elif len(image_files) <= 4:
        # Multiple images in tabs
        tabs = st.tabs(bone_data['views'])
        for i, (tab, image_file, view) in enumerate(zip(tabs, image_files, bone_data['views'])):
            with tab:
                image_path = os.path.join(image_folder, image_file)
                if os.path.exists(image_path):
                    st.image(image_path, caption=f"{bone_data['title']} - {view}", use_container_width=True)
                else:
                    st.warning(f"Image manquante: {image_file}")
    
    else:
        # Too many images, use selectbox
        selected_view = st.selectbox("Choisir une vue:", bone_data['views'], key=f"view_selector_{bone_group}")
        view_index = bone_data['views'].index(selected_view)
        image_file = image_files[view_index]
        image_path = os.path.join(image_folder, image_file)
        
        if os.path.exists(image_path):
            st.image(image_path, caption=f"{bone_data['title']} - {selected_view}", use_container_width=True)
        else:
            st.warning(f"Image manquante: {image_file}")

def create_bone_diagram(bone_group: str, highlighted_number: int):
    """Create a visual representation of the bone with numbered components."""
    components = ANATOMICAL_DATA[bone_group]["components"]
    
    # Create a grid layout for the numbers
    numbers_html = ""
    for i, num in enumerate(sorted(components.keys())):
        if num == highlighted_number:
            # Highlighted number (current question)
            numbers_html += f'''
                <div style="background-color: #ff4444; color: white; border-radius: 50%; 
                           width: 40px; height: 40px; display: inline-flex; align-items: center; 
                           justify-content: center; font-weight: bold; font-size: 16px;
                           margin: 3px; box-shadow: 0 4px 8px rgba(255,68,68,0.3);
                           animation: pulse 1.5s infinite;">
                    {num}
                </div>
            '''
        else:
            # Regular numbers
            numbers_html += f'''
                <div style="background-color: #e9ecef; color: #495057; border-radius: 50%; 
                           width: 35px; height: 35px; display: inline-flex; align-items: center; 
                           justify-content: center; font-weight: bold; margin: 3px;">
                    {num}
                </div>
            '''
    
    # Complete HTML structure
    diagram_html = f'''
    <style>
        @keyframes pulse {{
            0% {{ box-shadow: 0 4px 8px rgba(255,68,68,0.3); }}
            50% {{ box-shadow: 0 8px 16px rgba(255,68,68,0.6); }}
            100% {{ box-shadow: 0 4px 8px rgba(255,68,68,0.3); }}
        }}
    </style>
    <div style="border: 2px solid #1f77b4; border-radius: 10px; padding: 20px; 
                background-color: #f8f9fa; text-align: center;">
        <h3 style="color: #1f77b4; margin-bottom: 20px;">{bone_group}</h3>
        <div style="display: flex; flex-wrap: wrap; justify-content: center; gap: 5px; max-width: 600px; margin: 0 auto;">
            {numbers_html}
        </div>
    </div>
    '''
    
    return diagram_html

def main():
    st.set_page_config(
        page_title="Ostéologie Équine - Quiz",
        page_icon="🐎",
        layout="wide"
    )
    
    initialize_session_state()
    
    # Header
    st.title("🐎 Quiz d'Ostéologie Équine")
    st.markdown("*Apprenez l'anatomie équine de façon interactive*")
    
    # Sidebar for settings
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Bone selection
        st.subheader("Sélectionner les groupes d'os")
        available_bones = list(ANATOMICAL_DATA.keys())
        
        # Select all/none buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Tout sélectionner"):
                st.session_state.selected_bones = available_bones.copy()
                st.rerun()
        with col2:
            if st.button("Tout désélectionner"):
                st.session_state.selected_bones = []
                st.rerun()
        
        # Individual bone selection
        selected_bones_temp = []
        for bone in available_bones:
            bone_count = len(ANATOMICAL_DATA[bone]["components"])
            if st.checkbox(
                f"{bone} ({bone_count} structures)", 
                value=bone in st.session_state.selected_bones,
                key=f"bone_{bone}"
            ):
                selected_bones_temp.append(bone)
        
        st.session_state.selected_bones = selected_bones_temp
        
        st.divider()
        
        # Statistics
        st.subheader("📊 Statistiques")
        
        # Session stats
        st.markdown("**Cette session:**")
        if st.session_state.total_questions > 0:
            session_accuracy = (st.session_state.score / st.session_state.total_questions) * 100
            st.metric("Précision", f"{session_accuracy:.1f}%")
            st.metric("Score", f"{st.session_state.score}/{st.session_state.total_questions}")
            st.metric("Série actuelle", st.session_state.streak)
            st.metric("Meilleure série (session)", st.session_state.best_streak)
        else:
            st.info("Commencez le quiz pour voir vos statistiques de session!")
        
        st.markdown("---")
        
        # Persistent stats
        st.markdown("**Statistiques globales:**")
        if st.session_state.persistent_total_questions > 0:
            total_accuracy = (st.session_state.persistent_total_score / st.session_state.persistent_total_questions) * 100
            st.metric("Précision totale", f"{total_accuracy:.1f}%")
            st.metric("Score total", f"{st.session_state.persistent_total_score}/{st.session_state.persistent_total_questions}")
            st.metric("Meilleure série (toujours)", st.session_state.persistent_best_streak)
            st.metric("Sessions jouées", st.session_state.persistent_sessions_played)
        else:
            st.info("Aucune statistique globale disponible encore!")
        
        if st.button("🔄 Réinitialiser", type="secondary"):
            reset_game()
            st.rerun()
        
        st.divider()
        
        # Instructions
        st.subheader("📖 Instructions")
        st.markdown("""
        1. Sélectionnez les groupes d'os à étudier
        2. Cliquez sur "Nouvelle question"
        3. Identifiez la structure correspondant au numéro rouge clignotant
        4. Tapez votre réponse et validez
        5. Continuez pour améliorer votre score!
        
        **Astuce:** Les réponses partielles sont acceptées si elles contiennent les mots-clés principaux.
        """)
    
    # Main content area
    if not st.session_state.selected_bones:
        st.warning("⚠️ Veuillez sélectionner au moins un groupe d'os dans la barre latérale pour commencer.")
        return
    
    # Question generation
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🎲 Nouvelle Question", type="primary", use_container_width=True):
            st.session_state.current_question = generate_question(st.session_state.selected_bones)
            st.session_state.answer_submitted = False
            st.rerun()
    
    # Display current question
    if st.session_state.current_question:
        bone_group, component_number, correct_answer, bone_title = st.session_state.current_question
        
        st.markdown("---")
        
        col1, col2 = st.columns([3, 2])
        
        with col1:
            st.subheader(f"📋 {bone_title}")
            st.markdown(f"**Vues disponibles:** {', '.join(ANATOMICAL_DATA[bone_group]['views'])}")
            
            # Display anatomical images
            display_anatomical_image(bone_group)
        
        with col2:
            st.markdown("### ❓ Question")
            st.info(f"**Quelle est la structure numéro {component_number} ?**")
            
            # Answer input
            if not st.session_state.answer_submitted:
                user_answer = st.text_input(
                    "Votre réponse:", 
                    key="answer_input",
                    placeholder="Tapez le nom de la structure...",
                    help="Les accents ne sont pas obligatoires. Les réponses partielles sont acceptées."
                )
                
                col_submit, col_skip = st.columns(2)
                with col_submit:
                    submit_button = st.button("✅ Valider", type="primary", use_container_width=True)
                with col_skip:
                    skip_button = st.button("⏭️ Passer", type="secondary", use_container_width=True)
                
                if submit_button and user_answer:
                    st.session_state.total_questions += 1
                    st.session_state.persistent_total_questions += 1
                    is_correct = check_answer(user_answer, correct_answer)
                    
                    if is_correct:
                        st.session_state.score += 1
                        st.session_state.persistent_total_score += 1
                        st.session_state.streak += 1
                        
                        # Update best streaks
                        if st.session_state.streak > st.session_state.best_streak:
                            st.session_state.best_streak = st.session_state.streak
                        if st.session_state.streak > st.session_state.persistent_best_streak:
                            st.session_state.persistent_best_streak = st.session_state.streak
                        
                        st.success(f"🎉 Correct! La réponse était: **{correct_answer}**")
                        
                        # Special celebration message for 5 in a row
                        if st.session_state.streak == 5 and st.session_state.last_celebration_streak != st.session_state.streak:
                            st.session_state.last_celebration_streak = st.session_state.streak
                            show_celebration_message()
                        elif st.session_state.streak > 1:
                            st.balloons()
                            
                    else:
                        st.session_state.streak = 0
                        st.error(f"❌ Incorrect. La bonne réponse était: **{correct_answer}**")
                        st.info(f"Votre réponse: *{user_answer}*")
                    
                    # Save persistent stats
                    save_persistent_stats()
                    st.session_state.answer_submitted = True
                    
                elif skip_button:
                    st.session_state.total_questions += 1
                    st.session_state.persistent_total_questions += 1
                    st.session_state.streak = 0
                    st.warning(f"⏭️ Question passée. La réponse était: **{correct_answer}**")
                    save_persistent_stats()
                    st.session_state.answer_submitted = True
                
                elif submit_button and not user_answer:
                    st.warning("Veuillez entrer une réponse avant de valider.")
            
            else:
                # Show result and next question button
                st.markdown("---")
                if st.button("➡️ Question Suivante", type="primary", use_container_width=True):
                    st.session_state.current_question = generate_question(st.session_state.selected_bones)
                    st.session_state.answer_submitted = False
                    st.rerun()
    
    else:
        st.info("👆 Cliquez sur 'Nouvelle Question' pour commencer le quiz!")
    
    # Additional information section
    if st.session_state.current_question:
        bone_group = st.session_state.current_question[0]
        with st.expander("📚 Voir toutes les structures de ce groupe"):
            components = ANATOMICAL_DATA[bone_group]["components"]
            
            # Create two columns for better layout
            col1, col2 = st.columns(2)
            items = list(components.items())
            mid_point = len(items) // 2
            
            with col1:
                for num, name in items[:mid_point]:
                    if num == st.session_state.current_question[1]:
                        st.markdown(f"**{num}. {name}** ← *Question actuelle*")
                    else:
                        st.write(f"{num}. {name}")
            
            with col2:
                for num, name in items[mid_point:]:
                    if num == st.session_state.current_question[1]:
                        st.markdown(f"**{num}. {name}** ← *Question actuelle*")
                    else:
                        st.write(f"{num}. {name}")

if __name__ == "__main__":
    main()