import requests
import datetime
import time
import winsound
import sys, msvcrt, tabulate, json, copy, argparse
from hashlib import sha256


# change this to the district id you need. These are for TCR & EKM
district_ids = [303, 307]

URL = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/calendarByDistrict?district_id={0}&date={1}&vaccine=COVISHIELD"
BOOKING_URL = "https://cdn-api.co-vin.in/api/v2/appointment/schedule"

BOOKING_REQUEST = {
    "beneficiaries": ["8138634614897", "1256868718565"], 
    "slot": "12:00PM-01:00PM", 
    "dose": 2
    }


def check_calendar(bearer_token):
    HEADER = {"Authorization": f"Bearer {bearer_token}"}

    try:
        print('===================================================================================')
        today = datetime.datetime.today()
        
        options = []
        for district_id in district_ids:
            resp = requests.get(URL.format(
                                            district_id, 
                                            (today + datetime.timedelta(days=1)).strftime("%d-%m-%Y")), 
                                            headers=HEADER)
            
            if resp.status_code == 401:
                print('TOKEN INVALID')
                return False

            elif resp.status_code == 200:
                resp = resp.json()
                print(f"Response at {today.strftime('%Y-%m-%d %H:%M:%S')} for {district_id}: {len(resp['centers'])}")

                if len(resp['centers']) > 0:
                    for center in resp['centers']:
                        print(f"######### :::: {center['district_name']}")
                        out = {}
                        for session in center['sessions']:
                            if session['available_capacity'] > 10:
                                out['name'] = center['name']
                                out['district'] = center['district_name']
                                out['center_id'] = center['center_id']
                                out['available'] = session['available_capacity']
                                out['date'] = session['date']
                                out['slots'] = session['slots']
                                out['session_id'] = session['session_id']
                                options.append(out)
                                if center['district_name'] == 'Thrissur':
                                    winsound.Beep(440, 150)
                                elif center['district_name'] == 'Ernakulam':
                                    winsound.Beep(660, 150)
                            else:
                                pass
                else:
                    pass
            else:
                pass

        return options

    except Exception as e:
        print(str(e))
        winsound.Beep(1000, 2000)


def schedule_appointment(bearer_token, details):
    HEADER = {"Authorization": f"Bearer {bearer_token}"}

    try:
        print('================================= ATTEMPTING BOOKING ==================================================')
        today = datetime.datetime.today()
        
        resp = requests.post(BOOKING_URL, headers=HEADER, json=details)
        print(f'Booking Response Code: {resp.status_code}')
        print(f'Booking Response : {resp.text}')

        if resp.status_code == 401:
            print('TOKEN INVALID')
            return False

        elif resp.status_code == 200:
            print('##############    BOOKED!  ##############')
            sys.exit(0)

        else:
            return True

    except Exception as e:
        print(str(e))
        winsound.Beep(1000, 2000)


class TimeoutExpired(Exception):
    pass


def input_with_timeout(prompt, timeout, timer=time.monotonic):
    sys.stdout.write(prompt)
    sys.stdout.flush()
    endtime = timer() + timeout
    result = []
    while timer() < endtime:
        if msvcrt.kbhit():
            result.append(msvcrt.getwche()) #XXX can it block on multibyte characters?
            if result[-1] == '\r':
                return ''.join(result[:-1])
        time.sleep(0.04) # just to yield to other processes/threads
    raise TimeoutExpired


def check_and_book(bearer_token):
    try:
        options = check_calendar(bearer_token)

        if isinstance(options, bool):
            return False
        
        tmp_options = copy.deepcopy(options)
        if len(tmp_options) > 0:
            cleaned_options_for_display = []
            for item in tmp_options:
                item.pop('session_id', None)
                item.pop('center_id', None)
                cleaned_options_for_display.append(item)

            header = ['id'] + list(cleaned_options_for_display[0].keys())
            rows =  [[idx + 1] + list(x.values()) for idx, x in enumerate(cleaned_options_for_display)]

            print(tabulate.tabulate(rows, header, tablefmt='grid'))

        else:
            print("No viable options")
        
        choice = input_with_timeout('Enter Choice: ', 10)
    
    except TimeoutExpired:
        time.sleep(5)
        return True
    
    else:
        choice = choice.split('.')
        print(f'============> Got {choice}')
        new_req = copy.deepcopy(BOOKING_REQUEST)
        new_req['center_id'] = options[int(choice[0])-1]['center_id']
        new_req['session_id'] = options[int(choice[0])-1]['session_id']
        new_req['slot'] = options[int(choice[0])-1]['slots'][int(choice[1])-1]
        print(f'Booking with info: {new_req}')

        return schedule_appointment(bearer_token, new_req)


def generate_token_OTP(mobile):
    data = {"mobile": mobile, "secret": "U2FsdGVkX1/3I5UgN1RozGJtexc1kfsaCKPadSux9LY+cVUADlIDuKn0wCN+Y8iB4ceu6gFxNQ5cCfjm1BsmRQ=="}
    txnId = requests.post(url='https://cdn-api.co-vin.in/api/v2/auth/generateMobileOTP', json=data)
    
    if txnId.status_code == 200:
        txnId = txnId.json()['txnId']
    else:
        print('Unable to Create OTP')
        print(txnId.text)
        sys.exit(1)

    OTP = input("Enter OTP: ")
    data = {"otp": sha256(str(OTP).encode('utf-8')).hexdigest(), "txnId": txnId}

    token = requests.post(url='https://cdn-api.co-vin.in/api/v2/auth/validateMobileOtp', json=data)
    if token.status_code == 200:
        token = token.json()['token']
    else:
        print('Unable to Validate OTP')
        print(token.text)
        sys.exit(1)
    
    print(f'Token Generated: {token}')
    return token


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mobile', help='Pass the mobile to generate OTP')
    parser.add_argument('--token', help='Pass token directly')
    args = parser.parse_args()

    token = None
    
    if args.token:
        token = args.token
    elif args.mobile:
        token = generate_token_OTP(args.mobile)

    TOKEN_VALID = True
    while TOKEN_VALID == True:
        TOKEN_VALID = check_and_book(token)
        
        if TOKEN_VALID:
            pass
        
        else:
            tryOTP = None
            tryOTP = input("Token is INVALID. Mobile Number for generating OTP? : ")
            
            if tryOTP:
                token = generate_token_OTP(tryOTP)
                TOKEN_VALID = True
            else:
                TOKEN_VALID = False
                print("Exiting")

if __name__ == '__main__':
    main()
