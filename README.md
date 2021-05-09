# COVID-19 Vaccination Slot Booking Script
## Update:
### **We are getting all kinds of attention now - which I do not want to handle. So there won't be any additional commits to this project. It has been put on indefinite hold.**



### Important: 
- This is a proof of concept project. I do NOT endorse or condone, in any shape or form, automating any monitoring/booking tasks. **Use at your own risk.**
- This CANNOT book slots automatically. It doesn't skip any of the steps that a normal user would have to take on the official portal. You will still have to enter the OTP and Captcha.
- Do NOT use unless all the beneficiaries selected are supposed to get the same vaccine and dose. 
- There is no option to register new mobile or add beneficiaries. This can be used only after beneficiary has been added through the official app/site.
- API Details (read the first paragraph at least): https://apisetu.gov.in/public/marketplace/api/cowin/cowin-public-v2
- BMC Link: https://www.buymeacoffee.com/pallupz
- And finally, I know code quality isn't great. Suggestions are welcome.

### Noteworthy Forks
- https://github.com/bombardier-gif/covid-vaccine-booking : I haven't tried this personally but, it looks like a promising, completely automated solution that would require a bit more setting up.

### Usage:

For the anyone not familiar with Python and using Windows, using the ```covid-vaccine-slot-booking.exe``` executable file (EDIT: EXE is not working at the moment due to unresolved errors) would be the easiest way. It might trigger an anti-virus alert. That's because I used ```pyinstaller``` to package the python code and it needs a bit more effort to avoid such alerts.

OR

Use **Python 3.7** and install all the dependencies with:
```
pip install -r requirements.txt
```
Then, run the script file as show below:
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
