import streamlit as st
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


class KeyToAdApp:
    def __init__(self, mongo_uri):
        self.client = MongoClient(mongo_uri, server_api=ServerApi("1"))
        self.db = self.client["keytoad"]
        self.collection = self.db["keytoad"]
        self.emo_collection = self.db["emodata"]

        self.options = ["Normal", "Luxury", "Chill", "Exclusive", "Bad"]
        self.data_editor = None

        st.set_page_config(
            page_title="KeyToAd",
            page_icon="📣",
            layout="wide",
            initial_sidebar_state="expanded",
        )

        if "state" not in st.session_state:
            st.session_state["state"] = False

        if "data" not in st.session_state:
            st.session_state["data"] = None

    def get_random_data(self):
        listdata = list(self.collection.aggregate([{"$sample": {"size": 5}}]))

        status = True
        while status:
            for item in listdata:
                if self.emo_collection.find_one({"_id": item["_id"]}):
                    listdata = list(
                        self.collection.aggregate([{"$sample": {"size": 5}}])
                    )
                    break
            else:
                status = False

        return listdata

    def send_api(self, data):
        with st.spinner("Wait for it..."):
            self.emo_collection.insert_many(data)
        # st.info(data)

        st.session_state["state"] = False
        st.session_state["data"] = None
        st.success("Send API Success")

    def run(self):
        st.title("KeyToAd")

        if st.button("🔁 Get Random Data 🔁"):
            st.session_state["state"] = True
            with st.status("Loading Data..."):
                st.session_state["data"] = self.get_random_data()

        self.data_editor = StreamlitDataEditor(
            data=st.session_state["data"] if st.session_state["state"] else None,
            options=self.options,
        )

        if self.data_editor.is_data_available():
            self.data_editor.generate_editor()

        if st.button("✉️ Send API ✉️"):
            if st.session_state["state"]:
                self.send_api(st.session_state["data"])
            else:
                st.warning("Please get random data first")

        if st.button("⬆️ Go Top ⬆️"):
            js = """
            <script>
                var body = window.parent.document.querySelector(".main");
                console.log(body);
                body.scrollTop = 0;
            </script>
            """

            st.components.v1.html(js)


class StreamlitDataEditor:
    def __init__(self, data, options):
        self.data = data
        self.options = options

    def generate_editor(self):
        for i, item in enumerate(self.data):
            st.write(f"keyword: {item['context']}")
            st.write(f"Generate: {item['bot']}")
            item["Emotion"] = st.selectbox(
                f"Emotion for item {i+1}",
                options=self.options,
                key=f"emotion_{i}",
            )

    def is_data_available(self):
        return self.data is not None


if __name__ == "__main__":
    app = KeyToAdApp(
        "mongodb+srv://64015037:2YqYA4kjsTImOMmY@keytoad.nslb9f9.mongodb.net/?retryWrites=true&w=majority"
    )
    app.run()
