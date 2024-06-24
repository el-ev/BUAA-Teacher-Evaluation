# WHAT A HUGE PIECE OF SH*T!
import random
from dataclasses import dataclass

@dataclass
class Option:
    id: str
    content: str
    pts: float

@dataclass
class Question:
    isChoice: bool
    type: str
    id: str
    options: list[Option]


def fill_form(form_info, method='good'):
    # 这是活人能想出来的名字？
    basic_info = form_info['pjxtPjjgPjjgckb'][1]

    question_list = get_question_list(form_info)
    choice_list = [q for q in question_list if q.isChoice]
    other_list = [q for q in question_list if not q.isChoice]
    choice_answer = gen_answer(choice_list, method)
    total_score = int(sum(q.pts for q in choice_answer))

    answer_list = []
    for i in range(len(choice_list)):
        answer_list.append({
            'sjly': '1',  # not sure
            'stlx': choice_list[i].type,
            'wjid': basic_info['wjid'],
            'wjssrwid': basic_info['wjssrwid'],
            'wjstctid': "",
            'wjstid': choice_list[i].id,
            'xxdalist': [
                choice_answer[i].id
            ]
        })

    for i, q in enumerate(other_list):
        answer_list.append({
            'sjly': '1',  # not sure
            'stlx': q.type,
            'wjid': basic_info['wjid'],
            'wjssrwid': basic_info['wjssrwid'],
            'wjstctid': q.options[0].id,
            'wjstid': q.id,
            'xxdalist': [
                ""  # empty string
            ]
        })
    ret = {
        'pjidlist': [],
        'pjjglist': [
            {
                'bprdm': basic_info['bprdm'],
                'bprmc': basic_info['bprmc'],
                'kcdm': basic_info['kcdm'],
                'kcmc': basic_info['kcmc'],
                'pjdf': total_score,
                'pjfs': basic_info['pjfs'],
                'pjid': basic_info['pjid'],
                'pjlx': basic_info['pjlx'],
                'pjmap': form_info['pjmap'],
                'pjrdm': basic_info['pjrdm'],
                'pjrjsdm': basic_info['pjrjsdm'],
                'pjrxm': basic_info['pjrxm'],
                'pjsx': 1,  # Not sure
                'rwh': basic_info['rwh'],
                'stzjid': basic_info['stzjid'],
                'wjid': basic_info['wjid'],
                'wjssrwid': basic_info['wjssrwid'],
                'wtjjy': '',
                'xhgs': basic_info['xhgs'],
                'xnxq': basic_info['xnxq'],
                'sfxxpj': '1', # Not sure, but setting to '2' causes problems
                'sqzt': basic_info['sqzt'],
                'yxfz': basic_info['yxfz'],
                'sdrs': basic_info['sdrs'],
                "zsxz": basic_info['pjrjsdm'],
                'sfnm': '1',  # Anonymous
                'pjxxlist': answer_list
            }
        ],
        'pjzt': '1'  # 2 for save, 1 for submit
    }
    return ret


def get_question_list(form_info):
    ret = []
    for entry in form_info['pjxtWjWjbReturnEntity']['wjzblist'][0]['tklist']:
        q = Question(
            isChoice=entry['tmlx'] == '1',
            type=entry['tmlx'],
            id=entry['tmid'],
            options=[]
        )
        for option in entry['tmxxlist']:
            q.options.append(Option(
                id=option['tmxxid'],
                content=option['xxmc'],
                pts=float(option['xxfz'])
            ))
        q.options.sort(key=lambda x: x.pts, reverse=True)
        ret.append(q)
    return ret


def gen_answer(choice_list, method):
    ret = []
    if method == 'good':
        ret = gen_good_answer(choice_list)
    # the below two methods are not tested
    elif method == 'bad':
        ret = gen_bad_answer(choice_list)
    elif method == 'random':
        ret = gen_random_answer(choice_list)
    else:
        raise ValueError(f"Unknown method {method}")
    return ret


def gen_good_answer(choice_list):
    ret = []
    if len(choice_list) == 1:
        ret.append(choice_list[0].options[0])
    else:
        ret.append(choice_list[0].options[1])
    for q in choice_list[1:]:
        ret.append(q.options[0])
    return ret


def gen_bad_answer(choice_list: list[Question]):
    return dp(choice_list, 60)


def gen_random_answer(choice_list):
    target = random.randint(60, 100)
    return dp(choice_list, target)


def dp(choice_list, threshold):
    max_score = sum(q.options[0].pts for q in choice_list)
    if max_score >= threshold:
        threshold = max_score
    dp_list = [0] * (max_score + 1)
    dp_list[0] = 1
    for q in choice_list:
        for i in range(max_score, -1, -1):
            for option in q.options:
                if i + option.pts <= max_score:
                    dp_list[i + option.pts] = dp_list[i]
    target = threshold
    while dp_list[target] == 0:
        target += 1
    ret = []
    for q in choice_list:
        for option in q.options:
            if target - option.pts >= 0:
                target -= option.pts
                ret.append(option)
                break
    return ret