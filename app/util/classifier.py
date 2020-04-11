"""
classifier.py - Classify text elements to JSON doc

Copyright (c) 2020 by Thomas J. Daley, J.D.
"""
import json
import re


class Classifier(object):
    def classify_doc(self, text_content: str, code: str) -> dict:
        lines = text_content.split('\n')
        doc = []
        context = {}
        context['code'] = code
        context['code_name'] = None
        context['title'] = None
        context['subtitle'] = None
        context['chapter'] = None
        context['subchapter'] = None
        context['section_number'] = None
        context['section_name'] = None
        context['text'] = None
        context['future_effective_date'] = None
        context['save_section'] = False
        prior_context = context.copy()

        for line in lines:
            line = clean(line)
            if not line:
                continue

            context = classify(line, context)

            if prior_context['section_number'] != context['section_number'] and prior_context['text']:
                del prior_context['save_section']
                doc.append(prior_context)

            prior_context = context.copy()
        return doc


def extract_code_name(line: str) -> str:
    match = re.findall(r'^([A-Z\-\s]+) CODE', line)
    if match:
        return match[0]
    return None


def extract_title_name(line: str) -> str:
    match = re.findall(r'^TITLE ([A-Z0-9\-\.\s]+)', line)
    if match:
        return match[0]
    return None


def extract_subtitle_name(line: str) -> str:
    match = re.findall(r'^SUBTITLE ([A-Z0-9\-\.\s]+)', line)
    if match:
        return match[0]
    return None


def extract_chapter_name(line: str) -> str:
    match = re.findall(r'^CHAPTER ([A-Z0-9\-\.\s]+)', line)
    if match:
        return match[0]
    return None


def extract_subchapter_name(line: str) -> str:
    match = re.findall(r'^SUBCHAPTER ([A-Z0-9\-\.\s]+)', line)
    if match:
        return match[0]
    return None


def extract_section(line: str) -> str:
    match = re.findall(r'^Sec\. (\d+\.[\dA-Za-z]+)\. ([0-9A-Z\,\;\:\-\s]+)\. (.*)', line)
    if match:
        return match[0]
    return None, None, None


def is_legislative_history(line: str):
    lupper = line.upper().strip()
    if lupper.startswith('ADDED BY ACTS'):
        return True

    if lupper.startswith('AMENDED BY:'):
        return True

    if re.findall(r'^ACTS \d{4}', lupper):
        return True

    return False


def classify(line: str, context: dict) -> (bool, dict):
    context['save_section'] = False

    code_name = extract_code_name(line)
    if code_name:
        context['code_name'] = code_name
        context['text'] = None
        return context

    title_name = extract_title_name(line)
    if title_name:
        context['title'] = title_name
        context['text'] = None
        return context

    subtitle_name = extract_subtitle_name(line)
    if subtitle_name:
        context['subtitle'] = subtitle_name
        context['text'] = None
        return context

    chapter_name = extract_chapter_name(line)
    if chapter_name:
        context['chapter'] = chapter_name
        context['text'] = None
        return context

    subchapter_name = extract_subchapter_name(line)
    if subchapter_name:
        context['subchapter'] = subchapter_name
        context['text'] = None
        return context

    if is_legislative_history(line):
        return context

    section_number, section_name, code = extract_section(line)
    if section_number:
        context['save_section'] = context['section_number'] != section_number
        context['section_number'] = section_number.strip()
        context['section_name'] = section_name.strip()
        context['text'] = code.strip()
        return context

    if context['section_number']:
        if context.get('text', None):
            context['text'] += '\n\n' + line

    return context


def clean(line: str) -> str:
    return line.strip().replace('\r', '').replace('\t', '')
