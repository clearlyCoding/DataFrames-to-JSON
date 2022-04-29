import pandas as pd
import json
import math 
import sys


class _read():
	# 'using pandas to read csv files'
	def __init__ (self, path):
		self.df = pd.read_csv(path)


class course_Diction():
	# 'isolating course data'
	def __init__(self, course_DF):
		self.course_DF = course_DF
		self.course_Diction={}

	def parse(self):

		for course_id, course_name, course_teacher in self.course_DF.values:
			course_id = int(course_id)
			course_name = str(course_name)
			course_teacher = str(course_teacher)

			self.course_Diction.update({course_id: [course_name, course_teacher]})

class student_Diction():
	# 'isolating student values'
	def __init__ (self, student_DF):
		self.student_DF = student_DF
		self.student_Diction = {}

	def parse(self):
		for student_id, student_name in self.student_DF.values:
			student_id = int(student_id)
			student_name = str(student_name)
			self.student_Diction.update({student_id: student_name})

class test_Diction():
	# 'class to isolate test/course id overlapping data'

	def __init__ (self, test_DF):
		self.test_DF = test_DF
		self.test_Diction = {}
		
	def parse(self):
		for test_id, test_course_id, test_weight in self.test_DF.values:
			test_id = int(test_id)
			test_course_id = int(test_course_id)
			test_weight = float(test_weight)
			self.test_Diction.update({test_id: [test_course_id, test_weight]})


class marks_Diction():
	# 'class pulling together marks data and using other classes to pull together overlapping data'
	def __init__ (self, marks_DF,tests_dictionary={}):
		self.marks_DF = marks_DF
		self.marks_Diction = {}
		self.tests_dict = tests_dictionary
	def parse(self):
		for test_id, test_student_id, test_mark in self.marks_DF.values:
			test_student_id = int(test_student_id)
			test_id = int(test_id)
			test_mark = float(test_mark)

			# using the previous classes to pull together courseID studentId and Marks
			if test_id not in self.marks_Diction.keys():
				self.marks_Diction[test_id] = [{"studentID": test_student_id,  
										"courseID": self.tests_dict[test_id][0], 
										"Test Mark": test_mark,
										"Test Weight": self.tests_dict[test_id][1],
										"Student Weighted Mark": round(test_mark*(self.tests_dict[test_id][1]/100),2) #calculating weighted mark here, no use in creating a whole function for it
									}]
			else:
				self.marks_Diction[test_id].append({"studentID": test_student_id,  
										"courseID": self.tests_dict[test_id][0], 
										"Test Mark": test_mark,
										"Test Weight": self.tests_dict[test_id][1],
										"Student Weighted Mark": round(test_mark*(self.tests_dict[test_id][1]/100),2)
										})

	def pullCourses(self, courseID, studentID):
		#function to return specific rows of combined data based off of courseID input and studentID
		returnList=[]
		for key in self.marks_Diction.keys():
			for each_list in self.marks_Diction[key]:
					if each_list['courseID']== courseID and each_list['studentID'] == studentID:
						returnList.append(each_list)


		return returnList

	def checkError(self, courseIDs):
		#checking for weight errors
		weightCheck=0
		for key in self.marks_Diction.keys():
			for i in range(len(self.marks_Diction[key])):
				if self.marks_Diction[key][i]['courseID'] == courseIDs:
					weightCheck +=self.marks_Diction[key][i]['Test Weight']
					break
		if weightCheck!=100:
			return {'error':"Invalid course weights"}
	


class getAverages():
	#gets returns averages and counts
	def __init__ (self, marksDictionary = {}, coursesDictionary ={}, testsDictionary={}, studentDictionary = {}):
		self.student_id_and_averages = {}
		self.student_id_and_totalAverage= {}
		self.marksDictionary = marksDictionary
		self.coursesDictionary = coursesDictionary
		self.courseCount = len(self.coursesDictionary)
		self.testsDictionary = testsDictionary
		self.testCount = len(self.testsDictionary)
		self.studentDictionary = studentDictionary
		self.studentCount = len(self.studentDictionary)

class Generate_JSON():
	#JSON Generating Class
	def __init__ (self, studentAvg, classAvg, coursesDictionary, studentDictionary):
		self.studentAverages = studentAvg
		self.classAvg = classAvg
		self.coursesDictionary = coursesDictionary
		self.studentDictionary = studentDictionary

	def generate_Student (self, studentID):
		student_dictionary = {"id": studentID,
							  "name": self.studentDictionary[studentID],
							  "totalAverage": self.studentAverages[studentID],
							  }
		coursesList=[]
		for classID in self.classAvg[studentID-1].keys():
			if self.classAvg[studentID-1][classID]['testAvg'] >0:
				coursesList.append({"id": classID,
									"name": self.coursesDictionary[classID][0],
									"teacher": self.coursesDictionary[classID][1],
									"courseAverage": round(self.classAvg[studentID-1][classID]['testAvg'],2)
									})
			else:
				pass
		student_dictionary["courses"]=coursesList

		return student_dictionary

#inputs to read from files and assigning classes
COURSES_DATAFRAME = _read(sys.argv[1])
STUDENTS_DATAFRAME = _read(sys.argv[2])
TESTS_DATAFRAME = _read(sys.argv[3])
MARKS_DATAFRAME = _read(sys.argv[4])
WRITETOPATH = sys.argv[5]
courseDiction = course_Diction(COURSES_DATAFRAME.df)
studentDiction = student_Diction(STUDENTS_DATAFRAME.df)
testDiction = test_Diction(TESTS_DATAFRAME.df)
courseDiction.parse()
studentDiction.parse()
testDiction.parse()
marksDiction = marks_Diction(MARKS_DATAFRAME.df, testDiction.test_Diction)
marksDiction.parse()
courseListedAverage=[]
OverallAvg_dict = {}
avg = getAverages(marksDiction.marks_Diction,courseDiction.course_Diction, testDiction.test_Diction,studentDiction.student_Diction)


#getting averages
for each_Count in range(1,avg.studentCount+1):
		courseAverage={}
		OverallAvg = 0
		n=0
		for furtherCount in range(1,avg.courseCount+1):
			storeList = marksDiction.pullCourses(furtherCount, each_Count)
			TestAvg=0
			for eachTest in storeList:
				if eachTest['Student Weighted Mark'] >0:
					TestAvg += eachTest['Student Weighted Mark']
			courseAverage[furtherCount] = {'student ID': each_Count, "testAvg": TestAvg}	
			if TestAvg !=0:
				n+=1
			OverallAvg +=TestAvg
		courseListedAverage.append(courseAverage)
		OverallAvg_dict[each_Count] = round(OverallAvg/n,2)

#Reporting Error checks here
for eachCount in range(1, avg.courseCount+1):
	error_test = marksDiction.checkError(eachCount)
	if error_test!=None:
		break


#creating JSON Output

gen = Generate_JSON(OverallAvg_dict, courseListedAverage, courseDiction.course_Diction, studentDiction.student_Diction)
student_list=[]
JSONRequest = {}
for i in range(1, avg.studentCount+1):
	student_list.append(gen.generate_Student(i))
if error_test == None:
	JSONRequest={'students': student_list}
else:
	JSONRequest =error_test


#writing to file
with open(WRITETOPATH, 'w') as outputfile:
	json.dump(JSONRequest, outputfile, indent=4)

#print(json.dumps(JSONRequest,indent=4))