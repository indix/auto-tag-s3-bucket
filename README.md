# auto-tag-s3-buckets

This is a tiny utility that helps to automatically tag all S3 buckets from a Google spreadsheet.

## Usage
```
$ python main.py --help
usage: main.py [-h] [-i SPREADSHEET_ID] [-c CREDENTIALS_JSON]

optional arguments:
  -h, --help            show this help message and exit
  -i SPREADSHEET_ID, --spreadsheet-id SPREADSHEET_ID
                        Id of the Google spreadsheet - available in the URL
  -c CREDENTIALS_JSON, --credentials-json CREDENTIALS_JSON
                        Path to service credentials json file
```

The `CREDENTIALS_JSON` can be generated by following the instructions from [here](http://gspread.readthedocs.io/en/latest/oauth2.html#using-signed-credentials).

## Example spreadsheet format
<img src="https://raw.githubusercontent.com/indix/auto-tag-s3-bucket/master/docs/demo.png"/>

`Bucket` is a mandatory column which represents the bucket name we want to tag. Any other columns would become the names of Tags for the bucket.

## License
http://www.apache.org/licenses/LICENSE-2.0
