import socket
from picamera import PiCamera
from io import BytesIO
from PIL import Image
import numpy as np

def getCamera():
    '''Init the camera'''
    camera = PiCamera()
    camera.resolution = (640, 480)
    return camera

def captureImage(cameraObj):
    '''Capture image and return black-white version'''
    stream = BytesIO()
    cameraObj.capture(stream, format='jpeg')
    stream.seek(0)
    image = Image.open(stream)
    array = np.array(image)
    return array
    

def connectToServer(hostIp='192.168.29.189', port=6000):
    '''Returns a socket object'''
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((hostIp, port))
    return s

def sendDataToServer(socketObj, data):
    '''Used to send data over to server'''
    if type(data) == list:
        socketObj.send(bytes(data))
    if type(data) == str:
        socketObj.send(bytes(data, 'utf-8'))

def getDataFromServer(socketObj):
    '''Used to get back data from server'''
    return socketObj.recv(1024).decode('utf-8')
    
def closeConnection(socketObj):
    '''Used to close connection'''
    socketObj.close()
    

def sendImageToServer(socketObj, cameraObj):
    '''If client get signal, it will send over an image
        Resolution is fixed for now, could be change in the future'''
    
    imgCap = captureImage(cameraObj)
    for i in range(640): # fixed res, 640 by 480
        sendDataToServer(socketObj, list(imgCap[:, i, 0]))
        if getDataFromServer(socketObj) == 'next row':
            continue
    
    for i in range(640): # fixed res, 640 by 480
        sendDataToServer(socketObj, list(imgCap[:, i, 1]))
        if getDataFromServer(socketObj) == 'next row':
            continue
    
    for i in range(640): # fixed res, 640 by 480
        sendDataToServer(socketObj, list(imgCap[:, i, 2]))
        if getDataFromServer(socketObj) == 'next row':
            continue
    
    
    print('Image sent')


cam = getCamera()
s = connectToServer()

while True:
    dataRecv = getDataFromServer(s)
    if dataRecv == 'send image':
        sendImageToServer(s, cam)
    if dataRecv == 'end':
        print('Server has no requests')
        break
    

