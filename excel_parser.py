import datetime
import time
import sys

COMMA = ','
NONE_USE_LINE_NUMBER = 5
ID_INDEX = 0
TIME_INDEX = 1
STEP_NUMBER_INDEX = 5
STEP_REPEAT_INDEX = 6
VOLT_INDEX = 8
CURRENCY_INDEX = 9

def calculate_v(volt):
    return volt

def calculate_c(currency, ratio):
    ratio = float(ratio)
    return str(float(currency) * ratio)

def time_to_seconds(line):
    time_string = line.strip().split(COMMA)[TIME_INDEX]
    current_time = time.strptime(time_string.strip().split('.')[0],'%H:%M:%S')
    seconds_time = datetime.timedelta(hours=current_time.tm_hour, minutes=current_time.tm_min, seconds=current_time.tm_sec).total_seconds()
    return seconds_time

def line_mapper(line, currency_ratio):
    line = line.strip().split(COMMA)
    step_number = line[STEP_NUMBER_INDEX]
    step_repeat = line[STEP_REPEAT_INDEX]
    volt = calculate_v(line[VOLT_INDEX])
    currency = calculate_c(line[CURRENCY_INDEX], currency_ratio)
    key = (step_number, step_repeat)
    value = (volt, currency)
    return key, value

def read_excel(file_name, currency_ratio):
    excel_dict = dict()
    with open(file_name) as input_data:
        data_lines = input_data.readlines()
        data_lines = data_lines[NONE_USE_LINE_NUMBER:]
        previous_repeat = None
        previous_key = None
        current_repeat_start_time = "00:00:01,0000"
        current_results = list()
        for line in data_lines:
            k, v = line_mapper(line, currency_ratio)
            current_repeat = k[1]
            current_time_in_seconds = time_to_seconds(line)
            # there is a new repeat, current_time_in_seconds should be 00:00:01
            # otherwise should be the diff with first time plus 1 seconds
            if current_repeat != previous_repeat:
                current_repeat_start_time = current_time_in_seconds
                previous_repeat = current_repeat
            current_time_in_seconds = current_time_in_seconds - current_repeat_start_time + 1.0
            v = ["'" + str(current_time_in_seconds), v[0], v[1]]

            # id current k is different with previous k, it means we should add this pair-v to dict otherwise we just add
            # current v to list
            if k != previous_key:
                if previous_key is not None:
                    excel_dict[previous_key] = current_results
                    current_results = list()
                previous_key = k
            current_results.append(v)
        excel_dict[previous_key] = current_results

    return excel_dict

def retrieve_by_step(file_name, step_infos):
    excel_dict = read_excel(file_name, step_infos[0][2])
    for info in step_infos:
        step_number = info[0]
        step_repeat = info[1]
        new_file_name = file_name.split('.')[0] + '_processed_by_step_' + "_".join(info) + ".csv"
        current_data = excel_dict[(step_number, step_repeat)]
        title_voltage = "voltage_of_" + str(step_number) + "_" + str(step_repeat)
        title_currency = "currency_of_" + str(step_number) + "_" + str(step_repeat)
        title_time= "time_of_" + str(step_number) + "_" + str(step_repeat)
        data = list()
        data.append([title_time, title_voltage, title_currency])
        data.extend(current_data)
        w = open(new_file_name, "wb")
        for item in data:
            w.write(",".join(item))
            w.write("\n")
        w.close()

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i+n]

if __name__ == "__main__":
    arguments = sys.argv[1: ]
    print arguments
    if len(arguments) % 3 != 0:
        print "error number of arguments"
        exit(1)
    for retrieve_request in chunks(arguments, 3):
        file_name = retrieve_request[0]
        step_number = retrieve_request[1]
        step_repeat = retrieve_request[2]
        retrieve_by_step(file_name, [(step_number, step_repeat)])
