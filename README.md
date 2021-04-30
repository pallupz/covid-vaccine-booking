# COVID-19 Vaccine Second Dose Slot Booking Script

This very basic script can be used to automate covid vaccination slot booking on Co-WIN Platform. No option to register new user or add beneficiaries.

#### 3rd Party Package Dependency:
- ```tabulate``` : Used for displaying tabular data. For packgae installation, ```pip install tabulate```

#### Usage:
```
python covid-vaccine-slot-booking.py --mobile=9876543210
```
If you already have a bearer token, you can also use:
```
python covid-vaccine-slot-booking.py --token=YOUR-TOKEN-HERE
```

#### Important: 
- POC project. Use on your own risk
- Do NOT use unless all beneficiaries selected are supposed to get the same vaccine and dose. 

#### Steps:
1. Run script:

![image](https://user-images.githubusercontent.com/63504047/116673251-cb9fe200-a9c0-11eb-89a2-721847ec8c2d.png)

2. Select Beneficiaries. Read the important notes. You can select multiple beneficiaries by providing comma-separated index values.:

![image](https://user-images.githubusercontent.com/63504047/116673996-b5465600-a9c1-11eb-9686-ad7a5bb4680c.png)

3. Ensure correct beneficiary is getting selected:

![image](https://user-images.githubusercontent.com/63504047/116674114-ddce5000-a9c1-11eb-8aca-7305a5517a55.png)

4. Select a state and districts. Multiple districts can be selected by providing comma-separated index values
5. 
