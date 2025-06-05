import requests
import time
import json
import os
import datetime
import subprocess
from data import airports, CVO
from selenium_driver import get_driver, get_flight_data

# will be filled later in the script according to the available cities
weather_by_city = {}


# global cookies
# global calls_counter
# cookies = get_cookies()
# calls_counter = 0
# If fails should update XSRF-TOKEN & laravel_session from site.
def get_data(FROM, TO, DATE):
    # global cookies
    # global calls_counter
    # calls_counter += 1
    # if calls_counter % 25 == 0:
    #     cookies = get_cookies()


    headers = {
        'accept': 'application/json',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/json',
        'origin': 'https://multipass.wizzair.com',
        'priority': 'u=1, i',
        'referer': 'https://multipass.wizzair.com/en/w6/subscriptions/availability/60739699-ee6d-4039-b264-dda0652d828f',
        'sec-ch-ua': '"Chromium";v="135", "Not-A.Brand";v="8"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'traceparent': '00-0000000000000000121a306976e0e55b-60c182e6b630ba42-01',
        'tracestate': 'dd=s:1;o:rum',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
        'x-datadog-origin': 'rum',
        'x-datadog-parent-id': '6971997625556974146',
        'x-datadog-sampling-priority': '1',
        'x-datadog-trace-id': '1304408271601329499',
        'x-xsrf-token': 'eyJpdiI6IlwvQldTMG1ERXJFVWIyWjdCVDdWZTlBPT0iLCJ2YWx1ZSI6IlhHcGxTYlFySjhMZG5Dd1RucVR6VHFxakVjVHFoTUxENlVTOTVwM0QwVlZFWVRad09zSFJsZDlkaTBlRVlwZnJMR1JPMmJQeGFoeW9PVWhKcWp5VzdBPT0iLCJtYWMiOiJhNDJmYTYwNzE4ZmVmZGVkZGZhMDk4ZmUyODMxM2I1YjY0ZjQ0MGQyYTA3NWU3MTA1ODRhNDZiMzRhMTQ1MTU1In0=',
        # 'cookie': 'OptanonAlertBoxClosed=2025-04-06T09:29:43.247Z; _hjSessionUser_3488145=eyJpZCI6IjgzMzc5YWZhLTMwOTctNWQxNS1iNDdkLTlmODcwNmEwZTEzNiIsImNyZWF0ZWQiOjE3NDM5MzE3MTY2MDksImV4aXN0aW5nIjp0cnVlfQ==; _hjSessionUser_2830831=eyJpZCI6ImE1NjE5OTlhLWM3ODEtNTZmOC04YzRjLWU2MTI5ZmNkMTQxZSIsImNyZWF0ZWQiOjE3NDM5MzE4MDI4NjUsImV4aXN0aW5nIjp0cnVlfQ==; emcid=T-ONp3rZDk0; _clck=eud9i%7C2%7Cfuv%7C0%7C1922; __gads=ID=1d6786dfe08bbf7a:T=1744019985:RT=1744019985:S=ALNI_MZV5Baw_Tcv0qV8k7kHomBEiq_uZA; __gpi=UID=0000108c3e61d1f1:T=1744019985:RT=1744019985:S=ALNI_Mb5O3dDMejDasS-8sRw_APdNNMLmw; __eoi=ID=5fd9298806d87d4e:T=1744019985:RT=1744019985:S=AA-AfjaporwCYUi1w2JWWEFJwprP; _ga_CLN8TZXB9T=GS1.1.1744391415.2.0.1744391415.60.0.0; _ga_1FKHJ07CD4=GS1.1.1744391415.2.0.1744391415.60.0.0; _ga_XT7DLK33SZ=GS1.1.1744391415.2.0.1744391415.0.0.0; _ga_G2EKSJBE0J=GS1.1.1744391415.2.0.1744391415.60.0.0; AWSALBAPP-1=_remove_; AWSALBAPP-2=_remove_; AWSALBAPP-3=_remove_; datadome=25PJ6kAJd2sNPXWmK9FQhaG1KVIyuv7pkw0zhU2kj1_iJC5P1astSb36ft53mqZRERZqLPcjp3JzdR7_e4eAkFMqh2Q1M2ArlEL8MwD5EXTQ4mVCTFk0csN25xRuS2IQ; RequestVerificationToken=196718eeff3d487ea28da1db168abd77; OptanonConsent=isGpcEnabled=0&datestamp=Sat+May+24+2025+15%3A11%3A18+GMT%2B0300+(Israel+Daylight+Time)&version=202404.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=ae2baf12-76fa-41df-bd25-fa40b3cf6fb0&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&groups=C0004%3A0%2CC0003%3A0%2CC0002%3A0%2CC0001%3A1%2CC0007%3A0&intType=2&geolocation=IL%3BTA&AwaitingReconsent=false; _ga_Y88LW1YQMB=GS2.1.s1748111843$o25$g1$t1748112882$j0$l0$h0; _gid=GA1.2.713540803.1749032526; XSRF-TOKEN=eyJpdiI6ImF3YTQwODg0KzZlUEdZZU9ITmdQY2c9PSIsInZhbHVlIjoid1JRZU9YdlZCVmx6b3dBWVR6NXp5Wlp5RlBvOFVScStvSjlYekJCWWtkcXdLQWxVQ2FKc2xYTndiM1FnMHBsSjMxdW9BRXRyZHpiV3c0OWtJUE1DMXc9PSIsIm1hYyI6IjQzY2FlZDhiZWNiYjFjZTM3M2Q0YTEzMGYxZWQ3NGQyMDg2NTQ0MTQ4NzQxNDM3ZTI5ZWE1MmMwYTA2YTZlZGQifQ%3D%3D; _gat_UA-26916529-1=1; _ga=GA1.1.1865910503.1743931717; _ga_YGVXBHR3KK=GS2.1.s1749032525$o27$g1$t1749035159$j59$l0$h0; laravel_session=eyJpdiI6InFwU3JKd3BDb2ttZFZ4TU9RdFIxZGc9PSIsInZhbHVlIjoiazJxd04wRmhHK2N3RDV5aHh3bUhrTHZzRFQ1MzF3RXUyNTg1N1pCSWNmQ3VuQlBrUjlaeXdDRHMrRmQ5cDh6czhZRVQrR0ZhenlcL1c4d0VjYmJ6OUx3PT0iLCJtYWMiOiJhMzNhYmQ5ODZmYjJlYzM4MmI4MDJiMjJiY2I3MTkxNTE2Nzk4M2Y5NzA2Y2UyOTMyZGYyNjAxNjAyMTc2YzE0In0%3D; AWSALBAPP-0=AAAAAAAAAACT+zDc58NlFeMF9P7HfJ0U3Pg2SF9CTqjo7KSKJbceke9UexyADfRNXc3C6nKur/0yesjvVe5oMEgLoDnsFlZbxwF4lYpU2B8QN8+Y6sqJ+vg4eXfHqVN/9u0KFQCoGpDWuQ==; _dd_s=aid=5f90dc92-3220-4793-a14e-f78e819a4fed&rum=2&id=eae5492d-8f56-4c4e-a9ba-d5fa0d3ac273&created=1749032524780&expire=1749036058758',
    }

    json_data = {
        'flightType': 'OW',
        'origin': FROM,
        'destination': TO,
        'departure': DATE,
        'arrival': '',
        'intervalSubtype': None,
    }

    response = requests.post(
        'https://multipass.wizzair.com/en/w6/subscriptions/json/availability/60739699-ee6d-4039-b264-dda0652d828f',
        cookies=cookies,
        headers=headers,
        json=json_data,
    )
    if response.status_code != 200:
        print(f"failed {FROM} {TO} {DATE} {response.content}")

    return response.json()

# def get_data_selenium(driver):
#     driver =

def get_weather_color(description):
    normalized = description.lower().replace(" ", "")  # lowercase and remove all spaces

    good_conditions = ["sunny", "clear", "lightdrizzle"]
    reasonable_conditions = [
        "partlycloudy",
        "cloudy",
        "overcast",
        "patchyrainnearby",
    ]

    if normalized in good_conditions:
        return "green"
    elif normalized in reasonable_conditions:
        return "yellow"  # dark yellow
    else:
        return "red"


def get_weather_by_city(city):
    if city in weather_by_city:
        return weather_by_city[city]

    url = f"https://wttr.in/{city}?format=j1"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        forecast = []
        for day in data["weather"][:3]:
            forecast.append({
                "date": day["date"],
                "avgTemp": f"{day['avgtempC']}°C",
                "description": day["hourly"][4]["weatherDesc"][0]["value"]  # Midday forecast
            })

        weather_by_city[city] = {
            "text": "Forecast: ",
            "style": []
        }

        for day in forecast:
            color = get_weather_color(day["description"])
            weather_by_city[city]["text"] += f"{day['date']}: {day['avgTemp']}, {day['description']} || "
            weather_by_city[city]["style"].append({
                "date": day["date"],
                "description": day["description"],
                "color": color,
                "avgTemp": day['avgTemp']
            })

        return weather_by_city[city]

    except requests.RequestException as e:
        print(f"Error: {e} for city {city}")
        return None


#/*********************************
#***** CHANGEABLE PARAMETERS ******
#*********************************/
ARRIVAL_TYPE = "ALL"          # "ALL" | "SPECIFICS" | "COUNTRY_CODE"
FROM = "TLV"                  # The airport code we're taking off from
DATES = "ALL" # ["2025-06-05"]        # "ALL" | ["2025-01-31"]
MAX_CALL_COUNT_PER_DATE = 999 # maximum calls to the API in a single run
all_options = {}              # object to store all the results 

def generate_page(ARRIVAL_TYPE="ALL", FROM="TLV", DATES="ALL", MAX_CALL_COUNT_PER_DATE=999):
    # print(f"running with {xsrf=} {laravel_session=}")
    all_options = {}

    if DATES == "ALL":
        DATES = []
        for i in range(4):
            date = datetime.datetime.now() + datetime.timedelta(days=i)
            DATES.append(date.strftime("%Y-%m-%d"))  # format: YYYY-MM-DD

    if ARRIVAL_TYPE == "ALL":
        # next(..., []) gets the first match or returns an empty list if no match is found.
        arrival_options = next(
            (r["arrivalStations"] for r in CVO["routes"] if r["departureStation"]["id"] == FROM),
            []
        )
    elif ARRIVAL_TYPE == "SPECIFICS":
        arrival_options = ["SOF", "LAR", "BUD"]
    else:
        arrival_options = [{"id": ARRIVAL_TYPE}]


    counter = 0
    for d in DATES:
        if counter != 0:
            time.sleep(60) # sleeping 60 seconds to avoid 429, notice using regular browser don't have this limitation, maybe should be fixed in another way.
        driver = get_driver()
        all_options[d] = []
        for opt in arrival_options:
            counter += 1
            if counter > MAX_CALL_COUNT_PER_DATE:
                print("STOPPED CALLS DUE TO MAX_CALL_COUNT_PER_DATE")
                break
            TO = opt["id"]
            try:
                # data_for_date = get_data(FROM, TO, d)

                data_for_date = get_flight_data(driver, FROM, TO, d)
                if "code" in data_for_date:
                    if data_for_date["code"] == "error.availability":
                        continue
                    else:
                        raise Exception(f"failed due to {data_for_date}")
                if not data_for_date:
                    raise Exception(f"weird failed check it")
                all_options[d].append(data_for_date)
            except Exception as e:
                print(f"failed to get data {FROM} {TO} {d} err: {e}")
                continue
    # all_options = json.loads('{"2025-06-05": [{"flightsInbound": [], "flightsOutbound": [{"actionText": "Select", "arrival": "10:50 pm", "arrivalDate": "5 June 2025", "arrivalDateIso": null, "arrivalDateTimeIso": "2025-06-06 00:50:00", "arrivalOffsetText": "UTC+2", "arrivalStation": "MXP", "arrivalStationCode": "MXP", "arrivalStationText": "Milan Malpensa", "carrierText": "Operated by W4", "currency": "ILS", "departure": "7:35 pm", "departureDate": "5 June 2025", "departureDateIso": "2025-06-05", "departureDateTimeIso": "2025-06-05 22:35:00", "departureOffsetText": "UTC+3", "departureStation": "TLV", "departureStationCode": "TLV", "departureStationText": "Tel-Aviv", "discount": "0.00", "displayPrice": 43, "duration": "03h 15m", "fare": "43.00", "fareBasisCode": null, "fareSellKey": "MH5BWUNQfn5XNn5BWUNQflNVQlN_fjB_Mn5_WCEx", "flightCode": "W46404", "flightId": "6404", "isFree": "false", "key": "W46404 TLV#20250605T1935~MXP#20250605T2250", "price": "43.00", "priceTag": "wizzair.subscriptions.availability.results.price.tag.premium", "reference": "VzR_NjQwNH4gfn5UTFZ_MDYvMDUvMjAyNSAxOTozNX5NWFB_MDYvMDUvMjAyNSAyMjo1MH5_", "stops": "Nonstop", "taxes": "0.00", "totalPrice": "43.00"}]}, {"flightsInbound": [], "flightsOutbound": [{"actionText": "Select", "arrival": "11:45 pm", "arrivalDate": "5 June 2025", "arrivalDateIso": null, "arrivalDateTimeIso": "2025-06-06 01:45:00", "arrivalOffsetText": "UTC+2", "arrivalStation": "FCO", "arrivalStationCode": "FCO", "arrivalStationText": "Rome Fiumicino", "carrierText": "Operated by W4", "currency": "ILS", "departure": "8:55 pm", "departureDate": "5 June 2025", "departureDateIso": "2025-06-05", "departureDateTimeIso": "2025-06-05 23:55:00", "departureOffsetText": "UTC+3", "departureStation": "TLV", "departureStationCode": "TLV", "departureStationText": "Tel-Aviv", "discount": "0.00", "displayPrice": 43, "duration": "02h 50m", "fare": "43.00", "fareBasisCode": null, "fareSellKey": "MH5BWUNQfn5XNn5BWUNQflNVQlN_fjB_Mn5_WCEx", "flightCode": "W46042", "flightId": "6042", "isFree": "false", "key": "W46042 TLV#20250605T2055~FCO#20250605T2345", "price": "43.00", "priceTag": "wizzair.subscriptions.availability.results.price.tag.premium", "reference": "VzR_NjA0Mn4gfn5UTFZ_MDYvMDUvMjAyNSAyMDo1NX5GQ09_MDYvMDUvMjAyNSAyMzo0NX5_", "stops": "Nonstop", "taxes": "0.00", "totalPrice": "43.00"}]}], "2025-06-06": [{"flightsInbound": [], "flightsOutbound": [{"actionText": "Select", "arrival": "10:00 am", "arrivalDate": "6 June 2025", "arrivalDateIso": null, "arrivalDateTimeIso": "2025-06-06 13:00:00", "arrivalOffsetText": "UTC+3", "arrivalStation": "LCA", "arrivalStationCode": "LCA", "arrivalStationText": "Larnaca", "carrierText": "Operated by W6", "currency": "ILS", "departure": "8:55 am", "departureDate": "6 June 2025", "departureDateIso": "2025-06-06", "departureDateTimeIso": "2025-06-06 11:55:00", "departureOffsetText": "UTC+3", "departureStation": "TLV", "departureStationCode": "TLV", "departureStationText": "Tel-Aviv", "discount": "0.00", "displayPrice": 43, "duration": "01h 05m", "fare": "43.00", "fareBasisCode": null, "fareSellKey": "MH5BWUNQfn5XNn5BWUNQflNVQlN_fjB_Mn5_WCEx", "flightCode": "W64604", "flightId": "4604", "isFree": "false", "key": "W64604 TLV#20250606T0855~LCA#20250606T1000", "price": "43.00", "priceTag": "wizzair.subscriptions.availability.results.price.tag.premium", "reference": "VzZ_NDYwNH4gfn5UTFZ_MDYvMDYvMjAyNSAwODo1NX5MQ0F_MDYvMDYvMjAyNSAxMDowMH5_", "stops": "Nonstop", "taxes": "0.00", "totalPrice": "43.00"}, {"actionText": "Select", "arrival": "1:55 pm", "arrivalDate": "6 June 2025", "arrivalDateIso": null, "arrivalDateTimeIso": "2025-06-06 16:55:00", "arrivalOffsetText": "UTC+3", "arrivalStation": "LCA", "arrivalStationCode": "LCA", "arrivalStationText": "Larnaca", "carrierText": "Operated by W6", "currency": "ILS", "departure": "12:50 pm", "departureDate": "6 June 2025", "departureDateIso": "2025-06-06", "departureDateTimeIso": "2025-06-06 15:50:00", "departureOffsetText": "UTC+3", "departureStation": "TLV", "departureStationCode": "TLV", "departureStationText": "Tel-Aviv", "discount": "0.00", "displayPrice": 43, "duration": "01h 05m", "fare": "43.00", "fareBasisCode": null, "fareSellKey": "MH5BWUNQfn5XNn5BWUNQflNVQlN_fjB_Mn5_WCEx", "flightCode": "W64610", "flightId": "4610", "isFree": "false", "key": "W64610 TLV#20250606T1250~LCA#20250606T1355", "price": "43.00", "priceTag": "wizzair.subscriptions.availability.results.price.tag.premium", "reference": "VzZ_NDYxMH4gfn5UTFZ_MDYvMDYvMjAyNSAxMjo1MH5MQ0F_MDYvMDYvMjAyNSAxMzo1NX5_", "stops": "Nonstop", "taxes": "0.00", "totalPrice": "43.00"}, {"actionText": "Select", "arrival": "10:15 pm", "arrivalDate": "6 June 2025", "arrivalDateIso": null, "arrivalDateTimeIso": "2025-06-07 01:15:00", "arrivalOffsetText": "UTC+3", "arrivalStation": "LCA", "arrivalStationCode": "LCA", "arrivalStationText": "Larnaca", "carrierText": "Operated by W6", "currency": "ILS", "departure": "9:10 pm", "departureDate": "6 June 2025", "departureDateIso": "2025-06-06", "departureDateTimeIso": "2025-06-07 00:10:00", "departureOffsetText": "UTC+3", "departureStation": "TLV", "departureStationCode": "TLV", "departureStationText": "Tel-Aviv", "discount": "0.00", "displayPrice": 43, "duration": "01h 05m", "fare": "43.00", "fareBasisCode": null, "fareSellKey": "MH5BWUNQfn5XNn5BWUNQflNVQlN_fjB_Mn5_WCEx", "flightCode": "W64606", "flightId": "4606", "isFree": "false", "key": "W64606 TLV#20250606T2110~LCA#20250606T2215", "price": "43.00", "priceTag": "wizzair.subscriptions.availability.results.price.tag.premium", "reference": "VzZ_NDYwNn4gfn5UTFZ_MDYvMDYvMjAyNSAyMToxMH5MQ0F_MDYvMDYvMjAyNSAyMjoxNX5_", "stops": "Nonstop", "taxes": "0.00", "totalPrice": "43.00"}]}, {"flightsInbound": [], "flightsOutbound": [{"actionText": "Select", "arrival": "1:15 am", "arrivalDate": "7 June 2025", "arrivalDateIso": null, "arrivalDateTimeIso": "2025-06-07 02:15:00", "arrivalOffsetText": "UTC+1", "arrivalStation": "LGW", "arrivalStationCode": "LGW", "arrivalStationText": "London Gatwick", "carrierText": "Operated by W9", "currency": "ILS", "departure": "9:55 pm", "departureDate": "6 June 2025", "departureDateIso": "2025-06-06", "departureDateTimeIso": "2025-06-07 00:55:00", "departureOffsetText": "UTC+3", "departureStation": "TLV", "departureStationCode": "TLV", "departureStationText": "Tel-Aviv", "discount": "0.00", "displayPrice": 43, "duration": "03h 20m", "fare": "43.00", "fareBasisCode": null, "fareSellKey": "MH5BWUNQfn5XNn5BWUNQflNVQlN_fjB_Mn5_WCEx", "flightCode": "W95804", "flightId": "5804", "isFree": "false", "key": "W95804 TLV#20250606T2155~LGW#20250607T0115", "price": "43.00", "priceTag": "wizzair.subscriptions.availability.results.price.tag.premium", "reference": "Vzl_NTgwNH4gfn5UTFZ_MDYvMDYvMjAyNSAyMTo1NX5MR1d_MDYvMDcvMjAyNSAwMToxNX5_", "stops": "Nonstop", "taxes": "0.00", "totalPrice": "43.00"}]}, {"flightsInbound": [], "flightsOutbound": [{"actionText": "Select", "arrival": "2:30 pm", "arrivalDate": "6 June 2025", "arrivalDateIso": null, "arrivalDateTimeIso": "2025-06-06 16:30:00", "arrivalOffsetText": "UTC+2", "arrivalStation": "FCO", "arrivalStationCode": "FCO", "arrivalStationText": "Rome Fiumicino", "carrierText": "Operated by W4", "currency": "ILS", "departure": "11:40 am", "departureDate": "6 June 2025", "departureDateIso": "2025-06-06", "departureDateTimeIso": "2025-06-06 14:40:00", "departureOffsetText": "UTC+3", "departureStation": "TLV", "departureStationCode": "TLV", "departureStationText": "Tel-Aviv", "discount": "0.00", "displayPrice": 43, "duration": "02h 50m", "fare": "43.00", "fareBasisCode": null, "fareSellKey": "MH5BWUNQfn5XNn5BWUNQflNVQlN_fjB_Mn5_WCEx", "flightCode": "W46042", "flightId": "6042", "isFree": "false", "key": "W46042 TLV#20250606T1140~FCO#20250606T1430", "price": "43.00", "priceTag": "wizzair.subscriptions.availability.results.price.tag.premium", "reference": "VzR_NjA0Mn4gfn5UTFZ_MDYvMDYvMjAyNSAxMTo0MH5GQ09_MDYvMDYvMjAyNSAxNDozMH5_", "stops": "Nonstop", "taxes": "0.00", "totalPrice": "43.00"}, {"actionText": "Select", "arrival": "11:55 pm", "arrivalDate": "6 June 2025", "arrivalDateIso": null, "arrivalDateTimeIso": "2025-06-07 01:55:00", "arrivalOffsetText": "UTC+2", "arrivalStation": "FCO", "arrivalStationCode": "FCO", "arrivalStationText": "Rome Fiumicino", "carrierText": "Operated by W4", "currency": "ILS", "departure": "9:10 pm", "departureDate": "6 June 2025", "departureDateIso": "2025-06-06", "departureDateTimeIso": "2025-06-07 00:10:00", "departureOffsetText": "UTC+3", "departureStation": "TLV", "departureStationCode": "TLV", "departureStationText": "Tel-Aviv", "discount": "0.00", "displayPrice": 43, "duration": "02h 45m", "fare": "43.00", "fareBasisCode": null, "fareSellKey": "MH5BWUNQfn5XNn5BWUNQflNVQlN_fjB_Mn5_WCEx", "flightCode": "W46044", "flightId": "6044", "isFree": "false", "key": "W46044 TLV#20250606T2110~FCO#20250606T2355", "price": "43.00", "priceTag": "wizzair.subscriptions.availability.results.price.tag.premium", "reference": "VzR_NjA0NH4gfn5UTFZ_MDYvMDYvMjAyNSAyMToxMH5GQ09_MDYvMDYvMjAyNSAyMzo1NX5_", "stops": "Nonstop", "taxes": "0.00", "totalPrice": "43.00"}]}, {"flightsInbound": [], "flightsOutbound": [{"actionText": "Select", "arrival": "2:50 pm", "arrivalDate": "6 June 2025", "arrivalDateIso": null, "arrivalDateTimeIso": "2025-06-06 16:50:00", "arrivalOffsetText": "UTC+2", "arrivalStation": "WAW", "arrivalStationCode": "WAW", "arrivalStationText": "Warsaw Chopin", "carrierText": "Operated by W6", "currency": "ILS", "departure": "11:50 am", "departureDate": "6 June 2025", "departureDateIso": "2025-06-06", "departureDateTimeIso": "2025-06-06 14:50:00", "departureOffsetText": "UTC+3", "departureStation": "TLV", "departureStationCode": "TLV", "departureStationText": "Tel-Aviv", "discount": "0.00", "displayPrice": 43, "duration": "03h 00m", "fare": "43.00", "fareBasisCode": null, "fareSellKey": "MH5BWUNQfn5XNn5BWUNQflNVQlN_fjB_MX5_WCEx", "flightCode": "W61560", "flightId": "1560", "isFree": "false", "key": "W61560 TLV#20250606T1150~WAW#20250606T1450", "price": "43.00", "priceTag": "wizzair.subscriptions.availability.results.price.tag.premium", "reference": "VzZ_MTU2MH4gfn5UTFZ_MDYvMDYvMjAyNSAxMTo1MH5XQVd_MDYvMDYvMjAyNSAxNDo1MH5_", "stops": "Nonstop", "taxes": "0.00", "totalPrice": "43.00"}]}], "2025-06-07": [{"flightsInbound": [], "flightsOutbound": [{"actionText": "Select", "arrival": "2:55 pm", "arrivalDate": "7 June 2025", "arrivalDateIso": null, "arrivalDateTimeIso": "2025-06-07 18:55:00", "arrivalOffsetText": "UTC+4", "arrivalStation": "AUH", "arrivalStationCode": "AUH", "arrivalStationText": "Abu Dhabi", "carrierText": "Operated by 5W", "currency": "ILS", "departure": "10:35 am", "departureDate": "7 June 2025", "departureDateIso": "2025-06-07", "departureDateTimeIso": "2025-06-07 13:35:00", "departureOffsetText": "UTC+3", "departureStation": "TLV", "departureStationCode": "TLV", "departureStationText": "Tel-Aviv", "discount": "0.00", "displayPrice": 43, "duration": "04h 20m", "fare": "43.00", "fareBasisCode": null, "fareSellKey": "MH5BWUNQfn5XNn5BWUNQflNVQlN_fjB_Mn5_WCEx", "flightCode": "5W7086", "flightId": "7086", "isFree": "false", "key": "5W7086 TLV#20250607T1035~AUH#20250607T1455", "price": "43.00", "priceTag": "wizzair.subscriptions.availability.results.price.tag.premium", "reference": "NVd_NzA4Nn4gfn5UTFZ_MDYvMDcvMjAyNSAxMDozNX5BVUh_MDYvMDcvMjAyNSAxNDo1NX5_", "stops": "Nonstop", "taxes": "0.00", "totalPrice": "43.00"}]}, {"flightsInbound": [], "flightsOutbound": [{"actionText": "Select", "arrival": "7:50 pm", "arrivalDate": "7 June 2025", "arrivalDateIso": null, "arrivalDateTimeIso": "2025-06-07 22:50:00", "arrivalOffsetText": "UTC+3", "arrivalStation": "OTP", "arrivalStationCode": "OTP", "arrivalStationText": "Bucharest", "carrierText": "Operated by W4", "currency": "ILS", "departure": "4:55 pm", "departureDate": "7 June 2025", "departureDateIso": "2025-06-07", "departureDateTimeIso": "2025-06-07 19:55:00", "departureOffsetText": "UTC+3", "departureStation": "TLV", "departureStationCode": "TLV", "departureStationText": "Tel-Aviv", "discount": "0.00", "displayPrice": 43, "duration": "02h 55m", "fare": "43.00", "fareBasisCode": null, "fareSellKey": "MH5BWUNQfn5XNn5BWUNQflNVQlN_fjB_Mn5_WCEx", "flightCode": "W43264", "flightId": "3264", "isFree": "false", "key": "W43264 TLV#20250607T1655~OTP#20250607T1950", "price": "43.00", "priceTag": "wizzair.subscriptions.availability.results.price.tag.premium", "reference": "VzR_MzI2NH4gfn5UTFZ_MDYvMDcvMjAyNSAxNjo1NX5PVFB_MDYvMDcvMjAyNSAxOTo1MH5_", "stops": "Nonstop", "taxes": "0.00", "totalPrice": "43.00"}]}, {"flightsInbound": [], "flightsOutbound": [{"actionText": "Select", "arrival": "6:55 pm", "arrivalDate": "7 June 2025", "arrivalDateIso": null, "arrivalDateTimeIso": "2025-06-07 20:55:00", "arrivalOffsetText": "UTC+2", "arrivalStation": "BUD", "arrivalStationCode": "BUD", "arrivalStationText": "Budapest", "carrierText": "Operated by W6", "currency": "ILS", "departure": "4:25 pm", "departureDate": "7 June 2025", "departureDateIso": "2025-06-07", "departureDateTimeIso": "2025-06-07 19:25:00", "departureOffsetText": "UTC+3", "departureStation": "TLV", "departureStationCode": "TLV", "departureStationText": "Tel-Aviv", "discount": "0.00", "displayPrice": 43, "duration": "02h 30m", "fare": "43.00", "fareBasisCode": null, "fareSellKey": "MH5BWUNQfn5XNn5BWUNQflNVQlN_fjB_M35_WCEx", "flightCode": "W62328", "flightId": "2328", "isFree": "false", "key": "W62328 TLV#20250607T1625~BUD#20250607T1855", "price": "43.00", "priceTag": "wizzair.subscriptions.availability.results.price.tag.premium", "reference": "VzZ_MjMyOH4gfn5UTFZ_MDYvMDcvMjAyNSAxNjoyNX5CVUR_MDYvMDcvMjAyNSAxODo1NX5_", "stops": "Nonstop", "taxes": "0.00", "totalPrice": "43.00"}]}, {"flightsInbound": [], "flightsOutbound": [{"actionText": "Select", "arrival": "2:45 pm", "arrivalDate": "7 June 2025", "arrivalDateIso": null, "arrivalDateTimeIso": "2025-06-07 17:45:00", "arrivalOffsetText": "UTC+3", "arrivalStation": "LCA", "arrivalStationCode": "LCA", "arrivalStationText": "Larnaca", "carrierText": "Operated by W6", "currency": "ILS", "departure": "1:40 pm", "departureDate": "7 June 2025", "departureDateIso": "2025-06-07", "departureDateTimeIso": "2025-06-07 16:40:00", "departureOffsetText": "UTC+3", "departureStation": "TLV", "departureStationCode": "TLV", "departureStationText": "Tel-Aviv", "discount": "0.00", "displayPrice": 43, "duration": "01h 05m", "fare": "43.00", "fareBasisCode": null, "fareSellKey": "MH5BWUNQfn5XNn5BWUNQflNVQlN_fjB_Mn5_WCEx", "flightCode": "W64608", "flightId": "4608", "isFree": "false", "key": "W64608 TLV#20250607T1340~LCA#20250607T1445", "price": "43.00", "priceTag": "wizzair.subscriptions.availability.results.price.tag.premium", "reference": "VzZ_NDYwOH4gfn5UTFZ_MDYvMDcvMjAyNSAxMzo0MH5MQ0F_MDYvMDcvMjAyNSAxNDo0NX5_", "stops": "Nonstop", "taxes": "0.00", "totalPrice": "43.00"}, {"actionText": "Select", "arrival": "7:40 pm", "arrivalDate": "7 June 2025", "arrivalDateIso": null, "arrivalDateTimeIso": "2025-06-07 22:40:00", "arrivalOffsetText": "UTC+3", "arrivalStation": "LCA", "arrivalStationCode": "LCA", "arrivalStationText": "Larnaca", "carrierText": "Operated by W6", "currency": "ILS", "departure": "6:35 pm", "departureDate": "7 June 2025", "departureDateIso": "2025-06-07", "departureDateTimeIso": "2025-06-07 21:35:00", "departureOffsetText": "UTC+3", "departureStation": "TLV", "departureStationCode": "TLV", "departureStationText": "Tel-Aviv", "discount": "0.00", "displayPrice": 43, "duration": "01h 05m", "fare": "43.00", "fareBasisCode": null, "fareSellKey": "MH5BWUNQfn5XNn5BWUNQflNVQlN_fjB_Mn5_WCEx", "flightCode": "W64606", "flightId": "4606", "isFree": "false", "key": "W64606 TLV#20250607T1835~LCA#20250607T1940", "price": "43.00", "priceTag": "wizzair.subscriptions.availability.results.price.tag.premium", "reference": "VzZ_NDYwNn4gfn5UTFZ_MDYvMDcvMjAyNSAxODozNX5MQ0F_MDYvMDcvMjAyNSAxOTo0MH5_", "stops": "Nonstop", "taxes": "0.00", "totalPrice": "43.00"}]}, {"flightsInbound": [], "flightsOutbound": [{"actionText": "Select", "arrival": "10:50 pm", "arrivalDate": "7 June 2025", "arrivalDateIso": null, "arrivalDateTimeIso": "2025-06-08 00:50:00", "arrivalOffsetText": "UTC+2", "arrivalStation": "VIE", "arrivalStationCode": "VIE", "arrivalStationText": "Vienna", "carrierText": "Operated by W4", "currency": "ILS", "departure": "8:05 pm", "departureDate": "7 June 2025", "departureDateIso": "2025-06-07", "departureDateTimeIso": "2025-06-07 23:05:00", "departureOffsetText": "UTC+3", "departureStation": "TLV", "departureStationCode": "TLV", "departureStationText": "Tel-Aviv", "discount": "0.00", "displayPrice": 43, "duration": "02h 45m", "fare": "43.00", "fareBasisCode": null, "fareSellKey": "MH5BWUNQfn5XNn5BWUNQflNVQlN_fjB_Mn5_WCEx", "flightCode": "W42812", "flightId": "2812", "isFree": "false", "key": "W42812 TLV#20250607T2005~VIE#20250607T2250", "price": "43.00", "priceTag": "wizzair.subscriptions.availability.results.price.tag.premium", "reference": "VzR_MjgxMn4gfn5UTFZ_MDYvMDcvMjAyNSAyMDowNX5WSUV_MDYvMDcvMjAyNSAyMjo1MH5_", "stops": "Nonstop", "taxes": "0.00", "totalPrice": "43.00"}]}, {"flightsInbound": [], "flightsOutbound": [{"actionText": "Select", "arrival": "3:25 pm", "arrivalDate": "7 June 2025", "arrivalDateIso": null, "arrivalDateTimeIso": "2025-06-07 18:25:00", "arrivalOffsetText": "UTC+3", "arrivalStation": "VNO", "arrivalStationCode": "VNO", "arrivalStationText": "Vilnius", "carrierText": "Operated by W6", "currency": "ILS", "departure": "11:05 am", "departureDate": "7 June 2025", "departureDateIso": "2025-06-07", "departureDateTimeIso": "2025-06-07 14:05:00", "departureOffsetText": "UTC+3", "departureStation": "TLV", "departureStationCode": "TLV", "departureStationText": "Tel-Aviv", "discount": "0.00", "displayPrice": 43, "duration": "04h 20m", "fare": "43.00", "fareBasisCode": null, "fareSellKey": "MH5BWUNQfn5XNn5BWUNQflNVQlN_fjB_Mn5_WCEx", "flightCode": "W61966", "flightId": "1966", "isFree": "false", "key": "W61966 TLV#20250607T1105~VNO#20250607T1525", "price": "43.00", "priceTag": "wizzair.subscriptions.availability.results.price.tag.premium", "reference": "VzZ_MTk2Nn4gfn5UTFZ_MDYvMDcvMjAyNSAxMTowNX5WTk9_MDYvMDcvMjAyNSAxNToyNX5_", "stops": "Nonstop", "taxes": "0.00", "totalPrice": "43.00"}]}], "2025-06-08": [{"flightsInbound": [], "flightsOutbound": [{"actionText": "Select", "arrival": "2:55 pm", "arrivalDate": "8 June 2025", "arrivalDateIso": null, "arrivalDateTimeIso": "2025-06-08 18:55:00", "arrivalOffsetText": "UTC+4", "arrivalStation": "AUH", "arrivalStationCode": "AUH", "arrivalStationText": "Abu Dhabi", "carrierText": "Operated by 5W", "currency": "ILS", "departure": "10:35 am", "departureDate": "8 June 2025", "departureDateIso": "2025-06-08", "departureDateTimeIso": "2025-06-08 13:35:00", "departureOffsetText": "UTC+3", "departureStation": "TLV", "departureStationCode": "TLV", "departureStationText": "Tel-Aviv", "discount": "0.00", "displayPrice": 43, "duration": "04h 20m", "fare": "43.00", "fareBasisCode": null, "fareSellKey": "MH5BWUNQfn5XNn5BWUNQflNVQlN_fjB_Mn5_WCEx", "flightCode": "5W7086", "flightId": "7086", "isFree": "false", "key": "5W7086 TLV#20250608T1035~AUH#20250608T1455", "price": "43.00", "priceTag": "wizzair.subscriptions.availability.results.price.tag.premium", "reference": "NVd_NzA4Nn4gfn5UTFZ_MDYvMDgvMjAyNSAxMDozNX5BVUh_MDYvMDgvMjAyNSAxNDo1NX5_", "stops": "Nonstop", "taxes": "0.00", "totalPrice": "43.00"}]}, {"flightsInbound": [], "flightsOutbound": [{"actionText": "Select", "arrival": "10:35 pm", "arrivalDate": "8 June 2025", "arrivalDateIso": null, "arrivalDateTimeIso": "2025-06-09 01:35:00", "arrivalOffsetText": "UTC+3", "arrivalStation": "ATH", "arrivalStationCode": "ATH", "arrivalStationText": "Athens", "carrierText": "Operated by W4", "currency": "ILS", "departure": "8:15 pm", "departureDate": "8 June 2025", "departureDateIso": "2025-06-08", "departureDateTimeIso": "2025-06-08 23:15:00", "departureOffsetText": "UTC+3", "departureStation": "TLV", "departureStationCode": "TLV", "departureStationText": "Tel-Aviv", "discount": "0.00", "displayPrice": 43, "duration": "02h 20m", "fare": "43.00", "fareBasisCode": null, "fareSellKey": "MH5BWUNQfn5XNn5BWUNQflNVQlN_fjB_MX5_WCEx", "flightCode": "W47511", "flightId": "7511", "isFree": "false", "key": "W47511 TLV#20250608T2015~ATH#20250608T2235", "price": "43.00", "priceTag": "wizzair.subscriptions.availability.results.price.tag.premium", "reference": "VzR_NzUxMX4gfn5UTFZ_MDYvMDgvMjAyNSAyMDoxNX5BVEh_MDYvMDgvMjAyNSAyMjozNX5_", "stops": "Nonstop", "taxes": "0.00", "totalPrice": "43.00"}]}, {"flightsInbound": [], "flightsOutbound": [{"actionText": "Select", "arrival": "12:20 pm", "arrivalDate": "8 June 2025", "arrivalDateIso": null, "arrivalDateTimeIso": "2025-06-08 15:20:00", "arrivalOffsetText": "UTC+3", "arrivalStation": "OTP", "arrivalStationCode": "OTP", "arrivalStationText": "Bucharest", "carrierText": "Operated by W4", "currency": "ILS", "departure": "9:25 am", "departureDate": "8 June 2025", "departureDateIso": "2025-06-08", "departureDateTimeIso": "2025-06-08 12:25:00", "departureOffsetText": "UTC+3", "departureStation": "TLV", "departureStationCode": "TLV", "departureStationText": "Tel-Aviv", "discount": "0.00", "displayPrice": 43, "duration": "02h 55m", "fare": "43.00", "fareBasisCode": null, "fareSellKey": "MH5BWUNQfn5XNn5BWUNQflNVQlN_fjB_Mn5_WCEx", "flightCode": "W43258", "flightId": "3258", "isFree": "false", "key": "W43258 TLV#20250608T0925~OTP#20250608T1220", "price": "43.00", "priceTag": "wizzair.subscriptions.availability.results.price.tag.premium", "reference": "VzR_MzI1OH4gfn5UTFZ_MDYvMDgvMjAyNSAwOToyNX5PVFB_MDYvMDgvMjAyNSAxMjoyMH5_", "stops": "Nonstop", "taxes": "0.00", "totalPrice": "43.00"}, {"actionText": "Select", "arrival": "6:05 pm", "arrivalDate": "8 June 2025", "arrivalDateIso": null, "arrivalDateTimeIso": "2025-06-08 21:05:00", "arrivalOffsetText": "UTC+3", "arrivalStation": "OTP", "arrivalStationCode": "OTP", "arrivalStationText": "Bucharest", "carrierText": "Operated by W4", "currency": "ILS", "departure": "3:10 pm", "departureDate": "8 June 2025", "departureDateIso": "2025-06-08", "departureDateTimeIso": "2025-06-08 18:10:00", "departureOffsetText": "UTC+3", "departureStation": "TLV", "departureStationCode": "TLV", "departureStationText": "Tel-Aviv", "discount": "0.00", "displayPrice": 43, "duration": "02h 55m", "fare": "43.00", "fareBasisCode": null, "fareSellKey": "MH5BWUNQfn5XNn5BWUNQflNVQlN_fjB_Mn5_WCEx", "flightCode": "W43264", "flightId": "3264", "isFree": "false", "key": "W43264 TLV#20250608T1510~OTP#20250608T1805", "price": "43.00", "priceTag": "wizzair.subscriptions.availability.results.price.tag.premium", "reference": "VzR_MzI2NH4gfn5UTFZ_MDYvMDgvMjAyNSAxNToxMH5PVFB_MDYvMDgvMjAyNSAxODowNX5_", "stops": "Nonstop", "taxes": "0.00", "totalPrice": "43.00"}]}, {"flightsInbound": [], "flightsOutbound": [{"actionText": "Select", "arrival": "12:10 pm", "arrivalDate": "8 June 2025", "arrivalDateIso": null, "arrivalDateTimeIso": "2025-06-08 15:10:00", "arrivalOffsetText": "UTC+3", "arrivalStation": "IAS", "arrivalStationCode": "IAS", "arrivalStationText": "Iasi", "carrierText": "Operated by W4", "currency": "ILS", "departure": "9:05 am", "departureDate": "8 June 2025", "departureDateIso": "2025-06-08", "departureDateTimeIso": "2025-06-08 12:05:00", "departureOffsetText": "UTC+3", "departureStation": "TLV", "departureStationCode": "TLV", "departureStationText": "Tel-Aviv", "discount": "0.00", "displayPrice": 43, "duration": "03h 05m", "fare": "43.00", "fareBasisCode": null, "fareSellKey": "MH5BWUNQfn5XNn5BWUNQflNVQlN_fjB_Mn5_WCEx", "flightCode": "W43690", "flightId": "3690", "isFree": "false", "key": "W43690 TLV#20250608T0905~IAS#20250608T1210", "price": "43.00", "priceTag": "wizzair.subscriptions.availability.results.price.tag.premium", "reference": "VzR_MzY5MH4gfn5UTFZ_MDYvMDgvMjAyNSAwOTowNX5JQVN_MDYvMDgvMjAyNSAxMjoxMH5_", "stops": "Nonstop", "taxes": "0.00", "totalPrice": "43.00"}]}, {"flightsInbound": [], "flightsOutbound": [{"actionText": "Select", "arrival": "2:00 pm", "arrivalDate": "8 June 2025", "arrivalDateIso": null, "arrivalDateTimeIso": "2025-06-08 16:00:00", "arrivalOffsetText": "UTC+2", "arrivalStation": "KRK", "arrivalStationCode": "KRK", "arrivalStationText": "Krak\\u00f3w", "carrierText": "Operated by W6", "currency": "ILS", "departure": "11:15 am", "departureDate": "8 June 2025", "departureDateIso": "2025-06-08", "departureDateTimeIso": "2025-06-08 14:15:00", "departureOffsetText": "UTC+3", "departureStation": "TLV", "departureStationCode": "TLV", "departureStationText": "Tel-Aviv", "discount": "0.00", "displayPrice": 43, "duration": "02h 45m", "fare": "43.00", "fareBasisCode": null, "fareSellKey": "MH5BWUNQfn5XNn5BWUNQflNVQlN_fjB_MX5_WCEx", "flightCode": "W62098", "flightId": "2098", "isFree": "false", "key": "W62098 TLV#20250608T1115~KRK#20250608T1400", "price": "43.00", "priceTag": "wizzair.subscriptions.availability.results.price.tag.premium", "reference": "VzZ_MjA5OH4gfn5UTFZ_MDYvMDgvMjAyNSAxMToxNX5LUkt_MDYvMDgvMjAyNSAxNDowMH5_", "stops": "Nonstop", "taxes": "0.00", "totalPrice": "43.00"}]}, {"flightsInbound": [], "flightsOutbound": [{"actionText": "Select", "arrival": "2:50 pm", "arrivalDate": "8 June 2025", "arrivalDateIso": null, "arrivalDateTimeIso": "2025-06-08 17:50:00", "arrivalOffsetText": "UTC+3", "arrivalStation": "LCA", "arrivalStationCode": "LCA", "arrivalStationText": "Larnaca", "carrierText": "Operated by W6", "currency": "ILS", "departure": "1:45 pm", "departureDate": "8 June 2025", "departureDateIso": "2025-06-08", "departureDateTimeIso": "2025-06-08 16:45:00", "departureOffsetText": "UTC+3", "departureStation": "TLV", "departureStationCode": "TLV", "departureStationText": "Tel-Aviv", "discount": "0.00", "displayPrice": 43, "duration": "01h 05m", "fare": "43.00", "fareBasisCode": null, "fareSellKey": "MH5BWUNQfn5XNn5BWUNQflNVQlN_fjB_Mn5_WCEx", "flightCode": "W64604", "flightId": "4604", "isFree": "false", "key": "W64604 TLV#20250608T1345~LCA#20250608T1450", "price": "43.00", "priceTag": "wizzair.subscriptions.availability.results.price.tag.premium", "reference": "VzZ_NDYwNH4gfn5UTFZ_MDYvMDgvMjAyNSAxMzo0NX5MQ0F_MDYvMDgvMjAyNSAxNDo1MH5_", "stops": "Nonstop", "taxes": "0.00", "totalPrice": "43.00"}, {"actionText": "Select", "arrival": "10:15 pm", "arrivalDate": "8 June 2025", "arrivalDateIso": null, "arrivalDateTimeIso": "2025-06-09 01:15:00", "arrivalOffsetText": "UTC+3", "arrivalStation": "LCA", "arrivalStationCode": "LCA", "arrivalStationText": "Larnaca", "carrierText": "Operated by W6", "currency": "ILS", "departure": "9:10 pm", "departureDate": "8 June 2025", "departureDateIso": "2025-06-08", "departureDateTimeIso": "2025-06-09 00:10:00", "departureOffsetText": "UTC+3", "departureStation": "TLV", "departureStationCode": "TLV", "departureStationText": "Tel-Aviv", "discount": "0.00", "displayPrice": 43, "duration": "01h 05m", "fare": "43.00", "fareBasisCode": null, "fareSellKey": "MH5BWUNQfn5XNn5BWUNQflNVQlN_fjB_Mn5_WCEx", "flightCode": "W64606", "flightId": "4606", "isFree": "false", "key": "W64606 TLV#20250608T2110~LCA#20250608T2215", "price": "43.00", "priceTag": "wizzair.subscriptions.availability.results.price.tag.premium", "reference": "VzZ_NDYwNn4gfn5UTFZ_MDYvMDgvMjAyNSAyMToxMH5MQ0F_MDYvMDgvMjAyNSAyMjoxNX5_", "stops": "Nonstop", "taxes": "0.00", "totalPrice": "43.00"}]}, {"flightsInbound": [], "flightsOutbound": [{"actionText": "Select", "arrival": "10:15 am", "arrivalDate": "8 June 2025", "arrivalDateIso": null, "arrivalDateTimeIso": "2025-06-08 13:15:00", "arrivalOffsetText": "UTC+3", "arrivalStation": "RHO", "arrivalStationCode": "RHO", "arrivalStationText": "Rhodes", "carrierText": "Operated by W6", "currency": "ILS", "departure": "8:40 am", "departureDate": "8 June 2025", "departureDateIso": "2025-06-08", "departureDateTimeIso": "2025-06-08 11:40:00", "departureOffsetText": "UTC+3", "departureStation": "TLV", "departureStationCode": "TLV", "departureStationText": "Tel-Aviv", "discount": "0.00", "displayPrice": 43, "duration": "01h 35m", "fare": "43.00", "fareBasisCode": null, "fareSellKey": "MH5BWUNQfn5XNn5BWUNQflNVQlN_fjB_MX5_WCEx", "flightCode": "W67501", "flightId": "7501", "isFree": "false", "key": "W67501 TLV#20250608T0840~RHO#20250608T1015", "price": "43.00", "priceTag": "wizzair.subscriptions.availability.results.price.tag.premium", "reference": "VzZ_NzUwMX4gfn5UTFZ_MDYvMDgvMjAyNSAwODo0MH5SSE9_MDYvMDgvMjAyNSAxMDoxNX5_", "stops": "Nonstop", "taxes": "0.00", "totalPrice": "43.00"}]}, {"flightsInbound": [], "flightsOutbound": [{"actionText": "Select", "arrival": "2:50 pm", "arrivalDate": "8 June 2025", "arrivalDateIso": null, "arrivalDateTimeIso": "2025-06-08 16:50:00", "arrivalOffsetText": "UTC+2", "arrivalStation": "WAW", "arrivalStationCode": "WAW", "arrivalStationText": "Warsaw Chopin", "carrierText": "Operated by W6", "currency": "ILS", "departure": "11:50 am", "departureDate": "8 June 2025", "departureDateIso": "2025-06-08", "departureDateTimeIso": "2025-06-08 14:50:00", "departureOffsetText": "UTC+3", "departureStation": "TLV", "departureStationCode": "TLV", "departureStationText": "Tel-Aviv", "discount": "0.00", "displayPrice": 43, "duration": "03h 00m", "fare": "43.00", "fareBasisCode": null, "fareSellKey": "MH5BWUNQfn5XNn5BWUNQflNVQlN_fjB_MX5_WCEx", "flightCode": "W61560", "flightId": "1560", "isFree": "false", "key": "W61560 TLV#20250608T1150~WAW#20250608T1450", "price": "43.00", "priceTag": "wizzair.subscriptions.availability.results.price.tag.premium", "reference": "VzZ_MTU2MH4gfn5UTFZ_MDYvMDgvMjAyNSAxMTo1MH5XQVd_MDYvMDgvMjAyNSAxNDo1MH5_", "stops": "Nonstop", "taxes": "0.00", "totalPrice": "43.00"}]}]}')
    # time.sleep(7)
    print("after getting al options")
    # breakpoint()
    for date, options_by_date in all_options.items():
        options_by_date = [opt for opt in options_by_date if not opt.get("message")]
        for option in options_by_date:
            if "flightsOutbound" not in option:
                print(f"failed to find flightsOutbound in {option} THIS SHOULD NEVEL HAPPEN!")
                time.sleep(300)
                continue
            for flight in option["flightsOutbound"]:
                try:
                    flight_to = airports[flight["arrivalStationCode"]]
                    get_weather_by_city(flight_to["city"])
                except Exception as e:
                    print(f'failed with {flight["arrivalStationCode"]} and get weather for {flight_to["city"]} with err {e}')
    time.sleep(3)
    # weather_by_city = {'Milano': {'text': 'Forecast: 2025-06-05: 19°C, Patchy rain nearby || 2025-06-06: 21°C, Patchy rain nearby || 2025-06-07: 22°C, Partly Cloudy  || ', 'style': [{'date': '2025-06-05', 'description': 'Patchy rain nearby', 'color': '#cbcb4b', 'avgTemp': '19°C'}, {'date': '2025-06-06', 'description': 'Patchy rain nearby', 'color': '#cbcb4b', 'avgTemp': '21°C'}, {'date': '2025-06-07', 'description': 'Partly Cloudy ', 'color': '#cbcb4b', 'avgTemp': '22°C'}]}, 'Rome': {'text': 'Forecast: 2025-06-05: 23°C, Patchy rain nearby || 2025-06-06: 23°C, Sunny || 2025-06-07: 24°C, Sunny || ', 'style': [{'date': '2025-06-05', 'description': 'Patchy rain nearby', 'color': '#cbcb4b', 'avgTemp': '23°C'}, {'date': '2025-06-06', 'description': 'Sunny', 'color': 'green', 'avgTemp': '23°C'}, {'date': '2025-06-07', 'description': 'Sunny', 'color': 'green', 'avgTemp': '24°C'}]}, 'Larnaca': {'text': 'Forecast: 2025-06-05: 24°C, Sunny || 2025-06-06: 24°C, Sunny || 2025-06-07: 24°C, Sunny || ', 'style': [{'date': '2025-06-05', 'description': 'Sunny', 'color': 'green', 'avgTemp': '24°C'}, {'date': '2025-06-06', 'description': 'Sunny', 'color': 'green', 'avgTemp': '24°C'}, {'date': '2025-06-07', 'description': 'Sunny', 'color': 'green', 'avgTemp': '24°C'}]}, 'London': {'text': 'Forecast: 2025-06-05: 13°C, Light rain shower || 2025-06-06: 14°C, Patchy rain nearby || 2025-06-07: 14°C, Patchy light rain || ', 'style': [{'date': '2025-06-05', 'description': 'Light rain shower', 'color': 'red', 'avgTemp': '13°C'}, {'date': '2025-06-06', 'description': 'Patchy rain nearby', 'color': '#cbcb4b', 'avgTemp': '14°C'}, {'date': '2025-06-07', 'description': 'Patchy light rain', 'color': 'red', 'avgTemp': '14°C'}]}, 'Warsaw': {'text': 'Forecast: 2025-06-05: 21°C, Patchy rain nearby || 2025-06-06: 21°C, Patchy rain nearby || 2025-06-07: 19°C, Patchy rain nearby || ', 'style': [{'date': '2025-06-05', 'description': 'Patchy rain nearby', 'color': '#cbcb4b', 'avgTemp': '21°C'}, {'date': '2025-06-06', 'description': 'Patchy rain nearby', 'color': '#cbcb4b', 'avgTemp': '21°C'}, {'date': '2025-06-07', 'description': 'Patchy rain nearby', 'color': '#cbcb4b', 'avgTemp': '19°C'}]}, 'Abu Dhabi': {'text': 'Forecast: 2025-06-05: 30°C, Sunny || 2025-06-06: 30°C, Sunny || 2025-06-07: 30°C, Sunny || ', 'style': [{'date': '2025-06-05', 'description': 'Sunny', 'color': 'green', 'avgTemp': '30°C'}, {'date': '2025-06-06', 'description': 'Sunny', 'color': 'green', 'avgTemp': '30°C'}, {'date': '2025-06-07', 'description': 'Sunny', 'color': 'green', 'avgTemp': '30°C'}]}, 'Bucharest': {'text': 'Forecast: 2025-06-05: 25°C, Sunny || 2025-06-06: 25°C, Sunny || 2025-06-07: 23°C, Sunny || ', 'style': [{'date': '2025-06-05', 'description': 'Sunny', 'color': 'green', 'avgTemp': '25°C'}, {'date': '2025-06-06', 'description': 'Sunny', 'color': 'green', 'avgTemp': '25°C'}, {'date': '2025-06-07', 'description': 'Sunny', 'color': 'green', 'avgTemp': '23°C'}]}, 'Budapest': {'text': 'Forecast: 2025-06-05: 25°C, Sunny || 2025-06-06: 25°C, Sunny || 2025-06-07: 26°C, Sunny || ', 'style': [{'date': '2025-06-05', 'description': 'Sunny', 'color': 'green', 'avgTemp': '25°C'}, {'date': '2025-06-06', 'description': 'Sunny', 'color': 'green', 'avgTemp': '25°C'}, {'date': '2025-06-07', 'description': 'Sunny', 'color': 'green', 'avgTemp': '26°C'}]}, 'Vienna': {'text': 'Forecast: 2025-06-05: 22°C, Partly Cloudy  || 2025-06-06: 22°C, Partly Cloudy  || 2025-06-07: 20°C, Cloudy  || ', 'style': [{'date': '2025-06-05', 'description': 'Partly Cloudy ', 'color': '#cbcb4b', 'avgTemp': '22°C'}, {'date': '2025-06-06', 'description': 'Partly Cloudy ', 'color': '#cbcb4b', 'avgTemp': '22°C'}, {'date': '2025-06-07', 'description': 'Cloudy ', 'color': '#cbcb4b', 'avgTemp': '20°C'}]}, 'Vilnius': {'text': 'Forecast: 2025-06-05: 18°C, Moderate or heavy rain with thunder || 2025-06-06: 18°C, Light rain shower || 2025-06-07: 17°C, Partly Cloudy  || ', 'style': [{'date': '2025-06-05', 'description': 'Moderate or heavy rain with thunder', 'color': 'red', 'avgTemp': '18°C'}, {'date': '2025-06-06', 'description': 'Light rain shower', 'color': 'red', 'avgTemp': '18°C'}, {'date': '2025-06-07', 'description': 'Partly Cloudy ', 'color': '#cbcb4b', 'avgTemp': '17°C'}]}, 'Athens': {'text': 'Forecast: 2025-06-05: 24°C, Cloudy  || 2025-06-06: 26°C, Partly Cloudy  || 2025-06-07: 27°C, Partly Cloudy  || ', 'style': [{'date': '2025-06-05', 'description': 'Cloudy ', 'color': '#cbcb4b', 'avgTemp': '24°C'}, {'date': '2025-06-06', 'description': 'Partly Cloudy ', 'color': '#cbcb4b', 'avgTemp': '26°C'}, {'date': '2025-06-07', 'description': 'Partly Cloudy ', 'color': '#cbcb4b', 'avgTemp': '27°C'}]}, 'Iasi': {'text': 'Forecast: 2025-06-05: 23°C, Sunny || 2025-06-06: 23°C, Sunny || 2025-06-07: 23°C, Sunny || ', 'style': [{'date': '2025-06-05', 'description': 'Sunny', 'color': 'green', 'avgTemp': '23°C'}, {'date': '2025-06-06', 'description': 'Sunny', 'color': 'green', 'avgTemp': '23°C'}, {'date': '2025-06-07', 'description': 'Sunny', 'color': 'green', 'avgTemp': '23°C'}]}, 'Krakow': {'text': 'Forecast: 2025-06-05: 20°C, Partly Cloudy  || 2025-06-06: 20°C, Sunny || 2025-06-07: 18°C, Partly Cloudy  || ', 'style': [{'date': '2025-06-05', 'description': 'Partly Cloudy ', 'color': '#cbcb4b', 'avgTemp': '20°C'}, {'date': '2025-06-06', 'description': 'Sunny', 'color': 'green', 'avgTemp': '20°C'}, {'date': '2025-06-07', 'description': 'Partly Cloudy ', 'color': '#cbcb4b', 'avgTemp': '18°C'}]}, 'Rhodes': {'text': 'Forecast: 2025-06-05: 15°C, Patchy rain nearby || 2025-06-06: 15°C, Patchy rain nearby || 2025-06-07: 16°C, Sunny || ', 'style': [{'date': '2025-06-05', 'description': 'Patchy rain nearby', 'color': '#cbcb4b', 'avgTemp': '15°C'}, {'date': '2025-06-06', 'description': 'Patchy rain nearby', 'color': '#cbcb4b', 'avgTemp': '15°C'}, {'date': '2025-06-07', 'description': 'Sunny', 'color': 'green', 'avgTemp': '16°C'}]}}

    print("after getting all weather data")
    # breakpoint()
    for cur_date, options_by_date in all_options.items():
        options_by_date = [opt for opt in options_by_date if not opt.get("message")]
        if not options_by_date:
            continue  # skip date with no options

        print()
        print(f"Running for date {cur_date}")

        for option in options_by_date:
            first_flight = option["flightsOutbound"][0]
            flight_from = airports[first_flight["departureStationCode"]]
            flight_to = airports[first_flight["arrivalStationCode"]]

            print(f"flight from {flight_from['city']} -> {flight_to['city']}, {flight_to['state']}")

            try:
                weather = get_weather_by_city(flight_to["city"])
                print(weather["text"])
                for style in weather["style"]:
                    print(style)  # Optional: Format this if needed
            except Exception as e:
                print("failed for", weather_by_city, flight_to["city"], e)
                continue

            for flight in option["flightsOutbound"]:
                print(f"Available Flight: {flight['departureDateTimeIso']}-3hours")



    ################# Handle old index.html ##############
    # Step 1: Check if index.html exists
    if os.path.isfile("index.html"):
        # Step 2: Generate new filename with date and time
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        new_filename = f"backup_{timestamp}.html"
        
        # Rename the file
        os.rename("index.html", new_filename)
        print(f"Renamed to {new_filename}")
        
        # Step 3: Add the new file to git
        try:
            subprocess.run(["git", "add", new_filename], check=True)
            print(f"Added {new_filename} to git")
        except subprocess.CalledProcessError as e:
            print(f"Error adding to git: {e}")
    else:
        print("index.html does not exist.")

    


    ############## Handle new index.html ##############
    # Open the original file in read mode
    with open("template.html", "r", encoding="utf-8") as file:
        content = file.read()

    # Replace the words
    content = content.replace("__all_flights__", json.dumps(all_options))
    content = content.replace("__all_weather__", json.dumps(weather_by_city))
    new_filename = "index.html"
    # Write the modified content to a new file
    with open(new_filename, "w", encoding="utf-8") as new_file:
        new_file.write(content)

    try:
        subprocess.run(["git", "add", new_filename], check=True)
        print(f"Added {new_filename} to git")
    except subprocess.CalledProcessError as e:
        print(f"Error adding to git: {e}")

    ############### Push changes to git and update site ###########
    try:
        subprocess.run(["git", "commit", "-m", "auto site update using script"], check=True)
        subprocess.run(["git", "push"], check=True)
        print(f"Pushed new site to git")
    except subprocess.CalledProcessError as e:
        print(f"Error adding/pushing to git: {e}")


generate_page()