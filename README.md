# Bombardier COVID-19 Vaccination Slot Booking Script
This is a fork over the neat https://github.com/pallupz/covid-vaccine-booking Thanks for creating a playground for me to build on.

What this repository does:
1. Automates OTP read from the SMS (Android only) after the token expires
2. Randomly chooses one of the available slots instea of waiting for input from the user
3. Reduces the polling wait to optimize on the polling frequency (hence the name bombardier)
![image](https://user-images.githubusercontent.com/83712877/117170462-ac052100-ade7-11eb-8f20-8a0cc3bde79b.png)


How it works:
1. https://ifttt.com/ is used to create a SMS trigger. The trigger happens when the OTP SMS is received
2. The trigger sends the text of the SMS to a REST service, I have used a free service which needs 0 setup for a shared storage


**Parallely**
1. The script runs continuously to poll (same logic as the original repository)
2. Whenever th OTP expires, an OTP is requested
3. When the OTP SMS is received on the Android, phone, the above logic triggers to store the OTP SMS in the shared storage
4. The script polls the shared storage to get the OTP
5. Once the OTP is received, the polling resumes
6. If a free slot is found, rather than waiting for an input, it randomly chooses a slot and attempts to book


**Steps to setup**
1. Create a shared storage URL at https://extendsclass.com/json-storage.html (Type something random and click on Savebin and note the URL generated which will be of the type https://json.extendsclass.com/bin/1232323132)
2. Create an account in ifttt.com (A premium paid account is recommended for a quicker response)
3.     Create a new applet
4.     If this..... click on Android SMS trigger
5.     Select "New SMS received matches search" and use CoWIN as the search key
6.     Then... Choose a service named Webhooks and then select make a web request
7.         Paste the url you created in step 1 above
8.         Method is PUT
9.         Content Type PlainText
10.         Body: Add ingredient and select Text
11. On your android phone, install ifttt app
12.     Login 
13.     Ensure that the battery saver mode, and all other optimizations are removed. The appshould always run (This is the key for quick response). 
	Tip: If your IFTTT is not triggered when your SMS is received: https://www.androidpolice.com/2020/05/30/how-to-prevent-apps-sleeping-in-the-background-on-android/
	Also a premium account is faster
14. Clone this repository
15. 	Search for extendsclass url and replace with the one you created
16. 	Search for your_mobile_number and replace with your mobile number
17. Run the script, use the steps given below to enter your preferences
18. Hopefully you get the slot
19. Stay healthy and stay safe!

Tips: I used this command to run the script as it was giving me Syntax error:_ python3 src/covid-vaccine-slot-booking.py_
Also I used this command to install the dependencies _python3 pip install -r requirements.txt_


**Same steps in screenshots:**
![image](https://user-images.githubusercontent.com/83712877/117158837-67748800-addd-11eb-8880-4d26ef68fddf.png)
![image](https://user-images.githubusercontent.com/83712877/117159030-90951880-addd-11eb-8fd3-f4c6242d03a5.png)
![image](https://user-images.githubusercontent.com/83712877/117159172-b0c4d780-addd-11eb-90f0-ab8438db4c8e.png)
![image](https://user-images.githubusercontent.com/83712877/117159291-c76b2e80-addd-11eb-991a-dc6de4bbb620.png)
![image](https://user-images.githubusercontent.com/83712877/117159444-e669c080-addd-11eb-9b4c-448335b1c781.png)
![image](https://user-images.githubusercontent.com/83712877/117159516-f8e3fa00-addd-11eb-832d-fcf92238f823.png)
![image](https://user-images.githubusercontent.com/83712877/117159663-17e28c00-adde-11eb-9a5f-4faf39430279.png)
![image](https://user-images.githubusercontent.com/83712877/117159753-2c268900-adde-11eb-9bb3-4bb54f951683.png)
![image](https://user-images.githubusercontent.com/83712877/117159818-38aae180-adde-11eb-96b5-0e779803b4b2.png)
![image](https://user-images.githubusercontent.com/83712877/117159863-4496a380-adde-11eb-8874-40cc6f851cf6.png)
![image](https://user-images.githubusercontent.com/83712877/117160157-832c5e00-adde-11eb-8ca4-7bad71abde08.png)

![image](https://user-images.githubusercontent.com/83712877/117160850-16fe2a00-addf-11eb-9e0a-3f5aa4679208.png)
![image](https://user-images.githubusercontent.com/83712877/117160946-2e3d1780-addf-11eb-8f27-2477ac73d087.png)


# COVID-19 Vaccination Slot Booking Script

This very basic CLI based script can be used to automate covid vaccination slot booking on Co-WIN Platform. 

### Important: 
- POC project. **Use at your own risk**.
- Do NOT use unless all beneficiaries selected are supposed to get the same vaccine and dose. 
- No option to register new user or add beneficiaries. This can be used only after beneficiary has been added through the official app/site
- If you accidentally book a slot, don't worry. You can always login to the official portal and cancel that.
- API Details: https://apisetu.gov.in/public/marketplace/api/cowin/cowinapi-v2
- And finally, I know code quality probably isn't great. Suggestions are welcome.


### Usage:

For the anyone not familiar with Python and using Windows, using the ```covid-vaccine-slot-booking.exe``` executable file would be the easiest way. It might trigger an anti-virus alert. That's because I used ```pyinstaller``` to package the python code and it needs a bit more effort to avoid such alerts.

OR

Run the script file as show below:

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
```
pip install -r requirements.txt
```

### Steps:
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
8. Script will now start to monitor slots in these districts every 15 seconds.
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
