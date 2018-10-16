#!/usr/bin/env python
# coding: utf-8
# @Author: lapis-hong
# @Date  : 2018/8/10
import sys
import json
import random
import re
from collections import Counter

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


def parse_all_q():
    all_q = {}
    for line in open("all_q_list.csv"):
        q_id, q = line.strip().split(",", 1)
        all_q[q_id] = q
    return all_q


def gen_selected_triple():
    q_dic = parse_all_q()
    positive = []
    negative = []
    with open("origin", "w") as fo:
        for idx, line in enumerate(open("selected_qa_pair.csv")):
            q_id, a_id, vote, a = line.strip().split(",", 3)
            a = a.replace("\t", " ")
            try:
                q = q_dic[q_id].replace("\t", " ")

            except KeyError:
                pass
            if idx % 2 == 0:
                positive.append([q, a])
            else:
                negative.append(a)
        for (q, a_pos), a_neg in zip(positive, negative):
            fo.write("\t".join([q, a_pos, a_neg]) + "\n")


def gen_pred_pair():
    q_dic = parse_all_q()
    with open("pred", "w") as fo:
        for line in open("test_qa.csv"):
            q_id, a_id, vote, a = line.strip().split(",", 3)
            a = a.replace("\t", " ")
            q = q_dic[q_id].replace("\t", " ")
            fo.write("\t".join([q, a]) + "\n")


def cal_acc():
    q_list = []
    for line in open("test_qa.csv"):
        q_id, a_id, vote, a = line.strip().split(",", 3)
        q_list.append(q_id)
    score_list = []
    for line in open("result.txt"):
        score_list.append(float(line.strip()))

    score_dic = {}
    for q_id, score in zip(q_list, score_list):
        if q_id not in score_dic:
            score_dic[q_id] = [score]
        else:
            score_dic[q_id].append(score)
    cnt = 0
    for q_id, scores in score_dic.items():
        if max(scores) == scores[0]:
            cnt += 1
    acc = float(cnt) / len(score_dic)
    return acc






def train_test_split(train_ratio=0.9):
    with open("train", "w") as f1, open("test", "w") as f2:
        for ix, line in enumerate(open("origin")):
            if random.random() < train_ratio:
                f1.writelines(line)
            else:
                f2.writelines(line)


def clean_str(string):
    string = re.sub(r"[^A-Za-z0-9(),!?\'\`]", " ", string)
    string = re.sub(r"\'s", " \'s", string)
    string = re.sub(r"\'ve", " \'ve", string)
    string = re.sub(r"n\'t", " n\'t", string)
    string = re.sub(r"\'re", " \'re", string)
    string = re.sub(r"\'d", " \'d", string)
    string = re.sub(r"\'ll", " \'ll", string)
    string = re.sub(r",", " , ", string)
    string = re.sub(r"!", " ! ", string)
    string = re.sub(r"\(", " \( ", string)
    string = re.sub(r"\)", " \) ", string)
    string = re.sub(r"\?", " \? ", string)
    string = re.sub(r"\s{2,}", " ", string)
    return string.strip().lower()


def build_vocab(min_count=3):
    words = []
    for line in open("origin"):
        line = clean_str(line)
        line = line.strip().split(' ')
        for word in line:
            words.append(word)
    counter = Counter(words)
    word_count = counter.most_common(len(words))  # sort by word freq.
    vocab = ['PAD', 'UNK']
    vocab += [w[0] for w in word_count if w[1] >= min_count]
    with open("vocab", "w") as f:
        for i, word in enumerate(vocab):
            f.write(word + "\n")


if __name__ == '__main__':
    # gen_pair("Data2018/Set1/question.json", "Data2018/Set1/answer.json", "Data2018/Set1/pair")
    # gen_triple("Set1/question.json", "Set1/answer.json", "Set1/triple")
    # post_process("Set1/triple", "Set1/train")
    # gen_pred("Set2/question.json", "Set2/answer.json", "pred")
    # q_dic = parse_all_q()
    # gen_selected_triple()
    # train_test_split()
    # build_vocab(3)
    # gen_pred_pair()
    acc = cal_acc()
    print(acc)







