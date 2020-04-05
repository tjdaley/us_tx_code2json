# us_tx_code2json
Prepares Texas Codified Statutes for Quick Searching

<p align="center">
    <a href="https://github.com/tjdaley/us_tx_code2json/issues"><img alt="GitHub issues" src="https://img.shields.io/github/issues/tjdaley/us_tx_code2json"></a>
    <a href="https://github.com/tjdaley/us_tx_code2json/network"><img alt="GitHub forks" src="https://img.shields.io/github/forks/tjdaley/us_tx_code2json"></a>
    <a href="https://github.com/tjdaley/us_tx_code2json/stargazers"><img alt="GitHub stars" src="https://img.shields.io/github/stars/tjdaley/us_tx_code2json"><a>
    <img alt="Stage: Development" src="https://img.shields.io/badge/stage-Development-orange">
</p>
<p align="center">
    <a href="#purpose">Purpose</a> &bull;
    <a href="#installation">Installation</a> &bull;
    <a href="#configuration-files">Configuration Files</a> &bull;
    <a href="#usage">Usage</a> &bull;
    <a href="#virtual-environment">Virtual Env</a> &bull;
    <a href="#author">Author</a>
</p>

## Purpose
The application downloads HTML-version of Texas codified statutes and indexes them for quick searches.

## Installation
```
git clone https://github.com/tjdaley/us_tx_code2json
cd us_tx_code2json
python3 -m venv ./app/bin/activate
python -m pip -r requirements.txt
```

## Configuration Files

Each codified body of law, such as the Family Code, or Estates Code, or Civil Practice and Remedies Code, can be downloaded and processed.

In the ```codes``` folder, there is one JSON-encoded params file for each code. The ```app.py``` program takes one required argument which is the name of the file. By my convention, the name of the file is the same two-letter abbreviation that is used on texas.gov, but that is not required.

For example:

Code's Name | Two-Letter Abbreviation | Config File
------------|-------------------------|------------
Family Code | FA | fa.json
Estates Code | ES | es.json
Civil Practice & Remedies Code | CP | cp.json

Each configuation file is formatted like this (example Family Code configuration):

```json
{
    "code_name": "FA",
    "chapter_range_low": 1,
    "chapter_range_high": 266,
    "add_chapters": ["35A"],
    "skip_chapters" : []
}
```

Field Name | Description
-----------|------------
code_name | This is the two-letter abbreviation for constructing URLs to download code files.
chapter_range_low | The lowest chapter number in this codified set of statutes.
chapter_range_high | The highest chapter number in this codified set of statutes.
add_chapters | An array of non-numeric chapters that will be added to the list for processing.
skip_chapters | An array of chapters that will NOT be processed. This is mostly for skipping chapters that are causing problems.

## Usage

The ```app.py``` program can be invoked to download and process every chapter of the codified law or just one chapter, depending on the command line arguments used.

To download and process the entire Texas Family Code, use this command from the app folder:

```
python app.py --code fa
```

To download and process just the crypto chapter of the estates code, use this command:

```
python appy.py --code es --chapter 2001
```

## Virtual Environment

From the us_tx_code2json folder:

**To Activate** (*Linux ONLY*)
```
python3 -m venv ./app/bin/activate
```

**To Deactivate**
```
deactivate 
```

## Author

Thomas J. Daley, J.D. is an active family law litigation attorney practicing primarily in Collin County, Texas, an occassional mediator, and software developer. [Web Site](https://koonsfuller.com/attorneys/tom-daley/)
