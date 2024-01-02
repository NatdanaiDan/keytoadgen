import streamlit as st
import pandas as pd
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

pd.set_option("display.max_colwidth", 0)

uri = "mongodb+srv://64015037:2YqYA4kjsTImOMmY@keytoad.nslb9f9.mongodb.net/?retryWrites=true&w=majority"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi("1"))

from bson.objectid import ObjectId

st.set_page_config(
    page_title="KeyToAd",
    page_icon="📣",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("KeyToAd")

db = client["keytoad"]
collection = db["keytoad"]
emo_collection = db["emodata"]

if "state" not in st.session_state:
    st.session_state["state"] = False

if "data" not in st.session_state:
    st.session_state["data"] = None


def getrandomdata():
    listdata = list(collection.aggregate([{"$sample": {"size": 5}}]))
    # print objectid in listdata
    status = True

    while status:
        for item in listdata:
            # Check if _id already exists in emo_collection
            if emo_collection.find_one({"_id": item["_id"]}):
                # If duplicate _id, get new random data
                listdata = list(collection.aggregate([{"$sample": {"size": 5}}]))
                break
        else:
            # If no duplicate _id found, exit the loop
            status = False

    return listdata


def sendapi(data):
    st.info(f"Sending API... {data}")

    # Insert data into emo_collection
    emo_collection.insert_many(data)

    st.success("Send API Success")
    st.session_state["state"] = False
    st.session_state["data"] = None


if st.button("Get Random Data"):
    st.session_state["state"] = True
    data = getrandomdata()
    st.session_state["data"] = data

edited_df = st.data_editor(
    data=st.session_state["data"] if st.session_state["state"] else None,
    column_config={
        "Emotion": st.column_config.SelectboxColumn(
            "Emotion",
            options=["Normal", "Luxury", "Chill", "Exclusive", "Bad"],
            required=True,
        )
    },
    # width=3000,
    use_container_width=True,
)

st.table(edited_df)
if st.button("Send API"):
    if st.session_state["state"]:
        sendapi(edited_df)
    else:
        st.warning("Please get random data first")
