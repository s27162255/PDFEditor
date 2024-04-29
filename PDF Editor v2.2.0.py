# -*- coding: utf-8 -*-
################################
# Author: Ping
# Description: PDF Editor v2.2.0
# Date: 2024-04-19
# LastEditTime: 2024-04-19
################################
import PyPDF2
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QCursor, QIcon
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QMenu, QAction
from PyQt5.QtCore import Qt
from pdfrw import PdfWriter, PdfReader
from pikepdf import Pdf
from PDF_Editor_UI import Ui_MainWindow
from time import sleep
from datetime import datetime
from os.path import join, abspath, isdir, basename, split, exists
from subprocess import Popen
from os import makedirs, remove


class MainWindow_controller(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.PDF_Editor_UI = Ui_MainWindow()
        self.PDF_Editor_UI.setupUi(self)
        self.setup_control()
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            file_paths = [url.toLocalFile() for url in urls]
            if event.pos().x() <= self.width()/2:
                self.PDF_Editor_UI.filename_list = self.PDF_Editor_UI.filename_list+file_paths
                if (len(self.PDF_Editor_UI.filename_list) != 0):
                    self.PDF_Editor_UI.statusbar.showMessage(
                        f"新增{str(len(file_paths))}個pdf文件成功")
                    for file_path in file_paths:
                        if self.is_pdf_encrypted(file_path):
                            file_name = f'(請先解鎖此文件){basename(file_path).replace("(Lock)","")}'
                        else:
                            file_name = basename(
                                file_path).replace("(Lock)", "")
                        item = QtWidgets.QListWidgetItem(file_name)
                        item.setToolTip(file_path.replace("/", "\\"))
                        self.PDF_Editor_UI.listWidget.addItem(item)
                        self.PDF_Editor_UI.progressBar1.setValue(100)
                    sleep(0.3)
                    self.PDF_Editor_UI.progressBar1.reset()
            elif event.pos().x() > self.width()/2:
                self.PDF_Editor_UI.filename_list2 = self.PDF_Editor_UI.filename_list2+file_paths
                if (len(self.PDF_Editor_UI.filename_list2) != 0):
                    self.PDF_Editor_UI.statusbar.showMessage(
                        f"新增{str(len(file_paths))}個pdf文件成功")
                    for file_path in file_paths:
                        if self.is_pdf_encrypted(file_path):
                            file_name = f'(請先解鎖此文件){basename(file_path).replace("(Lock)","")}'
                        else:
                            file_name = basename(
                                file_path).replace("(Lock)", "")
                        item = QtWidgets.QListWidgetItem(file_name)
                        item.setToolTip(file_path.replace("/", "\\"))
                        self.PDF_Editor_UI.listWidget_2.addItem(item)
                        self.PDF_Editor_UI.progressBar2.setValue(100)
                    sleep(0.3)
                    self.PDF_Editor_UI.progressBar2.reset()
            event.accept()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            left_selected_items = self.PDF_Editor_UI.listWidget.selectedItems()
            right_selected_items = self.PDF_Editor_UI.listWidget_2.selectedItems()
            if len(left_selected_items) != 0 or len(right_selected_items) != 0:
                for item in left_selected_items:
                    self.PDF_Editor_UI.listWidget.takeItem(
                        self.PDF_Editor_UI.listWidget.row(item))
                    self.PDF_Editor_UI.statusbar.showMessage("刪除成功！")

                for item in right_selected_items:
                    self.PDF_Editor_UI.listWidget_2.takeItem(
                        self.PDF_Editor_UI.listWidget_2.row(item))
                    self.PDF_Editor_UI.statusbar.showMessage("刪除成功！")
            else:
                self.PDF_Editor_UI.statusbar.showMessage("沒有選擇刪除項目！")

    def setup_control(self):
        self.PDF_Editor_UI.select1.clicked.connect(self.open_file_1)
        self.PDF_Editor_UI.select2.clicked.connect(self.open_file_2)
        self.PDF_Editor_UI.clear1.clicked.connect(self.clear1)
        self.PDF_Editor_UI.clear2.clicked.connect(self.clear2)
        self.PDF_Editor_UI.start1.clicked.connect(self.combine_pdf_action)
        self.PDF_Editor_UI.end.clicked.connect(self.close)
        self.PDF_Editor_UI.start2.clicked.connect(self.split)
        self.PDF_Editor_UI.floder.clicked.connect(self.floder)
        self.PDF_Editor_UI.sign.clicked.connect(self.sign)
        self.PDF_Editor_UI.listWidget.customContextMenuRequested[QtCore.QPoint].connect(
            self.contextmenu_listWidget)
        self.PDF_Editor_UI.listWidget_2.customContextMenuRequested[QtCore.QPoint].connect(
            self.contextmenu_listWidget2)

    def contextmenu_listWidget(self):  # 合併區右鍵
        rightMenu = QMenu(self.PDF_Editor_UI.listWidget)

        self.action_unlock = QAction(u'解鎖')
        self.action_delete = QAction(u'刪除')
        self.action_sort = QAction(u'升序')
        self.action_sort_reverse = QAction(u'降序')

        rightMenu.addAction(self.action_unlock)
        rightMenu.addAction(self.action_delete)
        rightMenu.addAction(self.action_sort)
        rightMenu.addAction(self.action_sort_reverse)

        self.action_unlock.triggered.connect(self.unlockpdf)
        self.action_delete.triggered.connect(self.delete_list_widget1)
        self.action_sort_reverse.triggered.connect(
            self.sort_reverse_list_widget)
        self.action_sort.triggered.connect(self.sort_list_widget)

        rightMenu.exec_(QCursor.pos())

    def contextmenu_listWidget2(self):  # 拆分區右鍵
        rightMenu = QMenu(self.PDF_Editor_UI.listWidget_2)
        self.action_unlock = QAction(u'解鎖')
        self.action_delete = QAction(u'刪除')
        rightMenu.addAction(self.action_unlock)
        rightMenu.addAction(self.action_delete)
        self.action_unlock.triggered.connect(self.unlockpdf2)
        self.action_delete.triggered.connect(self.delete_list_widget2)
        rightMenu.exec_(QCursor.pos())

    def delete_list_widget1(self):  # 合併區右鍵(刪除)
        items = self.PDF_Editor_UI.listWidget.selectedItems()
        if len(items) > 0:
            for item in items:
                self.PDF_Editor_UI.listWidget.takeItem(
                    self.PDF_Editor_UI.listWidget.row(item))
            self.PDF_Editor_UI.statusbar.showMessage("刪除成功！")
        else:
            self.PDF_Editor_UI.statusbar.showMessage("沒有選擇刪除項目！")

    def delete_list_widget2(self):  # 拆分區右鍵(刪除)
        items = self.PDF_Editor_UI.listWidget_2.selectedItems()
        if len(items) > 0:
            for item in items:
                self.PDF_Editor_UI.listWidget_2.takeItem(
                    self.PDF_Editor_UI.listWidget_2.row(item))
            self.PDF_Editor_UI.statusbar.showMessage("刪除成功！")
        else:
            self.PDF_Editor_UI.statusbar.showMessage("沒有選擇刪除項目！")

    def sort_list_widget(self):  # 右鍵(正向排序)
        self.PDF_Editor_UI.filename_list = []
        for index in range(self.PDF_Editor_UI.listWidget.count()):
            item = self.PDF_Editor_UI.listWidget.item(index)
            self.PDF_Editor_UI.filename_list.append(item.text())
        self.PDF_Editor_UI.listWidget.sortItems(QtCore.Qt.AscendingOrder)
        self.PDF_Editor_UI.filename_list.sort(reverse=False)
        self.PDF_Editor_UI.statusbar.showMessage("排序完成!")

    def sort_reverse_list_widget(self):  # 右鍵(反向排序)
        self.PDF_Editor_UI.filename_list = []
        for index in range(self.PDF_Editor_UI.listWidget.count()):
            item = self.PDF_Editor_UI.listWidget.item(index)
            self.PDF_Editor_UI.filename_list.append(item.text())
        self.PDF_Editor_UI.listWidget.sortItems(QtCore.Qt.DescendingOrder)
        self.PDF_Editor_UI.filename_list.sort(reverse=True)
        self.PDF_Editor_UI.statusbar.showMessage("排序完成!")

    def open_file_1(self):  # 合併區選擇檔案
        try:
            self.PDF_Editor_UI.progressBar1.reset()
            openfileNames = QFileDialog.getOpenFileNames(
                self.PDF_Editor_UI.centralwidget, "選擇pdf文件", "./", "PDF (*.pdf *.PDF)")
            if (len(openfileNames[0]) != 0):
                self.PDF_Editor_UI.statusbar.showMessage(
                    f"新增{str(len(openfileNames[0]))}個pdf文件成功")
                for file_path in openfileNames[0]:
                    if self.is_pdf_encrypted(file_path):
                        file_name = f'(請先解鎖此文件){basename(file_path).replace("(Lock)","")}'
                    else:
                        file_name = basename(file_path).replace("(Lock)", "")
                    item = QtWidgets.QListWidgetItem(file_name)
                    item.setToolTip(file_path.replace("/", "\\"))
                    self.PDF_Editor_UI.listWidget.addItem(item)
                self.PDF_Editor_UI.progressBar1.setValue(100)
                sleep(0.3)
                self.PDF_Editor_UI.progressBar1.reset()
        except Exception as e:
            self.PDF_Editor_UI.statusbar.showMessage("新增失敗")
            QMessageBox.critical(self, "新增失敗", e)

    def open_file_2(self):  # 拆分區選擇檔案
        try:
            self.PDF_Editor_UI.progressBar2.reset()
            openfileNames = QFileDialog.getOpenFileNames(
                self.PDF_Editor_UI.centralwidget, "選擇pdf文件", "./", "PDF (*.pdf *.PDF)")
            if (len(openfileNames[0]) != 0):
                self.PDF_Editor_UI.statusbar.showMessage(
                    f"新增{str(len(openfileNames[0]))}個pdf文件成功")
                for file_path in openfileNames[0]:
                    if self.is_pdf_encrypted(file_path):
                        file_name = f'(請先解鎖此文件){basename(file_path).replace("(Lock)","")}'
                    else:
                        file_name = basename(file_path).replace("(Lock)", "")
                    item = QtWidgets.QListWidgetItem(file_name)
                    item.setToolTip(file_path.replace("/", "\\"))
                    self.PDF_Editor_UI.listWidget_2.addItem(item)
                self.PDF_Editor_UI.progressBar2.setValue(100)
                sleep(0.3)
                self.PDF_Editor_UI.progressBar2.reset()
        except Exception as e:
            self.PDF_Editor_UI.statusbar.showMessage("新增失敗")

    def clear1(self):  # 合併區清除
        try:
            self.PDF_Editor_UI.filename_list = []
            self.PDF_Editor_UI.listWidget.clear()
            self.PDF_Editor_UI.statusbar.showMessage("清除成功")
            self.PDF_Editor_UI.progressBar1.setValue(100)
            sleep(0.3)
            self.PDF_Editor_UI.progressBar1.reset()
        except Exception as e:
            self.PDF_Editor_UI.statusbar.showMessage("清除失敗")

    def clear2(self):  # 拆分區清除
        try:
            self.PDF_Editor_UI.filename_list2 = []
            self.PDF_Editor_UI.listWidget_2.clear()
            self.PDF_Editor_UI.statusbar.showMessage("清除成功")
            self.PDF_Editor_UI.progressBar2.setValue(100)
            sleep(0.3)
            self.PDF_Editor_UI.progressBar2.reset()
        except Exception as e:
            self.PDF_Editor_UI.statusbar.showMessage("清除失敗")

    def floder(self):  # 開啟資料夾
        try:
            Popen('explorer "'+abspath(r'.\PDFtemp')+'"')
        except Exception as e:
            self.PDF_Editor_UI.statusbar.showMessage(
                "找不到路徑"+abspath(r'.\PDFtemp'))

    def lockpdf(self, path):  # 加密
        password, ok = QtWidgets.QInputDialog.getText(
            self, "請輸入密碼", "密碼:", QtWidgets.QLineEdit.Password)
        if ok:
            with open(f'{path}', 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                pdf_writer = PyPDF2.PdfWriter()
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    pdf_writer.add_page(page)
                pdf_writer.encrypt(password)
                with open(f'{path}', 'wb') as output_file:
                    pdf_writer.write(output_file)

    def unlockpdf(self):  # 合併區解鎖
        items = self.PDF_Editor_UI.listWidget.selectedItems()
        if not items:
            self.PDF_Editor_UI.statusbar.showMessage("沒有選擇文件!")
        else:
            for item in items:
                try:
                    file_path = item.toolTip()
                    pdf = PyPDF2.PdfReader(open(file_path, "rb"))
                    if pdf.is_encrypted:
                        password, ok = QtWidgets.QInputDialog.getText(
                            self, "請輸入密碼", "密碼:", QtWidgets.QLineEdit.Password)
                        password = password.strip()
                        pdf.decrypt(password)
                        pdf_writer = PyPDF2.PdfWriter()
                        for page_num in range(len(pdf.pages)):
                            page = pdf.pages[page_num]
                            pdf_writer.add_page(page)
                        new_pdf_file = join(split(file_path)[0], split(
                            file_path)[1].replace("(Lock)", ""))
                        with open(new_pdf_file, 'wb') as output_file:
                            pdf_writer.write(output_file)
                        filename = item.text().replace("請先解鎖此文件", "已解鎖")
                        item.setText(f"{filename}")
                        item.setToolTip(new_pdf_file.replace("/", "\\"))
                        self.PDF_Editor_UI.statusbar.showMessage(
                            f"{item.text()} 解鎖成功!")
                    else:
                        self.PDF_Editor_UI.statusbar.showMessage(
                            f"{item.text()} 未加密!")
                except Exception as e:
                    print(e)
                    self.PDF_Editor_UI.statusbar.showMessage("密碼錯誤!請重新輸入!")
                    QMessageBox.critical(self, "錯誤", "密碼錯誤!請重新輸入!")

    def unlockpdf2(self):  # 拆分區解鎖
        items = self.PDF_Editor_UI.listWidget_2.selectedItems()
        if not items:
            self.PDF_Editor_UI.statusbar.showMessage("沒有選擇文件!")
        else:
            for item in items:
                try:
                    file_path = item.toolTip()
                    pdf = PyPDF2.PdfReader(open(file_path, "rb"))
                    if pdf.is_encrypted:
                        password, ok = QtWidgets.QInputDialog.getText(
                            self, "請輸入密碼", "密碼:", QtWidgets.QLineEdit.Password)
                        password = password.strip()
                        pdf.decrypt(password)
                        pdf_writer = PyPDF2.PdfWriter()
                        for page_num in range(len(pdf.pages)):
                            page = pdf.pages[page_num]
                            pdf_writer.add_page(page)
                        new_pdf_file = join(split(file_path)[0], split(
                            file_path)[1].replace("(Lock)", ""))
                        with open(new_pdf_file, 'wb') as output_file:
                            pdf_writer.write(output_file)
                        filename = item.text().replace("請先解鎖此文件", "已解鎖")
                        item.setText(f"{filename}")
                        item.setToolTip(new_pdf_file.replace("/", "\\"))
                        self.PDF_Editor_UI.statusbar.showMessage(
                            f"{item.text()} 解鎖成功!")
                    else:
                        self.PDF_Editor_UI.statusbar.showMessage(
                            f"{item.text()} 未加密!")
                except Exception as e:
                    self.PDF_Editor_UI.statusbar.showMessage("密碼錯誤!請重新輸入!")
                    QMessageBox.critical(self, "錯誤", "密碼錯誤!請重新輸入!")

    def combine_pdf_action(self):  # 合併PDF
        try:
            self.PDF_Editor_UI.filename_list = []
            for index in range(self.PDF_Editor_UI.listWidget.count()):
                item = self.PDF_Editor_UI.listWidget.item(index)
                file_path = item.toolTip()
                self.PDF_Editor_UI.filename_list.append(file_path)
            if (len(self.PDF_Editor_UI.filename_list) != 0):
                if ('(請先解鎖此文件)'not in item.text()):
                    if (len(self.PDF_Editor_UI.filename.text()) == 0):
                        output = datetime.now().strftime("%Y%m%d%H%M%S")+"-合併文件.pdf"
                    else:
                        output = self.PDF_Editor_UI.filename.text()+".pdf"
                    writer = PdfWriter()
                    for i in range(len(self.PDF_Editor_UI.filename_list)):
                        reader = PdfReader(self.PDF_Editor_UI.filename_list[i])
                        writer.addpages(reader.pages)
                        self.PDF_Editor_UI.progressBar1.setRange(
                            0, len(self.PDF_Editor_UI.filename_list))
                        self.PDF_Editor_UI.progressBar1.setValue(i+1)
                        if (exists(join(split(self.PDF_Editor_UI.filename_list[i])[0], "(Lock)"+split(self.PDF_Editor_UI.filename_list[i])[1]))):
                            remove(self.PDF_Editor_UI.filename_list[i])
                    if self.PDF_Editor_UI.checkBox.isChecked():
                        output = "(Lock)"+output
                        writer.write(join(abspath(r'.\PDFtemp'), output))
                        self.lockpdf(join(abspath(r'.\PDFtemp'), output))
                    else:
                        writer.write(join(abspath(r'.\PDFtemp'), output))
                    writer.killobj
                    self.PDF_Editor_UI.statusbar.showMessage(
                        join("合併成功! 文件路徑 -> "+abspath(r'.\PDFtemp'), output))
                    sleep(0.3)
                    self.PDF_Editor_UI.progressBar1.reset()
                else:
                    self.PDF_Editor_UI.statusbar.showMessage("尚有文件未解鎖!")
                    QMessageBox.warning(self, "警告", "尚有文件未解鎖!")
            else:
                self.PDF_Editor_UI.statusbar.showMessage("沒有文件!")
        except Exception as e:
            self.PDF_Editor_UI.statusbar.showMessage("合併失敗!")
            QMessageBox.critical(self, "合併失敗!")

    def split(self):  # 拆分PDF
        try:
            n = 1
            self.PDF_Editor_UI.filename_list2 = []
            for index in range(self.PDF_Editor_UI.listWidget_2.count()):
                item = self.PDF_Editor_UI.listWidget_2.item(index)
                file_path = item.toolTip()
                self.PDF_Editor_UI.filename_list2.append(file_path)
            if (len(self.PDF_Editor_UI.filename_list2) != 0):
                if ('(請先解鎖此文件)'not in item.text()):
                    for file in self.PDF_Editor_UI.filename_list2:
                        with Pdf.open(file) as pdf:
                            pages = pdf.pages
                            if self.PDF_Editor_UI.buttongroup1.checkedId() == 1:
                                x = 0
                                for i in pages:
                                    if (len(self.PDF_Editor_UI.filename2.text()) == 0):
                                        new_pdfname = f'{datetime.now().strftime("%Y%m%d-%H%M%S")}-拆分文件(第{str(n)}頁).pdf'
                                    else:
                                        new_pdfname = f'{self.PDF_Editor_UI.filename2.text()}(第{str(n)}頁).pdf'
                                    output = Pdf.new()
                                    output.pages.append(i)
                                    output.save(
                                        join(abspath(r'.\PDFtemp'), new_pdfname))
                                    n = n + 1
                                    self.PDF_Editor_UI.progressBar2.setRange(
                                        0, len(pages))
                                    x = x + 1
                                    self.PDF_Editor_UI.progressBar2.setValue(x)
                                    self.PDF_Editor_UI.statusbar.showMessage(
                                        join("拆分成功! 文件路徑 -> "+abspath(r'.\PDFtemp'), new_pdfname))
                                sleep(0.3)
                                self.PDF_Editor_UI.progressBar2.reset()

                            elif self.PDF_Editor_UI.buttongroup1.checkedId() == 2:
                                output = Pdf.new()
                                index1 = self.PDF_Editor_UI.spinBox.value()
                                if index1 > 0:
                                    index1 -= 1
                                index2 = self.PDF_Editor_UI.spinBox_2.value()
                                if index2 > len(pages):
                                    index2 = len(pages)
                                elif index2 == 0:
                                    index2 = 1
                                if index1 <= index2:
                                    if (len(self.PDF_Editor_UI.filename2.text()) == 0):
                                        new_pdfname = f'{datetime.now().strftime("%Y%m%d-%H%M%S")}-拆分文件(第{str(index1+1)}-{str(index2)}頁).pdf'
                                    else:
                                        new_pdfname = f'{self.PDF_Editor_UI.filename2.text()}(第{str(index1+1)}-{str(index2)}頁).pdf'

                                    output.pages.extend(pages[index1:index2])
                                    output.save(
                                        join(abspath(r'.\PDFtemp'), new_pdfname))
                                    self.PDF_Editor_UI.progressBar2.setValue(
                                        100)
                                    self.PDF_Editor_UI.statusbar.showMessage(
                                        join("拆分成功! 文件路徑 -> "+abspath(r'.\PDFtemp'), new_pdfname))
                                    sleep(0.3)
                                    self.PDF_Editor_UI.progressBar2.reset()
                                else:
                                    self.PDF_Editor_UI.statusbar.showMessage(
                                        "第二個值必須>=第一個值!!!")
                                    QMessageBox.warning(
                                        self, "警告", "第二個值必須>=第一個值!!!")

                            elif self.PDF_Editor_UI.buttongroup1.checkedId() == 3:
                                output = Pdf.new()
                                index1 = self.PDF_Editor_UI.spinBox_3.value()
                                if index1 > 0:
                                    index1 -= 1
                                index2 = self.PDF_Editor_UI.spinBox_4.value()
                                if index2 > len(pages):
                                    index2 = len(pages)
                                elif index2 == 0:
                                    index2 = 1
                                for i in range(index1, len(pages), index2):
                                    if (len(self.PDF_Editor_UI.filename2.text()) == 0):
                                        if i+index2 <= len(pages):
                                            new_pdfname = f'{datetime.now().strftime("%Y%m%d-%H%M%S")}-拆分文件(第{str(i+1)}-{str(i+index2)}頁).pdf'
                                        else:
                                            new_pdfname = f'{datetime.now().strftime("%Y%m%d-%H%M%S")}-拆分文件(第{str(i+1)}-{str(len(pages))}頁).pdf'
                                    else:
                                        new_pdfname = f'{self.PDF_Editor_UI.filename2.text()}(第{str(i+1)}-{str(i+index2)}頁).pdf'
                                    output = Pdf.new()
                                    output.pages.extend(pdf.pages[i:i+index2])
                                    output.save(
                                        join(abspath(r'.\PDFtemp'), new_pdfname))
                                self.PDF_Editor_UI.progressBar2.setValue(100)
                                self.PDF_Editor_UI.statusbar.showMessage(
                                    join("拆分成功! 文件路徑 -> "+abspath(r'.\PDFtemp'), new_pdfname))
                                sleep(0.3)
                                self.PDF_Editor_UI.progressBar2.reset()

                        if (exists(join(split(file)[0], "(Lock)"+split(file)[1]))):
                            remove(file)
                else:
                    self.PDF_Editor_UI.statusbar.showMessage("尚有文件未解鎖!")
                    QMessageBox.warning(self, "警告", "尚有文件未解鎖!")
            else:
                self.PDF_Editor_UI.statusbar.showMessage("沒有文件!")
        except Exception as e:
            self.PDF_Editor_UI.statusbar.showMessage("拆分失敗!")
            QMessageBox.critical(self, "拆分失敗!", str(e))

    def is_pdf_encrypted(self, pdf_file):  # 判斷是否有上鎖
        try:
            pdf = PyPDF2.PdfReader(open(pdf_file, "rb"))
            return pdf.is_encrypted
        except Exception as e:
            print("無法讀取 PDF 文件:", str(e))
            return False

    def sign(self):  # 說明
        QMessageBox.about(self, "PDF Editor v2.2.0 使用說明", """
        v2.2.0更新 -- 新增多種拆分方式、介面調整、修復'合併後的文件會被程式占用'的錯誤 -2024/04/19
        v2.1.2更新 -- 新增加密/解密功能、僅顯示檔名(鼠標移到項目上才顯示完整路徑) -2023/11/06

        合併:

        選擇要合併的文件->輸入合併後的檔名->點擊"開始"按鈕進行合併

        合併完的檔案可在"開啟資料夾"查看

        清除:這會清空列表內所有內容

        刪除:選擇列表內的項目點擊右鍵或Delete，可刪除項目

        排序:在列表中點擊右鍵可以進行全部排序，也可自行拖拉排序
        
        加密:勾選後，可在合併後的PDF文件加密
                          
        解鎖:右鍵->輸入文件->解除鎖定後才能合併
        -----
        拆分:

        選擇一個或多個文件->選擇拆分模式

        刪除:選擇列表內的項目點擊右鍵或Delete，可刪除項目
                          
        解鎖:右鍵->輸入文件->解除鎖定後才能拆分
        -----
        
        ##################################
        Author: Ping
        Description: PDF Editor v2.2.0
        Date: 2024-04-19
        ©2024 United Credit Services IT Ping - Tel:7650
        ##################################
        """)


if __name__ == '__main__':
    import sys
    if not isdir(abspath(r'.\PDFtemp')):
        makedirs(abspath(r'.\PDFtemp'))
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow_controller()
    window.setWindowTitle(
        "PDF Editor v2.2.0     ©2024 United Credit Services IT Ping - Tel:7650")
    window.setWindowIcon(QIcon(r'.\pdf.jpg'))
    window.show()
    sys.exit(app.exec_())
