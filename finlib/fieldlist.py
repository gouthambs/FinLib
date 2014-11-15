__author__ = 'gbalaraman'

import datetime

fieldlist = {
    'coupon' : dict(longname = "Coupon",
                    displayname = "Coupon",
                    document = "Coupon that the bond pays in % units",
                    type = float),
    'gwac' : dict(longname = "Gross Weighted Average Coupon",
                  displayname = "GrossWAC",
                  document = "Gross weighted average coupon in % units",
                  type = float),
    'wam' : dict(longname = "Weighted Amortization Months",
                 displayname = "WAM",
                 document = "",
                 type = float),
    'wala' : dict(longname = "Weighted Average Loan Age",
                  displayname = "WALA",
                  document = "",
                  type = float ),
    'term' : dict(type = int),
    'settle_date' : dict(type = datetime.date),
    'issue_date' : dict(type = datetime.date),
    'balloon' : dict( type=int),
    'current_balance' : dict( type=float),

}