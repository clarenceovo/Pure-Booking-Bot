import requests
from requests import Session
import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)
import json
class pure_api_handler:
    def __init__(self,username,password):
        self.__username = username
        self.__password = password
        self.api_endpoint = 'https://pure360-api.pure-international.com/api/v3'
        self.__session = Session()
        self.__load_token()

    def __load_token(self):
        self.__session.headers.update({"x-token":"1eef64f486d711714bfd58e098f4cffb"})
        self.__session.headers.update({"x-date":"1653109808000"})

    def get_profile(self):
        self.login()
        return self.__get("get_client_info", param={"is_mobile": 0, "region_id": 1})

    def get_location(self):
        return self.__get("view_location",param={"language_id":1,"region_id":1})


    def view_schedule(self,location_id,region_id,start_date,sector):
        param = {
            "location_ids":location_id,
            "region_id":region_id,
            "start_date":start_date,
            "sector":sector,
            "days":7,
            "language_id":1
        }

        return self.__get("view_schedule",param=param)

    def login(self):
        body={"username":self.__username,"password":self.__password,"region_id":1,"language_id":"1","jwt":True}
        login =  self.__post("login",body)
        if login['error']['code'] == 200:
            logger.debug("LOGIN SUCCESS")
            data = login['data']
            self.__session.headers.update({"X-JWT-Token":data['user']['jwt']})

        elif login['error']['code'] >=400:
            logger.error(F"LOGIN FAILED.REASON:{login['error']['message']}")
        else:
            logger.error("LOGIN ERROR")

    def get_location(self):
        return self.__get('view_location',param={
            "language_id":1,
            "region_id":1
        })

    def booking(self,class_id,region_id):
        self.login()
        body = {"class_id":class_id,"book_type":2,"booked_from":"WEB","region_id":region_id}
        return  self.__post("booking", body)


    def __post(self,url,body):
        return self.__session.post(f'{self.api_endpoint}/{url}',data=json.dumps(body)).json()

    def __get(self,url,param):
        ret = self.__session.get(f'{self.api_endpoint}/{url}',params=param).json()
        if ret['error']['code'] == 200:
            return ret['data']
        else:
            logger.error(f"API Service error :{ret['error']['message']}")
            return None


