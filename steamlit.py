import streamlit as st
import pandas as pd
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# pd.set_option("display.max_colwidth", 0)

# Your MongoDB URI
uri = "mongodb+srv://64015037:2YqYA4kjsTImOMmY@keytoad.nslb9f9.mongodb.net/?retryWrites=true&w=majority"
js = """
<script>
    var body = window.parent.document.querySelector(".main");
    console.log(body);
    body.scrollTop = 0;
</script>
"""


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

# Your MongoDB setup
db = client["keytoad"]
collection = db["keytoad"]
emo_collection = db["emodata"]

# Your Streamlit session state setup
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
    # st.info(f"Sending API... {data}")
    # print(data)
    # Insert data into emo_collection
    # with st.spinner("Wait for it..."):
    #     emo_collection.insert_many(data)

    st.session_state["state"] = False
    st.session_state["data"] = None
    st.success("Send API Success")
    st.components.v1.html(js)
    # st.balloons(s)


class StreamlitDataEditor:
    def __init__(self, data, options):
        self.data = data
        self.options = options

    def generate_editor(self):
        for i in range(len(self.data)):
            st.write(f"keyword: {self.data[i]['context']}")
            st.write(f"Generate: {self.data[i]['bot']}")
            self.data[i]["Emotion"] = st.selectbox(
                f"Emotion for item {i+1}",
                options=self.options,
                key=f"emotion_{i}",
            )

    def is_data_available(self):
        return self.data is not None


# Usage
if st.button("Get Random Data"):
    st.session_state["state"] = True
    with st.status("Loading Data..."):
        st.session_state["data"] = getrandomdata()

data_editor = StreamlitDataEditor(
    data=st.session_state["data"] if st.session_state["state"] else None,
    options=["Normal", "Luxury", "Chill", "Exclusive", "Bad"],
)

if data_editor.is_data_available():
    data_editor.generate_editor()

if st.button("Send API"):
    if st.session_state["state"]:
        sendapi(st.session_state["data"])
    else:
        st.warning("Please get random data first")

# if st.button("Send API and Get Random Data"):
#     if st.session_state["state"]:
#         sendapi(st.session_state["data"])
#         st.session_state["state"] = True
#         with st.status("Loading Data..."):
#             st.session_state["data"] = getrandomdata()
#             print(st.session_state["data"])
#     else:
#         st.warning("Please get random data first")
