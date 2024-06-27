import time
import requests
from getpass import getpass
from urllib.parse import quote
from form import fill_form
from login import login

session = requests.Session()

pjxt_url = "https://spoc.buaa.edu.cn/pjxt/"

def get_latest_task():
    task_list_url = pjxt_url + 'personnelEvaluation/listObtainPersonnelEvaluationTasks?pageNum=1&pageSize=1'
    task_response = session.get(task_list_url)
    task_json = task_response.json()
    if task_json['result']['total'] == 0:
        return None
    return (task_json['result']['list'][0]['rwid'], task_json['result']['list'][0]['rwmc'])


def get_questionnaire_list(task_id):
    list_url = pjxt_url + f'evaluationMethodSix/getQuestionnaireListToTask?rwid={task_id}&pageNum=1&pageSize=999'
    list_response = session.get(list_url)
    list_json = list_response.json()
    return list_json['result']


def set_evaluating_method(qinfo):
    confirm_url = pjxt_url + 'evaluationMethodSix/confirmQuestionnairePattern'
    revise_url = pjxt_url + 'evaluationMethodSix/reviseQuestionnairePattern'

    form = {
        'wjid': qinfo['wjid'],
        'msid': 1,
        'rwid': qinfo['rwid']
    }

    if qinfo['msid'] == '1':
        return
    if qinfo['msid'] == '2':
        _response = session.post(revise_url, json=form)
    elif qinfo['msid'] is None:
        _response = session.post(confirm_url, json=form)
    else:
        print(f"Unknown msid {qinfo['msid']} for {qinfo['wjmc']}")
        return


def get_course_list(qid):
    course_list_url = pjxt_url + f'evaluationMethodSix/getRequiredReviewsData?sfyp=0&wjid={qid}&pageNum=1&pageSize=999'
    course_list_response = session.get(course_list_url)
    course_list_json = course_list_response.json()

    if 'result' in course_list_json:
        return course_list_json['result']
    else:
        print(f"Failed to get course list for {qid}")
        return []


def evaluate_single_course(cinfo):
    topic_url = pjxt_url + f'evaluationMethodSix/getQuestionnaireTopic?rwid={quote(cinfo["rwid"])}&wjid={quote(cinfo["wjid"])}&sxz={quote(cinfo["sxz"])}&pjrdm={quote(cinfo["pjrdm"])}&pjrmc={quote(cinfo["pjrmc"])}&bpdm={quote(cinfo["bpdm"])}&bpmc={quote(cinfo["bpmc"])}&kcdm={quote(cinfo["kcdm"])}&kcmc={quote(cinfo["kcmc"])}&rwh={quote(cinfo["rwh"])}'
    topic_response = session.get(topic_url)
    topic_json = topic_response.json()
    evaluate_result = fill_form(topic_json['result'][0])  # Change this line to select evaluation method
    # json.dump(evaluate_result, open('evaluate_result.json', 'w'), indent=4)
    submit_url = pjxt_url + 'evaluationMethodSix/submitSaveEvaluation'
    response = session.post(submit_url, json=evaluate_result)
    if response.json()['msg'] == '成功':
        print(f"Successfully evaluated {cinfo['kcmc']}")
    else:
        print(response.json())
        exit(1)


def auto_evaluate():
    task = get_latest_task()
    if task is None:
        print('No task to evaluate')
        return
    print(f"Evaluating task {task[1]}, press Enter to continue, or Ctrl+C to exit")
    input()
    q_list = get_questionnaire_list(task[0])
    for q in q_list:
        print(f"Evaluating questionnaire {q['wjmc']}")
        set_evaluating_method(q)
        c_list = get_course_list(q['wjid'])
        for c in c_list:
            if c['ypjcs'] == c['xypjcs']:
                print(f"Course {c['kcmc']} has been evaluated, skip")
                continue
            print(f"Evaluating course {c['kcmc']}")
            evaluate_single_course(c)
        time.sleep(1)


def main():
    username = input('Enter username: ')
    password = getpass('Enter password: ')
    print('Logging in...')
    if login(session, pjxt_url + 'cas', username, password):
        print('Login successfully!')
        auto_evaluate()
        input('Evaluation finished! Press any key to exit...')
    else:
        input('Login failed!')


if __name__ == '__main__':
    main()
