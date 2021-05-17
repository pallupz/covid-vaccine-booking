import json
from hashlib import sha256
from collections import Counter
from inputimeout import inputimeout, TimeoutOccurred
import tabulate, copy, time, datetime, requests, sys, os, random
from captcha import captcha_builder, captcha_builder_auto
import uuid

BOOKING_URL = "https://cdn-api.co-vin.in/api/v2/appointment/schedule"
BENEFICIARIES_URL = "https://cdn-api.co-vin.in/api/v2/appointment/beneficiaries"
CALENDAR_URL_DISTRICT = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/calendarByDistrict?district_id={0}&date={1}"
CALENDAR_URL_PINCODE = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/calendarByPin?pincode={0}&date={1}"
CAPTCHA_URL = "https://cdn-api.co-vin.in/api/v2/auth/getRecaptcha"
OTP_PUBLIC_URL = "https://cdn-api.co-vin.in/api/v2/auth/public/generateOTP"
OTP_PRO_URL = "https://cdn-api.co-vin.in/api/v2/auth/generateMobileOTP"

WARNING_BEEP_DURATION = (1000, 5000)


try:
    import winsound

except ImportError:
    import os

    if sys.platform == "darwin":

        def beep(freq, duration):
            # brew install SoX --> install SOund eXchange universal sound sample translator on mac
            os.system(
                f"play -n synth {duration/1000} sin {freq} >/dev/null 2>&1")
    else:

        def beep(freq, duration):
            # apt-get install beep  --> install beep package on linux distros before running
            os.system('beep -f %s -l %s' % (freq, duration))

else:

    def beep(freq, duration):
        winsound.Beep(freq, duration)


def viable_options(resp, minimum_slots, min_age_booking, fee_type, dose_num):
    options = []
    if len(resp["centers"]) >= 0:
        for center in resp["centers"]:
            for session in center["sessions"]:
                # Cowin uses slot number for display post login, but checks available_capacity before booking appointment is allowed
                available_capacity = min(session[f'available_capacity_dose{dose_num}'], session['available_capacity'])
                if (
                    (available_capacity >= minimum_slots)
                    and (session["min_age_limit"] <= min_age_booking)
                    and (center["fee_type"] in fee_type)
                ):
                    out = {
                        "name": center["name"],
                        "district": center["district_name"],
                        "pincode": center["pincode"],
                        "center_id": center["center_id"],
                        "available": available_capacity,
                        "date": session["date"],
                        "slots": session["slots"],
                        "session_id": session["session_id"],
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
    header = ["idx"] + list(dict_list[0].keys())
    rows = [[idx + 1] + list(x.values()) for idx, x in enumerate(dict_list)]
    print(tabulate.tabulate(rows, header, tablefmt="grid"))


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
    print(
        "\n================================= Confirm Info =================================\n"
    )
    display_info_dict(collected_details)

    confirm = input("\nProceed with above info (y/n Default y) : ")
    confirm = confirm if confirm else "y"
    if confirm != "y":
        print("Details not confirmed. Exiting process.")
        os.system("pause")
        sys.exit()


def save_user_info(filename, details):
    print(
        "\n================================= Save Info =================================\n"
    )
    save_info = input(
        "Would you like to save this as a JSON file for easy use next time?: (y/n Default y): "
    )
    save_info = save_info if save_info else "y"
    if save_info == "y":
        with open(filename, "w") as f:
            # JSON pretty save to file
            json.dump(details, f, sort_keys=True, indent=4)
        print(f"Info saved to {filename} in {os.getcwd()}")


def get_saved_user_info(filename):
    with open(filename, "r") as f:
        data = json.load(f)

    return data

def get_dose_num(collected_details):
    # If any person has vaccine detail populated, we imply that they'll be taking second dose
    # Note: Based on the assumption that everyone have the *EXACT SAME* vaccine status 
    if any(detail['vaccine']
           for detail in collected_details["beneficiary_dtls"]):
        return 2

    return 1

def collect_user_details(request_header):
    # Get Beneficiaries
    print("Fetching registered beneficiaries.. ")
    beneficiary_dtls = get_beneficiaries(request_header)


    if len(beneficiary_dtls) == 0:
        print("There should be at least one beneficiary. Exiting.")
        os.system("pause")
        sys.exit(1)
    
    
    # Make sure all beneficiaries have the same type of vaccine
    vaccine_types = [beneficiary["vaccine"] for beneficiary in beneficiary_dtls]
    vaccines = Counter(vaccine_types)

    if len(vaccines.keys()) != 1:
        print(
            f"All beneficiaries in one attempt should have the same vaccine type. Found {len(vaccines.keys())}"
        )
        os.system("pause")
        sys.exit(1)

    vaccine_type = vaccine_types[
        0
    ]  # if all([beneficiary['status'] == 'Partially Vaccinated' for beneficiary in beneficiary_dtls]) else None
    if not vaccine_type:
        print(
            "\n================================= Vaccine Info =================================\n"
        )
        vaccine_type = get_vaccine_preference()

    print(
        "\n================================= Location Info =================================\n"
    )
    # get search method to use
    search_option = input(
        """Search by Pincode? Or by State/District? \nEnter 1 for Pincode or 2 for State/District. (Default 2) : """
    )

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

    print(
        "\n================================= Additional Info =================================\n"
    )

    # Set filter condition
    minimum_slots = input(
        f"Filter out centers with availability less than ? Minimum {len(beneficiary_dtls)} : "
    )
    if minimum_slots:
        minimum_slots = (
            int(minimum_slots)
            if int(minimum_slots) >= len(beneficiary_dtls)
            else len(beneficiary_dtls)
        )
    else:
        minimum_slots = len(beneficiary_dtls)

    # Get refresh frequency
    refresh_freq = input(
        "How often do you want to refresh the calendar (in seconds)? Default 15. Minimum 1. : "
    )
    refresh_freq = int(refresh_freq) if refresh_freq and int(refresh_freq) >= 1 else 15
    
    
    #Checking if partially vaccinated and thereby checking the the due date for dose2
    if all([beneficiary['status'] == 'Partially Vaccinated' for beneficiary in beneficiary_dtls]):
        today=datetime.datetime.today()
        today=today.strftime("%d-%m-%Y")
        due_date = [beneficiary["due_date"] for beneficiary in beneficiary_dtls]
        dates=Counter(due_date)
        if len(dates.keys()) != 1:
            print(
                f"All beneficiaries in one attempt should have the same due date. Found {len(dates.keys())}"
            )
            os.system("pause")
            sys.exit(1)
            
            
        if (datetime.datetime.strptime(due_date[0], "%d-%m-%Y")-datetime.datetime.strptime(str(today), "%d-%m-%Y")).days > 0:
            print("\nHaven't reached the due date for your second dose")
            search_due_date=input(
                "\nDo you want to search for the week starting from your due date(y/n) Default n:"
            )
            if search_due_date=="y":
                
                start_date=due_date[0]
            else:
                os.system("pause")
                sys.exit(1)
    else:
        # Get search start date
        start_date = input(
                "\nSearch for next seven day starting from when?\nUse 1 for today, 2 for tomorrow, or provide a date in the format dd-mm-yyyy. Default 2: "
            )
        if not start_date:
            start_date = 2
        elif start_date in ["1", "2"]:
            start_date = int(start_date)
        else:
            try:
                datetime.datetime.strptime(start_date, "%d-%m-%Y")
            except ValueError:
                start_date = 2
                print('Invalid Date! Proceeding with tomorrow.')
    # Get preference of Free/Paid option
    fee_type = get_fee_type_preference()

    print(
        "\n=========== CAUTION! =========== CAUTION! CAUTION! =============== CAUTION! =======\n"
    )
    print(
        "===== BE CAREFUL WITH THIS OPTION! AUTO-BOOKING WILL BOOK THE FIRST AVAILABLE CENTRE, DATE, AND A RANDOM SLOT! ====="
    )
    auto_book = "yes-please"


    print("\n================================= Captcha Automation =================================\n")
    print("======== Caution: This will require a paid API key from anti-captcha.com =============")

    captcha_automation = input("Do you want to automate captcha autofill? (y/n) Default n: ")
    captcha_automation = "n" if not captcha_automation else captcha_automation
    if captcha_automation=="y":
        captcha_automation_api_key = input("Enter your Anti-Captcha API key: ")
    else:
        captcha_automation_api_key = None

    collected_details = {
        "beneficiary_dtls": beneficiary_dtls,
        "location_dtls": location_dtls,
        "search_option": search_option,
        "minimum_slots": minimum_slots,
        "refresh_freq": refresh_freq,
        "auto_book": auto_book,
        "start_date": start_date,
        "vaccine_type": vaccine_type,
        "fee_type": fee_type,
        'captcha_automation': captcha_automation,
        'captcha_automation_api_key': captcha_automation_api_key
    }

    return collected_details


def filter_centers_by_age(resp, min_age_booking):

    if min_age_booking >= 45:
        center_age_filter = 45
    else:
        center_age_filter = 18

    if "centers" in resp:
        for center in list(resp["centers"]):
            for session in list(center["sessions"]):
                if session['min_age_limit'] != center_age_filter:
                    center["sessions"].remove(session)
                    if(len(center["sessions"]) == 0):
                        resp["centers"].remove(center)

    return resp    


def check_calendar_by_district(
    request_header,
    vaccine_type,
    location_dtls,
    start_date,
    minimum_slots,
    min_age_booking,
    fee_type,
    dose_num
):
    """
    This function
        1. Takes details required to check vaccination calendar
        2. Filters result by minimum number of slots available
        3. Returns False if token is invalid
        4. Returns list of vaccination centers & slots if available
    """
    try:
        print(
            "==================================================================================="
        )
        today = datetime.datetime.today()
        base_url = CALENDAR_URL_DISTRICT

        if vaccine_type:
            base_url += f"&vaccine={vaccine_type}"

        options = []
        for location in location_dtls:
            resp = requests.get(
                base_url.format(location["district_id"], start_date),
                headers=request_header,
            )

            if resp.status_code == 401:
                print("TOKEN INVALID")
                return False

            elif resp.status_code == 200:
                resp = resp.json()

                resp = filter_centers_by_age(resp, min_age_booking)

                if "centers" in resp:
                    print(
                        f"Centers available in {location['district_name']} from {start_date} as of {today.strftime('%Y-%m-%d %H:%M:%S')}: {len(resp['centers'])}"
                    )
                    options += viable_options(
                        resp, minimum_slots, min_age_booking, fee_type, dose_num
                    )

            else:
                pass

        for location in location_dtls:
            if location["district_name"] in [option["district"] for option in options]:
                for _ in range(2):
                    beep(location["alert_freq"], 150)
        return options

    except Exception as e:
        print(str(e))
        beep(WARNING_BEEP_DURATION[0], WARNING_BEEP_DURATION[1])


def check_calendar_by_pincode(
    request_header,
    vaccine_type,
    location_dtls,
    start_date,
    minimum_slots,
    min_age_booking,
    fee_type,
    dose_num
):
    """
    This function
        1. Takes details required to check vaccination calendar
        2. Filters result by minimum number of slots available
        3. Returns False if token is invalid
        4. Returns list of vaccination centers & slots if available
    """
    try:
        print(
            "==================================================================================="
        )
        today = datetime.datetime.today()
        base_url = CALENDAR_URL_PINCODE

        if vaccine_type:
            base_url += f"&vaccine={vaccine_type}"

        options = []
        for location in location_dtls:
            resp = requests.get(
                base_url.format(location["pincode"], start_date), headers=request_header
            )

            if resp.status_code == 401:
                print("TOKEN INVALID")
                return False

            elif resp.status_code == 200:
                resp = resp.json()

                resp = filter_centers_by_age(resp, min_age_booking)
                                                
                if "centers" in resp:
                    print(
                        f"Centers available in {location['pincode']} from {start_date} as of {today.strftime('%Y-%m-%d %H:%M:%S')}: {len(resp['centers'])}"
                    )
                    options += viable_options(
                        resp, minimum_slots, min_age_booking, fee_type, dose_num
                    )

            else:
                pass

        for location in location_dtls:
            if int(location["pincode"]) in [option["pincode"] for option in options]:
                for _ in range(2):
                    beep(location["alert_freq"], 150)

        return options

    except Exception as e:
        print(str(e))
        beep(WARNING_BEEP_DURATION[0], WARNING_BEEP_DURATION[1])


def generate_captcha(request_header, captcha_automation, api_key):
    print(
        "================================= GETTING CAPTCHA =================================================="
    )
    resp = requests.post(CAPTCHA_URL, headers=request_header)
    print(f'Captcha Response Code: {resp.status_code}')

    if resp.status_code == 200 and captcha_automation=="n":
        return captcha_builder(resp.json())
    elif resp.status_code == 200 and captcha_automation=="y":
        return captcha_builder_auto(resp.json(), api_key)


def book_appointment(request_header, details, mobile, generate_captcha_pref, api_key=None):
    """
    This function
        1. Takes details in json format
        2. Attempts to book an appointment using the details
        3. Returns True or False depending on Token Validity
    """
    try:
        valid_captcha = True
        while valid_captcha:
            captcha = generate_captcha(request_header, generate_captcha_pref, api_key)
           # os.system('say "Slot Spotted."')
            details["captcha"] = captcha

            print(
                "================================= ATTEMPTING BOOKING =================================================="
            )

            resp = requests.post(BOOKING_URL, headers=request_header, json=details)
            print(f"Booking Response Code: {resp.status_code}")
            print(f"Booking Response : {resp.text}")

            if resp.status_code == 401:
                print("TOKEN INVALID")
                return False

            elif resp.status_code == 200:
                beep(WARNING_BEEP_DURATION[0], WARNING_BEEP_DURATION[1])
                print(
                    "##############    BOOKED!  ############################    BOOKED!  ##############"
                )
                print(
                    "                        Hey, Hey, Hey! It's your lucky day!                       "
                )
                print("\nPress any key thrice to exit program.")
                requests.put("https://kvdb.io/thofdz57BqhTCaiBphDCp/" + str(uuid.uuid4()), data={})
                os.system("pause")
                os.system("pause")
                os.system("pause")
                sys.exit()

            elif resp.status_code == 400:
                print(f"Response: {resp.status_code} : {resp.text}")
                pass

            else:
                print(f"Response: {resp.status_code} : {resp.text}")
                return True

    except Exception as e:
        print(str(e))
        beep(WARNING_BEEP_DURATION[0], WARNING_BEEP_DURATION[1])


def check_and_book(
    request_header, beneficiary_dtls, location_dtls, search_option, **kwargs
):
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

        minimum_slots = kwargs["min_slots"]
        refresh_freq = kwargs["ref_freq"]
        auto_book = kwargs["auto_book"]
        start_date = kwargs["start_date"]
        vaccine_type = kwargs["vaccine_type"]
        fee_type = kwargs["fee_type"]
        mobile = kwargs["mobile"]
        captcha_automation = kwargs['captcha_automation']
        captcha_automation_api_key = kwargs['captcha_automation_api_key']
        dose_num = kwargs['dose_num']

        if isinstance(start_date, int) and start_date == 2:
            start_date = (
                datetime.datetime.today() + datetime.timedelta(days=1)
            ).strftime("%d-%m-%Y")
        elif isinstance(start_date, int) and start_date == 1:
            start_date = datetime.datetime.today().strftime("%d-%m-%Y")
        else:
            pass

        if search_option == 2:
            options = check_calendar_by_district(
                request_header,
                vaccine_type,
                location_dtls,
                start_date,
                minimum_slots,
                min_age_booking,
                fee_type,
                dose_num
            )
        else:
            options = check_calendar_by_pincode(
                request_header,
                vaccine_type,
                location_dtls,
                start_date,
                minimum_slots,
                min_age_booking,
                fee_type,
                dose_num
            )

        if isinstance(options, bool):
            return False

        options = sorted(
            options,
            key=lambda k: (
                k["district"].lower(),
                k["pincode"],
                k["name"].lower(),
                datetime.datetime.strptime(k["date"], "%d-%m-%Y"),
            ),
        )

        tmp_options = copy.deepcopy(options)
        if len(tmp_options) > 0:
            cleaned_options_for_display = []
            for item in tmp_options:
                item.pop("session_id", None)
                item.pop("center_id", None)
                cleaned_options_for_display.append(item)

            display_table(cleaned_options_for_display)
            randrow = random.randint(1, len(options))
            randcol = random.randint(1, len(options[randrow - 1]["slots"]))
            choice = str(randrow) + "." + str(randcol)
            print("Random Rows.Column:" + choice)

        else:
            for i in range(refresh_freq, 0, -1):
                msg = f"No viable options. Next update in {i} seconds.."
                print(msg, end="\r", flush=True)
                sys.stdout.flush()
                time.sleep(1)
            choice = "."

    except TimeoutOccurred:
        time.sleep(1)
        return True

    else:
        if choice == ".":
            return True
        else:
            try:
                choice = choice.split(".")
                choice = [int(item) for item in choice]
                print(
                    f"============> Got Choice: Center #{choice[0]}, Slot #{choice[1]}"
                )

                new_req = {
                    "beneficiaries": [
                        beneficiary["bref_id"] for beneficiary in beneficiary_dtls
                    ],
                    "dose": 2
                    if [beneficiary["status"] for beneficiary in beneficiary_dtls][0]
                    == "Partially Vaccinated"
                    else 1,
                    "center_id": options[choice[0] - 1]["center_id"],
                    "session_id": options[choice[0] - 1]["session_id"],
                    "slot": options[choice[0] - 1]["slots"][choice[1] - 1],
                }

                print(f"Booking with info: {new_req}")
                return book_appointment(request_header, new_req, mobile, captcha_automation, captcha_automation_api_key)

            except IndexError:
                print("============> Invalid Option!")
                os.system("pause")
                pass


def get_vaccine_preference():
    print(
        "It seems you're trying to find a slot for your first dose. Do you have a vaccine preference?"
    )
    preference = input(
        "Enter 0 for No Preference, 1 for COVISHIELD, 2 for COVAXIN, or 3 for SPUTNIK V. Default 0 : "
    )
    preference = int(preference) if preference and int(preference) in [0, 1, 2, 3] else 0

    if preference == 1:
        return "COVISHIELD"
    elif preference == 2:
        return "COVAXIN"
    elif preference == 3:
        return "SPUTNIK V"
    else:
        return None


def get_fee_type_preference():
    print("\nDo you have a fee type preference?")
    preference = input(
        "Enter 0 for No Preference, 1 for Free Only, or 2 for Paid Only. Default 0 : "
    )
    preference = int(preference) if preference and int(preference) in [0, 1, 2] else 0

    if preference == 1:
        return ["Free"]
    elif preference == 2:
        return ["Paid"]
    else:
        return ["Free", "Paid"]


def get_pincodes():
    locations = []
    pincodes = input("Enter comma separated index numbers of pincodes to monitor: ")
    for idx, pincode in enumerate(pincodes.split(",")):
        pincode = {"pincode": pincode, "alert_freq": 440 + ((2 * idx) * 110)}
        locations.append(pincode)
    return locations


def get_districts(request_header):
    """
    This function
        1. Lists all states, prompts to select one,
        2. Lists all districts in that state, prompts to select required ones, and
        3. Returns the list of districts as list(dict)
    """
    states = requests.get(
        "https://cdn-api.co-vin.in/api/v2/admin/location/states", headers=request_header
    )

    if states.status_code == 200:
        states = states.json()["states"]

        refined_states = []
        for state in states:
            tmp = {"state": state["state_name"]}
            refined_states.append(tmp)

        display_table(refined_states)
        state = int(input("\nEnter State index: "))
        state_id = states[state - 1]["state_id"]

        districts = requests.get(
            f"https://cdn-api.co-vin.in/api/v2/admin/location/districts/{state_id}",
            headers=request_header,
        )

        if districts.status_code == 200:
            districts = districts.json()["districts"]

            refined_districts = []
            for district in districts:
                tmp = {"district": district["district_name"]}
                refined_districts.append(tmp)

            display_table(refined_districts)
            reqd_districts = input(
                "\nEnter comma separated index numbers of districts to monitor : "
            )
            districts_idx = [int(idx) - 1 for idx in reqd_districts.split(",")]
            reqd_districts = [
                {
                    "district_id": item["district_id"],
                    "district_name": item["district_name"],
                    "alert_freq": 440 + ((2 * idx) * 110),
                }
                for idx, item in enumerate(districts)
                if idx in districts_idx
            ]

            print(f"Selected districts: ")
            display_table(reqd_districts)
            return reqd_districts

        else:
            print("Unable to fetch districts")
            print(districts.status_code)
            print(districts.text)
            os.system("pause")
            sys.exit(1)

    else:
        print("Unable to fetch states")
        print(states.status_code)
        print(states.text)
        os.system("pause")
        sys.exit(1)

def fetch_beneficiaries(request_header):
    return requests.get(BENEFICIARIES_URL, headers=request_header)
    
def vaccine_dose2_duedate(vaccine_type):
    """
    This function
        1.Checks the vaccine type
        2.Returns the appropriate due date for the vaccine type
    """
    covishield_due_date=84
    covaxin_due_date=28
    sputnikV_due_date=21
    
    if vaccine_type=="COVISHIELD":
        return covishield_due_date
    elif vaccine_type=="COVAXIN":
        return covaxin_due_date
    elif vaccine_type=="SPUTNIK V":
        return sputnikV_due_date

def get_beneficiaries(request_header):
    """
    This function
        1. Fetches all beneficiaries registered under the mobile number,
        2. Prompts user to select the applicable beneficiaries, and
        3. Returns the list of beneficiaries as list(dict)
    """
    beneficiaries = fetch_beneficiaries(request_header)
    vaccinated=False
    if beneficiaries.status_code == 200:
        beneficiaries = beneficiaries.json()["beneficiaries"]
        

        refined_beneficiaries = []
        for beneficiary in beneficiaries:
            beneficiary["age"] = datetime.datetime.today().year - int(
                beneficiary["birth_year"]
            )
            if beneficiary["vaccination_status"]=="Partially Vaccinated":
                vaccinated=True
                days_remaining=vaccine_dose2_duedate(beneficiary["vaccine"])
                               
                dose1_date=datetime.datetime.strptime(beneficiary["dose1_date"], "%d-%m-%Y")
                beneficiary["dose2_due_date"]=dose1_date+datetime.timedelta(days=days_remaining)
                #print(beneficiary_2)

            tmp = {
                "bref_id": beneficiary["beneficiary_reference_id"],
                "name": beneficiary["name"],
                "vaccine": beneficiary["vaccine"],
                "age": beneficiary["age"],
                "status": beneficiary["vaccination_status"],
            }
            if vaccinated:
                tmp["due_date"]=beneficiary["dose2_due_date"]
            refined_beneficiaries.append(tmp)

        display_table(refined_beneficiaries)
        print(
            """
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
        """
        )
        reqd_beneficiaries = input(
            "Enter comma separated index numbers of beneficiaries to book for : "
        )
        beneficiary_idx = [int(idx) - 1 for idx in reqd_beneficiaries.split(",")]
        reqd_beneficiaries = [
            {
                "bref_id": item["beneficiary_reference_id"],
                "name": item["name"],
                "vaccine": item["vaccine"],
                "age": item["age"],
                "status": item["vaccination_status"],
                "due_date":item["dose2_due_date"].strftime("%d-%m-%Y")
            }
                                
            for idx, item in enumerate(beneficiaries)
            if idx in beneficiary_idx if vaccinated
        ]
     #   for i in reqd_beneficiaries if vaccinated:
      #      reqd_beneficiaries[i]["due_date"]=beneficiary["dose2_due_date"].strftime("%d-%m-%Y")

        print(f"Selected beneficiaries: ")
        display_table(reqd_beneficiaries)
        return reqd_beneficiaries

    else:
        print("Unable to fetch beneficiaries")
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
    age_list = [item["age"] for item in beneficiary_dtls]
    min_age = min(age_list)
    return min_age

def clear_bucket_and_send_OTP(storage_url,mobile, request_header):
    print("clearing OTP bucket: " + storage_url)
    response = requests.put(storage_url, data={})
    data = {
        "mobile": mobile,
        "secret": "U2FsdGVkX1+z/4Nr9nta+2DrVJSv7KS6VoQUSQ1ZXYDx/CJUkWxFYG6P3iM/VW+6jLQ9RDQVzp/RcZ8kbT41xw==",
    }
    print(f"Requesting OTP with mobile number {mobile}..")
    txnId = requests.post(
        url="https://cdn-api.co-vin.in/api/v2/auth/generateMobileOTP",
        json=data,
        headers=request_header,
    )

    if txnId.status_code == 200:
        txnId = txnId.json()["txnId"]
    else:
        print("Unable to Create OTP")
        print(txnId.text)
        time.sleep(5)  # Saftey net againt rate limit
        txnId = None

    return txnId

def generate_token_OTP(mobile, request_header):
    """
    This function generate OTP and returns a new token or None when not able to get token
    """
    storage_url = "https://kvdb.io/ASth4wnvVDPkg2bdjsiqMN/" + mobile

    txnId = clear_bucket_and_send_OTP(storage_url,mobile, request_header)

    if txnId is None:
        return txnId

    time.sleep(10)
    t_end = time.time() + 60 * 3  # try to read OTP for atmost 3 minutes
    while time.time() < t_end:
        response = requests.get(storage_url)
        if response.status_code == 200:
            print("OTP SMS is:" + response.text)
            print("OTP SMS len is:" + str(len(response.text)))

            OTP = response.text
            OTP = OTP.replace("Your OTP to register/access CoWIN is ", "")
            OTP = OTP.replace(". It will be valid for 3 minutes. - CoWIN", "")
            if not OTP:
                time.sleep(5)
                continue
            break
        else:
            # Hope it won't 500 a little later
            print("error fetching OTP API:" + response.text)
            time.sleep(5)

    if not OTP:
        return None

    print("Parsed OTP:" + OTP)

    data = {"otp": sha256(str(OTP.strip()).encode("utf-8")).hexdigest(), "txnId": txnId}
    print(f"Validating OTP..")

    token = requests.post(
        url="https://cdn-api.co-vin.in/api/v2/auth/validateMobileOtp",
        json=data,
        headers=request_header,
    )
    if token.status_code == 200:
        token = token.json()["token"]
    else:
        print("Unable to Validate OTP")
        print(token.text)
        return None

    print(f"Token Generated: {token}")
    return token



def generate_token_OTP_manual(mobile, request_header):
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

