# Script to push machine learning results to DSS

import datetime as dt
import subprocess

# method for writing a single record to DSS
def write_DSS_record(dss_file_name, record_name, t, v, units, recType):
	
	bad_data_val = -999999.
	input_file_name = 'tmpDSS_input.txt'
	data_file_name = 'tmpDSS_output.txt'
	stdout_file_name = 'tmpDSS_stdout.txt'

	f = open(data_file_name, 'w')
	fmt = '%d%b%Y  %H%M'
	for _ in range(len(t)):
		if v[_] != bad_data_val:
			vstr = '{0:0.6f}'.format(v[_])
		else:
			vstr = '---'
		line = t[_].strftime(fmt) + '  ' + vstr + '\n'
		f.write(line)
	f.close()

	f = open(input_file_name, 'w')
	f.write(dss_file_name + '\n')
	outStr = 'EV data=' + record_name + ' UNITS=' + units + ' TYPE=' + recType + '\n'
	f.write(outStr)
	f.write('EF [DATE]  [TIME]  [data]\n')
	f.write('EF.M --- \n')
	outStr = 'IMP ' + data_file_name + '\n'
	f.write(outStr)
	f.close()

	cmd_line = "DSSUTL input=" + input_file_name + " >" + stdout_file_name
	stdout = open(stdout_file_name, 'w')
	subprocess.call(cmd_line, stdout=stdout)
	stdout.close()



csv_file_name = 'newdata_results_rf1.csv'
dss_file_name = 'newdata_results_rf1.dss'
dss_time_interval = '1HOUR'  # 15MIN, 1HOUR, 1DAY options
dss_fpart = 'MACHINE LEARNING'  # Typically used for data source
dss_apart = ''  # Typically used for location name
dss_bpart = 'RESERVOIR A'  # Typically also used for location name
dss_units = ' '  # Hardwired to be blank here - can modify to suit needs
start_col = 8


# Read file headers
f = open(csv_file_name, 'r')
line = f.readline()
sline = line.rstrip('\n').split(',')
headers = sline[start_col:]
params = []
for header in headers:
	params.append(header.strip('"'))
nparams = len(params)

# Read data
max_lines = 1000000
t = []
v = []
for _ in range(max_lines):
	line = f.readline()
	if _ % 1000 == 0:
		print('Reading file line ' + str(_))
	if not line:
		break
	sline = line.rstrip('\n').split(',')
	# parse datetime - format 2006-01-01 00:00:00
	ttmp = dt.datetime.strptime(sline[1], '%Y-%m-%d %H:%M:%S')
	t.append(ttmp)
	vtmp = [float((sline[j]).strip('"')) for j in range(start_col, len(sline))]
	v.append(vtmp)
f.close()

# Write to DSS
print('')
for _ in range(nparams):
	print('Writing DSS record for ' + params[_])
	vtmp = [v[j][_] for j in range(len(v))]
	record_name = '/'.join(['', dss_apart, dss_bpart, params[_], '', dss_time_interval, dss_fpart, ''])
	write_DSS_record(dss_file_name, record_name, t, vtmp, dss_units, 'INST-VAL')

print('Complete!')
	
