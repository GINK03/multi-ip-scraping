aws ec2 request-spot-instances --spot-price "0.03" --instance-count 1 --type "one-time" --launch-specification file://spec.json

