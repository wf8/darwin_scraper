#! /usr/bin/python

import requests
import time

letters = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
#letters = ['A']

for letter in letters:
    page = requests.get("http://www2.darwin.edu.ar/Proyectos/FloraArgentina/Especies.asp?Letra=" + letter)
    links = page.text.split("/Proyectos/FloraArgentina/DetalleEspecie.asp?")
    for link in links:
        if link.find("forma=") != -1:
            end = link.find('" title=')
            print(u''.join(("http://www2.darwin.edu.ar/Proyectos/FloraArgentina/DetalleEspecie.asp?", link[:end])).encode('utf-8').strip())
    time.sleep(0.2)
