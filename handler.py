import boto3
import PIL
from PIL import Image
from io import BytesIO
from os import path

s3 = boto3.resource('s3')
origin_bucket = 'pythia-python-originals'
destination_bucket = 'pythia-python-resized'
width_size = 600

def s3_resize_image(event, context):
    
    for key in event.get('Records'):
        object_key = key['s3']['object']['key']
        extension = path.splitext(object_key)[1].lower()

        # Grab the source file
        obj = s3.Object(
            bucket_name=origin_bucket,
            key=object_key,
        )
        obj_body = obj.get()['Body'].read()
    
        # Check the extension and
        # Define the buffer format
        if extension in ['.jpeg', '.jpg']:
            format = 'JPEG'
        if extension in ['.png']:
            format = 'PNG'

        # Resize the image with defined width and
        # proportional height.
        img = Image.open(BytesIO(obj_body))
        wpercent = (width_size / float(img.size[0]))
        hsize = int((float(img.size[1]) * float(wpercent)))
        img = img.resize((width_size, hsize), PIL.Image.ANTIALIAS)
        buffer = BytesIO()
        img.save(buffer, format)
        buffer.seek(0)

        # Upload the resized image to resized bucket
        obj = s3.Object(
            bucket_name=destination_bucket,
            key=object_key,
        )
        obj.put(
          ACL='public-read',
          ContentType='image/jpeg',
          Body=buffer,
          )

        # Print results to CloudWatch
        print('File saved at {}/{}'.format(
            destination_bucket,
            object_key,
        ))
