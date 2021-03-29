# %%
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import shapely.geometry as sg
import descartes as dc

sns.set_theme(style="white")
# Funtionalities
#------------------------------------------------------------------------------------------------------
# Data of Points
psD1 = pd.read_csv("https://github.com/DaveWongKaWa/vennDiagram/blob/main/VennDiagramD1xy.csv?raw=true")
psD1arr = [psD1.S, psD1.P, psD1.M]
psD2 = pd.read_csv("https://github.com/DaveWongKaWa/vennDiagram/blob/main/VennDiagramD2xy.csv?raw=true")
psD2arr = [psD2.S, psD2.P, psD2.M]

pCircle = sg.Point(3, 3).buffer(5)
sCircle = sg.Point(-3, 3).buffer(5)
mCircle = sg.Point(0, -3).buffer(5)

circles = {"P":pCircle, "S":sCircle, "M":mCircle}
pos = {"P":0, "S":1, "M":2}
cpos = {0:"P", 1:"S", 2:"M"}

# Previous Statement
previous = [None, None, None]

# Logic
def args(rel, obj1, obj2):
    if (rel == "A"):
        return operationA(obj1, obj2)
    elif (rel == "E"):
        return operationE(obj1, obj2)
    elif (rel == "I"):
        return operationI(obj1, obj2)
    elif (rel == "O"):
        return operationO(obj1, obj2)
def operationA(obj1, obj2):
    previous[0], previous[1], previous[2] = 0, obj1, obj2
    picture = circles[obj1].difference(circles[obj2])
    return [picture, "/", 0.3, False]
def operationE(obj1, obj2):
    previous[0], previous[1], previous[2] = 1, obj1, obj2
    return [circles[obj1].intersection(circles[obj2]), "/", 0.3, False]
def operationI(obj1, obj2):
    pos1, pos2, pos3 = pos[obj1], pos[obj2], 3 - (pos[obj1] + pos[obj2])
    x, y = psD1arr[pos2].iloc[pos1], psD1arr[pos2].iloc[pos1 + 6]
    if (previous[0] is not None):
        if (previous[0] == 0 and previous[2] == cpos[pos3]):
            x, y = 0, 0.75
        elif (previous[0] == 1 and pos[previous[1]] + pos[previous[2]] != pos1 + pos2):
            x, y = psD2arr[pos2].iloc[pos1], psD2arr[pos2].iloc[pos1 + 9]
    picture = sg.Point(float(x), float(y)).buffer(0.2)
    return [picture, None, 0.75, True]
def operationO(obj1, obj2):
    pos1, pos2, pos3 = pos[obj1], pos[obj2], 3 - (pos[obj1] + pos[obj2])
    x, y = psD1arr[pos2].iloc[pos1 + 3], psD1arr[pos2].iloc[pos1 + 6]
    if (previous[0] is not None):
        if (previous[0] == 0):
            if (previous[1] == obj1 and previous[2] == cpos[pos3]):
                x, y = psD2arr[pos2].iloc[pos1 + 6], psD2arr[pos2].iloc[pos1 + 15]
            elif (previous[1] == cpos[pos3] and previous[2] == obj2):
                x, y = psD2arr[pos2].iloc[pos1 + 3], psD2arr[pos2].iloc[pos1 + 12]
        elif (previous[0] == 1 and pos[previous[1]] + pos[previous[2]] == pos1 + pos2):
            x, y = psD2arr[pos2].iloc[pos1 + 3], psD2arr[pos2].iloc[pos1 + 12]
    picture = sg.Point(float(x), float(y)).buffer(0.2)
    return [picture, None, 0.75, True]

# convert string input to readable form and sylogical characteristics
class Interpreter:
    def __init__(self, premise1, premise2, conclusion):
        self.P1 = self.decompose(premise1)
        self.P2 = self.decompose(premise2)
        self.C = self.decompose(conclusion)
        self.p1 = self.P1.copy()
        self.p2 = self.P2.copy()
        self.c = [self.C[0], "S", "P"]
        self.PSM = None
        self.mood = self.findMood()
        self.figure = self.findFigure()
        self.standardForm = self.toStandardForm()
    def decompose(self, statement):
        _coverage, _status, _rel = {"All": 0, "No":1, "Some":2}, {"are":0, "are not":10}, {0:"A", 1:"E", 2:"I", 10:"E", 11:"A", 12:"O"}
        chars = list(statement)
        sections = []
        for i in range(len(chars)):
            if (chars[i] == "(" or chars[i] == ")"):
                sections.append(i)
        obj1 = statement[sections[0]+1:sections[1]]
        obj2 = statement[sections[2]+1:sections[3]]
        coverage = statement[0:sections[0]-1]
        status = statement[sections[1]+2:sections[2]-1]
        rel = _rel[_coverage[coverage] + _status[status]]
        return [rel, obj1, obj2]
    def findMood(self):
        rels = [self.P1[0], self.P2[0], self.C[0]]
        if ((rels[0] == "I" or rels[0] == "O") and (rels[1] == "A" or rels[1] == "E")):
            self.P1, self.P2 = self.P2, self.P1
            self.p1, self.p2 = self.p2, self.p1
            rels[0], rels[1] = rels[1], rels[0]
        return f"{rels[0]}{rels[1]}{rels[2]}"
    def findFigure(self):
        figures = {tuple([1, 2]):1, tuple([2, 2]):2, tuple([1, 1]):3, tuple([2, 1]):4}
        objs_P1, objs_P2 = {self.P1[1], self.P1[2]}, {self.P2[1], self.P2[2]}
        M ,= objs_P1.intersection(objs_P2)
        M_P1, M_P2 = self.P1.index(M), self.P2.index(M)
        self.PSM = [self.p1[3 - M_P1], self.p2[3 - M_P2], self.p1[M_P1]]
        self.p1[M_P1], self.p1[3 - M_P1] = "M", "P"
        self.p2[M_P2], self.p2[3 - M_P2] = "M", "S"
        return figures[tuple([M_P1, M_P2])]
    def toStandardForm(self):
        roman = {1:"I", 2:"II", 3:"III", 4:"IV"}
        return f"{self.mood}-{roman[self.figure]}"

class Drawer:
    def __init__(self, interpreter, p1 = None, p2 = None, c = None):
        self.p1 = interpreter.p1 if p1 is None else p1
        self.p2 = interpreter.p2 if p1 is None else p2
        self.c = interpreter.c if p1 is None else c
        self.PSM = interpreter.PSM if p1 is None else ["P", "S", "M"]
    def renderBackground(self):
        ax = plt.gca()
        Pfigure = ax.add_patch(dc.PolygonPatch(pCircle, ec="r", alpha=0.5, fill=False))
        Sfigure = ax.add_patch(dc.PolygonPatch(sCircle, ec="b", alpha=0.5, fill=False))
        Mfigure = ax.add_patch(dc.PolygonPatch(mCircle, ec="g", alpha=0.5, fill=False))
        ax.set_xlim(-10, 10); ax.set_ylim(-10, 10)
        ax.legend([Pfigure, Sfigure, Mfigure], [f"P = {self.PSM[0]}", f"S = {self.PSM[1]}", f"M = {self.PSM[2]}"])
        ax.set_aspect("equal")
        return ax
    def renderPremises(self):
        ax = self.renderBackground()
        arg1 = args(self.p1[0], self.p1[1], self.p1[2])
        arg2 = args(self.p2[0], self.p2[1], self.p2[2])
        ax.add_patch(dc.PolygonPatch(arg1[0], fc="black", ec="black", hatch=arg1[1], alpha=arg1[2], fill=arg1[3]))
        ax.add_patch(dc.PolygonPatch(arg2[0], fc="black", ec="black", hatch=arg2[1], alpha=arg2[2], fill=arg2[3]))
        ax.set_title("Premises")
        return ax
    def renderConclusion(self):
        ax = self.renderBackground()
        arg = args(self.c[0], self.c[1], self.c[2])
        ax.add_patch(dc.PolygonPatch(arg[0], fc="black", ec="black", hatch=arg[1], alpha=arg[2], fill=arg[3]))
        ax.set_title("Conclusion")
        return ax
#------------------------------------------------------------------------------------------------------
st.title("Venn Diagram")
option = st.sidebar.selectbox(
    'Statements / Standard Form',
     ['Statements', 'Standard Form'])
st.title(option)
#------------------------------------------------------------------------------------------------------
if (option == 'Statements'):
    st.subheader("Syntax")
    st.write("{Coverage} ({Subject}) {Status} ({Object})")
    st.write("Coverage: [All, No, Some]")
    st.write("Status: [are, are not]")
    st.write("Subject and object should have brackets")

    user_input1 = st.text_input("Premises1", "All (M) are (P)")
    user_input2 = st.text_input("Premises2", "All (S) are (M)")
    user_input3 = st.text_input("Conclusion", "All (S) are (P)")

    read = Interpreter(user_input1, user_input2, user_input3)
    draw = Drawer(read)

    st.subheader("Standard Form")
    st.write(read.standardForm)

    st.subheader("Visualization")
    fig = plt.figure(figsize=(12,12), dpi=120)
    fig.add_subplot(121)
    premisesPlot = draw.renderPremises()
    fig.add_subplot(122)
    conclusionPlot = draw.renderConclusion()
    st.pyplot(fig)
#------------------------------------------------------------------------------------------------------
if (option == 'Standard Form'):
    st.subheader("Syntax")
    st.write("{Mood}-{Figure}")
    st.write("Mood: Combination of A, E, I, O in length 3")
    st.write("Figure: [I, II, III, IV]")
    user_input4 = st.text_input("Standard Form: ", "AAA-I")
    st.write("Comming Soon")
# %%
