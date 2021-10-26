#!/bin/bash

ssh pi@192.168.2.175 "rm -rf ~/project"
scp -r ./src pi@192.168.2.175:~/project
