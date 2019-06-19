def costmin(mdl):
    mdl.minimize(mdl.Total_cost)
    return mdl
def co2min(mdl):
    mdl.minimize(mdl.Total_carbon+0.000001*mdl.Total_cost)
    return mdl
def epmin(mdl,epconst):
    mdl.add_constraint(epconst>=mdl.Total_carbon)
    mdl.minimize(mdl.Total_cost)
    return mdl