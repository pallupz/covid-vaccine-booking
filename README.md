<h1 align="center"> Bombardier Fully Automated COVID-19 Vaccination Slot Booking Script</h1>

<div align="center">

<i>This is a fork over the neat [covid-vaccine-booking](https://github.com/pallupz/covid-vaccine-booking). Thanks for creating a playground for me to build on :metal:</i>

<i>Loved the project? Please consider [donating](http://buymeacoff.ee/bombardier) to help it improve!</i>

</div>

## Quickstart Guide
**Instructions to follow on your laptop and phone below. To fetch OTP automatically, Step 2 is compulsory**

### 1. On your laptop
1. Make sure [Python 3.8+](https://python.org) is installed.
2. Clone this repo: ```git clone https://github.com/bombardier-gif/covid-vaccine-booking.git``` or download zip file and extract
3. Install the requirements:
	- ```pip install -r requirements.txt``` on Windows
	- ```pip3 install -r requirements.txt``` on Linux or Mac
4. Run the script:
	- ```python src\covid-vaccine-slot-booking.py``` on Windows
	- ```python3 src/covid-vaccine-slot-booking.py``` on Linux or Mac
5. Alternatively follow [these](#using-docker) steps to run this script using docker
6. Follow the steps. For more detailed guide: [Steps](#steps)

### 2. On your Phone (Required for fetching OTP automatically)
1. **Android Phone**: Follow either [Option 1: IFTTT app](#option-1-ifttt) or [Option 2: CoWIN OTP Retriever app](#option-2-cowin-otp-retriever)
2. **iPhone**: Follow [Using Shortcuts app](#using-shortcuts-app)

<br>

## Contents
  - [Before you start](#before-you-start)
  - [What this repository does](#what-this-repository-does)
  - [Setup Guide: Android](#setup-guide-for-android)
    - [Option 1: IFTTT app](#option-1-ifttt)
      - [Screenshots](#ifttt-steps-in-screenshots)
    - [Option 2: CoWIN OTP Retriever app](#option-2-cowin-otp-retriever) 
      - [Screenshots](#cowin-otp-retriever-steps-in-screenshots)
  - [Setup Guide: iOS](#setup-guide-for-ios)
    - [Using Shortcuts app](#using-shortcuts-app)
      - [Screenshots](#shortcuts-steps-in-screenshots)   
  - [COVID-19 Vaccination Slot Booking Script](#covid-19-vaccination-slot-booking-script)
    - [Important](#important)
    - [Usage](#usage)
    - [Third-Party Package Dependency](#third-party-package-dependency)
    - [Steps](#steps)
    - [How to run on windows](#how-to-run-on-windows)
    - [Using Docker](#using-docker)
  - [Troubleshooting common problems](#troubleshooting-common-problems)


## Before you start
1. If you face any issues please refer to the [troubleshooting section](#troubleshooting-common-problems) at the end of this doc
2. The captcha is a bit buggy and you may be required to make 5-6 tries before you are able to book
3. If you are still facing errors and want to run this script on windows using exe, please see the section below [How to run on windows](#how-to-run-on-windows)
4. Instructions for iOS have also been added. See the [Setup Guide for iOS](#setup-guide-for-ios) for details. Please note that its not possible to automate the OTP auto read on iOS completely, however its possible to make it a 1 tap process, which is far better than seeing and entering the OTP manually.

## What this repository does
1. Automates OTP read from the SMS after the token expires.
2. Randomly chooses one of the available slots instead of waiting for input from the user.
3. Reduces the polling wait to optimize on the polling frequency (hence the name bombardier)
<img src="https://user-images.githubusercontent.com/83712877/117467267-290fd200-af71-11eb-8461-d6e253c183d7.png" />

#### How it works via IFTTT app on Android
1. https://ifttt.com/ is used to create a SMS trigger. The trigger happens when the OTP SMS is received
2. The trigger sends the text of the SMS to a REST service, I have used a free service which needs 0 setup for a shared storage

#### How it works via CoWIN OTP Retriever app on Android
1. The [CoWinOTPRetriever Android app](./CoWinOtpRetreiver.apk) has been created to automatically read the OTP SMS and then send it to the shared storage
2. You only need to install and start the app, enter your CoWIN registered phone number, and then start the OTP listener.

#### How it works via Shortcuts app on iOS
1. [Shortcuts app](https://apps.apple.com/us/app/shortcuts/id915249334) is used to create an SMS trigger. The trigger happens when the OTP SMS is received
2. The trigger sends the text of the SMS to a REST service, I have used a free service which needs 0 setup for a shared storage

#### In Parallel
1. The script runs continuously to poll (same logic as the original repository)
2. Whenever the OTP expires, an OTP is requested
3. When the OTP SMS is received on the **Android**, phone, the above logic triggers to store the OTP SMS in the shared storage. On **iOS**, when the OTP SMS is received, the above logic triggers a notification which the user has to long press and confirm after which the OTP is stored in shared storage
4. The script polls the shared storage to get the OTP
5. Once the OTP is received, the polling resumes
6. If a free slot is found, rather than waiting for an input, it randomly chooses a slot and attempts to book

<br>

## KVDB setup
Regardless of Android or iOS, you will need a KVDB bucket configured to act as a key value store for your OTP messages coming from the IFTTT app or CoWIN OTP Retriever. You will need to update your personal key every 14 days or buy a pro account on kvdb.
Steps to get your own KVDB bucket:

1. Go to https://kvdb.io/
2. Click on Get started now
3. Enter your email and click on Create bucket
4. You will get a bucket key. It is just a random sequence of characters eg. ASth4wnvVDPkg2bdjsiqMN
5. Keep this key saved somewhere in your notes. We will need it.

## Setup Guide for Android

### Option 1: IFTTT

1. Create an account in ifttt.com (A premium paid account is recommended for a quicker response)
2. Create a new applet
3. If this..... click on Android SMS trigger
4. Select "New SMS received matches search" and use CoWIN as the search key
5. Then... Choose a service named Webhooks and then select make a web request
6. Paste the url: https://kvdb.io/<kvdb_bucket>/99XXXXXXXX replace 99XXXXXXXX with your phone number and <kvdb_bucket> with your own key that you got in the previous step of KVDB setup.
7. Method is PUT
8. Content Type PlainText
9. Body: Add ingredient and select Text
10. On your android phone, install ifttt app
11. Login 
12. Ensure that the battery saver mode, and all other optimizations are removed. The appshould always run (This is the key for quick response).
    1. **Tip**: If your IFTTT is not triggered when your SMS is received: https://www.androidpolice.com/2020/05/30/how-to-prevent-apps-sleeping-in-the-background-on-android/
       Also a premium account is faster
13. Clone this repository
14. Go to `src` directory and run the script  `cd src && python covid-vaccine-slot-booking.py`
15. On Mac I had to do the following too
    ```bash
    brew install python-tk
    brew install SoX
    ```
18. Run the script, use the steps given below to enter your preferences
19. Hopefully you get the slot
20. Stay healthy and stay safe!


#### IFTTT steps in screenshots:

| |
|:-------------------------:|
| <img alt="Step 1" src="https://user-images.githubusercontent.com/83712877/117159172-b0c4d780-addd-11eb-90f0-ab8438db4c8e.png"> Step 1 |

| | |
|:-------------------------:|:-------------------------:|
|<img alt="Step 2" src="https://user-images.githubusercontent.com/83712877/117159291-c76b2e80-addd-11eb-991a-dc6de4bbb620.png"> Step 2 |<img alt="Step 3" src="https://user-images.githubusercontent.com/83712877/117159444-e669c080-addd-11eb-9b4c-448335b1c781.png"> Step 3 |
|<img alt="Step 4" src="https://user-images.githubusercontent.com/83712877/117159516-f8e3fa00-addd-11eb-832d-fcf92238f823.png"> Step 4 |<img alt="Step 5" src="https://user-images.githubusercontent.com/83712877/117159753-2c268900-adde-11eb-9bb3-4bb54f951683.png"> Step 5 |
|<img alt="Step 6" src="https://user-images.githubusercontent.com/83712877/117159753-2c268900-adde-11eb-9bb3-4bb54f951683.png"> Step 6 |<img alt="Step 7" src="https://user-images.githubusercontent.com/83712877/117159818-38aae180-adde-11eb-96b5-0e779803b4b2.png"> Step 7 |
|<img alt="Step 8" src="https://user-images.githubusercontent.com/83712877/117159863-4496a380-adde-11eb-8874-40cc6f851cf6.png"> Step 8 |<img alt="Step 9" src="https://user-images.githubusercontent.com/83712877/117325821-b5a58c00-aeae-11eb-8156-2ea585a77834.png"> Step 9 |

<br>

### Option 2: CoWIN OTP Retriever
1. Install the [CoWinOTPRetriever Android app](./CoWinOtpRetreiver.apk?raw=true) by enabling installation from unknown sources.
2. Follow this guide to install apps from unknown sources: https://www.verizon.com/support/knowledge-base-222186/
3. Allow the app to run in background so that the app does not stop even if you multi-task or leave the phone idle. (Note that, there still might be some phone model specific settings and optimizations which could stop the app from running in background. Check point number 8)
4. Grant sms access to allow the app to read CoWIN OTP sms.
5. Enter 10 digit mobile number registered on the CoWIN portal. Also enter your personal KVDB bucket value.
6. Switch ON the OTP Listener.
7. If the OTP is successfully sent to the key value store, you will see the status as shown below.
8. Ensure that the battery saver mode, and all other optimizations are removed. The app should always run (This is the key for quick response). 
	Tip: If you don not see a success message on the app when you receive an OTP: https://www.androidpolice.com/2020/05/30/how-to-prevent-apps-sleeping-in-the-background-on-android/
8. Security tip: Make sure to change back your settings to disallow app installation from unknown sources.

#### CoWIN OTP Retriever steps in screenshots
| | | |
|:-------------------------:|:-------------------------:|:-------------------------:|
|<img alt="Step 1" src="https://user-images.githubusercontent.com/3753228/117923351-814c2880-b311-11eb-9008-fbf497271e08.png"> Step 1 |<img alt="Step 2" src="https://user-images.githubusercontent.com/3753228/117923398-9759e900-b311-11eb-9dec-4e003b772f0e.png"> Step 2 |<img alt="Step 3" src="https://user-images.githubusercontent.com/3753228/117923447-a771c880-b311-11eb-92f5-b08903f1b20e.png"> Step 3 |
|<img alt="Step 4" src="https://user-images.githubusercontent.com/3753228/117923482-b9ec0200-b311-11eb-8210-4c1e1b958d6a.png"> Step 4 |<img alt="Step 5" src="https://user-images.githubusercontent.com/3753228/117924614-9e81f680-b313-11eb-8583-bffcadf681f3.png"> Step 5 |<img alt="Step 6" src="https://user-images.githubusercontent.com/3753228/117923509-c40e0080-b311-11eb-9832-805c4676e4a5.png"> Step 6 |
|<img alt="Step 7" src="https://user-images.githubusercontent.com/3753228/117923554-d6883a00-b311-11eb-8ae1-8ea36ffaf35b.png"> Step 7 |<img alt="Step 8" src="https://user-images.githubusercontent.com/3753228/118130348-e17ac180-b41a-11eb-8af9-f9e13d671f07.png"> Step 8 |<img alt="Step 9" src="https://user-images.githubusercontent.com/3753228/117947493-df870480-b32d-11eb-923d-47efa55f9586.png"> Step 9 |
|<img alt="Step 10" src="https://user-images.githubusercontent.com/3753228/117948585-e4988380-b32e-11eb-9837-9abdda21c23e.png"> Step 10 |<img alt="Step 11" src="https://user-images.githubusercontent.com/3753228/117949247-8ae48900-b32f-11eb-8b77-5d98ed07cfc6.png"> Step 11 | |

<br>

## Setup Guide for iOS

### Using Shortcuts app
1. Open the shortcuts app
2. Tap on the + button at the top right
3. Tap on `Create Personal Automation`
3. Select the `Message` option
4. Put `CoWIN` in the Message Contains option & leave everything blank. Tap on Next button
5. Tap on `Add action` and search for the option `Set Variable`. Give the variable name `text` and input as `Shortcut Input`
6. Then add another action and select `URL` and paste the url: https://kvdb.io/<kvdb_bucket>/99XXXXXXXX replace 99XXXXXXXX with your phone number and <kvdb_bucket> with your bucket value from the KVDB setup step
7. Then add another action and select `Get Contents of Url`. Click on show more. Change the method to `PUT`. Request Body to `File` and in the file row tap on `Choose Variable` and select `text` which we defined in Step 6.
8. Click Next and save this automation.
9. Clone this repository
Go to `src` directory and run the script  `cd src && python covid-vaccine-slot-booking.py`
15. On Mac I had to do the following too
     - `brew install python-tk`
     - `brew install SoX`
18. Run the script, enter your phone number. 
19. Now as soon as OTP is recieved you will also get a notification from shortcuts app. Long press it and click on run. It will start OTP auto read process.
20. Use the steps given below to enter your preferences. 
21. Now whenever the script session expires, it will send the notification  described in step 13 and repeat the process to trigger OTP auto read. 
22. It is recommended that you set a different notification tone for this notification to be able to distinguish.
23. Hopefully you get the slot
24. Stay healthy and stay safe!

#### Shortcuts steps in screenshots

| | | |
|:-------------------------:|:-------------------------:|:-------------------------:|
|<img alt="Step 1" src="https://user-images.githubusercontent.com/83958525/117808231-40550500-b27a-11eb-9f58-17c3c9f52dc5.PNG"> Step 1 |<img alt="Step 2" src="https://user-images.githubusercontent.com/83958525/117808359-6a0e2c00-b27a-11eb-975b-cd3cbfda68b0.PNG"> Step 2 |<img alt="Step 3" src="https://user-images.githubusercontent.com/83958525/117808435-7db99280-b27a-11eb-933d-58a8af95dfaa.PNG"> Step 3 |
|<img alt="Step 4" src="https://user-images.githubusercontent.com/83958525/117808441-80b48300-b27a-11eb-92c4-e9e4eb144bef.PNG"> Step 4 |<img alt="Step 5" src="https://user-images.githubusercontent.com/83958525/117808450-8611cd80-b27a-11eb-9caa-b23a5a3c3509.PNG"> Step 5 |<img alt="Step 6" src="https://user-images.githubusercontent.com/83958525/117808480-8dd17200-b27a-11eb-986e-1405dec40e73.PNG"> Step 6 |
|<img alt="Step 7" src="https://user-images.githubusercontent.com/83958525/117808695-d1c47700-b27a-11eb-897a-7a4ef7761889.PNG"> Step 7 |<img alt="Step 8" src="https://user-images.githubusercontent.com/83958525/117808764-e7d23780-b27a-11eb-90b4-bb9859d45379.PNG"> Step 8 |<img alt="Step 9" src="https://user-images.githubusercontent.com/83958525/117808824-01737f00-b27b-11eb-8937-a473107a3fcd.PNG"> Step 9 |
|<img alt="Step 10" src="https://user-images.githubusercontent.com/83958525/117809022-40a1d000-b27b-11eb-86bd-31b5e9669887.PNG"> Step 10 |<img alt="Step 11" src="https://user-images.githubusercontent.com/83958525/117809074-51524600-b27b-11eb-9b2f-82cab9a92f49.jpeg"> Step 11 | |

<br>

## COVID-19 Vaccination Slot Booking Script

This very basic CLI based script can be used to automate covid vaccination slot booking on Co-WIN Platform. 

### Important: 
- POC project. **Use at your own risk**.
- Do NOT use unless all beneficiaries selected are supposed to get the same vaccine and dose. 
- No option to register new user or add beneficiaries. This can be used only after beneficiary has been added through the official app/site
- If you accidentally book a slot, don't worry. You can always login to the official portal and cancel that.
- API Details: https://apisetu.gov.in/public/marketplace/api/cowin/cowinapi-v2
- And finally, I know code quality probably isn't great. Suggestions are welcome.


### Usage:

For the anyone not familiar with Python and using Windows, using the ```covid-vaccine-slot-booking.exe``` executable file would be the easiest way. [Download it from here](https://github.com/bombardier-gif/covid-vaccine-booking/releases/latest). It might trigger an anti-virus alert. That's because I used ```pyinstaller``` to package the python code and it needs a bit more effort to avoid such alerts.

OR

Run the script file as show below by [downloading the source](https://github.com/bombardier-gif/covid-vaccine-booking/releases/latest):

```
python src\covid-vaccine-slot-booking.py
```
If you're on Linux, install the beep package before running the Python script. To install beep, run:
```
sudo apt-get install beep
```
If you already have a bearer token, you can also use:
```
python src\covid-vaccine-slot-booking.py --token=YOUR-TOKEN-HERE
```

### Third-Party Package Dependency:
- ```tabulate``` : For displaying data in tabular format.
- ```requests``` : For making GET and POST requests to the API.
- ```inputimeout``` : For creating an input with timeout.

Install all dependencies by running:
```pip install -r requirements.txt```

<br>

## Steps:
1. Run script:
	```python src\covid-vaccine-slot-booking.py```
2. Select Beneficiaries. Read the important notes. You can select multiple beneficiaries by providing comma-separated index values such as ```1,2```:
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
9. If at any stage your token becomes invalid, the script will make a beep and prompt for ```y``` or ```n```. If you'd like to continue, provide ```y``` and proceed to allow using same mobile number
	```
	Token is INVALID.  
	Try for a new Token? (y/n): y
	Try for OTP with mobile number ███████████? (y/n) : y
	Enter OTP: 888888
	```
11. When a center with more than minimum number of slots is available, the script will make a beep sound - different frequency for different district. It will then display the available options as table:
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
12. Before the next update, you'll have 10 seconds to provide a choice in the format ```centerIndex.slotIndex``` eg: The input```1.4``` will select the vaccination center in second row and its fourth slot.

<br>

## How to run on windows

1. **Step 1** - [Download the source or exe](https://github.com/bombardier-gif/covid-vaccine-booking/releases/latest).
2. **Step 2 -** Go to folder **tests** then **windows exe**.**zip**. Unzip the folder and Now run the program "**captcha_tests.exe**".  If you see a dialog box click on quit, and you will see a Captcha. If this is what happened you are all good to go. 
3. Now come back to main folder unzip "**windows exe.zip**"go to this "**windows exe**" folder 
   Now start the program "**covid-vaccine-slot-booking.exe**", you will not see any error.
4. DO NOT DELETE ANY FOLDER OR FILE. 

<br>

## Using docker

You can also run this script using docker. It's useful in case you don't want to
install all required dependencies manually (python etc.). Follow these steps:

1. Make sure [docker](https://docs.docker.com/get-docker/) is installed on your system.
2. Make sure file 'docker.sh' is executable:
	```chmod +x docker.sh```
3. Now build our docker image and run it:
	```./docker.sh```

**Noe** : Currently this docker image is only tested on MacOS and Linux.

<br>

## Troubleshooting common problems

### Problem 1

   ```
   Can't setFont(Times-Roman) missing the T1 files?
   Originally <class 'TypeError'>: makeT1Font() argument 2 must be str, not None
   ```

   **Solution 1:** Then run the python script directly in the **src** folder after installing the required modules from **requirements.txt.** That solved it for me

   **Solution 2:** If you are running ubantu(tested) or Windows, this problem is due to some font files from package (reportlab) which are included in arch linux but not on Ubuntu. Follow these steps to install reportlab correctly. It can be done after you have installed all the requirements rom txt file.

   1. ```git clone https://github.com/Distrotech/reportlab.git```
   2. ```cd reportlab```
   3. ```python3 setup.py install```

     This will download all the font files. 

   **Solution 3**: Try to perform the test first in **test** folder for captcha first to see if this error still there.

   **Solution 4:** (Recommended) Try to use this Linux executable " **./covid-vaccine-slot-booking**-linux " file directly from terminal it does not require anything to install just like windows exe. **Windows exe is under going testing**

    
### Problem 2

   Regarding beep package - Device not found or beep not found

   **Solution** : Follow these steps for Ubuntu

   1. ```sudo apt-get install beep``` #Install this once
   2. ```sudo modeprobe pcspkr``` #This will solve Device not found error 
   3. Testing beep is simple just type ```beep``` in terminal, this will produce a beep sound from your speakers.

### Problem 3

   SMS is not read automatically

   **Solution**: Make sure the settings shown below are the same on your phone:

| | |
|:-------------------------:|:-------------------------:|
| <img src="https://user-images.githubusercontent.com/83712877/117325821-b5a58c00-aeae-11eb-8156-2ea585a77834.png" alt="image" width="300" /> <br> Using IFTTT: This number must match the number you enter while running the script. |<img src="https://user-images.githubusercontent.com/3753228/117948585-e4988380-b32e-11eb-9837-9abdda21c23e.png" alt="image" width="300" /> <br> CowinOTPRetriever App: Make sure the switch is flipped on. |
   

   
