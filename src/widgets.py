# module widgets

# system
import time

# webui
import streamlit as st


def widget_info_notification(body: str, icon: str = '✅', dur: float = 3):
    widget = st.success(body=body, icon=icon)
    time.sleep(dur)
    widget.empty()


