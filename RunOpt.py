
from collections import namedtuple
import pandas as pd
import numpy as np

NumRetrofits=7
Timesteps=240
Horizon=range(0,Timesteps)
FIT=0.12
Cost_underfloor=100
Lifetime_underfloor=25
Embodied_underfloor=5.06
Embodied_boreholes=28.1
Lifetime_boreholes=50

InputTech = [
    ("HP_ex",0,10,0),#0
    ("Gas_B_ex",0.120,12.5,0.228),#1
    ("Oil_B_ex",0.101,12.5,0.301),#2
    ("Bio_B_ex",0.125,10,0.027),#3
    ("DH_ex",0.120,20,0.089),#4
    ("El_ex",0,15,0),#5
    ("ASHP",0,15,0),#6
    ("GSHP",0,20,0),#7
    ("Gas_Boiler",0.120,25,0.228),#8
    ("Oil_Boiler",0.101,25,0.301),#9
    ("Bio_Boiler",0.125,25,0.027),#10
    ("MGT",0.120,11,0.228),#11
    ("CChiller",0,15,0),#12
    ("PV",0,20,0),#13
    ("ST",0,20,0),#14
    ("Grid",0.237,100,0.1215)]#15
PVTech=13
STTech=14
GSHPTech=7
Lin_cap_costs = {(0):0,(1):0,(2):0,(3):0,(4):0,(5):0,(6):1020,(7):2380,(8):620,(9):570,(10):860,(11):900,(12):1020,(13):400,(14):1000,(15):0}

Fixed_cap_costs = {(0):0,(1):0,(2):0,(3): 0,(4):0,(5):0,(6):18300,(7):20000,(8):27600,(9):26600,(10):27800,(11):5000,(12):18300,(13):900,(14):4000,(15):0}

Lin_EE = {(0):0,(1):0,(2):0,(3):0,(4):0,(5):0,(6):74.76,(7):72.27,(8):51.2,(9):51.2,(10):51.2,(11):100,(12):50,(13):253.75,(14):184,(15):0}

Fixed_EE = {(0):0,(1):0,(2):0,(3):0,(4):0,(5):0,(6):2329.300,(7):1806.2,(8):0,(9):0,(10):0,(11):3750,(12):2329.300,(13):0,(14):0,(15):0}

CMatrix = {(0,0):2,(0,1):0.8,(0,2):0.8,(0,3):0.75,(0,4):0.95,(0,5):1,(0,6):3,(0,7):4,(0,8):0.9,(0,9):0.9,(0,10):0.85,(0,11):0.65,(0,12):0,(0,13):0,(0,14):0.450,(0,15):0,
  (1,0):0,(1,1):0,(1,2):0,(1,3):0,(1,4):0,(1,5):0,(1,6):0,(1,7):0,(1,8):0,(1,9):0,(1,10):0,(1,11):0,(1,12):3,(1,13):0,(1,14):0,(1,15):0,
  (2,0):-1,(2,1):0,(2,2):0,(2,3):0,(2,4):0,(2,5):-1.000,(2,6):-1.000,(2,7):-1.000,(2,8):0,(2,9):0,(2,10):0,(2,11):0.2,(2,12):-1.000,(2,13):0.15,(2,14):0,(2,15):1}

StorTech = [
    ("Heat",12.5,1685,20,4.68,30.69,0.25,0.25,0.99,0.9,0.95,120),
    ("Cool",26,3540,20,4.68,30.69,0.2,0.2,0.99,0.9,0.95,120),
    ("Elec",600,2000,20,157.14,0,0.5,0.5,0.999,0.92,0.92,120)]

discount=0.04
inp=range(0,len(InputTech))
inp2=range(0,len(InputTech)-1)
stor=range(0,len(StorTech))
disp=range(0,12)
ret=range(0,7)
Horizon=range(0,240)
ex_tech=range(0,6)
htech=range(0,12)
techin = namedtuple("Tech", ["name", "operating_costs","lifetime",'carbon_factor'])
techst = namedtuple("Tech", ["name","linear_cap_costs", "fixed_cap_costs","lifetime",'embodied_linear','embodied_fixed','max_charge','max_discharge','decay','chg_eff','dch_eff','MaxCap'])

TechStor = [techst(*s) for s in StorTech]
TechInp = [techin(*i) for  i in InputTech]
AnnuityInput = [None]*len(InputTech)
AnnuityStor = [None]*len(StorTech)
AnnuityRet = [None]*7
Lifetime_underfloor=25
for r in ret:
    AnnuityRet[r]=discount/(1-(1/((1+discount)**40)))
for s in stor:
    AnnuityStor[s]=discount/(1-(1/((1+discount)**TechStor[s].lifetime)))
for i in inp:
    AnnuityInput[i]=discount/(1-(1/((1+discount)**TechInp[i].lifetime)))
AnnuityUnderfloor= discount/(1-(1/((1+discount)**Lifetime_underfloor)))

