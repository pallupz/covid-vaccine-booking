#!/usr/bin/env python3

import copy
import traceback
import time
from types import SimpleNamespace
import requests, sys, argparse, os, datetime
import jwt
from utils import generate_token_OTP, generate_token_OTP_manual, check_and_book, beep, BENEFICIARIES_URL, WARNING_BEEP_DURATION, \
    display_info_dict, save_user_info, collect_user_details, get_saved_user_info, confirm_and_proceed, get_dose_num, display_table, fetch_beneficiaries

def is_token_valid(token):
    payload = jwt.decode(token, options={"verify_signature": False})
    remaining_seconds = payload['iat'] + 600 - int(time.time())
    if remaining_seconds <= 1*30: # 30 secs early before expiry for clock issues
        return False
    if remaining_seconds <= 60:
        print("Token is about to expire in next 1 min ...")
    return True

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--token', help='Pass token directly')
    args = parser.parse_args()

    filename = 'vaccine-booking-details-'
    mobile = None

    print('Running Script')
    beep(500, 150)

    try:
        base_request_header = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
            'origin': 'https://selfregistration.cowin.gov.in/',
            'referer': 'https://selfregistration.cowin.gov.in/'
        
        }

        token = None
        if args.token:
            token = args.token
        else:
            mobile = input("Enter the registered mobile number: ")
            filename = filename + mobile + ".json"
            otp_pref = input("\nDo you want to enter OTP manually, instead of auto-read? \nRemember selecting n would require some setup described in README (y/n Default n): ")
            otp_pref = otp_pref if otp_pref else "n"
            while token is None:
                if otp_pref=="n":
                    try:
                        token = generate_token_OTP(mobile, base_request_header)
                    except Exception as e:
                        print(str(e))
                        print('OTP Retrying in 5 seconds')
                        time.sleep(5)
                elif otp_pref=="y":
                    token = generate_token_OTP_manual(mobile, base_request_header)

        request_header = copy.deepcopy(base_request_header)
        request_header["Authorization"] = f"Bearer {token}"

        if os.path.exists(filename):
            print("\n=================================== Note ===================================\n")
            print(f"Info from perhaps a previous run already exists in {filename} in this directory.")
            print(f"IMPORTANT: If this is your first time running this version of the application, DO NOT USE THE FILE!")
            try_file = input("Would you like to see the details and confirm to proceed? (y/n Default y): ")
            try_file = try_file if try_file else 'y'

            if try_file == 'y':
                collected_details = get_saved_user_info(filename)
                print("\n================================= Info =================================\n")
                display_info_dict(collected_details)

                file_acceptable = input("\nProceed with above info? (y/n Default y): ")
                file_acceptable = file_acceptable if file_acceptable else 'y'

                if file_acceptable != 'y':
                    collected_details = collect_user_details(request_header)
                    save_user_info(filename, collected_details)

            else:
                collected_details = collect_user_details(request_header)
                save_user_info(filename, collected_details)

        else:
            collected_details = collect_user_details(request_header)
            save_user_info(filename, collected_details)
            confirm_and_proceed(collected_details)

        # HACK: Temporary workaround for not supporting reschedule appointments
        beneficiary_ref_ids = [beneficiary["bref_id"]
                               for beneficiary in collected_details["beneficiary_dtls"]]
        beneficiary_dtls    = fetch_beneficiaries(request_header)
        if beneficiary_dtls.status_code == 200:
            beneficiary_dtls    = [beneficiary
                                   for beneficiary in beneficiary_dtls.json()['beneficiaries']
                                   if  beneficiary['beneficiary_reference_id'] in beneficiary_ref_ids]
            active_appointments = []
            for beneficiary in beneficiary_dtls:
                expected_appointments = (1 if beneficiary['vaccination_status'] == "Partially Vaccinated" else 0)
                if len(beneficiary['appointments']) > expected_appointments:
                    data             = beneficiary['appointments'][expected_appointments]
                    beneficiary_data = {'name': data['name'],
                                        'state_name': data['state_name'],
                                        'dose': data['dose'],
                                        'date': data['date'],
                                        'slot': data['slot']}
                    active_appointments.append({"beneficiary": beneficiary['name'], **beneficiary_data})

            if active_appointments:
                print("The following appointments are active! Please cancel them manually first to continue")
                display_table(active_appointments)
                beep(WARNING_BEEP_DURATION[0], WARNING_BEEP_DURATION[1])
                return
        else:
            print("WARNING: Failed to check if any beneficiary has active appointments. Please cancel before using this script")
            input("Press any key to continue execution...")

        info = SimpleNamespace(**collected_details)

        while True: # infinite-loop
            # create new request_header
            request_header = copy.deepcopy(base_request_header)
            request_header["Authorization"] = f"Bearer {token}"

            # call function to check and book slots
            try:
                token_valid = is_token_valid(token)

                # token is invalid ? 
                # If yes, generate new one
                if not token_valid: 
                    print('Token is INVALID.')
                    token = None
                    while token is None:
                        if otp_pref=="n":
                            try:
                                token = generate_token_OTP(mobile, base_request_header)
                            except Exception as e:
                                print(str(e))
                                print('OTP Retrying in 5 seconds')
                                time.sleep(5)
                        elif otp_pref=="y":
                            token = generate_token_OTP_manual(mobile, base_request_header)

                check_and_book(
                    request_header, 
                    info.beneficiary_dtls,
                    info.location_dtls,
                    info.pin_code_location_dtls,
                    info.search_option,
                    min_slots=info.minimum_slots,
                    ref_freq=info.refresh_freq,
                    auto_book=info.auto_book,
                    start_date=info.start_date,
                    vaccine_type=info.vaccine_type,
                    fee_type=info.fee_type,
                    mobile=mobile,
                    captcha_automation=info.captcha_automation,
                    dose_num=get_dose_num(collected_details)
                            )
            except Exception as e:
                print(str(e))
                print('Retryin in 5 seconds')
                time.sleep(5)

    except Exception as e:
        print(str(e))
        print('Exiting Script')
        os.system("pause")


if __name__ == '__main__':
    main()
