import xml.etree.ElementTree as ET
import csv

def processar_consultas(config_file):
        
    # Abrir o arquivo de configuração:
    with open(config_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        xml_file = None
        consultas_file = None
        esperados_file = None

        # Ler as instruções do arquivo de configuração
        for line in lines:
            if line.startswith('LEIA='):
                xml_file = line.strip().split('=')[1]
            elif line.startswith('CONSULTAS='):
                consultas_file = line.strip().split('=')[1]
            elif line.startswith('ESPERADOS='):
                esperados_file = line.strip().split('=')[1]
        
        if not xml_file or not consultas_file or not esperados_file:
            print("Erro. Arquivo de configuração possivelmente incompleto.")
            return

        # Abrir o arquivo XML
        tree = ET.parse(xml_file)
        root = tree.getroot()

        # Abrir os arquivos CSV para escrita
        with open(consultas_file, 'w', newline='', encoding='utf-8') as consultas_csv, \
            open(esperados_file, 'w', newline='', encoding='utf-8') as esperados_csv:

            # Definir os cabeçalhos dos arquivos CSV
            consultas_writer = csv.writer(consultas_csv, delimiter=';')
            esperados_writer = csv.writer(esperados_csv, delimiter=';')
            consultas_writer.writerow(['QueryNumber', 'QueryText'])
            esperados_writer.writerow(['QueryNumber', 'DocNumber', 'DocVotes'])

            # Iterar sobre as consultas no arquivo XML
            for query in root.findall('.//QUERY'):
                query_number = query.find('QueryNumber').text.strip()
                query_text = query.find('QueryText').text.strip().upper()

                # Escrever a consulta no arquivo CSV de consultas
                consultas_writer.writerow([query_number, query_text])

                # Iterar sobre os documentos esperados para cada consulta
                for item in query.findall('.//Item'):
                    doc_number = item.text.strip()
                    doc_votes = item.get('score')

                    # Escrever o documento esperado no arquivo CSV de esperados
                    esperados_writer.writerow([query_number, doc_number, doc_votes])
        
        print("Processamento de consultas concluído. Arquivos CSV gerados com sucesso.")

# Chamada da função para processar as consultas
processar_consultas('src/cfg/pc.cfg')