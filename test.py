import boto3, json, uuid

sqs = boto3.resource('sqs')
queue = sqs.Queue("https://sqs.us-east-2.amazonaws.com/587356586656/loyw.fifo")

def send_test_message(username: str, image_name: str):
    body = {
        "username": username,
        "imageName": image_name,
    }
    
    queue.send_message(
        MessageBody=json.dumps(body),
        MessageGroupId=username,
        MessageDeduplicationId=str(uuid.uuid4())
    )

def clear_queue():
    while True:
        messages = queue.receive_messages(
            WaitTimeSeconds=1,
        )

        # Check if there are no messages in the queue.
        if len(messages) == 0:
            break
            
        messages[0].delete()
        
if __name__ == "__main__":
    clear_queue()
    send_test_message("kongbm", "test-image.jpg")