from utils import *
import pandas as pd
import gui

class Backward_Chain_System():
  def __init__(self, alpha=0.7, beta=0.2, gamma=0.85, eps=0.5):
    self.alpha = alpha
    self.beta = beta
    self.gamma = gamma
    self.eps = eps
    self.BH = {}
    self.BR = Base_Reglas()
    self.CH = Conj_Hipotesis(self.BR)

    # Opcional 5.2
    self.marcas = {}

    # Opcional 5.5
    self.gui = gui

  def check_BH(self,trip):
    if trip in self.BH.keys():
      vc = self.BH[trip]
      return True, vc

    return False, 0

  def check_CH(self,H):
    reglas_utiles = self.CH[H][1]
    return reglas_utiles

  def get_rules(self, trip):
    R = []
    for rule_id, regla in BR.items():
      for hecho in regla.conc:
        if hecho.trip == trip and abs(hecho.vc) >= self.eps:
          R.append(rule_id)
    return R

  def ask_user(self, trip):
    if self.gui:
      q = f"Cual es el valor de certeza que tiene respecto a la siguiente afirmación: {trip}"
      gui.q_var.set(q)
      gui.button.wait_variable(gui.ans_var)
      vc = float(gui.ans_var.get())
      return vc
    else:
      user_input = input(f'\n Cual es el valor de certeza que tiene respecto a la siguiente afirmación: "{trip}" \n Ingrese un valor en el rango [-1,1]:   ')
      return Hecho([trip,float(user_input)])

  def add_to_BH(self,H):
    if abs(H.vc)>=self.beta:
      in_BH, vc = self.check_BH(H.trip)
      if in_BH:
        self.BH[H.trip]= disyuncion(H.vc, vc)
      else:
        self.BH[H.trip] = H.vc
    else: pass

  def check_premisa(self, premisa):
    premisa_vc = []
    for clause in premisa:
      in_BH, clause_vc = self.check_BH(clause)
      if in_BH:
        continue
      else:
        clause_rules = self.get_rules(clause)
        if len(clause_rules):
          for rule_id in clause_rules:
            gamma_break = False
            r = self.BR[rule_id]
            prem_vc =self.check_premisa(r.premisa)
            conc = propagar(prem_vc, r, self.eps)
            for h in conc:
              if h.vc >= self.gamma and h.trip == clause: gamma_break = True
              self.add_to_BH(h)
            '''
              Se aplica el gamma break para no intentar mejorar mas el Hecho con esta clausula
              TODO: Ver como aplicar el gamma cuando el hecho ya esta en BH (no se si es necesario)
            '''
            if gamma_break: break
        else:
          h = self.ask_user(clause)
          self.add_to_BH(h)

    # Se revisa por ultima vez si la clausula entro a la base de hechos y se rescata su vc, si no se pregunta al usuario
    for clause in premisa:
      in_BH, vc = self.check_BH(clause)
      if in_BH:
        premisa_vc.append(vc)
      else:
        h = self.ask_user(clause)
        self.add_to_BH(h)
        premisa_vc.append(h.vc)
    return conjuncion(premisa_vc)



  def check_hipotesis(self, hip, bonus = False):
    rule_id = self.get_rules(hip)[0] # Solo hay una regla que concluya cada hipotesis por lo que esta lista solo tiene 1 elemento
    rule = self.BR[rule_id]
    premisa = rule.premisa
    if bonus:
      premisa_vc = self.bonus_check_premisa(premisa)
      hip_conc = propagar(premisa_vc, rule, self.eps)
      print(self.BH)
      if len(hip_conc):
        hip = hip_conc[0] # en este nivel solo puede haber 1 elemento en la conclusion
        self.CH[hip.trip] = hip.vc
    else:
      premisa_vc = self.check_premisa(premisa)
      hip_conc = propagar(premisa_vc, rule, self.eps)
      print(self.BH)
      if len(hip_conc):
        hip = hip_conc[0] # en este nivel solo puede haber 1 elemento en la conclusion
        self.CH[hip.trip] = hip.vc


#################### BONUS ##################################
  # 5.1
  def precalificador(self, premisa):
    for claus in premisa:
      in_BH, vc = self.check_BH(claus)
      if in_BH and vc < -self.beta: # vc menor a beta negativo indica que la info que se tiene es suficiente para estimar el hecho como falso.
        return False
    return True

  # 5.2
  def add_to_marks(self, H): # Funcion que marca una clausula si el usuario presenta incertidumbre al llegar al Caso 3.
    if abs(H.vc) < self.beta:
      self.marcas[H.trip] = H.vc

  # 5.3
  def generar_reticulado_BR(self):
    BR = self.BR
    reglas_id = BR.keys()
    premisas = []
    conclusiones = []
    dependencias = []
    tipos= []

    for id in reglas_id:

      regla = BR[id]
      premisas.append(regla.premisa)

      concs = []
      hip = False

      for H in regla.conc:
        concs.append((H.trip,H.vc))
        if H.trip in self.CH.keys():
          hip = True
      conclusiones.append(concs)

      deps = {}
      for clausula in regla.premisa:
        deps[clausula] = self.get_rules(clausula)
      dependencias.append(deps)

      if hip:
        tipos.append('Hipotesis')
      else:
        tipos.append('Conclusion Intermedia')

    BR_dict = {
        'Reglas': reglas_id,
        'Premisa': premisas,
        'Conclusion': conclusiones,
        'Dependencias': dependencias,
        'Tipo': tipos,
    }
    BR_df = pd.DataFrame(BR_dict)
    return BR_df

  def bonus_check_premisa(self, premisa):
    premisa_vc = []
    for clause in premisa:
      in_BH, clause_vc = self.check_BH(clause)
      if in_BH: # Caso 1: se revisa la base de Hechos
        continue
      else: # Caso 2: Se revisa la base de Reglas
        clause_rules = self.get_rules(clause)
        if len(clause_rules):
          for rule_id in clause_rules:
            gamma_break = False
            r = self.BR[rule_id]
            if self.precalificador(r.premisa): # Se aplica el calificador antes de chequear la premisa de las reglas que describen la clausula
              prem_vc =self.check_premisa(r.premisa)
              conc = propagar(prem_vc, r, self.eps)
              for h in conc:
                if h.vc >= self.gamma and h.trip == clause: gamma_break = True
                self.add_to_BH(h)
              '''
                Se aplica el gamma break para no intentar mejorar mas el Hecho con esta clausula
                TODO: Ver como aplicar el gamma cuando el hecho ya esta en BH (no se si es necesario)
              '''
              if gamma_break: break
        else: # Caso 3: Se pregunta al usuario
          if clause in self.marcas.keys(): # Se revisa si esta marcada y si lo esta se ignora
            pass
          else:
            if clause in self.marcas.keys(): pass # No se pregunta si la clausula esta marcada
            else:
              h = self.ask_user(clause)
              self.add_to_BH(h)
              self.add_to_marks(h)

    # Se revisa por ultima vez si la clausula esta en la base de hechos o si esta marcada y se rescata su vc, si no, se pregunta al usuario
    for clause in premisa:
      in_BH, vc = self.check_BH(clause)
      if in_BH:
        premisa_vc.append(vc)
      elif clause in self.marcas.keys():
        premisa_vc.append(self.marcas[clause])
      else:
        h = self.ask_user(clause)
        self.add_to_BH(h)
        premisa_vc.append(h.vc)
    return conjuncion(premisa_vc)
