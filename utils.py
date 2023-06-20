import numpy as np
from tkinter import *
from PIL import Image, ImageTk
import sys
import os

R1 = [
    ['animal tiene pelo'],
    [('animal es mamífero', 0.8),
        ('animal es ave', -1.0),
        ('animal es reptil', -1.0)]
    ]

R2 =[
    ['animal da leche'],
    [('animal es mamífero',1.0),
      ('animal es ave', -1.0),
      ('animal es reptil', -1.0)]
  ]

R3 = [
    ['animal pone huevos','animal tiene piel dura'],
    [('animal es mamífero', -1.0),
      ('animal es ave', -1.0),
      ('animal es reptil', 1.0)]
    ]

R4 = [
    ['animal pone huevos','animal puede volar'],
    [('animal es ave', 1.0),
      ('animal es reptil', -1.0)]
    ]

R5 = [
    ['animal tiene plumas'],
    [('animal es mamífero', -1.0),
      ('animal es ave', 1.0),
      ('animal es reptil',-1.0)]
    ]

R6 = [
    ['animal come carne'],
    [('animal es carnívoro', 1.0)]
    ]

R7 = [
    ['animal tiene garras'],
    [('animal es carnívoro', 0.8)]
    ]

R8 = [
    ['animal es mamífero','animal tiene pezuñas'],
    [('animal es ungulado', 1.0)]
    ]

R9 = [
    ['animal es mamífero','animal es rumiante'],
    [('animal es ungulado', 0.75)]
    ]

R10 = [
    ['animal vive con personas'],
    [('animal es doméstico', 0.9)]
    ]

R11 = [
    ['animal vive en zoológico'],
    [('animal es doméstico', -0.8)]
    ]

R12 = [
    ['animal es mamífero','animal es carnívoro',
      'animal tiene manchas oscuras'],
    [('animal es cheetah', 0.9)]
    ]

R13 = [['animal es mamífero',
        'animal es carnívoro','animal tiene rayas negras'],
      [('animal es tigre', 0.85)]
      ]

R14 = [
    ['animal es mamífero','animal es carnívoro','animal es doméstico'],
    [('animal es perro', 0.9)]
    ]

R15 = [
    ['animal es reptil','animal es doméstico'],
    [('animal es tortuga', 0.7)]
    ]

R16 = [
    ['animal es mamífero','animal es ungulado','animal tiene cuello largo'],
    [('animal es jirafa', 1.0)]
    ]

R17 = [
    ['animal es mamífero','animal es ungulado','animal tiene rayas negras'],
    [('animal es cebra',0.95)]
    ]

R18 = [
    ['animal es mamífero','animal puede volar','animal es feo'],
    [('animal es murcielago', 0.9)]
    ]

R19 = [
    ['animal es ave','animal vuela bien'],
    [('animal es gaviota', 0.9)]
    ]

R20 = [
    ['animal es ave','animal corre rápido'],
    [('animal es avestruz', 1.0)]
    ]

R21 = [
    ['animal es ave','animal es parlanchín'],
    [('animal es loro', 0.95)]
    ]

R22 = [
    ['animal es mamífero','animal es grande',
      'animal es ungulado','animal tiene trompa'],
    [('animal es elefante', 0.9)]
    ]

Rules = [R1,R2,R3,R4,R5,R6,R7,R8,R9,R10,R11,R12,R13,R14,R15,R16,R17,R18,R19,R20,R21,R22]

class Hecho():
  ''' Incluye triplete y valor de certeza
  tripl = "animal es/tiene <característica>", type(str)
  vc = float in [-1,1]
  '''
  def __init__(self,H):
    self.trip = H[0]
    self.vc = H[1]

  def __str__(self):
      return "accion is '% s', vc is % s" % (self.trip, self.vc)

class Regla():
  '''Recibe lista con primer elemento premisa y segundo elemento conclusion
  Premisa = [clausula_1, clasula_2, ...] ; clausula -> type(str)
  Conclusion = [accion_1, accion_2, ...] ; accion es tipo Hecho -> (trip, vc)
  Evaluar usar numpy por eficiencia
  '''
  def __init__(self,Rule):
    self.premisa = Rule[0]
    self.conc = []
    for accion in Rule[1]:
      self.conc.append(Hecho(accion))

  def __str__(self):
      return "Premisas: '% s'; Conclusion: % s" \
      % (self.premisa, [(x.trip,x.vc) for x in self.conc])


def Base_Reglas(Rules=Rules):
  '''Genera base de reglas a partir de lista de Reglas'''
  BR = {}
  for k,R in enumerate(Rules):
    BR['R'+str(k+1)] = Regla(R)
  return BR


def Conj_Hipotesis(BR):
  '''Retorna dict de conjunto de Hipótesis
  TODO: Incluir R(H) dado un eps
  '''

  animals = ['tigre','cheetah','perro','elefante','jirafa','cebra',
                  'murciélago','tortuga', 'gaviota','loro', 'avestruz']
  CH = {}
  for animal in animals:
    H = "animal es " + animal
    CH[H] = 0
  return CH

BR = Base_Reglas()
hip = Conj_Hipotesis(BR=BR)

def conjuncion(premisa_vc):
  '''min_mod: retorna vc de premisa, elegido como el item con min valor abs'''
  # p_abs = np.array([abs(claus_vc) for claus_vc in premisa_vc])
  # max_idx = np.argmin(p_abs)
  # return premisa_vc[max_idx]
  return min(premisa_vc)


def disyuncion(vc, vc_h):
  '''max_mod: retorna vc de premisa, elegido como el item con max valor abs'''
  vc_list = np.array([vc, vc_h])
  max_idx = np.argmax(vc_list)
  return vc_list[max_idx]

def propagar(vc, Rule, eps):
  '''Recibe vc de premisa agregada y regla
  TODO: revisar si conviene entregar 2 listas de H y vc por separado
  '''
  output = []

  for idx, hecho in enumerate(Rule.conc):
    delta = 0.2/hecho.vc
    if abs(hecho.vc) >= eps and abs(vc) >= delta:
      trig = True
      output.append(Hecho([hecho.trip, vc*hecho.vc]))
  return output

