import streamlit as st
import pandas as pd


allowed_extensions = {'xlsx'}
def allowed_files(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in allowed_extensions


def upload_files():
    