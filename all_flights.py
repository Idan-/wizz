import requests
import time
import json
import os
import datetime
import subprocess
from data import airports, CVO
from selenium_driver import get_driver, get_flight_data
import argparse
import shutil
from logger import logger
from concurrent.futures import ThreadPoolExecutor, as_completed





DEBUG = False

# will be filled later in the script according to the available cities
weather_by_city = {}

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
        return "yellow"
    else:
        return "red"


def get_weather_by_city(city):
    if city in weather_by_city:
        return weather_by_city[city]
    
    city = city.replace(" ", "+").lower()

    url = f"https://wttr.in/{city}?format=j1"
    logger.info(f"trying url {url}")
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
        logger.exception(f"Error for city {city} response status: {response.status_code} || Response content: {response.text}")
        return None


#/*********************************
#***** CHANGEABLE PARAMETERS ******
#*********************************/
# ARRIVAL_TYPE = "ALL"          # "ALL" | "SPECIFICS" | "COUNTRY_CODE"
# FROM = "TLV"                  # The airport code we're taking off from
# FROM = "LCA"                  # The airport code we're taking off from
# DATES = "ALL" # ["2025-06-05"]        # "ALL" | ["2025-01-31"]
# MAX_CALL_COUNT_PER_DATE = 999 # maximum calls to the API in a single run
all_options = {}              # object to store all the results 

def generate_page(ARRIVAL_TYPE="ALL", FROM="TLV", DATES="ALL", MAX_CALL_COUNT_PER_DATE=999):
    global weather_by_city # as we set this variable for debug we must state it's global
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

    if not DEBUG:
        counter = 0
        for d in DATES:
            if counter != 0:
                time.sleep(10) # sleeping 60 seconds to avoid 429, notice using regular browser don't have this limitation, maybe should be fixed in another way.
            driver = get_driver()
            all_options[d] = []
            for opt in arrival_options:
                counter += 1
                if counter > MAX_CALL_COUNT_PER_DATE:
                    logger.info("STOPPED CALLS DUE TO MAX_CALL_COUNT_PER_DATE")
                    break
                TO = opt["id"]
                try:
                    logger.info(f"get flight data with {FROM=} {TO=} {d}")
                    data_for_date = get_flight_data(driver, FROM, TO, d)
                    logger.info(f"result {FROM=} {TO=} {d} {data_for_date=}")
                    if "code" in data_for_date:
                        if data_for_date["code"] == "error.availability":
                            continue
                        else:
                            raise Exception(f"failed due to {data_for_date}")
                    if not data_for_date:
                        raise Exception(f"weird failed check it")
                    all_options[d].append(data_for_date)
                except Exception as e:
                    logger.exception(f"failed to get data {FROM} {TO} {d}")
                    continue
            driver.close()
    else: # If debug
        all_options = json.loads('{"2025-06-05": [{"flightsInbound": [], "flightsOutbound": [{"actionText": "Select", "arrival": "10:50 pm", "arrivalDate": "5 June 2025", "arrivalDateIso": null, "arrivalDateTimeIso": "2025-06-06 00:50:00", "arrivalOffsetText": "UTC+2", "arrivalStation": "MXP", "arrivalStationCode": "MXP", "arrivalStationText": "Milan Malpensa", "carrierText": "Operated by W4", "currency": "ILS", "departure": "7:35 pm", "departureDate": "5 June 2025", "departureDateIso": "2025-06-05", "departureDateTimeIso": "2025-06-05 22:35:00", "departureOffsetText": "UTC+3", "departureStation": "TLV", "departureStationCode": "TLV", "departureStationText": "Tel-Aviv", "discount": "0.00", "displayPrice": 43, "duration": "03h 15m", "fare": "43.00", "fareBasisCode": null, "fareSellKey": "MH5BWUNQfn5XNn5BWUNQflNVQlN_fjB_Mn5_WCEx", "flightCode": "W46404", "flightId": "6404", "isFree": "false", "key": "W46404 TLV#20250605T1935~MXP#20250605T2250", "price": "43.00", "priceTag": "wizzair.subscriptions.availability.results.price.tag.premium", "reference": "VzR_NjQwNH4gfn5UTFZ_MDYvMDUvMjAyNSAxOTozNX5NWFB_MDYvMDUvMjAyNSAyMjo1MH5_", "stops": "Nonstop", "taxes": "0.00", "totalPrice": "43.00"}]}, {"flightsInbound": [], "flightsOutbound": [{"actionText": "Select", "arrival": "11:45 pm", "arrivalDate": "5 June 2025", "arrivalDateIso": null, "arrivalDateTimeIso": "2025-06-06 01:45:00", "arrivalOffsetText": "UTC+2", "arrivalStation": "FCO", "arrivalStationCode": "FCO", "arrivalStationText": "Rome Fiumicino", "carrierText": "Operated by W4", "currency": "ILS", "departure": "8:55 pm", "departureDate": "5 June 2025", "departureDateIso": "2025-06-05", "departureDateTimeIso": "2025-06-05 23:55:00", "departureOffsetText": "UTC+3", "departureStation": "TLV", "departureStationCode": "TLV", "departureStationText": "Tel-Aviv", "discount": "0.00", "displayPrice": 43, "duration": "02h 50m", "fare": "43.00", "fareBasisCode": null, "fareSellKey": "MH5BWUNQfn5XNn5BWUNQflNVQlN_fjB_Mn5_WCEx", "flightCode": "W46042", "flightId": "6042", "isFree": "false", "key": "W46042 TLV#20250605T2055~FCO#20250605T2345", "price": "43.00", "priceTag": "wizzair.subscriptions.availability.results.price.tag.premium", "reference": "VzR_NjA0Mn4gfn5UTFZ_MDYvMDUvMjAyNSAyMDo1NX5GQ09_MDYvMDUvMjAyNSAyMzo0NX5_", "stops": "Nonstop", "taxes": "0.00", "totalPrice": "43.00"}]}], "2025-06-06": [{"flightsInbound": [], "flightsOutbound": [{"actionText": "Select", "arrival": "10:00 am", "arrivalDate": "6 June 2025", "arrivalDateIso": null, "arrivalDateTimeIso": "2025-06-06 13:00:00", "arrivalOffsetText": "UTC+3", "arrivalStation": "LCA", "arrivalStationCode": "LCA", "arrivalStationText": "Larnaca", "carrierText": "Operated by W6", "currency": "ILS", "departure": "8:55 am", "departureDate": "6 June 2025", "departureDateIso": "2025-06-06", "departureDateTimeIso": "2025-06-06 11:55:00", "departureOffsetText": "UTC+3", "departureStation": "TLV", "departureStationCode": "TLV", "departureStationText": "Tel-Aviv", "discount": "0.00", "displayPrice": 43, "duration": "01h 05m", "fare": "43.00", "fareBasisCode": null, "fareSellKey": "MH5BWUNQfn5XNn5BWUNQflNVQlN_fjB_Mn5_WCEx", "flightCode": "W64604", "flightId": "4604", "isFree": "false", "key": "W64604 TLV#20250606T0855~LCA#20250606T1000", "price": "43.00", "priceTag": "wizzair.subscriptions.availability.results.price.tag.premium", "reference": "VzZ_NDYwNH4gfn5UTFZ_MDYvMDYvMjAyNSAwODo1NX5MQ0F_MDYvMDYvMjAyNSAxMDowMH5_", "stops": "Nonstop", "taxes": "0.00", "totalPrice": "43.00"}, {"actionText": "Select", "arrival": "1:55 pm", "arrivalDate": "6 June 2025", "arrivalDateIso": null, "arrivalDateTimeIso": "2025-06-06 16:55:00", "arrivalOffsetText": "UTC+3", "arrivalStation": "LCA", "arrivalStationCode": "LCA", "arrivalStationText": "Larnaca", "carrierText": "Operated by W6", "currency": "ILS", "departure": "12:50 pm", "departureDate": "6 June 2025", "departureDateIso": "2025-06-06", "departureDateTimeIso": "2025-06-06 15:50:00", "departureOffsetText": "UTC+3", "departureStation": "TLV", "departureStationCode": "TLV", "departureStationText": "Tel-Aviv", "discount": "0.00", "displayPrice": 43, "duration": "01h 05m", "fare": "43.00", "fareBasisCode": null, "fareSellKey": "MH5BWUNQfn5XNn5BWUNQflNVQlN_fjB_Mn5_WCEx", "flightCode": "W64610", "flightId": "4610", "isFree": "false", "key": "W64610 TLV#20250606T1250~LCA#20250606T1355", "price": "43.00", "priceTag": "wizzair.subscriptions.availability.results.price.tag.premium", "reference": "VzZ_NDYxMH4gfn5UTFZ_MDYvMDYvMjAyNSAxMjo1MH5MQ0F_MDYvMDYvMjAyNSAxMzo1NX5_", "stops": "Nonstop", "taxes": "0.00", "totalPrice": "43.00"}, {"actionText": "Select", "arrival": "10:15 pm", "arrivalDate": "6 June 2025", "arrivalDateIso": null, "arrivalDateTimeIso": "2025-06-07 01:15:00", "arrivalOffsetText": "UTC+3", "arrivalStation": "LCA", "arrivalStationCode": "LCA", "arrivalStationText": "Larnaca", "carrierText": "Operated by W6", "currency": "ILS", "departure": "9:10 pm", "departureDate": "6 June 2025", "departureDateIso": "2025-06-06", "departureDateTimeIso": "2025-06-07 00:10:00", "departureOffsetText": "UTC+3", "departureStation": "TLV", "departureStationCode": "TLV", "departureStationText": "Tel-Aviv", "discount": "0.00", "displayPrice": 43, "duration": "01h 05m", "fare": "43.00", "fareBasisCode": null, "fareSellKey": "MH5BWUNQfn5XNn5BWUNQflNVQlN_fjB_Mn5_WCEx", "flightCode": "W64606", "flightId": "4606", "isFree": "false", "key": "W64606 TLV#20250606T2110~LCA#20250606T2215", "price": "43.00", "priceTag": "wizzair.subscriptions.availability.results.price.tag.premium", "reference": "VzZ_NDYwNn4gfn5UTFZ_MDYvMDYvMjAyNSAyMToxMH5MQ0F_MDYvMDYvMjAyNSAyMjoxNX5_", "stops": "Nonstop", "taxes": "0.00", "totalPrice": "43.00"}]}, {"flightsInbound": [], "flightsOutbound": [{"actionText": "Select", "arrival": "1:15 am", "arrivalDate": "7 June 2025", "arrivalDateIso": null, "arrivalDateTimeIso": "2025-06-07 02:15:00", "arrivalOffsetText": "UTC+1", "arrivalStation": "LGW", "arrivalStationCode": "LGW", "arrivalStationText": "London Gatwick", "carrierText": "Operated by W9", "currency": "ILS", "departure": "9:55 pm", "departureDate": "6 June 2025", "departureDateIso": "2025-06-06", "departureDateTimeIso": "2025-06-07 00:55:00", "departureOffsetText": "UTC+3", "departureStation": "TLV", "departureStationCode": "TLV", "departureStationText": "Tel-Aviv", "discount": "0.00", "displayPrice": 43, "duration": "03h 20m", "fare": "43.00", "fareBasisCode": null, "fareSellKey": "MH5BWUNQfn5XNn5BWUNQflNVQlN_fjB_Mn5_WCEx", "flightCode": "W95804", "flightId": "5804", "isFree": "false", "key": "W95804 TLV#20250606T2155~LGW#20250607T0115", "price": "43.00", "priceTag": "wizzair.subscriptions.availability.results.price.tag.premium", "reference": "Vzl_NTgwNH4gfn5UTFZ_MDYvMDYvMjAyNSAyMTo1NX5MR1d_MDYvMDcvMjAyNSAwMToxNX5_", "stops": "Nonstop", "taxes": "0.00", "totalPrice": "43.00"}]}, {"flightsInbound": [], "flightsOutbound": [{"actionText": "Select", "arrival": "2:30 pm", "arrivalDate": "6 June 2025", "arrivalDateIso": null, "arrivalDateTimeIso": "2025-06-06 16:30:00", "arrivalOffsetText": "UTC+2", "arrivalStation": "FCO", "arrivalStationCode": "FCO", "arrivalStationText": "Rome Fiumicino", "carrierText": "Operated by W4", "currency": "ILS", "departure": "11:40 am", "departureDate": "6 June 2025", "departureDateIso": "2025-06-06", "departureDateTimeIso": "2025-06-06 14:40:00", "departureOffsetText": "UTC+3", "departureStation": "TLV", "departureStationCode": "TLV", "departureStationText": "Tel-Aviv", "discount": "0.00", "displayPrice": 43, "duration": "02h 50m", "fare": "43.00", "fareBasisCode": null, "fareSellKey": "MH5BWUNQfn5XNn5BWUNQflNVQlN_fjB_Mn5_WCEx", "flightCode": "W46042", "flightId": "6042", "isFree": "false", "key": "W46042 TLV#20250606T1140~FCO#20250606T1430", "price": "43.00", "priceTag": "wizzair.subscriptions.availability.results.price.tag.premium", "reference": "VzR_NjA0Mn4gfn5UTFZ_MDYvMDYvMjAyNSAxMTo0MH5GQ09_MDYvMDYvMjAyNSAxNDozMH5_", "stops": "Nonstop", "taxes": "0.00", "totalPrice": "43.00"}, {"actionText": "Select", "arrival": "11:55 pm", "arrivalDate": "6 June 2025", "arrivalDateIso": null, "arrivalDateTimeIso": "2025-06-07 01:55:00", "arrivalOffsetText": "UTC+2", "arrivalStation": "FCO", "arrivalStationCode": "FCO", "arrivalStationText": "Rome Fiumicino", "carrierText": "Operated by W4", "currency": "ILS", "departure": "9:10 pm", "departureDate": "6 June 2025", "departureDateIso": "2025-06-06", "departureDateTimeIso": "2025-06-07 00:10:00", "departureOffsetText": "UTC+3", "departureStation": "TLV", "departureStationCode": "TLV", "departureStationText": "Tel-Aviv", "discount": "0.00", "displayPrice": 43, "duration": "02h 45m", "fare": "43.00", "fareBasisCode": null, "fareSellKey": "MH5BWUNQfn5XNn5BWUNQflNVQlN_fjB_Mn5_WCEx", "flightCode": "W46044", "flightId": "6044", "isFree": "false", "key": "W46044 TLV#20250606T2110~FCO#20250606T2355", "price": "43.00", "priceTag": "wizzair.subscriptions.availability.results.price.tag.premium", "reference": "VzR_NjA0NH4gfn5UTFZ_MDYvMDYvMjAyNSAyMToxMH5GQ09_MDYvMDYvMjAyNSAyMzo1NX5_", "stops": "Nonstop", "taxes": "0.00", "totalPrice": "43.00"}]}, {"flightsInbound": [], "flightsOutbound": [{"actionText": "Select", "arrival": "2:50 pm", "arrivalDate": "6 June 2025", "arrivalDateIso": null, "arrivalDateTimeIso": "2025-06-06 16:50:00", "arrivalOffsetText": "UTC+2", "arrivalStation": "WAW", "arrivalStationCode": "WAW", "arrivalStationText": "Warsaw Chopin", "carrierText": "Operated by W6", "currency": "ILS", "departure": "11:50 am", "departureDate": "6 June 2025", "departureDateIso": "2025-06-06", "departureDateTimeIso": "2025-06-06 14:50:00", "departureOffsetText": "UTC+3", "departureStation": "TLV", "departureStationCode": "TLV", "departureStationText": "Tel-Aviv", "discount": "0.00", "displayPrice": 43, "duration": "03h 00m", "fare": "43.00", "fareBasisCode": null, "fareSellKey": "MH5BWUNQfn5XNn5BWUNQflNVQlN_fjB_MX5_WCEx", "flightCode": "W61560", "flightId": "1560", "isFree": "false", "key": "W61560 TLV#20250606T1150~WAW#20250606T1450", "price": "43.00", "priceTag": "wizzair.subscriptions.availability.results.price.tag.premium", "reference": "VzZ_MTU2MH4gfn5UTFZ_MDYvMDYvMjAyNSAxMTo1MH5XQVd_MDYvMDYvMjAyNSAxNDo1MH5_", "stops": "Nonstop", "taxes": "0.00", "totalPrice": "43.00"}]}], "2025-06-07": [{"flightsInbound": [], "flightsOutbound": [{"actionText": "Select", "arrival": "2:55 pm", "arrivalDate": "7 June 2025", "arrivalDateIso": null, "arrivalDateTimeIso": "2025-06-07 18:55:00", "arrivalOffsetText": "UTC+4", "arrivalStation": "AUH", "arrivalStationCode": "AUH", "arrivalStationText": "Abu Dhabi", "carrierText": "Operated by 5W", "currency": "ILS", "departure": "10:35 am", "departureDate": "7 June 2025", "departureDateIso": "2025-06-07", "departureDateTimeIso": "2025-06-07 13:35:00", "departureOffsetText": "UTC+3", "departureStation": "TLV", "departureStationCode": "TLV", "departureStationText": "Tel-Aviv", "discount": "0.00", "displayPrice": 43, "duration": "04h 20m", "fare": "43.00", "fareBasisCode": null, "fareSellKey": "MH5BWUNQfn5XNn5BWUNQflNVQlN_fjB_Mn5_WCEx", "flightCode": "5W7086", "flightId": "7086", "isFree": "false", "key": "5W7086 TLV#20250607T1035~AUH#20250607T1455", "price": "43.00", "priceTag": "wizzair.subscriptions.availability.results.price.tag.premium", "reference": "NVd_NzA4Nn4gfn5UTFZ_MDYvMDcvMjAyNSAxMDozNX5BVUh_MDYvMDcvMjAyNSAxNDo1NX5_", "stops": "Nonstop", "taxes": "0.00", "totalPrice": "43.00"}]}, {"flightsInbound": [], "flightsOutbound": [{"actionText": "Select", "arrival": "7:50 pm", "arrivalDate": "7 June 2025", "arrivalDateIso": null, "arrivalDateTimeIso": "2025-06-07 22:50:00", "arrivalOffsetText": "UTC+3", "arrivalStation": "OTP", "arrivalStationCode": "OTP", "arrivalStationText": "Bucharest", "carrierText": "Operated by W4", "currency": "ILS", "departure": "4:55 pm", "departureDate": "7 June 2025", "departureDateIso": "2025-06-07", "departureDateTimeIso": "2025-06-07 19:55:00", "departureOffsetText": "UTC+3", "departureStation": "TLV", "departureStationCode": "TLV", "departureStationText": "Tel-Aviv", "discount": "0.00", "displayPrice": 43, "duration": "02h 55m", "fare": "43.00", "fareBasisCode": null, "fareSellKey": "MH5BWUNQfn5XNn5BWUNQflNVQlN_fjB_Mn5_WCEx", "flightCode": "W43264", "flightId": "3264", "isFree": "false", "key": "W43264 TLV#20250607T1655~OTP#20250607T1950", "price": "43.00", "priceTag": "wizzair.subscriptions.availability.results.price.tag.premium", "reference": "VzR_MzI2NH4gfn5UTFZ_MDYvMDcvMjAyNSAxNjo1NX5PVFB_MDYvMDcvMjAyNSAxOTo1MH5_", "stops": "Nonstop", "taxes": "0.00", "totalPrice": "43.00"}]}, {"flightsInbound": [], "flightsOutbound": [{"actionText": "Select", "arrival": "6:55 pm", "arrivalDate": "7 June 2025", "arrivalDateIso": null, "arrivalDateTimeIso": "2025-06-07 20:55:00", "arrivalOffsetText": "UTC+2", "arrivalStation": "BUD", "arrivalStationCode": "BUD", "arrivalStationText": "Budapest", "carrierText": "Operated by W6", "currency": "ILS", "departure": "4:25 pm", "departureDate": "7 June 2025", "departureDateIso": "2025-06-07", "departureDateTimeIso": "2025-06-07 19:25:00", "departureOffsetText": "UTC+3", "departureStation": "TLV", "departureStationCode": "TLV", "departureStationText": "Tel-Aviv", "discount": "0.00", "displayPrice": 43, "duration": "02h 30m", "fare": "43.00", "fareBasisCode": null, "fareSellKey": "MH5BWUNQfn5XNn5BWUNQflNVQlN_fjB_M35_WCEx", "flightCode": "W62328", "flightId": "2328", "isFree": "false", "key": "W62328 TLV#20250607T1625~BUD#20250607T1855", "price": "43.00", "priceTag": "wizzair.subscriptions.availability.results.price.tag.premium", "reference": "VzZ_MjMyOH4gfn5UTFZ_MDYvMDcvMjAyNSAxNjoyNX5CVUR_MDYvMDcvMjAyNSAxODo1NX5_", "stops": "Nonstop", "taxes": "0.00", "totalPrice": "43.00"}]}, {"flightsInbound": [], "flightsOutbound": [{"actionText": "Select", "arrival": "2:45 pm", "arrivalDate": "7 June 2025", "arrivalDateIso": null, "arrivalDateTimeIso": "2025-06-07 17:45:00", "arrivalOffsetText": "UTC+3", "arrivalStation": "LCA", "arrivalStationCode": "LCA", "arrivalStationText": "Larnaca", "carrierText": "Operated by W6", "currency": "ILS", "departure": "1:40 pm", "departureDate": "7 June 2025", "departureDateIso": "2025-06-07", "departureDateTimeIso": "2025-06-07 16:40:00", "departureOffsetText": "UTC+3", "departureStation": "TLV", "departureStationCode": "TLV", "departureStationText": "Tel-Aviv", "discount": "0.00", "displayPrice": 43, "duration": "01h 05m", "fare": "43.00", "fareBasisCode": null, "fareSellKey": "MH5BWUNQfn5XNn5BWUNQflNVQlN_fjB_Mn5_WCEx", "flightCode": "W64608", "flightId": "4608", "isFree": "false", "key": "W64608 TLV#20250607T1340~LCA#20250607T1445", "price": "43.00", "priceTag": "wizzair.subscriptions.availability.results.price.tag.premium", "reference": "VzZ_NDYwOH4gfn5UTFZ_MDYvMDcvMjAyNSAxMzo0MH5MQ0F_MDYvMDcvMjAyNSAxNDo0NX5_", "stops": "Nonstop", "taxes": "0.00", "totalPrice": "43.00"}, {"actionText": "Select", "arrival": "7:40 pm", "arrivalDate": "7 June 2025", "arrivalDateIso": null, "arrivalDateTimeIso": "2025-06-07 22:40:00", "arrivalOffsetText": "UTC+3", "arrivalStation": "LCA", "arrivalStationCode": "LCA", "arrivalStationText": "Larnaca", "carrierText": "Operated by W6", "currency": "ILS", "departure": "6:35 pm", "departureDate": "7 June 2025", "departureDateIso": "2025-06-07", "departureDateTimeIso": "2025-06-07 21:35:00", "departureOffsetText": "UTC+3", "departureStation": "TLV", "departureStationCode": "TLV", "departureStationText": "Tel-Aviv", "discount": "0.00", "displayPrice": 43, "duration": "01h 05m", "fare": "43.00", "fareBasisCode": null, "fareSellKey": "MH5BWUNQfn5XNn5BWUNQflNVQlN_fjB_Mn5_WCEx", "flightCode": "W64606", "flightId": "4606", "isFree": "false", "key": "W64606 TLV#20250607T1835~LCA#20250607T1940", "price": "43.00", "priceTag": "wizzair.subscriptions.availability.results.price.tag.premium", "reference": "VzZ_NDYwNn4gfn5UTFZ_MDYvMDcvMjAyNSAxODozNX5MQ0F_MDYvMDcvMjAyNSAxOTo0MH5_", "stops": "Nonstop", "taxes": "0.00", "totalPrice": "43.00"}]}, {"flightsInbound": [], "flightsOutbound": [{"actionText": "Select", "arrival": "10:50 pm", "arrivalDate": "7 June 2025", "arrivalDateIso": null, "arrivalDateTimeIso": "2025-06-08 00:50:00", "arrivalOffsetText": "UTC+2", "arrivalStation": "VIE", "arrivalStationCode": "VIE", "arrivalStationText": "Vienna", "carrierText": "Operated by W4", "currency": "ILS", "departure": "8:05 pm", "departureDate": "7 June 2025", "departureDateIso": "2025-06-07", "departureDateTimeIso": "2025-06-07 23:05:00", "departureOffsetText": "UTC+3", "departureStation": "TLV", "departureStationCode": "TLV", "departureStationText": "Tel-Aviv", "discount": "0.00", "displayPrice": 43, "duration": "02h 45m", "fare": "43.00", "fareBasisCode": null, "fareSellKey": "MH5BWUNQfn5XNn5BWUNQflNVQlN_fjB_Mn5_WCEx", "flightCode": "W42812", "flightId": "2812", "isFree": "false", "key": "W42812 TLV#20250607T2005~VIE#20250607T2250", "price": "43.00", "priceTag": "wizzair.subscriptions.availability.results.price.tag.premium", "reference": "VzR_MjgxMn4gfn5UTFZ_MDYvMDcvMjAyNSAyMDowNX5WSUV_MDYvMDcvMjAyNSAyMjo1MH5_", "stops": "Nonstop", "taxes": "0.00", "totalPrice": "43.00"}]}, {"flightsInbound": [], "flightsOutbound": [{"actionText": "Select", "arrival": "3:25 pm", "arrivalDate": "7 June 2025", "arrivalDateIso": null, "arrivalDateTimeIso": "2025-06-07 18:25:00", "arrivalOffsetText": "UTC+3", "arrivalStation": "VNO", "arrivalStationCode": "VNO", "arrivalStationText": "Vilnius", "carrierText": "Operated by W6", "currency": "ILS", "departure": "11:05 am", "departureDate": "7 June 2025", "departureDateIso": "2025-06-07", "departureDateTimeIso": "2025-06-07 14:05:00", "departureOffsetText": "UTC+3", "departureStation": "TLV", "departureStationCode": "TLV", "departureStationText": "Tel-Aviv", "discount": "0.00", "displayPrice": 43, "duration": "04h 20m", "fare": "43.00", "fareBasisCode": null, "fareSellKey": "MH5BWUNQfn5XNn5BWUNQflNVQlN_fjB_Mn5_WCEx", "flightCode": "W61966", "flightId": "1966", "isFree": "false", "key": "W61966 TLV#20250607T1105~VNO#20250607T1525", "price": "43.00", "priceTag": "wizzair.subscriptions.availability.results.price.tag.premium", "reference": "VzZ_MTk2Nn4gfn5UTFZ_MDYvMDcvMjAyNSAxMTowNX5WTk9_MDYvMDcvMjAyNSAxNToyNX5_", "stops": "Nonstop", "taxes": "0.00", "totalPrice": "43.00"}]}], "2025-06-08": [{"flightsInbound": [], "flightsOutbound": [{"actionText": "Select", "arrival": "2:55 pm", "arrivalDate": "8 June 2025", "arrivalDateIso": null, "arrivalDateTimeIso": "2025-06-08 18:55:00", "arrivalOffsetText": "UTC+4", "arrivalStation": "AUH", "arrivalStationCode": "AUH", "arrivalStationText": "Abu Dhabi", "carrierText": "Operated by 5W", "currency": "ILS", "departure": "10:35 am", "departureDate": "8 June 2025", "departureDateIso": "2025-06-08", "departureDateTimeIso": "2025-06-08 13:35:00", "departureOffsetText": "UTC+3", "departureStation": "TLV", "departureStationCode": "TLV", "departureStationText": "Tel-Aviv", "discount": "0.00", "displayPrice": 43, "duration": "04h 20m", "fare": "43.00", "fareBasisCode": null, "fareSellKey": "MH5BWUNQfn5XNn5BWUNQflNVQlN_fjB_Mn5_WCEx", "flightCode": "5W7086", "flightId": "7086", "isFree": "false", "key": "5W7086 TLV#20250608T1035~AUH#20250608T1455", "price": "43.00", "priceTag": "wizzair.subscriptions.availability.results.price.tag.premium", "reference": "NVd_NzA4Nn4gfn5UTFZ_MDYvMDgvMjAyNSAxMDozNX5BVUh_MDYvMDgvMjAyNSAxNDo1NX5_", "stops": "Nonstop", "taxes": "0.00", "totalPrice": "43.00"}]}, {"flightsInbound": [], "flightsOutbound": [{"actionText": "Select", "arrival": "10:35 pm", "arrivalDate": "8 June 2025", "arrivalDateIso": null, "arrivalDateTimeIso": "2025-06-09 01:35:00", "arrivalOffsetText": "UTC+3", "arrivalStation": "ATH", "arrivalStationCode": "ATH", "arrivalStationText": "Athens", "carrierText": "Operated by W4", "currency": "ILS", "departure": "8:15 pm", "departureDate": "8 June 2025", "departureDateIso": "2025-06-08", "departureDateTimeIso": "2025-06-08 23:15:00", "departureOffsetText": "UTC+3", "departureStation": "TLV", "departureStationCode": "TLV", "departureStationText": "Tel-Aviv", "discount": "0.00", "displayPrice": 43, "duration": "02h 20m", "fare": "43.00", "fareBasisCode": null, "fareSellKey": "MH5BWUNQfn5XNn5BWUNQflNVQlN_fjB_MX5_WCEx", "flightCode": "W47511", "flightId": "7511", "isFree": "false", "key": "W47511 TLV#20250608T2015~ATH#20250608T2235", "price": "43.00", "priceTag": "wizzair.subscriptions.availability.results.price.tag.premium", "reference": "VzR_NzUxMX4gfn5UTFZ_MDYvMDgvMjAyNSAyMDoxNX5BVEh_MDYvMDgvMjAyNSAyMjozNX5_", "stops": "Nonstop", "taxes": "0.00", "totalPrice": "43.00"}]}, {"flightsInbound": [], "flightsOutbound": [{"actionText": "Select", "arrival": "12:20 pm", "arrivalDate": "8 June 2025", "arrivalDateIso": null, "arrivalDateTimeIso": "2025-06-08 15:20:00", "arrivalOffsetText": "UTC+3", "arrivalStation": "OTP", "arrivalStationCode": "OTP", "arrivalStationText": "Bucharest", "carrierText": "Operated by W4", "currency": "ILS", "departure": "9:25 am", "departureDate": "8 June 2025", "departureDateIso": "2025-06-08", "departureDateTimeIso": "2025-06-08 12:25:00", "departureOffsetText": "UTC+3", "departureStation": "TLV", "departureStationCode": "TLV", "departureStationText": "Tel-Aviv", "discount": "0.00", "displayPrice": 43, "duration": "02h 55m", "fare": "43.00", "fareBasisCode": null, "fareSellKey": "MH5BWUNQfn5XNn5BWUNQflNVQlN_fjB_Mn5_WCEx", "flightCode": "W43258", "flightId": "3258", "isFree": "false", "key": "W43258 TLV#20250608T0925~OTP#20250608T1220", "price": "43.00", "priceTag": "wizzair.subscriptions.availability.results.price.tag.premium", "reference": "VzR_MzI1OH4gfn5UTFZ_MDYvMDgvMjAyNSAwOToyNX5PVFB_MDYvMDgvMjAyNSAxMjoyMH5_", "stops": "Nonstop", "taxes": "0.00", "totalPrice": "43.00"}, {"actionText": "Select", "arrival": "6:05 pm", "arrivalDate": "8 June 2025", "arrivalDateIso": null, "arrivalDateTimeIso": "2025-06-08 21:05:00", "arrivalOffsetText": "UTC+3", "arrivalStation": "OTP", "arrivalStationCode": "OTP", "arrivalStationText": "Bucharest", "carrierText": "Operated by W4", "currency": "ILS", "departure": "3:10 pm", "departureDate": "8 June 2025", "departureDateIso": "2025-06-08", "departureDateTimeIso": "2025-06-08 18:10:00", "departureOffsetText": "UTC+3", "departureStation": "TLV", "departureStationCode": "TLV", "departureStationText": "Tel-Aviv", "discount": "0.00", "displayPrice": 43, "duration": "02h 55m", "fare": "43.00", "fareBasisCode": null, "fareSellKey": "MH5BWUNQfn5XNn5BWUNQflNVQlN_fjB_Mn5_WCEx", "flightCode": "W43264", "flightId": "3264", "isFree": "false", "key": "W43264 TLV#20250608T1510~OTP#20250608T1805", "price": "43.00", "priceTag": "wizzair.subscriptions.availability.results.price.tag.premium", "reference": "VzR_MzI2NH4gfn5UTFZ_MDYvMDgvMjAyNSAxNToxMH5PVFB_MDYvMDgvMjAyNSAxODowNX5_", "stops": "Nonstop", "taxes": "0.00", "totalPrice": "43.00"}]}, {"flightsInbound": [], "flightsOutbound": [{"actionText": "Select", "arrival": "12:10 pm", "arrivalDate": "8 June 2025", "arrivalDateIso": null, "arrivalDateTimeIso": "2025-06-08 15:10:00", "arrivalOffsetText": "UTC+3", "arrivalStation": "IAS", "arrivalStationCode": "IAS", "arrivalStationText": "Iasi", "carrierText": "Operated by W4", "currency": "ILS", "departure": "9:05 am", "departureDate": "8 June 2025", "departureDateIso": "2025-06-08", "departureDateTimeIso": "2025-06-08 12:05:00", "departureOffsetText": "UTC+3", "departureStation": "TLV", "departureStationCode": "TLV", "departureStationText": "Tel-Aviv", "discount": "0.00", "displayPrice": 43, "duration": "03h 05m", "fare": "43.00", "fareBasisCode": null, "fareSellKey": "MH5BWUNQfn5XNn5BWUNQflNVQlN_fjB_Mn5_WCEx", "flightCode": "W43690", "flightId": "3690", "isFree": "false", "key": "W43690 TLV#20250608T0905~IAS#20250608T1210", "price": "43.00", "priceTag": "wizzair.subscriptions.availability.results.price.tag.premium", "reference": "VzR_MzY5MH4gfn5UTFZ_MDYvMDgvMjAyNSAwOTowNX5JQVN_MDYvMDgvMjAyNSAxMjoxMH5_", "stops": "Nonstop", "taxes": "0.00", "totalPrice": "43.00"}]}, {"flightsInbound": [], "flightsOutbound": [{"actionText": "Select", "arrival": "2:00 pm", "arrivalDate": "8 June 2025", "arrivalDateIso": null, "arrivalDateTimeIso": "2025-06-08 16:00:00", "arrivalOffsetText": "UTC+2", "arrivalStation": "KRK", "arrivalStationCode": "KRK", "arrivalStationText": "Krak\\u00f3w", "carrierText": "Operated by W6", "currency": "ILS", "departure": "11:15 am", "departureDate": "8 June 2025", "departureDateIso": "2025-06-08", "departureDateTimeIso": "2025-06-08 14:15:00", "departureOffsetText": "UTC+3", "departureStation": "TLV", "departureStationCode": "TLV", "departureStationText": "Tel-Aviv", "discount": "0.00", "displayPrice": 43, "duration": "02h 45m", "fare": "43.00", "fareBasisCode": null, "fareSellKey": "MH5BWUNQfn5XNn5BWUNQflNVQlN_fjB_MX5_WCEx", "flightCode": "W62098", "flightId": "2098", "isFree": "false", "key": "W62098 TLV#20250608T1115~KRK#20250608T1400", "price": "43.00", "priceTag": "wizzair.subscriptions.availability.results.price.tag.premium", "reference": "VzZ_MjA5OH4gfn5UTFZ_MDYvMDgvMjAyNSAxMToxNX5LUkt_MDYvMDgvMjAyNSAxNDowMH5_", "stops": "Nonstop", "taxes": "0.00", "totalPrice": "43.00"}]}, {"flightsInbound": [], "flightsOutbound": [{"actionText": "Select", "arrival": "2:50 pm", "arrivalDate": "8 June 2025", "arrivalDateIso": null, "arrivalDateTimeIso": "2025-06-08 17:50:00", "arrivalOffsetText": "UTC+3", "arrivalStation": "LCA", "arrivalStationCode": "LCA", "arrivalStationText": "Larnaca", "carrierText": "Operated by W6", "currency": "ILS", "departure": "1:45 pm", "departureDate": "8 June 2025", "departureDateIso": "2025-06-08", "departureDateTimeIso": "2025-06-08 16:45:00", "departureOffsetText": "UTC+3", "departureStation": "TLV", "departureStationCode": "TLV", "departureStationText": "Tel-Aviv", "discount": "0.00", "displayPrice": 43, "duration": "01h 05m", "fare": "43.00", "fareBasisCode": null, "fareSellKey": "MH5BWUNQfn5XNn5BWUNQflNVQlN_fjB_Mn5_WCEx", "flightCode": "W64604", "flightId": "4604", "isFree": "false", "key": "W64604 TLV#20250608T1345~LCA#20250608T1450", "price": "43.00", "priceTag": "wizzair.subscriptions.availability.results.price.tag.premium", "reference": "VzZ_NDYwNH4gfn5UTFZ_MDYvMDgvMjAyNSAxMzo0NX5MQ0F_MDYvMDgvMjAyNSAxNDo1MH5_", "stops": "Nonstop", "taxes": "0.00", "totalPrice": "43.00"}, {"actionText": "Select", "arrival": "10:15 pm", "arrivalDate": "8 June 2025", "arrivalDateIso": null, "arrivalDateTimeIso": "2025-06-09 01:15:00", "arrivalOffsetText": "UTC+3", "arrivalStation": "LCA", "arrivalStationCode": "LCA", "arrivalStationText": "Larnaca", "carrierText": "Operated by W6", "currency": "ILS", "departure": "9:10 pm", "departureDate": "8 June 2025", "departureDateIso": "2025-06-08", "departureDateTimeIso": "2025-06-09 00:10:00", "departureOffsetText": "UTC+3", "departureStation": "TLV", "departureStationCode": "TLV", "departureStationText": "Tel-Aviv", "discount": "0.00", "displayPrice": 43, "duration": "01h 05m", "fare": "43.00", "fareBasisCode": null, "fareSellKey": "MH5BWUNQfn5XNn5BWUNQflNVQlN_fjB_Mn5_WCEx", "flightCode": "W64606", "flightId": "4606", "isFree": "false", "key": "W64606 TLV#20250608T2110~LCA#20250608T2215", "price": "43.00", "priceTag": "wizzair.subscriptions.availability.results.price.tag.premium", "reference": "VzZ_NDYwNn4gfn5UTFZ_MDYvMDgvMjAyNSAyMToxMH5MQ0F_MDYvMDgvMjAyNSAyMjoxNX5_", "stops": "Nonstop", "taxes": "0.00", "totalPrice": "43.00"}]}, {"flightsInbound": [], "flightsOutbound": [{"actionText": "Select", "arrival": "10:15 am", "arrivalDate": "8 June 2025", "arrivalDateIso": null, "arrivalDateTimeIso": "2025-06-08 13:15:00", "arrivalOffsetText": "UTC+3", "arrivalStation": "RHO", "arrivalStationCode": "RHO", "arrivalStationText": "Rhodes", "carrierText": "Operated by W6", "currency": "ILS", "departure": "8:40 am", "departureDate": "8 June 2025", "departureDateIso": "2025-06-08", "departureDateTimeIso": "2025-06-08 11:40:00", "departureOffsetText": "UTC+3", "departureStation": "TLV", "departureStationCode": "TLV", "departureStationText": "Tel-Aviv", "discount": "0.00", "displayPrice": 43, "duration": "01h 35m", "fare": "43.00", "fareBasisCode": null, "fareSellKey": "MH5BWUNQfn5XNn5BWUNQflNVQlN_fjB_MX5_WCEx", "flightCode": "W67501", "flightId": "7501", "isFree": "false", "key": "W67501 TLV#20250608T0840~RHO#20250608T1015", "price": "43.00", "priceTag": "wizzair.subscriptions.availability.results.price.tag.premium", "reference": "VzZ_NzUwMX4gfn5UTFZ_MDYvMDgvMjAyNSAwODo0MH5SSE9_MDYvMDgvMjAyNSAxMDoxNX5_", "stops": "Nonstop", "taxes": "0.00", "totalPrice": "43.00"}]}, {"flightsInbound": [], "flightsOutbound": [{"actionText": "Select", "arrival": "2:50 pm", "arrivalDate": "8 June 2025", "arrivalDateIso": null, "arrivalDateTimeIso": "2025-06-08 16:50:00", "arrivalOffsetText": "UTC+2", "arrivalStation": "WAW", "arrivalStationCode": "WAW", "arrivalStationText": "Warsaw Chopin", "carrierText": "Operated by W6", "currency": "ILS", "departure": "11:50 am", "departureDate": "8 June 2025", "departureDateIso": "2025-06-08", "departureDateTimeIso": "2025-06-08 14:50:00", "departureOffsetText": "UTC+3", "departureStation": "TLV", "departureStationCode": "TLV", "departureStationText": "Tel-Aviv", "discount": "0.00", "displayPrice": 43, "duration": "03h 00m", "fare": "43.00", "fareBasisCode": null, "fareSellKey": "MH5BWUNQfn5XNn5BWUNQflNVQlN_fjB_MX5_WCEx", "flightCode": "W61560", "flightId": "1560", "isFree": "false", "key": "W61560 TLV#20250608T1150~WAW#20250608T1450", "price": "43.00", "priceTag": "wizzair.subscriptions.availability.results.price.tag.premium", "reference": "VzZ_MTU2MH4gfn5UTFZ_MDYvMDgvMjAyNSAxMTo1MH5XQVd_MDYvMDgvMjAyNSAxNDo1MH5_", "stops": "Nonstop", "taxes": "0.00", "totalPrice": "43.00"}]}]}')
    # time.sleep(7)
    logger.info("after getting al options")
    logger.info(json.dumps(all_options))
    # breakpoint()
    if not DEBUG:
        for date, options_by_date in all_options.items():
            options_by_date = [opt for opt in options_by_date if not opt.get("message")]
            for option in options_by_date:
                if "flightsOutbound" not in option:
                    logger.info(f"failed to find flightsOutbound in {option} THIS SHOULD NEVEL HAPPEN!")
                    time.sleep(3)
                    continue
                for flight in option["flightsOutbound"]:
                    try:
                        flight_to = airports[flight["arrivalStationCode"]]
                        get_weather_by_city(flight_to["city"])
                    except Exception as e:
                        logger.exception(f'failed with {flight["arrivalStationCode"]} and get weather')
    else: # if debug
        weather_by_city = {'Milano': {'text': 'Forecast: 2025-06-05: 19°C, Patchy rain nearby || 2025-06-06: 21°C, Patchy rain nearby || 2025-06-07: 22°C, Partly Cloudy  || ', 'style': [{'date': '2025-06-05', 'description': 'Patchy rain nearby', 'color': '#cbcb4b', 'avgTemp': '19°C'}, {'date': '2025-06-06', 'description': 'Patchy rain nearby', 'color': '#cbcb4b', 'avgTemp': '21°C'}, {'date': '2025-06-07', 'description': 'Partly Cloudy ', 'color': '#cbcb4b', 'avgTemp': '22°C'}]}, 'Rome': {'text': 'Forecast: 2025-06-05: 23°C, Patchy rain nearby || 2025-06-06: 23°C, Sunny || 2025-06-07: 24°C, Sunny || ', 'style': [{'date': '2025-06-05', 'description': 'Patchy rain nearby', 'color': '#cbcb4b', 'avgTemp': '23°C'}, {'date': '2025-06-06', 'description': 'Sunny', 'color': 'green', 'avgTemp': '23°C'}, {'date': '2025-06-07', 'description': 'Sunny', 'color': 'green', 'avgTemp': '24°C'}]}, 'Larnaca': {'text': 'Forecast: 2025-06-05: 24°C, Sunny || 2025-06-06: 24°C, Sunny || 2025-06-07: 24°C, Sunny || ', 'style': [{'date': '2025-06-05', 'description': 'Sunny', 'color': 'green', 'avgTemp': '24°C'}, {'date': '2025-06-06', 'description': 'Sunny', 'color': 'green', 'avgTemp': '24°C'}, {'date': '2025-06-07', 'description': 'Sunny', 'color': 'green', 'avgTemp': '24°C'}]}, 'London': {'text': 'Forecast: 2025-06-05: 13°C, Light rain shower || 2025-06-06: 14°C, Patchy rain nearby || 2025-06-07: 14°C, Patchy light rain || ', 'style': [{'date': '2025-06-05', 'description': 'Light rain shower', 'color': 'red', 'avgTemp': '13°C'}, {'date': '2025-06-06', 'description': 'Patchy rain nearby', 'color': '#cbcb4b', 'avgTemp': '14°C'}, {'date': '2025-06-07', 'description': 'Patchy light rain', 'color': 'red', 'avgTemp': '14°C'}]}, 'Warsaw': {'text': 'Forecast: 2025-06-05: 21°C, Patchy rain nearby || 2025-06-06: 21°C, Patchy rain nearby || 2025-06-07: 19°C, Patchy rain nearby || ', 'style': [{'date': '2025-06-05', 'description': 'Patchy rain nearby', 'color': '#cbcb4b', 'avgTemp': '21°C'}, {'date': '2025-06-06', 'description': 'Patchy rain nearby', 'color': '#cbcb4b', 'avgTemp': '21°C'}, {'date': '2025-06-07', 'description': 'Patchy rain nearby', 'color': '#cbcb4b', 'avgTemp': '19°C'}]}, 'Abu Dhabi': {'text': 'Forecast: 2025-06-05: 30°C, Sunny || 2025-06-06: 30°C, Sunny || 2025-06-07: 30°C, Sunny || ', 'style': [{'date': '2025-06-05', 'description': 'Sunny', 'color': 'green', 'avgTemp': '30°C'}, {'date': '2025-06-06', 'description': 'Sunny', 'color': 'green', 'avgTemp': '30°C'}, {'date': '2025-06-07', 'description': 'Sunny', 'color': 'green', 'avgTemp': '30°C'}]}, 'Bucharest': {'text': 'Forecast: 2025-06-05: 25°C, Sunny || 2025-06-06: 25°C, Sunny || 2025-06-07: 23°C, Sunny || ', 'style': [{'date': '2025-06-05', 'description': 'Sunny', 'color': 'green', 'avgTemp': '25°C'}, {'date': '2025-06-06', 'description': 'Sunny', 'color': 'green', 'avgTemp': '25°C'}, {'date': '2025-06-07', 'description': 'Sunny', 'color': 'green', 'avgTemp': '23°C'}]}, 'Budapest': {'text': 'Forecast: 2025-06-05: 25°C, Sunny || 2025-06-06: 25°C, Sunny || 2025-06-07: 26°C, Sunny || ', 'style': [{'date': '2025-06-05', 'description': 'Sunny', 'color': 'green', 'avgTemp': '25°C'}, {'date': '2025-06-06', 'description': 'Sunny', 'color': 'green', 'avgTemp': '25°C'}, {'date': '2025-06-07', 'description': 'Sunny', 'color': 'green', 'avgTemp': '26°C'}]}, 'Vienna': {'text': 'Forecast: 2025-06-05: 22°C, Partly Cloudy  || 2025-06-06: 22°C, Partly Cloudy  || 2025-06-07: 20°C, Cloudy  || ', 'style': [{'date': '2025-06-05', 'description': 'Partly Cloudy ', 'color': '#cbcb4b', 'avgTemp': '22°C'}, {'date': '2025-06-06', 'description': 'Partly Cloudy ', 'color': '#cbcb4b', 'avgTemp': '22°C'}, {'date': '2025-06-07', 'description': 'Cloudy ', 'color': '#cbcb4b', 'avgTemp': '20°C'}]}, 'Vilnius': {'text': 'Forecast: 2025-06-05: 18°C, Moderate or heavy rain with thunder || 2025-06-06: 18°C, Light rain shower || 2025-06-07: 17°C, Partly Cloudy  || ', 'style': [{'date': '2025-06-05', 'description': 'Moderate or heavy rain with thunder', 'color': 'red', 'avgTemp': '18°C'}, {'date': '2025-06-06', 'description': 'Light rain shower', 'color': 'red', 'avgTemp': '18°C'}, {'date': '2025-06-07', 'description': 'Partly Cloudy ', 'color': '#cbcb4b', 'avgTemp': '17°C'}]}, 'Athens': {'text': 'Forecast: 2025-06-05: 24°C, Cloudy  || 2025-06-06: 26°C, Partly Cloudy  || 2025-06-07: 27°C, Partly Cloudy  || ', 'style': [{'date': '2025-06-05', 'description': 'Cloudy ', 'color': '#cbcb4b', 'avgTemp': '24°C'}, {'date': '2025-06-06', 'description': 'Partly Cloudy ', 'color': '#cbcb4b', 'avgTemp': '26°C'}, {'date': '2025-06-07', 'description': 'Partly Cloudy ', 'color': '#cbcb4b', 'avgTemp': '27°C'}]}, 'Iasi': {'text': 'Forecast: 2025-06-05: 23°C, Sunny || 2025-06-06: 23°C, Sunny || 2025-06-07: 23°C, Sunny || ', 'style': [{'date': '2025-06-05', 'description': 'Sunny', 'color': 'green', 'avgTemp': '23°C'}, {'date': '2025-06-06', 'description': 'Sunny', 'color': 'green', 'avgTemp': '23°C'}, {'date': '2025-06-07', 'description': 'Sunny', 'color': 'green', 'avgTemp': '23°C'}]}, 'Krakow': {'text': 'Forecast: 2025-06-05: 20°C, Partly Cloudy  || 2025-06-06: 20°C, Sunny || 2025-06-07: 18°C, Partly Cloudy  || ', 'style': [{'date': '2025-06-05', 'description': 'Partly Cloudy ', 'color': '#cbcb4b', 'avgTemp': '20°C'}, {'date': '2025-06-06', 'description': 'Sunny', 'color': 'green', 'avgTemp': '20°C'}, {'date': '2025-06-07', 'description': 'Partly Cloudy ', 'color': '#cbcb4b', 'avgTemp': '18°C'}]}, 'Rhodes': {'text': 'Forecast: 2025-06-05: 15°C, Patchy rain nearby || 2025-06-06: 15°C, Patchy rain nearby || 2025-06-07: 16°C, Sunny || ', 'style': [{'date': '2025-06-05', 'description': 'Patchy rain nearby', 'color': '#cbcb4b', 'avgTemp': '15°C'}, {'date': '2025-06-06', 'description': 'Patchy rain nearby', 'color': '#cbcb4b', 'avgTemp': '15°C'}, {'date': '2025-06-07', 'description': 'Sunny', 'color': 'green', 'avgTemp': '16°C'}]}}

    logger.info("after getting all weather data")
    # breakpoint()
    for cur_date, options_by_date in all_options.items():
        options_by_date = [opt for opt in options_by_date if not opt.get("message")]
        if not options_by_date:
            continue  # skip date with no options

        logger.info(f"Running for date {cur_date}")

        for option in options_by_date:
            try:
                first_flight = option["flightsOutbound"][0]
                flight_from = airports[first_flight["departureStationCode"]]
                flight_to = airports[first_flight["arrivalStationCode"]]
            except Exception as e:
                logger.exception(f"************************ Failed to due to missing airport code {e}")
                logger.info(f"flight from { first_flight['departureStationCode'] } -> { first_flight['arrivalStationCode'] }")
                continue

            logger.info(f"flight from {flight_from['city']} -> {flight_to['city']}, {flight_to['state']}")

            try:
                logger.info("getting weather")
                weather = get_weather_by_city(flight_to["city"])
                logger.info(weather["text"])
                for style in weather["style"]:
                    logger.info(style)  # Optional: Format this if needed
            except Exception as e:
                logger.exception("failed for", weather_by_city, flight_to["city"])
                continue

            for flight in option["flightsOutbound"]:
                logger.info(f"Available Flight: {flight['departureDateTimeIso']}-3hours")
    return {"flights": all_options, "weather": weather_by_city}
    # write_html(all_options, weather_by_city)

def write_html(all_flights, weather_by_city, FROM):
    if not DEBUG:
        ################# Handle old index.html ##############
        # Step 1: Check if index.html exists
        if os.path.isfile("index.html"):
            # Step 2: Generate new filename with date and time
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            new_filename = f"backup_{timestamp}.html"
            
            # Rename the file
            os.rename("index.html", f"backups/{new_filename}")
            logger.info(f"Renamed to backups/{new_filename}")
            
        else:
            logger.info("index.html does not exist.")


    ############## Handle new index.html ##############
    # Open the original file in read mode
    
    with open("template.html", "r", encoding="utf-8") as file:
        content = file.read()

    # Replace the words
    content = content.replace("__all_flights__", json.dumps(all_flights))
    content = content.replace("__all_weather__", json.dumps(weather_by_city))
    if DEBUG:
        new_filename = "debug.html"
        with open(new_filename, "w", encoding="utf-8") as new_file:
            new_file.write(content)
    else:
        new_filename = "index.html"
        # Write the modified content to a new file
        with open(new_filename, "w", encoding="utf-8") as new_file:
            new_file.write(content)
        shutil.copy("index.html", f"index_{FROM}.html")



# Get run variable arguments from command line
parser = argparse.ArgumentParser(description='available flags example: "--departure TLV --arrival TLV"')
parser.add_argument(
    "--departure",
    type=str,
    default="TLV",
    help="departure airport code (default: TLV)"
)
parser.add_argument(
    "--arrival",
    type=str,
    default="ALL",
    help="departure airport code (default: TLV)"
)
args = parser.parse_args()


# create al list with all the wanted dates to check
DATES = []
for i in range(4):
    date = datetime.datetime.now() + datetime.timedelta(days=i)
    DATES.append(date.strftime("%Y-%m-%d"))  # format: YYYY-MM-DD


# init the driver (for updates so we can run in threads)
driver = get_driver()
driver.close()


# get all flights of specific date using a different thread of reduce run time
all_flights = {}
with ThreadPoolExecutor(max_workers=10) as executor: 
    # Submit all tasks ARRIVAL_TYPE="ALL", FROM="TLV", DATES="ALL"
    future_to_item = {executor.submit(generate_page, FROM=args.departure, ARRIVAL_TYPE=args.arrival, DATES=[date]): date for date in DATES}
    
    # Collect results as they complete
    for future in as_completed(future_to_item):
        result = future.result()
        for date, flights in result["flights"].items():
            all_flights[date] = flights

# Write the results to the index page
write_html(all_flights, weather_by_city, args.departure)