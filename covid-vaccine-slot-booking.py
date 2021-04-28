import requests
import datetime
import time
import winsound
import sys, msvcrt, tabulate, json, copy, argparse
from hashlib import sha256


# change this to the district id you need. These are for TCR & EKM
district_ids = [303, 307]

URL = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/calendarByDistrict?district_id={0}&date={1}&vaccine={2}"
BOOKING_URL = "https://cdn-api.co-vin.in/api/v2/appointment/schedule"
BENEFICIARIES_URL = "https://cdn-api.co-vin.in/api/v2/appointment/beneficiaries"

BOOKING_REQUEST_TEMPLATE = {
    "beneficiaries": [], 
    "slot": "", 
    "dose": 2
    }


def display_table(dict_list):
    header = ['idx'] + list(dict_list[0].keys())
    rows =  [[idx + 1] + list(x.values()) for idx, x in enumerate(dict_list)]
    print(tabulate.tabulate(rows, header, tablefmt='grid'))

class TimeoutExpired(Exception):
    pass


def check_calendar(request_header, vaccine_type, minimum_slots):
    try:
        print('===================================================================================')
        today = datetime.datetime.today()
        tomorrow = today + datetime.timedelta(days=1)
        
        options = []
        for district_id in district_ids:
            resp = requests.get(URL.format(district_id, tomorrow.strftime("%d-%m-%Y"), vaccine_type), 
                                headers=request_header)
            
            if resp.status_code == 401:
                print('TOKEN INVALID')
                return False

            elif resp.status_code == 200:
                resp = resp.json()
                print(f"Responses at {today.strftime('%Y-%m-%d %H:%M:%S')} for dist. {district_id} for {vaccine_type}: {len(resp['centers'])}")

                if len(resp['centers']) >= 0:
                    for center in resp['centers']:
                        print(f"######### :::: {center['district_name']}")
                        out = {}
                        for session in center['sessions']:
                            if session['available_capacity'] >= minimum_slots:
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


def book_appointment(request_header, details):
    try:
        print('================================= ATTEMPTING BOOKING ==================================================')
        
        resp = requests.post(BOOKING_URL, headers=request_header, json=details)
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


def check_and_book(request_header, vaccine_type, beneficiaries, minimum_slots):
    try:
        options = check_calendar(request_header, vaccine_type, minimum_slots)

        if isinstance(options, bool):
            return False
        
        tmp_options = copy.deepcopy(options)
        if len(tmp_options) > 0:
            cleaned_options_for_display = []
            for item in tmp_options:
                item.pop('session_id', None)
                item.pop('center_id', None)
                cleaned_options_for_display.append(item)

            display_table(cleaned_options_for_display)
            choice = input_with_timeout('----------> \nWait 10 seconds for updated options OR \n----------> \nEnter Choice e.g: 1.4 for (1st center 4th slot): ', 10)

        else:
            print("No viable options. Waiting for next update.")
            time.sleep(15)
            choice = '.'
        
    
    except TimeoutExpired:
        time.sleep(15)
        return True
    
    else:
        if choice == '.':
            return True
        else:
            choice = choice.split('.')
            choice = [int(item) for item in choice]
            print(f'============> Got {choice}')
            new_req = copy.deepcopy(BOOKING_REQUEST_TEMPLATE)
            new_req['beneficiaries'] = beneficiaries
            new_req['center_id'] = options[choice[0] - 1]['center_id']
            new_req['session_id'] = options[choice[0] - 1]['session_id']
            new_req['slot'] = options[int(choice[0]) - 1]['slots'][choice[1] - 1]
            print(f'Booking with info: {new_req}')

            return book_appointment(request_header, new_req)


def get_beneficiaries(request_header):
    beneficiaries = requests.get(BENEFICIARIES_URL, headers=request_header)

    if beneficiaries.status_code == 200:
        beneficiaries = beneficiaries.json()['beneficiaries']
        
        refined_beneficiaries = []
        for beneficiary in beneficiaries:
            tmp = {}
            tmp['beneficiary_reference_id'] = beneficiary['beneficiary_reference_id']
            tmp['name'] = beneficiary['name']
            tmp['vaccine'] = beneficiary['vaccine']
            tmp['status'] = beneficiary['vaccination_status']
            refined_beneficiaries.append(tmp)
        
        display_table(refined_beneficiaries)
        reqd_beneficiaries = input('Enter comma separated index numbers of beneficiaries to book for : ')
        beneficiary_idx = [int(idx) -1 for idx in reqd_beneficiaries.split(',')]
        reqd_beneficiaries = [(item['beneficiary_reference_id'], item['vaccine']) for idx, item in enumerate(refined_beneficiaries) if idx in beneficiary_idx]
        return reqd_beneficiaries

    else:
        print('Unable to fetch beneficiaries')
        print(beneficiaries.status_code)
        print(beneficiaries.text)
        sys.exit(1)


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
    parser.add_argument('--mobile', help='Pass the registered mobile to generate OTP')
    parser.add_argument('--token', help='Pass token directly')
    args = parser.parse_args()

    token = None
    
    if args.token:
        token = args.token
    elif args.mobile:
        token = generate_token_OTP(args.mobile)
    
    request_header = {"Authorization": f"Bearer {token}"}
    beneficiaries_dtls = get_beneficiaries(request_header)
    
    beneficiaries = [id for id, vaccine_type in beneficiaries_dtls]
    vaccine_type = max(vaccine_type for id, vaccine_type in beneficiaries_dtls)

    minimum_slots = int(input('Enter minimum number of slots available to filter for: '))

    TOKEN_VALID = True
    while TOKEN_VALID == True:
        TOKEN_VALID = check_and_book(request_header, vaccine_type, beneficiaries, minimum_slots)
        
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
