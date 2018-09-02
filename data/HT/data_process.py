#!/usr/bin/env python
# coding: utf-8
# @Author: lapis-hong
# @Date  : 2018/8/10
import sys
import json
import random

reload(sys)
sys.setdefaultencoding("utf-8")


def parse_data(filename):
    with open(filename) as f:
        return json.load(f)


def gen_pair(question_file, answer_file, out_file):

    answers = parse_data(answer_file)
    answer_dic = {a["related_id"]: a["answer_content"] for a in answers}

    questions = parse_data(question_file)
    question_dic = {q["question_id"]: q["question_content"] for q in questions}

    with open(out_file, 'w') as fo:
        for q_id, q in question_dic.items():
            if q_id in answer_dic:
                fo.write('\t'.join([q, answer_dic[q_id]])+'\n')


def gen_triple(question_file, answer_file, out_file):

    answers = parse_data(answer_file)
    answer_dic = {a["related_id"]: a["answer_content"] for a in answers}

    questions = parse_data(question_file)
    question_dic = {q["question_id"]: q["question_content"] for q in questions}

    with open(out_file, 'w') as fo:
        for q_id, q in question_dic.items():
            if q_id in answer_dic:
                a_pos = answer_dic[q_id]
                while True:
                    q_neg = random.choice(answer_dic.keys())
                    if q_neg != q_id:
                        break
                a_neg = answer_dic[q_neg]
                if q and a_pos and a_neg:
                    fo.write('\t'.join([q, a_pos, a_neg])+'\n')


def gen_pred(question_file, answer_file, outfile):
    with open(outfile, "w") as fo:
        answers = parse_data(answer_file)
        answer_dic = {}
        for a in answers:
            if a["related_id"] not in answer_dic:
                answer_dic[a["related_id"]] = [(a["answer_content"], a["answer_voted"])]
            else:
                answer_dic[a["related_id"]].append((a["answer_content"], a["answer_voted"]))
        questions = parse_data(question_file)
        question_dic = {q["question_id"]: q["question_content"] for q in questions}
        for q_id, q in question_dic.items():
            q = q.replace("\n", "")
            ans = answer_dic[q_id]
            ans = sorted(ans, key=lambda v: -int(v[1]))
            for a, v in ans:
                a = a.replace("\n", "")
                if q and a:
                    fo.write("\t".join([q, a])+'\n')


def post_process(infile, outfile):
    with open(outfile, 'w') as fo:
        for line in open(infile):
            line = line.strip().split('\t')
            if len(line) == 3:
                fo.write('\t'.join(line) + '\n')


if __name__ == '__main__':
    # gen_pair("Data2018/Set1/question.json", "Data2018/Set1/answer.json", "Data2018/Set1/pair")
    # gen_triple("Set1/question.json", "Set1/answer.json", "Set1/triple")
    # post_process("Set1/triple", "Set1/train")
    gen_pred("Set2/question.json", "Set2/answer.json", "pred")







