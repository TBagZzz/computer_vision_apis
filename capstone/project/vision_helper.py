import wikipedia
import io
import os
import random
import re
from google.cloud import vision
from google.cloud.vision import types
from datetime import timedelta,datetime,time,date
from PIL import Image
import csv

class Vision:

    def __init__(self,location):
        try:
            current_loc = os.getcwd()
            dir_path = os.path.dirname(os.path.realpath(__file__))
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.join(current_loc,'vision_api_credential.json')
            self.label_filename = ""
            self.client = vision.ImageAnnotatorClient()
            self.CUR_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.BASE_DIR = os.path.abspath(os.path.join(self.CUR_DIR,'..'))
            self.file_name = location
            self.domains = [".com",".org",".net",".edu",".gov",".int",".io",".co",
                           ".in",".au",".us",".cn",".pk",".hk"]
            self.designation = ["ceo","cto","manager","coo","cfo","intern","chief","executive",
                           "officer","cro","technical","financial","revenue","founder", "graphic",
                           "technician","software","developer","director","Sales","partner",
                           "lead","leader","general","associate","consultant","operational",
                           "senior", "vice", "president", "investor", "broker", "designer", "hr"]

            if int(os.path.getsize(self.file_name)) >= 1024:
                img = Image.open(self.file_name)
                #img = img.convert("L")
        #ALTER HERE FOR IMAGE COMPRESSION
                img.save(self.file_name, format="JPEG", quality=40)
            else:
                pass
            with io.open (self.file_name,'rb') as imgFile:
                self.content = imgFile.read()
            imgFile.close()

            self.image = vision.types.Image(content = self.content)
        except (FileNotFoundError, IOError):
            print("NOTE : Please Upload image in /upload URL first.")


    def provideLabel(self):
        """
        IMAGE DETECTION
         Returns most possible label for the image .
         Call this function before calling WikiDetails function .
         Log saved in label_log.txt . 
        """

        try:
            descriptionList = []
            response = self.client.label_detection(image = self.image)
            labels = response.label_annotations
            filename = os.path.join(self.BASE_DIR, ("logs/label_log.txt"))
            for i in range(len(labels)):
                print(labels[i].description)
            label = labels[0].description
            resultFile = open(filename,"a+")
            resultFile.write("\n"+str(datetime.now())+"\n")
            resultFile.write(label+"\n")
            resultFile.close()
            return(label)
        except (FileNotFoundError, IOError, AttributeError):
            return("NOTE : Please Upload image in /upload URL first.")


    def detect_text(self):
        """
        TEXT DETECTION 
         Returns Text detected in image .
         Log saved in OCR_log.txt .
        """

        # try:
        response = self.client.document_text_detection(image = self.image)
        texts = response.full_text_annotation
        filename = os.path.join(self.BASE_DIR, ("logs/OCR_log.txt"))
        resultFile = open(filename,"a+")
        Result = texts.text.split("\n")
        resultFile.write("\n"+str(datetime.now())+"\n")
        for i in Result:
            resultFile.write(i+"\n")
        resultFile.close()
        return(Result)
        # except (FileNotFoundError, IOError, AttributeError):
        #     return("NOTE : Please Upload image in /upload URL first. -2")



    def detect_text_card(self):

        try:
            response = self.client.document_text_detection(image = self.image)
            texts = response.full_text_annotation
            tmp = texts.text.split("\n")
            ResultJoined = " ".join(tmp)
            return(ResultJoined)
        except (FileNotFoundError, IOError, AttributeError):
            return("NOTE : Please Upload image in /upload URL first.")



    def detect_text_card_beta(self):

        try:
            resultArr = []
            links = []
            phonenumbers = []
            Name = ""

            response = self.client.document_text_detection(image = self.image)
            texts = response.full_text_annotation

            Result = texts.text.split("\n")

            for i in Result:
                splitted = i.split(" ")
                probability_designation = 0

                with open(os.path.join(self.BASE_DIR,"names.txt"),"r") as nameReader:
                    probability_name = 0
                    line = nameReader.read()
                    lineArr = line.split(" ")
                    try:
                        lineArr.remove("")
                    except:
                        pass
                    for elem0 in splitted:
                        elem_tmp = elem0.lower()
                        for value in lineArr:
                            if elem_tmp == value:
                                probability_name += 1
                        if (probability_name/len(splitted) >= 0.33):
                            Name =(" ".join([val for val in splitted]))
                            resultArr.append(["NAME",Name])

                for elem0 in splitted:
                    for domain in self.domains:
                        if re.match('[^@]+@[^@]+\.[^@]+', elem0):
                            resultArr.append(["EMAIL",elem0])

                        elif (elem0.endswith(domain) == True or elem0.endswith(domain.upper()) == True): 
                            links.append(elem0)
                            resultArr.append(["WEBSITE",links])

                new_i = re.sub(r"[()+-.&]", "", i)
                splitted_for_designation = new_i.split()
                for elem in splitted_for_designation:
                    elem_tmp = elem.lower()
                    for designation in self.designation:
                        if elem_tmp == designation:
                            probability_designation += 1
                    if (probability_designation/len(splitted_for_designation) >= 0.33):
                        designation = (" ".join([val for val in splitted]))
                        resultArr.append(["DESIGNATION",designation])


                new_array = list(new_i)    
                for j in range(0,len(new_array)-2):
                    loc = []
                    try:
                        if (new_array[j+1] == " "):
                            if (new_array[j].isdigit() == True and new_array[j+2].isdigit() == True):
                                loc.append(j+1)

                    except:
                        pass
                    loc.reverse()
                    Arr1 = list(new_array)            
                    #print(loc)
                    for Location in loc:
                        del Arr1[Location]
                    new_array = "".join(Arr1)
                    #print(newArr)
                try:
                    Array = new_array.split()
                    for elem1 in Array:
                        if re.match("^(\d{8,15})$", elem1):
                            if len(elem1)>=12:
                                numb = list(elem1)
                                if numb[0] == 0:
                                    numb = numb.pop(0)

                                a = "%s"%(numb[0]+numb[1])
                                b = [str(numb[i]) for i in range(2,7)]
                                b = "".join(b)
                                c = [str(numb[i]) for i in range(7,len(numb))]
                                c = "".join(c)

                                phonenumbers.append("+%s-%s-%s"%(a,b,c))
                                resultArr.append(["PHONE_NUMBER",phonenumbers])
                            else:
                                phonenumbers.append(elem1)
                                resultArr.append(["PHONE_NUMBER",phonenumbers])
                except:
                    pass

            return(resultArr)

        except (FileNotFoundError, IOError, AttributeError):
            return("NOTE : Please Upload image in /upload URL first.")




    def detect_logo(self):
        """
        LOGO DETECTION 
         Returns Logo detected in image .
         Log saved in logo_log.txt .
        """

        try:
            resultList = []
            filename = os.path.join(self.BASE_DIR, ("logs/logo_log.txt"))
            response = self.client.logo_detection(image = self.image)
            logo = response.logo_annotations
            resultFile = open(filename,"a+")
            resultFile.write("\n"+str(datetime.now())+"\n")
            for Logo in logo:
                resultList.append(str(Logo.description))
                resultFile.write(Logo.description+"\n")
            resultFile.close()
            return(resultList)

        except (FileNotFoundError, IOError, AttributeError):
            return("NOTE : Please Upload image in /upload URL first.")


#BETA

    # def WikiDetails(self):
    #   """
    #   WIKIA FOR LABEL (OPTIONAL)
    #   NOTE : Call this function only after calling provideLabel().
    #   """
    #   try:
    #       File = open(os.path.join(BASE_DIR,"logs/label_log.txt"),'r')
    #       identified_Obj = File.readline()
    #       try:
    #           Summary = wikipedia.summary(identified_Obj, sentences = 1)
    #       except wikipedia.DisambiguationError as e:
    #           randPage = random.choice(e.options)
    #           Summary = wikipedia.summary(randPage, sentences = 1)
    #       return(Summary)
    #       File.close()
    #   except (FileNotFoundError, IOError, AttributeError):
    #       return("NOTE : Please Upload image in /upload URL first.")

  
