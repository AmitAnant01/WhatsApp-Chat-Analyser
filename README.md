# WhatsApp Chat Analyzer

This is an end-to-end WhatsApp Chat Analyzer project built using Python and Streamlit. In this project, I used basic NLP techniques to clean and analyze chat data. The app allows users to upload their WhatsApp chat file and get useful insights like total messages, most active users, word frequency, emoji usage, and activity timeline. I also used libraries like pandas, matplotlib, and wordcloud for data processing and visualization. The project is fully deployed online using Streamlit Cloud, so anyone can use it easily through a browser without installing anything.


- Note: This only supported for Without Media file.

  
🔗 **Live App: lets Try this** [https://amitanant01-whatsapp-chat-analyser-app-ngt9ec.streamlit.app/](https://amitanant01-whatsapp-chat-analyser-app-ngt9ec.streamlit.app/)


## Features

* Chat statistics (total messages, words, media, links)
* User-wise analysis
* Timeline analysis (daily & monthly activity)
* Activity heatmap (most active days & hours)
* WordCloud generation
* Stopword filtering
* URL extraction
* Emoji analysis
* Interactive charts and graphs


## 🛠️ Tech Stack

* **Frontend & Backend:** Python + Streamlit
* **Libraries Used:**

  * pandas
  * matplotlib
  * seaborn
  * wordcloud
  * urlextract
  * emoji
  * collections
  * re (regex)



## Project Structure

```
├── app.py                # Main Streamlit app
├── helper.py             # Helper functions
├── preprocessor.py       # Chat preprocessing logic
├── requirements.txt      # Dependencies
├── README.md             # Project documentation
```


## How to Run Locally

```bash
git clone https://github.com/AmitAnant01/WhatsApp-Chat-Analyser.git
cd WhatsApp-Chat-Analyser
pip install -r requirements.txt
streamlit run app.py
```



## How to Use

1. Export your WhatsApp chat (without media)
2. Upload the `.txt` file into the app
3. Then Click on the 'Show Analysis' it will give you overall data insights


⭐If you like this project, give it a star on GitHub!
