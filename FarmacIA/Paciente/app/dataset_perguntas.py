import sqlite3
import csv
import os

# Nome do arquivo do banco de dados
DB_FILE = 'instance/remedios_chat.db'
# Nome do arquivo de saída
OUTPUT_FILE = 'dataset_perguntas_respostas.csv'

def create_dataset():

    if not os.path.exists(DB_FILE):
        print(f"Erro: O arquivo de banco de dados '{DB_FILE}' não foi encontrado.")
        print("Certifique-se de que este script está na mesma pasta que o seu banco de dados.")
        return

    print(f"Conectando ao banco de dados '{DB_FILE}'...")
    
    with sqlite3.connect(DB_FILE) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Query SQL para buscar todas as mensagens, juntando com as conversas
        query = """
            SELECT
                m.conversation_id,
                m.role,
                m.content,
                c.nome_remedio
            FROM
                messages AS m
            JOIN
                conversations AS c ON m.conversation_id = c.id
            ORDER BY
                m.conversation_id, m.created_at;
        """
        
        print("Executando a query para buscar as mensagens...")
        cursor.execute(query)
        all_messages = cursor.fetchall()
        print(f"Total de {len(all_messages)} mensagens encontradas.")

        qa_pairs = []
        for i in range(len(all_messages) - 1):
            current_message = all_messages[i]
            next_message = all_messages[i+1]

            if (current_message['role'] == 'user' and
                next_message['role'] == 'assistant' and
                current_message['conversation_id'] == next_message['conversation_id']):
                
                qa_pairs.append({
                    'medicamento': current_message['nome_remedio'],
                    'pergunta': current_message['content'],
                    'resposta': next_message['content']
                })
        
        if not qa_pairs:
            print("Nenhum par de pergunta/resposta encontrado.")
            return

        print(f"Processamento concluído. {len(qa_pairs)} pares de pergunta/resposta foram extraídos.")
        print(f"Salvando o dataset em '{OUTPUT_FILE}'...")

        with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['medicamento', 'pergunta', 'resposta']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            writer.writerows(qa_pairs)

        print(f"Dataset criado com sucesso em '{OUTPUT_FILE}'!")

if __name__ == '__main__':
    create_dataset()