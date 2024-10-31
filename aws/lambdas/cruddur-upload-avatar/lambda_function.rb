require 'aws-sdk-s3'
require 'json'

def lambda_handler(event:, context:)
  puts event
  if event['routeKey'] == "OPTIONS /{proxy+}"
    puts "This is OPTIONS!!!"
    return { 
      statusCode: 200,
      body: JSON.generate('Hello from cruddur-cors!'),
      headers: {
        "Access-Control-Allow-Headers": "*, Authorization",
        "Access-Control-Allow-Origin": "https://cruddur.myhomelab.xyz",
        "Access-Control-Allow-Methods": "OPTIONS,GET,POST"
      }
    }
  end
  
  sub = event['requestContext']['authorizer']['lambda']['sub']
  body = JSON.parse(event['body'])
  extension = body['extension']
  s3 = Aws::S3::Resource.new
  bucket_name = ENV["UPLOADS_BUCKET_NAME"]
  object_key = "#{sub}.#{extension}"
  obj = s3.bucket(bucket_name).object(object_key)
  url = obj.presigned_url(:put, expires_in: 300)
  body = {url: url}.to_json
  return { 
    statusCode: 200,
    body:body,
    headers: {
      "Access-Control-Allow-Headers": "*, Authorization",
      "Access-Control-Allow-Origin": "https://cruddur.myhomelab.xyz",
      "Access-Control-Allow-Methods": "OPTIONS,GET,POST"
    }
  }
end