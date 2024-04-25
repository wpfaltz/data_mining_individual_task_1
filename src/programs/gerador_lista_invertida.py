import xml.etree.ElementTree as ET
import csv
from collections import defaultdict

def gerar_lista_invertida(config_file):
    # Abrir o arquivo de configuração
    with open(config_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        arquivos_leitura = []
        arquivo_escrita = None

        # Ler as instruções do arquivo de configuração
        for line in lines:
            if line.startswith('LEIA='):
                arquivos_leitura.append(line.strip().split('=')[1])
            elif line.startswith('ESCREVA='):
                arquivo_escrita = line.strip().split('=')[1]

        if not arquivos_leitura or not arquivo_escrita:
            print("Erro: Arquivo de configuração incompleto ou algum dos arquivos não foi encontrado.")
            return
        
        # Dicionário para armazenar a lista invertida
        lista_invertida = defaultdict(list)

        # Iterar sobre os arquivos XML
        for arquivo_xml in arquivos_leitura:
            tree = ET.parse(arquivo_xml)
            root = tree.getroot()

            # Iterar sobre os registros
            for record in root.findall('.//RECORD'):
                recordnum = record.find('RECORDNUM').text.strip()
                if record.find('ABSTRACT') is not None:
                    abstract = record.find('ABSTRACT').text.strip()  
                else: 
                    if record.find('EXTRACT') is not None:
                        record.find('EXTRACT').text.strip()  
                    else:
                        continue

                # Processar o texto do abstract e adicionar as palavras à lista invertida
                palavras = abstract.split()
                for palavra in palavras:
                    palavra = palavra.upper().strip('.,!?":;')
                    if palavra.isalnum():
                        lista_invertida[palavra].append(recordnum)

        # Escrever a lista invertida no arquivo CSV
        with open(arquivo_escrita, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter = ';')
            for palavra, documentos in lista_invertida.items():
                writer.writerow([palavra, documentos])

        print("Lista invertida gerada com sucesso.")

# Chamada da função para gerar a lista invertida
gerar_lista_invertida('src/cfg/gli.cfg')
