#! /usr/bin/python
# -*- coding: utf-8 -*-

import codecs
import requests
import time
import sys

#links = ['http://www2.darwin.edu.ar/Proyectos/FloraArgentina/DetalleEspecie.asp?forma=&variedad=&subespecie=&especie=grandifolium&genero=Abutilon&espcod=15928',
#         'http://www2.darwin.edu.ar/Proyectos/FloraArgentina/DetalleEspecie.asp?forma=&variedad=&subespecie=&especie=weddelliana&genero=Aa&espcod=23894']

links = []
num_links = 0
with open('species_links.txt') as f:
    for line in f:
        links.append(line)
        num_links += 1

output_file = "darwinion_accepted_species.csv"
file = codecs.open(output_file, "w", "utf-8")
file.write(u'"Familia","Género","Especie","Sigla sp.","Subespecie","Sigla ssp.","Variedad","Sigla var.","Forma","Sigla f.","Publicado en","Volumen","Páginas","Año","Hábito","Status","Elevación (m s.m.)","Distribución Argentina","Distribución Misiones","Paises limítrofes","Distribución Brasil","Distribución Chile","Distribución Paraguay","Distribución Uruguay","Notas","Sinónimos"\n')
file.close()

def get_content(key, source):
    '''
    Parse a keyword from the html source
    '''
    if source.find(key) != -1:
        start = source.find(key)
        end = source.find('</td>', start + len(key))
        return u''.join(('"',source[start:end].replace(key, '').strip(),'"'))
    else:
        return ''

def get_synonyms(source):
    '''
    Parse the synonyms
    '''
    key = u'Sinónimos: </strong>'
    if source.find(key) != -1:
        start = source.find(key)
        end = source.find('</td>', start + len(key))
        synonyms = source[start:end].replace(key, '').strip()
        synonyms = synonyms.replace('</a>', '')
        synonyms_list = synonyms.split('<a href="')
        synonyms_list_no_anchors = []
        for synonym in synonyms_list:
            end_anchor = synonym.find('">') + 2
            syn = synonym[end_anchor:].strip()
            syn = syn.replace(', hom. illeg.', '')
            syn = syn.replace(',', '')
            syn = syn.replace('  ', ' ')
            if syn.strip() != '':
                synonyms_list_no_anchors.append(syn)
        synonyms = u','.join(synonyms_list_no_anchors)
        return u''.join(('"',synonyms,'"'))
    else:
        return ''

def prep_genbank_mining(row):
    '''
    Generate a list of species for MatrixMaker genbank mining
    '''
    if row[21] != '':
        accepted_binomial = u' '.join((row[1], row[2])) 
        file = codecs.open('gb_species.csv', 'a', 'utf-8')
        file.write(u','.join((accepted_binomial, row[25], '\n')).replace('"',''))
        file.close()


def get_data(link):
    '''
    Scrape the data for this species.
    '''
    try:
        page = requests.get(link)
        page.encoding = 'utf-8'
        source = page.text
        keys = [u'Familia</td><td width = "65%">',u'Género</td><td width="65%">',u'Especie</td><td width = "65%">',u'Sigla sp.</td><td width = "65%">',
                u'Subespecie</td><td width = "65%">',u'Sigla ssp.</td><td width = "65%">',u'Variedad</td><td width = "65%">',u'Sigla var.</td><td width = "65%">',
                u'Forma</td><td width = "65%">',
                u'Sigla f.</td><td width = "65%">',u'Publicado en</td><td width = "65%">',u'Volumen</td><td width = "65%">',u'Páginas</td><td width = "65%">',
                u'Año</td><td width = "65%">',
                u'Hábito</td><td width = "65%">',u'Status</td><td width = "65%">',u'Elevación (m s.m.)</td><td width = "65%">',u'Distribución Argentina</td><td width = "65%">',
                u'Distribución Misiones</td><td width = "65%" class=cuerpo>',u'Paises limítrofes</td><td width = "65%">',u'Distribución Brasil</td><td width = "75%" class=cuerpo>',
                u'Distribución Chile</td><td width = "65%" class=cuerpo>',u'Distribución Paraguay</td><td width = "65%" class=cuerpo>',
                u'Distribución Uruguay</td><td width = "65%" class=cuerpo>',u'Notas</td><td width = "65%">']
        row = []
        for key in keys:
            row.append(get_content(key, source))
        row.append(get_synonyms(source))
        row.append(u'\n')

        prep_genbank_mining(row) 
        file = codecs.open(output_file, "a", "utf-8")
        file.write(u','.join(row)) 
        file.close()
        # dont overload server
        time.sleep(0.2)

    except Exception as e:
        # need to retry
        time.sleep(0.5)
        get_data(link)


i = 1
for link in links:
    percent = str(round(100 * i/float(num_links), 2))
    sys.stdout.write('\r' + 'Completed: ' + str(i) + '/' + str(num_links) + ' (' + percent + '%)')
    sys.stdout.flush()
    get_data(link)
    i += 1
    #if i == 20:
    #     print('\nDone.')
    #     sys.exit(0)
print('\nDone.')
