# -*- coding: utf-8 -*-
"""
Created on Fri Sep 19 21:57:18 2014

@author: Gouthaman Balaraman
"""
import calendar
import datetime

def shift_months(from_date, num_months):
     month = from_date.month - 1 + num_months
     year = from_date.year + month / 12
     month = month % 12 + 1
     day = min(from_date.day,calendar.monthrange(year,month)[1])
     return from_date.replace(year=year,month=month,day=day)
     

def shift_days(from_date,num_days):
    return from_date + datetime.timedelta(days=num_days)


def shift_years(from_date,num_years):
    num_years = (int)(num_years)
    try:
        return from_date.replace(year=from_date.year + num_years)
    except:
        return from_date.replace(month=2, day=28, year=from_date.year+num_years)    


def get_month_diff(start_date, end_date):
    span = (end_date.year*12+end_date.month) - (start_date.year*12 + start_date.month)
    return span


def get_month_end(date):
    dayrange = calendar.monthrange(date. year, date. month)
    return date.replace(day=dayrange[1])