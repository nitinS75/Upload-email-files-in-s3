from setuptools import setup
setup(
    
    name = "email_to_s3",
    version = "0.1.0",
    py_modules = ['email_to_s3'],  # for file name
    # packages = ['email_to_s3.py'], for package
    install_requires =["boto3==1.20.31"],
 
    )

