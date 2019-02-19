
all: cleansedCrashData.csv

clean:
	rm cleansedCrashData.csv

cleansedCrashData.csv: crashData.csv 
	./cleanCrashData.py crashData.csv cleansedCrashData.csv

test:
	pytest test_spellcheck.py

