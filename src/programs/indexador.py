import csv
import string
import unicodedata
from collections import defaultdict
from math import log

def processar_palavra(palavra):
    # Remove caracteres especiais e converte para maiúsculas
    palavra = ''.join(filter(lambda x: x in string.ascii_letters, palavra)).upper()
    # Remove acentos
    palavra = ''.join(c for c in unicodedata.normalize('NFKD', palavra) if not unicodedata.combining(c))
    return palavra

def indexador(config_file):
    # Abrir o arquivo de configuração
    with open(config_file, 'r', encoding='utf-8') as f:
        leia_arquivo = None
        escreva_arquivo = None

        # Ler as instruções do arquivo de configuração
        for line in f:
            if line.startswith('LEIA='):
                leia_arquivo = line.strip().split('=')[1]
            elif line.startswith('ESCREVA='):
                escreva_arquivo = line.strip().split('=')[1]

        if not leia_arquivo or not escreva_arquivo:
            print("Erro: Arquivo de configuração incompleto.")
            return

        # Dicionário para armazenar o modelo vetorial
        modelo_vetorial = defaultdict(lambda:defaultdict(float))
        # Contador de termos para idf
        termos = 0

        # Conjunto com os IDs dos documentos que apareceram ao menos uma vez
        conjunto_ids_docs = set()

        # Dicionário para armazenar o número de ocorrências de cada palavra em cada documento
        freq_termo_doc = defaultdict(lambda: defaultdict(int))

        # Dicionário para armazenar a frequência máxima que um termo aparece em um documento
        max_freq_doc = defaultdict(int)

        # Ler a base de dados e construir o modelo vetorial
        with open(leia_arquivo, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=';')
            for row in reader:
                palavra = row[0]

                # Transformar as palavras da maneira solicitada
                termo = processar_palavra(palavra)
                
                if termo == '':
                    continue
                else:
                    termos += 1
                    doc_ids = list(eval(row[1]))
                    for doc_id in doc_ids:
                        freq_termo_doc[termo][doc_id] += 1
                        if doc_id not in conjunto_ids_docs:
                            conjunto_ids_docs.add(doc_id)
                        
                        if doc_id not in max_freq_doc:
                            max_freq_doc[doc_id] = freq_termo_doc[termo][doc_id]
                        elif freq_termo_doc[termo][doc_id] > max_freq_doc[doc_id]:
                            max_freq_doc[doc_id] = freq_termo_doc[termo][doc_id]
                        else:
                            continue

        qtd_documentos = len(conjunto_ids_docs)

        # Para que o modelo vetorial esteja normalizado, foram adotadas as equações 2.1, 2.2 e 2.3
        # do livro Modern Information Retrieval, edição de 1999
        for termo, doc_incidence in freq_termo_doc.items():
            for doc_id, freq_doc in doc_incidence.items():
                tf = freq_doc / max_freq_doc[doc_id] 
                idf = log((qtd_documentos/len(freq_termo_doc[termo])),10)
                weight = tf * idf
                modelo_vetorial[termo][doc_id] = weight

        # Escrever o modelo vetorial no arquivo CSV
        with open(escreva_arquivo, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(['Termo', 'DocID', 'TF-IDF'])
            for termo, docs in modelo_vetorial.items():
                for doc_id, tf_idf in docs.items():
                    writer.writerow([termo, doc_id, tf_idf])

        print("Indexação concluída. Modelo vetorial salvo em", escreva_arquivo)

# Chamada da função para realizar a indexação

if __name__ == "__main__":
    indexador('src/cfg/index.cfg')
