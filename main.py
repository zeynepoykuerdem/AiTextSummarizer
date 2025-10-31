import sys
import os
from openai import OpenAI
import fitz as pymudpf

from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QFileDialog
)
class MyApp(QWidget):
    def __init__(self):
        '''
        Initialiying the main window of the application
        '''
        super().__init__()
        self.setWindowTitle('My AI Text Summarizer App')
        self.setGeometry(100, 100, 400, 300)
        
        # Adding a layout 
        self.layout = QVBoxLayout()

        self.button = QPushButton('Summarize Text', self)

        self.label = QLabel('Click the button to summarize text.', self)
    
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.button)
        self.setLayout(self.layout) # Applying the layout to the main window
        self.button.clicked.connect(self.on_summarize_button_click)

    def on_summarize_button_click(self):
        """
        returns (file names, selected filter) by user
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            'Select one or more files to summarize', # Caption
             os.getcwd(), # Directory, working current directory
            'Text Files (*.pdf);; All files (*)' # File filter, onlx text files including .txt, .docx, .doc, .pdf
        )
        if file_path:
            print(f'Selected file: {file_path}')
            self.upload_file(file_path)

    
    def upload_file(self, file_path):
        """
        @ param file_path: Specific file path
        Extract text from the docuemnt and call openai_summarize function
        """
        doc_text= self.extract_text_from_pdf(file_path)
        if doc_text: # not an empty string
            self.openai_summarize(doc_text)
        else:
            print("No text extarcted from the dócument.")
        # get the text from the document, read all pages
        
    def extract_text_from_pdf(self, file_path):
        """
        @ param file_path: Specific file path
        Extract text from the pdf document
        """
        try:
            doc = pymudpf.open(file_path)
            text = []
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text += page.get_text()
            return text
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return []
        
    def openai_summarize(self, doc_text):
        """
        @ param text: Text to be summarized
        """
        try:
            openai_agent= OpenAI()
            # prompt expect an object not a string
            # thats why we are getting an error -> chat.completions.create()
            prompt= f"Analyze the follwing text and provide a concise summary.:n\n{doc_text}\n\n"

            response=openai_agent.chat.completions.create(
                model = "gpt-5",

                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes text documents."}
                    
                    ,{"role": "user", "content": f" Please provide a concise summary of this text {prompt}"}

                ]
            )
            # output_text does not exist in response object
            summary=response.choices[0].message.content
            self.label.setText("Summary:\n" + summary)
            self.label.setText("Summary printed to console.")

        except Exception as e:
            print(f"Error during OpenAI summarization: {e}")    

if __name__ == '__main__':
    app= QApplication(sys.argv)
    myApp = MyApp()
    myApp.show()
    sys.exit(app.exec())

 # Dosyalar yüklendikten sonra özetleme işlemi burada gerçekleştirilecek
 # sonuclar bir metin kutusunda gösterilecek
 # 
 # Kullanici dosyayi sectikten sonra, dosyalar okunacak openai api tarafindan
 # özetlenecek ve sonuçlar kullanıcıya gösterilecek       