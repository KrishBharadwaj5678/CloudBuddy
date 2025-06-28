import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

st.set_page_config(
    page_title="CloudBuddy – Your Cloud Storage Solution",
    page_icon="icon.png",
    menu_items={
        "About":"CloudBuddy makes file storage simple and accessible. Upload, store, and access your files with ease, anytime and anywhere. Keep your files in the cloud for up to 3 days, with no hassle and no worries."
    }
)

st.write("<h2 style='color:#00BFFF;'>Your Files, Our Cloud.</h2>", unsafe_allow_html=True)

st.info("⚠️ Your uploaded files will be deleted after 3 days!")

tab1,tab2 = st.tabs(["Upload File","Access File Link"])

Max_Size=20  # Maximum size of file
Total_Bytes = Max_Size*1024*1024   # Converting from MB to Bytes
folderName= "uploaded"  # Folder name where the file will be stored

with tab1:

    url = "https://unlimited-cloud-storage.p.rapidapi.com/rapidapi/telegram/upload.php"

    file=st.file_uploader("Upload your file",accept_multiple_files=False)

    if file is not None:
        fileName= file.name
        bytes = file.getvalue()

        if Total_Bytes>len(bytes):

            with st.spinner("Uploading your file..."):

                if not os.path.exists(folderName):
                    os.mkdir(folderName)

                localFile = os.path.join(folderName,fileName)

                # Storing files locally
                with open(f"{folderName}/{fileName}","wb+") as file:
                    file.write(bytes)

                with open(f"{folderName}/{fileName}","rb") as finalFile:
                    files = {
                        "document":(f"{fileName}",finalFile)
                    }
                    payload = {
                        "botToken": os.getenv("BOT_TOKEN"),
                        "chatId": os.getenv("CHAT_ID")
                    }
                    headers = {
                        "x-rapidapi-key": os.getenv("RAPIDAPI_KEY"),
                        "x-rapidapi-host": os.getenv("RAPIDAPI_HOST"),
                    }

                    response = requests.post(url, data=payload, files=files, headers=headers)

                if response.status_code == 200:
                    main = response.json()
                    cloudLink = main["data"]["result"]["document"]["file_id"]
                    cloudfileName = main["data"]["result"]["document"]["file_name"]
                    st.write("📁 Your File ID:")
                    st.code(cloudLink)
                    st.success(f"☁️ {cloudfileName} is in the cloud!")

                    try:
                        os.remove(localFile)  # deleting the local file
                    except PermissionError:
                        st.error("🚨 Error deleting the file after upload!")
                else:
                    st.error("📤 Error sending the file.")
        else:
            st.error("🚫 File size must not exceed 20MB.")

with tab2:
    fileId = st.text_input("Enter File ID",placeholder="Paste your File ID here...")
    getLink = st.button("Get Link")
    if getLink:
        with st.spinner("Hang tight, we're getting your link!"):
            url = "https://unlimited-cloud-storage.p.rapidapi.com/rapidapi/telegram/download.php"

            querystring = {"fileId": f"{fileId}"}

            headers = {
                "x-rapidapi-key": os.getenv("RAPIDAPI_KEY"),
                "x-rapidapi-host": os.getenv("RAPIDAPI_HOST")
            }

            try:
                response = requests.get(url, headers=headers, params=querystring)

                if response.status_code==200:
                    data = response.json()
                    if "file_path" in data:
                        st.code(data["file_path"])
                elif response.status_code==400:
                    st.error("🛑 Invalid File ID!")

            except requests.exceptions.HTTPError:
                st.error("❌ HTTP Error Occurred.")
            except requests.exceptions.ConnectionError:
                st.error("🌐 Network Error.")
            except:
                st.error("🤷‍♂️ An unexpected error occurred.")
