#!/usr/bin/env python
# coding: utf-8

from db import get
from parsers.schedule_parser import parser

get.events_to_db(parser())
