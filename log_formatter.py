import json
import logging
import os
import time

import click
from datetime import datetime

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

neosec_data_formatter_key = "DatasetFormatter"
version = "0.2.0"


###############################
# Templates for messages
###############################
def _get_log_template():
    return {
        "attributes": {},
        "message": "",
        "timestamp": ""
    }


def _get_call_template():
    return {
        "common": {
            "attributes": {
                "plugin_attributes": {},
                "plugin": {
                    "type": "",
                    "version": version
                }
            }
        },
        "logs": []
    }


@click.group()
def cli():
    """A cli-tool to format logs"""
    pass


def _decorate_csv_log(msg):
    log = _get_log_template()
    msg["responseHeaders"] = json.loads(msg["responseHeaders"])
    msg["requestHeaders"] = json.loads(msg["requestHeaders"])
    log["message"] = json.dumps(msg)
    log["timestamp"] = int(time.time_ns() / 1000000)
    return log


def _decorate_log(msg):
    formatted_msg = msg.replace("\n", "").replace("\r", "")
    log = _get_log_template()
    log["message"] = formatted_msg
    log["timestamp"] = int(time.time_ns() / 1000000)
    return log


def _build_call_file_from_list(logs):
    out = list()
    for log in logs:
        out.append(_decorate_log(log))
    return out


def _decorate_client_logs(file_paths, block_size=1000, skip_first_lines=0):
    out = list()
    with open(file_paths) as file:
        for line in file:
            if skip_first_lines > 0:
                skip_first_lines -= 1
                continue
            out.append(_decorate_log(line))
            if len(out) >= block_size:
                yield out
                out.clear()
    yield out


def _build_block(file_paths, block_size=1000):
    out = list()
    with open(file_paths) as file:
        for line in file:
            out.append(line)
            if len(out) >= block_size:
                yield out
                out.clear()
    yield out


def _build_message(logs, organisation_key, input_logs, block_size):
    call = _get_call_template()
    attributes = call["common"]["attributes"]
    attributes["api_key"] = f"{organisation_key}|{neosec_data_formatter_key}"
    dataset_formatter = attributes["plugin_attributes"]
    plugin_object = attributes["plugin"]
    dataset_formatter["input_logs"] = input_logs
    dataset_formatter["block_size"] = block_size
    plugin_object["type"] = "dataset-formatter"
    call["logs"] = logs
    return call


def _build_and_write_file(log_list, output_folder, api_key, input_logs, block_size, file_prefix):
    if log_list:
        formatted_call = _build_message(log_list, api_key, input_logs, block_size)
        with open(f"{output_folder}/formatted-calls-{file_prefix}.json", "w") as w_file:
            w_file.write(json.dumps(formatted_call))


def _get_suffix():
    dt = datetime.now()
    return str(dt.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])


@cli.command()
@click.option('--input_logs', help='Input logs folder or file ', required=True)
@click.option('--output_folder', help='Output formatted logs folder ', required=True)
@click.option('--api_key', help='User api-key', required=True)
@click.option('--block_size', default=1000, help='Number of logs in one message call', required=False)
@click.option('--skip_first_lines', default=0, help='Skip first [N] lines', required=False)
def format_logs(input_logs, output_folder, api_key, block_size, skip_first_lines):
    files = list()
    logger.info("Starting Local_log_format ...")
    if os.path.isdir(input_logs):
        files = [os.path.join(input_logs, f) for f in os.listdir(input_logs) if
                 os.path.isfile(os.path.join(input_logs, f)) and not f.startswith(".")]
    elif os.path.isfile(input_logs):
        files.append(input_logs)
    else:
        raise Exception("input_logs is nor folder nor file")
    for file in files:
        for logs in _decorate_client_logs(file, block_size, skip_first_lines):
            _build_and_write_file(logs, output_folder, api_key, input_logs, block_size, _get_suffix())


if __name__ == '__main__':
    cli()
