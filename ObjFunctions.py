#Single objective cost minimization
def costmin(mdl):
    mdl.minimize(mdl.Total_cost)
    return mdl
#Single objective CO2 minimization (total cost still considered so that technologies aren't installed in massive capacities)
def co2min(mdl):
    mdl.minimize(mdl.Total_carbon+0.000001*mdl.Total_cost)
    return mdl
#Multi-objective epsilon constraint for intermediate solutions
def epmin(mdl,epconst):
    mdl.add_constraint(epconst>=mdl.Total_carbon)
    mdl.minimize(mdl.Total_cost)
    return mdl