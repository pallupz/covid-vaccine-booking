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
    - All donations, as they materialize, will be split equally between COVID Kerala CMDRF and a centre for cerebral palsied children with multiple handicaps.
- Discord ID for DMs: pallupz#5726
- And finally, I know code quality isn't great. Suggestions are welcome.

### Noteworthy Forks
- https://github.com/bombardier-gif/covid-vaccine-booking : I haven't tried this personally but, it looks like a promising, bit more automated solution that would require some more setting up.

### Usage:

EXE file does not work anymore but the **Python 3.7** code does. If you don't already have Python and do not know how to set it up, instructions are at the bottom. It's not complicated at all and takes literally 5 minutes. Please do that and come back here.

Download this code as zip, and extract it to some folder like ```C:\temp\covid-vaccine-booking```. Going by this structure, the py files should be in ```C:\temp\covid-vaccine-booking\src```. 

Open command prompt and run ```cd C:\temp\covid-vaccine-booking```

Install all the dependencies with the below. This is a one-time activity (for anyone not familiar with Python)
```
pip install -r requirements.txt
```

If you're on Windows, install dependencies with below command
```
python3 -m pip install -r requirements.txt
```

If you're on Linux, install the beep package before running the Python script. To install, run:
```
sudo apt-get install beep
```
If you're on MacOS, install the SoX ([Sound eXchange](http://sox.sourceforge.net/ "Sound eXchange")) before running the Python script. To install, run:
```
brew install sox
```

Finally, run the script file as shown below:
```
python src\covid-vaccine-slot-booking.py
```

If you already have a bearer token, you can also use:
```
python src\covid-vaccine-slot-booking.py --token=YOUR-TOKEN-HERE
```

### Python 3.7.3 Installation in Windows
- Check if Python is already installed by opening command prompt and running ```python --version```.
- If the above command returns ```Python <some-version-number>``` you're probably good - provided version number is above 3.6
- If Python's not installed, command would say something like: ```'python' is not recognized as an internal or external command, operable program or batch file.```
- If so, download the installer from: https://www.python.org/ftp/python/3.7.3/python-3.7.3-amd64.exe
- Run that. In the first screen of installer, there will be an option at the bottom to "Add Python 3.7 to Path". Make sure to select it.
- Open command prompt and run ```python --version```. If everything went well it should say ```Python 3.7.3```
- In case of problem for python is not recognied problem. Set system PATH for python.
- You're all set! 

