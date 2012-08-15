#!/usr/bin/env python -O
# -*- coding: utf-8 -*-

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
	'''
	Convertit une date en heures + minutes + secondes + millisecondes
	en une date en millisecondes uniquement
	'''
	return millisecondes + (secondes * 1000) + (minutes * 60 * 1000) + (heures * 60 * 60 * 1000)


def format(ms):
	'''
	Calcule et renvoie une chaîne de caractères formatée à partir d'une date en millisecondes
	La chaîne renvoyée sera du type : 01:23:45,678
	'''
	heures = ms / (60 * 60 * 1000);
	ms = ms - heures * 60 * 60 * 1000;
	
	minutes = ms / (60 * 1000)	
	ms = ms - minutes * 60 * 1000;
	
	secondes = ms / 1000;
	ms = ms - secondes * 1000;
	return "%02d:%02d:%02d,%03d" % (heures, minutes, secondes, ms)


def lire_temps(chaine):
	'''
	Lire un temps depuis la chaine passée en paramètre
	Le temps est recherché selon la forme 01:23:45,678
	De nombreuses variantes de cette forme sont acceptées

	La fonction renvoie une date en millisecondes
	'''
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
	'''
	A partir de deux points (x0,y0) et (x1,y1) calculer les coefficients a et b tels que :
	
	y0 = a*x0 + b
	ET
	y1 = a*x1 + b


        |                      y = ax+b   +
        |                              +
      y1|---------------------------+ 
        |                        +  |`
        |          (x0,y0)    +     | `
        |              `   +        |(x1,y1)
      y0|---------------+           | 
        |            +  |           |
        |         +     |           |
	+-----------------------------------------------
	                x0         x1
	'''
	a = float(y1 - y0) / float(x1 - x0)
	b = y0 - (a * x0)
	return (a, b)


def appliquer_coefficients(a,b,x):
	'''
	Applique à un argument x la fonction affine f: z-> a*z+b 
	Retourne le résulat
	'''
	return int(a * float(x) + b)


def main():
	'''
	Fonction principale. 
	Lit les arguments depuis la ligne de commande : 4 dates
	Calcule les coefficients
	Parcourt toutes les lignes du fichier d'entrée pour créer une listes d'objets Element
	Applique les transformations sur tous les temps de toutes les entrées, et affiche les
	entrées transformées sur la sortie standard
	'''

	# Récupération des arguments de la ligne de commande : quatre 
	# temps (T0, T0', T1, T1') 

	(t0, t0_nouveau, t1, t1_nouveau) = [lire_temps(temps) for temps in sys.argv[1:5]]

	# Calcul des coefficients de la transformation affine à appliquer
	(a, b) = calculer_coefficients(t0, t0_nouveau, t1, t1_nouveau) 

	# Parcours du texte, fourni sur l'entrée standard du programme
	# On produit une liste d'Elements de sous-titre
	elements = []

	# Cette variable contient une référence vers l'élément en cours de création.
	# Elle est remplacée dès qu'un nouvel élément est trouvé
	element = None
	
	for ligne_brute in sys.stdin:

		# Suppression des blancs en début et en fin de chaîne	
		ligne = ligne_brute.strip()
		
		# La ligne est peut-être constituée d'un numéro
		match_numero = re.search('^\d+$', ligne)
		if match_numero is not None:

			# Dans ce cas, on crée un nouvel élément dans la liste, marqué avec ce numéro
			numero = int(match_numero.group(0)) 
			element = Element(numero)
			elements.append(element)
			
			# On peut passer à la ligne suivante
			continue
		

		# Sinon, la ligne est peut-être formée de deux temps de sous-titre, séparés par une flèche
		match_temps = re.search('^(\d{2}):(\d{2}):(\d{2}),(\d{3})\s+-->\s+(\d{2}):(\d{2}):(\d{2}),(\d{3})$', ligne)
		if match_temps is not None:
			# Dans ce cas, on modifie le dernier élément qui a été instancié, et on affecte
			# ses attributs  *debut* et *fin*  avec les valeurs qui ont été trouvées
			element.debut = ms(int(match_temps.group(1)), int(match_temps.group(2)), int(match_temps.group(3)), int(match_temps.group(4)))
			element.fin   = ms(int(match_temps.group(5)), int(match_temps.group(6)), int(match_temps.group(7)), int(match_temps.group(8)))

			# Après ça on peut passer à la ligne suivante
			continue
		

		# Sinon, la ligne est peut-être une ligne vide
		match_ligne_vide = re.search('^\s*$', ligne)
		if match_ligne_vide is not None:

			# Dans ce cas on ne fait rien et on passe à la ligne suivante
			continue
		
		# Enfin, si la ligne courante n'est ni un numéro, ni un temps, ni une ligne vide, alors il 
		# doit s'agir d'une ligne de texte.
		# On ajoute donc ce texte à l'élément en cours de création
		element.texte.append(ligne)

	# L'entrée standard est terminée, tous les éléments ont été créés.

	for element in elements:
		print element.numero
		#print str(element.debut)  + " --> " + str(element.fin)
		print format(appliquer_coefficients(a, b, element.debut))  + " --> " + format(appliquer_coefficients(a, b, element.fin))

		for ligne_de_texte in element.texte:
			print ligne_de_texte
		print;

'''
Si ce script est lancé par l'interpréteur, et non inclus en tant que module, 
on exécute la fonction main()
'''
if __name__ == '__main__':
	main()
