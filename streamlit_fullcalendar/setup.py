from setuptools import setup, find_packages

setup(
    name='streamlit_fullcalendar',
    version='0.1',
    description='FullCalendar integration with Streamlit',
    packages=find_packages(),
    include_package_data=True,
    install_requires=['streamlit'],
)
