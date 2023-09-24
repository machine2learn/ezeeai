#!/bin/bash

docker pull tensorflow/serving:2.11.1

nohup docker run -p 8501:8501 --mount type=bind,source=$PWD,target=/models/ -e MODEL_NAME=model_name -t tensorflow/serving:2.11.1 1>log 2>err &


