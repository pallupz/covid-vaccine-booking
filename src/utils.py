import json
from hashlib import sha256
from inputimeout import inputimeout, TimeoutOccurred
import tabulate, copy, time, datetime, requests, sys, os, random
from captcha import captcha_builder

BOOKING_URL = "https://cdn-api.co-vin.in/api/v2/appointment/schedule"
BENEFICIARIES_URL = "https://cdn-api.co-vin.in/api/v2/appointment/beneficiaries"
CALENDAR_URL_DISTRICT = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/calendarByDistrict?district_id={0}&date={1}"
CALENDAR_URL_PINCODE = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/calendarByPin?pincode={0}&date={1}"
CAPTCHA_URL = "https://cdn-api.co-vin.in/api/v2/auth/getRecaptcha"
OTP_PUBLIC_URL = 'https://cdn-api.co-vin.in/api/v2/auth/public/generateOTP'
OTP_PRO_URL = 'https://cdn-api.co-vin.in/api/v2/auth/generateMobileOTP'

WARNING_BEEP_DURATION = (1000, 2000)


try:
    import winsound

except ImportError:
    import os

    def beep(freq, duration):
        # apt install sox/brew install sox
        os.system(
                f"play -n synth {duration/1000} sin {freq} >/dev/null 2>&1")

else:
    def beep(freq, duration):
        winsound.Beep(freq, duration)


def viable_options(resp, minimum_slots, min_age_booking, fee_type, dose):
    options = []
    if len(resp['centers']) >= 0:
        for center in resp['centers']:
            for session in center['sessions']:
                # availability = session['available_capacity']
                availability = session['available_capacity_dose1'] if dose == 1 else session['available_capacity_dose2']
                if (availability >= minimum_slots) \
                        and (session['min_age_limit'] <= min_age_booking)\
                        and (center['fee_type'] in fee_type):
                    out = {
                        'name': center['name'],
                        'district': center['district_name'],
                        'pincode': center['pincode'],
                        'center_id': center['center_id'],
                        'available': availability,
                        'date': session['date'],
                        'slots': session['slots'],
                        'session_id': session['session_id']
                    }
                    options.append(out)

                else:
                    pass
    else:
        pass

    return options


def display_table(dict_list):
    """
    This function
        1. Takes a list of dictionary
        2. Add an Index column, and
        3. Displays the data in tabular format
    """
    header = ['idx'] + list(dict_list[0].keys())
    rows = [[idx + 1] + list(x.values()) for idx, x in enumerate(dict_list)]
    print(tabulate.tabulate(rows, header, tablefmt='grid'))


def display_info_dict(details):
    for key, value in details.items():
        if isinstance(value, list):
            if all(isinstance(item, dict) for item in value):
                print(f"\t{key}:")
                display_table(value)
            else:
                print(f"\t{key}\t: {value}")
        else:
            print(f"\t{key}\t: {value}")


def confirm_and_proceed(collected_details):
    print("\n================================= Confirm Info =================================\n")
    display_info_dict(collected_details)

    confirm = input("\nProceed with above info (y/n Default y) : ")
    confirm = confirm if confirm else 'y'
    if confirm != 'y':
        print("Details not confirmed. Exiting process.")
        os.system("pause")
        sys.exit()


def save_user_info(filename, details):
    print("\n================================= Save Info =================================\n")
    save_info = input("Would you like to save this as a JSON file for easy use next time?: (y/n Default y): ")
    save_info = save_info if save_info else 'y'
    if save_info == 'y':
        with open(filename, 'w') as f:
            json.dump(details, f)

        print(f"Info saved to {filename} in {os.getcwd()}")


def get_saved_user_info(filename):
    with open(filename, 'r') as f:
        data = json.load(f)

    return data


def collect_user_details(request_header):
    # Get Beneficiaries
    print("Fetching registered beneficiaries.. ")
    beneficiary_dtls = get_beneficiaries(request_header)

    if len(beneficiary_dtls) == 0:
        print("There should be at least one beneficiary. Exiting.")
        os.system("pause")
        sys.exit(1)

    # Make sure all beneficiaries have the same type of vaccine
    vaccine_types = [beneficiary['vaccine'] for beneficiary in beneficiary_dtls]
    statuses = [beneficiary['status'] for beneficiary in beneficiary_dtls]

    if len(set(statuses)) > 1:
        print("\n================================= Important =================================\n")
        print(f"All beneficiaries in one attempt should be of same vaccination status (same dose). Found {statuses}")
        os.system("pause")
        sys.exit(1)

    vaccines = set(vaccine_types)
    if len(vaccines) > 1 and ('' in vaccines):
        vaccines.remove('')
        vaccine_types.remove('')
        print("\n================================= Important =================================\n")
        print(f"Some of the beneficiaries have a set vaccine preference ({vaccines}) and some do not.")
        print("Results will be filtered to show only the set vaccine preference.")
        os.system("pause")

    if len(vaccines) != 1:
        print("\n================================= Important =================================\n")
        print(f"All beneficiaries in one attempt should have the same vaccine type. Found {len(vaccines)}")
        os.system("pause")
        sys.exit(1)

    vaccine_type = vaccine_types[0]
    if not vaccine_type:
        print("\n================================= Vaccine Info =================================\n")
        vaccine_type = get_vaccine_preference()

    print("\n================================= Location Info =================================\n")
    # get search method to use
    search_option = input(
        """Search by Pincode? Or by State/District? \nEnter 1 for Pincode or 2 for State/District. (Default 2) : """)

    if not search_option or int(search_option) not in [1, 2]:
        search_option = 2
    else:
        search_option = int(search_option)

    if search_option == 2:
        # Collect vaccination center preferance
        location_dtls = get_districts(request_header)

    else:
        # Collect vaccination center preferance
        location_dtls = get_pincodes()

    print("\n================================= Additional Info =================================\n")

    # Set filter condition
    minimum_slots = input(f'Filter out centers with availability less than ? Minimum {len(beneficiary_dtls)} : ')
    if minimum_slots:
        minimum_slots = int(minimum_slots) if int(minimum_slots) >= len(beneficiary_dtls) else len(beneficiary_dtls)
    else:
        minimum_slots = len(beneficiary_dtls)

    # Get refresh frequency
    refresh_freq = input('How often do you want to refresh the calendar (in seconds)? Default 15. Minimum 5. : ')
    refresh_freq = int(refresh_freq) if refresh_freq and int(refresh_freq) >= 5 else 15

    # Get search start date
    start_date = input(
        '\nSearch for next seven day starting from when?\nUse 1 for today, 2 for tomorrow, or provide a date in the format DD-MM-YYYY. Default 2: ')
    if not start_date:
        start_date = 2
    elif start_date in ['1', '2']:
        start_date = int(start_date)
    else:
        try:
            datetime.datetime.strptime(start_date, '%d-%m-%Y')
        except ValueError:
            print('Invalid Date! Proceeding with tomorrow.')
            start_date = 2

    # Get preference of Free/Paid option
    fee_type = get_fee_type_preference()

    print("\n=========== CAUTION! =========== CAUTION! CAUTION! =============== CAUTION! =======\n")
    print("===== BE CAREFUL WITH THIS OPTION! AUTO-BOOKING WILL BOOK THE FIRST AVAILABLE CENTRE, DATE, AND A RANDOM SLOT! =====")
    auto_book = input("Do you want to enable auto-booking? (yes-please or no) Default no: ")
    auto_book = 'no' if not auto_book else auto_book

    collected_details = {
        'beneficiary_dtls': beneficiary_dtls,
        'location_dtls': location_dtls,
        'search_option': search_option,
        'minimum_slots': minimum_slots,
        'refresh_freq': refresh_freq,
        'auto_book': auto_book,
        'start_date': start_date,
        'vaccine_type': vaccine_type,
        'fee_type': fee_type
    }

    return collected_details


def check_calendar_by_district(request_header, vaccine_type, location_dtls, start_date, minimum_slots, min_age_booking, fee_type, dose):
    """
    This function
        1. Takes details required to check vaccination calendar
        2. Filters result by minimum number of slots available
        3. Returns False if token is invalid
        4. Returns list of vaccination centers & slots if available
    """
    try:
        print('===================================================================================')
        today = datetime.datetime.today()
        base_url = CALENDAR_URL_DISTRICT

        if vaccine_type:
            base_url += f"&vaccine={vaccine_type}"

        options = []
        for location in location_dtls:
            resp = requests.get(base_url.format(location['district_id'], start_date), headers=request_header)

            if resp.status_code == 401:
                print('TOKEN INVALID')
                return False

            elif resp.status_code == 200:
                resp = resp.json()
                if 'centers' in resp:
                    print(f"Centers available in {location['district_name']} from {start_date} as of {today.strftime('%Y-%m-%d %H:%M:%S')}: {len(resp['centers'])}")
                    options += viable_options(resp, minimum_slots, min_age_booking, fee_type, dose)

            else:
                pass

        for location in location_dtls:
            if location['district_name'] in [option['district'] for option in options]:
                for _ in range(2):
                    beep(location['alert_freq'], 150)
        return options

    except Exception as e:
        print(str(e))
        beep(WARNING_BEEP_DURATION[0], WARNING_BEEP_DURATION[1])


def check_calendar_by_pincode(request_header, vaccine_type, location_dtls, start_date, minimum_slots, min_age_booking, fee_type, dose):
    """
    This function
        1. Takes details required to check vaccination calendar
        2. Filters result by minimum number of slots available
        3. Returns False if token is invalid
        4. Returns list of vaccination centers & slots if available
    """
    try:
        print('===================================================================================')
        today = datetime.datetime.today()
        base_url = CALENDAR_URL_PINCODE

        if vaccine_type:
            base_url += f"&vaccine={vaccine_type}"

        options = []
        for location in location_dtls:
            resp = requests.get(base_url.format(location['pincode'], start_date), headers=request_header)

            if resp.status_code == 401:
                print('TOKEN INVALID')
                return False

            elif resp.status_code == 200:
                resp = resp.json()
                if 'centers' in resp:
                    print(f"Centers available in {location['pincode']} from {start_date} as of {today.strftime('%Y-%m-%d %H:%M:%S')}: {len(resp['centers'])}")
                    options += viable_options(resp, minimum_slots, min_age_booking, fee_type, dose)

            else:
                pass

        for location in location_dtls:
            if int(location['pincode']) in [option['pincode'] for option in options]:
                for _ in range(2):
                    beep(location['alert_freq'], 150)

        return options

    except Exception as e:
        print(str(e))
        beep(WARNING_BEEP_DURATION[0], WARNING_BEEP_DURATION[1])


def generate_captcha(request_header):
    print('================================= GETTING CAPTCHA ==================================================')
    resp = requests.post(CAPTCHA_URL, headers=request_header)
    print(f'Captcha Response Code: {resp.status_code}')

    if resp.status_code == 200:
        return captcha_builder(resp.json())


def book_appointment(request_header, details):
    """
    This function
        1. Takes details in json format
        2. Attempts to book an appointment using the details
        3. Returns True or False depending on Token Validity
    """
    try:
        valid_captcha = True
        while valid_captcha:
#             captcha = generate_captcha(request_header)
#             details['captcha'] = captcha

            print('================================= ATTEMPTING BOOKING ==================================================')

            resp = requests.post(BOOKING_URL, headers=request_header, json=details)
            print(f'Booking Response Code: {resp.status_code}')
            print(f'Booking Response : {resp.text}')

            if resp.status_code == 401:
                print('TOKEN INVALID')
                return False

            elif resp.status_code == 200:
                beep(WARNING_BEEP_DURATION[0], WARNING_BEEP_DURATION[1])
                print('##############    BOOKED!  ############################    BOOKED!  ##############')
                print("                        Hey, Hey, Hey! It's your lucky day!                       ")
                print('\nPress any key thrice to exit program.')
                os.system("pause")
                os.system("pause")
                os.system("pause")
                sys.exit()

            elif resp.status_code == 400:
                print(f'Response: {resp.status_code} : {resp.text}')
                pass

            else:
                print(f'Response: {resp.status_code} : {resp.text}')
                return True

    except Exception as e:
        print(str(e))
        beep(WARNING_BEEP_DURATION[0], WARNING_BEEP_DURATION[1])


def check_and_book(request_header, beneficiary_dtls, location_dtls, search_option, **kwargs):
    """
    This function
        1. Checks the vaccination calendar for available slots,
        2. Lists all viable options,
        3. Takes user's choice of vaccination center and slot,
        4. Calls function to book appointment, and
        5. Returns True or False depending on Token Validity
    """
    try:
        min_age_booking = get_min_age(beneficiary_dtls)

        minimum_slots = kwargs['min_slots']
        refresh_freq = kwargs['ref_freq']
        auto_book = kwargs['auto_book']
        start_date = kwargs['start_date']
        vaccine_type = kwargs['vaccine_type']
        fee_type = kwargs['fee_type']
        dose = 2 if [beneficiary['status'] for beneficiary in beneficiary_dtls][0] == 'Partially Vaccinated' else 1

        if isinstance(start_date, int) and start_date == 2:
            start_date = (datetime.datetime.today() + datetime.timedelta(days=1)).strftime("%d-%m-%Y")
        elif isinstance(start_date, int) and start_date == 1:
            start_date = datetime.datetime.today().strftime("%d-%m-%Y")
        else:
            pass

        if search_option == 2:
            options = check_calendar_by_district(request_header, vaccine_type, location_dtls, start_date,
                                                 minimum_slots, min_age_booking, fee_type, dose)
        else:
            options = check_calendar_by_pincode(request_header, vaccine_type, location_dtls, start_date,
                                                minimum_slots, min_age_booking, fee_type, dose)

        if isinstance(options, bool):
            return False

        options = sorted(options,
                         key=lambda k: (k['district'].lower(), k['pincode'],
                                        k['name'].lower(),
                                        datetime.datetime.strptime(k['date'], "%d-%m-%Y"))
                         )

        tmp_options = copy.deepcopy(options)
        if len(tmp_options) > 0:
            cleaned_options_for_display = []
            for item in tmp_options:
                item.pop('session_id', None)
                item.pop('center_id', None)
                cleaned_options_for_display.append(item)

            display_table(cleaned_options_for_display)
            if auto_book == 'yes-please':
                print("AUTO-BOOKING IS ENABLED. PROCEEDING WITH FIRST CENTRE, DATE, and RANDOM SLOT.")
                option = options[0]
                random_slot = random.randint(1, len(option['slots']))
                choice = f'1.{random_slot}'
            else:
                choice = inputimeout(
                    prompt='----------> Wait 20 seconds for updated options OR \n----------> Enter a choice e.g: 1.4 for (1st center 4th slot): ',
                    timeout=20)

        else:
            try:
                for i in range(refresh_freq, 0, -1):
                    msg = f"No viable options. Next update in {i} seconds. OR press 'Ctrl + C' to refresh now."
                    print(msg, end="\r", flush=True)
                    sys.stdout.flush()
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
            choice = '.'

    except TimeoutOccurred:
        time.sleep(1)
        return True

    else:
        if choice == '.':
            return True
        else:
            try:
                choice = choice.split('.')
                choice = [int(item) for item in choice]
                print(f'============> Got Choice: Center #{choice[0]}, Slot #{choice[1]}')

                new_req = {
                    'beneficiaries': [beneficiary['bref_id'] for beneficiary in beneficiary_dtls],
                    'dose': 2 if [beneficiary['status'] for beneficiary in beneficiary_dtls][0] == 'Partially Vaccinated' else 1,
                    'center_id' : options[choice[0] - 1]['center_id'],
                    'session_id': options[choice[0] - 1]['session_id'],
                    'slot'      : options[choice[0] - 1]['slots'][choice[1] - 1]
                }

                print(f'Booking with info: {new_req}')
                return book_appointment(request_header, new_req)

            except IndexError:
                print("============> Invalid Option!")
                os.system("pause")
                pass


def get_vaccine_preference():
    print("It seems you're trying to find a slot for your first dose. Do you have a vaccine preference?")
    preference = input("Enter 0 for No Preference, 1 for COVISHIELD, 2 for COVAXIN, or 3 for SPUTNIK V. Default 0 : ")
    preference = int(preference) if preference and int(preference) in [0, 1, 2, 3] else 0

    if preference == 1:
        return 'COVISHIELD'
    elif preference == 2:
        return 'COVAXIN'
    elif preference == 3:
        return 'SPUTNIK V'
    else:
        return None


def get_fee_type_preference():
    print("\nDo you have a fee type preference?")
    preference = input("Enter 0 for No Preference, 1 for Free Only, or 2 for Paid Only. Default 0 : ")
    preference = int(preference) if preference and int(preference) in [0, 1, 2] else 0

    if preference == 1:
        return ['Free']
    elif preference == 2:
        return ['Paid']
    else:
        return ['Free', 'Paid']


def get_pincodes():
    locations = []
    pincodes = input("Enter comma separated pincodes to monitor: ")
    for idx, pincode in enumerate(pincodes.split(',')):
        pincode = {
            'pincode': pincode,
            'alert_freq': 440 + ((2 * idx) * 110)
        }
        locations.append(pincode)
    return locations


def get_districts(request_header):
    """
    This function
        1. Lists all states, prompts to select one,
        2. Lists all districts in that state, prompts to select required ones, and
        3. Returns the list of districts as list(dict)
    """
    states = requests.get('https://cdn-api.co-vin.in/api/v2/admin/location/states', headers=request_header)

    if states.status_code == 200:
        states = states.json()['states']

        refined_states = []
        for state in states:
            tmp = {'state': state['state_name']}
            refined_states.append(tmp)

        display_table(refined_states)
        state = int(input('\nEnter State index: '))
        state_id = states[state - 1]['state_id']

        districts = requests.get(f'https://cdn-api.co-vin.in/api/v2/admin/location/districts/{state_id}', headers=request_header)

        if districts.status_code == 200:
            districts = districts.json()['districts']

            refined_districts = []
            for district in districts:
                tmp = {'district': district['district_name']}
                refined_districts.append(tmp)

            display_table(refined_districts)
            reqd_districts = input('\nEnter comma separated index numbers of districts to monitor : ')
            districts_idx = [int(idx) - 1 for idx in reqd_districts.split(',')]
            reqd_districts = [{
                'district_id': item['district_id'],
                'district_name': item['district_name'],
                'alert_freq': 440 + ((2 * idx) * 110)
            } for idx, item in enumerate(districts) if idx in districts_idx]

            print(f'Selected districts: ')
            display_table(reqd_districts)
            return reqd_districts

        else:
            print('Unable to fetch districts')
            print(districts.status_code)
            print(districts.text)
            os.system("pause")
            sys.exit(1)

    else:
        print('Unable to fetch states')
        print(states.status_code)
        print(states.text)
        os.system("pause")
        sys.exit(1)


def get_beneficiaries(request_header):
    """
    This function
        1. Fetches all beneficiaries registered under the mobile number,
        2. Prompts user to select the applicable beneficiaries, and
        3. Returns the list of beneficiaries as list(dict)
    """
    beneficiaries = requests.get(BENEFICIARIES_URL, headers=request_header)

    if beneficiaries.status_code == 200:
        beneficiaries = beneficiaries.json()['beneficiaries']

        refined_beneficiaries = []
        for beneficiary in beneficiaries:
            beneficiary['age'] = datetime.datetime.today().year - int(beneficiary['birth_year'])

            tmp = {
                'bref_id': beneficiary['beneficiary_reference_id'],
                'name': beneficiary['name'],
                'vaccine': beneficiary['vaccine'],
                'age': beneficiary['age'],
                'status': beneficiary['vaccination_status']
            }
            refined_beneficiaries.append(tmp)

        display_table(refined_beneficiaries)
        print("""
        ################# IMPORTANT NOTES #################
        # 1. While selecting beneficiaries, make sure that selected beneficiaries are all taking the same dose: either first OR second.
        #    Please do no try to club together booking for first dose for one beneficiary and second dose for another beneficiary.
        #
        # 2. While selecting beneficiaries, also make sure that beneficiaries selected for second dose are all taking the same vaccine: COVISHIELD OR COVAXIN.
        #    Please do no try to club together booking for beneficiary taking COVISHIELD with beneficiary taking COVAXIN.
        #
        # 3. If you're selecting multiple beneficiaries, make sure all are of the same age group (45+ or 18+) as defined by the govt.
        #    Please do not try to club together booking for younger and older beneficiaries.
        ###################################################
        """)
        reqd_beneficiaries = input('Enter comma separated index numbers of beneficiaries to book for : ')
        beneficiary_idx = [int(idx) - 1 for idx in reqd_beneficiaries.split(',')]
        reqd_beneficiaries = [{
            'bref_id': item['beneficiary_reference_id'],
            'name': item['name'],
            'vaccine': item['vaccine'],
            'age': item['age'],
            'status': item['vaccination_status']
        } for idx, item in enumerate(beneficiaries) if idx in beneficiary_idx]

        print(f'Selected beneficiaries: ')
        display_table(reqd_beneficiaries)
        return reqd_beneficiaries

    else:
        print('Unable to fetch beneficiaries')
        print(beneficiaries.status_code)
        print(beneficiaries.text)
        os.system("pause")
        return []


def get_min_age(beneficiary_dtls):
    """
    This function returns a min age argument, based on age of all beneficiaries
    :param beneficiary_dtls:
    :return: min_age:int
    """
    age_list = [item['age'] for item in beneficiary_dtls]
    min_age = min(age_list)
    return min_age


def generate_token_OTP(mobile, request_header):
    """
    This function generate OTP and returns a new token
    """

    if not mobile:
        print("Mobile number cannot be empty")
        os.system('pause')
        sys.exit()

    valid_token = False
    while not valid_token:
        try:
            data = {"mobile": mobile,
                    "secret": "U2FsdGVkX1+z/4Nr9nta+2DrVJSv7KS6VoQUSQ1ZXYDx/CJUkWxFYG6P3iM/VW+6jLQ9RDQVzp/RcZ8kbT41xw=="
            }
            txnId = requests.post(url=OTP_PRO_URL, json=data, headers=request_header)

            if txnId.status_code == 200:
                print(f"Successfully requested OTP for mobile number {mobile} at {datetime.datetime.today()}..")
                txnId = txnId.json()['txnId']

                OTP = input("Enter OTP (If this takes more than 2 minutes, press Enter to retry): ")
                if OTP:
                    data = {"otp": sha256(str(OTP).encode('utf-8')).hexdigest(), "txnId": txnId}
                    print(f"Validating OTP..")

                    token = requests.post(url='https://cdn-api.co-vin.in/api/v2/auth/validateMobileOtp', json=data,
                                          headers=request_header)
                    if token.status_code == 200:
                        token = token.json()['token']
                        print(f'Token Generated: {token}')
                        valid_token = True
                        return token

                    else:
                        print('Unable to Validate OTP')
                        print(f"Response: {token.text}")

                        retry = input(f"Retry with {mobile} ? (y/n Default y): ")
                        retry = retry if retry else 'y'
                        if retry == 'y':
                            pass
                        else:
                            sys.exit()

            else:
                print('Unable to Generate OTP')
                print(txnId.status_code, txnId.text)

                retry = input(f"Retry with {mobile} ? (y/n Default y): ")
                retry = retry if retry else 'y'
                if retry == 'y':
                    pass
                else:
                    sys.exit()

        except Exception as e:
            print(str(e))

