from flask import Flask, render_template, request, send_file
from openai import OpenAI
import os
import fitz  # PyMuPDF
client = OpenAI(api_key='sk-proj-ul8PBrYTEh2itiVNnKlnT3BlbkFJrIihmmgKwfxwcCFLlwHA')

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/translate', methods=['POST'])

def translate():
    file = request.files['file']
    if file:
        # Dosyanın uzantısını kontrol edin
        filename = file.filename
        file_extension = filename.split('.')[-1].lower()

        if file_extension == 'pdf':
            # PDF dosyasını PyMuPDF ile açma
            pdf_document = fitz.open(stream=file.read(), filetype='pdf')
            text = ''
            for page_num in range(pdf_document.page_count):
                page = pdf_document.load_page(page_num)
                text += page.get_text()
        else:
            # Diğer dosya türlerini utf-8 olarak okuma
            text = file.read().decode('utf-8')

        # ChatGPT ile çeviri yapma
        response = client.chat.completions.create(model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a translator."},
            {"role": "user", "content": f"Translate this to Turkish: {text}"}
        ], max_tokens=4096)

        translated_text = response.choices[0].message.content.strip()

        # Çevrilen metni dosyaya yazma
        translated_file_path = os.path.join('static', 'translated_file.txt')
        with open(translated_file_path, 'w', encoding='utf-8') as f:
            f.write(translated_text)

        return send_file(translated_file_path, as_attachment=True, download_name='translated_file.txt')

if __name__ == '__main__':
    app.run(debug=True)
