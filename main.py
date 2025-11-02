import sys
import os
from google import genai
import fitz as pymudpf
from dotenv import load_dotenv
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QVBoxLayout,
    QLabel,
    QFileDialog,
    QScrollArea,
)
from reportlab.pdfgen import canvas
from reportlab.lib import pdfencrypt

load_dotenv()  # reads .env file
genai.api_key = os.getenv("GENAI_API_KEY")


class MyApp(QWidget):
    def __init__(self):
        """Initializing the main window of the application"""
        super().__init__()

        # Main window setup
        self.setWindowTitle("PDF Summarizer")
        self.setGeometry(100, 100, 600, 800)

        # Main layout
        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(15)
        self.main_layout.setContentsMargins(20, 20, 20, 20)

        # Header
        self.header = QLabel("PDF Summarizer")
        self.header.setStyleSheet(
            """
            font-size: 24px;
            font-weight: bold;
            margin: 10px;
            """
        )
        self.header.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.header)

        # Upload button
        self.button = QPushButton("Choose PDF File")
        self.button.setStyleSheet(
            """
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
            """
        )
        self.main_layout.addWidget(self.button)

        # Scroll area for summary
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea { border: none; }")

        # Content widget for scroll area
        self.content = QWidget()
        self.scroll_layout = QVBoxLayout(self.content)

        # Result label
        self.result_label = QLabel()
        self.result_label.setWordWrap(True)
        self.result_label.setStyleSheet(
            """
            QLabel {
                padding: 15px;
                font-size: 14px;
                line-height: 1.5;
                background-color: black;
                color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
            """
        )
        self.scroll_layout.addWidget(self.result_label)
        self.scroll.setWidget(self.content)
        self.main_layout.addWidget(self.scroll)

        # Set main layout
        self.setLayout(self.main_layout)

        # Connect button
        self.button.clicked.connect(self.on_summarize_button_click)

    def on_summarize_button_click(self):
        """Return selected file path by user"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select a PDF file to summarize",
            os.getcwd(),
            "PDF Files (*.pdf);;All Files (*)",
        )
        if file_path:
            print(f"Selected file: {file_path}")
            self.upload_file(file_path)
            return file_path

    def upload_file(self, file_path):
        """Extract text from PDF and call OpenAI summarization"""
        doc_text = self.extract_text_from_pdf(file_path)
        if doc_text:
            self.openai_summarize(doc_text)
        else:
            print("No text extracted from the document.")

    def extract_text_from_pdf(self, file_path):
        """Extract text from the PDF document"""
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
        """Summarize text and save summary as PDF"""
        try:
            genai_agent = genai.Client()
            response = genai_agent.models.generate_content(
                model="gemini-2.5-flash",
                contents=["Could you summarize the following text:\n" + doc_text],
            )
            summary = response.text
            display_text = summary if len(summary) < 500 else summary[:500] + "..."
            self.result_label.setText(display_text)

            # --- PDF oluşturma ---
            try:
                file_name = "Summary.pdf"
                pdf_canvas = canvas.Canvas(file_name)
                pdf_canvas.setFont("Helvetica", 12)

                lines = summary.split("\n")
                x = 100
                y = 800
                max_width = 500

                for line in lines:
                    for word in line.split(" "):
                        word_width = pdf_canvas.stringWidth(word + " ")
                        if x + word_width > max_width:
                            x = 100
                            y -= 15
                            if y < 50:
                                pdf_canvas.showPage()
                                pdf_canvas.setFont("Helvetica", 12)
                                y = 800

                        pdf_canvas.drawString(x, y, word)
                        x += word_width

                    # Satır bitince başa dön + alt satıra geç
                    x = 100
                    y -= 15
                    if y < 50:
                        pdf_canvas.showPage()
                        pdf_canvas.setFont("Helvetica", 12)
                        y = 800

                pdf_canvas.save()
                print(f"PDF summary created: {file_name}")

            except Exception as e:
                print(f"Error creating PDF summary: {e}")

        except Exception as e:
            print(f"Error during OpenAI summarization: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myApp = MyApp()
    myApp.show()
    sys.exit(app.exec())
