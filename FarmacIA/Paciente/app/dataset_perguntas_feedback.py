import sqlite3
import csv
import os

DB_FILE = 'instance/remedios_chat.db'
OUTPUT_FILE = 'dataset_com_feedback.csv'

def create_dataset_with_feedback():
    if not os.path.exists(DB_FILE):
        print(f"Erro: Banco de dados '{DB_FILE}' não encontrado.")
        return

    print(f"Conectando ao banco '{DB_FILE}'...")
    with sqlite3.connect(DB_FILE) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # LEFT JOIN para pegar respostas sem feedback tambem
        query = """
            SELECT
                m.id AS message_id,
                m.role,
                m.content,
                c.nome_remedio,
                f.score,
                f.comment
            FROM
                messages AS m
            JOIN
                conversations AS c ON m.conversation_id = c.id
            LEFT JOIN
                feedback AS f ON m.id = f.message_id
            ORDER BY
                c.id, m.created_at;
        """
        
        cursor.execute(query)
        all_messages = cursor.fetchall()
        print(f"Total de {len(all_messages)} mensagens encontradas.")

        qa_pairs = []
        for i in range(len(all_messages) - 1):
            current_message = all_messages[i]
            next_message = all_messages[i+1]

            if (current_message['role'] == 'user' and
                next_message['role'] == 'assistant'):
                
                qa_pairs.append({
                    'medicamento': current_message['nome_remedio'],
                    'pergunta': current_message['content'],
                    'resposta': next_message['content'],
                    'score': next_message['score'],
                    'comment': next_message['comment']
                })
        
        if not qa_pairs:
            print("Nenhum par de pergunta/resposta encontrado.")
            return

        print(f"Salvando {len(qa_pairs)} pares em '{OUTPUT_FILE}'...")

        with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['medicamento', 'pergunta', 'resposta', 'score', 'comment']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(qa_pairs)

        print(f"Dataset com feedback criado com sucesso!")

if __name__ == '__main__':
    create_dataset_with_feedback()