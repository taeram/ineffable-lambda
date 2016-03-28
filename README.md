# Ineffable Lambda
This AWS Lambda code is used to resize images uploaded by [ineffable](https://github.com/taeram/ineffable).

## Local development setup
```bash
    # Clone the repo
    git clone git@github.com:taeram/ineffable-lambda.git
    cd ineffable-lambda

    # Setup virtualenv
    virtualenv .venv
    source .venv/bin/activate

    # Install the latest supported version of boto3: https://docs.aws.amazon.com/lambda/latest/dg/current-supported-versions.html
    pip install boto3==1.2.6

    # Install and configure the AWS CLI
    pip install awscli six
    aws configure

    # Install ImageMagick
    sudo apt-get install -y imagemagick

    # Download and install the ffmpeg binary to the current directory (for converting .gif to .webm)
    FFMPEG_DIR=$( mktemp --directory )
    curl http://johnvansickle.com/ffmpeg/builds/ffmpeg-git-64bit-static.tar.xz | tar xJ --strip-components=1 -C $FFMPEG_DIR
    cp $FFMPEG_DIR/ffmpeg .
```

### Deploy to Lambda

Create a Lambda function:

* Login to the AWS Console, browse to Lambda and click Create a Lambda function
* In the Select Blueprint step, click Skip
* In the Configure function step, enter in the following:
 * Name: ineffable_lambda
 * Runtime: Python 2.7
* Under Lambda function code, select "Upload a .ZIP file"
 * In another browser window, download the latest version of the Lambda dependencies: [ineffable-lambda-dependencies.latest.zip](https://s3.amazonaws.com/ineffable-code/ineffable-lambda-dependencies.latest.zip)
 * Download the latest version of the `main.py` from this repo and add it to the dependencies zip file
 * Upload the zip file
* Under Lambda function handler and role:
 * Handler: main.lambda_handler
 * Role: S3 execution role
  * When asked for a name, call it `ineffable_lambda`
* Under Advanced settings:
 * Memory (MB): 128MB
 * Timeout: 5 min, 0 sec
 * VPC: No VPC
* Finally, click Next
* On the Review step, click Create function

Adding S3 Buckets to your Lambda function:

* Once your Lambda function has been created, browse to it
* In your Lambda function, click the "Event Sources" tab
* Click Add event source
 * Event source type: S3
* In the Add event source window:
 * Event source type: S3
 * Bucket: <select your S3 bucket>
 * Event type: Post
 * Prefix: <leave blank>
 * Suffix: <leave blank>
 * Enable event source: Enable now
* Click Submit
* Repeat these steps for each S3 bucket you're using with ineffable

Edit the IAM settings:

 * Login to the AWS console, and browse to IAM
 * In the sidebar, click Roles
 * Click the `ineffable_lambda` role we created above
 * Under Inline Policies, click "Edit Policy"
 * Update the policy so it looks like the following:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:*:*:*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:PutObjectAcl"
            ],
            "Resource": "*"
        }
    ]
}
```
 * Click Apply Policy

### Rebuilding the dependencies

This step shouldn't be necessary, but if you need to rebuild the dependencies:

* Spin up a new EC2 instance using AMI `ami-60b6c60a` in the `us-east-1` region
 * Check https://docs.aws.amazon.com/lambda/latest/dg/current-supported-versions.html for the latest AMI version for each region
* SSH into the new instance `ssh -i ~/.ssh/<your key pair>.pem ec2-user@<instance ip address>`
* Use git to clone this repo: `sudo yum install -y git && git clone git@github.com:taeram/ineffable-lambda.git`
* Build the package by: `sudo ./bin/package.sh`
* Copy the env.zip to your local machine
* Add main.py to env.zip and upload env.zip to AWS Lambda
