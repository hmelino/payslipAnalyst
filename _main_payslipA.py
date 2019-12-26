from PyPDF2 import PdfFileReader
import re as r
import passFile
from passFile import password
import os
import datetime
import time
import matplotlib.pyplot as plt

print("Started")
start=time.time()
today=datetime.date.today()
oneYearAgo=today-datetime.timedelta(365)
payslipsArray=[]


def withinOneYear(page_content):
	oneYearAgo=datetime.datetime.today()-datetime.timedelta(365)
	processedDate=r.findall("(\d{2}\D\d{2}\D\d{4})",page_content)[0]
	date=datetime.datetime.strptime(processedDate,"%d/%m/%Y")
	if date > oneYearAgo:
		return date
		
def withinOneYearV2(date):
	today=datetime.datetime.today().date()
	if (today - date.date()).days < 365:
		return True
	return False



def findHourPay(source):
	data=r.findall("Lounge1(\d{1,4}\W\d{2})",source)
	return [float(n) for n in data]
	
def findHolidayPay(source):
	data=r.findall("Holiday Lounge\d(\d{1,4}\W\d{2})",source)
	return [float(n) for n in data]
	
def totalGrossPay(hourPay,grossPay):
	return sum(hourPay,grossPay)
	
	
	
class Payslip:
  def __init__(self,date,weekOne,weekTwo,tax,NI,pension,grossPay,name):
  	self.name=name
  	self.date=date
  	self.weekOne=weekOne
  	self.weekTwo=weekTwo
  	self.tax=tax
  	self.NI=NI
  	self.pension=pension
  	self.grossPay=grossPay

class PayslipWeekClass:
	def __init__(self,tronc,holiday,hour,totalPay):
		self.tronc=tronc
		self.holiday=holiday
		self.hour=hour
		self.totalPay=totalPay
		
def processData(page_content,n,correctDate):
	troncs=r.findall("Troncs Lounge\d(\d{1,3}\W\d{2})",page_content)
	hours=r.findall("Hour Lounge(\d{1,3}\W\d{2,4})\d\W",page_content)[0]
	holidayFirstWeek=r.findall("Holiday Lounge(\d)(\d{2}\W\d{2})(\d{2,3}\W\d{2})Hour",page_content)
	holidaySecondWeek=r.findall("Holiday Lounge(\d)(\d{2}\W\d{2})(\d{2,3}\W\d{2})Deductions",page_content)
	holidayFirstWeekV2=r.findall("Holiday Lounge(\d)(\d{2}\W\d{2})(\d{2,3}\W\d{2})Holiday",page_content)
	if not holidayFirstWeek:
		holidayFirstWeek=[0]*3
	else:holidayFirstWeek=holidayFirstWeek[0]
	if not holidaySecondWeek:
		holidaySecondWeek=[0]*3
	else:
		holidaySecondWeek=holidaySecondWeek[0]

	hoursPay=r.findall("\W\d{2}(\d{1,4}\W\d{2})Hour Lounge",page_content)
	#print(hoursPay)
	if len(hoursPay)==1:
			
		hoursPay.append(0)
	tax, NI, pension = r.findall("Tax€(\d{1,4}\W\d{2})€NI€(\d{1,3}\W\d{2})€D and D Peoples Pension .{3}€(\d{1,3}\W\d{2})",page_content)[0]
	weekOne=PayslipWeekClass(float(troncs[0]),float(holidayFirstWeek[2]),hours[0],float(hoursPay[0]))
	weekTwo=PayslipWeekClass(float(troncs[1]),float(holidaySecondWeek[2]),hours[1],float(hoursPay[1]))
		
	biweeklyPayslip=Payslip(correctDate,weekOne,weekTwo,float(tax),float(NI),float(pension),(weekOne.totalPay+weekOne.tronc+weekTwo.totalPay+weekTwo.tronc+weekOne.holiday+weekTwo.holiday),n)
	return biweeklyPayslip
	

def loadAllFiles():
	directory = os.fsencode("Payslips/")
	arrayOfFiles=[]
	for file in os.listdir(directory):
		filename = os.fsdecode(file)
		if filename.endswith(".pdf"):
			l=os.path.join(filename)
			arrayOfFiles.append(l)
	return arrayOfFiles


def filtratePayslips(listOfPayslips):
	payslipsArray=[]
	for n in listOfPayslips:
		m=open("Payslips/"+str(n),"rb")
		pdf=PdfFileReader(m)
		pdf.decrypt(password)
		pageObj = pdf.getPage(0)
		page_content = pageObj.extractText()
		correctDate=withinOneYear(page_content)
		if correctDate:
			payslipsArray.append(processData(page_content,n,correctDate))
	return sorted(payslipsArray,key=lambda x: x.date)
	

class Total():
	def __init__(self,Tax,NI,Paid,Pension,Holiday,Gross):
		self.Tax=Tax
		self.NI=NI
		self.Paid=Paid
		self.Pension=Pension
		self.Holiday=Holiday
		self.Gross=Gross




loadedFiles=loadAllFiles()
howManyPayslips=len(loadedFiles)
payslips=filtratePayslips(loadedFiles)

total=Total(0,0,0,0,0,0)
total.Tax=sum([f.tax for f in payslips])
total.NI=sum([f.NI for f in payslips])

payslipValues=[f.grossPay for f in payslips]
totalPaid=sum(payslipValues)
totalPensionPaid=sum([f.pension for f in payslips])
totalHoliday=sum([f.weekOne.holiday + f.weekTwo.holiday for f in payslips])
payslipDates=[f.date.date() for f in payslips]
totalGrossPay=totalPaid+total.NI+totalPensionPaid+total.Tax
plt.plot([f.tax for f in payslips])
plt.plot(payslipValues)
plt.axhline(sum(payslipValues)/
len(payslipValues))
plt.grid()
print(f"Total Net pay is £{round(sum(payslipValues),2)}")
print(f"Average pay is £{round(sum(payslipValues)/len(payslipValues),2)}")


plt.show()
finish=time.time()
print(finish-start)
o=sorted(payslipsArray,key=lambda nunu : nunu.date)
	
