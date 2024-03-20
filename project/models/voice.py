# -*- coding: utf-8 -*-
from flask import flash
import pyaudio
import wave
import cv2
import os
import glob
from cryptography.fernet import Fernet
import pickle
import time
import io
import requests
from pinatapy import PinataPy
from scipy.io.wavfile import read
from IPython.display import Audio, display, clear_output
from retry import retry

from project.models.main_functions import *

pinata = PinataPy("240cbec28872e0e4791d", "ad13723a839e079b9bc72d68b5b437c1a705e894c60c36e24c777212c62dbfb2")

class voice(object):

    def __init__(self) -> None:
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 2
        self.RATE = 48000
        self.CHUNK = 1024
        self.RECORD_SECONDS = 3

        self.FILENAME = "./test.wav"
        self.MODEL = "\\gmm_models\\voice_auth.gmm"
        self.VOICEPATH = "\\voice_database\\"
        #Regularly updated GMM libraries IPFS CID
        self.IPFS_HASH = ""

        #Encryption keys for the GMM library
        self.IPFS_PRIVATE_KEY = Fernet.generate_key()
        self.fernet = Fernet(self.IPFS_PRIVATE_KEY)

        self.VOICEDICT = {}

    def add_user(self, voice1, voice2, voice3, username):   

        result = False
        source = self.VOICEPATH + username
        absolute_path = os.path.dirname(__file__) + self.VOICEPATH + username
        os.mkdir(absolute_path)
        
        voice_dir = [voice1, voice2, voice3]
        self.VOICEDICT[username] = voice_dir
        X = []
        Y = []
        for name in voice_dir:
            # reading audio files of speaker
            (sr, audio) = read(io.BytesIO(name))
                    
            # extract 40 dimensional MFCC
            vector = extract_features(audio,sr)
            vector = vector.flatten()
            X.append(vector)
            Y.append(name)
        X = np.array(X, dtype=object)

        le = preprocessing.LabelEncoder()
        le.fit(Y)
        Y_trans = le.transform(Y)
        clf = LogisticRegression(random_state=0).fit(X.tolist(), Y_trans)

        if os.path.isfile(os.path.dirname(__file__) + "\\gmm_models\\voice_auth.gmm"): 
            os.remove(os.path.dirname(__file__) + "\\gmm_models\\voice_auth.gmm")
            if self.IPFS_HASH != "":
                response = pinata.remove_pin_from_ipfs(self.IPFS_HASH)   
                print(response)  
        # saving model
        pickle.dump(clf, open(os.path.dirname(__file__) + '\\gmm_models\\voice_auth.gmm', 'wb'))
        try:
            #Encrypt Biometric Database
            with open(os.path.dirname(__file__) + "\\gmm_models\\voice_auth.gmm", "rb") as voice_dict:
                safe_voice_dict = open(os.path.dirname(__file__) + "\\gmm_models\\encrypted_voice_auth.gmm", "w")
                encrypted_voice = self.fernet.encrypt(voice_dict.read())
                safe_voice_dict.write(str(encrypted_voice, 'utf-8'))
                safe_voice_dict.close()
        except Exception as e:
            print("Error during encryption:", e)
        #Write Biometric Database to IPFS
        if os.path.isfile(os.path.dirname(__file__) + "\\gmm_models\\encrypted_voice_auth.gmm"):
            response = pinata.pin_file_to_ipfs(os.path.dirname(__file__) + '\\gmm_models\\encrypted_voice_auth.gmm')   
            self.IPFS_HASH = response['IpfsHash']
            print(self.IPFS_HASH)

            print(username + ' added successfully') 
            result = True
        
        features = np.asarray(())
        return result

    def recognise(self, voice, username):
        # Voice Authentication
        VOICENAMES = [ name for name in os.listdir(os.path.dirname(__file__) + self.VOICEPATH) if os.path.isdir(os.path.join(os.path.dirname(__file__) + self.VOICEPATH, name)) ]

        #IPFS Read Biometric Database
        enc_voice_dict = requests.get("https://ipfs.io/ipfs/" + self.IPFS_HASH).text
        voice_dict = self.fernet.decrypt(bytes(enc_voice_dict, encoding='utf-8'))
        with open(os.path.dirname(__file__) + "\\gmm_models\\voice_auth.gmm", 'wb') as file:
            file.write(voice_dict)
            print(voice_dict)

        print(VOICENAMES)
        if username in VOICENAMES:
            userIndex = VOICENAMES.index(username)
            arr = [VOICENAMES[userIndex]]
            try:
                # load model 
                model = pickle.load(open(os.path.dirname(__file__) + self.MODEL,'rb'))

                # reading audio files of speaker
                (sr, audio) = read(io.BytesIO(voice))
                    
                # extract 40 dimensional MFCC
                vector = extract_features(audio,sr)
                vector = vector.flatten()
                test_audio = vector

                # predict with model
                pred = model.predict(test_audio.reshape(1,-1))

                # decode predictions
                le = preprocessing.LabelEncoder()
                le.fit(arr)
                identity = le.inverse_transform(pred)[0]

                # if voice not recognized than terminate the process
                if identity == 'unknown':
                    print("Not Recognised!")
                    return "Not Found"
                else:
                    print( "Recognized as - ", username)
                    return "Identified and logged in!"
                    
            except:
                print("Stopped")
                return "Not Found"
        else:
            return "Username Missing"

    def delete_user(self, username):

        try:
            name = username 

            users = [ name for name in os.listdir(os.path.dirname(__file__) + self.VOICEPATH) if os.path.isdir(os.path.join(os.path.dirname(__file__) + self.VOICEPATH, name)) ]
            
            if name not in users or name == "unknown":
                print('No such user !!')
                return "No user"

            [os.remove(path) for path in glob.glob(os.path.dirname(__file__) + self.VOICEPATH + name + '/*')]
            os.removedirs(os.path.dirname(__file__) + self.VOICEPATH + name)

            if os.path.isfile(os.path.dirname(__file__) + "\\gmm_models\\voice_auth.gmm"): 
                os.remove(os.path.dirname(__file__) + "\\gmm_models\\voice_auth.gmm")
                
            voice_dir = [ name for name in os.listdir(os.path.dirname(__file__) + self.VOICEPATH) if os.path.isdir(os.path.join(os.path.dirname(__file__) + self.VOICEPATH, name)) ]
            X = []
            Y = []
            for voice in self.VOICEDICT[username]:
                # reading audio files of speaker
                print("test")
                (sr, audio) = read(io.BytesIO(voice))
                            
                # extract 40 dimensional MFCC
                vector = extract_features(audio,sr)
                vector = vector.flatten()
                X.append(vector)
                Y.append(name)
                
            X = np.array(X, dtype=object)

            le = preprocessing.LabelEncoder()
            le.fit(Y)
            Y_trans = le.transform(Y)
            clf = LogisticRegression(random_state=0).fit(X.tolist(), Y_trans)

            if os.path.isfile(os.path.dirname(__file__) + "\\gmm_models\\voice_auth.gmm"): 
                os.remove(os.path.dirname(__file__) + "\\gmm_models\\voice_auth.gmm")
            # saving model
            pickle.dump(clf, open(os.path.dirname(__file__) + '\\gmm_models\\voice_auth.gmm', 'wb'))

            print('User ' + name + ' deleted successfully')
            return "deleted"

        except:
            print("Error encountered")
            return "deleted"



