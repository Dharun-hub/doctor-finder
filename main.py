import streamlit as st
from PIL import Image
import requests
from bs4 import BeautifulSoup
import time

st.set_page_config(page_title="Doctor Finder", layout="wide", initial_sidebar_state="expanded")
st.markdown("# Welcome to Doctor Finder! 🎉")

st.subheader("We help you to find doctors around the world.")
st.markdown(
    """
    <style>
    .main{
        background-color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)


with st.sidebar:
    img = Image.open('images/Designer.png')
    st.image(img, width=450)
    st.markdown("Simply enter your location and discover a variety of doctors near you, "
                "each with their own specialties. Whether you need a general practitioner, a specialist, or a surgeon, "
                "our platform connects you with the right healthcare professionals in your area. Start your "
                "search today and take a step towards better health!")

location = st.text_input("Enter any city", help="Use only city names")
speciality = st.selectbox('Speciality:', ['Dentist', 'Gynecologist/obstetrician', 'General Physician',
                                          'Dermatologist', 'Ear-nose-throat (ent) Specialist',
                                          'Homeopath', 'Ayurveda'])


def scrape_doctors(location, speciality):
    page = 1
    doc_list = []
    values = []
    recommendation_list = []
    hospital_list = []
    area_list = []
    while True:
        response = requests.get(f"https://www.practo.com/search/doctors?results_type=doctor&q=%5B%7B%22word%22%3A%22{speciality}%22%2C%22autocompleted%22%3Atrue%2C%22category%22%3A%22subspeciality%22%7D%5D&city={location}&page={page}")
        time.sleep(5)
        practo_data = response.text
        soup = BeautifulSoup(practo_data, 'html.parser')
        doctors = soup.find_all(name='h2', class_="doctor-name")
        reccom = soup.find_all('span', {'data-qa-id': 'doctor_recommendation'})
        hospitals = soup.find_all(name='span', class_='u-c-pointer u-t-hover-underline')
        areas = soup.find_all(name='div', class_='u-bold u-d-inlineblock u-valign--middle')
        if not doctors:
            break
        for doctor in doctors:
            doc_list.append(doctor.getText())
            values.extend([div.text.strip() for div in soup.select('div.info-section > div.u-grey_3-text > div.uv2-spacer--xs-top > div')])
            recommendation_list.extend(span.text for span in reccom)
        for area in areas:
            a = area.find('a')
            area_list.append(a.getText())
        for hospital in hospitals:
            hospital_list.append(hospital.getText())

        time.sleep(2)
        page += 1
    return doc_list, values, recommendation_list, hospital_list, area_list


if st.button("SCRAPE"):
    with st.spinner("Scraping data .... "):
        doc_list, exp_list, reccom_list, hos_lists, area_list = scrape_doctors(location, speciality)
    st.success(f"Found {len(doc_list)} doctors:")
    cleaned_hos = [clinic for clinic in hos_lists if clinic not in ['\xa0+ 1 more', '\xa0+ 2 more']]

    if doc_list:
        st.write("### Doctors List")
        for i in range(len(doc_list)):
            with st.expander(f"{i+1} - {doc_list[i]}"):
                st.text(f'Clinic: {cleaned_hos[i]}\n'
                        f'Location: {area_list[i]}\n'
                        f'{exp_list[i]}\n'
                        f'Patient recommendation: {reccom_list[i]}')
