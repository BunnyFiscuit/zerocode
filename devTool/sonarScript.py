import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pprint import pprint
import time
from pygit2 import Repository
import os
import pathlib
import sys

def postToSpreadsheet(git_username, git_repo_name, parsed_metrics):
    try:
        # Google spreadsheet API
        scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]


        creds = ServiceAccountCredentials.from_json_keyfile_name("devTool/cred.json", scope)

        client = gspread.authorize(creds)

        sheet = client.open("SonarQube Dev tool").sheet1  # Open the spreadhseet

        data = sheet.get_all_records()  # Get a list of all records

        formated_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

        insertRow = [formated_time, git_username, git_repo_name, parsed_metrics[0], parsed_metrics[1], parsed_metrics[2]]

        try:
            sheet.append_row(insertRow, table_range="A1")
        except:
            raise IOError('Could not add the row to the google spreadsheet')

        print('Successfully upploaded metrics to the spreadsheet')
    except:
        print("Could not post data to the spreadsheet")


def find_git_repo(path, last=None):
    path = pathlib.Path(path).absolute()

    if path == last:
        return None
    if (path / '.git').is_dir():
        return path

    return find_git_repo(path.parent, last=path)


def start_sonarqube_scanner():
    try:
        print("Running sonarqube scanner...")
        SONARSCANNER_PATH = ""
        if os.name.lower() in ["darwin", "posix"]: # mac
            SONARSCANNER_PATH = "/usr/local/opt/sonar-scanner/bin/sonar-scanner"
        else: # os.name == "nt" Windows
            SONARSCANNER_PATH = "X:\\_Work\\Software\\sonar-scanner\\sonar-scanner-4.5.0.2216-windows\\bin\\sonar-scanner.bat"
        os.system("sonar-scanner.bat")
    except Exception as e:
        print("Could not run sonar scanner.")
        raise(e)


def load_metrics_sonarqube(component_name):

    url = f"http://localhost:9000/api/measures/component?component={component_name}&metricKeys=new_coverage,coverage,new_technical_debt,new_critical_violations,new_major_violations"
    token="cf9d753738caf6262a91893ba5c8ffd25ee4df20"
    try:
        session = requests.Session()
        session.auth = token, ''
        call = getattr(session, 'get')
        res = call(url)
        if res.status_code != 200:
            raise Exception('GET /tasks/ {}'.format(res.status_code))
        metrics = res.json()['component']['measures']
        return metrics
    except Exception as e:
        raise e


def parse_metrics(metrics):
    for metric in metrics:
        if metric['metric']=='new_technical_debt':
            new_technical_debt = metric['period']['value']
        elif metric['metric']=='new_critical_violations':
            new_critical_violations = metric['period']['value']
        elif metric['metric']=='new_major_violations':
            new_major_violations = metric['period']['value']

    parsed_metrics=[new_technical_debt, new_critical_violations, new_major_violations]
    return parsed_metrics


def print_metrics(metrics):
    print('new_technical_debt: ' + metrics[0])
    print('new_critical_violations: ' + metrics[1])
    print('new_major_violations: ' + metrics[2])


def pre_commit_sonarqube():
    try:
        start_sonarqube_scanner()
        sonarqube_metrics = load_metrics_sonarqube("zerocode")
        # parse metrics from json format
        parsed_metrics = parse_metrics(sonarqube_metrics)
        # print metrics
        print_metrics(parsed_metrics)

    except Exception as e:
        print("Commit aborted. Error in pre-commit. See details below.")
        print("Reason", e)
        exit()


def pre_push_sonarqube():
    try:
        # get git details
        git_username = os.popen('git config user.name').read()
        git_repo_path = find_git_repo('.')
        # print(str(git_repo_path))
        if git_repo_path is not None:
            git_repo = Repository(str(git_repo_path))
        git_repo_name = git_repo.head.shorthand

        sonarqube_metrics = load_metrics_sonarqube("zerocode")
        # parse metrics from json format
        parsed_metrics = parse_metrics(sonarqube_metrics)

        postToSpreadsheet(git_username, git_repo_name, parsed_metrics)
    except Exception as e:
        print("Push aborted. Error in pre-push. See details below.")
        sys.exit() # .exit(f"Reason: {e}")


def pre_pull_sonarqube():
    try:
        start_sonarqube_scanner()
    except Exception as e:
        print("Pull aborted. Error in pre-pull. See details below.")
        sys.exit() #.exit(f"Reason: {e}")
