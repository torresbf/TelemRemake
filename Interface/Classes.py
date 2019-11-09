import numpy as np
import copy
from datetime import datetime


# Data armazena os dados atuais
class Data:
    def __init__(self):
        # Constantes
        self.wheelPosMax = 0
        self.wheelPosMin = 0
        self.pSizes = [16, 22, 16, 30]

        # Dados
        self.p1Order = ['acelX', 'acelY', 'acelZ', 'velDD', 'velT', 'sparkCut', 'suspPos', 'time']
        self.p2Order = ['oleoP', 'fuelP', 'tps', 'rearBrakeP', 'frontBrakeP', 'volPos', 'beacon', 'correnteBat', 'rpm', 'time2']
        self.p3Order = ['ect', 'batVoltage', 'releBomba', 'releVent', 'pduTemp', 'tempDiscoD', 'tempDiscoE', 'time3']
        self.p4Order = ['ext1', 'ext2', 'ext3', 'ext4', 'ext5', 'ext6', 'ext7', 'ext8', 'time4']
        self.updateDataFunctions = {1: self.updateP1Data, 2: self.updateP2Data, 3: self.updateP3Data, 4: self.updateP4Data}

        self.dic = {
            'acelX': 0,
            'acelY': 0,
            'acelZ': 0,
            'velDD': 0,
            'velT': 0,
            'sparkCut': 0,
            'suspPos': 0,
            'oleoP': 0,
            'fuelP': 0,
            'tps': 0,
            'rearBrakeP': 0,
            'frontBrakeP': 0,
            'volPos': 0,
            'beacon': 0,
            'correnteBat': 0,
            'rpm': 0,
            'ect': 0,
            'batVoltage': 0,
            'releBomba': 0,
            'releVent': 0,
            'pduTemp': 0,
            'tempDiscoD': 0,
            'tempDiscoE': 0,
            'time': 0,
            'time2': 0,
            'time3': 0,
            'time4': 0,
            'ext1': 0,
            'ext2': 0,
            'ext3': 0,
            'ext4': 0,
            'ext5': 0,
            'ext6': 0,
            'ext7': 0,
            'ext8': 0,
        }

        self.dicRaw = copy.deepcopy(self.dic)
        self.alarms = copy.deepcopy(self.dic)
        # Configura alarmes padrao
        self.setDefaultAlarms()
        self.arrayTemp = np.zeros(50)
        self.arrayFuelP = np.zeros(50)
        self.arrayOilP = np.zeros(50)
        self.arrayBattery = np.zeros(50)
        self.arrayTime2 = np.zeros(50)
        self.arrayTime3 = np.zeros(50)

    def setDefaultAlarms(self):
        for key in self.alarms:
            self.alarms[key] = []
        self.alarms['batVoltage'] = [11.5, 'lesser than']
        self.alarms['ect'] = [95, 'greater than']

    # Caso valor seja signed, é necessario trata-lo como complemento de 2
    def twosComplement(self, number, bits):
        if (number & (1 << (bits - 1))) != 0:
            number = number - (1 << bits)        # compute negative value
        return number

    def updateP1Data(self, buffer):
        # recebe o valor contido na lista de dados(leitura) em suas respectivas posições e realiza as operações de deslocamento e soma binária
        if ((int(buffer[0]) == 1) and (len(buffer) == self.pSizes[0])):  # testa se é o pacote 1 e está completo
            self.dicRaw['acelX'] = (int(buffer[2]) << 8) + int(buffer[3])
            self.dicRaw['acelX'] = self.twosComplement(self.dicRaw['acelX'], 16)
            self.dic['acelX'] = round(float(self.dicRaw['acelX'] / 16384), 3)

            self.dicRaw['acelY'] = (int(buffer[4]) << 8) + int(buffer[5])
            self.dicRaw['acelY'] = self.twosComplement(self.dicRaw['acelY'], 16)
            self.dic['acelY'] = round(float(self.dicRaw['acelY'] / 16384), 3)

            self.dicRaw['acelZ'] = (int(buffer[6]) << 8) + int(buffer[7])
            self.dicRaw['acelZ'] = self.twosComplement(self.dicRaw['acelZ'], 16)
            self.dic['acelZ'] = round(float(self.dicRaw['acelZ'] / 16384), 3)

            self.dic['velDD'] = int(buffer[8])
            self.dicRaw['velDD'] = int(buffer[8])
            self.dic['velT'] = int(buffer[9])
            self.dicRaw['velT'] = int(buffer[9])
            self.dicRaw['sparkCut'] = ((buffer[10]) & 128) >> 7
            self.dic['sparkCut'] = self.dicRaw['sparkCut']
            self.dicRaw['suspPos'] = (((buffer[10]) & 127) << 8) + int(buffer[11])
            self.dic['suspPos'] = self.dicRaw['suspPos']
            self.dicRaw['time'] = ((buffer[12]) << 8) + int(buffer[13])
            self.dic['time'] = 25 * self.dicRaw['time']
            return 1
        else:
            return 0

    def updateP2Data(self, buffer):
        if ((int(buffer[0]) == 2) and (len(buffer) == self.pSizes[1])):  # testa se é o pacote 2 e está completo
            self.dicRaw['oleoP'] = (int(buffer[2]) << 8) + int(buffer[3])
            self.dic['oleoP'] = round(float(self.dicRaw['oleoP'] * 0.001), 4)
            self.dicRaw['fuelP'] = (int(buffer[4]) << 8) + int(buffer[5])
            self.dic['fuelP'] = round(float(self.dicRaw['fuelP'] * 0.001), 4)
            self.dicRaw['tps'] = (int(buffer[6]) << 8) + int(buffer[7])
            self.dic['tps'] = self.dicRaw['tps']
            self.dicRaw['rearBrakeP'] = (int(buffer[8]) << 8) + int(buffer[9])
            self.dic['rearBrakeP'] = round(self.dicRaw['rearBrakeP'] * 0.02536, 1)
            self.dicRaw['frontBrakeP'] = (int(buffer[10]) << 8) + int(buffer[11])
            self.dic['frontBrakeP'] = round(self.dicRaw['frontBrakeP'] * 0.02536, 1)
            self.dicRaw['volPos'] = (int(buffer[12]) << 8) + int(buffer[13])
            if self.wheelPosMax - self.wheelPosMin != 0:
                self.dic['volPos'] = round(((self.dicRaw['volPos'] - self.wheelPosMin) * 240 / (self.wheelPosMax - self.wheelPosMin) - 120), 2)
            self.dicRaw['beacon'] = int(buffer[14] >> 7)
            self.dic['beacon'] = self.dicRaw['beacon']
            self.dicRaw['correnteBat'] = ((int(buffer[14]) & 127) << 8) + int(buffer[15])
            self.dic['correnteBat'] = self.dicRaw['correnteBat']
            self.dicRaw['rpm'] = (int(buffer[16]) << 8) + int(buffer[17])
            self.dic['rpm'] = self.dicRaw['rpm']
            self.dicRaw['time2'] = (int(buffer[18]) << 8) + int(buffer[19])
            self.dic['time2'] = 25 * self.dicRaw['time2']
            return 1
        else:
            return 0

    def updateP3Data(self, buffer):
        if ((int(buffer[0]) == 3) and (len(buffer) == self.pSizes[2])):  # testa se é o pacote 3 e está completo

            self.dicRaw['ect'] = (buffer[2] << 8) + buffer[3]
            self.dic['ect'] = round(float(self.dicRaw['ect'] * 0.1), 2)
            self.dicRaw['batVoltage'] = (buffer[4] << 8) + (buffer[5])
            self.dic['batVoltage'] = round(float(self.dicRaw['batVoltage'] * 0.01), 2)
            self.dicRaw['releBomba'] = int((buffer[6] & 128) >> 7)
            self.dic['releBomba'] = self.dicRaw['releBomba']
            self.dicRaw['releVent'] = int((buffer[6] & 32) >> 5)
            self.dic['releVent'] = self.dicRaw['releVent']
            self.dicRaw['pduTemp'] = (buffer[7] << 8) + buffer[7]
            self.dic['pduTemp'] = round(float(self.dicRaw['pduTemp']), 2)
            self.dicRaw['tempDiscoE'] = (buffer[8] << 8) + buffer[9]
            self.dic['tempDiscoE'] = round(float(self.dicRaw['tempDiscoE']), 2)
            self.dicRaw['tempDiscoD'] = (buffer[10] << 8) + buffer[11]
            self.dic['tempDiscoD'] = round(float(self.dicRaw['tempDiscoD']), 2)
            self.dicRaw['time3'] = (buffer[12] << 8) + buffer[13]
            self.dic['time3'] = 25 * self.dicRaw['time3']
            return 1
        else:
            return 0

    def updateP4Data(self, buffer):
        if ((int(buffer[0]) == 4) and (len(buffer) == self.pSizes[3])):  # testa se é o pacote 3 e está completo
            for i in range(0, len(self.p4Order) -1):
                j = 2 + 3*i
                key = self.p4Order[i]
                self.dicRaw[key] = (buffer[j] << 16) + (buffer[j+1] << 8) + buffer[j+2]
                self.dic[key] = self.dicRaw[key]
            self.dicRaw['time4'] = (buffer[26] << 8) + (buffer[27])
            self.dic['time4'] = 25 * self.dicRaw['time4']
            return 1
        else:
            return 0

    # Arrasta para esquerda uma posicao os dados dos vetores e substitui ultimo valor com o dado mais recente
    def rollArrays(self):
        self.arrayBattery = np.roll(self.arrayBattery, -1)
        self.arrayBattery[-1] = self.dic['batVoltage']
        self.arrayOilP = np.roll(self.arrayOilP, -1)
        self.arrayOilP[-1] = self.dic['oleoP']
        self.arrayTemp = np.roll(self.arrayTemp, -1)
        self.arrayTemp[-1] = self.dic['ect']
        self.arrayFuelP = np.roll(self.arrayFuelP, -1)
        self.arrayFuelP[-1] = self.dic['fuelP']
        self.arrayTime2 = np.roll(self.arrayTime2, -1)
        self.arrayTime2[-1] = self.dic['time2']
        self.arrayTime3 = np.roll(self.arrayTime3, -1)
        self.arrayTime3[-1] = self.dic['time3']

    # Cria string separada por espaco com os nomes dos dados do pacote X, definidos em pXOrder
    def createPackString(self, packNo):
        if packNo == 1:
            list = self.p1Order
        elif packNo == 2:
            list = self.p2Order
        elif packNo == 3:
            list = self.p3Order
        elif packNo == 4:
            list = self.p4Order

        delimiter = ' '
        vec = [packNo]
        for key in list:
            vec.append(self.dicRaw[key])
        string = delimiter.join(str(x) for x in vec)
        string = string + '\n'
        return string


# Classe armazena um arquivo
class File:
    def __init__(self):
        self.save = 0

    def startDataSave(self, arquivo):
        now = datetime.now()
        # define o nome do arquivo concatenando o nome definido pelo usuário e hora e minuto do início da gravação
        arquivo = arquivo + "_" + str(now.hour) + "_" + str(now.minute) + ".txt"
        print(arquivo)
        self.arq = open(arquivo, 'w')
        self.save = 1
        # escreve os valores de setup no início do arquivo

    def writeRow(self, string):
        self.arq.write(string)

    # Função para parar a gravação dos dados no arquivo txt
    def stopDataSave(self):
        if self.save != 0:
            self.save = 0  # atualiza o valor da variavel save, a qual é usada para verificar se está ocorrendo ou não não gravação dos dados
            self.arq.close()


# Escrve mensagens na instancia logInstance.
# Nesse caso, logInstance é um campo da interface. Pode ser qualquer campo que aceite a
# Funcao setText
class Log():
    def __init__(self, logInstance, maxElements=200):
        self.Log = []
        self.logInstance = logInstance
        self.maxElements = maxElements

    # Insere novo texto de erro na primeira posicao do vetor
    def writeLog(self, text):
        self.Log.append(" ")
        # Faz o roll
        if len(self.Log) < self.maxElements:
            self.Log = self.Log[-1:] + self.Log[:-1]
            self.Log[0] = text
        else:
            self.Log = self.Log[-1:] + self.Log[:self.maxElements-1]
            self.Log[0] = text
        string = '\n'.join(str(x) for x in self.Log)
        #string = string + '\n'
        self.logInstance.setText(string)
        # print(text)


# Concatena vetor em uma string separada por delimiter
def vectorToString(line, delimiter, addNewLine=True):
    string = delimiter.join(str(x) for x in line)
    if addNewLine:
        string = string + '\n'
    return string