import streamlit as st

st.title("User Input")
st.headers
x = st.text_input("Input 1: ")
st.write(f"The first input is: {x}")
#st.write("Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/).")
is_clicked = st.button("Click Me")
st.write('##this is a title: ')
