This is an extremely simple app to demonstrate running a Streamlit app that connects to Snowflake in an Azure Web App.

## Setup
1. Create Azure Function App:
    - visit https://portal.azure.com/#create/Microsoft.WebSite
    - pick subscription & resource group
    - name the app (streamlittest)
    - runtime stack: Python
    - version: 3.10 
    - pick or create a linux plan
    - review & create
    - create
2. Go to the new resource in the Azure portal
    - find the Configuration blade
    - go to the General Settings tab
    - set the startup command to: `python -m streamlit run app.py --server.port 8000 --server.address 0.0.0.0`
    - click Save
3. Next, go to the Deployment Center blade and set up a repository.  I use:
    - Source: Github
    - Provider (click the 'Change Provider' link): App Service Build Service
    - sign in to Github if necessary
    - pick your org, repo, and branch
    - click Save
4. You can switch to the logs tab to monitor the progress of the code deployment.
5. Once the status shows 'Success (Active)', visit streamlittest.azurewebsites.net (changing 'streamlittest' to whatever you named your app)

## Usage
Test the connection.
1. Pick a connection method:
    - Default (user name and password)
    - SSO (single-sign-on)
    - KPA (key pair authentication)
2. Fill in the appropriate information for the connection method you picked
    - note that the 'save connection' drop-down may not do anything in Azure
3. Press Enter or click Submit
4. Once you see 'Congrats, you're connected!', the app has connected to Snowflake successfully.
5. If you like, click the Pick your Database dropdown to see the list of databases available to your user in its default role, if any.

## Running Locally
If you'd like to run this app locally so that you can try it out yourself, or modify it:

1. Install Streamlit as described here: https://docs.streamlit.io/library/get-started/installation
2. Clone this repo
3. Activate the environment you created in step 1
4. Run the streamlit command in the root directory of the repo:<br>
    `streamlit run app.py`
5. Test the connection as described above
    - note that the save connection drop-down WILL work; it will save the credentials in a pickle file.  Please do not allow the pickle files to be uploaded to github (they are included in .gitignore to help avoid that)!