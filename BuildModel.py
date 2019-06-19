def retrofithub(Lin_cap_costs,Fixed_cap_costs,Lin_EE,Fixed_EE,CMatrix,STTech,PVTech,GSHPTech,htech,Horizon,Biomass_potential,Roof_area,Bldg_area,ExistingSystem,Retrofit_costs,Retrofit_EE,Loads,Days,PeakLoad,P_solar,inp,inp2,stor,ret,ex_tech,TechStor,TechInp,AnnuityRet,AnnuityStor,AnnuityInput,AnnuityUnderfloor,FIT,Cost_underfloor,Embodied_underfloor,Lifetime_underfloor,Embodied_boreholes,Lifetime_boreholes,gap):
    from docplex.mp.model import Model
    from docplex.util.environment import get_environment
    mdl = Model(name='LCA_retrofithub')
    ##VARIABLE DECLARATION
    mdl.Pin=mdl.continuous_var_matrix(Horizon,inp,lb=0,name='Pin')
    mdl.P_export=mdl.continuous_var_matrix(Horizon,stor,lb=0,name='P_export')
    mdl.y=mdl.binary_var_list(inp2,name='y')
    mdl.Capacity=mdl.continuous_var_list(inp2,lb=0,name='Capacity')
    mdl.y_retrofit=mdl.binary_var_list(ret,name='y_retrofit')
    mdl.y_underfloor=mdl.binary_var(name='y_underfloor')
    #Storage
    mdl.Qin=mdl.continuous_var_matrix(Horizon,stor,lb=0,name='Qin')
    mdl.Qout=mdl.continuous_var_matrix(Horizon,stor,lb=0,name='Qout')
    mdl.E=mdl.continuous_var_matrix(Horizon,stor,lb=0,name='E')
    mdl.Storage_cap=mdl.continuous_var_list(stor,lb=0,name='Storage_cap')
    mdl.y_stor=mdl.binary_var_list(stor,name='y_stor')
    #Dummy variables
    mdl.dummy=mdl.continuous_var_cube(Horizon,inp,ret,lb=0,name='dummy')#dummy for conversion tech
    mdl.dummer=mdl.continuous_var_cube(Horizon,stor,ret,lb=0,name='dummer')#dummy for storage
    mdl.dummy_pv=mdl.continuous_var_matrix(stor,ret,lb=0,name='dummy_pv')#dummy pv variable
    mdl.dummy_st=mdl.continuous_var_matrix(stor,ret,lb=0,name='dummy_st')#dummy st variable
    #Objective variables
    mdl.Operating_cost=mdl.continuous_var(lb=0,name='Operating_cost')
    mdl.Income_via_exports=mdl.continuous_var(lb=0,name='Income_via_exports')
    mdl.Investment_cost_tech=mdl.continuous_var(lb=0,name='Investment_cost_tech')
    mdl.Investment_cost_stor=mdl.continuous_var(lb=0,name='Investment_cost_stor')
    mdl.Investment_cost_ret=mdl.continuous_var(lb=0,name='Inveestment_cost_ret')
    mdl.Total_cost=mdl.continuous_var(lb=0,name='Total_cost')
    mdl.Total_carbon=mdl.continuous_var(lb=0,name='Total_carbon')
    mdl.Operating_emissions=mdl.continuous_var(lb=0,name='Operating_emissions')
    mdl.Embodied_system_emissions=mdl.continuous_var(lb=0,name='Embodied_system_emissions')
    mdl.Embodied_boreholes=mdl.continuous_var(lb=0,name='Embodied_boreholes')
    mdl.Embodied_storage=mdl.continuous_var(lb=0,name='Embodied_storage')
    mdl.Embodied_retrofit=mdl.continuous_var(lb=0,name='Embodied_retrofit')
    mdl.Embodied_underfloor=mdl.continuous_var(lb=0,name='Embodied_underfloor')
    ##CONSTRAINT DECLARATION
    #Dummy variable constraints (equates P[h,i]*y_retrofit[r])
    mdl.add_constraints(mdl.dummy[h,i,r]>=0 for h in Horizon for i in inp for r in ret)
    mdl.add_constraints(mdl.dummy[h,i,r]<=50000*mdl.y_retrofit[r] for h in Horizon for i in inp for r in ret)
    mdl.add_constraints(mdl.Pin[h,i]-mdl.dummy[h,i,r]>=0 for h in Horizon for i in inp for r in ret)
    mdl.add_constraints(mdl.Pin[h,i]-mdl.dummy[h,i,r]<=50000*(1-mdl.y_retrofit[r]) for h in Horizon for i in inp for r in ret)
    mdl.add_constraint(mdl.Storage_cap[0]<=Bldg_area/58*1.5)
    mdl.add_constraint(mdl.Storage_cap[1]<=Bldg_area/122*1.5)
    mdl.add_constraint(mdl.Storage_cap[2]<=Bldg_area*0.1)
    mdl.add_constraint(mdl.sum(mdl.y[ht] for ht in htech)==1)
    #Dummer variable constraint (equates P_export[h,s]*y_retrofit[r])
    mdl.add_constraints(mdl.dummer[h,s,r]>=0 for h in Horizon for s in stor for r in ret)
    mdl.add_constraints(mdl.dummer[h,s,r]<=50000*mdl.y_retrofit[r] for h in Horizon for s in stor for r in ret)
    mdl.add_constraints(mdl.P_export[h,s]-mdl.dummer[h,s,r]>=0 for h in Horizon for s in stor for r in ret)
    mdl.add_constraints(mdl.P_export[h,s]-mdl.dummer[h,s,r]<=50000*(1-mdl.y_retrofit[r])for h in Horizon for s in stor for r in ret)
    mdl.add_constraints(mdl.P_export[h,s]==0 for h in Horizon for s in stor if s!=2)
    #Dummy pv variable constraints (equates Capacity["PV"]*y_retrofit[r])
    mdl.add_constraints(mdl.dummy_pv[s,r]>=0 for s in stor for r in ret)
    mdl.add_constraints(mdl.dummy_pv[s,r]<=50000*mdl.y_retrofit[r] for r in ret for s in stor)
    mdl.add_constraints(mdl.Capacity[PVTech]-mdl.dummy_pv[s,r]>=0 for r in ret for s in stor)
    mdl.add_constraints(mdl.Capacity[PVTech]-mdl.dummy_pv[s,r]<=50000*(1-mdl.y_retrofit[r])for r in ret for s in stor)
    #Dummy st variable constraints (equates Capacity["ST"]*y_retrofit[r])
    mdl.add_constraints(mdl.dummy_st[s,r]>=0 for r in ret for s in stor)
    mdl.add_constraints(mdl.dummy_st[s,r]<=50000*mdl.y_retrofit[r] for r in ret for s in stor)
    mdl.add_constraints(mdl.Capacity[STTech]-mdl.dummy_st[s,r]>=0 for r in ret for s in stor)
    mdl.add_constraints(mdl.Capacity[STTech]-mdl.dummy_st[s,r]<=50000*(1-mdl.y_retrofit[r])for r in ret for s in stor)
    #Fixed cost constraint
    mdl.add_constraints(mdl.Capacity[i]<=50000*mdl.y[i] for i in inp2)
    #Load balance
    mdl.add_constraints(mdl.sum(mdl.Pin[h,i]*CMatrix[s,i] for i in inp)+mdl.Qout[h,s]-mdl.Qin[h,s]==mdl.sum(mdl.y_retrofit[r]*Loads[h,s,r] for r in ret)+mdl.P_export[h,s] for s in stor for h in Horizon)
    #Capacity constraint
    mdl.add_constraints(mdl.Pin[h,i]*CMatrix[(s,i)]<=mdl.Capacity[i] for i in inp2 for s in stor for h in Horizon)
    #Solar PV constraint
    mdl.add_constraints(mdl.Pin[h,PVTech]==mdl.sum(P_solar[h,r]*mdl.dummy_pv[2,r] for r in ret) for h in Horizon)
    #Solar ST constraint
    mdl.add_constraints(mdl.Pin[h,STTech]==mdl.sum(P_solar[h,r]*mdl.dummy_st[0,r]for r in ret)for h in Horizon)
    #Max elements (only one heating system can be installed)
    mdl.add_constraints(mdl.sum(mdl.y[d] for d in htech)<=1 for s in stor)
    #Roof area constraints
    mdl.add_constraint(mdl.Capacity[PVTech]+mdl.Capacity[STTech]<=Roof_area)
    #Storage balance
    for h in Horizon:
        if (h==0) or (h==24) or (h==48) or (h==72) or (h==96) or (h==120) or (h==144) or (h==168) or (h==192) or (h==216):
            mdl.add_constraints(mdl.E[h,s]==TechStor[s].decay*mdl.E[h+23,s]+TechStor[s].chg_eff*mdl.Qin[h,s]-(1/TechStor[s].dch_eff)*mdl.Qout[h,s] for s in stor)
        else:
            mdl.add_constraints(mdl.E[h,s]==TechStor[s].decay*mdl.E[h-1,s]+TechStor[s].chg_eff*mdl.Qin[h,s]-(1/TechStor[s].dch_eff)*mdl.Qout[h,s] for s in stor)
    #Storage charge limit
    mdl.add_constraints(mdl.Qin[h,s]<=TechStor[s].max_charge*mdl.Storage_cap[s] for h in Horizon for s in stor)
    #Storage discharge limit
    mdl.add_constraints(mdl.Qout[h,s]<=TechStor[s].max_discharge*mdl.Storage_cap[s] for h in Horizon for s in stor)
    #Storage capacity constraint
    mdl.add_constraints(mdl.E[h,s]<=mdl.Storage_cap[s] for h in Horizon for s in stor)
    #Fixed cost storage
    mdl.add_constraints(mdl.Storage_cap[s]<=100000*mdl.y_stor[s] for s in stor)
    #Only one retrofit state
    mdl.add_constraint(mdl.sum(mdl.y_retrofit[r] for r in ret)==1)
    #Need for underfloor CHECK RETROFIT STATES FROM RAPHAEL'S PAPER
    mdl.add_constraint(mdl.y_underfloor>=(mdl.sum(mdl.y_retrofit[r] for r in range(0,5))+mdl.y[6]+mdl.y[GSHPTech]-1.5)/2)
    #Existing system size #ALSO CHECK RETROFIT STATES HERE
    mdl.add_constraints(mdl.Capacity[e]==PeakLoad[0,0]*mdl.y[e] for e in ex_tech)
    #Existing system install
    mdl.add_constraints(mdl.y[e]==0 for e in ex_tech if e!=ExistingSystem)
    #Restrict export of systems
    mdl.add_constraints(mdl.dummer[h,2,r]<=mdl.dummy[h,PVTech,r] for r in ret for h in Horizon)
    #Restriction of biomass
    mdl.add_constraints(mdl.sum((mdl.dummy[h,3,r]+mdl.dummy[h,10,r])*(Days[h,r]) for h in Horizon)<=Bldg_area*Biomass_potential for r in ret)
    ##Calculate objective function variables
    #Operating cost
    mdl.add_constraint(mdl.Operating_cost==mdl.sum(TechInp[i].operating_costs*Days[h,r]*mdl.dummy[h,i,r] for h in Horizon for i in inp for r in ret))
    # Income from selling PV at FIT
    mdl.add_constraint(mdl.Income_via_exports==mdl.sum(FIT*Days[h,r]*mdl.dummer[h,2,r] for h in Horizon for r in ret))
    #Technology investment cost
    mdl.add_constraint(mdl.Investment_cost_tech==mdl.sum((Fixed_cap_costs[(i)]*mdl.y[i]+Lin_cap_costs[(i)]*mdl.Capacity[i])*AnnuityInput[i] for i in inp2))
    mdl.add_constraint(mdl.Investment_cost_stor==mdl.sum((TechStor[s].fixed_cap_costs*mdl.y_stor[s]+TechStor[s].linear_cap_costs*mdl.Storage_cap[s])*AnnuityStor[s] for s in stor))
    mdl.add_constraint(mdl.Investment_cost_ret==mdl.sum((Retrofit_costs[r]*mdl.y_retrofit[r])*AnnuityRet[r] for r in ret)+(AnnuityUnderfloor*Cost_underfloor*mdl.y_underfloor*Bldg_area))
    mdl.add_constraint(mdl.Total_cost==mdl.Investment_cost_tech+mdl.Investment_cost_stor+mdl.Investment_cost_ret+mdl.Operating_cost-mdl.Income_via_exports)
    mdl.add_constraint(mdl.Embodied_system_emissions==mdl.sum((Lin_EE[(i)]*mdl.Capacity[i]+Fixed_EE[(i)]*mdl.y[i])/TechInp[i].lifetime for i in inp2))
    mdl.add_constraint(mdl.Embodied_storage==mdl.sum((TechStor[s].embodied_linear*mdl.Storage_cap[s]+TechStor[s].embodied_fixed*mdl.y_stor[s])/TechStor[s].lifetime for s in stor))
    mdl.add_constraint(mdl.Embodied_retrofit==mdl.sum(Retrofit_EE[r]*mdl.y_retrofit[r]/40 for r in ret))
    mdl.add_constraint(mdl.Embodied_underfloor==Embodied_underfloor*mdl.y_underfloor*Bldg_area/Lifetime_underfloor)
    mdl.add_constraint(mdl.Embodied_boreholes==mdl.Capacity[GSHPTech]/0.03*Embodied_boreholes/Lifetime_boreholes)
    mdl.add_constraint(mdl.Operating_emissions==mdl.sum(TechInp[i].carbon_factor*Days[h,r]*mdl.dummy[h,i,r] for h in Horizon for i in inp for r in ret))
    mdl.add_constraint(mdl.Total_carbon==mdl.Embodied_system_emissions+mdl.Embodied_storage+mdl.Embodied_retrofit+mdl.Embodied_underfloor+mdl.Embodied_boreholes+mdl.Operating_emissions)
    mdl.parameters.mip.tolerances.mipgap = gap
    return mdl