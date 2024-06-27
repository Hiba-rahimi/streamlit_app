import streamlit as st
import base64
import sys
import os

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def run():

    st.set_page_config(page_title="Bank Recon",
                        page_icon="assets/logo.png", 
                        layout="wide")
    st.sidebar.image("assets/Logo_hps_0.png", use_column_width=True)
    st.sidebar.divider()
    st.sidebar.page_link("app.py", label="**Accueil**" , icon="🏠")
    st.sidebar.page_link("pages/results_recon.py", label="**:alarm_clock: Historique**")
    st.sidebar.page_link("pages/MasterCard_UI.py", label=" **🔀 MasterCard Network Reconciliaiton Option**" )
    #st.sidebar.page_link("pages/Visa_UseCase.py", label=" **Visa Network Reconciliaiton Option**" , icon="🔀")
    st.write("# Bienvenue ! 👋")
    file_ = open("assets/animated-logo.gif", "rb")
    contents = file_.read()
    data_url = base64.b64encode(contents).decode("utf-8")
    file_.close()
    st.markdown(
        f'<div style="display: flex; justify-content: center; align-items: flex-start;"><img src="data:image/gif;base64,{data_url}" alt"logo animation gif" width="auto" height="400"></div>',
        unsafe_allow_html=True,
    )
    code ="""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@600;700&display=swap');

* {
  box-sizing: border-box;
}

 .page-contain {
    display: flex;
    align-items: center;
    justify-content: center;
    border: .75em solid white;
    padding: 2em;
    font-family: 'Open Sans', sans-serif;
 }

.data-card {
  display: flex;
  flex-direction: column;
  max-width: 40em;
  height: 25em;
  overflow: hidden;
  border-radius: .5em;
  text-decoration: none;
  background: #e2eeff;
  margin: 1em;
  padding: 2.75em 2.5em;
  box-shadow: 0 1.5em 2.5em -.5em rgba(#000000, .1);
  transition: transform .45s ease, background .45s ease;
  
  h3 {
    color: #2E3C40;
    font-size: 1.5em;
    font-weight: 600;
    line-height: 1;
    padding-bottom: .5em;
    margin: 0 0 0.142857143em;
    border-bottom: 2px solid #753BBD;
    transition: color .45s ease, border .45s ease;
  }

  h4 {
    color: #627084;
    text-transform: uppercase;
    font-size: 1.125em;
    font-weight: 700;
    line-height: 1;
    letter-spacing: 0.1em;
    margin: 0 0 1.777777778em;
    transition: color .45s ease;
  }

  p {
    opacity: 0;
    color: #FFFFFF;
    font-weight: 600;
    line-height: 1.8;
    margin: 0 0 1.25em;
    transform: translateY(-1em);
    transition: opacity .45s ease, transform .5s ease;
  }

  .link-text {
    display: block;
    color: #753BBD;
    font-size: 1.125em;
    font-weight: 600;
    line-height: 1.2;
    margin: auto 0 0;
    transition: color .45s ease;

    svg {
      margin-left: .5em;
      transition: transform .6s ease;
      
      path {
        transition: fill .45s ease;
      }
    }
  }
  
  &:hover {
    background: #db98eb;
    transform: scale(1.02);
    
    h3 {
      color: #FFFFFF;
      border-bottom-color: #A754C4;
    }

    h4 {
      color: #FFFFFF;
    }

    p {
      opacity: 1;
      transform: none;
    }

    .link-text {
      color: #FFFFFF;

      svg {
        animation: point 1.25s infinite alternate;
        
        path {
          fill: #FFFFFF;
        }
      }
    }
  }
}

@keyframes point {
  0% {
   transform: translateX(0);
  }
  100% {
    transform: translateX(.125em);
  }
}
    </style>
<section class="page-contain">
  <a href="./MasterCard_UI" class="data-card">
    <h3>Option de rapprochement réseau MasterCard</h3>
    <span class="link-text">
      Let's Get Started
    <svg width="25" height="16" viewBox="0 0 25 16" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path fill-rule="evenodd" clip-rule="evenodd" d="M17.8631 0.929124L24.2271 7.29308C24.6176 7.68361 24.6176 8.31677 24.2271 8.7073L17.8631 15.0713C17.4726 15.4618 16.8394 15.4618 16.4489 15.0713C16.0584 14.6807 16.0584 14.0476 16.4489 13.657L21.1058 9.00019H0.47998V7.00019H21.1058L16.4489 2.34334C16.0584 1.95281 16.0584 1.31965 16.4489 0.929124C16.8394 0.538599 17.4726 0.538599 17.8631 0.929124Z" fill="#753BBD"/>
      </svg>
    </span>
  </a>
  <a href="#blank" class="data-card">
    <h3>Option de rapprochement réseau Visa</h3>
    <span class="link-text">
      Let's Get Started 
      <svg width="25" height="16" viewBox="0 0 25 16" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path fill-rule="evenodd" clip-rule="evenodd" d="M17.8631 0.929124L24.2271 7.29308C24.6176 7.68361 24.6176 8.31677 24.2271 8.7073L17.8631 15.0713C17.4726 15.4618 16.8394 15.4618 16.4489 15.0713C16.0584 14.6807 16.0584 14.0476 16.4489 13.657L21.1058 9.00019H0.47998V7.00019H21.1058L16.4489 2.34334C16.0584 1.95281 16.0584 1.31965 16.4489 0.929124C16.8394 0.538599 17.4726 0.538599 17.8631 0.929124Z" fill="#753BBD"/>
      </svg>
    </span>
  </a>
</section>
        """
    st.html(code)


if __name__ == "__main__":
    run()