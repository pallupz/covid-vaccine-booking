# covid-vaccine-booking

This very basic script can be used to automate covid vaccine second dose slot booking on Co-WIN Platform. No option to register new user or add beneficiaries .

### Usage:
```
python covid-vaccine-slot-booking.py --mobile=9876543210
```
If you already have a bearer token, you can also use:
```
python covid-vaccine-slot-booking.py --token=YOUR-TOKEN-HERE
```

#### Important: 
- Do NOT use unless all beneficiaries selected are supposed to get the same vaccine. 
- Beware of district, and a lot of other, hardcoding. Too lazy to fix.
