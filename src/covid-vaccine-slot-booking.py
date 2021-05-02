from collections import Counter
import requests, sys, argparse, os
from utils import generate_token_OTP, get_beneficiaries, check_and_book, get_districts, get_min_age, beep, \
    BENEFICIARIES_URL, WARNING_BEEP_DURATION


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--token', help='Pass token directly')
    args = parser.parse_args()

    mobile = None
    try:
        if args.token:
            token = args.token
        else:
            mobile = input("Enter the registered mobile number: ")
            token = generate_token_OTP(mobile)

        request_header = {"Authorization": f"Bearer {token}"}

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

        # Collect vaccination center preferance
        district_dtls = get_districts()

        # Set filter condition
        minimum_slots = int(input('Filter out centers with availability less than: '))
        minimum_slots = minimum_slots if minimum_slots > len(beneficiary_dtls) else len(beneficiary_dtls)

        token_valid = True
        while token_valid:
            request_header = {"Authorization": f"Bearer {token}"}

            # call function to check and book slots
            token_valid = check_and_book(request_header, beneficiary_dtls, district_dtls, minimum_slots)

            # check if token is still valid
            beneficiaries_list = requests.get(BENEFICIARIES_URL, headers=request_header)
            if beneficiaries_list.status_code == 200:
                token_valid = True

            else:
                # if token invalid, regenerate OTP and new token
                beep(WARNING_BEEP_DURATION[0], WARNING_BEEP_DURATION[1])
                print('Token is INVALID.')
                token_valid = False

                tryOTP = input('Try for a new Token? (y/n): ')
                if tryOTP.lower() == 'y':
                    if mobile:
                        tryOTP = input(f"Try for OTP with mobile number {mobile}? (y/n) : ")
                        if tryOTP.lower() == 'y':
                            token = generate_token_OTP(mobile)
                            token_valid = True
                        else:
                            token_valid = False
                            print("Exiting")
                    else:
                        mobile = input(f"Enter 10 digit mobile number for new OTP generation? : ")
                        token = generate_token_OTP(mobile)
                        token_valid = True
                else:
                    print("Exiting")
                    os.system("pause")

    except Exception as e:
        print(str(e))
        print('Exiting Script')
        os.system("pause")


if __name__ == '__main__':
    main()
