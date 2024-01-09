import streamlit as st
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


class KeyToAdApp:
    def __init__(self, mongo_uri):
        self.client = MongoClient(mongo_uri, server_api=ServerApi("1"))
        self.db = self.client["keytoad"]
        self.collection = self.db["keytoad"]
        self.emo_collection = self.db["emodata"]
        self.collection_duplicate = self.db["keytoadduplicated"]

        self.options = ["Bad", "Normal", "Luxury", "Chill", "Exclusive"]
        self.data_editor = None
        self.javascriptgotop = """
            <script>
                var body = window.parent.document.querySelector(".main");
                console.log(body);
                body.scrollTop = 0;
            </script>
            """
        # count row in emo_collection

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

        if "progress" not in st.session_state:
            st.session_state["progress"] = self.emo_collection.count_documents({})

    def get_random_data(self, sample_size=5):
        while True:
            listdata = list(
                self.collection.aggregate([{"$sample": {"size": sample_size}}])
            )

            if not any(
                self.emo_collection.find_one({"_id": item["_id"]}) for item in listdata
            ):
                return listdata

    def get_random_match_all(self, sample_size=1):
        while True:
            data = list(
                self.collection_duplicate.aggregate(
                    [{"$sample": {"size": sample_size}}]
                )
            )
            context_text = data[0]["context"]

            # Check if context_text is not in self.emo_collection
            while self.emo_collection.find_one({"_id": data[0]["_id"]}):
                data = list(
                    self.collection_duplicate.aggregate(
                        [{"$sample": {"size": sample_size}}]
                    )
                )
                context_text = data[0]["context"]

            # Use match stage to get all data that have the same context
            match_stage = {"$match": {"context": context_text}}
            datasame = list(self.collection_duplicate.aggregate([match_stage]))

            return datasame

    def send_api(self, data):
        with st.spinner("Wait for it..."):
            self.emo_collection.insert_many(data)
        # st.info(data)

        st.session_state["state"] = False
        st.session_state["data"] = None
        st.success("Send API Success")

    def run(self):
        st.title("KeyToAd")
        st.header(
            "get random กับ match all ต่างกันที่ get random จะเอาข้อมูลที่ไม่ซ้ำกันเลยแบบสุ่มจริงๆ แต่ match all จะ random ข้อมูลที่มี context เหมือนกันมาทั้งหมด Recommend Match ALL !!!"
        )
        st.header("⚠️⚠️⚠️ Recommend Match ALL !!! ⚠️⚠️⚠️ จะได้สอนดีกว่า")
        st.metric(label="Progress", value=f"{st.session_state['progress']}")

        if st.button("🔁 Get Random Data 🔁"):
            st.session_state["state"] = True
            with st.status("Loading Data..."):
                st.session_state["data"] = self.get_random_data()

        if st.button("🔁 Get Random Match All 🔁"):
            st.session_state["state"] = True
            with st.status("Loading Data..."):
                st.session_state["data"] = self.get_random_match_all()

        self.data_editor = StreamlitDataEditor(
            data=st.session_state["data"] if st.session_state["state"] else None,
            options=self.options,
        )

        if self.data_editor.is_data_available():
            self.data_editor.generate_editor()

        if st.button("✉️ Send API ✉️"):
            if st.session_state["state"]:
                self.send_api(st.session_state["data"])
                st.session_state["progress"] = self.emo_collection.count_documents({})
            else:
                st.warning("Please get random data first")

        if st.button("⬆️ Go Top ⬆️"):
            st.components.v1.html(self.javascriptgotop)


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
