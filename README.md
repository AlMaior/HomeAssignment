# HomeAssignment
Please **implement** as part of home assignment integration tests for small util `log formatter`.
It is command-line util, which transforms logs from *access log* format to *collection log format*
and also splits logs into defined size blocks.


Executing example of the util:

`python log_formatter.py format-logs --input_logs <log file or folder> --output_folder <folder to save results> --api_key <provide key[any string]> --block_size <size of logs in single output file>`

Example - the input file/folder contains 1000 lines of access logs. We define *block_size*  = 350. The result 
of util execution will be 2 files with block size 350 and 1 file with block size 300.

Example of collection log format:
```json
    {
        "common": {
            "attributes": {
                "plugin_attributes": {
                    "input_logs": "input_logs",
                    "block_size": 2000
                },
                "plugin": {
                    "type": "dataset-formatter",
                    "version": "0.2.0"
                },
                "api_key": "some_api_key|DatasetFormatter"
            }
        },
        "logs": [
            {
                "attributes": {},
                "message": "45.138.4.22 - - [20/Dec/2020:06:05:35 +0100] \"POST /index.php?option=com_contact&view=contact&id=1 HTTP/1.1\" 200 188 \"-\" \"Mozilla/5.0(Linux;Android10;MAR-LX1BBuild/HUAWEIMAR-L21B;wv)AppleWebKit/537.36(KHTML,likeGecko)Version/4.0Chrome/85.0.4183.81MobileSafari/537.36EdgW/1.0\" \"-\"",
                "timestamp": 1645075807256
            },
            {
                "attributes": {},
                "message": "45.153.227.31 - - [20/Dec/2020:12:33:49 +0100] \"GET /index.php?option=com_contact&view=contact&id=1 HTTP/1.1\" 200 9873 \"-\" \"Mozilla/5.0(WindowsNT6.1;Win64;x64)AppleWebKit/537.36(KHTML,likeGecko)Chrome/83.0.4103.116Safari/537.36\" \"-\"",
                "timestamp": 1645075807257
            }
        ]
    }
```

Block size is defined as the size of array *logs*. In the current example, the block size is 2. As for the previous example, each file will contain the current JSON (collection format) with 
according *logs* array size 

**message** contains the original access log from input file. 

**timestamp** is insertion time of specific log to *logs* array.

**common.attributes.plugin_attributes.block_size** is meta-info on block size.

**common.attributes.api_key** is argument which provided to util with suffix `|DatasetFormatter` 


