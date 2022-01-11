#!/bin/bash

ssh pi@mars-rover "rm -rf ~/project"
scp -r ./src pi@mars-rover:~/project
