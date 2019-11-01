import io
import os
import random
import numpy as numpy
from datetime import timedelta,datetime,time,date
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
from .vision_helper import Vision
import six
import re
import string

class NLP:
    def __init__(self):
        # try:
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.BASE_DIR = os.path.abspath(os.path.join(self.BASE_DIR,'..'))
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'natural_language_credential.json'
        self.client = language.LanguageServiceClient()
        self.domains = ["com","org","net","edu","gov","int","io"]
        self.designation = ["CEO","CTO","Manager","CFO","Intern","Chief","executive",
                            "Exective","officer","Officer","CFO","CRO","Technical",
                            "Technician","Software developer"," developer"]

    def link_fetch(self, Input): 
      # longest length string with entity_type in fetched entity is usually a website.       
        ls = []
        Input = Input.split(" ")
        for str in (Input):
            ls.append(len(str))
        max = ls[0] 
        for i in range(1, len(ls)): 
            if ls[i] > max: 
                max = ls[i]
        loc = ls.index(max) 
        return(Input[loc])


    def cardDetails(self):
        """
        BUSINESS CARD DETAILS COLLECTION
         Log saved in businessCard_log.txt . 
        """
        resultArr = []
        visionObj = Vision()
        vision_result = visionObj.detect_text_card()
        if isinstance(vision_result, six.binary_type):
            vision_result = vision_result.decode('utf-8')

        # Instantiates a plain text document.
        doc = types.Document( 
            content=vision_result,
            type=enums.Document.Type.PLAIN_TEXT)

        entities = self.client.analyze_entities(doc).entities

        filename = os.path.join(self.BASE_DIR, ("logs/businessCard_log.txt"))
        resultFile = open(filename,"a+")
        resultFile.write("\n"+str(datetime.now())+"\n")
        phoneNumbers = []
        emails = []
        links = []

        for ent in entities:

            entity_type = enums.Entity.Type(ent.type)
            print(ent.name, entity_type.name)
            entSplit = (ent.name).split(" ")

            if (entity_type.name not in ["ADDRESS","EVENT"]):
                count = 0
                if re.match('[^@]+@[^@]+\.[^@]+',ent.name):
                    ent_name = self.link_fetch(ent.name)
                    resultFile.write("{:<20}".format("EMAIL")+ent_name+"\n")
                    resultArr.append(["EMAIL",ent_name])

                elif (entity_type.name == "PHONE_NUMBER"):
                    phoneNumbers.append(ent.name)
                    for i in range(len(phoneNumbers)):
                        resultFile.write("{:<20}".format(entity_type.name)+(phoneNumbers[i])+"\n")                    
                    resultArr.append([entity_type.name, phoneNumbers])


                elif (entity_type.name not in ["CONSUMER_GOOD","DATE","OTHER","WORK_OF_ART","LOCATION"]):
                    
                    for elem in entSplit:
                        if ((entity_type.name).upper() == "PERSON" and elem in self.designation):
                            count += 1

                    if (count == len(entSplit) and elem in self.designation):
                        resultFile.write(entity_type.name + ent.name+"\n")
                        resultArr.append(["DESIGNATION",ent.name])

                    else:    
                        resultFile.write("{:<20}".format(entity_type.name)+ent.name+"\n")
                        resultArr.append([entity_type.name,ent.name])
    

                else:
                    for val in entSplit:
                        if (((val.rsplit(".",1)[-1])).lower() in self.domains):
                            links.append(val)
                            for i in range(len(links)):                            
                                resultFile.write("{:<20}".format("WEBSITE")+links[i]+"\n")
                            resultArr.append(["WEBSITE",links])
                



    #, entity.metadata.get('wikipedia_url')])
        resultFile.close()
        return(resultArr)