import boto3
import logging
import gspread
import argparse
import sys
from oauth2client.service_account import ServiceAccountCredentials

class Functions(object):
  @staticmethod
  def is_empty(str):
    return str.strip() == ""

  @staticmethod
  def is_not_empty(str):
    return not Functions.is_empty(str)

class Bucket:
  def __init__(self, zipped):
    self.tags = dict()
    for (name, value) in zipped:
      if name == 'Bucket':
        self.name = value
      elif Functions.is_not_empty(name) and Functions.is_not_empty(value):
        self.tags[name] = value
      else:
        logging.debug("Ignoring tag %s=%s for %s because one of them is empty", name, value, self.name)

  def is_valid(self):
    return Functions.is_not_empty(self.name)

  def as_dict(self):
    return {
      "bucket": self.name,
      "tags": self.tags
    }

  def tags_as_list(self):
    tags = []
    for name in self.tags:
      tags.append({"Key": name, "Value": self.tags[name]})

    return tags

  def merge_existing_tags(self, tagset):
    for tag in tagset:
      if Functions.is_empty(self.tags[tag['Key']]):
        self.tags[tag['Key']] = tag.Value
      else:
        logging.warn("Not overriding an existing tag, %s=%s for %s", tag['Key'], tag['Value'], self.name)


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument("-i", "--spreadsheet-id", help="Id of the Google spreadsheet - available in the URL")
  parser.add_argument("-c", "--credentials-json", help="Path to service credentials json file")
  args = parser.parse_args()
  if not args.credentials_json:
    sys.exit("-c is required. Please pass service account credentials file")
  elif not args.spreadsheet_id:
    sys.exit("-i is required. Please pass the spreadsheet ID")

  scope = ['https://spreadsheets.google.com/feeds']
  credentials = ServiceAccountCredentials.from_json_keyfile_name(args.credentials_json, scope)
  gc = gspread.authorize(credentials)
  worksheet = gc.open_by_key(args.spreadsheet_id).sheet1
  headers = filter(Functions.is_not_empty, worksheet.row_values(1))
  s3 = boto3.resource('s3')

  total_rows = worksheet.row_count

  for row_idx in range(2, total_rows):
    row = worksheet.row_values(row_idx)
    zipped = zip(headers, row)
    bucket = Bucket(zipped)
    if bucket.is_valid():
      bucket_tagging = s3.BucketTagging(bucket.name)
      bucket.merge_existing_tags(bucket_tagging.tag_set)
      print "Final set of tags for ", bucket.name, "is ", bucket.tags_as_list()
      bucket_tagging.put(Tagging={
        'TagSet': bucket.tags_as_list()
      })
    else:
      logging.warn("Ignoring an invalid row - %d in the sheet", row_idx)
