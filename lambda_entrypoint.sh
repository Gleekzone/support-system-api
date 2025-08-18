#!/bin/sh
if [ -z "${AWS_LAMBDA_RUNTIME_API}" ]; then
  # Local con RIE
  exec /usr/local/bin/aws-lambda-rie /usr/bin/python3 -m awslambdaric "$@"
else
  # En Lambda real
  exec /usr/bin/python3 -m awslambdaric "$@"
fi