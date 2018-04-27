import os
import sys
from shutil import copyfile
from shutil import rmtree

home_path = os.path.expanduser("~")
apk_output_folder = home_path + "/KKBOX/kkbox_android/KKBOX/build/outputs/apk"
spoon_folder = home_path + "/Desktop/important/spoonHelper"
output_folder = spoon_folder + "/output"
open_report_cmd = "open " + output_folder + "/result1/result.html"
deviceID = "emulator-5554"


def execute_test(parameters=None):

    parameter_dict = get_parameter(parameters)
    spoon_cmd = get_spoon_cmd(parameter_dict)

    delete_result_folder()

    freq = int(parameter_dict.get('freq'))
    run_test(freq, spoon_cmd)

    generate_report()

    open_report(parameter_dict)

    os.system("adb -s {} shell rm -rf /mnt/sdcard/app_spoon-screenshots/*".format(deviceID))


def open_report(parameter):
    if parameter.get("notify").lower() == "true":
        os.system(open_report_cmd)


def delete_result_folder():
    _result_folders = [os.path.join(output_folder, folder) for folder in os.listdir(output_folder) if
                       os.path.isdir(os.path.join(output_folder, folder))]

    for folder in _result_folders:
        rmtree(folder)


def generate_report():
    # all result gather in the first one
    _result_folders = [folder for folder in os.listdir(output_folder) if
                       os.path.isdir(os.path.join(output_folder, folder))]

    _report = os.path.join(output_folder, _result_folders[0], "result.html")

    with open(_report, 'w') as result_file:
        for idx, folder in enumerate(_result_folders):
            individual_report = os.path.join(output_folder, folder, "index.html")
            copyfile(individual_report, individual_report.replace("index", "index_backup"))
            with open(individual_report) as html_file:
                html_content = html_file.read()
                if idx >= 1:
                    html_content = html_content.replace("href=\"device", "href=\"../" + folder + "/device")

                result_file.write("<br>\n" + html_content)


def get_parameter(parameters):
    """
    Parsing the arguments from command line and transform to a dictionary
    :param parameters: Arguments in list type
    :return: Dictionary have arguments
    """
    parameter_dict = {'freq': 1, 'notify': "true"}

    if parameters:
        for parameter in parameters:
            key, value = parameter.split("=")
            parameter_dict[key] = value

    return parameter_dict


def run_test(_freq, cmd):
    """
    Run Spoon command and according to frequency to generate different folder.
    ex: result1, result2, result3 output folder
    """
    for count in range(_freq):
        os.system(cmd.replace("result", "result" + str(count + 1)))


def get_spoon_cmd(parameter_dict):
    """
    According to the input parameters to adjust the content of command.
    :param parameter_dict: The dictionary of parameter
    :return: Command in str format
    """
    class_name_parameter = " --e class=com.kkbox.tests.e2e."
    # class_name_parameter = " --e class=com.kkbox.tests.e2e.cucumber.feature."
    # class_name_parameter = " --e package=com.kkbox.tests.e2e."
    test_case_size = " --size "
    spoon_cmd = "java -jar {0}/spoon-runner-1.7.1-jar-with-dependencies.jar \
             --output {1}/result \
             --grant-all \
             --no-animations \
             --apk {2}/KKBOX-play-debug.apk \
             --test-apk {2}/KKBOX-play-debug-androidTest.apk".format(spoon_folder, output_folder, apk_output_folder)

    if 'class' in parameter_dict:
        class_name_parameter += parameter_dict.get('class')
        spoon_cmd += class_name_parameter

    if 'size' in parameter_dict:
        test_case_size += parameter_dict.get('size')
        spoon_cmd += test_case_size

    return spoon_cmd


if __name__ == "__main__":
    execute_test(sys.argv[1:]) if len(sys.argv) > 1 else execute_test()
