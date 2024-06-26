import math
import json
from data import *

'''
Eventually use customerId to get income and debt from nessie api
'''
def get_viable_houses(zipcode, prefs, income, debt):
    (min_afford, max_afford) = calc_affordable_price(income, debt)

    house_list = get_houses_by_zip(zipcode, 
               (prefs["bed"], prefs["bed"] + 3), 
               (prefs["bath"], prefs["bath"] + 6), 
               (min_afford, max_afford)
    )

    house_tuples = sort_house_list(prefs, house_list, min_afford, max_afford)
    for h in house_tuples:
        print(h)

'''
prefs: {
    bed: int,
    bath: int
}

houses: [{
    attomId: 
    addr: string,
    listPrice: int,
    lotSize: int,
    bed: int,
    bath: float,
    rooms: int,
    a_score: float,
    p_score: float
},...]

return: [(house_object, affordability_score, preference_score), ...]
'''
def sort_house_list(prefs, house_list, min_afford, max_afford):
    def calc_a_score(house): 
        list_price = house["listingPrice"]

        # anything below the mean of min and max afford is completely affordable (a_score = 1)
        impact = 0.8 # how much deviation from the mean impacts affordability
        print("-----------")
        print((impact * (list_price - ((min_afford + max_afford) / 2)) / (max_afford - min_afford)))
        print(list_price)
        print(((min_afford + max_afford) / 2))
        print(max_afford - min_afford)
        print(list_price - (((min_afford + max_afford) / 2)))
        print("-----------")
        score = 1 - (impact * (list_price - ((min_afford + max_afford) / 2)) / (max_afford - min_afford))

        return min(score, 1)

    def calc_p_score(house):
        footage_per_dollar = house["lotsize"] / house["listingPrice"]
        bed_score = max(0, 75 * (house["beds"] - prefs["bed"]))
        bath_score = max(0, 75 * (house["bathstotal"] - prefs["bath"]))
        rooms_score = 20 * house["roomsTotal"]

        return footage_per_dollar + bed_score + bath_score + rooms_score
    
    max_p_score = 0

    house_tuples = []
    for house in house_list:
        p_score = calc_p_score(house)
        max_p_score = max(max_p_score, p_score)
        house_tuples.append((house, calc_a_score(house), p_score))

    house_tuples = [(house, a_score, p_score / max_p_score) for (house, a_score, p_score) in house_tuples]
    def sort_func(house_tuple):
        (_, a_score, p_score) = house_tuple
        boosted_a_score = a_score
        return math.sqrt(boosted_a_score * boosted_a_score + p_score * p_score)
    
    house_tuples.sort(key=sort_func, reverse=True)

    scored_houses = []
    for (house_object, a_score, p_score) in house_tuples:
        house_object["a_score"] = a_score
        house_object["p_score"] = p_score
        scored_houses.append(house_object)

    return scored_houses

'''
income: annual post tax income
debt: minimum monthly debt
'''
def calc_affordable_price(income, debt):
    # calculate monthly payments
    monthly_income = (income / 12) - debt
    min_monthly_payment = 0.05 * monthly_income
    max_monthly_payment = 0.7 * monthly_income

    '''
    M = how much pay per month
    r = monthly interest rate (yearly / 12) -> 7.5%
    n = total payments they make over the whole mortgage (30 years -> 360) = 12 ( years of mortage)
    house price = P + down payment
    '''
    def calc_home_price(monthly_payment): 
        down_payment = 0.2 * income
        r = 0.075 / 12
        n = 30 * 12

        P = (monthly_payment * (pow(r + 1, n) - 1)) / (r * pow(r + 1, n))
        return P + down_payment

    # calculate affordable price range (min, max) given monthly payments
    return (int(calc_home_price(min_monthly_payment)), int(calc_home_price(max_monthly_payment)))

'''
{
    attomId: string
    addr: string,
    listPrice: int,
    lotSize: int
    bed: int,
    bath: float,
    rooms: int,
}
'''

house_list = [
    {
        "attomId": 1,
        "addr": "addr 1",
        "listPrice": 1345,
        "lotSize": 1000,
        "bed": 3,
        "bath": 5,
        "rooms": 6
    },
    {
        "attomId": 2,
        "addr": "addr 2",
        "listPrice": 2000,
        "lotSize": 1500,
        "bed": 2,
        "bath": 5,
        "rooms": 6
    },
    {
        "attomId": 3,
        "addr": "addr 3",
        "listPrice": 3843,
        "lotSize": 1200,
        "bed": 1,
        "bath": 3,
        "rooms": 5
    }
]

prefs = {
    "list_price": 2000,
    "bed": 1,
    "bath": 1
}

# (min_afford, max_afford) = calc_affordable_price(100000, 500)
# sorted = sort_house_list(prefs, house_list, min_afford, max_afford)
# for house in sorted:
#     print(house)

# print(calc_affordable_price(100000, 500))
# get_viable_houses("95014", prefs, 100000, 500)