<h1 align="center"> Bombardier Fully Automated COVID-19 Vaccination Slot Booking Script</h1>

<div align="center">

<i>This is a fork over the neat [covid-vaccine-booking](https://github.com/pallupz/covid-vaccine-booking). Thanks for creating a playground for me to build on :metal:</i>
<i>It allows rescheduling for both dose 1 and 2 withing the script but Only 1 beneficiary at a time</i>

</div>

## Guide

### Pre-requisites

1. [Setup on Windows/Linux/MacOS/Docker/AWS](https://github.com/bombardier-gif/covid-vaccine-booking/wiki/Setup) (Required)
2. [KVDB Bucket](https://github.com/bombardier-gif/covid-vaccine-booking/wiki/KVDB)
3. Phone Setup
   1. Android
      1. [CoWIN OTP Retriever](https://github.com/bombardier-gif/covid-vaccine-booking/wiki/CoWIN-OTP-Retriever) (Recommended)
      2. [IFTTT](https://github.com/bombardier-gif/covid-vaccine-booking/wiki/IFTTT)
   2. [iPhone](https://github.com/bombardier-gif/covid-vaccine-booking/wiki/Shortcuts)

### Usage

`./covid-vaccine-slot-booking.py [--mobile <mobile_no>] [--token <token>] [--kvdb-bucket <kvdb_bucket_key] [--config <path_to_config] [--no-tty]`

This very basic CLI based script can be used to automate covid vaccination slot booking on Co-WIN Platform.

_Note: All parameters are optional._

| Parameter     | Description                                                |
| ------------- | ---------------------------------------------------------- |
| --mobile      | Registered mobile on CoWIN                                 |
| --token       | Token of the user                                          |
| --kvdb-bucket | kvdb.io bucket key                                         |
| --config      | Path to store the configuration file                       |
| --no-tty      | Do not ask any terminal inputs. Proceed with smart choices |

| Environment Variable | Description              |
| -------------------- | ------------------------ |
| BEEP                 | Setting `no` skips beeps |
| KVDB_BUCKET          | kvdb.io bucket key       |

## Contents

- [Before you start](#before-you-start)
- [COVID-19 Vaccination Slot Booking Script](#covid-19-vaccination-slot-booking-script)
  - [Important](#important)
  - [Steps](#steps)
- [Troubleshooting common problems](#troubleshooting-common-problems)

## Before you start

1. If you face any issues please refer to the [troubleshooting section](#troubleshooting-common-problems) at the end of this doc
2. If you are still facing errors and want to run this script on windows using exe, please see the section below [How to run on windows](#how-to-run-on-windows)
3. Instructions for iOS have also been added. See the [Setup Guide for iOS](#setup-guide-for-ios) for details. Please note that its not possible to automate the OTP auto read on iOS completely, however its possible to make it a 1 tap process, which is far better than seeing and entering the OTP manually.

## COVID-19 Vaccination Slot Booking Script

This very basic CLI based script can be used to automate covid vaccination slot booking on Co-WIN Platform.

### Important:

- POC project. **Use at your own risk**.
- Do NOT use unless all beneficiaries selected are supposed to get the same vaccine and dose.
- No option to register new user or add beneficiaries. This can be used only after beneficiary has been added through the official app/site
- If you accidentally book a slot, don't worry. You can always login to the official portal and cancel that.
- API Details: https://apisetu.gov.in/public/marketplace/api/cowin/cowinapi-v2
- And finally, I know code quality probably isn't great. Suggestions are welcome.

## Steps:

1. Run script:
   `python src\covid-vaccine-slot-booking.py`
2. Select Beneficiaries. Read the important notes. You can select multiple beneficiaries by providing comma-separated index values such as `1,2`:

   ```
   Enter the registered mobile number: ██████████
   Requesting OTP with mobile number ██████████..
   Enter OTP: 999999
   Validating OTP..
   Token Generated: █████████████████████████████████████████████████████████████
   Fetching registered beneficiaries..
   +-------+----------------------------+---------------------------+------------+
   | idx   | beneficiary_reference_id   | name                      | vaccine    |
   +=======+============================+===========================+============+
   | 1     | ██████████████             | █████████████████████████ | COVISHIELD |
   +-------+----------------------------+---------------------------+------------+
   | 2     | ██████████████             | █████████████████         |            |
   +-------+----------------------------+---------------------------+------------+

   ################# IMPORTANT NOTES #################
   # 1. While selecting beneficiaries, make sure that selected beneficiaries are all taking the same dose: either first OR second.
   # Please do no try to club together booking for first dose for one beneficiary and second dose for another beneficiary.
   #
   # 2. While selecting beneficiaries, also make sure that beneficiaries selected for second dose are all taking the same vaccine: COVISHIELD OR COVAXIN.
   # Please do no try to club together booking for beneficiary taking COVISHIELD with beneficiary taking COVAXIN.
   ###################################################

   Enter comma separated index numbers of beneficiaries to book for : 2
   ```

3. Ensure correct beneficiaries are getting selected:

   ```
   Selected beneficiaries:
   +-------+----------------------------+-----------+
   | idx   | beneficiary_reference_id   | vaccine   |
   +=======+============================+===========+
   | 1     | ██████████████             |           |
   +-------+----------------------------+-----------+
   ```

4. Select a state
   ```
   +-------+-----------------------------+
   | idx   | state                       |
   +=======+=============================+
   | 1     | Andaman and Nicobar Islands |
   +-------+-----------------------------+
   | 2     | Andhra Pradesh              |
   +-------+-----------------------------+
   +-------+-----------------------------+
   +-------+-----------------------------+
   | 35    | Uttar Pradesh               |
   +-------+-----------------------------+
   | 36    | Uttarakhand                 |
   +-------+-----------------------------+
   | 37    | West Bengal                 |
   +-------+-----------------------------+
   ```
   ```
   Enter State index: 18
   ```
5. Select districts you are interested in. Multiple districts can be selected by providing comma-separated index values
   ```
   +-------+--------------------+
   | idx   | district           |
   +=======+====================+
   | 1     | Alappuzha          |
   +-------+--------------------+
   | 2     | Ernakulam          |
   +-------+--------------------+
   | 3     | Idukki             |
   +-------+--------------------+
   +-------+--------------------+
   +-------+--------------------+
   | 13    | Thrissur           |
   +-------+--------------------+
   | 14    | Wayanad            |
   +-------+--------------------+
   ```
   ```
   Enter comma separated index numbers of districts to monitor : 2,13
   ```
6. Ensure correct districts are getting selected.
   ```
   Selected districts:
   +-------+---------------+-----------------+-----------------------+
   | idx   | district_id   | district_name   | district_alert_freq   |
   +=======+===============+=================+=======================+
   | 1     | 307           | Ernakulam       | 660                   |
   +-------+---------------+-----------------+-----------------------+
   | 2     | 303           | Thrissur        | 3080                  |
   +-------+---------------+-----------------+-----------------------+
   ```
7. Enter the minimum number of slots to be available at the center:
   ```
   Filter out centers with availability less than: 5
   ```
8. Script will now start to monitor slots in these districts every 15 seconds. `Note`: It will ask you monitor frequency `ProTip`: Do not select less than 5 seconds it will bombard cowin server and will get your request blocked, create issues in OTP generation for your number. #85
   ```
   ===================================================================================
   Centers available in Ernakulam from 01-05-2021 as of 2021-04-30 15:13:44: 0
   Centers available in Thrissur from 01-05-2021 as of 2021-04-30 15:13:44: 0
   No viable options. Waiting for next update in 15s.
   ===================================================================================
   Centers available in Ernakulam from 01-05-2021 as of 2021-04-30 15:13:59: 0
   Centers available in Thrissur from 01-05-2021 as of 2021-04-30 15:13:59: 0
   No viable options. Waiting for next update in 15s.
   ```
9. If at any stage your token becomes invalid, the script will make a beep and prompt for `y` or `n`. If you'd like to continue, provide `y` and proceed to allow using same mobile number
   ```
   Token is INVALID.
   Try for a new Token? (y/n): y
   Try for OTP with mobile number ███████████? (y/n) : y
   Enter OTP: 888888
   ```
10. When a center with more than minimum number of slots is available, the script will make a beep sound - different frequency for different district. It will then display the available options as table:
    ```
    ===================================================================================
    Centers available in Ernakulam from 01-05-2021 as of 2021-04-30 15:34:19: 1
    Centers available in Thrissur from 01-05-2021 as of 2021-04-30 15:34:19: 0
    +-------+----------------+------------+-------------+------------+------------------------------------------------------------------------------+
    | idx   | name           | district   | available   | date       | slots                                                                        |
    +=======+================+============+=============+============+==============================================================================+
    | 1     | Ayyampilly PHC | Ernakulam  | 30          | 01-05-2021 | ['09:00AM-10:00AM', '10:00AM-11:00AM', '11:00AM-12:00PM', '12:00PM-02:00PM'] |
    +-------+----------------+------------+-------------+------------+------------------------------------------------------------------------------+
    ---------->  Wait 10 seconds for updated options OR
    ---------->  Enter a choice e.g: 1.4 for (1st center 4th slot): 1.3
    ```
11. Before the next update, you'll have 10 seconds to provide a choice in the format `centerIndex.slotIndex` eg: The input`1.4` will select the vaccination center in second row and its fourth slot.
12. After successful slot booking, the appointment slip will be downloaded in your current working directory in the format `mobile_appointmentno`.

<br>

## Troubleshooting common problems

### Problem 1

```
Can't setFont(Times-Roman) missing the T1 files?
Originally <class 'TypeError'>: makeT1Font() argument 2 must be str, not None
```

**Solution 1:** Then run the python script directly in the **src** folder after installing the required modules from **requirements.txt.** That solved it for me

**Solution 2:** If you are running ubantu(tested) or Windows, this problem is due to some font files from package (reportlab) which are included in arch linux but not on Ubuntu. Follow these steps to install reportlab correctly. It can be done after you have installed all the requirements rom txt file.

1.  `git clone https://github.com/Distrotech/reportlab.git`
2.  `cd reportlab`
3.  `python3 setup.py install`

    This will download all the font files.

**Solution 3**: Try to perform the test first in **test** folder for captcha first to see if this error still there.

**Solution 4:** (Recommended) Try to use this Linux executable " **./covid-vaccine-slot-booking**-linux " file directly from terminal it does not require anything to install just like windows exe. **Windows exe is under going testing**

### Problem 2

Regarding beep package - Device not found or beep not found

**Solution** : Follow these steps for Ubuntu

1.  `sudo apt-get install beep` #Install this once
2.  `sudo modprobe pcspkr` #This will solve Device not found error
3.  Testing beep is simple just type `beep` in terminal, this will produce a beep sound from your speakers.

### Problem 3

SMS is not read automatically

**Solution**: Make sure the settings shown below are the same on your phone:

|                                                                                                                                                                                                                                     |                                                                                                                                                                                                            |
| :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------: | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------: |
| <img src="https://user-images.githubusercontent.com/83712877/117325821-b5a58c00-aeae-11eb-8156-2ea585a77834.png" alt="image" width="300" /> <br> Using IFTTT: This number must match the number you enter while running the script. | <img src="https://user-images.githubusercontent.com/3753228/117948585-e4988380-b32e-11eb-9837-9abdda21c23e.png" alt="image" width="300" /> <br> CowinOTPRetriever App: Make sure the switch is flipped on. |

## Running unit tests with `pytest`

- Install `pytest` from `requirements.txt` if not already installed
- Note that `src/conftest.py` is an empty config file [needed for pytest to run](https://stackoverflow.com/a/50610630/13866213)
- Run `python3 -m pytest` from command line from the repo root to execute all tests in `src/tests`
