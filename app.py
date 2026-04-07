import streamlit as st
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import streamlit.components.v1 as components

# ---------------- FUZZY SETUP ---------------- #

trafficA = ctrl.Antecedent(np.arange(0, 101, 1), 'trafficA')
trafficB = ctrl.Antecedent(np.arange(0, 101, 1), 'trafficB')
priority = ctrl.Consequent(np.arange(0, 1.01, 0.01), 'priority')

trafficA['low'] = fuzz.trimf(trafficA.universe, [0, 20, 40])
trafficA['medium'] = fuzz.trimf(trafficA.universe, [30, 50, 70])
trafficA['high'] = fuzz.trimf(trafficA.universe, [60, 80, 100])

trafficB['low'] = fuzz.trimf(trafficB.universe, [0, 20, 40])
trafficB['medium'] = fuzz.trimf(trafficB.universe, [30, 50, 70])
trafficB['high'] = fuzz.trimf(trafficB.universe, [60, 80, 100])

priority['A'] = fuzz.trimf(priority.universe, [0, 0, 0.6])
priority['B'] = fuzz.trimf(priority.universe, [0.4, 1, 1])

# ---------------- RULES ---------------- #

rule1 = ctrl.Rule(trafficA['low'] & trafficB['low'], priority['A'])

rule2 = ctrl.Rule(trafficA['low'] & trafficB['medium'], priority['B'])
rule3 = ctrl.Rule(trafficA['low'] & trafficB['high'], priority['B'])

rule4 = ctrl.Rule(trafficA['medium'] & trafficB['low'], priority['A'])
rule5 = ctrl.Rule(trafficA['medium'] & trafficB['medium'], priority['A'])
rule6 = ctrl.Rule(trafficA['medium'] & trafficB['high'], priority['B'])

rule7 = ctrl.Rule(trafficA['high'] & trafficB['low'], priority['A'])
rule8 = ctrl.Rule(trafficA['high'] & trafficB['medium'], priority['A'])
rule9 = ctrl.Rule(trafficA['high'] & trafficB['high'], priority['B'])

system = ctrl.ControlSystem([
    rule1, rule2, rule3,
    rule4, rule5, rule6,
    rule7, rule8, rule9
])

def decide_priority(a, b):
    sim = ctrl.ControlSystemSimulation(system)
    sim.input['trafficA'] = a
    sim.input['trafficB'] = b
    sim.compute()

    return sim.output.get('priority', 0.0)

# ---------------- UI ---------------- #

st.set_page_config(page_title="Smart Traffic System", layout="centered")

st.title("🚦 Smart Traffic Control using Fuzzy Logic")

# Inputs
st.subheader("Traffic Input")
st.write("0-40: Low | 30-70: Medium | 60-100: High")
t1 = st.slider("Traffic R1", 0, 100, 10)
t2 = st.slider("Traffic R2", 0, 100, 10)
t3 = st.slider("Traffic R3", 0, 100, 10)
t4 = st.slider("Traffic R4", 0, 100, 10)

emergency = st.selectbox("Emergency Road", ["None", "R1", "R2", "R3", "R4"])
pedestrian = st.checkbox("Pedestrian Crossing")

# ---------------- VISUALIZATION ---------------- #

st.subheader("🚦 Live Intersection")


def intersection_ui(active):
    
    if active == "A":   # vertical
        r1 = r4 = "#00FF00"   # top & bottom
        r2 = r3 = "#FF0000"

    elif active == "B": # horizontal
        r2 = r3 = "#00FF00"   # left & right
        r1 = r4 = "#FF0000"

    else:
        r1 = r2 = r3 = r4 = "#FF0000"

    html = f"""
    <div style="position:relative; width:320px; height:320px; margin:auto;">
        <div style="position:absolute; top:0; left:140px; width:40px; height:320px; background:#2c2c2c;"></div>
        <div style="position:absolute; top:140px; left:0; width:320px; height:40px; background:#2c2c2c;"></div>

        <div style="position:absolute; top:20px; left:150px; width:20px; height:20px; background:{r1}; border-radius:50%;"></div>
        <div style="position:absolute; top:150px; left:20px; width:20px; height:20px; background:{r2}; border-radius:50%;"></div>
        <div style="position:absolute; top:150px; right:20px; width:20px; height:20px; background:{r3}; border-radius:50%;"></div>
        <div style="position:absolute; bottom:20px; left:150px; width:20px; height:20px; background:{r4}; border-radius:50%;"></div>

        <div style="position:absolute; top:130px; left:130px; width:60px; height:60px; background:#000; border-radius:10px;"></div>
    </div>
    """

    components.html(html, height=350)

# ---------------- LOGIC ---------------- #

pairA = (t1 + t4) // 2
pairB = (t2 + t3) // 2

active = None

# 🚑 Emergency
if emergency != "None":
    st.error(f"🚑 Emergency on {emergency}")

    if emergency in ["R1", "R4"]:
        intersection_ui("A")
    else:
        intersection_ui("B")

    st.info("After emergency → normal traffic resumes")

# 🚶 Pedestrian
if pedestrian:
    st.warning("🚶 Pedestrian crossing → ALL RED")
    intersection_ui("NONE")
    st.info("After pedestrian → normal traffic resumes")

# 🧠 ALWAYS run fuzzy after overrides
pr = decide_priority(pairA, pairB)

if pr < 0.5:
    active = "A"
else:
    active = "B"

st.success(f"Priority: Pair {active} goes first")
intersection_ui(active)
