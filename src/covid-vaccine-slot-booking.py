import copy
from collections import Counter
import requests, sys, argparse, os, datetime
from utils import generate_token_OTP, get_beneficiaries, check_and_book, get_districts, get_pincodes, beep, \
    BENEFICIARIES_URL, WARNING_BEEP_DURATION, get_vaccine_preference


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--token', help='Pass token directly')
    args = parser.parse_args()

    mobile = None
    try:
        base_request_header = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
        }
        
        token = None
        if args.token:
            token = args.token
        else:
            mobile = input("Enter the registered mobile number: ")
            while token is None:
                token = generate_token_OTP(mobile, base_request_header)

        request_header = copy.deepcopy(base_request_header)
        request_header["Authorization"] = f"Bearer {token}"
        # Get Beneficiaries
        print("Fetching registered beneficiaries.. ")
        beneficiary_dtls = get_beneficiaries(request_header)

        if len(beneficiary_dtls) == 0:
            print("There should be at least one beneficiary. Exiting.")
            os.system("pause")
            sys.exit(1)

        # Make sure all beneficiaries have the same type of vaccine
        vaccine_types = [beneficiary['vaccine'] for beneficiary in beneficiary_dtls]
        vaccines = Counter(vaccine_types)

        if len(vaccines.keys()) != 1:
            print(f"All beneficiaries in one attempt should have the same vaccine type. Found {len(vaccines.keys())}")
            os.system("pause")
            sys.exit(1)

        vaccine_type = vaccine_types[0]
        if not vaccine_type:
            print("\n================================= Vaccine Info =================================\n")
            vaccine_type = get_vaccine_preference()

        print("\n================================= Location Info =================================\n")

        search_option = input("""Search by Pincode? Or by State/District? \nEnter 1 for Pincode or 2 for State/District. (Default 2) : """)

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
        refresh_freq = input('How often do you want to refresh the calendar (in seconds)? Default 15. Minimum 1. : ')
        refresh_freq = int(refresh_freq) if refresh_freq and int(refresh_freq) >= 1 else 15

        # Get search start date
        start_date = input('Search for next seven day starting from when?\nUse 1 for today, 2 for tomorrow, or provide a date in the format yyyy-mm-dd. Default 2: ')
        if not start_date:
            start_date = 2
        elif start_date in ['1', '2']:
            start_date = int(start_date)
        else:
            try:
                datetime.datetime.strptime(start_date, '%Y-%m-%d')
            except ValueError:
                start_date = 2

        print("\n=========== CAUTION! =========== CAUTION! CAUTION! =============== CAUTION! =======\n")
        print(" ==== BE CAREFUL WITH THIS OPTION! AUTO-BOOKING WILL BOOK THE FIRST AVAILABLE CENTRE, DATE, AND SLOT! ==== ")
        auto_book = "yes-please"

        token_valid = True
        while token_valid:
            request_header = copy.deepcopy(base_request_header)
            request_header["Authorization"] = f"Bearer {token}"

            # call function to check and book slots
            token_valid = check_and_book(request_header, beneficiary_dtls, location_dtls, search_option,
                                         min_slots=minimum_slots,
                                         ref_freq=refresh_freq,
                                         auto_book=auto_book,
                                         start_date=start_date,
                                         vaccine_type=vaccine_type)

            # check if token is still valid
            beneficiaries_list = requests.get(BENEFICIARIES_URL, headers=request_header)
            if beneficiaries_list.status_code == 200:
                token_valid = True

            else:
                # if token invalid, regenerate OTP and new token
                beep(WARNING_BEEP_DURATION[0], WARNING_BEEP_DURATION[1])
                print('Token is INVALID.')
                token_valid = False
                token = None

                while token is None:
                    token = generate_token_OTP(mobile, base_request_header)
                token_valid = True

    except Exception as e:
        print(str(e))
        print('Exiting Script')
        os.system("pause")


if __name__ == '__main__':
    main()
