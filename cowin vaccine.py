#!/usr/bin/env python
# coding: utf-8

# In[21]:


from datetime import datetime
import json
import requests
import time


# In[22]:


def askUserAge():
    print("Enter User's Age: ", end = '')
    userAge = int(input())
    return userAge

def askFeeType():
    print('Enter your choice number for Vaccine Fee:')
    print('1. Free')
    print('2. Paid')
    print('3. ANY')
    feeType = int(input())
    if feeType == 1:
        return 'Free'
    elif feeType == 2:
        return 'Paid'
    else:
        return 'ANY'

def askDesiredVaccine():
    print('Enter your choice number for Vaccine:')
    print('1. Covaxin')
    print('2. Covishield')
    print('3. Sputnik V')
    print('4. ANY')
    desiredVaccine = int(input())
    if desiredVaccine == 1:
        return 'COVAXIN'
    elif desiredVaccine == 2:
        return 'COVISHIELD'
    elif desiredVaccine == 3:
        return 'SPUTNIK V'
    else:
        return 'ANY'

def getDesiredDoseKey():
    print('Enter your choice number for Dose:')
    print('1. Dose 1')
    print('2. Dose 2')
    doseNum = int(input())
    if doseNum == 1:
        return 'available_capacity_dose1'
    else:
        return 'available_capacity_dose2'


# In[23]:


def askSearchType():
    print('Enter your choice number to select Location:')
    print('1. by PIN')
    print('2. by District')
    searchType = int(input())
    if searchType == 1:
        return True
    else:
        return False

def askStateID():
    print('Enter State ID: ')
    statesURL = 'https://cdn-api.co-vin.in/api/v2/admin/location/states'
    statesResponse = requests.get(statesURL)
    if statesResponse.ok:
        statesData = statesResponse.json()
        print('STATE ID', '\t', 'STATE NAME')
        for state in statesData['states']:
            print('{:^8}\t{}'.format(state['state_id'], state['state_name']))
        stateID = input()
        return stateID
    else:
        print('ERROR IN STATES RESPONSE')

def askDistrictID():
    stateID = askStateID()
    print('Enter District ID: ')
    districtsURL = 'https://cdn-api.co-vin.in/api/v2/admin/location/districts/{}'.format(stateID)
    districtsResponse = requests.get(districtsURL)
    if districtsResponse.ok:
        districtsData = districtsResponse.json()
        print('DISTRICT ID', '\t', 'DISTRICT NAME')
        for district in districtsData['districts']:
            print('{:^11}\t{}'.format(district['district_id'], district['district_name']))
        districtID = input()
        return districtID
    else:
        print('ERROR IN DISTRICTS RESPONSE')

def getCalendarURL():
    isSearchByPIN = askSearchType()
    currentDate = datetime.today().strftime('%d-%m-%Y')
    
    if isSearchByPIN:
        print('Please Enter PIN: ', end = '')
        pinCode = input()
        calendarURL = 'https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin?pincode={}&date={}'.format(pinCode, currentDate)
        return calendarURL
    
    else:
        districtID = askDistrictID()
        calendarURL = 'https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id={}&date={}'.format(districtID, currentDate)
        return calendarURL


# In[24]:


def askUserChoices():
    userChoices = {}
    userChoices['userAge'] = askUserAge()
    userChoices['desiredFeeType'] = askFeeType()
    userChoices['desiredVaccine'] = askDesiredVaccine()
    userChoices['desiredDoseKey'] = getDesiredDoseKey()
    userChoices['calendarURL'] = getCalendarURL()
    return userChoices


# In[25]:


def getVaccinationCalendar(calendarURL):
    calendarResponse = requests.get(calendarURL)
    if calendarResponse.ok:
        calendarData = calendarResponse.json()
        return calendarData
    else:
        print('ERROR IN VACCINATION CALENDAR RESPONSE!!!')


# In[26]:


def checkFeeType(centerFeeType, desiredFeeType):
    if desiredFeeType == 'ANY' or centerFeeType == desiredFeeType:
        return True
    else:
        return False

def checkVaccineCapacity(availableCapacity):
    if availableCapacity > 0:
        return True
    else:
        return False

def checkMinAge(minAgeAllowed, userAge):
    if userAge >= minAgeAllowed:
        return True
    else:
        return False

def checkDesiredVaccine(availableVaccine, desiredVaccine):
    if desiredVaccine == 'ANY' or availableVaccine == desiredVaccine:
        return True
    else:
        return False

def checkDesiredDose(availabeDoseCount):
    if availabeDoseCount > 0:
        return True
    else:
        return False


# In[27]:


def searchVaccine(vaccinationCalendar, userChoices):
    if 'centers' in vaccinationCalendar:
        centers = vaccinationCalendar['centers']
        for center in centers:
            isFeeTypeFound = checkFeeType(center['fee_type'], userChoices['desiredFeeType'])
            if isFeeTypeFound:
                sessions = center['sessions']
                for session in sessions:
                    isVaccineCapacityFound = checkVaccineCapacity(session['available_capacity'])
                    if isVaccineCapacityFound:
                        isAgeAllowed = checkMinAge(session['min_age_limit'], userChoices['userAge'])
                        if isAgeAllowed:
                            isDesiredVaccineFound = checkDesiredVaccine(session['vaccine'], userChoices['desiredVaccine'])
                            if isDesiredVaccineFound:
                                isDesiredDoseFound = checkDesiredDose(session[userChoices['desiredDoseKey']])
                                if isDesiredDoseFound:
                                    print('Center: ', center['name'], '\tDate: ', session['date'], '\tAvailability: ', session[userChoices['desiredDoseKey']])
                                    return True
                            else:
                                continue
                        else:
                            continue
                    else:
                        continue
            else:
                continue
        return False
    else:
        print('UNABLE TO FETCH CENTERS!!!')
        return False


# In[28]:


userChoices = askUserChoices()


# In[ ]:


vaccineNotFound = True
attemptNum = 0
while vaccineNotFound:
    attemptNum += 1
    print('Attempt= ', attemptNum, '\tTimestamp= ', datetime.today())
    vaccinationCalendar = getVaccinationCalendar(userChoices['calendarURL'])
    isVaccineFound = searchVaccine(vaccinationCalendar, userChoices)
    if isVaccineFound:
        winsound.Beep(1000, 10000)  # Beep at 1000 Hz for 10 sec
        vaccineNotFound = False
    time.sleep(3)


# In[ ]:




