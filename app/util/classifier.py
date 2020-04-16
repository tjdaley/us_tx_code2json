"""
classifier.py - Classify text elements to JSON doc

Copyright (c) 2020 by Thomas J. Daley, J.D.
"""
import json
import re


class Classifier(object):
    def classify_doc(self, text_content: str, code: str, filename: str) -> dict:
        lines = text_content.split('\n')
        doc = []
        context = {}
        context['code'] = code
        context['code_name'] = None
        context['title'] = None
        context['subtitle'] = None
        context['chapter'] = None
        context['subchapter'] = None
        context['section_prefix'] = None
        context['section_number'] = None
        context['section_name'] = None
        context['text'] = None
        context['filename'] = filename
        context['future_effective_date'] = None
        context['save_section'] = False
        context['source_text'] = ''
        prior_context = context.copy()

        for source_line in lines:
            line = clean(source_line)
            if not line:
                continue

            context = classify(line, context, source_line)

            if prior_context['section_number'] != context['section_number'] and prior_context['text']:
                del prior_context['save_section']
                doc.append(prior_context)

            prior_context = context.copy()
        doc.append(context)
        return doc


def extract_code_name(line: str) -> str:
    match = re.findall(r'^([A-Z\-\s]+) CODE', line)
    if match:
        return match[0]

    match = re.findall(r'^CODE OF ([A-Z\-\s]+)', line)
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
        return match[0][0], match[0][1], match[0][2], 'Sec.'

    match = re.findall(r'^Art\. (\d+\.[\dA-Za-z]+)\. ([0-9A-Z\,\;\:\-\s]+)\. (.*)', line)
    if match:
        return match[0][0], match[0][1], match[0][2], 'Art.'

    return None, None, None, None


def is_legislative_history(line: str):
    lupper = line.upper().strip()
    if lupper.startswith('ADDED BY ACTS'):
        return True

    if lupper.startswith('AMENDED BY:'):
        return True

    if re.findall(r'^ACTS \d{4}', lupper):
        return True

    return False


def classify(line: str, context: dict, source_line: str) -> (bool, dict):
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
        # context['text'] = None
        return context

    if is_legislative_history(line):
        return context

    section_number, section_name, code, prefix = extract_section(line)
    if section_number:
        context['save_section'] = context['section_number'] != section_number
        context['section_prefix'] = prefix
        context['section_number'] = section_number.strip()
        context['section_name'] = section_name.strip()
        context['text'] = code.strip()
        context['source_text'] = source_line
        return context

    if context['section_number']:
        if context.get('text', None):
            context['text'] += '\n\n' + line
            context['source_text'] += ('\n\n' + source_line)

    return context


def clean(line: str) -> str:
    return line.strip().replace('\r', '').replace('\t', '')
