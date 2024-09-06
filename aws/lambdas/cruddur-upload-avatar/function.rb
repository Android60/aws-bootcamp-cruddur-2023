require 'aws-sdk-s3'
require 'json'

def lambda_handler(event:, context:)
  puts event
  s3 = Aws::S3::Resource.new
  bucket_name = ENV["UPLOADS_BUCKET_NAME"]
  object_key = 'mock.jpg'
  obj = s3.bucket(bucket_name).object(object_key)
  url = obj.presigned_url(:put, expires_in: 300)
  body = {url: url}.to_json
  return { statusCode: 200, body:body}
end