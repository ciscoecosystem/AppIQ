#!/bin/sh
/usr/sbin/sshd
echo "=================================" >> /home/app/log/app.log
date >> /home/app/log/app.log
# pip install graphene >> /home/app/log/app.log
# pip install flask_graphql >> /home/app/log/app.log

echo "=================================" >> /home/app/log/app.log

python /home/app/src/Service/app.py >> /home/app/log/app.log 2>> /home/app/log/app.log
