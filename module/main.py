import boto3, json, logging

from HiDT_module import HiDT_module
from utils import remove_ext, log_wanring, log_info

BUCKET_NAME = "loyw"
STYLES_DIR = "../data/styles"
LOGGING_LEVEL = logging.INFO

s3 = boto3.client('s3')
sqs = boto3.resource('sqs')
queue = sqs.Queue("https://sqs.us-east-2.amazonaws.com/587356586656/loyw.fifo")

if __name__ == "__main__":
    logging.basicConfig(level=LOGGING_LEVEL)
    log_info("Image module initialized.")

    try:
        while True:
            messages = queue.receive_messages(
                WaitTimeSeconds=10,
            )

            # Check if there are no messages in the queue.
            if len(messages) == 0:
                continue
            
            try:
                body = json.loads(messages[0].body)
            except json.JSONDecodeError as err:
                messages[0].delete()
                log_wanring("Received an invalid message: " + str(err))
                continue
                
            messages[0].delete()
            response = s3.list_objects(
                Bucket=BUCKET_NAME,
                Prefix=body["username"] + '/' + remove_ext(body["imageName"]) + '/'
            )

            # Check if the images has already been created.
            if "Contents" in response and len(response["Contents"]) == 5:
                log_info(f"{body['username']}'s {body['imageName']} has already been created.")
                continue
            
            try:
                results = HiDT_module.infer(body["username"], body["imageName"], STYLES_DIR)
                log_info("Image " + "\"" + "\", \"".join(results) + "\"" + " have been created.")
            except KeyError as err:
                log_wanring("Received an invalid message: " + str(err))


    except KeyboardInterrupt:
        log_info("Image module terminated.")