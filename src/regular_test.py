import re

fo = open("text",'r',encoding='UTF-8')
lines = fo.readlines()
for line in lines: 
	pattern = re.compile('(?<!\d)\d{2,4}\D\d{1,2}\D\d{1,2}(?!\d)')

	#pattern = re.compile(r"^\d{4}(-\d\d){2}")
	pattern2 = re.compile('\d')
	result1 = re.search(pattern, line)

	if result1:
		str_buf = ""

		result2 = re.findall(pattern2, result1.group())
		for m in result2:
			str_buf += m
		print(str_buf)
	
