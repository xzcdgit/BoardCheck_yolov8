# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'd:\Code\Python\BoardCheck_yolov8\Main.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(932, 737)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/imgs/TitleLogo.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setIconSize(QtCore.QSize(24, 24))
        MainWindow.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setStyleSheet("")
        self.tabWidget.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.tabWidget.setObjectName("tabWidget")
        self.tab_3 = QtWidgets.QWidget()
        self.tab_3.setStyleSheet("border-image: url(:/imgs/background.png);")
        self.tab_3.setObjectName("tab_3")
        self.gridLayout_14 = QtWidgets.QGridLayout(self.tab_3)
        self.gridLayout_14.setObjectName("gridLayout_14")
        self.tabWidget.addTab(self.tab_3, "")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.gridLayout = QtWidgets.QGridLayout(self.tab)
        self.gridLayout.setObjectName("gridLayout")
        self.label_output_sts = QtWidgets.QLabel(self.tab)
        self.label_output_sts.setObjectName("label_output_sts")
        self.gridLayout.addWidget(self.label_output_sts, 0, 6, 1, 1)
        self.label_input_sts = QtWidgets.QLabel(self.tab)
        self.label_input_sts.setObjectName("label_input_sts")
        self.gridLayout.addWidget(self.label_input_sts, 0, 5, 1, 1)
        self.label_body_num = QtWidgets.QLabel(self.tab)
        self.label_body_num.setObjectName("label_body_num")
        self.gridLayout.addWidget(self.label_body_num, 0, 3, 1, 1)
        self.label_img1_show = QtWidgets.QLabel(self.tab)
        self.label_img1_show.setTextFormat(QtCore.Qt.AutoText)
        self.label_img1_show.setAlignment(QtCore.Qt.AlignCenter)
        self.label_img1_show.setObjectName("label_img1_show")
        self.gridLayout.addWidget(self.label_img1_show, 2, 0, 1, 7)
        self.label_camera_sts = QtWidgets.QLabel(self.tab)
        self.label_camera_sts.setWordWrap(False)
        self.label_camera_sts.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse)
        self.label_camera_sts.setObjectName("label_camera_sts")
        self.gridLayout.addWidget(self.label_camera_sts, 0, 0, 1, 1)
        self.label_arclight_num = QtWidgets.QLabel(self.tab)
        self.label_arclight_num.setObjectName("label_arclight_num")
        self.gridLayout.addWidget(self.label_arclight_num, 0, 4, 1, 1)
        self.label_io_sts = QtWidgets.QLabel(self.tab)
        self.label_io_sts.setObjectName("label_io_sts")
        self.gridLayout.addWidget(self.label_io_sts, 0, 1, 1, 1)
        self.label_fps = QtWidgets.QLabel(self.tab)
        self.label_fps.setObjectName("label_fps")
        self.gridLayout.addWidget(self.label_fps, 0, 2, 1, 1)
        self.label_board_size = QtWidgets.QLabel(self.tab)
        self.label_board_size.setObjectName("label_board_size")
        self.gridLayout.addWidget(self.label_board_size, 1, 0, 1, 3)
        self.gridLayout.setRowMinimumHeight(0, 1)
        self.gridLayout.setRowMinimumHeight(1, 30)
        self.gridLayout.setRowStretch(2, 1)
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.gridLayout_13 = QtWidgets.QGridLayout(self.tab_2)
        self.gridLayout_13.setObjectName("gridLayout_13")
        self.groupBox_9 = QtWidgets.QGroupBox(self.tab_2)
        self.groupBox_9.setObjectName("groupBox_9")
        self.gridLayout_11 = QtWidgets.QGridLayout(self.groupBox_9)
        self.gridLayout_11.setObjectName("gridLayout_11")
        self.groupBox_6 = QtWidgets.QGroupBox(self.groupBox_9)
        self.groupBox_6.setObjectName("groupBox_6")
        self.gridLayout_8 = QtWidgets.QGridLayout(self.groupBox_6)
        self.gridLayout_8.setObjectName("gridLayout_8")
        self.lineEdit_3 = QtWidgets.QLineEdit(self.groupBox_6)
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.gridLayout_8.addWidget(self.lineEdit_3, 2, 1, 1, 1)
        self.label_8 = QtWidgets.QLabel(self.groupBox_6)
        self.label_8.setObjectName("label_8")
        self.gridLayout_8.addWidget(self.label_8, 0, 0, 1, 1)
        self.label_9 = QtWidgets.QLabel(self.groupBox_6)
        self.label_9.setObjectName("label_9")
        self.gridLayout_8.addWidget(self.label_9, 1, 0, 1, 1)
        self.label_10 = QtWidgets.QLabel(self.groupBox_6)
        self.label_10.setObjectName("label_10")
        self.gridLayout_8.addWidget(self.label_10, 2, 0, 1, 1)
        self.lineEdit = QtWidgets.QLineEdit(self.groupBox_6)
        self.lineEdit.setObjectName("lineEdit")
        self.gridLayout_8.addWidget(self.lineEdit, 0, 1, 1, 1)
        self.label_11 = QtWidgets.QLabel(self.groupBox_6)
        self.label_11.setObjectName("label_11")
        self.gridLayout_8.addWidget(self.label_11, 3, 0, 1, 1)
        self.lineEdit_2 = QtWidgets.QLineEdit(self.groupBox_6)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.gridLayout_8.addWidget(self.lineEdit_2, 1, 1, 1, 1)
        self.lineEdit_4 = QtWidgets.QLineEdit(self.groupBox_6)
        self.lineEdit_4.setText("")
        self.lineEdit_4.setEchoMode(QtWidgets.QLineEdit.Password)
        self.lineEdit_4.setObjectName("lineEdit_4")
        self.gridLayout_8.addWidget(self.lineEdit_4, 3, 1, 1, 1)
        self.gridLayout_11.addWidget(self.groupBox_6, 0, 0, 1, 1)
        self.groupBox_7 = QtWidgets.QGroupBox(self.groupBox_9)
        self.groupBox_7.setObjectName("groupBox_7")
        self.gridLayout_9 = QtWidgets.QGridLayout(self.groupBox_7)
        self.gridLayout_9.setObjectName("gridLayout_9")
        self.label_12 = QtWidgets.QLabel(self.groupBox_7)
        self.label_12.setObjectName("label_12")
        self.gridLayout_9.addWidget(self.label_12, 0, 0, 1, 1)
        self.lineEdit_5 = QtWidgets.QLineEdit(self.groupBox_7)
        self.lineEdit_5.setObjectName("lineEdit_5")
        self.gridLayout_9.addWidget(self.lineEdit_5, 0, 1, 1, 1)
        self.label_13 = QtWidgets.QLabel(self.groupBox_7)
        self.label_13.setObjectName("label_13")
        self.gridLayout_9.addWidget(self.label_13, 1, 0, 1, 1)
        self.lineEdit_6 = QtWidgets.QLineEdit(self.groupBox_7)
        self.lineEdit_6.setObjectName("lineEdit_6")
        self.gridLayout_9.addWidget(self.lineEdit_6, 1, 1, 1, 1)
        self.label_14 = QtWidgets.QLabel(self.groupBox_7)
        self.label_14.setObjectName("label_14")
        self.gridLayout_9.addWidget(self.label_14, 2, 0, 1, 1)
        self.lineEdit_7 = QtWidgets.QLineEdit(self.groupBox_7)
        self.lineEdit_7.setObjectName("lineEdit_7")
        self.gridLayout_9.addWidget(self.lineEdit_7, 2, 1, 1, 1)
        self.gridLayout_11.addWidget(self.groupBox_7, 0, 1, 1, 1)
        self.groupBox_8 = QtWidgets.QGroupBox(self.groupBox_9)
        self.groupBox_8.setObjectName("groupBox_8")
        self.gridLayout_10 = QtWidgets.QGridLayout(self.groupBox_8)
        self.gridLayout_10.setObjectName("gridLayout_10")
        self.label_16 = QtWidgets.QLabel(self.groupBox_8)
        self.label_16.setObjectName("label_16")
        self.gridLayout_10.addWidget(self.label_16, 1, 0, 1, 1)
        self.label_15 = QtWidgets.QLabel(self.groupBox_8)
        self.label_15.setObjectName("label_15")
        self.gridLayout_10.addWidget(self.label_15, 0, 0, 1, 1)
        self.lineEdit_9 = QtWidgets.QLineEdit(self.groupBox_8)
        self.lineEdit_9.setObjectName("lineEdit_9")
        self.gridLayout_10.addWidget(self.lineEdit_9, 1, 1, 1, 1)
        self.lineEdit_8 = QtWidgets.QLineEdit(self.groupBox_8)
        self.lineEdit_8.setObjectName("lineEdit_8")
        self.gridLayout_10.addWidget(self.lineEdit_8, 0, 1, 1, 1)
        self.gridLayout_11.addWidget(self.groupBox_8, 0, 2, 1, 1)
        self.gridLayout_13.addWidget(self.groupBox_9, 0, 0, 1, 1)
        self.groupBox_10 = QtWidgets.QGroupBox(self.tab_2)
        self.groupBox_10.setObjectName("groupBox_10")
        self.groupBox_11 = QtWidgets.QGroupBox(self.groupBox_10)
        self.groupBox_11.setGeometry(QtCore.QRect(30, 30, 261, 151))
        self.groupBox_11.setObjectName("groupBox_11")
        self.gridLayout_12 = QtWidgets.QGridLayout(self.groupBox_11)
        self.gridLayout_12.setObjectName("gridLayout_12")
        self.label_21 = QtWidgets.QLabel(self.groupBox_11)
        self.label_21.setObjectName("label_21")
        self.gridLayout_12.addWidget(self.label_21, 0, 0, 1, 1)
        self.label_20 = QtWidgets.QLabel(self.groupBox_11)
        self.label_20.setObjectName("label_20")
        self.gridLayout_12.addWidget(self.label_20, 0, 1, 1, 1)
        self.label_22 = QtWidgets.QLabel(self.groupBox_11)
        self.label_22.setObjectName("label_22")
        self.gridLayout_12.addWidget(self.label_22, 0, 2, 1, 1)
        self.label_18 = QtWidgets.QLabel(self.groupBox_11)
        self.label_18.setObjectName("label_18")
        self.gridLayout_12.addWidget(self.label_18, 1, 0, 1, 1)
        self.doubleSpinBox_4 = QtWidgets.QDoubleSpinBox(self.groupBox_11)
        self.doubleSpinBox_4.setMaximum(1.0)
        self.doubleSpinBox_4.setObjectName("doubleSpinBox_4")
        self.gridLayout_12.addWidget(self.doubleSpinBox_4, 1, 1, 1, 1)
        self.doubleSpinBox_5 = QtWidgets.QDoubleSpinBox(self.groupBox_11)
        self.doubleSpinBox_5.setMaximum(1.0)
        self.doubleSpinBox_5.setObjectName("doubleSpinBox_5")
        self.gridLayout_12.addWidget(self.doubleSpinBox_5, 1, 2, 1, 1)
        self.label_19 = QtWidgets.QLabel(self.groupBox_11)
        self.label_19.setObjectName("label_19")
        self.gridLayout_12.addWidget(self.label_19, 2, 0, 1, 1)
        self.doubleSpinBox_2 = QtWidgets.QDoubleSpinBox(self.groupBox_11)
        self.doubleSpinBox_2.setMaximum(1.0)
        self.doubleSpinBox_2.setObjectName("doubleSpinBox_2")
        self.gridLayout_12.addWidget(self.doubleSpinBox_2, 2, 1, 1, 1)
        self.doubleSpinBox_3 = QtWidgets.QDoubleSpinBox(self.groupBox_11)
        self.doubleSpinBox_3.setMaximum(1.0)
        self.doubleSpinBox_3.setObjectName("doubleSpinBox_3")
        self.gridLayout_12.addWidget(self.doubleSpinBox_3, 2, 2, 1, 1)
        self.groupBox_12 = QtWidgets.QGroupBox(self.groupBox_10)
        self.groupBox_12.setGeometry(QtCore.QRect(320, 40, 241, 131))
        self.groupBox_12.setObjectName("groupBox_12")
        self.gridLayout_15 = QtWidgets.QGridLayout(self.groupBox_12)
        self.gridLayout_15.setObjectName("gridLayout_15")
        self.doubleSpinBox = QtWidgets.QDoubleSpinBox(self.groupBox_12)
        self.doubleSpinBox.setObjectName("doubleSpinBox")
        self.gridLayout_15.addWidget(self.doubleSpinBox, 0, 0, 1, 1)
        self.pushButton_2 = QtWidgets.QPushButton(self.groupBox_10)
        self.pushButton_2.setEnabled(False)
        self.pushButton_2.setGeometry(QtCore.QRect(730, 100, 122, 23))
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton = QtWidgets.QPushButton(self.groupBox_10)
        self.pushButton.setEnabled(False)
        self.pushButton.setGeometry(QtCore.QRect(602, 100, 122, 23))
        self.pushButton.setObjectName("pushButton")
        self.groupBox = QtWidgets.QGroupBox(self.groupBox_10)
        self.groupBox.setGeometry(QtCore.QRect(749, 230, 143, 44))
        self.groupBox.setObjectName("groupBox")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.label_7 = QtWidgets.QLabel(self.groupBox)
        self.label_7.setObjectName("label_7")
        self.gridLayout_5.addWidget(self.label_7, 0, 0, 1, 1)
        self.groupBox_3 = QtWidgets.QGroupBox(self.groupBox_10)
        self.groupBox_3.setGeometry(QtCore.QRect(450, 230, 143, 44))
        self.groupBox_3.setObjectName("groupBox_3")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.groupBox_3)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.label_3 = QtWidgets.QLabel(self.groupBox_3)
        self.label_3.setObjectName("label_3")
        self.gridLayout_4.addWidget(self.label_3, 0, 0, 1, 1)
        self.groupBox_4 = QtWidgets.QGroupBox(self.groupBox_10)
        self.groupBox_4.setGeometry(QtCore.QRect(599, 230, 144, 44))
        self.groupBox_4.setObjectName("groupBox_4")
        self.gridLayout_6 = QtWidgets.QGridLayout(self.groupBox_4)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.label_6 = QtWidgets.QLabel(self.groupBox_4)
        self.label_6.setObjectName("label_6")
        self.gridLayout_6.addWidget(self.label_6, 0, 0, 1, 1)
        self.gridLayout_13.addWidget(self.groupBox_10, 1, 0, 1, 1)
        self.tabWidget.addTab(self.tab_2, "")
        self.gridLayout_3.addWidget(self.tabWidget, 0, 0, 2, 8)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 932, 23))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "中集-板检系统"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), _translate("MainWindow", "首页"))
        self.label_output_sts.setText(_translate("MainWindow", "输出"))
        self.label_input_sts.setText(_translate("MainWindow", "输入"))
        self.label_body_num.setText(_translate("MainWindow", "叠板"))
        self.label_img1_show.setText(_translate("MainWindow", "板材检测"))
        self.label_camera_sts.setText(_translate("MainWindow", "相机"))
        self.label_arclight_num.setText(_translate("MainWindow", "人检"))
        self.label_io_sts.setText(_translate("MainWindow", "io模块"))
        self.label_fps.setText(_translate("MainWindow", "FPS:0"))
        self.label_board_size.setText(_translate("MainWindow", "板材尺寸："))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "数据显示"))
        self.groupBox_9.setTitle(_translate("MainWindow", "常规参数"))
        self.groupBox_6.setTitle(_translate("MainWindow", "相机参数"))
        self.label_8.setText(_translate("MainWindow", "ip"))
        self.label_9.setText(_translate("MainWindow", "端口"))
        self.label_10.setText(_translate("MainWindow", "用户名"))
        self.label_11.setText(_translate("MainWindow", "密码"))
        self.groupBox_7.setTitle(_translate("MainWindow", "PLC参数"))
        self.label_12.setText(_translate("MainWindow", "ip"))
        self.label_13.setText(_translate("MainWindow", "端口"))
        self.label_14.setText(_translate("MainWindow", "超时时间"))
        self.groupBox_8.setTitle(_translate("MainWindow", "文件设置"))
        self.label_16.setText(_translate("MainWindow", "图像记录地址"))
        self.label_15.setText(_translate("MainWindow", "AI模型地址"))
        self.groupBox_10.setTitle(_translate("MainWindow", "AI解析设置"))
        self.groupBox_11.setTitle(_translate("MainWindow", "ROI"))
        self.label_21.setText(_translate("MainWindow", "\\"))
        self.label_20.setText(_translate("MainWindow", "X"))
        self.label_22.setText(_translate("MainWindow", "Y"))
        self.label_18.setText(_translate("MainWindow", "ori点1"))
        self.label_19.setText(_translate("MainWindow", "ori点2"))
        self.groupBox_12.setTitle(_translate("MainWindow", "置信度设置"))
        self.pushButton_2.setText(_translate("MainWindow", "停止"))
        self.pushButton.setText(_translate("MainWindow", "运行"))
        self.groupBox.setTitle(_translate("MainWindow", "信号输出"))
        self.label_7.setText(_translate("MainWindow", "否"))
        self.groupBox_3.setTitle(_translate("MainWindow", "人体检测"))
        self.label_3.setText(_translate("MainWindow", "否"))
        self.groupBox_4.setTitle(_translate("MainWindow", "弧光检测"))
        self.label_6.setText(_translate("MainWindow", "否"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "参数设置"))
import img_rc
