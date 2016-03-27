# Ineffable Lambda
This AWS Lambda code is used to resize images uploaded by [ineffable](https://github.com/taeram/ineffable).

## Local development setup
```bash
    # Clone the repo
    git clone git@github.com:taeram/ineffable-lambda.git
    cd ineffable-lambda

    # Install system dependencies (for Ubuntu)
    sudo apt-get install -y libjpeg-dev libtiff-dev libzip-dev gcc tk-dev tcl-dev

    # Setup virtualenv
    virtualenv .venv
    source .venv/bin/activate

    # Install the python dependencies
    pip install -r requirements.txt

    # Install the latest supported version of boto3: https://docs.aws.amazon.com/lambda/latest/dg/current-supported-versions.html
    pip install boto3==1.2.6

    # Install and configure the AWS CLI
    pip install awscli six
    aws configure

    # Download and install the ffmpeg binary to the current directory (for converting .gif to .webm)
    FFMPEG_DIR=$( mktemp --directory )
    curl http://johnvansickle.com/ffmpeg/builds/ffmpeg-git-64bit-static.tar.xz | tar xJ --strip-components=1 -C $FFMPEG_DIR
    cp $FFMPEG_DIR/ffmpeg .
```

### Deploy to Lambda

    * Download the latest version of the Lambda dependencies: [ineffable-lambda-dependencies.latest.zip](https://s3.amazonaws.com/ineffable-code/ineffable-lambda-dependencies.latest.zip)
    * Download the latest version of the `main.py` from this repo and add it to the dependencies zip file
    * Upload the zip file to AWS Lambda
    * Done!

### Rebuilding the dependencies

This step shouldn't be necessary, but if you need to rebuild the dependencies:

    * Spin up a new EC2 instance using AMI `ami-60b6c60a` in the `us-east-1` region
     * Check https://docs.aws.amazon.com/lambda/latest/dg/current-supported-versions.html for the latest AMI version for each region
    * SSH into the new instance `ssh -i ~/.ssh/<your key pair>.pem ec2-user@<instance ip address>`
    * Use git to clone this repo: `sudo yum install -y git && git clone git@github.com:taeram/ineffable-lambda.git`
    * Build the package by: `sudo ./bin/package.sh`
    * Copy the env.zip to your local machine
    * Add main.py to env.zip and upload env.zip to AWS Lambda
