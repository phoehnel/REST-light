#!/bin/bash
service nginx start
uwsgi --init uwsgi.ini