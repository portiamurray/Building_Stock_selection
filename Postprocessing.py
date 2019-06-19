def ReturnSolutions(b,RetrofitS,SystemS,Costs,Emissions,e,m):
    Costs[b].loc[e,'Total_cost']=m.Total_cost.solution_value
    Costs[b].loc[e,'Inv_systems']=m.Investment_cost_tech.solution_value
    Costs[b].loc[e,'Inv_stor']=m.Investment_cost_stor.solution_value
    Costs[b].loc[e,'Inv_ret']=m.Investment_cost_ret.solution_value
    Costs[b].loc[e,'FIT_profit']=m.Income_via_exports.solution_value
    Costs[b].loc[e,'Ops']=m.Operating_cost.solution_value
    Emissions[b].loc[e,'Total_carbon']=m.Total_carbon.solution_value
    Emissions[b].loc[e,'Ops']=m.Operating_emissions.solution_value
    Emissions[b].loc[e,'EE_systems']=m.Embodied_system_emissions.solution_value
    Emissions[b].loc[e,'EE_boreholes']=m.Embodied_boreholes.solution_value
    Emissions[b].loc[e,'EE_stor']=m.Embodied_storage.solution_value
    Emissions[b].loc[e,'EE_ret']=m.Embodied_retrofit.solution_value
    Emissions[b].loc[e,'EE_underfloor']=m.Embodied_underfloor.solution_value
    RetrofitS[b].loc[e,'y_no_retrofit']=m.y_retrofit[0].solution_value
    RetrofitS[b].loc[e,'y_roof_retrofit']=m.y_retrofit[1].solution_value
    RetrofitS[b].loc[e,'y_ground_retrofit']=m.y_retrofit[2].solution_value
    RetrofitS[b].loc[e,'y_wall_retrofit']=m.y_retrofit[3].solution_value
    RetrofitS[b].loc[e,'y_win_retrofit']=m.y_retrofit[4].solution_value
    RetrofitS[b].loc[e,'y_winwall_retrofit']=m.y_retrofit[5].solution_value
    RetrofitS[b].loc[e,'y_full_retrofit']=m.y_retrofit[6].solution_value
    SystemS[b].loc[e,'Capacity_Heat_Oil_Boiler']=m.Capacity[9].solution_value
    SystemS[b].loc[e,'Capacity_Heat_Gas_Boiler']=m.Capacity[8].solution_value
    SystemS[b].loc[e,'Capacity_Heat_Bio_Boiler']=m.Capacity[10].solution_value
    SystemS[b].loc[e,'Capacity_Heat_ASHP']=m.Capacity[6].solution_value
    SystemS[b].loc[e,'Capacity_Heat_GSHP']=m.Capacity[7].solution_value
    SystemS[b].loc[e,'Capacity_MGT']=m.Capacity[11].solution_value
    SystemS[b].loc[e,'Capacity_Chiller']=m.Capacity[12].solution_value
    SystemS[b].loc[e,'Capacity_Elec_PV']=m.Capacity[PVTech].solution_value
    SystemS[b].loc[e,'Capacity_Heat_ST']=m.Capacity[STTech].solution_value
    SystemS[b].loc[e,'Storage_cap_Heat']=m.Storage_cap[0].solution_value
    SystemS[b].loc[e,'Storage_cap_Cool']=m.Storage_cap[1].solution_value
    SystemS[b].loc[e,'Storage_cap_Elec']=m.Storage_cap[2].solution_value
    SystemS[b].loc[e,'Heat_Gas_B_ex']=m.Capacity[1].solution_value
    SystemS[b].loc[e,'Heat_Oil_B_ex']=m.Capacity[2].solution_value
    SystemS[b].loc[e,'Heat_Bio_B_ex']=m.Capacity[3].solution_value
    SystemS[b].loc[e,'Heat_DH_ex']=m.Capacity[4].solution_value
    SystemS[b].loc[e,'Heat_El_ex']=m.Capacity[5].solution_value
    SystemS[b].loc[e,'Heat_HP_ex']=m.Capacity[0].solution_value
    SystemS[b].loc[e,'Underfloor']=m.y_underfloor.solution_value
    return [RetrofitS,SystemS,Costs,Emissions]

def writer(l,writepath,SystemS,RetrofitS,Emissions,Costs):
    import pandas as pd
    writer = pd.ExcelWriter(writepath, engine='xlsxwriter')
    # Write each dataframe to a different worksheet.
    SystemS[l].to_excel(writer, sheet_name='System_selection')
    RetrofitS[l].to_excel(writer, sheet_name='Retrofit_System')
    Emissions[l].to_excel(writer, sheet_name='Emissions')
    Costs[l].to_excel(writer, sheet_name='Costs')
    return