#!/usr/bin/env python -O
'''
Ce script pour Python s'utilise avec des fichiers de sous-titre au format SRT
Il faut lui fournir en argument quatre temps, avec la syntaxe des sous-titres SRT (01:23:45,678), qui 
correspondent a quatre temps (T0, T0_nouveau, T1, T1_nouveau).
Sur l'entrée standard, le fichier SRT à transformer
La sortie standard, si tout se passe bien, sera identique à l'entree, mais sur tous les temps aura
ete appliquee une fonction affine. 
T0 deviendra T0_nouveau, et T1 deviendra T1_nouveau.
'''

import sys
import re

class Element:
	'''
	Classe utilisée pour représenter un élément de sous titre.
	Dans ce programme, un élément de sous titre est constitué de : 
	- un numéro, (pareil que dans un fichier SRT)
	- une date de début d'affichage
	- une date de fin d'affichage
	- une ou plusieurs lignes de texte
	'''
	def __init__(self, num):
		self.texte = []
		self.debut = None
		self.fin = None
		self.numero = num

def ms(heures, minutes, secondes, millisecondes):
	return millisecondes + (secondes * 1000) + (minutes * 60 * 1000) + (heures * 60 * 60 * 1000)

def format(ms):
	heures = ms / (60 * 60 * 1000);
	ms = ms - heures * 60 * 60 * 1000;
	
	minutes = ms / (60 * 1000)	
	ms = ms - minutes * 60 * 1000;
	
	secondes = ms / 1000;
	ms = ms - secondes * 1000;
	return "%02d:%02d:%02d,%03d" % (heures, minutes, secondes, ms)


def lire_temps(chaine):
	matches = re.findall('(?<!\d)\d{1,3}(?!\d)', chaine)
	if (len(matches) < 4):
		print chaine, " : format incorrect"
		exit(1)
	else:
		#print matches
		return ms(
					int(matches[0]), 
					int(matches[1]), 
					int(matches[2]), 
					int(matches[3]))
					

def calculer_coefficients(x0, y0, x1, y1):
	a = float(y1 - y0) / float(x1 - x0)
	b = y0 - (a * x0)
	return (a, b)

def appliquer_coefficients(a,b,x):
	return int(a * float(x) + b)

(t0_str, t0_nouveau_str, t1_str, t1_nouveau_str) = sys.argv[1:5]
t0         = lire_temps(t0_str)
t0_nouveau = lire_temps(t0_nouveau_str)
t1         = lire_temps(t1_str)
t1_nouveau = lire_temps(t1_nouveau_str)

(a, b) = calculer_coefficients(t0, t0_nouveau, t1, t1_nouveau) 
#print (a,b)


elements = []
element = None
for ligne_brute in sys.stdin:
	ligne = ligne_brute.strip()
	#print "longueur liste : ", len(elements)
	
	match_numero = re.search('^\d+$', ligne)
	if match_numero is not None:
		numero = int(match_numero.group(0)) 
		element = Element(numero)
		elements.append(element)
		continue
	
	match_temps = re.search('^(\d{2}):(\d{2}):(\d{2}),(\d{3})\s+-->\s+(\d{2}):(\d{2}):(\d{2}),(\d{3})$', ligne)
	if match_temps is not None:
		#print match_temps.group(0)
		element.debut = ms(int(match_temps.group(1)), int(match_temps.group(2)), int(match_temps.group(3)), int(match_temps.group(4)))
		element.fin   = ms(int(match_temps.group(5)), int(match_temps.group(6)), int(match_temps.group(7)), int(match_temps.group(8)))
		continue
	
	match_ligne_vide = re.search('^\s*$', ligne)
	if match_ligne_vide is not None:
		#print "Ligne vide au numero", numero, ": ", ligne
		continue
	
	element.texte.append(ligne)



for element in elements:
	print element.numero
	#print str(element.debut)  + " --> " + str(element.fin)
	print format(appliquer_coefficients(a, b, element.debut))  + " --> " + format(appliquer_coefficients(a, b, element.fin))

	for ligne_de_texte in element.texte:
		print ligne_de_texte
	print;
