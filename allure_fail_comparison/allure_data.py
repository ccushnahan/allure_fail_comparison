import pandas
import openpyxl
import re


def process_data(data: dict, base_url: str) -> pandas.DataFrame:
    """Takes data and structures it."""

    structured_data = [["test_id", "test_name", "test_status", "flaky", "new_fail", "prev_run_result", "failed_step", "failed_base_step", "image_urls"]]
    for test_data in data.values():
        rel_data = extract_relevant_info(test_data, base_url)
        structured_data.append(rel_data)
    df = pandas.DataFrame(structured_data[1:], columns=structured_data[0])
    print(df.head())
    return df


def extract_relevant_info(test: dict, base_url: str) -> dict:
    test_id = get_test_id(test)
    test_name = test['fullName']
    test_status = test['status']
    flaky = test['flaky']
    new_fail = test['newFailed']
    failed_step = get_failed_step(test)
    failed_base_step = get_base_failed_step(failed_step)
    prev_run_result = get_prev_run_result(test)
    image_urls = get_image_urls(test, base_url)
    return [
        test_id,
        test_name,
        test_status,
        flaky,
        new_fail,
        prev_run_result,
        failed_step,
        failed_base_step,
        image_urls
    ]

def get_failed_step(test: dict) -> str:
    """Gets the failed step"""

    for step in test['testStage']["steps"]:
        if step['status'] == 'broken':
            return step['name']
        if step['status'] == 'failed':
            return step['name']

def get_base_failed_step(failed_step: str):
    """Return failed step without values."""
    base_failed_step = re.sub(r'"[a-zA-Z ]+"', '"([^\\"]*)"', failed_step)
    return base_failed_step


def get_image_urls(test: dict, base_url) -> str:
    """Get image url if possible"""
    urls = []
    for after_stage in test['afterStages']:
        if after_stage['attachments'] != []:
            image_source = after_stage['attachments']['source']
            image_url = f"{base_url}data/attachments/{image_source}"
            urls.append(image_url)
    return ", ".join(urls)


def get_test_id(test: dict) -> str:
    """Gets ID tag of test"""
    for item in test['labels']:
        if "OPTSPSEND" in item['value']:
            return item['value']
    return ""

def get_prev_run_result(test: dict) -> str:
    """Gets previous run result."""
    history = test['extra']['history']
    try:
        return history['items'][0]['status']
    except Exception as e:
        return "No history found"

def export_data(df: pandas.DataFrame, date: str) -> None:
    """Saves data to variety of formats."""
    date = date.replace("/", "-")
    df.to_excel(f"test_run_{date}.xlsx")