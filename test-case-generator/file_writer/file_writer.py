import os
import sys
import re

def from_dict(dct):
    def lookup(match):
        key = match.group(1)
        return dct.get(key, f'<{key} not found>')
    return lookup


def write_begin(test_counter):
    # write standard beginning of template into test_cases/qa_tx.py
    f_template = open('template/standard_tx_first.py', 'r')
    f_template_text = f_template.read()
    file_name = "test_cases/qa"+str(test_counter)+"_tx.py"
    f = open(file_name, "w")
    f.write(f_template_text)
    f.close()
    f_template.close()
    # write standard beginning of template into test_cases/qa_rx.py
    file_name = "test_cases/qa"+str(test_counter)+"_rx.py"
    f_template = open('template/standard_rx_first.py', 'r')
    f_template_text = f_template.read()
    f = open(file_name, "w")
    f.write(f_template_text)
    f.close()
    f_template.close()


def write_config(test_counter, source_data, bw, sf, paylen, impl_head, has_crc, cr):
    # write config file for run
    f = open("config", "w")
    f.write(str(test_counter)+"\n")
    f.write(str(source_data)+"\n")
    f.write(str(bw)+"\n")
    f.write(str(sf)+"\n")
    f.write(str(paylen)+"\n")
    f.write(str(impl_head)+"\n")
    f.write(str(has_crc)+"\n")
    f.write(str(cr)+"\n")
    f.close()


def write_template(test_counter, source_data, bw, sf, paylen, impl_head, has_crc, cr):
    file_name_tx = "test_cases/qa"+str(test_counter)+"_tx.py"
    file_name_rx = "test_cases/qa"+str(test_counter)+"_rx.py"
    f_template = open(
        'template/testcase_tx.py', 'r')
    f_template_text = f_template.read()
    subs = {
        "filename": str(test_counter),
        "source_data": str(source_data),
        "bw": str(bw),
        "sf": str(sf),
        "pay_len": str(paylen),
        "impl_head": str(impl_head),
        "has_crc": str(has_crc),
        "cr": str(cr)
    }
    replaced_text = re.sub('@@(.*?)@@', from_dict(subs), f_template_text)

    f = open(file_name_tx, "a")
    f.write(replaced_text)
    f.close()

    f_template = open('template/testcase_rx.py', 'r')
    f_template_text = f_template.read()
    subs = {
        "filename": str(test_counter),
        "source_data": str(source_data),
        "bw": str(bw),
        "sf": str(sf),
        "pay_len": str(paylen),
        "impl_head": str(impl_head),
        "has_crc": str(has_crc),
        "cr": str(cr)
    }
    # replace placeholder text with actual variables
    replaced_text = re.sub('@@(.*?)@@', from_dict(subs), f_template_text)

    f = open(file_name_rx, "a")
    f.write(replaced_text)
    f.close()


def write_end(test_counter):
    file_name_tx = "test_cases/qa"+str(test_counter)+"_tx.py"
    file_name_rx = "test_cases/qa"+str(test_counter)+"_rx.py"
    # write standard last of template into test_cases/qa_tx.py
    f_template = open('template/standard_tx_last.py', 'r')
    f_template_text = f_template.read()
    f = open(file_name_tx, "a")
    f.write(f_template_text)
    f.close()
    f_template.close()
    # write standard last of template into test_cases/qa_rx.py
    f_template = open('template/standard_rx_last.py', 'r')
    f_template_text = f_template.read()
    f = open(file_name_rx, "a")
    f.write(f_template_text)
    f.close()
    f_template.close()
