from api_handler.api import pure_api_handler
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)
import os
import json
import sys
from datetime import datetime , timedelta
import pandas as pd
pd. set_option('display.max_columns', 500)
pd.options.mode.chained_assignment = None
class pure_bot:

    def __init__(self):
        self.__is_running = True
        logger.debug("Bot started. Loading Pure API Service ")
        self.__get_config()
        self.api_handler = pure_api_handler(self.__config['username'],self.__config['password'])

    def get_date(self):
        now = datetime.utcnow() +timedelta(hours=8)
        return now.strftime("%Y-%m-%d")

    def __json_printer(self ,json_dict:dict, display_field:list,name_conversion:None):
        ret_str = ''
        for item in json_dict.keys():
            if item in display_field:
                if name_conversion and isinstance(name_conversion,dict):
                    if item in name_conversion.keys():
                        ret_str += f'{name_conversion[item]}:{json_dict[item]}\n'
                    else:
                        ret_str += f'{item}:{json_dict[item]}\n'
                else:
                    ret_str += f'{item}:{json_dict[item]}\n'

        print(ret_str)


    def __get_config(self):
        try:
            self.__config = self.__ticker=json.load(open(os.path.join(os.getcwd(),"config/config.json")))
        except Exception as err:
            logger.error(self.__config)
            sys.exit(0)

    def get_profile(self):
        ret = self.api_handler.get_profile()
        self.__json_printer(ret['user'],['last_name',"first_name","state","preferred_location",], {
            "first_name":"First Name",
            "last_name":"Last Name",
            "state":"Membership Status",
            "preferred_location":"Perferred Location"
        })


    def view_location(self):
        center_type = int(input("\nLocation Type( Fitness [1]   Yoga[2] ):" ))
        ret = self.api_handler.get_location()
        if center_type ==2:
            ret = [ x for x in ret['locations'] if x['is_yoga']== True]
        if center_type == 1:
            ret = [ x for x in ret['locations'] if x['is_fitness']== True]
        for item  in ret:
            self.__json_printer(item["names"],['en'], {"en":"Name"})
            #self.__json_printer(item,["is_fitness","is_yoga"],None)

    def _get_command(self):
        cmd = f"""
-----------------------
1: View Location\n
2: Get Available Class\n
3: Check Booking Status\n 
4: \n
5: Cancel Booking\n
6: Get Profile\n
7: Quit Bot
-----------------------
"""
        print(cmd)


    def get_available_class(self):
        location_str = ''
        date_str = ''
        class_str = ''
        map_dict={}
        index = 0
        class_type = int(input("\nClass Type( Fitness [1]   Yoga[2] ):" ))
        ret = self.api_handler.get_location()
        if class_type ==2:
            ret = [(x['id'],x['names']['en']) for x in ret['locations'] if x['is_yoga']== True and "names" in x.keys()]
            class_type = 'Y'
        if class_type == 1:
            ret = [ (x['id'],x['short_name']['en']) for x in ret['locations'] if x['is_fitness']== True and "short_name" in x.keys()]
            class_type = 'F'
        location_dict = dict(ret)
        for item in location_dict.keys():
            index+=1
            map_dict[index]=item
            location_str +=f"[{index}]:{location_dict[item]}\n"
        try:
            map_id = int(input("Center Selection\n"
                                f"{location_str}\n"
                           f"Input the location ID:"))
        except:
            print("Please Enter Numerical Command")
        location_id = map_dict[map_id]
        print(f'Center Selected:{location_dict[location_id]}')

        schedule = self.api_handler.view_schedule(location_id,1,self.get_date(),class_type)
        map_dict = {}
        index=0
        if len(schedule['classes'])>0 and isinstance(schedule,dict):

            schedule = pd.DataFrame(schedule['classes'])

            class_date = schedule['start_date'].unique()

            for item in class_date:
                index += 1
                map_dict[index] = item
                date_str += f"[{index}]:{item}\n"

            try:
                map_id = int(input("Date Selection\n"
                                   f"{date_str}\n"
                                   f"Input the Date:"))
            except:
                print("Please Enter Numerical Command")
            date  = map_dict[map_id]
            print(f"You selected {date}")
            classes = schedule.copy()

            classes = classes.query(f"start_date == '{date}'")
            classes['class_name']= classes.apply(lambda x:x['class_type']['name'],axis=1)
            classes = classes[['id','start_date',"start_time","duration","teacher","class_name"]]
            class_dict = classes.to_dict('records')
            map_dict = {}
            index = 0
            for item in class_dict:
                index += 1
                map_dict[index] = item['id']
                class_str += f"[{index}]: TYPE: {item['class_name']} TIME :{item['start_time']}  TEACHER:{item['teacher']['full_name']}\n"

            try:
                map_id = int(input(f"Class Selection\n{class_str}"))
                class_id = map_dict[map_id]
                print(f"You selected :{class_id}")


                #If beyond 2 days , save to csv and wait for batch execute
                #If within booking period , execute the booking immediately
                booking = self.api_handler.booking(int(class_id), 1)
                # Check booking status
                if booking['error']['code'] == 200:
                    if booking['data']['waiting_number'] >0:
                        status = "Waitlisted"
                    else:
                        status = "Booked"
                    print(f"Booking Success!Status: {status}")
                    return
                elif booking['error']['code'] == 442:
                    print("You dont have Yoga service plan :( ")

            except Exception as err:
                print(f"Please Enter Numerical Command.{err}")

    def cmd_end(self):
        action = input("---------\nBACK TO MAIN [1] | Exit [2]:")
        if int(action) == 2:
            self.__is_running = False
        else:
            return

    def run(self):
        ret = self.api_handler.get_location()
        print("\n"+
              """                                                  
  ..........  ...       ...........     ........  
 :BBPJJJJJ5GG5GB5      .GBGJJJJJ5GGP~:JPGYJJJJJJ: 
 :BBJ      PBBBBP      .BB5     .5BBBBBG^.        
 :BBGJJJJYPG5JBB5      .GBGJJJYPGBY!5BBGJJJJJJJY: 
 :BBY......   PBB~.   .!BBJ    !GB5..PBB7.......  
 .55!          ^?55YYY55?~       755~ ^7Y5YYYYYY:                                    
                             ^! ~ :! !7.^?..?..?: 
                                         .  .  . 
Welcome to Pure Booking Bot!            
                                                 """)
        while self.__is_running:
            self._get_command()
            cmd = input("Command: ")

            try:
                cmd = int(cmd)
                if cmd ==1:
                    self.view_location()
                    self.cmd_end()
                elif cmd ==2:
                    self.get_available_class()
                    self.cmd_end()
                elif cmd == 3:
                    return
                elif cmd == 4:
                    return
                elif cmd == 5:
                    return
                elif cmd == 6:
                    self.get_profile()
                    self.cmd_end()
                elif cmd ==7:
                    print("Quitting the Bot. BYE~!")
                    self.__is_running = False
                else:
                    print("Command Invaild")
            except Exception as err:
                print(f"Error : {err}")

    def test(self):
        self.get_available_class()

    def cron(self):
        """
        1. Get the list from booking.csv (local record db)
        2. Run the booking function (login + booking)
        3. Mark Complete
        4. Done :)
        :return:
        """
        return



if __name__ == '__main__':
    bot = pure_bot()
    #2
    # bot.test()
    bot.run()

