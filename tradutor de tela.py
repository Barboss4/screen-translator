import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit, QLabel, QPushButton, QGroupBox, QComboBox
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QFont, QFontMetrics
import pyautogui
import pytesseract
from translate import Translator

class Overlay(QWidget):
    def __init__(self):
        super().__init__()
        self.capture_rect = QRect(100, 100, 900, 150)  # Onde inicia a Caixa para capturar o texto e o tamanho da caixa
        self.display_rect = QRect(400, 100, 400, 150)  # Onde inicia a Caixa para exibir a tradução e o tamanho da caixa
        self.dragging_capture = False
        self.dragging_display = False
        self.translated_text = ""
        self.initUI()  # Chama initUI após inicializar os atributos necessários

        # Inicializa o tradutor com a linguagem padrão
        self.translator = Translator(to_lang="pt")

    def initUI(self):
        # Configura a interface do usuário, incluindo as caixas de entrada de texto
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setGeometry(0, 0, 1920, 1080)  # Ajuste para a resolução do seu monitor

        # Cria o grupo de controle
        self.control_group = QGroupBox('Control Box', self)
        self.control_group.setGeometry(10, 10, 300, 200)
        self.control_group.setStyleSheet("background-color: rgba(255, 255, 255, 180);")

        # Configurar controles de entrada de texto para as dimensões da caixinha de captura
        self.width_label_capture = QLabel('W:', self.control_group)
        self.width_label_capture.setGeometry(10, 35, 20, 20)

        self.width_input_capture = QLineEdit(self.control_group)
        self.width_input_capture.setText(str(self.capture_rect.width()))
        self.width_input_capture.setGeometry(30, 35, 50, 20)
        self.width_input_capture.editingFinished.connect(self.update_capture_dimensions)

        self.height_label_capture = QLabel('H:', self.control_group)
        self.height_label_capture.setGeometry(90, 35, 20, 20)

        self.height_input_capture = QLineEdit(self.control_group)
        self.height_input_capture.setText(str(self.capture_rect.height()))
        self.height_input_capture.setGeometry(110, 35, 50, 20)
        self.height_input_capture.editingFinished.connect(self.update_capture_dimensions)

        # Configurar controles de entrada de texto para as dimensões da caixinha de exibição
        self.width_label_display = QLabel('W:', self.control_group)
        self.width_label_display.setGeometry(10, 85, 20, 20)

        self.width_input_display = QLineEdit(self.control_group)
        self.width_input_display.setText(str(self.display_rect.width()))
        self.width_input_display.setGeometry(30, 85, 50, 20)
        self.width_input_display.editingFinished.connect(self.update_display_dimensions)

        self.height_label_display = QLabel('H:', self.control_group)
        self.height_label_display.setGeometry(90, 85, 20, 20)

        self.height_input_display = QLineEdit(self.control_group)
        self.height_input_display.setText(str(self.display_rect.height()))
        self.height_input_display.setGeometry(110, 85, 50, 20)
        self.height_input_display.editingFinished.connect(self.update_display_dimensions)
        
        # Adiciona um botão para iniciar a tradução
        self.translate_button = QPushButton('OK', self.control_group)
        self.translate_button.clicked.connect(self.capture_and_translate_text)
        self.translate_button.setGeometry(10, 160, 50, 30)  # Ajuste conforme necessário
        
        # Adiciona um botão para fechar a aplicação
        self.close_button = QPushButton('Fechar', self.control_group)
        self.close_button.clicked.connect(self.close_application)
        self.close_button.setGeometry(70, 160, 50, 30)  # Ajuste conforme necessário

        # Adiciona uma combobox para escolher a linguagem de entrada para OCR
        self.lang_input_label = QLabel('Lang OCR:', self.control_group)
        self.lang_input_label.setGeometry(10, 120, 60, 20)

        self.lang_input_combo = QComboBox(self.control_group)
        self.lang_input_combo.setGeometry(70, 120, 80, 20)
        self.lang_input_combo.addItems(['eng', 'fra', 'spa', 'deu'])  # Adicione mais idiomas conforme necessário

        # Adiciona uma combobox para escolher a linguagem de saída para tradução
        self.lang_output_label = QLabel('Lang Trad:', self.control_group)
        self.lang_output_label.setGeometry(160, 120, 60, 20)

        self.lang_output_combo = QComboBox(self.control_group)
        self.lang_output_combo.setGeometry(220, 120, 80, 20)
        self.lang_output_combo.addItems(['pt', 'en', 'fr', 'es'])  # Adicione mais idiomas conforme necessário

        self.dragging_control_group = False

        self.show()

    def close_application(self):
        # Fecha a aplicação
        QApplication.instance().quit()

    def update_capture_dimensions(self):
        # Atualiza as dimensões da caixa de captura com base nos valores inseridos
        try:
            width = int(self.width_input_capture.text())
            height = int(self.height_input_capture.text())
            self.capture_rect.setWidth(width)
            self.capture_rect.setHeight(height)
            self.update()
        except ValueError:
            pass

    def update_display_dimensions(self):
        # Atualiza as dimensões da caixa de exibição com base nos valores inseridos
        try:
            width = int(self.width_input_display.text())
            height = int(self.height_input_display.text())
            self.display_rect.setWidth(width)
            self.display_rect.setHeight(height)
            self.update()
        except ValueError:
            pass

    def paintEvent(self, event):
        # Desenha as caixas de captura e exibição na janela, e o texto traduzido dentro da caixa de exibição
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Caixa de captura
        painter.setPen(QPen(QColor(0, 0, 255), 3))  # Borda azul
        painter.setBrush(QBrush(QColor(0, 0, 0, 100)))  # Preenchimento preto opaco
        painter.drawRect(self.capture_rect)
        
        # Caixa de exibição
        painter.setPen(QPen(QColor(255, 0, 0), 3))  # Borda vermelha
        painter.setBrush(QBrush(QColor(255, 255, 255)))  # Preenchimento branco opaco
        painter.drawRect(self.display_rect)

        # Desenha o texto traduzido dentro da caixinha de exibição
        if self.translated_text:
            painter.setPen(QPen(QColor(0, 0, 0)))  # Cor do texto
            optimal_font_size = self.get_optimal_font_size(painter, self.translated_text, self.display_rect)
            painter.setFont(QFont('Arial', optimal_font_size))
            text_rect = self.display_rect.adjusted(5, 5, -5, -5)  # Ajuste as margens internas
            painter.drawText(text_rect, Qt.TextWordWrap, self.translated_text)

    def get_optimal_font_size(self, painter, text, rect):
        # Calcula o tamanho de fonte ideal para garantir que o texto caiba dentro da caixa de exibição
        font_size = 1
        while True:
            font = QFont('Arial', font_size)
            painter.setFont(font)
            fm = QFontMetrics(font)
            text_rect = fm.boundingRect(rect.adjusted(5, 5, -5, -5), Qt.TextWordWrap, text)
            if text_rect.width() > rect.width() or text_rect.height() > rect.height():
                break
            font_size += 1
        return font_size - 1

    def mousePressEvent(self, event):
        # Detecta quando o botão do mouse é pressionado e inicia o arrasto da caixa correspondente
        if event.button() == Qt.LeftButton:
            if self.capture_rect.contains(event.pos()):
                self.dragging_capture = True
                self.drag_pos = event.pos() - self.capture_rect.topLeft()
            elif self.display_rect.contains(event.pos()):
                self.dragging_display = True
                self.drag_pos = event.pos() - self.display_rect.topLeft()
            elif self.control_group.geometry().contains(event.pos()):
                self.dragging_control_group = True
                self.drag_pos = event.pos() - self.control_group.geometry().topLeft()

    def mouseMoveEvent(self, event):
        # Move a caixa de captura ou exibição enquanto o botão do mouse está sendo arrastado
        if self.dragging_capture:
            self.capture_rect.moveTopLeft(event.pos() - self.drag_pos)
            self.update()
        elif self.dragging_display:
            self.display_rect.moveTopLeft(event.pos() - self.drag_pos)
            self.update()
        elif self.dragging_control_group:
            self.control_group.move(event.pos() - self.drag_pos)

    def mouseReleaseEvent(self, event):
        # Detecta quando o botão do mouse é solto e para o arrasto da caixa correspondente
        if event.button() == Qt.LeftButton:
            self.dragging_capture = False
            self.dragging_display = False
            self.dragging_control_group = False

    def capture_and_translate_text(self):
        # Captura o texto da área definida pela caixa de captura, realiza o OCR para extrair o texto, traduz o texto extraído e armazena o resultado
        x, y, width, height = self.capture_rect.x(), self.capture_rect.y(), self.capture_rect.width(), self.capture_rect.height()
        screenshot = pyautogui.screenshot(region=(x, y, width, height))
        
        # Reconhecimento de texto
        ocr_lang = self.lang_input_combo.currentText()
        text = pytesseract.image_to_string(screenshot, lang=ocr_lang)
        
        # Tradução do texto
        output_lang = self.lang_output_combo.currentText()
        self.translator = Translator(to_lang=output_lang)
        self.translated_text = self.translator.translate(text)
        
        # Atualiza a janela para exibir o texto traduzido
        self.update()

def main():
    app = QApplication(sys.argv)
    overlay = Overlay()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
