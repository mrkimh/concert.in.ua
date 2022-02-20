import random
from datetime import datetime
import string


def generate_number_ticket():
    global final_string

    str1 = ''.join((random.choice(string.ascii_letters) for x in range(20)))  
    str1 += ''.join((random.choice(string.digits) for x in range(12)))  
  
    sam_list = list(str1) # it converts the string to list.  
    random.shuffle(sam_list) # It uses a random.shuffle() function to shuffle the string.  
    final_string = ''.join(sam_list)  

    print(final_string)  
    return final_string


def current_time():
    global curr_time
    now = datetime.now()
    timestamp = datetime.timestamp(now)
    date_time = datetime.fromtimestamp(timestamp)
    curr_time = date_time.strftime("%m/%d/%Y, %H:%M:%S")
    return curr_time
