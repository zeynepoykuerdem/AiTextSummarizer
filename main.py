import sys
import os
from google import genai
import fitz as pymudpf
from dotenv import load_dotenv
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QFileDialog, QScrollArea
)
load_dotenv() #reads .env file
genai.api_key = os.getenv("GENAI_API_KEY")
class MyApp(QWidget):
    def __init__(self):
        '''
        Initializing the main window of the application
        '''
        super().__init__()
        # Main window setup
        self.setWindowTitle('PDF Summarizer')
        self.setGeometry(100, 100, 600, 800)  # Taller window for better scroll area
        
        # Main layout
        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(15)
        self.main_layout.setContentsMargins(20, 20, 20, 20)

       # Simple header
        self.header = QLabel('PDF Summarizer')
        self.header.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            margin: 10px;
        """)
        self.header.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.header)


         # Simple upload button
        self.button = QPushButton('Choose PDF File')
        self.button.setStyleSheet("""
            QPushButton {
                padding: 10px;
                font-size: 16px;
                margin: 10px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.main_layout.addWidget(self.button)

        # Scroll area for summary
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea { border: none; }")

        # Content widget for scroll area
        self.content = QWidget()
        self.scroll_layout = QVBoxLayout(self.content)

        # Result label
        self.result_label= QLabel()
        self.result_label.setWordWrap(True)
        self.result_label.setStyleSheet("""
            QLabel {
                padding: 15px;
                font-size: 14px;
                line-height: 1.5;
                background-color: black;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
        """)
        self.scroll_layout.addWidget(self.result_label)
        
        self.scroll.setWidget(self.content)
        self.main_layout.addWidget(self.scroll)
 
          # Set the main layout
        self.setLayout(self.main_layout)
        
        # Connect button
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
            text = ""
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text += page.get_text()
            return text
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return ""
        
    def openai_summarize(self, doc_text):
        """
        @ param text: Text to be summarized
        """
        try:
            genai_agent= genai.Client() # Create a client object to interact with the OpenAI API
            # prompt expect an object not a string
            # thats why we are getting an error -> chat.completions.create()
            file=doc_text
            #Client object has not attribute chat
            response=genai_agent.models.generate_content(
                model = "gemini-2.5-flash",
                #Error during OpenAI summarization: can only concatenate str (not "list") to str
                contents= ["Could you summarize the following text:\n" + file]

            
            )
            # output_text does not exist in response object
            summary=response.text
            display_text= summary if len(summary) < 500 else summary[:500] + "..."
            self.result_label.setText(display_text) # result label a ekliyorum

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