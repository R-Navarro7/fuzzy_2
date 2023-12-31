from tkinter import *
from utils import *
from PIL import Image, ImageTk
import pandas as pd
import reticulado
import os


class Backward_Chain_System_GUI():
  def __init__(self, alpha=0.7, beta=0.2, gamma=0.85, eps=0.5, bonus = True):
    self.alpha = alpha
    self.beta = beta
    self.gamma = gamma
    self.eps = eps
    self.BH = {}
    self.BR = Base_Reglas()
    self.CH = Conj_Hipotesis(self.BR)
    self.bonus = True
    # Opcional 5.2
    self.marcas = {}

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

    q_bin = ['animal tiene trompa','animal vive en zoológico',
                'animal vive con personas','animal come carne',
                'animal pone huevos' ]
    q_neg = ['animal puede volar', 'animal tiene rayas negras',
              'animal tiene manchas oscuras','animal tiene pezuñas',
              'animal tiene garras', 'animal tiene plumas']
    q_unk = ['animal es parlanchín','animal es doméstico',
            'animal da leche', 'animal tiene piel dura',
            'animal tiene pelo']
    q_range = ['animal vuela bien','animal es feo', 'animal corre rápido',
                'animal tiene cuello largo', 'animal es grande']
    q_conj = ['animal es mamífero', 'animal es ave', 'animal es reptil',
                  'animal es ungulado','animal es carnívoro','animal es rumiante']

    # Obtener tipo de pregunta con trip
    Q = [trip in q_bin,trip in q_neg,trip in q_unk,trip in q_range,trip in q_conj]
    idx = Q.index(True)
    k=1
    if idx == 0:
      question = f'\nEs cierto que el {trip}  ? \
      \nIngrese uno de los siguientes valores según su respuesta: -1:NO | 0: NO SÉ | 1:SI   '

    if idx == 1:
      k = -1
      question = f'\nEs falso que el {trip}  ? \
      \nIngrese uno de los siguientes valores según su respuesta: -1:NO | 0: NO SÉ | 1:SI   '
      
    if idx == 2:
      question = f'¿Usted sabe si el {trip}  ? \
      \nIngrese uno de los siguientes valores según su respuesta: -1:FALSO | 0:NO SÉ | 1:VERDADERO   '

    if idx == 3:
      question = f'¿Que tan {trip.split()[-1]} diría que {trip.split()[-2]} el animal? \
      \nIngrese un valor en el rango [-1,1]: '

    if idx == 4:
      question = f'¿Animal está en el conjunto de tipo {trip.split()[-1]}?  \
      \nIngrese uno de los siguientes valores según su respuesta: -1:NO | 0: NO SÉ | 1:SI   '

    q_var.set(question)
    button.wait_variable(ans_var)
    H = Hecho([trip,k*float(ans_var.get())])
    return H

  def add_to_BH(self,H, marked = False):
    if marked:
      in_BH, vc = self.check_BH(H.trip)
      if in_BH:
        self.BH[H.trip]= disyuncion(H.vc, vc)
      else:
        self.BH[H.trip] = H.vc
    else:
      if abs(H.vc)>=self.beta:
        in_BH, vc = self.check_BH(H.trip)
        if in_BH:
          self.BH[H.trip]= disyuncion(H.vc, vc)
        else:
          self.BH[H.trip] = H.vc
      else: pass

  def check_hipotesis(self, hip):
    rule_id = self.get_rules(hip)[0] # Solo hay una regla que concluya cada hipotesis por lo que esta lista solo tiene 1 elemento
    rule = self.BR[rule_id]
    premisa = rule.premisa
    premisa_vc = self.bonus_check_premisa(premisa)
    hip_conc = propagar(premisa_vc, rule, self.eps)
    print(self.BH)
    if len(hip_conc):
      hip = hip_conc[0] # en este nivel solo puede haber 1 elemento en la conclusion
      self.CH[hip.trip] = hip.vc


  def precalificador(self, premisa):
    for claus in premisa:
      in_BH, vc = self.check_BH(claus)
      if in_BH and vc < -self.beta: # vc menor a beta negativo indica que la info que se tiene es suficiente para estimar el hecho como falso.
        return False
    return True

  def add_to_marks(self, H): # Funcion que marca una clausula si el usuario presenta incertidumbre al llegar al Caso 3.
    if abs(H.vc) < self.beta:
      self.marcas[H.trip] = H.vc
      self.add_to_BH(H, marked=True)

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
              prem_vc =self.bonus_check_premisa(r.premisa)
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
        self.add_to_marks(h)
        premisa_vc.append(h.vc)
    return conjuncion(premisa_vc)

def main_gui():
    AEI = Backward_Chain_System_GUI()

    hipotesis = AEI.CH.keys()

    for h in hipotesis:
        AEI.check_hipotesis(h)
        if AEI.CH[h] >= AEI.alpha:
            print(f'La hipotesis "{h}" ha sido comprobada con un nivel de certeza {AEI.CH[h]}.')
            claus_used = BR[AEI.get_rules(h)[0]].premisa
            hechos_usados = [(claus,AEI.BH[claus]) for claus in claus_used]
            ans = f'El {h} con nivel de certeza {AEI.CH[h]}.\nLos hechos que han permitido esta conclusión han sido:\n{" | ".join([f"{H[0]} con certeza {H[1]}" for H in hechos_usados])}'
            path = f"img/{h.split(' ')[-1]}.jpg"
            final_var.set(ans)
            display_image(path)
            return
    # Si ninguna prediccion supera alfa se toma la con mayor valor de certeza
    vc_max = 0
    h_max = ''
    for h in hipotesis:
        if AEI.CH[h] > vc_max:
            h_max, vc_max = h, AEI.CH[h]
    if vc_max == 0:
        print(f'No se ha podido comprobar ninguna hipotesis con un nivel de certeza mayor a 0')
        ans = f'No se ha podido comprobar ninguna hipotesis con un nivel de certeza mayor a 0'
        path = f"img/sad.jpg"
        final_var.set(ans)
        display_image(path)
        return
    else:
        print(f'La hipotesis "{h_max}" ha sido comprobada con un nivel de certeza {vc_max}.')
        claus_used = BR[AEI.get_rules(h_max)[0]].premisa
        hechos_usados = [(claus,AEI.BH[claus]) for claus in claus_used]
        ans = f'El {h_max} con nivel de certeza {vc_max}.\nLos hechos que han permitido esta conclusión han sido:\n{" | ".join([f"{H[0]} con certeza {H[1]}" for H in hechos_usados])}'
        path = f"img/{h_max.split(' ')[-1]}.jpg"
        final_var.set(ans)
        display_image(path)
        return

import tkinter

def send_value():
	value = scale.get()
	ans_var.set(str(value))
	scale.set(0.00)

def display_image(img_path):
	image = Image.open(img_path)
	image = image.resize((300, 300), Image.ANTIALIAS)
	img = ImageTk.PhotoImage(image)
	photo = Label(master,image=img)
	photo.image = img
	photo.grid(row=7,column=2)

def init_img():
	image = Image.open("img/init.jpg")
	image = image.resize((300, 300), Image.ANTIALIAS)
	img = ImageTk.PhotoImage(image)
	photo = Label(master,image=img)
	photo.image = img
	photo.grid(row=7,column=2)

def show_ret():
  reticulado.show()

def start():
	main_gui()

def restart_aei():
	init_img()
	final_var.set('')
	start()

def exit_programm():
	master.destroy()
	os._exit(0)


master=tkinter.Tk()
master.title("'Guess the Animal :D'")
master.geometry("740x620")

master.protocol('WM_DELETE_WINDOW', exit_programm)

q_var = StringVar()
q_var.set('Presione el boton "Start" para empezar')

ans_var = StringVar()
final_var = StringVar()
final_var.set('')

instrucciones = "Instrucciones: \n \n Conteste las preguntas a continuación indicando el valor de certeza que tenga respecto a cada afirmación.\n  \nRepita lo anterior hasta que el programa indique el animal estimado junto a una imagen y su valor de certeza."

q_label=Label(master, text=instrucciones)
q_label.grid(row=2,column=2)

q_label=Label(master, textvariable=q_var)
q_label.grid(row=4,column=2)

scale=Scale(master, from_=-1.0, to=1.0, resolution=0.01, length=300 , orient=HORIZONTAL)
scale.grid(row=5,column=2)

button=tkinter.Button(master, text="Enviar", command=send_value)
button.grid(row=5,column=3)

frame=tkinter.Frame(master, width=20, height=20)
frame.grid(row=1,column=1)

frame=tkinter.Frame(master, width=20, height=40)
frame.grid(row=3,column=1)

final_label=Label(master, textvariable=final_var)
final_label.grid(row=6,column=2)

init_img()
button_ret=tkinter.Button(master, text="Base de Reglas", command=show_ret)
button_ret.grid(row=1,column=3)
button_r=tkinter.Button(master, text="Reiniciar", command=restart_aei)
button_r.grid(row=8,column=2)
button_r=tkinter.Button(master, text="Salir", command=exit_programm)
button_r.grid(row=8,column=3)

master.after(500, start())
master.mainloop()