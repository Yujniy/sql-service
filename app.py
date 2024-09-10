from flask import Flask, request, jsonify, render_template, send_file, after_this_request
import os
import tempfile

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/submit', methods=['POST'])
def submit():
    data = request.json['data']
    columns = [f"col_{i}" for i in range(len(data[0]))]
    rows = data

    # Создание временного файла SQL с фиксированным именем
    sql_path = os.path.join(tempfile.gettempdir(), 'database.sql')

    with open(sql_path, 'w', encoding='utf-8') as f:
        # Создание таблицы
        f.write(f"DROP TABLE IF EXISTS mytable;\n")
        f.write(f"CREATE TABLE IF NOT EXISTS mytable ({', '.join([f'{col} TEXT' for col in columns])});\n")

        # Вставка данных
        for row in rows:
            values = ', '.join([f"'{value}'" for value in row])
            f.write(f"INSERT INTO mytable ({', '.join(columns)}) VALUES ({values});\n")

        # Добавление запроса для отображения содержимого таблицы
        f.write("SELECT * FROM mytable;\n")

    return jsonify({"message": "Данные успешно сохранены", "file_url": f"/download/database.sql"}), 200

@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(tempfile.gettempdir(), filename)

    @after_this_request
    def remove_file(response):
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Ошибка при удалении файла: {e}")
        return response

    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)