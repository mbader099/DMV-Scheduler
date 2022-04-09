from json import JSONEncoder

import requests


class ServiceType:
    def __init__(self, svcId, displayName, locationsUrl):
        self.svcId = svcId
        self.displayName = displayName
        self.locationsUrl = locationsUrl
        self.locationsJson = []

    def fetchLocationsJson(self):
        self.locationsJson = requests.get(url=self.locationsUrl).json().get('locations')


svc_types = [
    ServiceType("all_transactions", "All Transactions", "https://www.dmv.virginia.gov/onlineservices/transactions.json"),
    ServiceType("connect", "DMV Connect Transactions", "https://www.dmv.virginia.gov/onlineservices/connects.json"),
    ServiceType("ezpass", "EZ-Pass Transactions", "https://www.dmv.virginia.gov/onlineservices/ezpass.json"),
    ServiceType("knowl_test", "Learners Permit / Knowledge Test", "https://www.dmv.virginia.gov/onlineservices/learnersKnowledgeTesting.json"),
    ServiceType("moto_skills", "Motorcycle Skills Test", "https://www.dmv.virginia.gov/onlineservices/motorcycleTests.json"),
    ServiceType("dl_skills", "Driver's License Skills Test", "https://www.dmv.virginia.gov/onlineservices/driverTests.json")
]
