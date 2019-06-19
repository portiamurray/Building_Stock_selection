def buildingimport(path,NumRetrofits):
    import pandas as pd
    import numpy as np

    Retrofit_Objectives=pd.read_excel(path,'Sheet1',usecols='A:Q',header=None)
    Rettitles=['Roof_area','Bldg_area','ExistingSystem','Retrofit_cost0','Retrofit_cost1','Retrofit_cost2','Retrofit_cost3','Retrofit_cost4','Retrofit_cost5','Retrofit_cost6','EmbodiedE0','EmbodiedE1','EmbodiedE2','EmbodiedE3','EmbodiedE4','EmbodiedE5','EmbodiedE6']
    Retrofit_Objectives.columns=Rettitles
    Retrofit_costs=[None]*7
    Retrofit_EE=[None]*7
    for i in range(0,7):
        labelc='Retrofit_cost'+str(i)
        labele='EmbodiedE'+str(i)
        Retrofit_costs[i]=Retrofit_Objectives.loc[0,labelc]
        Retrofit_EE[i]=Retrofit_Objectives.loc[0,labele]
    Roof_area=Retrofit_Objectives.loc[0,'Roof_area']
    Bldg_area=Retrofit_Objectives.loc[0,'Bldg_area']
    Retrofit={}
    Ret={}
    Loads = np.empty([240,3,NumRetrofits])
    Days = np.empty([240,NumRetrofits])
    P_solar = np.empty([240,NumRetrofits])
    retits=['noretrofit','roof','ground','wall','win','winwall','full']
    for r in range(0,7):
        Retrofit[r]=pd.read_excel(path,retits[r],usecols='A:E',header=None)
        rettitles=['Heat','Cool','Elec','PV','Rep_days']
        Retrofit[r].columns=rettitles
        Ret[r]=Retrofit[r].as_matrix()
        Loads[:,0,r]=Ret[r][:,0]
        Loads[:,1,r]=Ret[r][:,1]
        Loads[:,2,r]=Ret[r][:,2]
        Days[:,r]=Ret[r][:,4]
        P_solar[:,r]=Ret[r][:,3]
    Heat=Loads[:,0,:]
    Cool=Loads[:,1,:]
    Elec=Loads[:,2,:]
    PeakLoad=Loads.max(axis=0)
    if Retrofit_Objectives.loc[0,'ExistingSystem']==7:
        ExistingSystem=0
        Cost_underfloor=0
        Embodied_underfloor=0
    elif Retrofit_Objectives.loc[0,'ExistingSystem']==4:
        ExistingSystem=1
        Cost_underfloor=100
        Embodied_underfloor=5.06
    elif Retrofit_Objectives.loc[0,'ExistingSystem']==2:
        ExistingSystem=2
        Cost_underfloor=100
        Embodied_underfloor=5.06
    elif Retrofit_Objectives.loc[0,'ExistingSystem']==6:
        ExistingSystem=3
        Cost_underfloor=100
        Embodied_underfloor=5.06
    elif Retrofit_Objectives.loc[0,'ExistingSystem']==9:
        ExistingSystem=4
        Cost_underfloor=100
        Embodied_underfloor=5.06
    elif Retrofit_Objectives.loc[0,'ExistingSystem']==5:
        ExistingSystem=5
        Cost_underfloor=100
        Embodied_underfloor=5.06
    elif Retrofit_Objectives.loc[0,'ExistingSystem']==8:
        ExistingSystem=0
        Cost_underfloor=0
        Embodied_underfloor=0
    elif Retrofit_Objectives.loc[0,'ExistingSystem']==3:
        ExistingSystem=2
        Cost_underfloor=0
        Embodied_underfloor=0
    return [Roof_area,Bldg_area,ExistingSystem,Retrofit_costs,Retrofit_EE,Loads,PeakLoad,P_solar,Days,Cost_underfloor,Embodied_underfloor]