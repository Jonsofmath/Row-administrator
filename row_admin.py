# ***********************************************************************
# Program that simulates a queue manager in a bank. Will generate 3
# windows that simulate the following:
# Input station -> simulates the touch terminal through which the
# users choose the procedure to carry out.
# Employee view -> each button simulates the trigger that each employee
# would have in your cubicle to ask for a new customer.
# Main screen -> Simulates the screen that we always see in banks
# where it is announced who is being cared for and where.
#
# Communication between screens is done through an MQTT server
# provided by the teacher.
#
# Made by Jairo Cortes and Jonathan Ramirez in June, 2021

import sys
import paho.mqtt.client as mqtt

from PySide6 import QtCore, QtWidgets, QtGui

counter = 0       # clients counter
CajaClients = []  # array of users waiting for "cajas"
PlatClients = []  # array of users waiting for "plataforma"
ServClients = []  # array of users waiting for "servicio cliente"


# **********************************************
# MQTT Entry Station Class
# **********************************************
class MQTTEntryStation(QtWidgets.QWidget):
    def __init__(self):
        # - Initialize the parent class
        super().__init__()
        # - Class member to store the MQTT client object
        self.mqtt_client = None

    # - Text labels
        self.setWindowTitle('Estacion de Entrada')
        self.setGeometry(100, 100, 400, 150)

    # - Declaration of a layout container
        self.wellcometext = QtWidgets.QLabel(
            'Bienvenido, escoja su tramite', alignment=QtCore.Qt.AlignTop)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.wellcometext)

        # buttons creation
        self.cajas = QtWidgets.QPushButton('cajas', self)
        self.plataforma = QtWidgets.QPushButton('Plataforma', self)
        self.ServClient = QtWidgets.QPushButton('Servicio al cliente', self)
        self.cajas.adjustSize()
        self.plataforma.adjustSize()
        self.ServClient.adjustSize()
        self.cajas.move(15, 70)
        self.plataforma.move(140, 70)
        self.ServClient.move(270, 70)

        # capture button events
        self.cajas.clicked.connect(self.SendMessageCajas)
        self.plataforma.clicked.connect(self.SendMessagePlat)
        self.ServClient.clicked.connect(self.SendMessageSCT)

    # send a message depending on the button pressed
    @QtCore.Slot()
    def SendMessageCajas(self):
        self.mqtt_client.publish("cajas", "cliente")

    @QtCore.Slot()
    def SendMessagePlat(self):
        self.mqtt_client.publish("plataforma", "cliente")

    @QtCore.Slot()
    def SendMessageSCT(self):
        self.mqtt_client.publish("servcliente", "cliente")

    def set_client(self, new_mqtt_client):
        # - Assign the mqtt client
        self.mqtt_client = new_mqtt_client


# **********************************************
# MQTT Employee Station Class
# **********************************************
class MQTTEmployeeStation(QtWidgets.QWidget):
    def __init__(self):
        # - Initialize the parent class
        super().__init__()
        # - Class member to store the MQTT client object
        self.mqtt_client = None

    # - Text labels
        self.setWindowTitle('Vista de empleados')
        self.setGeometry(100, 100, 300, 400)

        # - Declaration of a layout container
        self.layout = QtWidgets.QVBoxLayout(self)

        # buttons creation
        self.caja1 = QtWidgets.QPushButton('caja1', self)
        self.caja2 = QtWidgets.QPushButton('caja2', self)
        self.caja3 = QtWidgets.QPushButton('caja3', self)
        self.plat = QtWidgets.QPushButton('plataforma1', self)
        self.serv = QtWidgets.QPushButton('servclient1', self)
        self.caja1.move(100, 30)
        self.caja2.move(100, 70)
        self.caja3.move(100, 110)
        self.plat.move(100, 190)
        self.serv.move(100, 280)

        # capture button events
        self.caja1.clicked.connect(self.SendMessageCaja1)
        self.caja2.clicked.connect(self.SendMessageCaja2)
        self.caja3.clicked.connect(self.SendMessageCaja3)
        self.plat.clicked.connect(self.SendMessagePlat)
        self.serv.clicked.connect(self.SendMessageServ)

    # send a message depending on the button pressed
    @QtCore.Slot()
    def SendMessageCaja1(self):
        self.mqtt_client.publish("cajas", "caja1")

    @QtCore.Slot()
    def SendMessageCaja2(self):
        self.mqtt_client.publish("cajas", "caja2")

    @QtCore.Slot()
    def SendMessageCaja3(self):
        self.mqtt_client.publish("cajas", "caja3")

    @QtCore.Slot()
    def SendMessagePlat(self):
        self.mqtt_client.publish("plataforma", "plataforma")

    @QtCore.Slot()
    def SendMessageServ(self):
        self.mqtt_client.publish("servcliente", "Serv-Cliente")

    def set_client(self, new_mqtt_client):
        # - Assign the mqtt client
        self.mqtt_client = new_mqtt_client


# **********************************************
# MQTT Main Station Class
# **********************************************
class MQTTMainStation(QtWidgets.QWidget):
    def __init__(self):
        # - Initialize the parent class
        super().__init__()
        # - Class member to store the MQTT client object
        self.mqtt_client = None

    # - Text labels
        self.setWindowTitle('Pantalla Principal')
        self.setGeometry(100, 100, 400, 150)

    # - Declaration of a layout container
        self.wellcometext = QtWidgets.QLabel(
            'Bienvenido al Banco', alignment=QtCore.Qt.AlignTop)
        self.text1 = QtWidgets.QLabel("cliente:", self)
        self.text1.move(115, 50)
        self.text2 = QtWidgets.QLabel("en:", self)
        self.text2.move(135, 70)
        self.ticket = QtWidgets.QLabel("----", self)
        self.ticket.move(170, 50)
        self.Where = QtWidgets.QLabel("----", self)
        self.Where.move(170, 70)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.wellcometext)

    def set_client(self, new_mqtt_client):
        # - Assign the mqtt client
        self.mqtt_client = new_mqtt_client

    def on_message(self, client, userdata, message):
        global counter
        # if message comes from users, should be filtered
        messagein = str(message.payload.decode("utf-8"))
        if messagein == 'cliente':
            counter = counter+1
            if message.topic == 'cajas':
                CajaClients.append(counter)
            elif message.topic == 'plataforma':
                PlatClients.append(counter)
            else:
                ServClients.append(counter)
            print("fila en cajas: ", CajaClients)
            print("fila en plataforma: ", PlatClients)
            print("fila en servicio al cliente: ", ServClients)
        elif messagein == 'plataforma':
            try:
                user = PlatClients.pop(0)
                self.ticket.setText(str(user))
                self.Where.setText(messagein)
            except IndexError:
                print("No hay clientes esperando Plataforma")

        elif messagein == 'Serv-Cliente':
            try:
                user = ServClients.pop(0)
                self.ticket.setText(str(user))
                self.Where.setText(messagein)
            except IndexError:
                print("No hay clientes esperando Servicio")
        else:
            try:
                user = CajaClients.pop(0)
                self.ticket.setText(str(user))
                self.Where.setText(messagein)
            except IndexError:
                print("No hay clientes esperando Cajas")


# - Main entry point
if __name__ == "__main__":
    # - Declaring the QT Application
    app = QtWidgets.QApplication([])
# - Adding widgets
    entrystation = MQTTEntryStation()
    employeestation = MQTTEmployeeStation()
    mainstation = MQTTMainStation()

    # MQTT client for users interface
    userclient = mqtt.Client()
    userclient.connect("172.104.194.159", 1884)
    userclient.loop_start()
    userclient.subscribe([("cajas", 2), ("plataforma", 1), ("servcliente", 0)])
    entrystation.set_client(userclient)

    # MQTT client for employees interface
    employeeclient = mqtt.Client()
    employeeclient.connect("172.104.194.159", 1884)
    employeeclient.loop_start()
    employeeclient.subscribe(
        [("cajas", 2), ("plataforma", 1), ("servcliente", 0)])
    employeestation.set_client(employeeclient)

    # MQTT client for Main Screen interface
    MainClient = mqtt.Client()
    MainClient.connect("172.104.194.159", 1884)
    MainClient.loop_start()
    MainClient.on_message = mainstation.on_message
    MainClient.subscribe([("cajas", 2), ("plataforma", 1), ("servcliente", 0)])
    mainstation.set_client(MainClient)

    entrystation.show()
    employeestation.show()
    mainstation.show()
    sys.exit(app.exec())  # MQTT client for users interface
