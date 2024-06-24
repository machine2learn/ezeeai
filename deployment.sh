#!/bin/bash

docker pull tensorflow/serving:2.13.0

nohup docker run -p 8501:8501 --mount type=bind,source=$PWD,target=/models/ -e MODEL_NAME=model_name -t tensorflow/serving:2.13.0 1>log 2>err &


