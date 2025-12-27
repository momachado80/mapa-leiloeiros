#!/usr/bin/env python3
"""
Processa a lista atual de leiloeiros (55 registros)
"""
import json
import pandas as pd
from pathlib import Path
import re

# Dados dos leiloeiros (55 registros completos)
leiloeiros = [
    {"nome": "ADEMILSON CESAR TEIXEIRA", "matricula": "1165", "cidade": "ARAÇATUBA", "site": None, "email": "ademilsonct@gmail.com", "telefone": "(18)99136-8689"},
    {"nome": "ADILSON HENRIQUE VASCONCELOS", "matricula": "1212", "cidade": "SÃO PAULO", "site": None, "email": "ahvvasconcelos@gmail.com", "telefone": "(11)97373-5950"},
    {"nome": "ADRIANA RODRIGUES CONRADO", "matricula": "1051", "cidade": "PROMISSÃO", "site": None, "email": "adrianarodriguesconrado@gmail.com", "telefone": "(14)99679-3708"},
    {"nome": "ADRIANO MAZANATTI", "matricula": "622", "cidade": "ASSIS", "site": None, "email": "adriano_mazanatti@yahoo.com.br", "telefone": "(18)3322-6519"},
    {"nome": "ADRIANO PIOVEZAN FONTE", "matricula": "1325", "cidade": "GUARUJÁ", "site": "www.lancejudicial.com.br", "email": "contato@lancejudicial.com.br", "telefone": "(13)3384-8000"},
    {"nome": "ADRIANO ROCHA NEVES", "matricula": "696", "cidade": "SÃO PAULO", "site": "www.rocha.lel.br", "email": "contato@rocha.lel.br", "telefone": "(11)2548-0002"},
    {"nome": "ADRIANO TESSARINI DE CARVALHO", "matricula": "770", "cidade": "SÃO PAULO", "site": None, "email": None, "telefone": "(11)5586-3010"},
    {"nome": "ADRIANO VASCONCELOS", "matricula": "1288", "cidade": "FRANCA", "site": None, "email": "borgesleiloes@hotmail.com", "telefone": "(16)3025-2800"},
    {"nome": "AEDI DE ANDRADE VERRONE", "matricula": "840", "cidade": "SÃO PAULO", "site": "www.lanceleiloes.com", "email": "lanceleiloes@lancelelloes.com", "telefone": "(11)5811-0730"},
    {"nome": "AFONSO MARANGONI", "matricula": "1357", "cidade": "SÃO PAULO", "site": "www.owadv.com.br", "email": "angelo@owadv.com.br", "telefone": "(41)99865-4489"},
    {"nome": "AGATHA JOCELYN VILAS BOAS", "matricula": "1028", "cidade": "SÃO PAULO", "site": None, "email": "agatha.leiloeiraoficial@gmail.com", "telefone": "(11)5513-3872"},
    {"nome": "AGNALDO JOSÉ DE MELO", "matricula": "1306", "cidade": "ASSIS", "site": None, "email": "forca_livre@hotmail.com", "telefone": "(18)99629-4343"},
    {"nome": "AHMAD SAID MOURAD", "matricula": "1084", "cidade": "SÃO PAULO", "site": None, "email": "DEPSAID@GMAIL.COM", "telefone": "(11)99642-1016"},
    {"nome": "AHMID HUSSEIN IBRAHIN TAHA", "matricula": "1013", "cidade": "SÃO PAULO", "site": "www.tahaleiloes.com.br", "email": "ahmid@tahaleiloes.com.br", "telefone": "(11)99906-3223"},
    {"nome": "ALBERTO JOSE MARCHI MACEDO", "matricula": "978", "cidade": "SÃO PAULO", "site": "www.albertomacedoleiloes.com.br", "email": "alberto@albertomacedoleiloes.com.br", "telefone": "(11)3227-4101"},
    {"nome": "ALESSANDRA CRISTHINA MACEDO DE FREITAS", "matricula": "668", "cidade": "SÃO PAULO", "site": "www.freitasleiloeiro.com.br", "email": "ale.macedo@freitasleiloeiro.com.br", "telefone": "(11)3117-1000"},
    {"nome": "ALESSANDRO DE ASSIS TEIXEIRA", "matricula": "1264", "cidade": "POÇOS DE CALDAS", "site": "www.leiloesjudiciaismg.com.br", "email": "contato@leiloesjudiciaismg.com.br", "telefone": "(35)99228-1011"},
    {"nome": "ALESSANDRO FERRARI", "matricula": "1219", "cidade": "ARARAQUARA", "site": None, "email": "arquiteto_ferrari@gmail.com", "telefone": "(16)99961-7100"},
    {"nome": "ALETHEA CARVALHO LOPES", "matricula": "899", "cidade": "SÃO PAULO", "site": "www.vivaleiloes.com.br", "email": "alethea@vivaleiloes.com.br", "telefone": "(11)3957-7717"},
    {"nome": "ALEXANDRE TRAVASSOS", "matricula": "951", "cidade": "SÃO PAULO", "site": "www.majudicial.com", "email": "alexandre.travassos@majudicial.com", "telefone": "(11)99816-4206"},
    {"nome": "ALEXIA DE OLIVEIRA SILVA", "matricula": "1286", "cidade": "SÃO PAULO", "site": None, "email": "alexiaoliveiras@gmail.com", "telefone": "(11)96453-1995"},
    {"nome": "ALEXIA VILAS BOAS DE ANDRADE", "matricula": "1326", "cidade": "SÃO PAULO", "site": "www.outlook.com", "email": "villasboas.alexia@outlook.com", "telefone": "(11)96447-6512"},
    {"nome": "ALEXSANDRO BATISTA", "matricula": "1097", "cidade": "CAMPINAS", "site": "www.batistaleiloes.com.br", "email": "atendimento@batistaleiloes.com.br", "telefone": "(19)3263-4884"},
    {"nome": "ALFIO CARLOS AFFONSO ZALLI NETO", "matricula": "1066", "cidade": "SÃO PAULO", "site": "www.tezaleiloes.com.br", "email": "contato@tezaleiloes.com.br", "telefone": "(11)2323-3353"},
    {"nome": "ALINE SOUZA FLORES", "matricula": "1218", "cidade": "SÃO PAULO", "site": None, "email": "alineflores@hotmail.com", "telefone": "(11)97336-2300"},
    {"nome": "ALOISIO CRAVO CARDOSO", "matricula": "387", "cidade": "SÃO PAULO", "site": "www.aloisiocravo.com.br", "email": "aloisiocravo@aloisiocravo.com.br", "telefone": "(11)3088-7142"},
    {"nome": "ALOISIO LAHYRE DE MAGALHAES", "matricula": "461", "cidade": "SÃO PAULO", "site": None, "email": None, "telefone": "(11)2088-4287"},
    {"nome": "ALVARO MENDES DA SILVA JUNIOR", "matricula": "1210", "cidade": "SÃO PAULO", "site": None, "email": "all_vinho@hotmail.com", "telefone": "(11)99947-7561"},
    {"nome": "AMANDA FIGUEIREDO PAULELLA", "matricula": "1200", "cidade": "SÃO PAULO", "site": "www.outlook.com", "email": "afigueiredop@outlook.com", "telefone": "(11)93939-9049"},
    {"nome": "AMANDA PRISCILA PENA CREPALDI", "matricula": "1001", "cidade": "BAURU", "site": None, "email": "amandacrepaldirp@hotmail.com", "telefone": "(14)99820-9539"},
    {"nome": "AMANDA PEREIRA TOMAZELLI", "matricula": "1115", "cidade": "SÃO PAULO", "site": "www.ricoleiloes.com.br", "email": "amanda@ricoleiloes.com.br", "telefone": "(11)4040-8060"},
    {"nome": "AMAURY DE LEMOS ROSSATO", "matricula": "574", "cidade": "CAMPINAS", "site": None, "email": "arleiloes@gmail.com", "telefone": "(19)3242-2468"},
    {"nome": "AMELIA AMARAL LEVY", "matricula": "1257", "cidade": "SÃO PAULO", "site": None, "email": "levy.amelia@gmail.com", "telefone": "(11)99317-6476"},
    {"nome": "ANA CAROLINA PEREIRA DOS REIS FUGIMOTO", "matricula": "1347", "cidade": "CAMPINAS", "site": None, "email": "carolreisfg@gmail.com", "telefone": "(19)99218-5566"},
    {"nome": "ANA CLARA DE MELLO E SILVA", "matricula": "716", "cidade": "VALINHOS", "site": None, "email": "anaclarademello@bol.com.br", "telefone": "(19)3849-7675"},
    {"nome": "ANA CLAUDIA CAMARGO DE OLIVEIRA", "matricula": "1129", "cidade": "SÃO PAULO", "site": None, "email": "anaclaudia_leiloeira@gmail.com", "telefone": "(11)98988-4277"},
    {"nome": "ANA CLAUDIA CAROLINA CAMPOS FRAZAO", "matricula": "836", "cidade": "SÃO PAULO", "site": "www.frazaoleiloes.com.br", "email": "claudia@frazaoleiloes.com.br", "telefone": "(11)3550-4066"},
    {"nome": "ANA LETICIA MALERBA BUISSA", "matricula": "860", "cidade": "SÃO JOSÉ DO RIO PRETO", "site": None, "email": "gbuissa@uol.com.br", "telefone": "(17)3353-9925"},
    {"nome": "ANA MARIA ANDRADE QUINTO", "matricula": "1163", "cidade": "SÃO PAULO", "site": None, "email": "anaquinto9@hotmail.com", "telefone": "(11)96611-4610"},
    {"nome": "ANANIAS GODOI", "matricula": "1351", "cidade": "MOGI DAS CRUZES", "site": None, "email": "ananiasgodoyadv@hotmail.com", "telefone": "(11)94494-9201"},
    {"nome": "ANDERSON LOPES DE PAULA", "matricula": "1083", "cidade": "SÃO PAULO", "site": "www.e-leiloes.com.br", "email": "atendimento@e-leiloes.com.br", "telefone": "(11)4372-9034"},
    {"nome": "ANDERSON AMARAL BARROS MORALES", "matricula": "379", "cidade": "SOCORRO", "site": "www.socorronet.com.br", "email": "andersonmorales@socorronet.com.br", "telefone": "(19)3855-3233"},
    {"nome": "ANDRE AMARAL BARROS", "matricula": "1164", "cidade": "SÃO PAULO", "site": None, "email": "amaral.contatoleiloeiro@gmail.com", "telefone": "(11)96540-1346"},
    {"nome": "ANDRE CENCIN", "matricula": "1143", "cidade": "SÃO PAULO", "site": "www.cencin.com.br", "email": "cencin@cencin.com.br", "telefone": "(11)3192-2644"},
    {"nome": "ANDRE LUIS DIAS ALBINO", "matricula": "900", "cidade": "SÃO JOSÉ DO RIO PRETO", "site": "www.cemservicos.com.br", "email": "andre.albino@cemservicos.com.br", "telefone": "(17)3211-6655"},
    {"nome": "ANDRE MACEDO CAMPOS TOLEDO", "matricula": "1022", "cidade": "SÃO PAULO", "site": None, "email": "atoledoadv@gmail.com", "telefone": "(11)2626-5379"},
    {"nome": "ANDRE MARIO ARAUJO", "matricula": "962", "cidade": "FRANCA", "site": None, "email": "andremario_araujo@yahoo.com.br", "telefone": "(16)99314-0380"},
    {"nome": "ANDRE SILVA SOBREIRA DA SILVA", "matricula": "898", "cidade": "SÃO PAULO", "site": "www.icentraljudicial.com.br", "email": "atendimento@icentraljudicial.com.br", "telefone": "(11)3393-3155"},
    {"nome": "ANDREA XAVIER MARQUES FERREIRA", "matricula": "888", "cidade": "SÃO PAULO", "site": "www.conceitoleiloes.com.br", "email": "andrea@conceitoleiloes.com.br", "telefone": "(11)5512-2226"},
    {"nome": "ANDRÉ DE PIERI SPINA", "matricula": "1161", "cidade": "GUARATINGUETÁ", "site": "www.mjgassessoria.com.br", "email": "mjgassessoria@mjgassessoria.com.br", "telefone": "(11)99664-6864"},
    {"nome": "ANGELA EIKO INOUE DOS SANTOS", "matricula": "1144", "cidade": "SÃO PAULO", "site": "www.extrajustleiloes.com.br", "email": "atendimento@extrajustleiloes.com.br", "telefone": "(11)3393-3158"},
    {"nome": "ANGELA MEIRELLES LEMES AVELAR", "matricula": "1123", "cidade": "SÃO PAULO", "site": None, "email": "ANGELMLAVELAR@HOTMAIL.COM", "telefone": "(11)99988-3205"},
    {"nome": "ANGELA PECINI SILVEIRA", "matricula": "715", "cidade": "CAMPINAS", "site": "www.pecinileiloes.com.br", "email": "angela@pecinileiloes.com.br", "telefone": "(19)3295-9777"},
    {"nome": "ANGELA SARAIVA PORTES SOUZA", "matricula": "1328", "cidade": "SÃO PAULO", "site": "www.saraivaleiloes.com.br", "email": "angela@saraivaleiloes.com.br", "telefone": "(31)99180-1333"},
    {"nome": "ANGELICA MIEKO INOUE DANTAS", "matricula": "747", "cidade": "SÃO PAULO", "site": "www.lancetotal.com.br", "email": "lancetotal@lancetotal.com.br", "telefone": "(11)3393-3160"},
    {"nome": "ANTONIO BOLLA FERREIRA LIMA", "matricula": "578", "cidade": "SÃO PAULO", "site": None, "email": "antonio.bolla@itelefonica.com.br", "telefone": "(11)5512-2226"}
]

def is_corpor
