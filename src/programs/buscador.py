import csv
from collections import defaultdict
from indexador import processar_palavra
from math import sqrt, cos

def calcula_tamanho_vetor(termos):
    return sqrt(sum(tf_idf ** 2 for tf_idf in termos.values()))

def produto_escalar(vetor_a, vetor_b):
    soma = 0
    for termo, idf in vetor_a.items():
        if termo in vetor_b.keys():
            soma += idf * vetor_b[termo]
    return soma


def buscador(config_file):
    with open(config_file, 'r', encoding='utf-8') as f:
        modelo_arquivo = None
        consultas_arquivo = None
        resultados_arquivo = None

        for line in f:
            if line.startswith('MODELO='):
                modelo_arquivo = line.strip().split('=')[1]
            elif line.startswith('CONSULTAS='):
                consultas_arquivo = line.strip().split('=')[1]
            elif line.startswith('RESULTADOS='):
                resultados_arquivo = line.strip().split('=')[1]

        if not modelo_arquivo or not consultas_arquivo or not resultados_arquivo:
            print("Erro: Arquivo de configuração incompleto.")
            return
        
        # Conjunto das ids dos docs
        conjunto_ids_docs = set()

        # Carregar o modelo vetorial
        modelo_vetorial = defaultdict(lambda: defaultdict(float))
        freq_termo_doc =  defaultdict(lambda: defaultdict(int))
        with open(modelo_arquivo, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=';')
            next(reader)  # Pular o cabeçalho
            for row in reader:
                termo = row[0]
                doc_id = row[1]
                if doc_id not in conjunto_ids_docs:
                            conjunto_ids_docs.add(doc_id)
                tf_idf = float(row[2])
                modelo_vetorial[doc_id][termo] = tf_idf
                freq_termo_doc[termo][doc_id] += 1

        # Ler as consultas e realizar a busca
        with open(consultas_arquivo, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=';')
            with open(resultados_arquivo, 'w', newline='', encoding='utf-8') as output_file:
                writer = csv.writer(output_file, delimiter=';')
                writer.writerow(['Consulta', 'Resultados'])
                for row in reader:
                    query_number = row[0]
                    if query_number == "QueryNumber":
                        continue
                    else:
                        consulta = row[1]
                        termos_consulta = consulta.split()
                        vetor_q = defaultdict(lambda: float('inf'))
                        for termo_consulta in termos_consulta:
                            termo_consulta = processar_palavra(termo_consulta)
                            if termo_consulta in freq_termo_doc.keys():
                                peso_termo_doc_qualquer = list(freq_termo_doc[termo_consulta].keys())[0]
                                tf = freq_termo_doc[termo_consulta][peso_termo_doc_qualquer]
                                idf = modelo_vetorial[peso_termo_doc_qualquer][termo_consulta] / tf
                                vetor_q[termo_consulta] = idf
                        
                        tamanho_q = calcula_tamanho_vetor(vetor_q)
                        similaridade_query = list()
                        for doc_id, termos in modelo_vetorial.items():
                            tamanho_doc = calcula_tamanho_vetor(termos)
                            arg_cos = produto_escalar(vetor_q, modelo_vetorial[doc_id]) / (tamanho_q * tamanho_doc)
                            similaridade_query_doc = cos(arg_cos)
                            similaridade_query.append([doc_id, similaridade_query_doc])

                    similaridade_query_ordenada = sorted(similaridade_query, key=lambda x: x[1], reverse=True)
                    for i in range(len(similaridade_query_ordenada)):
                        similaridade_query_ordenada[i] = [i+1, similaridade_query_ordenada[i][0], similaridade_query_ordenada[i][1]]
                    
                    writer.writerow([query_number, similaridade_query_ordenada])

        print("Busca concluída. Resultados salvos em", resultados_arquivo)

# Chamada da função para realizar a busca
buscador('src/cfg/busca.cfg')