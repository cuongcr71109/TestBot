import requests
from datetime import datetime, timedelta
import time
import operator
import json
import collections

class BotHandler:
    def __init__(self, token):
            self.token = token
            self.api_url = "https://api.telegram.org/bot{}/".format(token)

    
    #functions get_updates
    def get_updates(self, offset=0, timeout=30):
        method_url = r'getUpdates'
        params = {'timeout': timeout, 'offset': offset}
        resp = requests.get(self.api_url + method_url, params)
        result = resp.json()['result']
        return result
        # data = json.loads(resp.text)
        # if data['ok'] == True:
        #     result_json = data['result']
        #     return  result_json
    #function send messages    
    def send_message(self, chat_id, text):
        params = {'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML'}
        method_url = r'sendMessage'
        resp = requests.post(self.api_url + method_url, params)
        return resp
    
    #function delete message
    def del_message(self, chat_id, message_id):
        params = {'chat_id':chat_id ,'message_id': message_id}
        method_url = r'deleteMessage'
        resp= requests.get(self.api_url + method_url,params)
        return True
    #fucntion forward message
    def forward_message(self, chat_id, from_chat_id, message_id, schedule_date):
        params= {'chat_id':chat_id, 'from_chat_id':from_chat_id,'message_id': message_id, 'schedule_date':schedule_date}
        method_url=r'forwardMessage'
        resp= requests.post(self.api_url + method_url, params)
        return resp

    #function kick member
    def kick_member(self, chat_id, user_id):
        params= {'chat_id': chat_id, 'user_id': user_id}
        method_url = r'kickChatMember'
        resp= requests.post(self.api_url + method_url, params)
        return resp
    
    
           

token = '1421953999:AAGkKzSCLNGtq0lS1jQQvZv2dUW078zPkLg' #Token of your bot
my_bot = BotHandler(token) #Your bot's name



def main():
    new_offset = 0
    print('hi, now launching...')
    now= datetime.now()
    now= now.strftime("%H:%M:%S")
    print(now)
    myDict={} # contain violations/member
    groupDict={} #contain group chat_id
    delMes={} # contain delete message
    personDict={}
    def getList(dict):
        return list(dict.keys())
    while True:
        all_updates = my_bot.get_updates(new_offset)
        
        #file contains suitable content to reply
        with open("greeting.txt","r") as file:
            data = file.read().split("\n")
            
        #file contains banned words 
        with open ("ban_words.txt","r") as f:
            banList = f.read().split("\n")
            
            
        if len(all_updates) > 0:
            for current_update in all_updates:
                print(current_update)
                first_update_id = current_update['update_id']
                first_chat_id = current_update['message']['chat']['id']   
                message_id = current_update['message']['message_id']
                user_id = current_update['message']['from']['id'] 
               
                  
                if 'text' not in current_update['message'] :
                    first_chat_text = 'New member'
                else:                    
                    first_chat_text = current_update['message']['text']
                
                if 'last_name' in current_update['message']:   
                    first_last_name= current_update['message']['chat']['last_name']
                    
                                                
                elif 'first_name'  in current_update['message']:
                    first_chat_name = current_update['message']['chat']['first_name']
                
                elif 'message' in current_update['message']:
                    message_id = current_update['message']['message_id']
                                
                elif 'new_chat_member' in current_update['message']:
                    first_chat_name = current_update['message']['new_chat_member']['first_name']
                    first_last_name = current_update['message']['from']['last_name']
                    
                elif 'from' in current_update['message'] and 'left_chat_member' not in current_update['message']:
                    first_chat_name = current_update['message']['from']['first_name']
                    first_last_name = current_update['message']['from']['last_name']
                    
                elif 'left_chat_member' in current_update['message']:
                    first_chat_name= current_update['message']['left_chat_member']['first_name']
                    first_last_name= current_update['message']['left_chat_member']['last_name']
               
                else:
                    first_chat_name = "unknown"
                    
                user_fullname= first_chat_name +" " + first_last_name 
                
                if first_chat_id in groupDict:
                    groupDict[first_chat_id] +=1
                else:
                    groupDict.update({first_chat_id:1})
                # print(list(groupDict.values()))
                chatList=getList(groupDict)
                # print(chatList)
                
               
                #delete message
                if first_chat_id in groupDict.keys():    
                    num = groupDict.get(first_chat_id)
                    for txt in banList:
                        if txt in first_chat_text:
                            new_offset = first_update_id + 1
                            my_bot.del_message(first_chat_id, message_id)
                              
                            if first_chat_id in delMes:
                                delMes[first_chat_id] +=1
                            else:
                                delMes.update({first_chat_id:1})
                            
                               
                            if user_fullname in personDict :
                                personDict[user_fullname] +=1
                                    
                            else:
                                personDict.update({user_fullname:1})    
                                # print(personDict)  
                                key_id=max(personDict.items(), key=operator.itemgetter(1))[0]
                                                          
          
                            if user_id in myDict:
                                myDict[user_id]+=1
                            else:
                                myDict.update({user_id: 1})
                            # print(myDict)   
                            if myDict[user_id] == 4 :
                                my_bot.send_message(first_chat_id, first_chat_name +" " + first_last_name+ ": " "You violated too many times, if once again, you will be kicked")
                            elif myDict[user_id] > 10 :
                                my_bot.kick_member(first_chat_id, user_id)
                        
                    #reply message             
                    if first_chat_text in data:
                        my_bot.send_message(first_chat_id, 'Nice to meet you, ' + first_chat_name)
                        new_offset = first_update_id + 1    
                    else:
                        my_bot.send_message(first_chat_id," ")
                        new_offset = first_update_id + 1

                    #print information
                    if first_chat_id in groupDict.keys():
                        if first_chat_text == "/count":
                            new_offset = first_update_id + 1
                            my_bot.send_message(first_chat_id,'Total messages are : ' +str(num))
                            
                            if str(delMes.get(first_chat_id)) == "None":
                                my_bot.send_message(first_chat_id,'Total deleted messages are : 0' )
                                my_bot.send_message(first_chat_id, 'Total violations are : 0' )
                            else:
                                my_bot.send_message(first_chat_id,'Total deleted messages are : ' +str(delMes.get(first_chat_id)))
                                my_bot.send_message(first_chat_id, 'Total violations are : ' + str(delMes.get(first_chat_id)))
                            
                            #Violated most
                            if len(personDict) >0:
                                for user_fullname in personDict.keys():
                                    key_id=max(personDict.items(), key=operator.itemgetter(1))[0]
                                    print(key_id)
                                    my_bot.send_message(first_chat_id, 'Person violating most is : ' +key_id)
                                
                            else : 
                                my_bot.send_message(first_chat_id, ' ')
                        
                            
                        elif first_chat_text == "/id":
                            my_bot.send_message(first_chat_id,"Your id is: " + str(user_id))
                    

                        
                        
                    if first_chat_id:
                        listMes=[]
                        numofList= len(listMes)
                        listMes.append(message_id)
                        # print(listMes[numofList-1])
                        
                        addList=[]
                        for first_chat_id in chatList:
                            if first_chat_id != -1001221371880:
                                addList.append(first_chat_id)
                        for i in addList:
                            # print(i)
                            my_bot.forward_message(i,'-1001221371880',listMes[numofList-1],time.sleep(10))
                                    
                        
                    
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
        