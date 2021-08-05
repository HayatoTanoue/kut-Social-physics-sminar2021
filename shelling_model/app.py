import streamlit as st
from multiapp import MultiApp
import shelling_app
import network_shelling_app

app = MultiApp()

# Add all your application here
app.add_app("shelling", shelling_app.app)
app.add_app("network shelling", network_shelling_app.app)


# The main app
app.run()
