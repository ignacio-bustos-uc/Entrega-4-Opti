from gurobipy import Model, GRB, quicksum
import pandas as pd

# Conjuntos
# Ubicaciones de las fuentes de agua existentes
# id_fuente, id_comuna
fuentes_df = pd.read_csv('data/fuentes_existentes_por_comuna.csv') # Ready
E = fuentes_df['id_fuente'].tolist()

# Posibles ubicaciones para instalar generadores
# id_ubicacion, id_comuna
ubicaciones_df = pd.read_csv('data/ubicaciones_por_comuna.csv')
S = ubicaciones_df['id_ubicacion'].tolist()

# Tipos de generadores
# id_generador, id_tipo, nombre_generador
generadores_df = pd.read_csv('data/generadores.csv')
G = generadores_df['id_generador'].tolist()
generator_capacity = generadores_df.set_index('id_generador')['capacidad'].to_dict()

# Comunas
# id_comuna, nombre_comuna
comunas_df = pd.read_csv('data/comunas.csv')
C = comunas_df['id_comuna'].tolist()

# Parameters

# Demanda de agua en cada fuente (litros)
# id_fuente, demanda_agua
# Esto se podria calcular con una binomial segun la cantidad de gente en la comuna
H_e = fuentes_df.set_index('id_fuente')['demanda_agua'].to_dict()


# Energia requerida por litro en cada ubicacion (kW/litro)
# id_fuente, energia_requerida
energia_df = pd.read_csv('data/fuentes_energia_por_litro.csv')
C_e = energia_df.set_index('id_fuente')['energia_por_litro'].to_dict()

# Capacidad en kW del generador g en la ubicacion s
# id_generador, id_ubicacion, capacidad
capacidades_df = pd.read_csv('data/generador_capacidades_por_ubicacion.csv')
J_gs = {(row['id_generador'], row['id_ubicacion']): row['capacidad'] for _, row in capacidades_df.iterrows()}

# Si fuera constante
# J_gs = {(g, s): generator_capacity[g] for g in G for s in S}

# Maxima cantidad de generadores que se pueden instalar en la region
W = 50

# Maximo numero de generadores de tipo g que se pueden instalar en la comuna c
max_generators_df = pd.read_csv('data/max_generadores_por_tipo_por_comuna.csv')
Z_gc = {(row['id_generador'], row['id_comuna']): row['max_generators'] for _, row in max_generators_df.iterrows()}

# Costo de instalar un generador (pesos)
Q = 100000

# Presupuesto total para la instalacion de generadores (pesos)
P = 100000000

# Numero suficientemente grande
M1 = 1e6

# Fraccion minima de la demanda de agua que debe ser satisfecha
alpha = 0.0001

# Fraccion minima de eficiencia que debe ser satisfecha
beta = 0.1

# Parametro binario: 1 si la fuente de agua e esta en la comuna c
# id_fuente, id_comuna
delta_ec = {(row['id_fuente'], row['id_comuna']): 1 for _, row in fuentes_df.iterrows()}
# Seteamos 0 para las combinaciones que no existen
for e in E:
    for c in C:
        if (e, c) not in delta_ec:
            delta_ec[(e, c)] = 0

# Parametro binario: 1 si la ubicacion s esta en la comuna c
# id_ubicacion, id_comuna
epsilon_sc = {(row['id_ubicacion'], row['id_comuna']): 1 for _, row in ubicaciones_df.iterrows()}
# Seteamos 0 para las combinaciones que no existen
for s in S:
    for c in C:
        if (s, c) not in epsilon_sc:
            epsilon_sc[(s, c)] = 0

# Distribucion del presupuesto por comuna
total_population = comunas_df['poblacion'].sum()
comunas_df['proporcion_poblacion'] = comunas_df['poblacion'] / total_population
comunas_df['presupuesto'] = comunas_df['proporcion_poblacion'] * P
P_Cc = dict(zip(comunas_df['id_comuna'], comunas_df['presupuesto']))

model = Model('Generator_Installation')

# Variables de decision
A_egs = model.addVars(E, G, S, lb=0, ub=1, vtype=GRB.CONTINUOUS, name='A_egs')
X_gs = model.addVars(G, S, vtype=GRB.BINARY, name='X_gs')

model.setObjective(
    quicksum(A_egs[e, g, s] * H_e[e] for e in E for g in G for s in S),
    GRB.MAXIMIZE
)

# Restricciones

# 1 Limites en el numero total de generadores instalados
model.addConstr(
    quicksum(X_gs[g, s] for g in G for s in S) <= W,
    'MaxGenerators'
)

# 2. Restricciones de capacidad del generador
for s in S:
    lhs = quicksum(A_egs[e, g, s] * H_e[e] * C_e[e] for e in E for g in G)
    rhs = quicksum(J_gs[g, s] * X_gs[g, s] for g in G)
    model.addConstr(lhs <= rhs, name=f"Energy_Capacity_at_Location_{s}")

# 3. Restricciones de presupuesto por comuna
for c in C:
    lhs = quicksum(Q * X_gs[g, s] * epsilon_sc[s, c] for g in G for s in S)
    rhs = P_Cc[c]
    model.addConstr(lhs <= rhs, name=f"Budget_Constraint_Commune_{c}")

# 4. Cada comuna debe tener al menos un generador
for c in C:
    lhs = quicksum(epsilon_sc[s, c] * X_gs[g, s] for g in G for s in S)
    model.addConstr(lhs >= 1, name=f"Min_Generators_Commune_{c}")

# 5. Minima cobertura de demanda de agua por fuente
for e in E:
    for c in C:
        if delta_ec[e, c] == 1:
            lhs = quicksum(epsilon_sc[s, c] * A_egs[e, g, s] for g in G for s in S)
            model.addConstr(lhs >= alpha, name=f"Demand_Coverage_Source_{e}_Commune_{c}")

# 6. Asignar fracciones solo si el generador esta instalado
for e in E:
    for g in G:
        for s in S:
            model.addConstr(A_egs[e, g, s] <= M1 * X_gs[g, s], name=f"A_Assignment_{e}_{g}_{s}")

# 7. Limites en el numero de generadores de un tipo en una comuna
for c in C:
    for g in G:
        lhs = quicksum(epsilon_sc[s, c] * X_gs[g, s] for s in S)
        rhs = Z_gc[g, c]
        model.addConstr(lhs <= rhs, name=f"Max_Generators_Type_{g}_Commune_{c}")

# 9. Criterio de factibilidad
for s in S:
    for g in G:
        lhs = quicksum(A_egs[e, g, s] * H_e[e] * C_e[e] for e in E)
        rhs = beta * J_gs[g, s] * X_gs[g, s]
        model.addConstr(lhs >= rhs, name=f"Feasibility_Criterion_{g}_{s}")


model.optimize()

if model.status == GRB.INFEASIBLE:
    print('Model is infeasible.')
    model.computeIIS()
    model.write("model.ilp")

elif model.status == GRB.OPTIMAL:
    print(f'Optimal Objective Value: {model.objVal}')
    # Generadores instalados
    for g in G:
        for s in S:
            if X_gs[g, s].X > 0.5:
                print(f'Generator type {g} installed at location {s}')
    for e in E:
        total_coverage = sum(A_egs[e, g, s].X for g in G for s in S)
        print(f"Source {e}: {total_coverage * 100:.2f}% of demand covered")
else:
    print('No optimal solution found.')
