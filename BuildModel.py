#This code optimises for both the retrofit option (no retrofit, roof insulation, facade insulation, window replacement, basement insulation, facade and window replacement, or full retrofit with all components)
#and the heating system option (oil boiler, gas boiler, biomass boiler, ground source heat pump, air source heat pump) for a given building. Please note that biomass is constrained in terms of kWh/m2/year depending on community availability.
#Installaion of PV on roofs (max roof area input and constrained), batteries, and thermal storage are also constrained.
#Please note that this optimisation considers grey/embodied emissions of all conversion technologies, storage technologies, and building retrofit materials
#This model is written by Portia Murray adapted from the model from Raphael Wu (10.1016/j.apenergy.2016.12.161)
def retrofithub(Lin_cap_costs,Fixed_cap_costs,Lin_EE,Fixed_EE,CMatrix,STTech,PVTech,GSHPTech,htech,Horizon,Biomass_potential,Roof_area,Bldg_area,ExistingSystem,Retrofit_costs,Retrofit_EE,Loads,Days,PeakLoad,P_solar,inp,inp2,stor,ret,ex_tech,TechStor,TechInp,AnnuityRet,AnnuityStor,AnnuityInput,AnnuityUnderfloor,FIT,Cost_underfloor,Embodied_underfloor,Lifetime_underfloor,Embodied_boreholes,Lifetime_boreholes,gap):
    from docplex.mp.model import Model
    from docplex.util.environment import get_environment
    mdl = Model(name='LCA_retrofithub')
    ##VARIABLE DECLARATION
    mdl.Pin=mdl.continuous_var_matrix(Horizon,inp,lb=0,name='Pin') #Incoming power for conversion technologies
    mdl.P_export=mdl.continuous_var_matrix(Horizon,stor,lb=0,name='P_export') #Energy exported out of the building
    mdl.y=mdl.binary_var_list(inp2,name='y') #Binary value indicating whether or not a technology is installed
    mdl.Capacity=mdl.continuous_var_list(inp2,lb=0,name='Capacity') #Capacity of conversion technologies (in kW)
    mdl.y_retrofit=mdl.binary_var_list(ret,name='y_retrofit') #Binary indicating which retrofit option is installed (no retrofit, roof, facade, window, basement, window-facade, full retrofit). This variable decides which building demands are used.
    mdl.y_underfloor=mdl.binary_var(name='y_underfloor') #Binary indicating the installation of underfloor heating (required for installation of heat pumps in old buildings <1990)
    #Storage
    mdl.Qin=mdl.continuous_var_matrix(Horizon,stor,lb=0,name='Qin') #Hourly charging of energy storages
    mdl.Qout=mdl.continuous_var_matrix(Horizon,stor,lb=0,name='Qout') #Hourly discharging of energy storages
    mdl.E=mdl.continuous_var_matrix(Horizon,stor,lb=0,name='E') #Hour energy levels for energy storage
    mdl.Storage_cap=mdl.continuous_var_list(stor,lb=0,name='Storage_cap') #Capacity of energy storages (in kWh)
    mdl.y_stor=mdl.binary_var_list(stor,name='y_stor') #Binary variable indicating whether or not a storage system is installed
    #Dummy variables
    mdl.dummy=mdl.continuous_var_cube(Horizon,inp,ret,lb=0,name='dummy')#dummy for conversion tech (Represents mdl.Pin*mdl.y_retrofit). This is pushed with the constraints on lines 43-47
    mdl.dummer=mdl.continuous_var_cube(Horizon,stor,ret,lb=0,name='dummer')#dummy for storage (Represents mdl.P_export*mdl.y_retrofit). This is pushed with the constraints on lines 55-60
    mdl.dummy_pv=mdl.continuous_var_matrix(stor,ret,lb=0,name='dummy_pv')#dummy PV variable (Represents Capacity["PV"]*y_retrofit[r]). This is pushed with the constraints on lines 61-65
    mdl.dummy_st=mdl.continuous_var_matrix(stor,ret,lb=0,name='dummy_st')#dummy Storage variable (Represents Capacity["ST"]*y_retrofit[r]). This is pushed with the constraints on lines 66-70
    #Cost objective variables
    mdl.Operating_cost=mdl.continuous_var(lb=0,name='Operating_cost') #Total operating costs for energy carriers used in the building
    mdl.Income_via_exports=mdl.continuous_var(lb=0,name='Income_via_exports') #Profits from selling electricity (feed-in renumeration)
    mdl.Investment_cost_tech=mdl.continuous_var(lb=0,name='Investment_cost_tech') #Investment cost of conversion technologies (PV + heating system)
    mdl.Investment_cost_stor=mdl.continuous_var(lb=0,name='Investment_cost_stor') #Investment cost of storage technologies
    mdl.Investment_cost_ret=mdl.continuous_var(lb=0,name='Inveestment_cost_ret') #Investment cost of retrofit options
    mdl.Total_cost=mdl.continuous_var(lb=0,name='Total_cost') #Total costs to minimize
    #CO2 emissions objective variables
    mdl.Operating_emissions=mdl.continuous_var(lb=0,name='Operating_emissions') #Total CO2 emissions from energy carriers used within the building
    mdl.Embodied_system_emissions=mdl.continuous_var(lb=0,name='Embodied_system_emissions') #Embodied/grey CO2 emissions from conversion technologies (heating system + PV)
    mdl.Embodied_boreholes=mdl.continuous_var(lb=0,name='Embodied_boreholes') #Embodied/grey emissions from boreholes (Only for GSHP)
    mdl.Embodied_storage=mdl.continuous_var(lb=0,name='Embodied_storage') #Embodied/grey emissions from storages (Only if installed)
    mdl.Embodied_retrofit=mdl.continuous_var(lb=0,name='Embodied_retrofit') #Embodied/grey emissions from retrofit materials
    mdl.Embodied_underfloor=mdl.continuous_var(lb=0,name='Embodied_underfloor') #Embodied/grey emissions from underfloor heating (if used)
    mdl.Total_carbon = mdl.continuous_var(lb=0,name='Total_carbon') #Total CO2 emissions to minimize or used in the epsilon constraint
    ##CONSTRAINT DECLARATION
    #Dummy variable constraints (equates Pin[h,i]*y_retrofit[r])
    mdl.add_constraints(mdl.dummy[h,i,r]>=0 for h in Horizon for i in inp for r in ret)
    mdl.add_constraints(mdl.dummy[h,i,r]<=50000*mdl.y_retrofit[r] for h in Horizon for i in inp for r in ret)
    mdl.add_constraints(mdl.Pin[h,i]-mdl.dummy[h,i,r]>=0 for h in Horizon for i in inp for r in ret)
    mdl.add_constraints(mdl.Pin[h,i]-mdl.dummy[h,i,r]<=50000*(1-mdl.y_retrofit[r]) for h in Horizon for i in inp for r in ret)
    #Maximum allowable storage capacities based on available building area
    mdl.add_constraint(mdl.Storage_cap[0]<=Bldg_area/58*1.5)#Hot water storage
    mdl.add_constraint(mdl.Storage_cap[1]<=Bldg_area/122*1.5)#Cold water storage
    mdl.add_constraint(mdl.Storage_cap[2]<=Bldg_area*0.1)#Battery
    #Limit to one space heating system which can be installed
    mdl.add_constraint(mdl.sum(mdl.y[ht] for ht in htech)==1)
    #Dummer variable constraint (equates P_export[h,s]*y_retrofit[r])
    mdl.add_constraints(mdl.dummer[h,s,r]>=0 for h in Horizon for s in stor for r in ret)
    mdl.add_constraints(mdl.dummer[h,s,r]<=50000*mdl.y_retrofit[r] for h in Horizon for s in stor for r in ret)
    mdl.add_constraints(mdl.P_export[h,s]-mdl.dummer[h,s,r]>=0 for h in Horizon for s in stor for r in ret)
    mdl.add_constraints(mdl.P_export[h,s]-mdl.dummer[h,s,r]<=50000*(1-mdl.y_retrofit[r])for h in Horizon for s in stor for r in ret)
    mdl.add_constraints(mdl.P_export[h,s]==0 for h in Horizon for s in stor if s!=2) #Only the electrical energy carrier can be exported from building
    #Dummy PV variable constraints (equates Capacity["PV"]*y_retrofit[r])
    mdl.add_constraints(mdl.dummy_pv[s,r]>=0 for s in stor for r in ret)
    mdl.add_constraints(mdl.dummy_pv[s,r]<=50000*mdl.y_retrofit[r] for r in ret for s in stor)
    mdl.add_constraints(mdl.Capacity[PVTech]-mdl.dummy_pv[s,r]>=0 for r in ret for s in stor)
    mdl.add_constraints(mdl.Capacity[PVTech]-mdl.dummy_pv[s,r]<=50000*(1-mdl.y_retrofit[r])for r in ret for s in stor)
    #Dummy solar thermal variable constraints (equates Capacity["ST"]*y_retrofit[r])
    mdl.add_constraints(mdl.dummy_st[s,r]>=0 for r in ret for s in stor)
    mdl.add_constraints(mdl.dummy_st[s,r]<=50000*mdl.y_retrofit[r] for r in ret for s in stor)
    mdl.add_constraints(mdl.Capacity[STTech]-mdl.dummy_st[s,r]>=0 for r in ret for s in stor)
    mdl.add_constraints(mdl.Capacity[STTech]-mdl.dummy_st[s,r]<=50000*(1-mdl.y_retrofit[r])for r in ret for s in stor)
    #Fixed cost constraint (Binary must equal 1 if the capacity is >0)
    mdl.add_constraints(mdl.Capacity[i]<=50000*mdl.y[i] for i in inp2)
    #Load balance (Total conversion technology production + storage discharge - storage charge = Energy demand + exported energy)
    mdl.add_constraints(mdl.sum(mdl.Pin[h,i]*CMatrix[s,i] for i in inp)+mdl.Qout[h,s]-mdl.Qin[h,s]==mdl.sum(mdl.y_retrofit[r]*Loads[h,s,r] for r in ret)+mdl.P_export[h,s] for s in stor for h in Horizon)
    #Capacity constraint (Total power output of the conversion technology must be less than or equal to the capacity for dispatcable converstion tech, i.e. all except PV)
    mdl.add_constraints(mdl.Pin[h,i]*CMatrix[(s,i)]<=mdl.Capacity[i] for i in inp2 for s in stor for h in Horizon)
    #Solar PV constraint (PV production must equal the solar incidence times the efficiency)
    mdl.add_constraints(mdl.Pin[h,PVTech]==mdl.sum(P_solar[h,r]*mdl.dummy_pv[2,r] for r in ret) for h in Horizon)
    #Solar Storage constraint (Solar thermal production must equal the solar incidence times the efficiency)
    mdl.add_constraints(mdl.Pin[h,STTech]==mdl.sum(P_solar[h,r]*mdl.dummy_st[0,r]for r in ret)for h in Horizon)
    #Max elements (only one heating system can be installed)
    mdl.add_constraints(mdl.sum(mdl.y[d] for d in htech)<=1 for s in stor)
    #Roof area constraints (PV and Solar thermal install area must be less than max area)
    mdl.add_constraint(mdl.Capacity[PVTech]+mdl.Capacity[STTech]<=Roof_area)
    #Storage balance
    for h in Horizon:
        if (h==0) or (h==24) or (h==48) or (h==72) or (h==96) or (h==120) or (h==144) or (h==168) or (h==192) or (h==216): #First hour of the day
            mdl.add_constraints(mdl.E[h,s]==TechStor[s].decay*mdl.E[h+23,s]+TechStor[s].chg_eff*mdl.Qin[h,s]-(1/TechStor[s].dch_eff)*mdl.Qout[h,s] for s in stor)
        else: #All other hours of the day
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
    #Need for underfloor if building is old and ASHP installed. Also ensure that windows are replace if the building is old for ASHP
    mdl.add_constraint(mdl.y_underfloor>=(mdl.sum(mdl.y_retrofit[r] for r in range(0,5))+mdl.y[6]+mdl.y[GSHPTech]-1.5)/2)
    #Existing system size
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
    #Calculate the total cost to be minimized
    mdl.add_constraint(mdl.Investment_cost_tech==mdl.sum((Fixed_cap_costs[(i)]*mdl.y[i]+Lin_cap_costs[(i)]*mdl.Capacity[i])*AnnuityInput[i] for i in inp2))
    mdl.add_constraint(mdl.Investment_cost_stor==mdl.sum((TechStor[s].fixed_cap_costs*mdl.y_stor[s]+TechStor[s].linear_cap_costs*mdl.Storage_cap[s])*AnnuityStor[s] for s in stor))
    mdl.add_constraint(mdl.Investment_cost_ret==mdl.sum((Retrofit_costs[r]*mdl.y_retrofit[r])*AnnuityRet[r] for r in ret)+(AnnuityUnderfloor*Cost_underfloor*mdl.y_underfloor*Bldg_area))
    mdl.add_constraint(mdl.Total_cost==mdl.Investment_cost_tech+mdl.Investment_cost_stor+mdl.Investment_cost_ret+mdl.Operating_cost-mdl.Income_via_exports)
    #Calculate the total CO2 emissions to be minimized constrained (epsilon constraint) for intermediate multi-objective solutions
    mdl.add_constraint(mdl.Embodied_system_emissions==mdl.sum((Lin_EE[(i)]*mdl.Capacity[i]+Fixed_EE[(i)]*mdl.y[i])/TechInp[i].lifetime for i in inp2))
    mdl.add_constraint(mdl.Embodied_storage==mdl.sum((TechStor[s].embodied_linear*mdl.Storage_cap[s]+TechStor[s].embodied_fixed*mdl.y_stor[s])/TechStor[s].lifetime for s in stor))
    mdl.add_constraint(mdl.Embodied_retrofit==mdl.sum(Retrofit_EE[r]*mdl.y_retrofit[r]/40 for r in ret))
    mdl.add_constraint(mdl.Embodied_underfloor==Embodied_underfloor*mdl.y_underfloor*Bldg_area/Lifetime_underfloor)
    mdl.add_constraint(mdl.Embodied_boreholes==mdl.Capacity[GSHPTech]/0.03*Embodied_boreholes/Lifetime_boreholes)
    mdl.add_constraint(mdl.Operating_emissions==mdl.sum(TechInp[i].carbon_factor*Days[h,r]*mdl.dummy[h,i,r] for h in Horizon for i in inp for r in ret))
    mdl.add_constraint(mdl.Total_carbon==mdl.Embodied_system_emissions+mdl.Embodied_storage+mdl.Embodied_retrofit+mdl.Embodied_underfloor+mdl.Embodied_boreholes+mdl.Operating_emissions)
    mdl.parameters.mip.tolerances.mipgap = gap
    return mdl